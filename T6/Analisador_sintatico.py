import re
import os
import sys
import Analisador_lexico as lexer_module

# Caminhos padrão
ENTRADA = r".\Exemplo\Input\Exemplo.txt"
SAIDA = r".\Exemplo\Output\Exemplo_out.txt"

INFINITY_STACK = 999999999
ESTAGIOS = [
    'pre-flop',
    'flop',
    'turn',
    'river'
]

POSICOES = [
    ('utg', 3),
    ('utg+1', 4),
    ('lj', 5),
    ('hj', 6),
    ('mp', 7),
    ('co', 8),
    ('btn', 9),
    ('sb', 1),
    ('bb', 2)
]

POSICOES_PREFLOP = [
    ('utg', 1),
    ('utg+1', 2),
    ('lj', 3),
    ('hj', 4),
    ('mp', 5),
    ('co', 6),
    ('btn', 7),
    ('sb', 8),
    ('bb',9)
]


JOGADORES = [
    'EU',
    'ELE',
    'VILAO'
]


#gramatica simplificada para o jogo de poker

#   historia ::= introducao {jogadas} {resultado}

#   introducao ::= JOGADOR VERBO_POSSE situacoes
#   situacoes ::= situacao [E situacao]
#   situacao ::= COM quantidade_fichas [NO posicao] [COM mao]
#                | [COM quantidade_fichas] NO posicao [COM mao]
#                | [COM quantidade_fichas] [NO posicao] COM mao
#   jogador ::= EU | ELE | VILAO | posicao
#   mao ::= CARTA [DE NAIPE] [E] CARTA [DE NAIPE] | CARTA [E] CARTA [SUIT] 
#   posicao ::= BTN | CO | BB | SB | UTG | UTG+1 | MP | HJ | LJ

#   jogadas ::= primeira_jogada {jogada}
#   primeira_jogada ::= [NO] ESTAGIO jogada
#   jogada ::= jogador acao_jogador [E jogador acao_jogador] PONTO
#   acao_jogador ::= ACAO JOGADOR_ATIVA [quantidade_fichas|POTE] 
#                   | ACAO JOGADOR_PASSIVA
#   ESTAGIO ::= pre-flop | flop | turn | river

#resultado      ::= jogador VERBO_RESULTADO [quantidade_fichas|POTE] PONTO

def posicoes_txt():
    posicoes = []
    for posicao in POSICOES:
        posicoes.append(posicao[0].upper())
    return posicoes

class PokerParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[self.pos] if self.tokens else None
        self.jogadas_registradas = []
        self.stage = None
        self.player_atual = None
        self.minha_posicao = None
        self.acao = None
        self.quantia = None
        self.pote = 0
        self.posicao_do_vilao = []
        self.stacks = []
        self.players = []

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
        while self.token_atual and (self.token_atual[1] == 'NO' or self.token_atual[1] in ESTAGIOS):
            self.jogadas()
        if self.token_atual and (self.token_atual[1] in JOGADORES or self.token_atual[1] in posicoes_txt()):
            self.resultado()
        return self.jogadas_registradas

    #   introducao ::= JOGADOR VERBO_POSSE situacoes    
    def introducao(self):
        while self.token_atual and self.token_atual[1] in JOGADORES:
            self.player_atual = self.token_atual[1]
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


    def add_player(self, stack):
        if len(self.players) == 0:
            self.players.append({
                            "jogador":self.player_atual,
                            "stack": stack
            })
            return False
        
        for jogador in self.players:
            if self.player_atual == jogador['jogador']:
                return False
        
        self.players.append({
                            "jogador":self.player_atual,
                            "stack": stack
            })
                
                
    #   situacao ::= COM quantidade_fichas [NO posicao] [COM mao]
    #                | [COM quantidade_fichas] NO posicao [COM mao]
    #                | [COM quantidade_fichas] [NO posicao] COM mao
    def situacao(self):
        stack = None
        if self.token_atual and self.token_atual[1] == 'COM':
            if self.tokens[self.pos + 1][1] in ['NUM_INT', 'NUM_REAL']:
                self.consumir('COM')
                stack = self.quantidade_fichas()
                self.add_player(stack)
                if self.token_atual and self.token_atual[1] == "UNIDADE_POTE":
                    self.consumir('UNIDADE_POTE')
                else:
                    self.consumir('UNIDADE')
                if self.token_atual and self.token_atual[1] == 'NO':
                    self.consumir('NO')
                    self.posicao()
                if self.token_atual and self.token_atual[1] == 'COM':
                    self.consumir('COM')
                    self.mao()
            else:
                self.consumir('COM')
                self.mao()
                self.add_player(INFINITY_STACK)
        else: 
            if self.token_atual and self.token_atual[1] == 'NO':
                    self.consumir('NO')
                    self.posicao()
                    if self.token_atual and self.token_atual[1] == 'COM':
                        self.consumir('COM')
                        self.mao()
            self.add_player(INFINITY_STACK)
        
    #   jogador ::= EU | ELE | VILAO [DA posicao] | posicao
    def jogador(self):
        for jogador in JOGADORES:
            if self.token_atual and self.token_atual[1] == jogador.upper():
                self.consumir(jogador.upper())
                if self.token_atual and self.token_atual[1] == 'DA':
                    self.consumir('DA')
                    self.posicao()
                break
            
    #   posicao ::= BTN | CO | BB | SB | UTG | UTG+1 | MP | HJ | LJ    
    def posicao(self):
        for posicao in posicoes_txt():
            if self.token_atual and self.token_atual[1] == posicao.upper():
                self.consumir(posicao.upper())
                break

    #   mao ::= CARTA [DE NAIPE] [E] CARTA [DE NAIPE] | CARTA [E] CARTA [SUIT] | 'par' DE CARTA
    def mao(self):
        if self.token_atual and self.token_atual[0] == 'par':
            self.consumir('FORCA_MAO')
            self.consumir('DE')
            self.consumir('CARTA')
        else:
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
        while self.token_atual and self.token_atual[1] in JOGADORES and self.tokens[self.pos+1] != 'VERBO_RESULTADO' and not(self.token_atual[1] == "NO" or self.token_atual[1] in ESTAGIOS):
            self.jogada()

    #   primeira_jogada ::= [NO] ESTAGIO jogada
    def primeira_jogada(self):
        if self.token_atual and self.token_atual[1] == 'NO':
            self.consumir('NO')
        
        self.stage = self.token_atual[0]
        self.consumir('ESTAGIO')
        self.jogada()
    
    #   jogada ::= jogador acao_jogador PONTO
    def jogada(self):
        self.player_atual = self.token_atual[1]
        self.jogador()
        self.acao_jogador()
        for jogador in self.players:
            if jogador['jogador'] == self.player_atual:
                 jogador['stack'] -= self.quantia
                 stack = jogador['stack'] 
        self.jogadas_registradas.append({
            'estagio': self.stage,
            'jogador':self.player_atual,
            'acao': self.acao,
            'quantia': self.quantia,
            'pote': self.pote,
            'stack': stack
            })
        
        self.consumir('.')

    #   acao_jogador ::= ACAO JOGADOR_ATIVA [quantidade_fichas|POTE]
    #                   | ACAO JOGADOR_PASSIVA
    #                   | ALL_IN
    def acao_jogador(self):
        if self.token_atual and self.token_atual[1] == 'ALL_IN':
            self.acao = self.token_atual[1]
            self.consumir('ACAO_JOGADOR_ATIVA')
            
        elif self.token_atual and self.token_atual[1] == 'ACAO_JOGADOR_ATIVA':
            self.acao = self.token_atual[1]
            self.consumir('ACAO_JOGADOR_ATIVA')
            if self.token_atual and self.token_atual[1] in ['NUM_INT', 'NUM_REAL']:
                self.quantidade_fichas()
            else:
                if self.token_atual and self.token_atual[1] == 'POTE':
                    self.quantia += self.pote    
                    self.consumir(self.token_atual[1])
        elif self.token_atual and self.token_atual[1] == 'ACAO_JOGADOR_PASSIVA':
            self.acao = self.token_atual[1]
            self.consumir('ACAO_JOGADOR_PASSIVA')
            self.pote += self.quantia

    #quantidade_fichas ::= ('NUM_INT'|'NUM_REAL') UNIDADE|UNIDADE_POTE
    def quantidade_fichas(self):
        if  self.token_atual and self.token_atual[1] == 'NUM_INT':
            quantia = int(self.token_atual[0])
            self.consumir('NUM_INT')
        else:
            quantia = float(self.token_atual[0])
            self.consumir('NUM_REAL')

        if self.stage:
            if self.token_atual and self.token_atual[1] == 'UNIDADE_POTE':
                self.quantia = quantia*self.pote
                self.pote += self.quantia
            else:
                self.quantia = quantia
                self.pote += self.quantia

            self.consumir(self.token_atual[1])
        else:
            return quantia
        

    #resultado      ::= jogador VERBO_RESULTADO [QUANTIDADE_FICHAS|POTE] PONTO
    def resultado(self):
        if self.token_atual and self.token_atual[1] in JOGADORES:
            self.jogador()
        self.consumir('VERBO_RESULTADO')
        if self.token_atual and self.token_atual[1] in ['QUANTIDADE_FICHAS', 'POTE']:
            self.consumir(self.token_atual[1])  # tratado como verbo no lexer
        self.consumir('.')

        
def sintax(caminho_arquivo, caminho_saida):
    caminho_saida_alt = caminho_saida.replace('.txt', '_alt.txt')
    caminho_saida_lexico = caminho_saida.replace('_out.txt', '_lexico.txt')
    tokens, tokens_com_linha, erro = lexer_module.lexico(caminho_arquivo, caminho_saida_lexico, caminho_saida_alt)
    
    if erro:
        with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write(erro + "\n")
                out.write("Fim da compilacao\n")
        return erro
    else:
        parser = PokerParser(tokens_com_linha)
        try:
            jogadas = parser.historia()
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write("Fim da compilacao\n")
            print("História sintaticamente válida!")
            return None, jogadas
        except SyntaxError as e:
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write(str(e) + "\n")
                out.write("Fim da compilacao\n")
            print(str(e))
            return e



if __name__ == "__main__":
    if len(sys.argv) >= 3:
        if  sys.argv[1] == "Demo":
            for file in os.listdir(r".\Exemplo\Input"):
                caminho_arquivo = os.path.join(r".\Exemplo\Input", file)
                caminho_saida = os.path.join(r".\Exemplo\Output", file.replace('.txt', '_out.txt'))
                sintax(caminho_arquivo, caminho_saida)
        else:
            caminho_arquivo = sys.argv[1]
            caminho_saida = sys.argv[2]
            sintax(caminho_arquivo, caminho_saida)
                
    else:
        caminho_arquivo = ENTRADA
        caminho_saida = SAIDA
        sintax(caminho_arquivo, caminho_saida)