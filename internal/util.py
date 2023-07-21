from . import config
import subprocess
import os
import sys

class C4JInsideError(Exception):
    pass
def printc(obj, flag=0, head=config.p_head):
    if flag:
        print('{}{}'.format(head, obj))
    else:
        print('{}{}'.format(head, obj), file=sys.stderr)
def get_d4j_cmd(cmd, args):
    base_cmd = [config.d4j, cmd]
    for i in args:
        base_cmd.append('-{}'.format(i))
        base_cmd.append(args[i])
    return base_cmd
def invoke_d4j(cmd, **args):
    base_cmd = get_d4j_cmd(cmd, args)
    ret = subprocess.run(base_cmd, capture_output=True)
    if ret.returncode:
        print(ret.stdout.decode('utf-8'))
        printc('Failed to invoke <{}>, see error info.\n{}'.format(' '.join(base_cmd), ret.stderr.decode('utf-8')))
        #raise C4JInsideError('Failed to invoke {}'.format(' '.join(base_cmd)))
        return False, ret.stdout.decode('utf-8'), ret.stderr.decode('utf-8')
    return True, ret.stdout.decode('utf-8'), ret.stderr.decode('utf-8')
def invoke_d4j_direct(cmd, **args):
    if os.system(' '.join(get_d4j_cmd(cmd, args))):
        printc('Failed to invoke <{}>, see error info.'.format(' '.join(get_d4j_cmd(cmd, args))))
        return -1
    return 0
def system(cmd):
    os.system(cmd)
def run_and_get(cmd, at:str):
    ret = subprocess.run(cmd, cwd=at, capture_output=True)
    if ret.returncode:
        return False, ret.stderr.decode('utf-8')
    else:
        return True, ret.stdout.decode('utf-8')
def exists(name):
    return os.path.exists(name)
