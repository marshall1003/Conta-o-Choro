import Analisador_lexico as lexer_module
import Analisador_sintatico as sintax_module
import os
import sys

FILE = "Exemplo.txt"
ENTRADA = os.path.join(r"C:\Users\maria\Desktop\Marciel\Redes\Conta-o-Choro\T6",FILE)
SAIDA = os.path.join(r"C:\Users\maria\Desktop\Marciel\Redes\Conta-o-Choro\T6", FILE.replace('.txt', '_out.txt'))

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
            if self.tokens[i][1].lower() in sintax_module.POSICOES:
                
                tok1 = self.tokens[i]      # posição como sujeito
                tok2 = self.tokens[i + 1]  # verbo "estava"
                tok3 = self.tokens[i + 2]  # "no"
                tok4 = self.tokens[i + 3]  # posição como destino

                if tok1[1].lower() in sintax_module.POSICOES and tok2[0].lower() == 'estava' and tok3[1] == 'NO':
                    if tok4[1].lower() in sintax_module.POSICOES:
                        self.erros.append(f"Linha {tok1[2]} - Redundância posicional: '{tok1[0]} estava no {tok4[0]}'")

    def analisar(self):
        self.verificar_redundancia_posicional()
        return self.erros

# Exemplo de uso:
if __name__ == '__main__':
    
    if len(sys.argv) >= 3:
        caminho_arquivo = sys.argv[1]
        caminho_saida = sys.argv[2]
    else:
        caminho_arquivo = ENTRADA
        caminho_saida = SAIDA
    
    caminho_saida_alt = caminho_saida.replace('.txt', '_alt.txt')
    
    tokens, tokens_com_linha, erro_lex = lexer_module.lexico(caminho_arquivo, caminho_saida, caminho_saida_alt)
    erro_sintax = sintax_module.sintax(tokens_com_linha, erro_lex, caminho_saida)
    
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