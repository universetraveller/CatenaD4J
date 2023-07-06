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
    for _, i in node.filter(javalang.tree.StatementExpression):
        if not isinstance(i.expression, javalang.tree.MethodInvocation):
            continue
        invocation = i.expression
        if invocation.selectors:
            for sel in invocation.selectors:
                if not isinstance(sel, javalang.tree.MethodInvocation):
                    continue
                nodeBool = containsAssert(sel, AllNodes)
                if nodeBool:
                    logger.log('found containsAssert getting True in recursive, add {} to {}'.format(sel.member, parseAddNameToSet(sel)), True)
                    break
        if nodeBool:
            break
        nodeBool = containsAssert(invocation, AllNodes)
        if nodeBool:
            logger.log('found containsAssert getting True in recursive, add {} to {}'.format(invocation.member, parseAddNameToSet(invocation)), True)
            break
    AllNodes[name][idx] = nodeBool
    return nodeBool
def parseUpperCase(S):
    tokens = []
    now = ''
    for i in S:
        if i.isupper() and now != '':
            tokens.append(now.lower())
            now = ''
        now += i
    tokens.append(now.lower())
    return tokens
def anyMatchPartial(matchList, shouldMatched):
    for i in matchList:
        if i in parseUpperCase(shouldMatched):
            return True
    return False
prefixes = ('assert', 'verify', 'test', 'check', 'validate')
def containsAssert(node, AllNodes):
    if not isinstance(node, javalang.tree.MethodInvocation):
        return False
    members.add(node.member)
    if node.qualifier != '':
        qualifiers.add(node.qualifier)
    if node.member in JunitAsserts or anyMatchPartial(prefixes, node.member):
        return True
    #if node.qualifier in ('Assert', 'Asserts', 'Assertions', 'TestUtils', 'TestCase'): 
    if node.qualifier in ('Assert', 'Asserts', 'Assertions', 'TestCase'): 
        return True
    if not node.member in AllNodes:
        return False
    return containsAssertList(node.member, AllNodes)
def tryBlock(src, node, AllNodes):
    begin = tryGetLine(node)
    max_ = 0
    yes = False
    if begin == -1:
        return '<fail to get block>'
    list_line = []
    for _, subnode in node:
        if containsAssert(subnode, AllNodes):
            if isinstance(subnode, javalang.tree.MethodInvocation):
                logger.log('found containsAssert getting True in tryBlock, add {} to {}'.format(subnode.member, parseAddNameToSet(subnode)), True)
            yes = True
        list_line.append(tryGetLine(subnode))
    max_ = max(list_line)
    if len(src.splitlines()) > max_:
        max_ += 1
    return src.splitlines()[begin - 1 : max_], yes
shouldCheck = set()
import copy
def analyze_invocation(node, logger, src, AllNodes):
    all_set.add(node.member)
    logger.log('add {} to all_set'.format(node.member))
    if node.qualifier == '':
        add_set.add(node.member)
    # root caller
    if containsAssert(node, AllNodes):
        #if node.qualifier in ('Assert', 'Asserts', 'Assertions', 'TestUtils', 'TestCase'): 
        if node.qualifier in ('Assert', 'Asserts', 'Assertions', 'TestCase'): 
            if not '{}.{}'.format(node.qualifier, node.member) in shouldCheck:
                logger.log('#should check: {}.{}'.format(node.qualifier, node.member))
                shouldCheck.add('{}.{}'.format(node.qualifier, node.member))
        logger.log('found containsAssert getting True in analyze_invocation, add {} to {}'.format(node.member, parseAddNameToSet(node)), True)
        logger.log('qualifier: {}'.format(node.qualifier))
        logger.log('code: {}'.format(src.splitlines()[tryGetLine(node)-1]))
def noSubStatementExpression(node):
    for _, i in node:
        if i == node:
            continue
        assert not isinstance(i, javalang.tree.StatementExpression)
def analyze_node(node, logger, src, AllNodes):
    logger.log('analyze: {}'.format(node.name))
    for _, i in node.filter(javalang.tree.StatementExpression):
        try:
            noSubStatementExpression(i)
        except AssertionError:
            # no need, would traverse to it
            logger.log('#SubStatementExpression exists')
            logger.log('*'*20)
            logger.log('line:')
            logger.log(tryGetLine(i))
            logger.log('*'*15)
            logger.log('{}'.format(i))
            logger.log('*'*20)
        if not isinstance(i.expression, javalang.tree.MethodInvocation):
            continue
        invocation = i.expression
        if invocation.selectors:
            for sel in invocation.selectors:
                if not isinstance(sel, javalang.tree.MethodInvocation):
                    continue
                logger.log('In selectors:')
                analyze_invocation(sel, logger, src, AllNodes)
        logger.log('Invocation:')
        analyze_invocation(invocation, logger, src, AllNodes)
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
            newAllNodes = copy.deepcopy(AllNodes)
            # root caller
            analyze_node(j, logger, src, newAllNodes)
    logger.log('-------------')
logger = filelog('./logs/log5')
for i in tqdm.tqdm(wait):
    i = i.split(':')[0].split('_')
    if i[0] == 'Time' and i[1] == '21':
        continue
    analyze(i[0], i[1], logger)
logger.log('-----')
logger.log('qualifiers: {}'.format(len(qualifiers)))
for i in qualifiers:
    logger.log(i)
logger.log('-----')
logger.log('members: {}'.format(len(members)))
for i in members:
    logger.log(i)
logger.log('-----')
with open('./names/table', 'r') as f:
    JunitAsserts = f.read().splitlines()
a = (pure_name_set | mess_name_set) - set(JunitAsserts)
logger.log('in new: {}'.format(len(a)))
for i in a:
    logger.log(i)
logger.log('-----')
a = set(JunitAsserts) - (pure_name_set | mess_name_set)
logger.log('in old: {}'.format(len(a)))
for i in a:
    logger.log(i)
logger.log('-----')
logger.log('all: {}'.format(len(all_set)))
for i in all_set:
    logger.log(i)
logger.log('-----')
logger.log('empty q: {}'.format(len(add_set)))
for i in add_set:
    logger.log(i)
logger.log('-----')
logger.log('pure: {}'.format(len(pure_name_set)))
for i in pure_name_set:
    logger.log(i)
logger.log('mess: {}'.format(len(mess_name_set)))
for i in mess_name_set:
    logger.log(i)
logger.log('-----')
logger.end()
