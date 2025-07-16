from antlr4 import *
from LALexer import LALexer

input_stream = FileStream("entrada.txt", encoding="utf-8")
lexer = LALexer(input_stream)
for token in lexer.getAllTokens():
    print(token)