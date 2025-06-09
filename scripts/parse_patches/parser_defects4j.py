import unidiff
from math import inf

HEAD_OF_FILENAME = 2
INSERT = 0
REPLACE = 1
DELETE = 2

class MetaEdit:
    def __init__(self, _from, _to, _cont):
        self._from = _from
        self._to = _to
        self.cont = _cont

class Edit:
    def __init__(self, _next, _type, _from, _to=None):
        self.type = _type
        self.meta = _from
        self.target = _to
        self.next_line_in_source = _next.source_line_no
        self.next_line_in_target = _next.target_line_no

def process_meta(l, _type):
    if _type == DELETE:
        attr_name = 'source_line_no'
    elif _type == INSERT:
        attr_name = 'target_line_no'
    else:
        raise IOError()
    cont = []
    _min = inf
    _max = -inf
    for i in l:
        line = getattr(i, attr_name)
        _min = line if line < _min else _min
        _max = line if line > _max else _max
        cont.append(i.value)
    return MetaEdit(_min, _max, ''.join(cont))

def process_now(tp, _next):
    length = (len(tp[0]), len(tp[1]))
    if length == (0, 0):
        raise IOError()
    elif length[0] == 0:
        return Edit(_next, DELETE, process_meta(tp[1], DELETE))
    elif length[1] == 0:
        return Edit(_next, INSERT, process_meta(tp[0], INSERT))
    else:
        return Edit(_next, REPLACE, process_meta(tp[1], DELETE), process_meta(tp[0], INSERT))

class Parser:
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        self.edits = {}

    def parse(self, filename):
        return self.parse_file(filename)

    def parse_file(self, filename):
        edits = {}
        for patched_file in unidiff.PatchSet.from_filename(filename, encoding=self.encoding):
            name = patched_file.source_file.lstrip('a/')
            superHunks = []
            for superHunk in patched_file:
                superHunks.append(superHunk)
            edits[name] = self.parse_hunks(superHunks)
        return edits

    def parse_hunks(self, hunks):
        edits = []
        for hunk in hunks:
            edits.extend(self.parse_hunk(hunk))
        return edits

    def parse_hunk(self, hunk):
        edits = []
        temp = ([], [])
        is_chunk = False
        for line in hunk:
            if not line.is_context:
                is_chunk = True
            if not is_chunk:
                continue
            if line.is_context:
                edits.append(process_now(temp, line))
                temp = ([], [])
                is_chunk = False
                continue
            if line.is_added:
                idx = 0
            elif line.is_removed:
                idx = 1
            else:
                print('Unknown type: {}'.format(line.line_type))
                print('Line: {}'.format(line.value))
                continue
            temp[idx].append(line)
        return edits

def d4j_patch_to_map(edits):
    '''
        Reversed patch that defects4j uses is reversed again here
    '''
    #
    # format:
    # <root> { 
    #   num_of_hunks : int
    #   patch_idx : {
    #       patch_type = 'insert | delete | replace'
    #       file_name : str
    #       next_line_no : int
    #       // optional:
    #       from_line_no : int
    #       to_line_no : int
    #       replaced_with : str
    #       replaced : str
    #   }
    # }
    root = {}
    root['num_of_hunks'] = 0
    idx = -1
    for name in edits:
        edits_each_file = edits[name]
        root['num_of_hunks'] += len(edits_each_file)
        for edit in edits_each_file:
            idx += 1
            root[idx] = {}
            root[idx]['file_name'] = name
            if edit.type == REPLACE:
                patch_type = 'replace'
                root[idx]['from_line_no'] = edit.target._from
                root[idx]['to_line_no'] = edit.target._to
                root[idx]['replaced_with'] = edit.meta.cont
                root[idx]['replaced'] = edit.target.cont
            elif edit.type == INSERT:
                patch_type = 'delete'
                root[idx]['from_line_no'] = edit.meta._from
                root[idx]['to_line_no'] = edit.meta._to
                root[idx]['replaced'] = edit.meta.cont
            elif edit.type == DELETE:
                patch_type = 'insert'
                root[idx]['replaced_with'] = edit.meta.cont
            else:
                raise IOError()
            root[idx]['patch_type'] = patch_type
            root[idx]['next_line_no'] = edit.next_line_in_target
            assert root[idx]['patch_type'] in ('insert', 'delete', 'replace')
            assert root[idx]['next_line_no'] > 0
    assert root['num_of_hunks'] > 0
    return root

if __name__ == '__main__':
    parser = Parser()
    edits = parser.parse('./136.src.patch')
    print(d4j_patch_to_map(edits))
