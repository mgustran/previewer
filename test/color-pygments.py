import os

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, PythonLexer
from pygments.formatters import TerminalFormatter, Terminal256Formatter, TerminalTrueColorFormatter

code = 'print "Hello World"'
with open('../previewer.py', 'r') as f:
    code2 = f.read().encode('utf-8')
formatter = TerminalFormatter(bg='dark')
lexer = get_lexer_for_filename(f.name)
# formatter.darkbg = T
# formatter.format()
result1 = highlight(code2, lexer, formatter)
result2 = highlight(code2, lexer, Terminal256Formatter())
result3 = highlight(code2, lexer, TerminalTrueColorFormatter())
print(result1)
print(result2)
print(result2)
# os.system(f'echo "{result}"')
#
# result1_formatted = result1.replace()