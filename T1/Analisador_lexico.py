import re
import os
import sys


    # Caminhos padrão
ENTRADA = r"C:\Users\maria\Desktop\Marciel\Compiladores\Testes\casos-de-teste\1.casos_teste_t1\entrada\34-algoritmo_8-1_apostila_LA_erro_linha_20.txt"
SAIDA = r"C:\Users\maria\Desktop\Marciel\Compiladores\T1\testes\34-algoritmo_8-1_apostila_LA_erro_linha_20.txt"

# Definição simplificada de tokens baseada em uma gramática típica de Linguagem Algorítmica (LA)
TOKENS = [
    # Palavras reservadas (um token para cada)
    ('programa', r'\bprograma\b'),
    ('inicio', r'\binicio\b'),
    ('fim', r'\bfim\b'),
    ('algoritmo', r'\balgoritmo\b'),
    ('fim_algoritmo', r'\bfim_algoritmo\b'),
    ('leia', r'\bleia\b'),
    ('escreva', r'\bescreva\b'),
    ('se', r'\bse\b'),
    ('e', r'\be\b'),
    ('ou', r'\bou\b'),
    ('nao', r'\bnao\b'),
    ('fim_se', r'\bfim_se\b'),
    ('caso', r'\bcaso\b'),
    ('fim_caso', r'\bfim_caso\b'),
    ('seja', r'\bseja\b'),
    ('entao', r'\bentao\b'),
    ('senao', r'\bsenao\b'),
    ('enquanto', r'\benquanto\b'),
    ('fim_enquanto', r'\bfim_enquanto\b'),
    ('registro', r'\bregistro\b'),
    ('fim_registro', r'\bfim_registro\b'),
    ('faca', r'\bfaca\b'),
    ('para', r'\bpara\b'),
    ('fim_para', r'\bfim_para\b'),
    ('ate', r'\bate\b'),
    ('inteiro', r'\binteiro\b'),
    ('real', r'\breal\b'),
    ('literal', r'\bliteral\b'),
    ('logico', r'\blogico\b'),
    ('verdadeiro', r'\bverdadeiro\b'),
    ('falso', r'\bfalso\b'),
    ('declare', r'\bdeclare\b'),
    ('tipo', r'\btipo\b'),
    ('constante', r'\bconstante\b'),
    ('var', r'\bvar\b'),
    ('funcao', r'\bfuncao\b'),
    ('fim_funcao', r'\bfim_funcao\b'),
    ('procedimento', r'\bprocedimento\b'),
    ('fim_procedimento', r'\bfim_procedimento\b'),
    ('retorne', r'\bretorne\b'),

    # Operadores relacionais
    ('<=', r'<='),
    ('>=', r'>='),
    ('<>', r'<>'),
    ('=', r'='),
    ('<', r'<'),
    ('>', r'>'),

    # Operadores aritméticos
    ('+', r'\+'),
    ('-', r'-'),
    ('*', r'\*'),
    ('/', r'/'),
    ('%', r'%'),

    # Operador de atribuição
    ('<-', r'<-'),

    # Delimitadores
    ('(', r'\('),
    (')', r'\)'),
    ('[', r'\['),
    (']', r'\]'),
    (',', r','),
    (';', r';'),
    (':', r':'),

    
    # Símbolos especiais
    ('..', r'\.\.'), #Agrupador
    ('.', r'\.'), #atributo/função de classe
    ('^', r'\^'), #ponteiro
    ('&', r'\&'), #referência


    # Literais e identificadores
    ('NUM_REAL', r'\d+\.\d+'),
    ('NUM_INT', r'\d+'),
    ('CADEIA_INCOMPLETA', r'"([^"])*\n'),              
    ('CADEIA', r'"([^"\\]|\\.)*"'),
    ('IDENT', r'\b[_a-zA-Z][_a-zA-Z0-9]*\b'),

    # Espaço e comentário
    ('ESPACO', r'[ \t\n\r]+'),
    ('COMENTARIO_QUEBRADO', r'\{[^}]*\n'),
    ('COMENTARIO', r'\{[^}]*\}'),

]

def lexer(codigo):
    pos = 0
    tokens = []
    codigo_len = len(codigo)
    linha_atual = 1

    while pos < codigo_len:
        match = None
        for token_type, regex in TOKENS:
            pattern = re.compile(regex)
            match = pattern.match(codigo, pos)
            if match:
                matched_text = match.group(0)

                for other_type, other_regex in TOKENS:
                    other_pattern = re.compile(other_regex)
                    other_match = other_pattern.match(codigo, pos)
                    if other_match and len(other_match.group(0)) > len(matched_text):
                        token_type = other_type
                        matched_text = other_match.group(0)
                        match = other_match
                
                if matched_text.find('\n\n') != -1:
                    pass
                if token_type == 'CADEIA':
                    if matched_text.find('\n') != -1:
                        return tokens, f"Linha {linha_atual}: cadeia literal nao fechada"
                
                if token_type == 'COMENTARIO':
                    if matched_text.find('\n') != -1:
                        return tokens, f"Linha {linha_atual}: comentario nao fechado"
                    
                if token_type == 'COMENTARIO_QUEBRADO':
                    if matched_text.find('\n') != -1:
                        return tokens, f"Linha {linha_atual}: comentario nao fechado"
                if token_type not in ['ESPACO', 'COMENTARIO']:
                    tokens.append((matched_text, token_type))

                linha_atual += matched_text.count('\n')
                pos += len(matched_text)
                break

        if not match:
            simbolo = codigo[pos]
            return tokens, f"Linha {linha_atual}: {simbolo} - simbolo nao identificado"

    return tokens, None

def lexico(caminho_arquivo, caminho_saida):
    
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        codigo = f.read()

    tokens, erro = lexer(codigo)

    with open(caminho_saida, "w", encoding="utf-8") as out:
        for matched_text, token_type in tokens:
            if token_type in ('IDENT', 'NUM_INT', 'NUM_REAL', 'CADEIA'):
                out.write(f"<'{matched_text}',{token_type}>\n")
            else:
                out.write(f"<'{matched_text}','{token_type}'>\n")

        if erro:
            out.write(erro + "\n")
            print(erro)
        else:
            print("Código léxicamente correto.")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        caminho_arquivo = sys.argv[1]
        caminho_saida = sys.argv[2]
    else:
        caminho_arquivo = ENTRADA
        caminho_saida = SAIDA
    
    lexico(caminho_arquivo, caminho_saida)