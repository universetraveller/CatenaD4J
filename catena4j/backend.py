from . import config
import sys
from . import util
from . import entries
def print_help():
    util.printc(config.helper, 1, '')
def is_help_spec(s):
    if s in ('-h', '--help'):
        return True
    return False
def is_help_cmd():
    if len(sys.argv) == 1 or is_help_spec(sys.argv[1]):
        return True
    return False
def d4j_backend():
    util.task_printc('Try to run defects4j').finish()
    util.invoke_d4j_direct(' '.join(sys.argv[1:]))
    return
def c4j_backend(args):
    if not args.command in entries.names():
        d4j_backend()
    else:
        entries.invoke(args.command, args)
