import Analisador_lexico as lexer_module
import Analisador_sintatico as sintax_module
import os
import sys


# Caminhos padrão
ENTRADA = r".\Exemplo\Input\Exemplo.txt"
SAIDA = r".\Exemplo\Output\Exemplo_out.txt"
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
        for i in range(len(self.tokens) - 3):
            if self.tokens[i][1] in sintax_module.posicoes_txt():
                
                tok1 = self.tokens[i]      # posição como sujeito
                tok2 = self.tokens[i + 1]  # verbo "estava"
                tok3 = self.tokens[i + 2]  # "no"
                tok4 = self.tokens[i + 3]  # posição como destino

                if tok1[1] in sintax_module.posicoes_txt() and tok2[0].lower() == 'estava' and tok3[1] == 'NO':
                    if tok4[1] in sintax_module.posicoes_txt():
                        self.erros.append(f"Linha {tok1[2]} - Redundância posicional: '{tok1[0]} estava no {tok4[0]}'")

    def verificar_ordem_jogadores(self):
        pass


    def analisar(self):
        self.verificar_redundancia_posicional()
        return self.erros

def semantic(caminho_arquivo, caminho_saida):

    caminho_saida_alt = caminho_saida.replace('.txt', '_alt.txt')
    caminho_saida_lexico = caminho_saida.replace('_out.txt', '_lexico.txt')
    caminho_saida_sintax = caminho_saida.replace('_out.txt', '_sintax.txt')
    tokens, tokens_com_linha, erro = lexer_module.lexico(caminho_arquivo, caminho_saida_lexico, caminho_saida_alt)
    erro_sintax = sintax_module.sintax(caminho_arquivo, caminho_saida_sintax)
    if erro_sintax:
        pass
    else:
        parser = PokerSemantico(tokens_com_linha)
        erros_semanticos = parser.analisar()
        if erros_semanticos:
            with open(caminho_saida, "w", encoding="utf-8") as out:
                for mensagem in erros_semanticos:
                    out.write(mensagem + "\n")
                out.write("Fim da compilacao\n")
        else:
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write("Fim da compilacao\n")
            print("História semanticamente válida!")

# Exemplo de uso:
if __name__ == '__main__':
    
    if  sys.argv[1] == "Demo":
            for file in os.listdir(r".\Exemplo\Input"):
                caminho_arquivo = os.path.join(r".\Exemplo\Input", file)
                caminho_saida = os.path.join(r".\Exemplo\Output", file.replace('.txt', '_out.txt'))
                semantic(caminho_arquivo, caminho_saida)
    elif len(sys.argv) >= 3:
            caminho_arquivo = sys.argv[1]
            caminho_saida = sys.argv[2]
            semantic(caminho_arquivo, caminho_saida)
    else:
        caminho_arquivo = ENTRADA
        caminho_saida = SAIDA
        semantic(caminho_arquivo, caminho_saida)