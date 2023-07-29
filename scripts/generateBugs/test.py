import time
import threading
import util
import timeout_decorator
import joblib
@timeout_decorator.timeout(0.2)
def  test():
    time.sleep(1)
    print(1, end='')
def test1():
    try:
        test()
    except:
        print(2, end='')
joblib.Parallel(n_jobs=15)(joblib.delayed(test1)()for i in range(50))
exit()
a = util.runCommand(['defects4j', 'test', '-w', './working/data/Chart_15'], timeout=0.5)
print(a)
