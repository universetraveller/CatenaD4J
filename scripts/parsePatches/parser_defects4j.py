import unidiff
import json

HEAD_OF_FILENAME = 2
INSERT = 0
REPLACE = 1
DELETE = 2
class IsNotImplementedException(Exception):
    pass
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
    cont = ''
    if _type == DELETE:
        attr_name = 'source_line_no'
    elif _type == INSERT:
        attr_name = 'target_line_no'
    else:
        raise IOError()
    lines = []
    for i in l:
        lines.append(getattr(i, attr_name))
        cont += i.value
    return MetaEdit(min(lines), max(lines), cont)
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
    def __init__(self, obj, encoding='utf-8'):
        self.obj = obj
        #self.parse()
        self.encoding = encoding
    def parse(self):
        self.files = {}
        if isinstance(self.obj, list):
            for i in self.obj:
                self.parse_file(i)
        elif isinstance(self.obj, str):
            self.parse_file(self.obj)
        else:
            raise IsNotImplementedException()
    def parse_file(self, filename):
        for patched_file in unidiff.PatchSet.from_filename(filename, encoding=self.encoding):
            name = patched_file.source_file[HEAD_OF_FILENAME:]
            superHunks = []
            for superHunk in patched_file:
                superHunks.append(superHunk)
            self.files[name] = superHunks
        self.parse_hunks()
    def parse_hunks(self):
        self.edits = {}
        for name in self.files:
            Hunks = self.files[name]
            self.edits[name] = []
            for hunk in Hunks:
                self.edits[name].extend(self.parse_hunk(hunk))
    def parse_hunk(self, hunk):
        edits = []
        temp = ([], [])
        tag = False
        for line in hunk:
            if not line.is_context:
                tag = True
            if not tag:
                continue
            if line.is_context:
                edits.append(process_now(temp, line))
                temp = ([], [])
                tag = False
                continue
            if line.is_added:
                idx = 0
            elif line.is_removed:
                idx = 1
            else:
                print('Unk type: {}'.format(line.line_type))
                print('Line: {}'.format(line.value))
                continue
            temp[idx].append(line)
        return edits
    def dump_d4j_patch(self):
        self.d4j_patch_to_map()
        return json.dumps(self.root, indent=4)
    def d4j_patch_to_map(self):
        # defects4j-style patch is from buggy to fixed patch
        # original patch is from fixed to buggy
        # d4j-style from buggy to fixed patch is reversed version of original patch
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
        #       }
        # }
        root = {}
        root['num_of_hunks'] = 0
        idx = -1
        for name in self.edits:
            edits = self.edits[name]
            root['num_of_hunks'] += len(edits)
            for edit in edits:
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
        self.root = root
        return self.root
if __name__ == '__main__':
    parser = Parser(['./136.src.patch'])
    parser.parse()
    print(parser.dump_d4j_patch())
