import sys
from  cliente.rede import Rede_cliente
from cliente.interface import Interface_jogo

print("RODOU")

def rodar_cliente():
    ip_servidor = "127.0.0.1"
    
    rede = Rede_cliente(host = ip_servidor, porta = 5000)

    print("[CLIENTE] Tentando se conectar ao servidor...")

    if rede.conectar():
        app = Interface_jogo(rede)
        app.executar()
    else:
        print("[CLIENTE] Falha ao iniciar")
        sys.exit(1)

if __name__ == "__main__":
    rodar_cliente()