import util
tree = util.readFileToAST('./java.java')
_glb = util.traverse_get_global(tree)
node = util.get_only_node('testCanInlineReferenceToFunction35', _glb)
print(util.try_get_node_pos(node))
print(util.begin_pos_of_node(node))
