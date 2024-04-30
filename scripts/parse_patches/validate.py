import glob
import os
import sys
root = '/root/defects4j/framework/projects/'
if len(sys.argv) > 1:
    root = f'{sys.argv[1]}/framework/projects/'
projs = ['Chart', 'Lang', 'Math', 'Time', 'Closure', 'Mockito']
def assertion(fn):
    s = True
    ret = 'utf-8'
    try:
        a = open(fn, 'r').read()
    except UnicodeDecodeError:
        s = False
        print('Decode error, utf-8, '+i)
        ret = 'latin-1'
    try:
        b = open(fn, 'r', encoding='latin-1').read()
    except UnicodeDecodeError:
        s = False
        print('Decode error, latin-1, '+i)
        return '?'
    if s:
        if not a == b:
            print('Unequal strings of utf-8 and latin-1, '+i)
    return ret
for proj in projs:
    paths = glob.glob('{}{}/patches/*.src.patch'.format(root, proj))
    if not os.path.exists('./patches/{}/'.format(proj)):
        os.makedirs('./patches/{}/'.format(proj))
    for i in paths:
        enc = assertion(i)
        if enc == '?':
            print('skip '+i)
            continue
        idx = i.replace('{}{}/patches/'.format(root, proj), '').replace('.src.patch', '')
        with open(i, encoding=enc) as f:
            f = f.read().splitlines()
        c = False
        d = False
        for j in f:
            if '===============================================================' in j:
                c = True
            if 'diff --git' in j:
                d = True
        if not d or c:
            print('{}_{}'.format(proj, idx))
