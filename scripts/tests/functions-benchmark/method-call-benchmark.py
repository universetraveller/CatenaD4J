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

with open('/tmp/bugs_static/Chart_1/source/org/jfree/chart/plot/PiePlot3D.java') as f:
    a = f.read().splitlines()

def lp1(a):
    for i in a:
        str(i)

s = len(a)
def lp2(a):
    for i in a[0:s]:
        str(i)

#test(lp1, a, 100000)
#test(lp2, a, 100000)

def lc1(_original):
    content = []
    for line in _original:
        content.append([[], line, []])

def lc2(_original):
    content = [[[], line, []] for line in _original]

def lc3(_original):
    content = list(map(lambda line: [[], line, []], _original))


def sc1(a):
    return '{}{}{}'.format(a[0], a[1], a[2])

def sc2(a):
    return a[0] + a[1] + a[2]

def sc3(a):
    return ''.join((a[0], a[1], a[2]))

#test(compute, 100, 100000)
#test(compute1, 100, 100000)
#test(compute2, 100, 100000)
#test(lc1, a, 100000)
#test(lc2, a, 100000)
#test(lc3, a, 100000)
#a = (a[0], a[1], a[2])
#test(sc1, a, 100000)
#test(sc2, a, 100000)
#test(sc3, a, 100000)
