import socket 
import threading
import json
import time
import os
import traceback

from compartilhado.protocolo import LARGURA_TELA, ALTURA_TELA, RES_LOGAR, ST_GAME, CMD_MOVER, empacotar

HOST = '0.0.0.0'
PORTA = 5000

def carregar_mapa_do_disco(numero_fase):
    """Lê o arquivo JSON correspondente à fase usando caminhos absolutos seguros."""
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(diretorio_atual) # Sobe um nível para a raiz do projeto
    caminho_arquivo = os.path.join(raiz_projeto, "fases", f"fase{numero_fase}.json")
    
    print(f"[DEBUG SERVIDOR] Tentando carregar o mapa de: {caminho_arquivo}")
    
    if os.path.exists(caminho_arquivo):
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                print(f"[DEBUG SERVIDOR] Mapa da Fase {numero_fase} carregado com sucesso! {len(dados)} objetos encontrados.")
                return dados
        except Exception as e:
            print(f"[ERRO CHAVE] Falha ao ler o arquivo JSON da fase {numero_fase}: {e}")
    else:
        print(f"[ERRO CRÍTICO] Arquivo de mapa NÃO encontrado no caminho: {caminho_arquivo}")
        print("[DICA] Certifique-se de que a pasta 'fases' está na raiz do seu projeto e contém 'fase1.json'.")
    return None

estado_jogo = {
    "jogadores": {
        "vermelho": {"x": 100, "y": 300},
        "azul": {"x": 110, "y": 300}
    },
    "objetos_cenario": carregar_mapa_do_disco(1),
    "botao_pressionado": False,
    "fase_atual": 1,
    "fim_de_jogo": False
}

clientes_conectados = {}
lock = threading.Lock()

def atualizar_clientes():
    pacote_estado = empacotar(ST_GAME, estado_jogo)
    for cor, sock_cliente in clientes_conectados.items():
        try:
            sock_cliente.sendall(pacote_estado)
        except Exception:
            pass

def checar_colisao(x_player, y_player, tamanho, obj):
    p_esquerda = x_player - tamanho // 2
    p_direita = x_player + tamanho // 2
    p_topo = y_player - tamanho // 2
    p_baixo = y_player + tamanho // 2

    o_esquerda = obj["x"]
    o_direita = obj["x"] + obj["largura"]
    o_topo = obj["y"]
    o_baixo = obj["y"] + obj["altura"]

    if (p_direita > o_esquerda and p_esquerda < o_direita and
            p_baixo > o_topo and p_topo < o_baixo):
        return True
    return False

def processar_movimento(cor_jogador, direcao):
    PASSO = 5
    TAMANHO_JOGADOR = 2

    with lock:
        x_atual = estado_jogo["jogadores"][cor_jogador]["x"]
        y_atual = estado_jogo["jogadores"][cor_jogador]["y"]

        x_novo = x_atual
        y_novo = y_atual

        if direcao == "cima": 
            y_novo -= PASSO
        elif direcao == "baixo":
            y_novo += PASSO
        elif direcao == "esquerda":
            x_novo -= PASSO  
        elif direcao == "direita":
            x_novo += PASSO
            
        if not (TAMANHO_JOGADOR // 2 <= x_novo <= LARGURA_TELA - TAMANHO_JOGADOR // 2):
            x_novo = x_atual
        if not (TAMANHO_JOGADOR // 2 <= y_novo <= ALTURA_TELA - TAMANHO_JOGADOR // 2):
            y_novo = y_atual

        colidiu = False
        for obj in estado_jogo["objetos_cenario"]:
            if obj["cor"] == "neutro":
                if checar_colisao(x_novo, y_novo, TAMANHO_JOGADOR, obj):
                    colidiu = True
                    break
            elif cor_jogador == "azul" and obj["cor"] == "vermelho":
                if checar_colisao(x_novo, y_novo, TAMANHO_JOGADOR, obj):
                    colidiu = True
                    break
            elif cor_jogador == "vermelho" and obj["cor"] == "azul":
                if checar_colisao(x_novo, y_novo, TAMANHO_JOGADOR, obj):
                    colidiu = True
                    break
            
        if not colidiu:
            estado_jogo["jogadores"][cor_jogador]["x"] = x_novo
            estado_jogo["jogadores"][cor_jogador]["y"] = y_novo

            botoes_ativos = set()

            x_azul = estado_jogo["jogadores"]["azul"]["x"]
            y_azul = estado_jogo["jogadores"]["azul"]["y"]
            x_vermelho = estado_jogo["jogadores"]["vermelho"]["x"]
            y_vermelho = estado_jogo["jogadores"]["vermelho"]["y"]

            for obj in estado_jogo["objetos_cenario"]:
                if obj["tipo"] == "objetivo":
                    if (checar_colisao(x_azul, y_azul, TAMANHO_JOGADOR, obj) and 
                        checar_colisao(x_vermelho, y_vermelho, TAMANHO_JOGADOR, obj)):
                        
                        proxima_fase = estado_jogo["fase_atual"] + 1
                        novo_mapa = carregar_mapa_do_disco(proxima_fase)
                        
                        if novo_mapa is not None:
                            estado_jogo["fase_atual"] = proxima_fase
                            estado_jogo["objetos_cenario"] = novo_mapa
                            estado_jogo["jogadores"]["vermelho"] = {"x": 100, "y": 300}
                            estado_jogo["jogadores"]["azul"] = {"x": 110, "y": 300}
                            print(f"[SERVIDOR] Avançando para a Fase {proxima_fase}!")
                            return
                        else:
                            estado_jogo["fim_de_jogo"] = True
                            print("[SERVIDOR] Fim de jogo alcançado!")
                            return

                if obj["tipo"] == "botao":
                    if (checar_colisao(x_azul, y_azul, TAMANHO_JOGADOR, obj) or 
                        checar_colisao(x_vermelho, y_vermelho, TAMANHO_JOGADOR, obj)):
                        botoes_ativos.add(obj["ativa"])

            mapa_limpo = carregar_mapa_do_disco(estado_jogo["fase_atual"])
            
            if mapa_limpo:
                novos_objetos = []
                for obj in mapa_limpo:
                    if obj["tipo"] == "porta" and obj["grupo"] in botoes_ativos:
                        continue
                    novos_objetos.append(obj)
                
                estado_jogo["objetos_cenario"] = novos_objetos

def gerenciar_cliente(sock_cliente, cor_jogador):
    print(f"[SERVIDOR] Thread iniciada para o jogador {cor_jogador}")

    try:
        sock_cliente.sendall(empacotar(RES_LOGAR, {"cor": cor_jogador}))
        atualizar_clientes()
    except Exception as e:
        print(f"[ERRO] falha ao enviar confirmação para o jogador {cor_jogador}: {e}")
        return

    buffer = ""
    while True:
        try:
            dados = sock_cliente.recv(1024)
            if not dados:
                break
            buffer += dados.decode('utf-8')

            while "\n" in buffer:
                linha, buffer = buffer.split("\n", 1)
                if not linha.strip():
                    continue

                try:
                    mensagem = json.loads(linha)

                    if mensagem["tipo"] == CMD_MOVER:
                        direcao = mensagem["dados"]["direcao"]
                        processar_movimento(cor_jogador, direcao)
                        atualizar_clientes()
                except Exception as e:
                    print("\n" + "="*50)
                    print(f"[ERRO CRÍTICO NO PROCESSAMENTO DO JSON DO SERVIDOR]")
                    traceback.print_exc() 
                    print("="*50 + "\n")
                    break
        except Exception as e:
            print(f"[Aviso] falha ao receber dados do jogador {cor_jogador.upper()}")
            break
        
    sock_cliente.close()
    with lock:
        if cor_jogador in clientes_conectados:
            del clientes_conectados[cor_jogador]
    print(f"[SERVIDOR] jogador {cor_jogador.upper()} saiu do jogo")

def iniciar_servidor():
    sock_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_servidor.bind((HOST, PORTA))
    sock_servidor.listen(2)

    print(f"[SERVIDOR] Servidor iniciado na porta {PORTA}")

    cores_disponiveis = ["azul", "vermelho"]
    while len(clientes_conectados) < 2:
        sock_cliente, endereco = sock_servidor.accept()
        cores_atribuidas = cores_disponiveis[len(clientes_conectados)]

        print(f"[CONEXAO] {endereco} conectado, jogador {cores_atribuidas.upper()}")

        clientes_conectados[cores_atribuidas] = sock_cliente

        t = threading.Thread(target=gerenciar_cliente, args=(sock_cliente, cores_atribuidas))
        t.daemon = True
        t.start()

    print("[SERVIDOR] Ambos os jogadores conectados. Jogo em andamento!")
    while len(clientes_conectados) > 0:
        time.sleep(1)

if __name__ == "__main__":
    iniciar_servidor()