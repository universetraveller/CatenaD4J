import javalang
import util
import json
import tqdm
class filelog:
    def __init__(self, filename):
        self.file = open(filename, 'a')
    def log(self, cont):
        self.file.write('{}\n'.format(cont))
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
def tryGetLine(node):
    try:
        return node.position.line
    except:
        return -1
def tryBlock(src, node):
    begin = tryGetLine(node)
    yes = False
    max_ = 0
    if begin == -1:
        return '<fail to get block>'
    list_line = []
    for _, subnode in node:
        if isinstance(subnode, javalang.tree.MethodInvocation) and subnode.qualifier == '':
            yes = True
        list_line.append(tryGetLine(subnode))
    max_ = max(list_line)
    return src.splitlines()[begin - 1 : max_], yes
def analyze_node(node, logger, src):
    logger.log('analyze: {}'.format(node.name))
    childs = node.children
    for i in childs:
        if not type(i) == list:
            continue
        if not len(i) > 0:
            continue
        analyze_child(i, logger, src)
valid_block = (javalang.tree.IfStatement, javalang.tree.WhileStatement, javalang.tree.DoStatement, javalang.tree.ForStatement, javalang.tree.TryStatement, javalang.tree.SwitchStatement, javalang.tree.BlockStatement)
def analyze_child(nodelist, logger, src):
    for i in nodelist:
        if not isinstance(i, javalang.tree.Statement):
            continue
        if isinstance(i, valid_block):
            block, yes = tryBlock(src, i)
            logger.log('get block code:\n{}'.format('\n'.join(block)))
            mess_blocks.add('\n'.join(block))
            if yes:
                logger.log('pure block')
                pure_blocks.add('\n'.join(block))
        if isinstance(i, javalang.tree.StatementExpression):
            if isinstance(i.expression, javalang.tree.MethodInvocation):
                all_set.add(i.expression.member)
                logger.log('add {} to all_set'.format(i.expression.member))
                if i.expression.qualifier == '':
                    pure_name_set.add(i.expression.member)
                    logger.log('add {} to pure_name_set'.format(i.expression.member))
                    logger.log('code: {}'.format(src.splitlines()[tryGetLine(i)-1]))
                else:
                    if 'assert' in i.expression.member.lower() or 'test' in i.expression.member.lower() or 'verify' in i.expression.member.lower():
                        mess_name_set.add(i.expression.member)
                        logger.log('add {} to mess_name_set'.format(i.expression.member))
                        logger.log('qualifier: {}'.format(i.expression.qualifier))
                        logger.log('code: {}'.format(src.splitlines()[tryGetLine(i)-1]))
        else:
            logger.log('unk statement at {}'.format(tryGetLine(i)))
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
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            if node.name in testcases:
                Nodes.append(node)
        for j in Nodes:
            analyze_node(j, logger, src)
    logger.log('-------------')
logger = filelog('./logs/log0')
for i in tqdm.tqdm(wait):
    i = i.split(':')[0].split('_')
    if i[0] == 'Time' and i[1] == '21':
        continue
    analyze(i[0], i[1], logger)
logger.log('')
logger.log('pure name: {}'.format(len(pure_name_set)))
for i in pure_name_set:
    logger.log(i)
logger.log('')
logger.log('mess name: {}'.format(len(mess_name_set)))
for i in mess_name_set:
    logger.log(i)
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
logger.end()
