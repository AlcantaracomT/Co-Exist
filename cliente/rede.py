import socket
import threading
import json
from compartilhado.protocolo import CMD_MOVER, empacotar

class Rede_cliente:
    def __init__(self, host='127.0.0.1', porta=5000):
        self.host = host
        self.porta = porta
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cor_atribuida = None
        self.estado_atual = None
        self.conectado = False

    def conectar(self):
        try:
            self.socket.connect((self.host, self.porta))
            self.conectado =True

            print(f"[REDE] Conectado ao servidor {self.host}:{self.porta}")

            dados_iniciais = self.socket.recv(1024).decode('utf-8')

            if "\n" in dados_iniciais:
                dados_iniciais = dados_iniciais.split("\n")[0]

            pacote = json.loads(dados_iniciais)

            if pacote["tipo"] == "RES_LOGAR":
                self.cor_atribuida = pacote["dados"]["cor"]
                print(f"[REDE] Você é o jogador {self.cor_atribuida.upper()}")

            thread_escuta = threading.Thread(target=self._escutar_servidor, daemon=True)
            thread_escuta.start()
            return True
        except Exception as e:
            print(f"[ERRO DE CONEXÂO] não conectou  em {e}")
            self.conectado = False
            return False
        
    def _escutar_servidor(self):
        Buffer = ''

        while self.conectado:
            try:
                dados = self.socket.recv(4096)
                if not dados:
                    print(f"[REDE] erro de conexão")
                    self.conectado = False
                    break

                Buffer += dados.decode('utf-8')

                while "\n" in Buffer:
                    linha, Buffer = Buffer.split("\n", 1)
                    
                    # CORRIGIDO: Checagem simples, limpa e segura para strings vazias
                    if not linha.strip():
                        continue

                    pacote = json.loads(linha)
                    if pacote["tipo"] == "ST_GAME":
                        self.estado_atual = pacote["dados"]
            except Exception as e:
                print(f"[REDE] Erro ao receber dados do servidor: {e}")
                self.conectado = False
                break

    def enviar_movimento(self, direcao):
        if not self.conectado:
            return
        
        try:
            pacote_movimento = empacotar(CMD_MOVER, {"direcao": direcao})
            self.socket.sendall(pacote_movimento)
        except Exception as e:
            print(f"[REDE] Erro ao enviar comando: {e}")
            self.conectado = False

