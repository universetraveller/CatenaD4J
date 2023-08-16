from . import util
from . import loaders
from . import backend
from . import config
def sanity_check(task):
    registry = open('{}/projects/{}/bugs-registry.csv'.format(config.root, task.proj), 'r').read().splitlines()[1:]
    for line in registry:
        line = line.split(',')
        if task.bug_id == line[0].strip() and task.cid == line[1].strip():
            task.loader = loaders.get_loader(line[2].strip())
            return True
    util.printc('Cannot find cid in bugs-registry')
    return False
def print_help():
    util.printc('usage: catena4j export -p properties [-w working_directory] [-o output_file]')
__PROP_TO_TRAP = ['tests.trigger', 'classes.modified', 'patch']
class Task:
    def __init__(self):
        self.stat = None
        self.loader = None
        self.proj = None
        self.bug_id = None
        self.cid = None
        self.prop = None
        self.wd = None
        self.opf = None
def validate(args):
    validator = util.args_validator(args, 'p',  'wo', 'export')
    validator.validate()
    if validator.is_valid():
        return True
    validator.print_all(util.printc)
    return False
INVALID = -1
COMMON= 0
D4J = 1
def tokenize(args):
    task = Task()
    if args.w == None:
        task.wd = '.'
    else:
        task.wd = args.w
    if not args.o == None:
        task.opf = args.o
    if not args.p in __PROP_TO_TRAP:
        task.stat = D4J
    else:
        task.stat = COMMON
        task.prop = args.p
    if not util.exists('{}/.catena4j.info'.format(task.wd)):
        task.stat = D4J
        util.printc('Cannot find info file')
        return task
    else:
        with open('{}/.catena4j.info'.format(task.wd), 'r') as f:
            f = f.read().splitlines()
        for line in f:
            if 'project' in line:
                task.proj = line.split('=')[1].strip()
            elif 'bugid' in line:
                task.bug_id = line.split('=')[1].strip()
            elif 'cid' in line:
                task.cid = line.split('=')[1].strip()
        if not sanity_check(task):
            task.stat = INVALID
        return task
def EXPORT(args):
    if not validate(args):
        print_help()
        return
    task = tokenize(args)
    if task.stat == INVALID:
        util.printc('Task ends with invalid arguments')
    if task.stat == D4J:
        backend.d4j_backend()
    if task.stat == COMMON:
        attr = task.loader.get_attr(task.proj, task.bug_id, task.cid, task.prop)
        if not task.opf == None:
            with open(task.opf, 'r') as f:
                f.write(attr)
                f.flush()
        else:
            end_ch = '\n'
            if attr.endswith('\n'):
                end_ch = ''
            print(attr, end=end_ch, flush=True)
