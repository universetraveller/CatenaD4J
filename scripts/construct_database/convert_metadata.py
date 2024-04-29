import json
import os
import tqdm
import sys
with open(sys.argv[1], 'r') as f:
    waitlist = f.read().splitlines()
props = ['classes.modified', 'classes.relevant', 'cp.compile', 'cp.test', 'dir.bin.classes', 'dir.bin.tests',  'dir.src.classes', 'dir.src.tests', 'tests.all', 'tests.relevant', 'tests.trigger']
root = {}
bench = os.path.abspath(sys.argv[2])
if not bench.endswith('/'):
    bench += '/'
d4j = os.path.abspath(sys.argv[3])
for i in waitlist:
    i = i.split(':')[0]
    _bench = bench + i
    if i == 'Time_21':
        continue
    root[i] = {}
    path = './d4j_export/{}/'.format(i)
    for j in props:
        filepath = path + j
        with open(filepath, 'r') as f:
            f = f.read().splitlines()
        if j.startswith('tests') or j.startswith('classes'):
            root[i][j] =  f
        else:
            assert len(f) == 1
            if j.startswith('cp'):
                f[0] = f[0].replace(d4j, '<PathToD4j>')
                f[0] = f[0].replace(_bench, '<PathToBuggyDir>')
            root[i][j] = f[0]
with open('./d4j_export/database.json', 'w') as f:
    f.write(json.dumps(root, indent=4))
