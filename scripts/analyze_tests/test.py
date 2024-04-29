import javalang
f = open('./java.java', 'r')
tree = javalang.parse.parse(f.read())
for _, i in tree:
    if isinstance(i, javalang.tree.StatementExpression):
        print(i)
    if i.position:
        print(i.position)
