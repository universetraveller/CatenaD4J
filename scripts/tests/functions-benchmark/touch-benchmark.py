from pathlib import Path
import time
d = Path('./touches')
d.mkdir(exist_ok=True)
n = 100000
print('touch')
#import os
start = time.perf_counter_ns()
for i in range(n):
    p = d / f'{i}.touched'
    #os.system(f'touch {str(p)}')
    p.touch()
end = time.perf_counter_ns()
print('total:', end - start, 'ns')
print('average:', (end - start) / n, 'ns')

#print('---')
#
#print('pure string')
#s = ''
#start = time.perf_counter_ns()
#for i in range(n):
#    p = d / f'{i}.touched'
#    s += str(p)
#end = time.perf_counter_ns()
#print('total:', end - start, 'ns')
#print('average:', (end - start) / n, 'ns')
