import Analisador_lexico as lexer_module
import Analisador_sintatico as sintax_module
import os
import sys
import json

# Caminhos padrão
BASE_DIR = os.path.dirname(__file__)
ENTRADA = os.path.join(BASE_DIR, r"Exemplo\Input\Exemplo - Tudo certo.txt")
SAIDA = os.path.join(BASE_DIR, r"Exemplo\Output\Exemplo - Tudo certo_out.txt")
sys.argv = [r'C:\Users\628069\Documents\GitHub\Conta-o-Choro\T6\Analisador_semantico.py', 'Demo']


class ErroSemantico(Exception):
    def __init__(self):
        super().__init__("Ocorreram erros semânticos")
        self.mensagens = []

    def adicionar(self, mensagem):
        self.mensagens.append(mensagem)

    def __str__(self):
        return "\n".join(self.mensagens)


class PokerSemantico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.erros = []

    def verificar_redundancia_posicional(self):
        if self.erros:
            return
        for i in range(len(self.tokens) - 3):
            if self.tokens[i][1] in sintax_module.posicoes_txt():
                
                tok1 = self.tokens[i]      # posição como sujeito
                tok2 = self.tokens[i + 1]  # verbo "estava"
                tok3 = self.tokens[i + 2]  # "no"
                tok4 = self.tokens[i + 3]  # posição como destino

                if tok1[1] in sintax_module.posicoes_txt() and tok2[0].lower() == 'estava' and tok3[1] == 'NO':
                    if tok4[1] in sintax_module.posicoes_txt():
                        self.erros.append(f"Linha {tok1[2]} - Redundância posicional: '{tok1[0]} estava no {tok4[0]}'")

    def verificar_ordem_jogadores(self, historia):
        if self.erros:
            return
        jogador_anterior = None
        stage = None
        for jogada in historia:
            if stage is None or stage != jogada['estagio']:
                stage = jogada['estagio']
                jogador_anterior = None
            elif jogador_anterior:
                if jogada['jogador'] == jogador_anterior:
                    self.erros.append(f"Linha {jogada['linha']} - Jogador '{jogada['jogador']}' jogou duas vezes seguidas")
                else:
                    jogador_anterior = jogada['jogador']
            else:
                jogador_anterior = jogada['jogador']

    def verificar_duplicidade_posicao(self, jogadores):
        if self.erros:
            return
        posicoes = []
        for jogador in jogadores:
            if len(posicoes) == 0:
                posicoes.append(jogador['posicao'])
            else: 
                if jogador['posicao'] not in posicoes:
                    posicoes.append(jogador['posicao'])
                else:
                    self.erros.append(f"Há mais de um '{jogador['posicao']}' na mesa!")
        
    def verificar_jogar_fora_de_ordem(self, historia, jogadores):
        if self.erros:
            return
        
        posicoes_em_jogo = []
        player_finalizado = []
        agressor = None
        respostas = 0
        jogador_atual = None
        for jogador in jogadores:
            for pos in sintax_module.POSICOES:
                if jogador['posicao'] == pos[0].upper():
                    posicoes_em_jogo.append(pos)
                    break
                
        posicoes_em_jogo = sorted(posicoes_em_jogo, key=lambda x: x[1])  # Ordena por posição
        stage = None
        
        for jogada in historia:
            for jogador in jogadores:
                if jogador['jogador'] == jogada['jogador']:
                    jogada_pos = jogador['posicao'].upper()
                    break

            if stage is None or stage != jogada['estagio']:
                primeira_acao = True
                agressor = None
                respostas = 0
                stage = jogada['estagio']
                jogador_atual = jogada_pos
                if agressor:
                    rodada_completa = len(posicoes_em_jogo) - 1
                else:
                    rodada_completa = len(posicoes_em_jogo)
                if respostas != rodada_completa and stage != 'pre-flop' and not primeira_acao:
                    self.erros.append(f"Linha {jogada['linha']} - Avançou para {stage} de forma indevida")
            

            if jogador_atual != jogada_pos:
                self.erros.append(f"Linha {jogada['linha']} - Jogador '{jogada['jogador']}' jogou fora de ordem")
            else:
                if jogada['acao'] in ['ALL_IN', 'ALL_IN_CALL', 'FOLD']:
                    if jogada_pos not in player_finalizado:
                        player_finalizado.append(jogada_pos)
                        for i in posicoes_em_jogo:
                            if i[0].upper() == jogada_pos:
                                jogador_atual = next_player(posicoes_em_jogo, jogador_atual)
                                posicoes_em_jogo.remove(i)
                                break
                    else:
                        if jogada['acao'] == 'ALL_IN':
                            agressor = jogada_pos
                            respostas = 0
                        elif jogada['acao'] == 'ALL_IN_CALL':
                            respostas += 1
                        if jogada['acao'] == 'FOLD':
                            self.erros.append(f"Linha {jogada['linha']} - Jogador '{jogada['jogador']}' já havia desistido")
                        else:
                            self.erros.append(f"Linha {jogada['linha']} - Jogador '{jogada['jogador']}' já estava em all in")
                        break
                else:
                    if jogada['acao'] in ['ACAO_JOGADOR_ATIVA']:
                        agressor = jogada_pos
                        respostas = 0
                    else:
                        respostas += 1
                    jogador_atual = next_player(posicoes_em_jogo, jogador_atual)
            

    def analisar(self, historia, jogadores):
        self.verificar_redundancia_posicional()
        self.verificar_duplicidade_posicao(jogadores)
        self.verificar_ordem_jogadores(historia)
        self.verificar_jogar_fora_de_ordem(historia, jogadores)
        return self.erros

def next_player(posicoes, jogador_atual):
        if not posicoes:
            return None
        if jogador_atual is None:
            return posicoes[0][0].upper()
        try:
            for i in posicoes:
               pos = i[0].upper()
               if   pos == jogador_atual:
                    index = posicoes.index(i)
                    return posicoes[(index + 1) % len(posicoes)][0].upper()
        except ValueError:
            return posicoes[0][0].upper()  # Retorna o primeiro jogador se o atual não for encontrado

def semantic(caminho_arquivo, caminho_saida):

    caminho_saida_alt = caminho_saida.replace('.txt', '_alt.txt')
    try:
        caminho_saida_lexico = caminho_saida.replace('_semantic.txt', '_lexico.txt')
    except:
        caminho_saida_lexico = caminho_saida.replace('.txt', '_lexico.txt')

    try:
        caminho_saida_sintax = caminho_saida.replace('_semantic.txt', '_sintax.txt')
    except:
        caminho_saida_sintax = caminho_saida.replace('.txt', '_sintax.txt')

    tokens, tokens_com_linha, erro_lex = lexer_module.lexico(caminho_arquivo, caminho_saida_lexico, caminho_saida_alt, False)
    
    if erro_lex:
        print("Conta essa história direito!")
        return None, None
    
    erro_sintax, historia, jogadores = sintax_module.sintax(caminho_arquivo, caminho_saida_sintax)
    
    if erro_sintax:
        print("Conta essa história direito!")
    else:
        parser = PokerSemantico(tokens_com_linha)
        erros_semanticos = parser.analisar(historia, jogadores)
        if erros_semanticos:
            with open(caminho_saida, "w", encoding="utf-8") as out:
                for mensagem in erros_semanticos:
                    out.write(mensagem + "\n")
                    print(mensagem)
                
                print("Conta essa história direito!")
                out.write("Conta essa história direito!\n")
        else:
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write("Boa! Sua história está redonda!\n")

            print("Semântica: OK!")
            return historia, jogadores

# Exemplo de uso:
if __name__ == '__main__':
    size = len(sys.argv)
    if len(sys.argv) > 1:
        if  sys.argv[1] == "Demo":
                for file in os.listdir(os.path.join(BASE_DIR, r"Exemplo\Input")):
                    caminho_arquivo = os.path.join(BASE_DIR, r"Exemplo\Input", file)
                    caminho_saida = os.path.join(BASE_DIR, r"Exemplo\Output",file.replace('.txt', ''), file.replace('.txt', '_semantic.txt'))
                    print(f"Analisando historia: {os.path.basename(caminho_arquivo)}")
                    semantic(caminho_arquivo, caminho_saida)
                    print("")
        elif len(sys.argv) >= 3:
                caminho_arquivo = sys.argv[1]
                caminho_saida = sys.argv[2]
                semantic(caminho_arquivo, caminho_saida)
        else:
            caminho_arquivo = ENTRADA
            caminho_saida = SAIDA
            semantic(caminho_arquivo, caminho_saida)
    else:
        caminho_arquivo = ENTRADA
        caminho_saida = SAIDA
        semantic(caminho_arquivo, caminho_saida)
    
    #remove _alt files
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, r"Exemplo\Output")):
        for file in files:
            if "_alt" in file:
                arquivo_remover = os.path.join(root, file)
                try:
                    os.remove(arquivo_remover)
                    #print(f"Removido: {os.path.basename(arquivo_remover)}")
                except Exception as e:
                    print(f"Erro ao remover {os.path.basename(arquivo_remover)}: {e}")