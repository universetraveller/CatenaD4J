import re
class A:
    pass

a=A()
a.b = A()
a.b.c = '12'

import time
n = 1000000
start = time.perf_counter_ns()
for i in range(n):
    s = a.b.c
end = time.perf_counter_ns()
print((end - start) / n)

start = time.perf_counter_ns()
for i in range(n):
    s = '1' + '2'
end = time.perf_counter_ns()
print((end - start) / n)
