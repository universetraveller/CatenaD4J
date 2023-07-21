from . import config
from . import util
from . import ProjectManager

class DefaultPathLoader:
    def __init__(self):
        self.root = config.root
        self.path = '{}/projects/{}/{}/{}.{}'
    def construct_path(self, proj, bid, cid, attr):
        return self.path.format(self.root, proj, bid, cid, attr)
    def get_attr(self, proj, bid, cid, attr):
        with open(self.construct_path(proj, bid, cid, attr), 'r') as f:
            f = f.read().splitlines()
        return f
    def load(self, proj, bid, cid, buggy, wd):
        pass
