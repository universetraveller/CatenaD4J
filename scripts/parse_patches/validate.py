import glob
import os
import sys
import d4jpath
root = d4jpath.d4j_home
projs = d4jpath.all_projs
for proj in projs:
    paths = glob.glob('{}/framework/projects/{}/patches/*.src.patch'.format(root, proj))
    for i in paths:
        with open(i, encoding='latin-1') as f:
            f = f.read().splitlines()
        idx = i[i.rfind('/') + 1:]
        idx = idx[:idx.find('.')]
        c = False
        d = False
        for j in f:
            if '===============================================================' in j:
                c = True
            if 'diff --git' in j:
                d = True
        if not d or c:
            print(proj, idx)
