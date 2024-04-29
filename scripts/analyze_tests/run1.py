import javalang
import util
import json
import tqdm
class filelog:
    def __init__(self, filename):
        self.file = open(filename, 'a')
    def log(self, cont, console=False):
        self.file.write('{}\n'.format(cont))
        if console:
            print(cont)
    def end(self):
        self.file.close()
with open('../research/database.json', 'r') as db:
    database = json.load(db)
with open('../research/2toMore', 'r') as f:
    wait = f.read().splitlines()
root = '/root/workbench/d4j_buggy'
pure_name_set = set()
mess_name_set = set()
all_set = set()
mess_blocks = set()
pure_blocks = set()
add_set = set()
qualifiers = set()
members = set()

valid_block = (javalang.tree.IfStatement, javalang.tree.WhileStatement, javalang.tree.DoStatement, javalang.tree.ForStatement, javalang.tree.TryStatement, javalang.tree.SwitchStatement, javalang.tree.BlockStatement)

primitiveAssert = False

with open('./names/junit', 'r') as f:
    JunitAsserts = f.read().splitlines()

def tryGetLine(node):
    try:
        return node.position.line
    except:
        return -1
def parseAddNameToSet(node):
    if node.qualifier == '':
        pure_name_set.add(node.member)
        return 'pure_name_set'
    else:
        mess_name_set.add(node.member)
        return 'mess_name_set'
def containsAssertList(name, AllNodes):
    has = False
    for i in range(len(AllNodes[name])):
        if containsAssertDeclaration(i, AllNodes, name):
            has = True
            break
    return has

def containsAssertDeclaration(idx, AllNodes, name):
    nodelist = AllNodes[name]
    node = nodelist[idx]
    if type(node) == bool:
        return node
    # set to False to prevent infinite calling
    nodeBool = False
    AllNodes[name][idx] = nodeBool
    nodeBody = node.body
    if nodeBody == None:
        nodeBody = []
    for i in nodeBody:
        if not isinstance(i, javalang.tree.Statement):
            # skip assignments etc.
            continue
        if isinstance(i, javalang.tree.AssertStatement):
            nodeBool = True
        elif isinstance(i, valid_block):
            for _, subnode in i:
                if containsAssert(subnode, AllNodes):
                    nodeBool = True
                    logger.log('found containsAssert getting True in block recursive, add {} to {}'.format(subnode.member, parseAddNameToSet(subnode)), True)
                    break
        elif isinstance(i, javalang.tree.StatementExpression):
            if isinstance(i.expression, javalang.tree.MethodInvocation):
                nodeBool = containsAssert(i.expression, AllNodes)
                if nodeBool:
                    logger.log('found containsAssert getting True in method recursive, add {} to {}'.format(i.expression.member, parseAddNameToSet(i.expression)), True)
        if nodeBool:
            break
    AllNodes[name][idx] = nodeBool
    return nodeBool
def containsAssert(node, AllNodes):
    if not isinstance(node, javalang.tree.MethodInvocation):
        return False
    members.add(node.member)
    if node.qualifier == '':
        if node.member in JunitAsserts:
            return True
        elif 'assert' in node.member.lower() or 'verify' in node.member.lower() or 'test' in node.member.lower():
            return True
        else:
            if not node.member in AllNodes:
                return False
            return containsAssertList(node.member, AllNodes)
    else:
        qualifiers.add(node.qualifier)
        if node.qualifier in ('Assert', 'Asserts', 'Assertions', 'TestUtils'): 
            return True
        elif 'assert' in node.member.lower() or 'verify' in node.member.lower() or 'test' in node.member.lower():
            return True
        elif node.member in AllNodes:
            return containsAssertList(node.member, AllNodes)
        elif node.member in JunitAsserts:
            return True
        else:
            return False
def tryBlock(src, node, AllNodes):
    begin = tryGetLine(node)
    max_ = 0
    yes = False
    if begin == -1:
        return '<fail to get block>'
    list_line = []
    for _, subnode in node:
        if containsAssert(subnode, AllNodes):
            logger.log('found containsAssert getting True in tryBlock, add {} to {}'.format(subnode.member, parseAddNameToSet(subnode)), True)
            yes = True
        list_line.append(tryGetLine(subnode))
    max_ = max(list_line)
    if len(src.splitlines()) > max_:
        max_ += 1
    return src.splitlines()[begin - 1 : max_], yes
def analyze_invocation(node, logger, src, AllNodes):
    all_set.add(node.member)
    logger.log('add {} to all_set'.format(node.member))
    if node.qualifier == '':
        add_set.add(node.member)
    if containsAssert(node, AllNodes):
        logger.log('found containsAssert getting True in analyze_invocation, add {} to {}'.format(node.member, parseAddNameToSet(node)), True)
        logger.log('qualifier: {}'.format(node.qualifier))
        logger.log('code: {}'.format(src.splitlines()[tryGetLine(node)-1]))
def analyze_node(node, logger, src, AllNodes):
    logger.log('analyze: {}'.format(node.name))
    for i in node.body:
        if not isinstance(i, javalang.tree.Statement):
            # skip assignments etc.
            continue
        if isinstance(i, javalang.tree.AssertStatement):
            logger.log("found primitive assert at {}".format(tryGetLine(i)))
            primitiveAssert = True
            add_set.add(src.splitlines()[tryGetLine(i)-1])
        elif isinstance(i, valid_block):
            # blocks
            block, yes = tryBlock(src, i, AllNodes)
            logger.log('get block code:\n{}'.format('\n'.join(block)))
            if yes:
                logger.log('is pure block')
                pure_blocks.add('\n'.join(block))
            else:
                logger.log('is mess block')
                mess_blocks.add('\n'.join(block))
        elif isinstance(i, javalang.tree.StatementExpression):
            if isinstance(i.expression, javalang.tree.MethodInvocation):
                # find all invocation
                analyze_invocation(i.expression, logger, src, AllNodes)
            else:
                logger.log('found unk statement expression at {}\n{}'.format(tryGetLine(i), src.splitlines()[tryGetLine(i)-1]))
        else:
            logger.log('unk statement at {}'.format(tryGetLine(i)))
            logger.log('unk statement:\n{}'.format(src.splitlines()[tryGetLine(i)-1]))
def analyze(proj, bid, logger):
    logger.log('-------------')
    logger.log('{}_{}'.format(proj, bid))
    trigger_map = {}
    export = database.get('defects4j').get(proj).get(bid).get('export')
    triggers = export.get('tests.trigger')
    for i in triggers:
        i = i.split('::')
        if not i[0] in trigger_map:
            trigger_map[i[0]] = []
        trigger_map[i[0]].append(i[1])
    src_dir = '{}/{}_{}/{}/'.format(root, proj, bid, export.get('dir.src.tests'))
    for i in trigger_map:
        path = '{}/{}.java'.format(src_dir, i.replace('.', '/'))
        logger.log(path)
        testcases = trigger_map[i]
        with open(path, 'r') as src:
            src = src.read()
        tree = javalang.parse.parse(src)
        Nodes = []
        AllNodes = {}
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            if not node.name in AllNodes:
                AllNodes[node.name] = []
            AllNodes[node.name].append(node)
            if node.name in testcases:
                Nodes.append(node)
        for j in Nodes:
            analyze_node(j, logger, src, AllNodes)
    logger.log('-------------')
logger = filelog('./logs/log1')
for i in tqdm.tqdm(wait):
    i = i.split(':')[0].split('_')
    if i[0] == 'Time' and i[1] == '21':
        continue
    analyze(i[0], i[1], logger)
logger.log('')
logger.log('pure name: {}'.format(len(pure_name_set)))
fp = open('./names/pure_names2', 'w')
for i in pure_name_set:
    fp.write(i+'\n')
    logger.log(i)
fp.close()
logger.log('')
fp = open('./names/mess_names2', 'w')
logger.log('mess name: {}'.format(len(mess_name_set)))
for i in mess_name_set:
    fp.write(i+'\n')
    logger.log(i)
fp.close()
logger.log('')
fp = open('./names/empty_qualifier', 'w')
logger.log('empty qualifier: {}'.format(len(add_set)))
for i in add_set:
    fp.write(i+'\n')
    logger.log(i)
fp.close()
logger.log('')
logger.log('all name: {}'.format(len(all_set)))
for i in all_set:
    logger.log(i)
logger.log('')
logger.log('pure blocks: {}'.format(len(pure_blocks)))
for i in pure_blocks:
    logger.log(i)
    logger.log('-----')
logger.log('mess blocks: {}'.format(len(mess_blocks)))
for i in mess_blocks:
    logger.log(i)
    logger.log('-----')
logger.log('primitive asserts: {}'.format(primitiveAssert))
logger.log('-----')
logger.log('qualifiers: {}'.format(len(qualifiers)))
for i in qualifiers:
    logger.log(i)
logger.log('-----')
logger.log('members: {}'.format(len(members)))
for i in members:
    logger.log(i)
logger.log('-----')
logger.end()
