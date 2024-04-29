import javalang
method = 'helperCanInlineReferenceToFunction'
with open('./FunctionInjectorTest.java', 'r') as f:
    tree = javalang.parse.parse(f.read())
Nodes = []
AllNodes = {}
for path, node in tree.filter(javalang.tree.MethodDeclaration):
    if not node.name in AllNodes:
        AllNodes[node.name] = []
    AllNodes[node.name].append(node)
    if node.name in 'testIssue1101a':
        Nodes.append(node)
print(method in AllNodes)
if method in AllNodes:
    ms = AllNodes[method]
    for i in ms:
        for j in i.body:
            print(j)
for i in Nodes:
    for j in i.body:
        for _, node in j:
            if isinstance(node, javalang.tree.MethodInvocation):
                print(node.member)
