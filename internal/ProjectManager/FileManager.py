
import os
from .constants import EMPTY_ALIAS, BEGIN_POINTER
from .Commit import Commit
class NameConflictError(Exception):
    pass
class CommitFailed(Exception):
    pass
def findLastMatch(l1, l2):
    lt1 = len(l1)
    lt2 = len(l2)
    if lt1 == 0 or lt2 == 0:
        return None
    if not l1[0] == l2[0]:
        return None
    idx = 0
    max_idx = min(lt1, lt2)
    while idx < max_idx:
        if not l1[idx] == l2[idx]:
            return l1[idx-1]
        idx += 1
    return l1[max_idx-1]
backup_encoding = ['utf-8', 'latin-1']
def validate_encoding(filename):
    for enc in backup_encoding:
        try:
            with open(filename, 'r', encoding=enc) as f:
                f = f.read()
            return enc
        except FileNotFoundError:
            with open(filename, 'w', encoding=enc) as f:
                pass
            return enc
        except:
            continue
    return backup_encoding[0]
class FileEdit:
    def __init__(self, filepath, editInst):
        self.filepath = filepath
        self.editInst = editInst
    def key(self):
        return self.filepath
    def apply_to(self, fmInst):
        fmInst.get(self.key()).apply_edit(self.editInst)
class BaseFileManager:
    def __init__(self, base_dir:str):
        self.base_dir = base_dir
        self.files = {}
    def setFileFormat(self, FileClass):
        self.FileClass = FileClass
    def setFile(self, key, f):
        self.files[key] = f
    def getFile(self, key):
        if key in self.files:
            return self.files[key]
        raise KeyError('No file named {}'.format(key))
    def removeFile(self, key):
        if key in self.files:
            self.files.pop(key)
class FileManager(BaseFileManager):
    def __init__(self, base_dir:str, FileClass=None):
        super().__init__(base_dir)
        self.pointer = BEGIN_POINTER
        self.commits = {}
        self.alias_map = {}
        self.setFileFormat(FileClass)
    def trace_file(self, filepath:str, alias:str=EMPTY_ALIAS, encoding=None):
        if not isinstance(alias, str):
            raise TypeError('Only support string alias')
        if self.FileClass == None:
            raise TypeError('Invalid file class')
        if alias == EMPTY_ALIAS:
            pass
        elif alias.startswith(self.base_dir):
            raise NameConflictError('Not allow to use alias begins with base_dir \'{}\''.format(self.base_dir))
        elif alias in self.files:
            raise NameConflictError('{} is used'.format(alias))
        elif not alias in self.alias_map:
            self.alias_map[alias] = filepath
        else:
            raise NameConflictError('{} is used'.format(alias))
        fullpath = '{}/{}'.format(self.base_dir, filepath)
        if encoding == None:
            encoding = validate_encoding(fullpath)
        self.setFile(filepath, self.FileClass(fullpath, encoding=encoding))
        self.alias_map[fullpath] = filepath
    def remove(self, name:str):
        if name in self.alias_map:
            filename = self.alias_map[name]
            self.alias_map.pop(name)
            name = filename
        self.removeFile(name)
    def get(self, name:str):
        if name in self.alias_map:
            name = self.alias_map[name]
        return self.getFile(name)
    def commit(self, message:str, idx:int=BEGIN_POINTER, alias:str=EMPTY_ALIAS):
        if not isinstance(alias, str):
            raise TypeError('Only support string alias')
        if not isinstance(idx, int):
            raise TypeError('Only support int commit id')
        if idx in self.commits:
            raise CommitFailed('commit id {} is used'.format(idx))
        if idx == BEGIN_POINTER:
            idx = self.pointer + 1
            while idx in self.commits:
                idx += 1
        if alias == EMPTY_ALIAS:
            pass
        elif alias in self.files:
            raise NameConflictError('{} is used'.format(alias))
        elif alias.startswith(self.base_dir):
            raise NameConflictError('Not allow to use alias begins with base_dir {}'.format(self.base_dir))
        elif not alias in self.alias_map:
            self.alias_map[alias] = idx
        else:
            raise NameConflictError('{} is used'.format(alias))
        commit = Commit(idx, self.pointer, message)
        tag = False
        for i in self.files:
            fileInst = self.getFile(i)
            if fileInst.edited:
                tag = True
                commit.addChange(fileInst.commit())
        if not tag:
            raise CommitFailed('Nothing to commit')
        self.commits[idx] = commit
        self.pointer = idx
        return True
    def reset(self):
        for filename in self.files:
            fileInst = self.getFile(filename)
            if fileInst.edited:
                fileInst.abortEdits()
    def apply_edit(self, EditInst):
        EditInst.apply_to(self)
    def write_to_file(self):
        for name in self.files:
            fileInst = self.getFile(name)
            if os.path.exists(fileInst.filepath):
                with open('{}/{}'.format(self.base_dir, name), 'w') as f:
                    f.write(fileInst.toString())
        return True
    def _findRootPath(self, commit_id):
        if commit_id == BEGIN_POINTER:
            return [BEGIN_POINTER]
        p = []
        p.append(commit_id)
        commit = self.commits[commit_id]
        while commit.pre != BEGIN_POINTER:
            p.append(commit.pre)
            commit = self.commits[commit.pre]
        p.append(BEGIN_POINTER)
        return p
    def checkout(self, commit_id):
        if commit_id in self.alias_map:
            commit_id = self.alias_map[commit_id]
        if commit_id == self.pointer:
            return True
        restorePath = self._findRootPath(self.pointer)
        applyPath = self._findRootPath(commit_id)
        last = findLastMatch(restorePath[::-1], applyPath[::-1])
        self.reset()
        for i in restorePath:
            if i == last:
                break
            commit = self.commits[i]
            for j in commit.changes:
                j.restore(self.get(j.filename))
        tasks = []
        for i in applyPath:
            if i == last:
                break
            commit = self.commits[i]
            tasks.append(commit)
        for task in tasks[::-1]:
            for i in task.changes:
                i.apply(self.get(i.filename))
        self.pointer = commit_id
        return True
    def dump(filepath:str):
        raise NotImplementedError('Method to dump file manager is not implemented now')
