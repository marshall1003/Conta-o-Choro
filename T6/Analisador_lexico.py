import re
import os
import sys


    # Caminhos padrão
ENTRADA = r"C:\Users\maria\Desktop\Marciel\Redes\Conta-o-Choro\T6\Exemplo.txt"
SAIDA = r"C:\Users\maria\Desktop\Marciel\Redes\Conta-o-Choro\T6\Exemplo_lex_out.txt"


TOKENS = [
    ('EU', r'\beu\b'),
    ('ELE', r'\bele\b'),
    ('VILAO', r'\b(o )?vilao\b'),
    ('VERBO_POSSE', r'\b(estava|tinha)\b'),
    #('VERBO_SITUACIONAL', r'\b(|fiquei|fic(ou|ar))|f(u|o)i))\b'),
    ('VERBO_RESULTADO', r'\b(ganh(ei|ou)|perd(i|eu))\b'),
    ('VERBO_IRRELEVANTE', r'\b(pens(ar|ei|ou)|ach(ar|ei|ou))\b'),
    ('NEGACAO', r'\bnao\b'),
    ('ACAO_JOGADOR_ATIVA', r'\b(apost(ei|ou|ar)|(c-)?bet(ar|ei|ou)|aument(ei|ou)|blef(ei|ou|ar)|(d(ar |ei |eu ))?all in)\b'),
    ('ACAO_JOGADOR_PASSIVA', r'\b(pag(uei|ou|ar)|desisti(u|r)?d(ar|ei|eu) mesa|(d(ar |ei |eu ))?check|check(ar|ei|ou)|fold(ar|ei|ou)?)\b'),
    ('QUANTIDADE_FICHAS', r'\b\d+(\.\d+)?(\s)?(blind(s)|pingo(s)|bb(s)?|%( do pote)?|usd|dolar(es)?|brl|rea(l|is))\b'),
    ('ESTAGIO', r'\b(pre(-)?flop|flop|turn|river)\b'),
    ('ANTE', r'\bante\b'),
    ('POTE', r'\b(o )?pote\b'),
    ('BTN', r'\b(o )?(botao|btn)\b'),
    ('CO', r'\b(o )?(cutoff|co)\b'),
    ('BB', r'\b(o )?(big blind|bb)\b'),
    ('SB', r'\b(o )?(small blind|sb)\b'),
    ('UTG', r'\b(o )?(under the gun|utg)\b'),
    ('UTG+1', r'\b(o )?(under the gun|utg)( mais um|\+1)\b'),
    ('MP', r'\b(o )?(middle position|mp)\b'),
    ('HJ', r'\b(o )?(hi-jack|hj)\b'),
    ('LJ', r'\b(o )?(lo-jack|lj)\b'),
    ('CARTA', r'\b(as|rei|dama|valete|dez|nove|oito|sete|seis|cinco|quatro|tres|dois|duque)\b'),
    ('NAIPE', r'\b(espadas|paus|copas|ouros)\b'),
    ('SUIT', r'\b(suited|naipado|offsuit)\b'),
    ('COM', r'\bcom\b'),
    ('E', r'\be\b'),
    ('ENTAO', r'\bentao\b'),
    ('MAS', r'\bmas\b'),
    ('PORQUE', r'\bporque\b'),
    ('QUE', r'\bque\b'),
    ('NA', r'\bna\b'),
    ('NO', r'\bno\b'),
    ('PRA', r'\bpra\b'),
    ('PARA', r'\bpara\b'),
    ('DE', r'\bde\b'),
    ('DO', r'\bdo\b'),
    ('OUT', r'\bout(s)?\b'),
    ('FORCA_MAO', r'\b(high|alto|(maior |segundo |terceiro |quarto )?par|(top |second |third |forth |over |bottom )?pair|dois pares|two pair|trinca|set|sequencia|straight|flush|full house|straight flush)\b'),
    ('DRAW', r'\b(broca|ponta|duas pontas|gutter|double gutter|draw)\b'),
    ('NUM_INT', r'\b\d+\b'),
    ('NUM_REAL', r'\b\d+\.\d+\b'),
    ('CADEIA', r'"([^"\\]|\\.)*"'),
    ('.', r'\.'),
    (',', r','),
    ('WS', r'[ \t\n\r]+'),
]


def lexer(codigo):
    pos = 0
    tokens = []
    tokens_com_linha = []
    codigo_len = len(codigo)
    linha_atual = 1

    while pos < codigo_len:
        match = None
        for token_type, regex in TOKENS:
            pattern = re.compile(regex)
            match = pattern.match(codigo, pos)
            if match:
                valor = match.group(0)
                if token_type != 'WS':  # Ignorar espaços
                    tokens.append((valor.lower(), token_type))
                    tokens_com_linha.append((valor.lower(), token_type, linha_atual))
                pos = match.end()
                linha_atual += valor.count('\n')
                break
        if not match:
            return tokens, tokens_com_linha, f"Erro léxico na linha {linha_atual}: Símbolo não reconhecido '{codigo[pos]}'" 
    return tokens, tokens_com_linha, None

def lexico(caminho_arquivo, caminho_saida, caminho_saida_alt=None):
    
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        codigo = f.read().lower()

    tokens, tokens_com_linha, erro = lexer(codigo)

    with open(caminho_saida, "w", encoding="utf-8") as out:
        for matched_text, token_type in tokens:
            out.write(f"<'{matched_text}',{token_type}>\n")
            
    with open(caminho_saida_alt, "w", encoding="utf-8") as out:
        for matched_text, token_type, linha in tokens_com_linha:
            out.write(f"<'{matched_text}',{token_type},{linha}>\n")
            
        if erro:
            out.write(erro + "\n")
            print(erro)
        else:
            print("Código léxicamente correto.")
        
    return tokens, tokens_com_linha, erro

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        caminho_arquivo = sys.argv[1]
        caminho_saida = sys.argv[2]
        
    else:
        caminho_arquivo = ENTRADA
        caminho_saida = SAIDA
    
    caminho_saida_alt = caminho_saida.replace('.txt', '_alt.txt')
    
    lexico(caminho_arquivo, caminho_saida, caminho_saida_alt)