import time
def test(f, n, *args, **kwargs):
    a = 0
    for i in range(n):
        start = time.perf_counter_ns()
        f(*args, **kwargs)
        end = time.perf_counter_ns()
        a += end - start
    return a, a/n

def test1(f, n, *args, **kwargs):
    print(f'Average elapsed time: {test(f, n, *args, **kwargs)[1]} ns')
