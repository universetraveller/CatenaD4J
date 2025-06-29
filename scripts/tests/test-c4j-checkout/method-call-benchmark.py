import time
def test(f, v, n):
    a = 0
    for i in range(n):
        start = time.perf_counter_ns()
        f(v)
        end = time.perf_counter_ns()
        a += end - start
    print(a/n)


def compute(a):
    return a ** 3

def compute1(b):
    return compute(b)

def compute2(b):
    return compute1(b)

test(compute, 100, 100000)
test(compute1, 100, 100000)
test(compute2, 100, 100000)
