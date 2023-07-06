import util
import javalang
class CustomClass(set):
    def __init__(self, name):
        self.name = name
class AssertionFailedException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)
    def __str__(self):
        return self.msg
def fail(msg:str=''):
    raise AssertionFailedException(msg)
def assertEquals(a, b):
    if not type(a) == type(b):
        fail('Type not equals: {} and {}'.format(type(a), type(b)))
    if not a == b:
        fail('Expected {} but given {}'.format(a, b))
def assertGreaterThan(a, b):
    if not a > b:
        fail('{} is not greater than {}'.format(a, b))
def assertListEquals(a, b):
    a = list(a)
    b = list(b)
    if len(a) != len(b):
        fail('Length not equals, expected {} but given {}'.format(len(a), len(b)))
    for i in range(len(a)):
        if not a[i] == b[i]:
            fail('UnEquals at index {} that expects {} but given {}'.format(i, a[i], b[i]))

def test_class_name():
    inst = CustomClass('no name')
    assertEquals('CustomClass', util.class_name(inst))
def test_filter_tokens():
    code = '''
        public class test{
            public static void main(String[] args){
                    System.out.println("test");
                }
            private void testFunc(){
                    if(true){
                        }
                }
        }
    '''
    tokens = util.tokenize_java_code(code)
    actual = javalang.tokenizer.tokenize(code)
    assertListEquals(map(lambda x:x.value, actual), map(lambda x:x.value, tokens))

    tokens = util.tokenize_java_code(code)
    actual = javalang.tokenizer.tokenize(code)
    expected_sep = []
    expected_id = []
    for i in actual:
        if util.class_name(i) == 'Separator':
            expected_sep.append(i)
        if util.class_name(i) == 'Identifier':
            expected_id.append(i)
    assertListEquals(map(lambda x:x.value, expected_sep), map(lambda x:x.value, util.filter_tokens(tokens)['Separator']))
    tokens = util.tokenize_java_code(code)
    assertListEquals(map(lambda x:x.value, expected_id), map(lambda x:x.value, util.filter_tokens(tokens)['Identifier']))
    try:
        tokens = util.tokenize_java_code(code)
        if len(list(tokens)) !=  0:
            raise IOError("")
        fail()
    except IOError:
        pass

def test_parse_ending_point_same_for_sep_and_all():
    with open('./test_resource/code1.java', 'r') as f:
        code1 = util.tokenize_java_code(f.read())
    with open('./test_resource/code2.java', 'r') as f:
        code2 = util.tokenize_java_code(f.read())
    with open('./test_resource/lines', 'r') as f:
        lines = f.read().splitlines()
    tokens1 = list(code1)
    tokens2 = list(code2)
    sep1 = util.filter_tokens(tokens1)['Separator']
    sep2 = util.filter_tokens(tokens2)['Separator']
    PosList = []
    for i in lines:
        PosList.append(util.Pos(int(i), 0))

    tree2 = util.readFileToAST('./test_resource/code2.java')
    nodepos = []
    for i in PosList:
        nodepos.append(util._node_of_pos(tree2, i))
    nodepos = list(map(lambda x:util.least_pos_of_node(x), nodepos))

    PosListC1 = []
    PosListC1.append(util.Pos(1110, 0))
    PosListC1.append(util.Pos(1015, 0))
    PosListC1.append(util.Pos(1106, 0))
    PosListC1.append(util.Pos(1127, 0))
    PosListC1.append(util.Pos(139, 0))
    tree1 = util.readFileToAST('./test_resource/code1.java')
    nodepos1 = []
    for i in range(len(PosListC1)):
        nodepos1.append(util._node_of_pos(tree1, PosListC1[i]))
    nodepos1 = list(map(lambda x:util.least_pos_of_node(x), nodepos1))
    for i in range(len(PosList)):
        try:
            assertEquals(util.parse_ending_point(PosList[i], tokens2, nodepos[i]), util.parse_ending_point(PosList[i], sep2, nodepos[i]))
        except util.ParseError:
            # ignore incomplete statements
            continue
    for i in range(len(PosListC1)):
        assertEquals(util.parse_ending_point(PosListC1[i], tokens1, nodepos1[i]), util.parse_ending_point(PosListC1[i], sep1, nodepos1[i]))
def test_parse_ending_point():
    PosListC1 = []
    PosListC1.append(util.Pos(1110, 0))
    PosListC1.append(util.Pos(1015, 0))
    PosListC1.append(util.Pos(1106, 0))
    PosListC1.append(util.Pos(1127, 0))
    PosListC1.append(util.Pos(139, 0))
    with open('./test_resource/code1.java', 'r') as f:
        src1 = f.read()
        code1 = util.tokenize_java_code(src1)
        tree1 = util.code_to_AST(src1)
    tokens1 = list(code1)
    nodepos1 = []
    for i in PosListC1:
        nodepos1.append(util._node_of_pos(tree1, i))
    nodepos1 = list(map(lambda x:util.least_pos_of_node(x), nodepos1))
    sep1 = util.filter_tokens(tokens1)['Separator']
    with open('./test_resource/answer1', 'r') as f:
        ans = f.read().split('<>')

    try:
        util.parse_ending_point(util.Pos(1114, 0), sep1)
        fail()
    except util.ParseError:
        pass
    try:
        util.parse_ending_point(util.Pos(1114, 0), tokens1)
        fail()
    except util.ParseError:
        pass
    '''
    try:
        util.parse_ending_point(util.Pos(3, 0), sep1)
        fail()
    except util.ParseError:
        pass
    try:
        util.parse_ending_point(util.Pos(3, 0), tokens1)
        fail()
    except util.ParseError:
        pass
    '''

    for i in range(len(PosListC1)):
        assertEquals(ans[i].strip(), util.catch_block(src1, PosListC1[i], util.parse_ending_point(PosListC1[i], sep1, nodepos1[i])).strip())
def test_parse_ending_point_1():
    with open('./test_resource/code1.java', 'r') as f:
        src1 = f.read()
        code1 = util.tokenize_java_code(src1)
        tree1 = util.code_to_AST(src1)
    tokens1 = list(code1)
    sep1 = util.filter_tokens(tokens1)['Separator']
    beg = util.Pos(1176, 1)
    end = util.Pos(1189, 49)
    node = util._node_of_pos(tree1, beg)
    assertEquals(end, util.parse_ending_point(beg, sep1, util.least_pos_of_node(node)))
def test_catch_block():
    with open('./test_resource/code1.java', 'r') as f:
        code1 = f.read()
    ans = '''        if (denominator.equals(fraction.denominator)) {
            num = numerator.subtract(fraction.numerator);
            den = denominator;
        } else {
            num = (numerator.multiply(fraction.denominator)).subtract((fraction.numerator).multiply(denominator));
            den = denominator.multiply(fraction.denominator);
        }'''
    assertEquals(ans, util.catch_block(code1, util.Pos(1106, 0), util.Pos(1112, 0)))
    assertEquals(ans, util.catch_code(code1, util.Pos(1106, 0), util.Pos(1112, 9)))
def test_least_pos_of_node_common():
    tree = util.readFileToAST('./test_resource/code1.java')
    _map = util.traverse_get_global(tree)
    tos = util.get_only_node('toString', _map)
    for i in tos.body:
        if isinstance(i, javalang.tree.IfStatement):
            assertEquals(util.Pos(1134, 39), util.least_pos_of_node(i))
            break
def test_least_pos_of_node_try_statement():
    tokens = util.tokenize_java_code(open('./test_resource/code1.java' ,'r').read())
    tree = util.readFileToAST('./test_resource/code1.java')
    _map = util.traverse_get_global(tree)
    test = util.get_only_node('testQ', _map)
    for i in test.body:
        if isinstance(i, javalang.tree.TryStatement):
            '''
            with open('./test_resource/code1.java', 'r') as f:
                code1 = f.read()
            tokens1 = list(util.tokenize_java_code(code1))
            sep1 = util.filter_tokens(tokens1)['Separator']
            print(util.catch_code(code1, util._try_get_node_pos(i), util.parse_ending_point(util._try_get_node_pos(i), sep1, util.least_pos_of_node(i))))
            '''
            assertGreaterThan(util.least_pos_of_node(i, tokens), util.Pos(1142, 9))
            break
def test_least_pos_of_node_if_statement():
    tokens = util.tokenize_java_code(open('./test_resource/code1.java' ,'r').read())
    tree = util.readFileToAST('./test_resource/code1.java')
    _map = util.traverse_get_global(tree)
    test = util.get_only_node('testP', _map)
    for i in test.body:
        if isinstance(i, javalang.tree.IfStatement):
            assertGreaterThan(util.least_pos_of_node(i, tokens), util.Pos(1149, 7))
            break
def test_parseUpperCase():
    s = 'testUpperCase'
    tokens = ['test', 'upper', 'case']
    assertListEquals(tokens, util.parseUpperCase(s))
    s = 'TestUpperCase'
    tokens = ['test', 'upper', 'case']
    assertListEquals(tokens, util.parseUpperCase(s))
    s = 'TestupperCase'
    tokens = ['testupper', 'case']
    assertListEquals(tokens, util.parseUpperCase(s))
def test_safe_nodes_in_try_block():
    tree = util.readFileToAST('./test_resource/code1.java')
    _map = util.traverse_get_global(tree)
    node1 = util.get_only_node('testTry1', _map).body[0]
    node2 = util.get_only_node('testTry2', _map).body[0]
    node3 = util.get_only_node('testTry3', _map).body[0]
    assertEquals(1, len(util.safe_nodes_in_try_block(node1)))
    assertEquals('test1', util.safe_nodes_in_try_block(node1)[0].expression.member)
    assertEquals(0, len(util.safe_nodes_in_try_block(node2)))
    assertEquals(1, len(util.safe_nodes_in_try_block(node3)))
    assertEquals('test1', util.safe_nodes_in_try_block(node3)[0].expression.member)
def test_try_accept_update_bool():
    assertEquals(True, util.try_accept_update_bool(True, True))
    assertEquals(True, util.try_accept_update_bool(False, True))
    assertEquals(True, util.try_accept_update_bool(True, False))
    assertEquals(False, util.try_accept_update_bool(False, False))
    assertEquals(True | True, util.try_accept_update_bool(True, True))
    assertEquals(False | True, util.try_accept_update_bool(False, True))
    assertEquals(True | False, util.try_accept_update_bool(True, False))
    assertEquals(False | False, util.try_accept_update_bool(False, False))
def test_insert_at_pos():
    testStr = '''for i in range(5):
        print(1)
        print(i)'''
    inserted = '''for i in range(5):
        print(10)
        print(i)'''
    assertEquals(inserted, util.insert_at_pos('0', util.Pos(2, 16), testStr))
    assertListEquals(inserted.splitlines(), util.insert_at_pos('0', util.Pos(2, 16),  testStr.splitlines()))
    assertEquals(inserted, util.insert_at_pos('0', util.Pos(2, 15), testStr, True))
    assertListEquals(inserted.splitlines(), util.insert_at_pos('0', util.Pos(2, 15),  testStr.splitlines(), True))
from inspect import isfunction
import traceback
def run_tests():
    tests = []
    for i in globals():
        if i.startswith('test_') and isfunction(globals()[i]):
            tests.append(globals()[i])
    test_num = len(tests)
    failing = {}
    print('Run tests:')
    for i in tests:
        try:
            print('\t' + i.__name__)
            i()
        except Exception as E:
            failing[i.__name__] = traceback.format_exc()
    print('\nTotal: {}'.format(len(tests)))
    print('-'*20)
    print('Failing tests: {}'.format(len(failing)))
    if not len(failing) == 0:
        f = open('./failing_tests', 'w')
        for i in failing:
            print('\t' + i)
            f.write('--- '+i+'\n')
            f.write(failing[i])
            f.write('-'*20)
            f.write('\n')
        f.close()


if __name__ == '__main__':
    run_tests()
