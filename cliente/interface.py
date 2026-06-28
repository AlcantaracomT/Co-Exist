import pygame
import sys 
import traceback
from compartilhado.protocolo import LARGURA_TELA, ALTURA_TELA

COR_FUNDO = (240, 240, 240)      
COR_NEUTRA = (50, 50, 50)        
COR_AZUL = (0, 122, 255)        
COR_VERMELHO = (255, 59, 48)     
COR_TEXTO = (100, 100, 100)

COR_BOTAO = (0, 200, 100)     
COR_VITORIA = (255, 215, 0)     
COR_VERDE = (0, 255, 0) 
COR_B = (240, 240, 240)

class Interface_jogo:
    def __init__(self, rede_cliente):
        pygame.init()
        self.rede = rede_cliente
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(f"Jogo Coop - Jogador {self.rede.cor_atribuida.upper()}")
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont(None, 18)

    def executar(self):
        rodando = True 

        while rodando and self.rede.conectado: 
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False

            teclas = pygame.key.get_pressed()
            direcao = "parado"

            if teclas[pygame.K_UP] or teclas[pygame.K_w]:
                direcao = "cima"
            elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                direcao = "baixo"
            elif teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                direcao = "esquerda"
            elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                direcao = "direita"     

            if direcao != "parado":
                self.rede.enviar_movimento(direcao)

            self.tela.fill(COR_FUNDO)

            try:
                if self.rede.estado_atual:
                    if self.rede.estado_atual["fim_de_jogo"]:
                        texto_vit = self.fonte.render("VOCÊS VENCERAM! TRABALHO EM EQUIPE CONCLUÍDO!", True, COR_BOTAO)
                        self.tela.blit(texto_vit, (LARGURA_TELA // 2 - 180, ALTURA_TELA // 2))
                    else:
                        self.desenhar_cenario()
                        self.desenhar_jogador()
                else:
                    self._desenhar_carregamento()
            except Exception as e:
                print("\n" + "="*50)
                print(f"[ERRO CRÍTICO NA RENDERIZAÇÃO DO CLIENTE]")
                traceback.print_exc()
                print("="*50 + "\n")
                rodando = False 
            
            pygame.display.flip()
            self.relogio.tick(60)

        pygame.quit()
        sys.exit()
    
    def desenhar_jogador(self):
        dados_jogadores = self.rede.estado_atual["jogadores"]
        pos_azul = dados_jogadores["azul"]
        pygame.draw.rect(self.tela, COR_AZUL, (pos_azul["x"] - 15, pos_azul["y"] - 15, 30, 30))

        pos_vermelho = dados_jogadores["vermelho"]
        pygame.draw.rect(self.tela, COR_VERMELHO, (pos_vermelho["x"] - 15, pos_vermelho["y"] - 15, 30, 30))


    def desenhar_cenario(self):
        if not self.rede.estado_atual or self.rede.estado_atual.get("objetos_cenario") is None:
            return

        cor_local = self.rede.cor_atribuida
        objetos = self.rede.estado_atual["objetos_cenario"]

        for obj in objetos:
            if obj is None:
                continue
                
            if obj["cor"] == "vermelho" and cor_local == "azul":
                continue
            if obj["cor"] == "azul" and cor_local == "vermelho":
                continue

            if obj["tipo"] == "botao1":
                if cor_local != "vermelho":
                    continue
                cor_desenho = COR_BOTAO
            if obj["tipo"] == "botao2":
                if cor_local != "azul":
                    continue
                cor_desenho = COR_BOTAO
            elif obj["tipo"] == "botao1-2":
                cor_desenho = COR_BOTAO
            elif obj["tipo"] == "botao3":
                cor_desenho = COR_BOTAO
            elif obj["tipo"] == "botao31":
                cor_desenho = COR_BOTAO
            elif obj["tipo"] == "botao32":
                cor_desenho = COR_BOTAO
            elif obj["tipo"] == "objetivo":
                cor_desenho = COR_VITORIA
            elif obj["cor"] == "neutro":
                cor_desenho = COR_NEUTRA
            elif obj["cor"] == "azul":
                cor_desenho = COR_VERMELHO
            elif obj["cor"] == "vermelho":
                cor_desenho = COR_AZUL
            elif obj["tipo"] == "bosS":
                cor_desenho = COR_VERDE
            elif obj["tipo"] == "bosS2":
                if cor_local != "vermelho":
                    continue
                cor_desenho = COR_VERDE
            elif obj["tipo"] == "bosS2-o":
                if cor_local != "azul":
                    continue
                cor_desenho = COR_VERDE

            elif obj["tipo"] == "bosS2-j":
                cor_desenho = COR_B

            pygame.draw.rect(self.tela, cor_desenho, (obj["x"], obj["y"], obj["largura"], obj["altura"]))

        texto_cor = self.fonte.render(f"Voce enxerga apenas: Rastro e {cor_local.upper()}", True, COR_TEXTO)
        self.tela.blit(texto_cor, (10, 10))

    def _desenhar_carregamento(self):
        texto = self.fonte.render("Carregando...", True, COR_TEXTO)
        self.tela.blit(texto, (LARGURA_TELA // 2 - 50, ALTURA_TELA // 2))
            
