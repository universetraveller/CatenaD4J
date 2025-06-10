


from .constants import BEGIN_POINTER
class FileDiff:
    def __inir__(self, filename, inst=None):
        self.filename = filename
        self.inst = inst
    def apply(self):
        raise NotImplementedError('Method apply has not been implemented now')
    def restore(self):
        raise NotImplementedError('Method restore has not been implemented now')
class Commit:
    def __init__(self, commit_id, pre, message, _changes=[]):
        if commit_id == BEGIN_POINTER:
            raise ValueError('This commit id is not allowed')
        self.commit_id = commit_id
        self.pre = pre
        self.message = message
        self.changes = []
        for i in _changes:
            self.changes.append(i)
    def addChange(self, DiffInst):
        self.changes.append(DiffInst)
    def __str__(self):
        diffs = ''
        for i in self.changes:
            diffs += '{}\n'.format(i)
        return 'Commit id: {}\nPre commit id: {}\n\n\t{}\n\nChanges:\n{}'.format(self.commit_id, self.pre, self.message, diffs)
