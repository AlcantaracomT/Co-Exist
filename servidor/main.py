import socket 
import threading
import json
import time
import os
import traceback

from compartilhado.protocolo import LARGURA_TELA, ALTURA_TELA, RES_LOGAR, ST_GAME, CMD_MOVER, empacotar

HOST = '0.0.0.0'
PORTA = 5000
TEMP = 0

CONT2 = 0
CONT3 = 0

def carregar_mapa_do_disco(numero_fase):
    """Lê o arquivo JSON correspondente à fase usando caminhos absolutos seguros."""
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(diretorio_atual) 
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
    "foi": False,
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
    p_esquerda = (x_player) - tamanho // 2
    p_direita = (x_player) + tamanho // 2
    p_topo = (y_player)- tamanho // 2
    p_baixo = (y_player) + tamanho // 2
    
    o_esquerda = obj["x"]
    o_direita = obj["x"] + obj["largura"]
    o_topo = obj["y"]
    o_baixo = obj["y"] + obj["altura"]

    if (p_direita >= o_esquerda and p_esquerda <= o_direita and
            p_baixo >= o_topo and p_topo <= o_baixo):
        return True
    return False

def notColidindo(cor_jogador, x_novo, y_novo, TAMANHO_JOGADOR):
    estado_jogo["jogadores"][cor_jogador]["x"] = x_novo
    estado_jogo["jogadores"][cor_jogador]["y"] = y_novo

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

def processar_movimento(cor_jogador, direcao):
    PASSO = 5
    TAMANHO_JOGADOR = 22
    global CONT2, CONT3

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

            if  obj["tipo"] == "botao1" and cor_jogador ==  "azul":
                if checar_colisao(x_novo, y_novo, TAMANHO_JOGADOR, obj):
                    obj["y"] = 510
                    obj["tipo"] = "botao2"
                    colidiu = True
                    break

            elif obj["tipo"] == "botao2" and cor_jogador ==  "vermelho":
                if checar_colisao(x_novo, y_novo, TAMANHO_JOGADOR, obj):
                    obj["y"] = 300
                    obj["x"] = 50
                    obj["largura"] = 40
                    obj["tipo"] = "botao1-2"
                    colidiu = True
                    break

            elif obj["tipo"] == "botao1-2":
                x_azul = estado_jogo["jogadores"]["azul"]["x"]
                y_azul = estado_jogo["jogadores"]["azul"]["y"]
                x_vermelho = estado_jogo["jogadores"]["vermelho"]["x"]
                y_vermelho = estado_jogo["jogadores"]["vermelho"]["y"]
                if (checar_colisao(x_azul, y_azul, TAMANHO_JOGADOR, obj) and 
                checar_colisao(x_vermelho, y_vermelho, TAMANHO_JOGADOR, obj)):
                    obj["largura"] = 0
                    obj["altura"] = 0
                    estado_jogo["botao_pressionado"] = True
                    colidiu = True
                    break

            if obj["tipo"] == "bosS":
                if checar_colisao(x_novo, y_novo, TAMANHO_JOGADOR, obj):
                    estado_jogo["jogadores"][cor_jogador]["x"] = 100
                    estado_jogo["jogadores"][cor_jogador]["y"] = 210
                    colidiu = True
                    break

            if estado_jogo["botao_pressionado"] == True: 
                if obj["id"] == 5:
                    obj["x"] = -300

                if obj["tipo"] == "espinho":
                    obj["x"] = 120

                if obj["id"] == 12:
                    obj["x"] = 700

                if obj["tipo"] == "bosS2-j":
                    obj["tipo"] = "bosS2"
            
                if  obj["tipo"] == "botao3" and cor_jogador ==  "azul":
                    if checar_colisao(x_novo, y_novo, TAMANHO_JOGADOR, obj):
                        obj["y"] = 510
                        obj["tipo"] = "botao31"
                        CONT2 = 1
                        colidiu = True
                if obj["tipo"] == "botao31" and cor_jogador ==  "vermelho":
                    if checar_colisao(x_novo, y_novo, TAMANHO_JOGADOR, obj):
                        obj["y"] = 300
                        obj["x"] = 50
                        obj["largura"] = 40
                        obj["tipo"] = "botao32"
                        colidiu = True
                elif obj["tipo"] == "botao32":
                    x_azul = estado_jogo["jogadores"]["azul"]["x"]
                    y_azul = estado_jogo["jogadores"]["azul"]["y"]
                    x_vermelho = estado_jogo["jogadores"]["vermelho"]["x"]
                    y_vermelho = estado_jogo["jogadores"]["vermelho"]["y"]
                    if (checar_colisao(x_azul, y_azul, TAMANHO_JOGADOR, obj) and 
                    checar_colisao(x_vermelho, y_vermelho, TAMANHO_JOGADOR, obj)):
                        obj["largura"] = 0
                        obj["altura"] = 0
                        CONT3 = 1
                        colidiu = True
                if obj["tipo"] == "bosS2":
                    if checar_colisao(x_novo, y_novo, TAMANHO_JOGADOR, obj):
                        estado_jogo["jogadores"][cor_jogador]["x"] = 100
                        estado_jogo["jogadores"][cor_jogador]["y"] = 210
                        colidiu = True
                        break

                if CONT2 == 1:
                    if obj["id"] == 11:
                        obj["x"] = -510
                if CONT2 == 1 and CONT3 == 1:
                        if obj["id"] == 13:
                            obj["x"] = 700
            


        if not colidiu:
            notColidindo(cor_jogador, x_novo, y_novo, TAMANHO_JOGADOR)

def animaBos():
    global TEMP, TEMP2
    for obj in estado_jogo["objetos_cenario"]:
            if obj["id"] == 5:
                if TEMP == 0:
                    obj["x"] +=1
                else:
                    obj["x"] -=1
                if obj["x"] == 300:
                    TEMP = 1
                elif obj["x"] == 200:
                    TEMP = 0
def gameLoop():
    while True:
        with lock:
            animaBos()
            atualizar_clientes()
        time.sleep(0.05)


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
    t_game = threading.Thread(target=gameLoop)
    t_game.daemon = True
    t_game.start()

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