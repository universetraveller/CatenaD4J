from .constants import *


class MetaLineEdit:
    # edit type to edit single line
    def __init__(self, _type, back:bool=False, cont:str=None):
        self._type = _type
        self.initEdit(back, cont)
    def initEdit(self, back, cont):
        if self._type == INSERT:
            self.back = back
            self.cont = cont
        elif self._type == REPLACE:
            self.cont = cont
        elif self._type == DELETE:
            # do nothing
            pass
        else:
            raise NotImplementedError('Not support type {}'.format(self.type))
class IndexEdit:
    def __init__(self, line_no, inst):
        self.line_no = line_no
        self.inst = inst
class LineEdit:
    def __init__(self, _type, line_no:int, offset:int=None, code:str=None, _range:int=1, sub_offset=None, sub_code=None):
        self._type = _type
        if not offset == None:
            self.line_no = line_no + offset
        else:
            self.line_no = line_no
        self.code = code
        self._range = _range
        if not sub_offset == None:
            self.sub_line_no = line_no + sub_offset
        self.sub_code = sub_code
        self.translated = False
    def translate_into_meta_line_edits(self):
        self.translate(_to='meta_line_edits')
    def translate(self, _to:str):
        if self.translated:
            return
        self.index_edits = []
        if _to == 'meta_line_edits':
            self.translated = True
            if self._type == INSERT_BEFORE:
                self.index_edits.append(IndexEdit(self.line_no, MetaLineEdit(INSERT, cont=self.code)))
            elif self._type == INSERT_AFTER:
                self.index_edits.append(IndexEdit(self.line_no, MetaLineEdit(INSERT, back=True, cont=self.code)))
            elif self._type == DELETE:
                for i in range(self._range):
                    self.index_edits.append(IndexEdit(self.line_no + i, MetaLineEdit(DELETE)))
            elif self._type == REPLACE:
                self.index_edits.append(IndexEdit(self.line_no, MetaLineEdit(REPLACE, cont=self.code)))
                for i in range(1, self._range):
                    self.index_edits.append(IndexEdit(self.line_no + i, MetaLineEdit(DELETE)))
            else:
                pass
        else:
            raise NotImplementedError('This transformation is not implemented')
def createLineInsert(line, code, back=False, offset=None):
    if not back:
        return LineEdit(INSERT_BEFORE, line, offset, code)
    else:
        return LineEdit(INSERT_AFTER, line, offset, code)
def createLineDelete(line, _range=1, offset=None):
    return LineEdit(DELETE, line, offset, _range=_range)
def createLineReplace(line, code, _range=1, offset=None):
    return LineEdit(REPLACE, line, offset, code, _range)
