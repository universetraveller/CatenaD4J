from .constants import *
from .EditTypes import LineEdit
from .Commit import FileDiff
import os

class CacheDiff(FileDiff):
    # [[origin], [edited]]
    def __init__(self, filepath, inst):
        self.filename = filepath
        self.inst = inst
    def apply(self, FileInst):
        if FileInst.edited:
            FileInst.abortEdits()
        for i, j in enumerate(self.inst[1]):
            if not self.inst[0][i].line_no == j.line_no:
                return False
            if not self.inst[0][i] == FileInst.content[j.line_no-1]:
                return False
            FileInst.content[j.line_no-1]=j
        return True
    def restore(self, FileInst):
        if FileInst.edited:
            FileInst.abortEdits()
        for i, j in enumerate(self.inst[0]):
            if not self.inst[1][i].line_no == j.line_no:
                return False
            if not self.inst[1][i] == FileInst.content[j.line_no-1]:
                return False
            FileInst.content[j.line_no-1]=j
        return True
    def __str__(self):
        content = ''
        for i, j in enumerate(self.inst[0]):
            cont0 = str(j).splitlines()
            cont1 = str(self.inst[1][i]).splitlines()
            for k in cont0:
                content += '- {}\n'.format(k)
            for k in cont1:
                content += '+ {}\n'.format(k)
        return '--- {}\n+++ {}\n{}'.format(self.filename, self.filename, content)
class EditCacheLine:
    def __init__(self, line_no:int, cont:int):
        self.line_no = line_no
        self.cont = cont
        self.edited = False
        self.prefix = ''
        self.suffix = ''
    def __eq__(self, obj):
        return self.line_no == obj.line_no and self.cont == obj.cont and self.edited == obj.edited and self.prefix == obj.prefix and self.suffix == obj.suffix
    def apply_edit(self, MetaEditInst):
        self.edited = True
        if MetaEditInst._type == INSERT:
            self.insert(MetaEditInst.cont, MetaEditInst.back)
        elif MetaEditInst._type == DELETE:
            self.delete()
        elif MetaEditInst._type == REPLACE:
            self.replace(MetaEditInst.cont)
        else:
            raise NotImplementedError('Unsupported edit type: {}'.format(MetaEditInst._type))
    def commit(self):
        self.cont = '{}{}{}'.format(self.prefix, self.cont, self.suffix)
        self.prefix = ''
        self.suffix = ''
        self.edited = False
    def insert(self, cont, back):
        if back:
            self.suffix += ' {}'.format(cont)
        else:
            self.prefix = '{} {}'.format(cont, self.prefix)
    def delete(self):
        self.cont = ''
    def replace(self, cont):
        self.cont = cont
    def __str__(self):
        return '{}{}{}'.format(self.prefix, self.cont, self.suffix)
    def copy(self):
        backup = EditCacheLine(self.line_no, self.cont)
        backup.edited = self.edited
        backup.prefix = self.prefix
        backup.suffix = self.suffix
        return backup
class EditCacheFile:
    def __init__(self, filepath:str, encoding='utf-8'):
        self.filepath = filepath
        self.edited = False
        self.content = []
        self.uncommitted = []
        self.encoding=encoding
        self.read()
    def read(self):
        with open(self.filepath, 'r', encoding=self.encoding) as f:
            # with return characters
            # for line commit would add suffix after content
            f = f.readlines()
        for idx in range(len(f)):
            self.content.append(EditCacheLine(idx + 1, f[idx]))
    def toString(self, keeps_line_no:bool=False):
        res = ''
        for i in self.content:
            if keeps_line_no:
                res += '{}\n'.format(str(i).replace('\n', ''))
            else:
                res += str(i)
        return res
    def __str__(self):
        return self.toString(False)
    def diff_with(self, obj):
        raise NotImplementedError('Not allow to use diff')
    def get_code(self, beg, end):
        res = ''
        for i in range(beg-1, end):
            res += str(self.content[i])
        return res
    def apply_edit(self, EditInst):
        self.edited = True
        if EditInst._type == DELETE_FILE:
            os.remove(self.filepath)
            return
        edits = []
        if EditInst._type == INSERT_BEFORE_AFTER:
            edits.append(LineEdit(INSERT_BEFORE, EditInst.line_no, code=EditInst.code))
            edits.append(LineEdit(INSERT_AFTER, EditInst.sub_line_no, code=EditInst.sub_code))
        elif EditInst._type == WRAP:
            edits.append(LineEdit(INSERT_BEFORE, EditInst.line_no, code=EditInst.code))
            edits.append(LineEdit(INSERT_AFTER, EditInst.line_no+EditInst._range-1, code='}'))
        elif EditInst._type == MOVE_BEFORE:
            edits.append(LineEdit(DELETE, EditInst.line_no, _range=EditInst._range))
            edits.append(LineEdit(INSERT_BEFORE, EditInst.sub_line_no, code=self.get_code(EditInst.line_no, EditInst.line_no+EditInst._range-1)))
        elif EditInst._type == MOVE_AFTER:
            edits.append(LineEdit(DELETE, EditInst.line_no, _range=EditInst._range))
            edits.append(LineEdit(INSERT_AFTER, EditInst.sub_line_no, code=self.get_code(EditInst.line_no, EditInst.line_no+EditInst._range-1)))
        else:
            edits.append(EditInst)
        for edit in edits:
            edit.translate_into_meta_line_edits()
        for edit in edits:
            for idx_edit in edit.index_edits:
                if len(self.content) == idx_edit.line_no - 1:
                    self.content.append(EditCacheLine(1, ''))
                lineInst = self.content[idx_edit.line_no - 1]
                if not lineInst.line_no == idx_edit.line_no:
                    raise ValueError('Unmatched line number: {} and {}\n\tin {}'.format(lineInst.line_no, idx_edit.line_no, self.filepath))
                self.uncommitted.append(lineInst.copy())
                lineInst.apply_edit(idx_edit.inst)
    def commit(self):
        if not self.edited:
            raise ValueError('Nothing to commit')
        self.edited = False
        origin = []
        for i in self.uncommitted:
            origin.append(i)
        self.uncommitted = []
        after = []
        for i in origin:
            _line_no = i.line_no
            lineInst = self.content[_line_no-1]
            if not lineInst.line_no == _line_no:
                raise ValueError('Unmatched line number: {} and {}\n\tin {}'.format(lineInst.line_no, _line_no, self.filepath))
            lineInst.commit()
            after.append(lineInst.copy())
        return CacheDiff(self.filepath, [origin, after])
    def abortEdits(self):
        if not self.edited:
            return False
        self.edited = False
        origin = []
        for i in self.uncommitted:
            origin.append(i)
        self.uncommitted = []
        for i in origin:
            _line_no = i.line_no
            lineInst = self.content[_line_no-1]
            if not lineInst.line_no == _line_no:
                raise ValueError('Unmatched line number: {} and {}\n\tin {}'.format(lineInst.line_no, _line_no, self.filepath))
            self.content[_line_no-1] = i
        return True
