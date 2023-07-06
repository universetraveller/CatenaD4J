import javalang
import json
def code_to_AST(code:str):
    return javalang.parse.parse(code)
def file_to_AST(f):
    return code_to_AST(f.read())
def readFileToAST(filename:str):
    with open(filename, 'r') as f:
        return file_to_AST(f)
def traverse_get_global(root, _filter = javalang.tree.MethodDeclaration, _key = 'name'):
    _globals = {}
    for _, node in root.filter(_filter):
        _node_key = getattr(node, _key)
        if not _node_key in _globals:
            _globals[_node_key] = []
        _globals[_node_key].append(node)
    return _globals
def read_file_to_list(filename:str):
    with open(filename, 'r') as f:
        return f.read().splitlines()
def get_member_cache(filename:str = './table'):
    return read_file_to_list(filename)
def get_json_database(filename:str = './database.json'):
    with open(filename, 'r') as f:
        return json.load(f)
def tokenize_java_code(code:str):
    return list(javalang.tokenizer.tokenize(code))
def class_name(instance):
    return instance.__class__.__name__
def filter_tokens(tokens):
    tokens_map = {}
    for token in tokens:
        if not class_name(token) in tokens_map:
            tokens_map[class_name(token)] = []
        tokens_map[class_name(token)].append(token)
    return tokens_map
def get_only_node(name:str, _globals:dict):
    if not name in _globals:
        raise ParseError('Cannot find method <{}> in AST'.format(name))
    root = _globals[name]
    if not len(root) == 1:
        raise ParseError('Contains more than one version of method <{}>'.format(name))
    return root[0]

class Pos:
    def __init__(self, row, col):
        self.row = row
        self.col = col
    def __eq__(self, obj):
        return self.row == obj.row and self.col == obj.col
    def __gt__(self, obj):
        if self.row > obj.row:
            return True
        if self.row < obj.row:
            return False
        if self.col > obj.col:
            return True
        return False
    def __str__(self):
        return 'Pos({}, {})'.format(self.row, self.col)
class ParseError(Exception):
    pass
def _try_get_node_pos(node):
    try:
        pos = node.position
        return Pos(pos.line, pos.column)
    except:
        return Pos(0, 0)
def try_get_node_pos(node):
    return _try_get_node_pos(node)
def _node_of_pos(root, _pos):
    # test only
    line = _pos.row
    col = _pos.col
    for _, i in root:
        _pos1 = _try_get_node_pos(i)
        if _pos1.row == line:
            if col == 0 or col == _pos1.col:
                return i
    return javalang.ast.Node()
def try_accept(value, classname, tpos, tokens):
    while tpos < len(tokens):
        token = tokens[tpos]
        if not class_name(token) == classname:
            tpos += 1
            continue
        if not token.value == value:
            tpos += 1
            continue
        break
    return tpos
def _find_another_token(match, idx, tokens):
    _left = 1
    _right = 0
    pattern = tokens[idx].value
    _type = class_name(tokens[idx])
    while idx < len(tokens)-1:
        idx += 1
        token = tokens[idx]
        if not class_name(token) == _type:
            continue
        if token.value == match:
            _right += 1
        if token.value == pattern:
            _left += 1
        # should parse multi-block statements
        if _left == _right:
            return idx
    raise ParseError("Cannot find end of the code")
def least_pos_of_node(node, tokens=None):
    _max = Pos(0, 0)
    if tokens == None:
        pass
    elif isinstance(node, javalang.tree.TryStatement):
        _pos = _try_get_node_pos(node)
        tpos = -1
        for try_token in tokens:
            tpos += 1
            if try_token.position.line != _pos.row:
                continue
            if try_token.position.column < _pos.col:
                continue
            break
        if class_name(try_token) == 'Keyword' and try_token.value == 'try':
            tpos = try_accept('{', 'Separator', tpos, tokens)
            tpos = _find_another_token('}', tpos, tokens) + 1
            token = tokens[tpos]
            if class_name(token) == 'Keyword':
                if token.value in ('catch', 'finally'):
                    tpos = try_accept('{', 'Separator', tpos, tokens)
                    tpos = _find_another_token('}', tpos, tokens)
                    token = tokens[tpos]
            _max = Pos(token.position.line, token.position.column)
    for _, i in node:
        _pos = _try_get_node_pos(i)
        if _pos > _max:
            _max = _pos
    return _max
def _can_return(token, least):
    if least is None:
        return True
    lineDist = least.row - token.position.line
    if lineDist < 0:
        return True
    if lineDist > 0:
        return False
    # case that dist equals to  0
    colDist = least.col - token.position.column
    if colDist > 0:
        return False
    return True
def _find_another(match, idx, tokens, least):
    _left = 1
    _right = 0
    pattern = tokens[idx].value
    _type = class_name(tokens[idx])
    for token in tokens[idx+1:]:
        if not class_name(token) == _type:
            continue
        if token.value == match:
            _right += 1
        if token.value == pattern:
            _left += 1
        # should parse multi-block statements
        if _left == _right and _can_return(token, least):
            return Pos(token.position.line, token.position.column)
    raise ParseError("Cannot find end of the code")
def parse_ending_point(_from:Pos, tokens:list, least:Pos=None):
    # not support switch statements now
    idx = 0
    max_idx = len(tokens)
    if tokens[max_idx - 1].position.line < _from.row:
        raise ParseError("Fail to locate beginning point")
    while tokens[idx].position.line < _from.row: 
        idx += 1
    while tokens[idx].position.line == _from.row and tokens[idx].position.column < _from.col:
        idx += 1
    if idx > 0 and tokens[idx].position.line >= _from.row:
        t = tokens[idx-1]
        if t.position.column + len(t.value) > _from.col and t.position.line == _from.row:
            idx -= 1
    hit = False
    while idx < max_idx:
        t = tokens[idx]
        if not class_name(t) == 'Separator':
            idx += 1
            continue
        if not hit:
            hit = True
            if t.value in ('}', ')', ']'):
                raise ParseError("Lack of matched bracket: <{}> at line {}".format(t.value, t.position.line))
        if t.value == '(':
            mid_p = _find_another(')', idx, tokens, None)
            while not (t.position.line == mid_p.row and t.position.column == mid_p.col):
                idx += 1
                t = tokens[idx]
        if t.value == ';':
            return Pos(t.position.line, t.position.column)
        if t.value == '{':
            return _find_another('}', idx, tokens, least)
        idx += 1
    raise ParseError("No statement here")
def catch_code(code, _begin:Pos, _end:Pos):
    codeList = code.splitlines()
    return _catch_code(codeList, _begin, _end)
def _catch_code(cl, begin, end):
    code = ''
    bgc = begin.col
    if bgc > 0:
        bgc -= 1
    bgl = cl[begin.row-1][bgc:]
    edc = end.col
    edl = cl[end.row-1][:edc]
    code = '{}\n{}\n{}'.format(bgl, '\n'.join(cl[begin.row:end.row-1]), edl)
    return code
def catch_block(code, _begin:Pos, _end:Pos):
    codeList = code.splitlines()
    return _catch_block(codeList, _begin, _end)
def _catch_block(cl, begin, end):
    return '\n'.join(cl[begin.row-1:end.row])
def insert_at_pos(s, pos, codeList, back=False):
    isString = False
    if type(codeList) == str:
        isString = True
        codeList = codeList.splitlines()
    ori = codeList[pos.row - 1]
    pointer = pos.col
    if not back:
        pointer -= 1
    codeList[pos.row - 1] = '{}{}{}'.format(ori[:pointer], s, ori[pointer:])
    if isString:
        return '\n'.join(codeList)
    return codeList
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
def safe_nodes_in_try_block(node):
    # should not trace statements in try block
    # except the block has no fail()
    if not isinstance(node, javalang.tree.TryStatement):
        return []
    safe = []
    ret = False
    for subnode in node.block:
        if not isinstance(subnode, javalang.tree.StatementExpression):
            continue
        if not isinstance(subnode.expression, javalang.tree.MethodInvocation):
            continue
        if subnode.expression.member == 'fail':
            ret = True
            continue
        if subnode.expression.member.startswith('assert'):
            continue
        safe.append(subnode)
    if not ret:
        safe = []
    return safe
def try_accept_update_bool(ori, new):
    if ori:
        return ori
    if new:
        return new
    return ori
def anyMatchPartial(matchList, shouldMatched):
    for i in matchList:
        if i in parseUpperCase(shouldMatched):
            return True
    return False
