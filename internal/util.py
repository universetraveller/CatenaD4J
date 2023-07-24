from . import config
import subprocess
import os
import sys
class C4JInsideError(Exception):
    pass
def printc(obj, flag=0, head=config.p_head, end='\n'):
    if flag:
        print('{}{}'.format(head, obj), end=end, flush=True)
    else:
        print('{}{}'.format(head, obj), end=end, file=sys.stderr, flush=True)
class FOR_EACH:
    def __init__(self, iterable, do):
        self.iterable = iterable
        self.do = do
    def run(self):
        for i in self.iterable:
            self.do(i)
class INVOKE0:
    def __init__(self, do):
        self.do = do
    def run(self):
        self.do()
class INVOKE1:
    def __init__(self, do, arg):
        self.do = do
        self.arg = arg
    def run(self):
        self.do(arg)
class INVOKE:
    def __init__(self, __func, *args, **argsm):
        self.func = __func
        self.args = args
        self.argsm = argsm
    def run(self):
        self.result = self.func(*self.args, **self.argsm)
        return self.result
    def invoke(self, *args, **argsm):
        self.result = self.func(*args, **argsm)
        return self.result
    def get_result(self):
        return self.result
class task_printer:
    def __init__(self, title, finishing, failed, anchor, head):
        self.finishing = finishing
        self.failed = failed
        points = anchor - len(title) - len(head)
        if points < 0:
            points=0
        printc(title, head=head, end='')
        printc('{} '.format('.'*points), head='', end='')
    def finish(self):
        printc(self.finishing, head='')
    def fail(self):
        printc(self.failed, head='')
def task_printc(finished, finishing='Finished', failed='Failed', anchor=75, head=config.p_head):
    return task_printer(finished, finishing, failed, anchor, head)
def auto_task_printc(task, finished, finishing='Finished', failed='Failed', anchor=75, head=config.p_head, reraise=True):
    printer = task_printc(finished, finishing, failed, anchor, head)
    try:
        task.run()
    except:
        printer.fail()
        if reraise:
            raise
        return -1
    printer.finish()
    return 0
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
def config_run(config, default, func, *args, **argsm):
    return func(*args, **argsm) if config else default
def get_c4j_tag(pid, bid, cid, buggy):
    return config.TAG_PATTERN.format(pid=pid, bid=bid, cid=cid, buggy='BUGGY' if buggy else 'FIXED')
