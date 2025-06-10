from . import util
from . import config
import glob
def PIDS(args):
    for proj in util.listdir(f'{config.root}/projects/'):
        if not proj.startswith('.'):
            print(proj)
def BIDS(args):
    validator = util.args_validator(args, 'p', '', 'bids')
    validator.validate()
    if not validator.is_valid():
        validator.print_all(util.printc)
        util.printc('usage: catena4j bids -p project_name')
        return
    if not util.exists(f'{config.root}/projects/{args.p}'):
        util.printc('Project {args.p} does not exist')
        return
    if not util.exists(f'{config.root}/projects/{args.p}/bugs-registry.csv'):
        util.printc('Invalid project directory: missing bugs registry')
        return
    ids = set()
    with open(f'{config.root}/projects/{args.p}/bugs-registry.csv', 'r') as f:
        registry = f.read().splitlines()[1:]
    for line in registry:
        ids.add(int(line[:line.find(',')]))
    ids = list(ids)
    ids.sort()
    for bid in ids:
        print(bid)
def CIDS(args):
    validator = util.args_validator(args, 'pb', '', 'cids')
    validator.validate()
    if not validator.is_valid():
        validator.print_all(util.printc)
        util.printc('usage: catena4j cids -p project_name -b bug_id')
        return
    if not util.exists(f'{config.root}/projects/{args.p}'):
        util.printc('Project {args.p} does not exist')
        return
    if not util.exists(f'{config.root}/projects/{args.p}/bugs-registry.csv'):
        util.printc('Invalid project directory: missing bugs registry')
        return
    with open(f'{config.root}/projects/{args.p}/bugs-registry.csv', 'r') as f:
        registry = f.read().splitlines()[1:]
    for line in registry:
        line = line.split(',')
        if line[0].strip() == args.b:
            print(line[1].strip())
