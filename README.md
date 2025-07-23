# Conta-o-Choro

Projeto de Compiladores 2025/1

Autor: Marciel Silva de Almeida (628069)

Ferramenta para jogadores de poker contarem suas histórias de bad beats e suckouts.

Esta ferramenta foi desenvolvida em Python.

# Requisitos
- Bibliotecas básicas Python (os, re, sys)
- Existência da pasta Input (caso deseje executar os testes Demo)

# Execução

Em linha de comando windows:

`python ARG1 ARG2 ARG3` (para execução própria)

`python ARG1 Demo` (para execução Exemplo)

`ARG1`: caminho do analisador semântico

`ARG2`: caminho para o arquivo de entrada (sua história)

`ARG3`: caminho para o arquivo de saída

# Instruções para criação de histórias
- a História deve conter Introdução e jogadas. Pode conter Resultado.

## Introdução
- Descrição objetiva sobre quem está envolvido ("Eu", <Nome_jogador>, "o Vilão"). Há suporte para situações multiway (mais de 2 jogadores). Use frases como
- "Daniel estava no botão com rei de copas e rei de ouros"
- "Marciel estava com 50 USD no BB"

> ⚠️ **Atenção:**
> 
> Não utilizar verbos no plural (descreva cada jogador separadamente).
>
> Sempre use o passado (afinal, a situação ja aconteceu)
>
> Nunca esqueça de dizer a posição do jogador (há tratamento de erros quanto a isso)

## Jogada
- Descrição dos momentos (pre-flop, flop, turn e river) e ações tomadas pelos jogadores (bet, fold, aumentar, pagar...)
- "Marciel apostou 50 blinds. O Vilão pagou. Eu foldei."

> ⚠️ **Atenção:**
>
> Descreva a ação de cada jogador na ordem das posições (SB, BB, UTG, UTG+1, LJ, HJ, MP, CO, BTN). Há tratamento para isso
>
> Sempre informe que realizou a ação (ha tratamento sobre isso)
>
> Evite ações irreais ("<Jogador A> apostou. <Jogador A> pagou", por exemplo. Cenário tratado)
## Resultado

- apenas para informar quem venceu/perdeu a rodada
- "Eu perdi"
- "Daniel venceu"


> ⚠️ **Atenção:**
>
> Não é possível utilizar jogadas após chegar nos resultados (o que aconteceu, aconteceu)
