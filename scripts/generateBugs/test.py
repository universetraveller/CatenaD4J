import time
import threading
import util
import timeout_decorator
run_timeout = 1
class a:
    def __init__(self, b):
        self.b=b
    def p(self):
        self.b = 1

    @timeout_decorator.timeout(run_timeout)
    def do_sth(self):
        ti = time.time()
        while time.time() - ti < 3:
            continue
        print('after')
qq = a(1)
print(time.time())
qq.do_sth()
print(time.time())
exit()
a = util.runCommand(['defects4j', 'test', '-w', './working/data/Chart_15'], timeout=0.5)
print(a)
