import heapq
from collections import Counter
#from collections import OrderedDict
DEFAULT_METHOD = lambda *x:x[-1]

class TraverseListener:
    def __init__(self):
        self.collected = []
        self.callbacks = [DEFAULT_METHOD, DEFAULT_METHOD, DEFAULT_METHOD, DEFAULT_METHOD]
        self.ignored = set()

    def invoke_callback(self, idx, *args):
        ret = self.callbacks[idx](*args)
        if not ret in self.ignored:
            self.collected.append(ret)
        return ret

    def traverse_started(self, node):
        return self.invoke_callback(0, node)

    def traverse_child_started(self, node, child):
        return self.invoke_callback(1, node, child)

    def traverse_child_finished(self, node, child):
        return self.invoke_callback(2, node, child)

    def traverse_finished(self, node):
        return self.invoke_callback(3, node)

    def register_callback_function(self, idx, func):
        self.callbacks[idx] = func

    def clear(self):
        self.collected.clear()

    def ignore(self, obj):
        self.ignored.add(obj)

def get_listener_instance():
    return TraverseListener()

class HuffmanNode:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def to_tree(self):
        if self.left is None and self.right is None:
            return self.char
        return (self.left.to_tree(), self.right.to_tree())

class StaticHuffmanRegistry:
    def __init__(self, chars: list):
        self.freq = Counter(chars)
        self.codes = {}
        self.root = None
        self._build_tree()

    def _build_tree(self):
        heap = [HuffmanNode(char, freq) for char, freq in self.freq.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            a = heapq.heappop(heap)
            b = heapq.heappop(heap)
            merged = HuffmanNode(freq=a.freq + b.freq)
            merged.left = a
            merged.right = b
            heapq.heappush(heap, merged)

        self._generate_codes(heap[0], (0b0, 0))
        self.root = heap[0]

    def _generate_codes(self, node, code):
        if node.char is not None:
            self.codes[node.char] = code
            return
        code, length = code
        leftcode = code << 1
        rightcode = code << 1
        rightcode += 0b1
        self._generate_codes(node.left, (leftcode, length + 1))
        self._generate_codes(node.right, (rightcode, length + 1))

    def dump_tree(self):
        return self.root.to_tree(), self.codes

class Node:
    def __init__(self, text):
        self.text = text
        self.children = {}
        #self.children = OrderedDict()
        self.is_head = False
        self.is_tail = False

    def __lt__(self, o):
        return self.text < o.text

    def has_child(self, text):
        return text in self.children

    def add_child(self, text):
        if self.has_child(text):
            return
        self.children[text] = Node(text)

    def get_child(self, text):
        if self.has_child(text):
            return self.children.get(text)
        raise ValueError(f'Could not find child {text}')

    def to_tree(self, convert=lambda x:x):
        root = []
        for child in self.children:
            child = self.children.get(child)
            root.append(child.to_tree(convert=convert))
            if self.is_tail:
                root.append(None)
        if not root:
            return convert(self.text)
        #return (convert(self.text), root) if self.text else root
        return root if self.text is None else (convert(self.text), root)

    def dft(self, listener=None):
        if listener is None:
            listener = get_listener_instance()
        listener.traverse_started(self)
        for child in sorted(self.children.values(), reverse=True):
            listener.traverse_child_started(self, child)
            child.dft(listener)
            listener.traverse_child_finished(self, child)
        listener.traverse_finished(self)
        return listener

def merge_text(text, node):
    if not text in node.children:
        node.children[text] = Node(text)
    return node.children.get(text)

def merge_list(l, root):
    i = iter(l)
    root = merge_text(next(i), root)
    root.is_head = True
    for text in i:
        root = merge_text(text, root)
    root.is_tail = True

def build_from_ll(ll):
    root = Node(None)
    for l in ll:
        merge_list(l, root)
    return root

def from_tree(tree, convert=lambda x:x):
    res = []
    prefix = []
    if tree is None:
        return [[]]
    if isinstance(tree, (str, int)):
        return [[convert(tree)]]
    if isinstance(tree, tuple):
        prefix = [convert(tree[0])]
        tree = tree[1]
    for child in tree:
        for subtree in from_tree(child, convert):
            _ = prefix.copy()
            _.extend(subtree)
            res.append(_)
    return res

class Registry:
    def __init__(self):
        self.index = 0
        self.registry = {}
        self.static = []

    def get_map(self):
        ret = {}
        for i in self.static:
            ret[i] = self.registry[i]
        for i in self.registry:
            ret[self.registry[i]] = i
        return ret

    def get_id(self, identifier, static=False):
        # Patch to ensure order
        if isinstance(identifier, int):
            return identifier
        if static:
            self.static.append(identifier)
        if not identifier in self.registry:
            self.registry[identifier] = self.index
            self.index += 1
        return self.registry[identifier]

def test_compress():
    with open('./Chart/20/tests.relevant') as f:
        data = f.read().splitlines()
    root = build_from_ll(list(map(lambda x:x.split('.'), data)))
    tree = root.to_tree()
    print(tree)
    import json
    print(json.dumps(tree, indent=2))
    rebuild = list(map(lambda x:'.'.join(x), from_tree(tree)))
    for i in range(len(rebuild)):
        assert rebuild[i] == data[i]

def test_compress_properties():
    '''
       Bug found at Codec 13-16 cp.test and all cp.compile and cp.test
       
       [FIXED] Path {user.home} (/root in this machine) is used
       but the rebuilt version does not contain the leading /;
       [REASON] Node.to_tree skips empty text
       [PATCH] Only check if the text is None

       [FIXED] The rebuilt classpaths are in random sequence;
       [REASON] The tree is not order sensitive, every rebuilding process
       would try to build a tree's subtree first
       [PATCH] Add ranking support for classpaths but it causes the compressed
       file size to increase 24K

       [FIXED] The rebuilt version lacks covered path, e.g. src/main/resources
       src/main/resources/xxx.jar are both in the original cp but the rebuilt cp
       skips the previous one
       [REASON] Node.to_tree could not tell the tail
       [PATCH] Add a None at the end of the list (is_tail is True)
    '''
    import gzip
    import pickle
    with gzip.GzipFile(filename='test/properties.pkl.gz') as f:
        d = pickle.loads(f.read())
    index = d['index']
    # Patch to ensure order
    def index_get(i):
        return index.get(i, i)
    #    return i if i < 0 else index.get(i)
    def get(proj, id, prop):
        proj = d[index.get(proj)]
        id = proj[int(id)]
        # Patch to ensure order
        res = from_tree(id[index.get(prop)], index_get)
        #res = from_tree(id[index.get(prop)], index.get)
        if prop == 'tests.trigger':
            return list(map(lambda x:f"{'.'.join(x[:-1])}::{x[-1]}", res))

        elif prop.startswith('classes') or prop.startswith('tests'):
            return list(map(lambda x:'.'.join(x), res))
        
        elif prop.startswith('cp'):
            # Patch to ensure order
            res.sort(key=lambda x:x[-1], reverse=True)
            #res.sort(key=lambda x:int(x[-1]))
            return ':'.join(map(lambda x:'/'.join(x[:-1]), res))
            #return ':'.join(map(lambda x:'/'.join(x), res))

        elif prop.startswith('dir'):
            return '/'.join(res[0])

    import json
    import time

    ct = 0
    ctn = 0
    def execute(f, *args, **kwargs):
        nonlocal ct, ctn
        start = time.perf_counter_ns()
        res = f(*args, **kwargs)
        end = time.perf_counter_ns()
        ct += end - start
        ctn += 1
        return res

    with open('/root/workbench/Archived/d4j_export/database.json') as f:
        d1 = json.load(f)
    for proj in d1:
        for id in d1[proj]:
            for prop in d1[proj][id]:
                _prop = d1[proj][id][prop]
                _prop1 = execute(get, proj, id, prop)
                if not _prop == _prop1:
                    print(f'Expected\n"{_prop}" but got\n"{_prop1}"\n  at {proj} {id} {prop}')
    print(f'avg: {ct/ctn} ns')

def test_Codec_cp_resources():
    l = [['a', 'b', 'c'], ['a', 'b', 'c', 'd']]
    root = build_from_ll(l)
    assert len(from_tree(root.to_tree())) == len(l)

def test_Codec_cp_empty_leading():
    l = [['', 'a', 'b', 'c']]
    root = build_from_ll(l)
    assert from_tree(root.to_tree()) == l

def test_cp_rebuilt_sequence():
    cp = 'a/b/c:d/e/f:a/g/h'
    _prop = cp.split(':')
    _prop = list(map(lambda x:x.split('/'), _prop))
    root = build_from_ll(_prop)
    assert ':'.join(map(lambda x:'/'.join(x), from_tree(root.to_tree()))) == cp

if __name__ == '__main__':
    test_Codec_cp_resources()
    test_Codec_cp_empty_leading()
    #test_cp_rebuilt_sequence()
    test_compress_properties()
