import javalang
Junit4 = open('./org.junit.Assert.java', 'r')
Junit38 = open('./junit.framework.Assert.java', 'r')
Junit4Src = Junit4.read()
Junit38Src = Junit38.read()
tree4 = javalang.parse.parse(Junit4Src)
tree38 = javalang.parse.parse(Junit38Src)
set4 = set()
set38 = set()
for _, node in tree4.filter(javalang.tree.MethodDeclaration):
    if 'public' in node.modifiers:
        set4.add(node.name)
for _, node in tree38.filter(javalang.tree.MethodDeclaration):
    if 'public' in node.modifiers:
        set38.add(node.name)
set38.remove('format')
setall = set4.union(set38)
for i in set4:
    assert i in setall
for i in set38:
    assert i in setall
with open('./names/junit', 'w') as f:
    for i in setall:
        f.write(i+'\n')
