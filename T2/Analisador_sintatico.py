import re
import os
import sys
import Analisador_lexico as lexer_module

# Caminhos padrão
FILE = "27-algoritmo_5-4_apostila_LA_1_erro_linha_18_acusado_linha_19.txt"
ENTRADA = os.path.join(r"C:\Users\maria\Desktop\Marciel\Compiladores\Testes\casos-de-teste\2.casos_teste_t2\entrada", FILE)
SAIDA = os.path.join(r"C:\Users\maria\Desktop\Marciel\Compiladores\T2\testes",FILE)

OP_RELACIONAIS = [
    '=', 
    '<>', 
    '<', 
    '>', 
    '<=', 
    '>=']

COMANDOS = [
    'se',
    'caso',
    'leia',
    'escreva',
    'para',
    'enquanto',
    'faca',
    '<-'
]
 
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[self.pos] if self.tokens else None
        self.token_anterior = 0
        

    def consumir(self, esperado_tipo):
        if self.token_atual and self.token_atual[1] == esperado_tipo:
            self.pos += 1
            self.token_anterior = self.token_atual
            self.token_atual = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        else:
            self.erro_sintatico(esperado_tipo)

    def erro_sintatico(self, esperado=None):
        valor = self.token_atual[0] if self.token_atual else 'EOF'

        if esperado == 'CADEIA':
            if self.token_atual and (self.token_atual[1] == 'CADEIA' or self.token_atual[1] == 'CADEIA_INCOMPLETA'):
                raise SyntaxError(f"Linha {self.token_atual[2]}: cadeia literal nao fechada")
            else:
                raise SyntaxError(f"Linha {self.token_atual[2]}: erro sintatico proximo a {valor}")
        elif valor == 'EOF':
            raise SyntaxError(f"Linha {self.token_anterior[2]+1}: erro sintatico proximo a {valor}")
        
        else:
            raise SyntaxError(f"Linha {self.token_atual[2]}: erro sintatico proximo a {valor}")

    # <programa> ::= declaracoes 'algoritmo' corpo 'fim_algoritmo'
    def programa(self):
        self.declaracoes()
        self.consumir('algoritmo')
        self.corpo()
        self.consumir('fim_algoritmo')

    # <identificador> ::= IDENT
    def identificador(self):
        self.consumir('IDENT')

    # <corpo> ::=  {declaracao_local} {comandos}
    def corpo(self):
        self.declaracao_local()
        body = True
        while body:
            body = self.comando()
        
    # declaracoes ::= {declaracao_loc_global} 
    def declaracoes(self):
        try:
            self.declaracao_local()
        except:
            try:
                self.declaracao_global()
            except:
                pass

    # declaracao_local ::= 'declare' variavel | 'constante' IDENT ':' tipo_basico '=' valor_constante | 'tipo' IDENT ':' tipo
    def declaracao_local(self):
        while self.token_atual and self.token_atual[1] in ['declare', 'constante', 'tipo']:
            if self.token_atual[1] == 'declare':
                self.declaracao_variaveis()
            elif self.token_atual[1] == 'constante':
                self.consumir('constante')
                self.identificador()
                self.consumir(':') 
                self.tipo_basico()
                self.consumir('=')
                self.valor_constante()
            elif self.token_atual[1] == 'tipo':
                self.consumir('tipo')
                self.identificador()
                self.consumir(':')
                self.tipo_basico()
            else:
                self.erro_sintatico()

    # declaracao_global ::= 'procedimento' IDENT "(" [parametros] ")" declaracao_local comando 'fim_procedimento' 
    # | 'funcao' IDENT "(" [parametros] ")" ":" tipo_estendido declaracao_local comando 'fim_funcao'
    def declaracao_global(self):
        if self.token_atual and self.token_atual[1] == 'procedimento':
            try:
                self.consumir('procedimento')
                self.identificador()
                self.consumir('(')
                self.parametros()
                self.consumir(')')
                self.declaracao_local()
                self.comando()
                self.consumir('fim_procedimento')
            except SyntaxError:
                self.erro_sintatico()
        elif self.token_atual and self.token_atual[1] == 'funcao':
            try:
                self.consumir('funcao')
                self.identificador()
                self.consumir('(')
                self.parametros()
                self.consumir(')')
                self.consumir(':')
                self.tipo_estendido()
                self.declaracao_local()
                self.comando()
                self.consumir('fim_funcao')
            except SyntaxError:
                self.erro_sintatico()
        else:
            self.erro_sintatico()

    # <declaracao> ::= <declaracao_variaveis> | ...
    def declaracao(self):
        if self.token_atual[1] == 'declare':
            self.declaracao_variaveis()
        else:
            self.erro_sintatico()

    #variavel ::= identificador (',' identificador)* ':' tipo
    def variavel(self):
        self.identificador()
        while self.token_atual and self.token_atual[1] == ',':
            self.consumir(',')
            self.identificador()
        self.consumir(':')
        self.tipo()

    #tipo ::= registro | tipo_estendido
    def tipo(self):
        if self.token_atual[1] == 'registro':
            try:
                self.consumir('registro')
                while self.token_atual and self.token_atual[1] == 'IDENT':
                    self.variavel()
                self.consumir('fim_registro')
            except SyntaxError:
                self.erro_sintatico()
        elif self.token_atual[1] in ['inteiro', 'real', 'literal', 'logico']:
            self.tipo_basico()
        else:
            self.erro_sintatico('tipo')

    # <declaracao_variaveis> ::= 'declare' <identificador> ':' <tipo>
    def declaracao_variaveis(self):
        self.consumir('declare')
        self.identificador()
        while self.token_atual and self.token_atual[1] == ',':
            self.consumir(',')
            self.identificador()
        self.consumir(':')
        self.tipo()

    # tipo_basico ::= 'inteiro' | 'real' | 'literal' | 'logico'
    def tipo_basico(self):
        if self.token_atual[1] in ['inteiro', 'real', 'literal', 'logico']:
            self.consumir(self.token_atual[1])
        else:
            self.erro_sintatico('tipo')

    # <comando> ::= <comando_leia> | <comando_escreva> | <comando_atribuicao> | ...
    def comando(self):
        if not self.token_atual:
            return False
        match self.token_atual[1]:
            case 'se':
                self.comando_se()
            case 'caso':
                self.comando_caso()
            case 'leia':
                self.comando_leia()
            case 'escreva':
                self.comando_escreva()
            case 'para':
                self.comando_para()
            case 'enquanto':
                self.comando_enquanto()
            case 'faca':
                self.comando_faca()
            case 'IDENT':  
                self.comando_atribuir()
            case _:
                return False
        return True
    
    def comando_caso(self):
        self.consumir('caso')
        self.exp_aritmetica()
        self.consumir('seja')
        while self.token_atual and self.token_atual[1] != 'fim_caso':
            self.selecao()
            if self.token_atual and self.token_atual[1] == 'senao':
                self.consumir('senao')
                body = True
                while body:
                    body = self.comando()
        self.consumir('fim_caso')
    
    def selecao(self): 
        self.constantes()
        self.consumir(':')
        body = True
        while body:
            body = self.comando()
    
    def constantes(self):
        self.numero_intervalo()
        while self.token_atual and self.token_atual[1] == ',':
            self.consumir(',')
            self.numero_intervalo()
        
    def numero_intervalo(self):
        if  self.token_atual and self.token_atual[1] == '-':
            self.consumir('-')
        self.consumir('NUM_INT')
        if self.token_atual and self.token_atual[1] == '..':
            self.consumir('..')
            if self.token_atual and self.token_atual[1] == '-':
                self.consumir('-') 
            self.consumir('NUM_INT')

    def comando_para(self):
        self.consumir('para')
        self.identificador()
        self.consumir('ate')
        self.expressao()
        self.consumir('faca')
        self.comando()
        self.consumir('fim_para')
    
    def comando_faca(self):
        self.consumir('faca')
        self.comando()
        self.consumir('fim_faca')
    
    def comando_chamada(self):
        self.identificador()
        self.consumir('(')
        self.expressao()
        while self.token_atual and self.token_atual[1] == ',':
            self.consumir(',')
            self.expressao()
        self.consumir(')')
    # <comando_atribuir> ::= <identificador> '<-' <expressao>
    def comando_atribuir(self):
        if self.token_atual and self.token_atual[1] == '^':
            self.consumir('^')
        self.identificador()
        self.consumir('<-')
        self.expressao()

    #cmdleia ::= 'leia' '(' [^] identificador {',' [^] identificador} ')'
    def comando_leia(self):
        if self.token_atual and self.token_atual[1] == 'leia':
            self.consumir('leia')
        self.consumir('(')
        if self.token_atual and self.token_atual[1] == '^':
            self.consumir("^")
        self.identificador()
        while self.token_atual and self.token_atual[1] == ',':
            self.consumir(',')
            if self.token_atual and self.token_atual[1] == '^':
                self.consumir("^")
            self.identificador()
        self.consumir(')')
    
    #cmdescreva ::= 'escreva' '(' expressao (',' expressao)* ')'    
    def comando_escreva(self):
        self.consumir('escreva')
        self.consumir('(')
        self.expressao()
        while self.token_atual and self.token_atual[1] == ',':
            self.consumir(',')
            self.expressao()
        self.consumir(')')

    def comando_atribuicao(self):
        self.identificador()
        self.consumir('<-')
        self.expressao()

    def comando_se(self):
        self.consumir('se')
        self.expressao()
        self.consumir('entao')
        body_se = True
        while body_se:
            body_se = self.comando()
        if self.token_atual and self.token_atual[1] == 'senao':
            self.consumir('senao')
        body_senao = True
        while body_senao:
            body_senao = self.comando()
        self.consumir('fim_se')

    def comando_enquanto(self):
        self.consumir('enquanto')
        self.expressao()
        self.consumir('faca')
        self.comandos()
        self.consumir('fim_enquanto')

    # expressao ::= termo_logico (op_logico_1 termo_logico)*
    #op_logico_1 ::= 'ou'
    def expressao(self):
        self.termo_logico()
        while self.token_atual and self.token_atual[1] == 'ou':
            self.consumir('ou')
            self.termo_logico()

    def termo_logico(self):
        self.fator_logico()
        while self.token_atual and self.token_atual[1] == 'e':
            self.consumir('e')
            self.fator_logico()
    
    def fator_logico(self):
        if self.token_atual and self.token_atual[1] == 'nao':
            self.consumir('nao')
        if self.token_atual and self.token_atual[1] == 'verdadeiro':
            self.consumir('verdadeiro')
        elif self.token_atual and self.token_atual[1] == 'falso':
            self.consumir('falso')
        else:
            self.exp_relacional()
    
    def exp_relacional(self):
        self.exp_aritmetica()
        while self.token_atual and self.token_atual[1] in OP_RELACIONAIS:
            operador = self.token_atual[1]
            self.consumir(operador)
            self.exp_aritmetica()
    
    def exp_aritmetica(self):
        self.termo()
        while self.token_atual and self.token_atual[1] in ['+', '-']:
            operador = self.token_atual[1]
            self.consumir(operador)
            self.termo()
    
    def termo(self):
        self.fator()
        while self.token_atual and self.token_atual[1] in ['*', '/']:
            operador = self.token_atual[1]
            self.consumir(operador)
            self.fator()
    
    def fator(self):
        self.parcela()
        while self.token_atual and self.token_atual[1] == '%':
            self.consumir('^')
            self.parcela()
        
    def parcela(self):
        if self.token_atual and self.token_atual[1] == '-':
            self.consumir('-')
        try:
            self.parcela_unaria()
        except:
            self.parcela_nao_unaria()

    def parcela_unaria(self):
        if self.token_atual and self.token_atual[1] == 'IDENT':
            self.identificador()
            if self.token_atual and self.token_atual[1] == '(':
                self.consumir('(')
                self.expressao()
                while self.token_atual and self.token_atual[1] == ',':
                    operador = self.token_atual[1]
                    self.consumir(operador)
                    self.expressao()
                self.consumir(')')
        elif self.token_atual and self.token_atual[1] == 'NUM_INT':
            self.consumir('NUM_INT')
        elif self.token_atual and self.token_atual[1] == 'NUM_REAL':
            self.consumir('NUM_REAL')
        elif self.token_atual and self.token_atual[1] == '(':
            self.consumir('(')
            self.expressao()
            self.consumir(')')
        elif self.token_atual and self.token_atual[1] == '^':
                self.consumir('^')
                self.identificador()
        else:
            raise SyntaxError(f"Não é unario")
        
    def parcela_nao_unaria(self):
        if self.token_atual and self.token_atual[1] == '&':
            self.consumir('&')
            self.identificador()
        else:
            self.consumir('CADEIA')
        
        
def sintax(caminho_entrada, caminho_saida):
    pass

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        caminho_arquivo = sys.argv[1]
        caminho_saida = sys.argv[2]
    else:
        caminho_arquivo = ENTRADA
        caminho_saida = SAIDA
    
    caminho_saida_alt = caminho_saida.replace('.txt', '_alt.txt')
    
    tokens, tokens_com_linha, erro = lexer_module.lexico(caminho_arquivo, caminho_saida, caminho_saida_alt)
    
    if erro:
        with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write(erro + "\n")
                out.write("Fim da compilacao\n")
    else:
        parser = Parser(tokens_com_linha)
        try:
            parser.programa()
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write("Fim da compilacao\n")
        except SyntaxError as e:
            with open(caminho_saida, "w", encoding="utf-8") as out:
                out.write(str(e) + "\n")
                out.write("Fim da compilacao\n")
            print(str(e))
        sintax(caminho_saida, caminho_saida)