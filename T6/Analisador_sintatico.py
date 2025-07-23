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

ACAO_JOGADOR_PASSIVA = [
    'FOLD',
    'CALL',
    'CHECK',
    'ALL_IN_CALL'
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
        self.acao = None
        self.quantia = None
        self.posicao_mesa = None
        self.linha = None
        self.pote = 0
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
        return self.jogadas_registradas, self.players

    #   introducao ::= jogador VERBO_POSSE situacoes    
    def introducao(self):
        while self.token_atual and (
            self.token_atual[1] in JOGADORES or 
            self.token_atual[1] in posicoes_txt() or 
            self.token_atual[1] == 'CADEIA'):
            
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
        if self.token_atual and self.token_atual[1] == '.':
            self.consumir('.')


    def add_player(self, stack):
        if len(self.players) == 0:
            self.players.append({
                            "jogador":self.player_atual,
                            'posicao': self.posicao_mesa,
                            "stack": round(stack,1)
            })
            return False
        
        for jogador in self.players:
            if self.player_atual == jogador['jogador']:
                return False
        
        self.players.append({
                            "jogador":self.player_atual,
                            'posicao': self.posicao_mesa,
                            "stack": round(stack, 1)
            })
                
                
    #   situacao ::= COM quantidade_fichas NO posicao [COM mao]
    #                | [COM quantidade_fichas] NO posicao [COM mao]
    def situacao(self):
        self.player_atual = self.token_atual[1]
        self.jogador()
        self.consumir('VERBO_POSSE')
        stack = None
        if self.token_atual and self.token_atual[1] == 'COM':
            self.consumir('COM')
            stack = self.quantidade_fichas()
            if self.token_atual and self.token_atual[1] == "UNIDADE_POTE":
                self.consumir('UNIDADE_POTE')
            else:
                if self.token_atual and self.token_atual[1] == "UNIDADE":
                    self.consumir('UNIDADE')
                else:
                    self.consumir('BB')
            self.consumir('NO')
            self.posicao()
                
            if self.token_atual and self.token_atual[1] == 'COM':
                self.consumir('COM')
                self.mao()
            self.add_player(stack)
        else: 
            self.consumir('NO')
            self.posicao()
            if self.token_atual and self.token_atual[1] == 'COM':
                self.consumir('COM')
                self.mao()
            self.add_player(INFINITY_STACK)
        
    #   jogador ::= EU | ELE | VILAO [DA posicao] | posicao | CADEIA
    def jogador(self):
        if self.token_atual and self.token_atual[1] in JOGADORES:
            self.player_atual = self.token_atual[1]
            self.consumir(self.token_atual[1])
            if self.token_atual and self.token_atual[1] == 'DA':
                self.consumir('DA')
                self.posicao()
        elif self.token_atual and self.token_atual[1] in posicoes_txt():
            self.player_atual = self.token_atual[1]
            self.consumir(self.token_atual[1])
        elif self.token_atual and self.token_atual[1] == 'CADEIA':
            self.player_atual = self.token_atual[0]
            self.consumir('CADEIA')
        else:
            raise SyntaxError(f"Esperado jogador, encontrado {self.token_atual}")
            
    #   posicao ::= BTN | CO | BB | SB | UTG | UTG+1 | MP | HJ | LJ    
    def posicao(self):
        for posicao in posicoes_txt():
            if self.token_atual and self.token_atual[1] == posicao.upper():
                self.posicao_mesa = posicao.upper()
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
        while self.token_atual and (
                self.token_atual[1] in JOGADORES or 
                self.token_atual[1] in posicoes_txt() or 
                self.token_atual[1] == 'CADEIA') and (
                self.tokens[self.pos+1] != 'VERBO_RESULTADO') and not(
                self.token_atual[1] == "NO" or 
                self.token_atual[1] in ESTAGIOS):
            
            self.jogada()

    #   primeira_jogada ::= [NO] ESTAGIO jogada
    def primeira_jogada(self):
        if self.token_atual and self.token_atual[1] == 'NO':
            self.consumir('NO')
        
        self.stage = self.token_atual[0]
        self.consumir('ESTAGIO')
        self.jogada()
    
    def find_player_stack(self):
        for jogador in self.players:
            if jogador['jogador'] == self.player_atual:
                jogador['stack'] -= self.quantia 
                return jogador['stack']
        raise SyntaxError(f"{self.player_atual} não está na mão!")
    #   jogada ::= jogador acao_jogador PONTO
    def jogada(self):
        stack = None
        self.player_atual = self.token_atual[1]
        self.jogador()
        self.acao_jogador()
        stack = self.find_player_stack()            
        if stack is not None:
            self.jogadas_registradas.append({
            'estagio': self.stage,
            'jogador':self.player_atual,
            'acao': self.acao,
            'quantia': round(self.quantia,1),
            'pote': round(self.pote,1),
            'stack': round(stack,1),
            'linha': self.linha
            }) 
        else:
            raise SyntaxError(f"Jogador {self.player_atual} não encontrado na lista de jogadores.")
        if self.token_atual and self.token_atual[1] == '.':    
            self.consumir('.')

    #   acao_jogador ::= ACAO JOGADOR_ATIVA [quantidade_fichas|POTE]
    #                   | ACAO JOGADOR_PASSIVA
    #                   | ALL_IN
    def acao_jogador(self):
        if self.token_atual and self.token_atual[1] == 'ALL_IN':
            self.acao = self.token_atual[1]
            for jogador in self.players:
                if jogador['jogador'] == self.player_atual:
                    self.quantia = jogador['stack']
            self.pote += self.quantia
            self.linha == self.token_atual[2]
            self.consumir('ALL_IN')
            
        elif self.token_atual and self.token_atual[1] == 'ACAO_JOGADOR_ATIVA':
            self.acao = self.token_atual[1]
            self.consumir('ACAO_JOGADOR_ATIVA')
            if self.token_atual and self.token_atual[1] in ['NUM_INT', 'NUM_REAL']:
                self.quantidade_fichas()
            else:
                if self.token_atual and self.token_atual[1] == 'POTE':
                    self.quantia += self.pote
                    self.linha = self.token_atual[2]    
                    self.consumir(self.token_atual[1])
        elif self.token_atual and self.token_atual[1] in ACAO_JOGADOR_PASSIVA:
            
            self.acao = self.token_atual[1]
            self.linha = self.token_atual[2]
            
            try:
                stack = self.find_player_stack()
            except SyntaxError as e:
                raise SyntaxError(f"Erro na linha {self.linha}: {str(e)}")
            
            if self.jogadas_registradas[-1]['quantia'] > stack:
                self.quantia = stack
                self.pote += self.quantia
            
            if self.token_atual[1] == 'ALL_IN_CALL':
                self.quantia = stack
                self.pote += self.quantia
            
            self.consumir(self.token_atual[1])
            self.pote += self.quantia
        else:
            raise SyntaxError(f"Esperado ação do jogador, encontrado {self.token_atual}")
    #quantidade_fichas ::= ('NUM_INT'|'NUM_REAL') UNIDADE|UNIDADE_POTE
    def quantidade_fichas(self):
        if  self.token_atual and self.token_atual[1] == 'NUM_INT':
            quantia = int(self.token_atual[0])
            self.linha = self.token_atual[2]
            self.consumir('NUM_INT')
        elif self.token_atual and self.token_atual[1] == 'NUM_REAL':
            quantia = float(self.token_atual[0])
            self.linha = self.token_atual[2]
            self.consumir('NUM_REAL')
        else:
            if self.token_atual and self.token_atual[1] == 'CARTA':
                raise SyntaxError(f"Linha {self.token_atual[2]} - Jogador '{self.player_atual}' sem posicao")

            raise SyntaxError(f"Linha {self.token_atual[2]} - Esperado quantidade de fichas ou posicao, encontrado {self.token_atual[1]}")

        if self.stage:
            if self.token_atual and self.token_atual[1] == 'UNIDADE_POTE':
                self.quantia = quantia*self.pote
                stack = self.find_player_stack()
                if stack < quantia:
                    raise SyntaxError(f"Jogador {self.player_atual} não tem fichas suficientes para apostar {quantia}. Fichas disponíveis: {stack+quantia}.")
                self.pote += self.quantia
            else:
                self.quantia = quantia
                stack = self.find_player_stack()
                if stack < quantia:
                    raise SyntaxError(f"Jogador {self.player_atual} não tem fichas suficientes para apostar {quantia} {self.token_atual[0]}. Fichas disponíveis: {stack+quantia}.")
                self.pote += self.quantia
            self.linha = self.token_atual[2]
            self.consumir(self.token_atual[1])
        else:
            return quantia
        

    #resultado      ::= jogador VERBO_RESULTADO [QUANTIDADE_FICHAS|POTE] PONTO
    def resultado(self):
        if self.token_atual and (
            self.token_atual[1] in JOGADORES or 
            self.token_atual[1] in posicoes_txt() or 
            self.token_atual[1] == 'CADEIA'):
                
                self.jogador()

        self.consumir('VERBO_RESULTADO')
        if self.token_atual and self.token_atual[1] in ['QUANTIDADE_FICHAS', 'POTE']:
            self.consumir(self.token_atual[1])  # tratado como verbo no lexer
        if self.token_atual and self.token_atual[1] == '.':
            self.consumir('.')

        
def sintax(caminho_arquivo, caminho_saida):
    caminho_saida_alt = caminho_saida.replace('.txt', '_alt.txt')
    caminho_saida_lexico = caminho_saida.replace('_sintax.txt', '_lexico.txt')
    tokens, tokens_com_linha, erro = lexer_module.lexico(caminho_arquivo, caminho_saida_lexico, caminho_saida_alt)
    
    if erro:
        if not os.path.exists(os.path.dirname(caminho_saida)):
            os.makedirs(os.path.dirname(caminho_saida))  
        with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write(erro + "\n")
                out.write("Fim da compilacao\n")
    else:
        parser = PokerParser(tokens_com_linha)
        try:
            jogadas, jogadores = parser.historia()
            if not os.path.exists(os.path.dirname(caminho_saida)):
                os.makedirs(os.path.dirname(caminho_saida))  
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write("Fim da compilacao\n")
            print("Sintax: OK!")
            return None, jogadas, jogadores
        except SyntaxError as e:
            if not os.path.exists(os.path.dirname(caminho_saida)):
                os.makedirs(os.path.dirname(caminho_saida))     
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write(str(e) + "\n")
                out.write("Fim da compilacao\n")
            print(str(e))
            return e, None, None



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