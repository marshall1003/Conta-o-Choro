import re
import os
import sys
import Analisador_lexico as lexer_module

# Caminhos padrão
FILE = "Exemplo.txt"
ENTRADA = os.path.join(r"C:\Users\maria\Desktop\Marciel\Redes\Conta-o-Choro\T6",FILE)
SAIDA = os.path.join(r"C:\Users\maria\Desktop\Marciel\Redes\Conta-o-Choro\T6", FILE.replace('.txt', '_out.txt'))


ESTAGIOS = [
    'pre-flop',
    'flop',
    'turn',
    'river'
]

POSICOES = [
    'btn',
    'co',
    'bb',
    'sb',
    'utg',
    'utg+1',
    'mp',
    'hj',
    'lj'
]

JOGADORES = [
    'eu',
    'ele',
    'vilao'
]


#gramatica simplificada para o jogo de poker

#   historia ::= introducao {jogadas} {resultado}

#   introducao ::= JOGADOR VERBO_POSSE situacoes
#   situacoes ::= situacao [E situacao]
#   situacao ::= COM QUANTIDADE_FICHAS [NO posicao] [COM mao]
#                | [COM QUANTIDADE_FICHAS] NO posicao [COM mao]
#                | [COM QUANTIDADE_FICHAS] [NO posicao] COM mao
#   jogador ::= EU | ELE | VILAO | posicao
#   mao ::= CARTA [DE NAIPE] [E] CARTA [DE NAIPE] | CARTA [E] CARTA [SUIT] 
#   posicao ::= BTN | CO | BB | SB | UTG | UTG+1 | MP | HJ | LJ

#   jogadas ::= primeira_jogada {jogada}
#   primeira_jogada ::= [NO] ESTAGIO jogada
#   jogada ::= jogador acao_jogador [E jogador acao_jogador] PONTO
#   acao_jogador ::= ACAO JOGADOR_ATIVA [QUANTIDADE_FICHAS|POTE] 
#                   | ACAO JOGADOR_PASSIVA
#   ESTAGIO ::= pre-flop | flop | turn | river

#resultado      ::= jogador VERBO_RESULTADO [QUANTIDADE_FICHAS|POTE] PONTO


class PokerParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[self.pos] if self.tokens else None

    def consumir(self, tipo):
        if self.token_atual and self.token_atual[1] == tipo:
            self.pos += 1
            self.token_atual = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        else:
            raise SyntaxError(f"Esperado {tipo}, encontrado {self.token_atual}")
    
    def parse(self):
        self.historia()
        if self.token_atual:
            raise SyntaxError(f"Token inesperado após fim da história: {self.token_atual}")
        print("História sintaticamente válida!")

    
    #   historia ::= introducao {jogadas} {resultado}
    def historia(self):
        self.introducao()
        if self.token_atual and (self.token_atual[1] == 'NO' or self.token_atual[1] in ESTAGIOS):
            self.jogadas()
        if self.token_atual and (self.token_atual[1] in JOGADORES or self.token_atual[1] in POSICOES):
            self.resultado()

    #   introducao ::= JOGADOR VERBO_POSSE situacao    
    def introducao(self):
        self.jogador()
        self.consumir('VERBO_POSSE')
        self.situacoes()
    
    #   situacoes ::= situacao [E situacao]
    def situacoes(self):
        self.situacao()
        body = True
        while body:
            if self.token_atual and self.token_atual[1] == 'E':
                self.consumir('E')
                self.situacao()
            else:
                body = False

    #   situacao ::= COM QUANTIDADE_FICHAS [NO posicao] [COM mao]
    #                | [COM QUANTIDADE_FICHAS] NO posicao [COM mao]
    #                | [COM QUANTIDADE_FICHAS] [NO posicao] COM mao
    def situacao(self):
        if self.token_atual and self.token_atual[1] == 'COM':
            if self.tokens[self.pos + 1][1] == 'QUANTIDADE_FICHAS':
                self.consumir('COM')
                self.consumir('QUANTIDADE_FICHAS')
                if self.token_atual and self.token_atual[1] == 'NO':
                    self.consumir('NO')
                    self.posicao()
                if self.token_atual and self.token_atual[1] == 'COM':
                    self.consumir('COM')
                    self.mao()
            else:
                if self.token_atual and self.token_atual[1] == 'COM':
                    self.consumir('COM')
                    self.mao()
        else: 
            if self.token_atual and self.token_atual[1] == 'NO':
                    self.consumir('NO')
                    self.posicao()
                    if self.token_atual and self.token_atual[1] == 'COM':
                        self.consumir('COM')
                        self.mao()
        
    #   jogador ::= EU | ELE | VILAO | posicao
    def jogador(self):
        for jogador in JOGADORES:
            if self.token_atual and self.token_atual[1] == jogador.upper():
                self.consumir(jogador.upper())
                break
            
    #   posicao ::= BTN | CO | BB | SB | UTG | UTG+1 | MP | HJ | LJ    
    def posicao(self):
        for posicao in POSICOES:
            if self.token_atual and self.token_atual[1] == posicao.upper():
                self.consumir(posicao.upper())
                break

    #   mao ::= CARTA [DE NAIPE] [E] CARTA [DE NAIPE] | CARTA [E] CARTA [SUIT] 
    def mao(self):
        if self.token_atual and self.token_atual[1] == 'CARTA':
            self.consumir('CARTA')
            if self.token_atual and self.token_atual[1] == 'DE':
                self.consumir('DE')
                self.consumir('NAIPE')
            if self.token_atual and self.token_atual[1] == 'E':
                self.consumir('E')
            if self.token_atual and self.token_atual[1] == 'CARTA':
                self.consumir('CARTA')
                if self.token_atual and self.token_atual[1] == 'DE':
                    self.consumir('DE')
                    self.consumir('NAIPE')
            if self.token_atual and self.token_atual[1] == 'SUIT':
                self.consumir('SUIT')
    
#   jogadas ::= primeira_jogada {jogada}
    def jogadas(self):
        self.primeira_jogada()
        while self.token_atual and self.token_atual[1] in JOGADORES and self.tokens[self.pos+1] != 'VERBO_RESULTADO':
            self.jogada()

    #   primeira_jogada ::= [NO] ESTAGIO jogada
    def primeira_jogada(self):
        if self.token_atual and self.token_atual[1] == 'NO':
            self.consumir('NO')
        if self.token_atual and self.token_atual[1] == 'ESTAGIO':
            self.consumir('ESTAGIO')
            self.jogada()
    
    #   jogada ::= jogador acao_jogador PONTO
    def jogada(self):
        self.jogador()
        self.acao_jogador()
        self.consumir('PONTO')

    #   acao_jogador ::= ACAO JOGADOR_ATIVA [QUANTIDADE_FICHAS|POTE]
    #                   | ACAO JOGADOR_PASSIVA
    def acao_jogador(self):
        if self.token_atual and self.token_atual[1] == 'ACAO_JOGADOR_ATIVA':
            self.consumir('ACAO_JOGADOR_ATIVA')
            if self.token_atual and (self.token_atual[1] == 'QUANTIDADE_FICHAS' or self.token_atual[1] == 'POTE'):
                self.consumir(self.token_atual[1])
        elif self.token_atual and self.token_atual[1] == 'ACAO_JOGADOR_PASSIVA':
            self.consumir('ACAO_JOGADOR_PASSIVA')
        
    #resultado      ::= jogador VERBO_RESULTADO [QUANTIDADE_FICHAS|POTE] PONTO
    def resultado(self):
        if self.token_atual and self.token_atual[1] in JOGADORES:
            self.jogador()
        self.consumir('VERBO_RESULTADO')
        if self.token_atual and self.token_atual[1] in ['QUANTIDADE_FICHAS', 'POTE']:
            self.consumir(self.token_atual[1])  # tratado como verbo no lexer
        self.consumir('PONTO')

        
def sintax(tokens_com_linha, erro, caminho_saida):
    if erro:
        with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write(erro + "\n")
                out.write("Fim da compilacao\n")
    else:
        parser = PokerParser(tokens_com_linha)
        try:
            parser.historia()
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write("Fim da compilacao\n")
            print("História sintaticamente válida!")
            return None
        except SyntaxError as e:
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write(str(e) + "\n")
                out.write("Fim da compilacao\n")
            print(str(e))
            return e



if __name__ == "__main__":
    if len(sys.argv) >= 3:
        caminho_arquivo = sys.argv[1]
        caminho_saida = sys.argv[2]
    else:
        caminho_arquivo = ENTRADA
        caminho_saida = SAIDA
    
    caminho_saida_alt = caminho_saida.replace('.txt', '_alt.txt')
    
    tokens, tokens_com_linha, erro = lexer_module.lexico(caminho_arquivo, caminho_saida, caminho_saida_alt)
    
    sintax(tokens_com_linha, erro, caminho_saida)