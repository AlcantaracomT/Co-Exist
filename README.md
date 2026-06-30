#  Jogo Cooperativo

##  Sobre o Projeto

O **Jogo Cooperativo** é um jogo de labirinto cooperativo e assimétrico desenvolvido em Python utilizando arquitetura **Cliente-Servidor**.

O objetivo é fazer com que dois jogadores, representados pelos blocos **Azul** e **Vermelho**, cooperem para alcançar o objetivo dourado que finaliza cada fase.

Cada jogador:

- Enxerga apenas elementos da sua própria cor;
- Colide apenas com objetos da sua cor;
- Precisa se comunicar com o outro jogador para superar obstáculos.

Essa mecânica cria uma experiência de **cooperação cega**, onde a comunicação entre os participantes é indispensável para resolver os desafios.

---

#  Funcionamento da Aplicação

A aplicação utiliza uma arquitetura distribuída **Cliente-Servidor Autoritária**.

## Servidor

O servidor é a única fonte da verdade (*Authoritative Server*) e é responsável por:

- armazenar o estado global do jogo;
- carregar os mapas em JSON;
- processar movimentação;
- calcular colisões;
- controlar botões e obstáculos;
- sincronizar os clientes;
- detectar a conclusão da fase.

## Cliente

Os clientes funcionam apenas como interface gráfica.

Cada cliente:

- captura os comandos do teclado (`W`, `A`, `S`, `D` ou setas direcionais);
- envia a direção desejada ao servidor;
- recebe continuamente o estado atualizado do jogo;
- renderiza a cena utilizando **Pygame**;
- filtra os elementos visíveis de acordo com a cor do jogador.

---

# Objetivo do Jogo

A fase é concluída quando **os dois jogadores ocupam simultaneamente o bloco de objetivo dourado**.

Ao detectar essa condição, o servidor:

1. encerra a fase atual;
2. recarrega o mapa;
3. reposiciona os jogadores.

---

#  Requisitos

Para executar o projeto é necessário:

- Python instalado no servidor e nos clientes;
- Biblioteca **Pygame** instalada nas máquinas clientes;
- Rede IP funcional para comunicação via sockets;
- Executar o servidor antes dos clientes.

Instalação do Pygame:

```bash
pip install pygame
```

---

#  Execução

Inicie primeiro o servidor:

```bash
python servidor/main.py
```

Depois execute os clientes:

```bash
python cliente/main.py
```

O primeiro cliente conectado receberá a identidade **Azul**.

O segundo cliente receberá a identidade **Vermelho**.

---

#  Arquitetura

```
Clientes
    │
    │ TCP (Sockets)
    
Servidor Autoritário
    │
    ├── Estado Global
    ├── Colisões
    ├── Física
    ├── Mapas JSON
    └── Sincronização
```

---

#  Comunicação

A comunicação utiliza **Sockets TCP (`SOCK_STREAM`)**.

## Motivos da escolha do TCP

### Garantia de entrega

Todas as mensagens enviadas chegam ao destino, evitando perda de estados importantes do jogo.

### Ordenação

As mensagens chegam exatamente na ordem em que foram enviadas.

Isso evita problemas durante a reconstrução dos objetos JSON recebidos pelo cliente.

### Confiabilidade

Como toda a lógica do jogo é centralizada no servidor, a consistência dos estados é mais importante do que baixa latência.

---

#  Protocolo da Camada de Aplicação

Toda comunicação é realizada utilizando mensagens em **JSON**, separadas por uma quebra de linha (`\n`).

Exemplo:

```json
{
    "tipo": "CMD_MOVER",
    "direcao": "cima"
}
```

---

#  Estados da Aplicação

## Inicialização

O servidor:

- abre um socket na porta **5000**;
- permanece aguardando conexões.

---

## Conexão

Ao receber clientes:

- o primeiro torna-se o jogador **Azul**;
- o segundo torna-se o jogador **Vermelho**.

Cada conexão é tratada em uma thread independente.

---

## Game Loop

Uma thread principal executa continuamente:

- atualização do estado;
- cálculo de colisões;
- sincronização dos clientes.

O ciclo ocorre aproximadamente a cada:

```
0.05 segundos
```

---

## Desconexão

Caso um cliente encerre a aplicação:

- uma exceção é capturada;
- o jogador é removido da lista de clientes conectados;
- o servidor continua funcionando normalmente.

---

#  Mensagens do Protocolo

## RES_LOGAR

### Objetivo

Informar ao cliente qual personagem ele controlará.

### Fluxo

Servidor → Cliente

### Payload

```json
{
    "cor": "azul"
}
```

ou

```json
{
    "cor": "vermelho"
}
```

---

## ST_GAME

### Objetivo

Sincronizar completamente o estado do jogo.

### Fluxo

Servidor → Cliente

### Payload

```json
{
    "jogadores": {},
    "objetos_cenario": {},
    "fase_atual": 1,
    "fim_de_jogo": false
}
```

---

## CMD_MOVER

### Objetivo

Solicitar movimentação do jogador.

### Fluxo

Cliente → Servidor

### Payload

```json
{
    "direcao": "cima"
}
```

Valores possíveis:

- `"cima"`
- `"baixo"`
- `"esquerda"`
- `"direita"`

---

# Delimitação dos Pacotes

Como o TCP trabalha com fluxo contínuo de bytes, várias mensagens podem chegar agrupadas.

Para resolver isso, o protocolo utiliza **quebra de linha (`\n`)** como delimitador.

## Envio

Cada mensagem JSON recebe um `\n` ao final.

Exemplo:

```
{"tipo":"CMD_MOVER","direcao":"cima"}\n
```

---

## Recebimento

O cliente:

1. lê os dados utilizando `recv()`;
2. concatena o conteúdo em um buffer;
3. separa mensagens completas usando:

```python
split("\n", 1)
```

Somente após separar uma mensagem completa é realizado:

```python
json.loads()
```

Essa estratégia evita erros de decodificação quando múltiplos pacotes chegam juntos.

---

# Tecnologias Utilizadas

- Python
- Pygame
- JSON
- Socket TCP
- Threads

---
