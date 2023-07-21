with open('./testf', 'r') as f:
    f  = f.read()
import util
with open('pt', 'w')  as g:
    g.write(util.reformat_tokens(util.tokenize_java_code(f)))
