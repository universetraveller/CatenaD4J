from util import *
import javalang
import copy



class Assertion:
    def __init__(self, begin, end, source, name='<Unknown>'):
        self.begin = begin
        self.end = end
        self.source = source
        self.name = name
        self.child = []
    def __gt__(self, obj):
        return self.begin > obj.begin
    def fill_child(self, child):
        for i in child:
            if isinstance(i, Assertion):
                self.child.append(i)
        # no need to do it for having developed parse_node_body_v2
        '''
        self.child.sort()
        tag = False
        for i in range(len(self.child)):
        '''
    def childView(self):
        now = '['
        for i in self.child:
            now += '{}<Begin: {}, End: {}>,\n'.format(i.__class__.__name__, i.begin, i.end)
        now += ']'
        return now
    def __str__(self):
        return 'Begin: {}\nEnd: {}\nSource: {}\nName: {}\nChilds: {}'.format(self.begin, self.end, self.source, self.name, self.childView())
class StatementAssertion(Assertion):
    pass
class BlockAssertion(Assertion):
    pass
name_pattern = '{}_catena_{}'
class failing_test(Assertion):
    def split(self):
        self.splited = []
        if len(self.child) <= 1:
            return False
        code = open(self.source, 'r').read()
        # name map
        tree = code_to_AST(code)
        nodes_map = traverse_get_global(tree)
        named = []
        for i in nodes_map:
            named.append(i)
        # generate
        _code_lines = code.splitlines()
        for i in range(len(self.child)):
            code_lines = copy.deepcopy(_code_lines)
            for j in range(len(self.child)):
                if j == i:
                    continue
                st = self.child[j]
                beg = st.begin.row
                end = st.end.row
                for line_idx in range(beg-1, end):
                    code_lines[line_idx] = '//{}'.format(code_lines[line_idx])
                '''
                code_lines = insert_at_pos('/*', beg, code_lines)
                code_lines = insert_at_pos('*/', end, code_lines, True)
                '''
            new_code = '\n'.join(code_lines)
            new_code = catch_block(new_code, self.begin, self.end)
            new_tokens = tokenize_java_code(new_code)
            for idx in range(len(new_tokens)):
                token = new_tokens[idx]
                if not class_name(token) == 'Identifier' or not token.value == self.name:
                    continue
                new_i = int(i)
                while name_pattern.format(self.name, new_i) in named:
                    new_i += 100
                new_name = name_pattern.format(self.name, new_i)
                named.append(new_name)
                new_tokens[idx].value = new_name
                self.splited.append(javalang.tokenizer.reformat_tokens(new_tokens))
                break
        return True
cache = get_member_cache()
class Appendable:
    def __init__(self):
        pass
    def append(self, obj):
        pass
def getAppendable(L):
    if hasattr(L, 'append'):
        return L
    return Appendable()
activeTokens = ('assert', 'verify', 'test', 'check', 'validate')
activeQualifiers = ('Assert', 'Asserts', 'Assertions', 'TestCase')
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
                    break
        if nodeBool:
            break
        nodeBool = containsAssert(invocation, AllNodes)
        if nodeBool:
            break
    AllNodes[name][idx] = nodeBool
    return nodeBool
def containsAssert(node, _globals, check=None):
    check = getAppendable(check)
    if not isinstance(node, javalang.tree.MethodInvocation):
        return False
    if node.member in cache:
        return True
    if anyMatchPartial(activeTokens, node.member):
        check.append('Use pattern matching')
        return True
    if node.qualifier in activeQualifiers:
        check.append('Use qualifier matching')
        return True
    if not node.member in _globals:
        return False
    ret = containsAssertList(node.member, _globals)
    if ret:
        check.append('Use list matching')
    return ret
def read_if_statement(node, _globals, tokens):
    pass
def read_try_statement(node, _globals, tokens):
    pass
def read_for_statement(node, _globals, tokens):
    pass
def read_statement_expression(node, _globals,tokens):
    yes = False
    ret = None
    for child in node.selectors:
        if containsAssert(child, _globals):
            yes = True
            break
    if yes or containsAssert(node.expression, _globals):
        begin_pos = try_get_node_pos(node)
        ret = StatementAssertion(begin_pos, parse_ending_point(begin_pos, tokens, least_pos_of_node(node)), 'Statement')
    return ret, yes
def get_safe_statement_expression(node):
    safe = []
    for _, i in node.filter(javalang.tree.TryStatement):
        safe.extend(safe_nodes_in_try_block(i))
    return safe
# concept of parse_node_body_v2 is only StatementExpression contains assertion, and all assertion has a same level of importance.
def parse_node_body_v2(node, _globals, tokens):
    # should return StatementExpression's Pos which contains assertion
    safe = get_safe_statement_expression(node)
    res = []
    check = []
    for _, se in node.filter(javalang.tree.StatementExpression):
        _globals_bak = copy.deepcopy(_globals)
        add = False
        '''
        if se in safe:
            check = True
            continue
        '''
        invocation = se.expression
        if not isinstance(invocation, javalang.tree.MethodInvocation):
            continue
        if invocation.selectors:
            for sel in invocation.selectors:
                if not isinstance(sel, javalang.tree.MethodInvocation):
                    continue
                if containsAssert(sel, _globals_bak, check):
                    check.append('Selector contains assertion')
                    add = True
                    break
        if not add:
            add = containsAssert(invocation, _globals_bak, check)
        if add:
            if se in safe:
                check.append('StatementExpression is in safe: <{}.{}>'.format(se.expression.qualifier, se.expression.member))
            else:
                beg = try_get_node_pos(se)
                if beg == Pos(0, 0):
                    check.append('Begin pos is Pos(0, 0)')
                res.append(StatementAssertion(beg, parse_ending_point(beg, tokens, least_pos_of_node(se)), 'StatementExpression'))
    return res, check
def parse_node_boby(node, _globals, tokens):
    # in this case, we assume that only statements raising exceptions or error
    Assertions = []
    check = False
    for sub in node.body:
        if not isinstance(sub, javalang.tree.Statement):
            continue
        if isinstance(sub, javalang.tree.AssertStatement):
            begin_pos = try_get_node_pos(sub)
            end_pos = parse_ending_point(begin_pos, tokens, least_pos_of_node(sub))
            Assertions.append(StatementAssertion(begin_pos, end_pos, node.name))
        elif isinstance(sub, javalang.tree.IfStatement):
            res, che = read_if_statement(sub, _globals, tokens)
            if che:
                check = che
            Assertions.append(res)
        elif isinstance(sub, javalang.tree.TryStatement):
            res, che = read_try_statement(sub, _globals, tokens)
            if che:
                check = che
            Assertions.append(res)
        elif isinstance(sub, javalang.tree.ForStatement):
            res, che = read_for_statement(sub, _globals, tokens)
            if che:
                check = che
            Assertions.append(res)
        elif isinstance(sub, (javalang.tree.WhileStatement, javalang.tree.DoStatement, javalang.tree.SwitchStatement, javalang.tree.BlockStatement)):
            # not implemented
            for _, sub_i in sub:
                if containsAssert(sub_i, _globals):
                    check = True
        elif isinstance(sub, javalang.tree.StatementExpression):
            res, che = read_statement_expression(sub, _globals, tokens)
            if che:
                check = che
            Assertions.append(res)
        else:
            # not implemented
            continue
    return Assertions, check
def process_test_node_v2(filename, name, _globals=None, tokens=None):
    # name: name of failing test method
    # _globals: name map of the file AST
    if _globals == None:
        _globals = traverse_get_global(readFileToAST(filename))
    if tokens == None:
        tokens = tokenize_java_code(open(filename, 'r').read())
    # tokens: Separator tokens of file code
    node = get_only_node(name, _globals)
    begin_pos = try_get_node_pos(node)
    least = least_pos_of_node(node)
    end_pos = parse_ending_point(begin_pos, tokens, least)
    test = failing_test(begin_pos, end_pos, filename, name)
    childs, check = parse_node_body_v2(node, _globals, tokens)
    test.fill_child(childs)
    return test, check
def process_test_node(filename, name, _globals, tokens):
    node = get_only_node(name, _globals)
    begin_pos = try_get_node_pos(node)
    least = least_pos_of_node(node)
    end_pos = parse_ending_point(begin_pos, tokens, least)
    test = failing_test(begin_pos, end_pos, filename, name)
    childs, check = parse_node_body(node, _globals, tokens)
    test.fill_child(childs)
    return test, check
def test_process():
    #a, b = process_test_node_v2('./test_resource/code3.java', 'testTry')
    a, b = process_test_node_v2('./test_resource/code3.java', 'testTry')
    print(b)
    print(a)
    a.split()
    for i in a.splited:
        print(i)
if __name__ =='__main__':
    test_process()
