import javalang
import util
f = open('./java1.java', 'r')
tree = javalang.parse.parse(f.read())
exps = set()
for _, i in tree:
    if isinstance(i, javalang.tree.StatementExpression):
        exps.add(i.expression.__class__.__name__)
        if isinstance(i.expression, javalang.tree.MethodInvocation):
            if i.expression.selectors:
                for j in i.expression.selectors:
                    print('Sel: {}'.format(j))
            print('{}.{}'.format(i.expression.qualifier, i.expression.member))
print('exps:')
for i in exps:
    print(i)
a = 0
b = 0
for _, i in tree:
    if isinstance(i, javalang.tree.StatementExpression):
        a+=1
for _, i in tree.filter(javalang.tree.StatementExpression):
    b += 1
print(a)
print(b)
for _, i in tree.filter(javalang.tree.TryStatement):
    print(i)
tokens = list(javalang.tokenizer.tokenize('public void Main(){test();}'))
tokens[2].value = 'ttt'
for i in tokens:
    print(i)
