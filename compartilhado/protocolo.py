import json

LARGURA_TELA = 800
ALTURA_TELA = 600

REG_LOGAR = "REQ_LOGAR"
RES_LOGAR = "REQ_LOGAR"
CMD_MOVER = "CMD_MOVER"
ST_GAME = "ST_GAME"

def empacotar(tipo_mensagem, dados):
    mensage = {
        "tipo": tipo_mensagem,
        "dados": dados
    }

    return (json.dumps(mensage) + "\n").encode('utf-8')

def desempacotar(byts_recebido):
    string_json = byts_recebido.decode('utf-8').strip()
    return json.loads(string_json)