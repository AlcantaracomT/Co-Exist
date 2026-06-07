import pygame
import json
import sys
import os

LARGURA_TELA = 800
ALTURA_TELA = 600

COR_FUNDO = (240, 240, 240)
COR_NEUTRA = (50, 50, 50)
COR_AZUL = (0, 122, 255)
COR_VERMELHO = (255, 59, 48)
COR_OBJETIVO = (255, 215, 0)
COR_TEXTO = (30, 30, 30)

def iniciar_editor():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Editor de Mapas - CO-EXIST")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont(None, 20)

    objetos_criados = []
    
    objetos_criados.append({"id": 1, "tipo": "parede", "x": 0, "y": 0, "largura": 800, "altura": 20, "cor": "neutro"})
    objetos_criados.append({"id": 2, "tipo": "parede", "x": 0, "y": 580, "largura": 800, "altura": 20, "cor": "neutro"})
    objetos_criados.append({"id": 3, "tipo": "parede", "x": 0, "y": 0, "largura": 20, "altura": 600, "cor": "neutro"})
    objetos_criados.append({"id": 4, "tipo": "parede", "x": 780, "y": 0, "largura": 20, "altura": 600, "cor": "neutro"})

    desenhando = False
    x_ini, y_ini = 0, 0
    x_fim, y_fim = 0, 0

    cor_atual = "azul"  
    tipo_atual = "espinho" 
    
    id_contador = 5
    numero_fase_salvar = 3 
    while True:
        tela.fill(COR_FUNDO)
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: 
                    desenhando = True
                    x_ini, y_ini = evento.pos
                    x_fim, y_fim = evento.pos


            elif evento.type == pygame.MOUSEMOTION:
                if desenhando:
                    x_fim, y_fim = evento.pos


            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1 and desenhando:
                    desenhando = False
                    x_fim, y_fim = evento.pos
                    
                    
                    x_real = min(x_ini, x_fim)
                    y_real = min(y_ini, y_fim)
                    largura = abs(x_fim - x_ini)
                    altura = abs(y_fim - y_ini)

                    if largura > 5 and altura > 5:
                        novo_obj = {
                            "id": id_contador,
                            "tipo": tipo_atual,
                            "x": x_real,
                            "y": y_real,
                            "largura": largura,
                            "altura": altura,
                            "cor": "neutro" if tipo_atual == "objetivo" else cor_atual
                        }
                        objetos_criados.append(novo_obj)
                        id_contador += 1
                        print(f"[EDITOR] Bloco adicionado: {novo_obj}")

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_a:
                    cor_atual = "azul"
                    tipo_atual = "espinho"
                elif evento.key == pygame.K_v:
                    cor_atual = "vermelho"
                    tipo_atual = "espinho"
                elif evento.key == pygame.K_n:
                    cor_atual = "neutro"
                    tipo_atual = "espinho"
                elif evento.key == pygame.K_o:
                    tipo_atual = "objetivo"
                
                elif evento.key == pygame.K_z:
                    if len(objetos_criados) > 4: 
                        removido = objetos_criados.pop()
                        print(f"[EDITOR] Removido: {removido}")
                
                elif evento.key == pygame.K_s:
                    os.makedirs("fases", exist_ok=True)
                    caminho = f"fases/fase{numero_fase_salvar}.json"
                    with open(caminho, "w", encoding="utf-8") as f:
                        json.dump(objetos_criados, f, indent=2)
                    print(f"\n[SUCESSO] Labirinto salvo com sucesso em: {caminho}!")
                    print(f"[SUCESSO] Total de {len(objetos_criados)} objetos catalogados.\n")

        for obj in objetos_criados:
            if obj["tipo"] == "objetivo":
                cor_render = COR_OBJETIVO
            elif obj["cor"] == "azul":
                cor_render = COR_AZUL
            elif obj["cor"] == "vermelho":
                cor_render = COR_VERMELHO
            else:
                cor_render = COR_NEUTRA
            pygame.draw.rect(tela, cor_render, (obj["x"], obj["y"], obj["largura"], obj["altura"]))

        if desenhando:
            x_real = min(x_ini, x_fim)
            y_real = min(y_ini, y_fim)
            largura = abs(x_fim - x_ini)
            altura = abs(y_fim - y_ini)
            
            if tipo_atual == "objetivo":
                cor_preview = COR_OBJETIVO
            else:
                cor_preview = COR_AZUL if cor_atual == "azul" else (COR_VERMELHO if cor_atual == "vermelho" else COR_NEUTRA)
                
            pygame.draw.rect(tela, cor_preview, (x_real, y_real, largura, altura), 2)

        texto_hud = f"Tipo Atual: {tipo_atual.upper()} | Cor Atual: {cor_atual.upper()} | Próximo ID: {id_contador}"
        texto_ajuda = "Comandos: [A] Azul | [V] Vermelho | [N] Neutro | [O] Objetivo | [Z] Desfazer | [S] SALVAR"
        
        surf_hud = fonte.render(texto_hud, True, COR_TEXTO)
        surf_ajuda = fonte.render(texto_ajuda, True, COR_TEXTO)
        tela.blit(surf_hud, (25, 25))
        tela.blit(surf_ajuda, (25, 45))

        pygame.display.flip()
        relogio.tick(60)

if __name__ == "__main__":
    iniciar_editor()