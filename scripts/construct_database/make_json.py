import os
import json
import sys

path2export =  sys.argv[1]
path2output = sys.argv[2]

root = {}
for proj in os.listdir(path2export):
    path2proj = os.path.join(path2export, proj)
    if not os.path.isdir(path2proj):
        continue
    root[proj] = {}
    for id in os.listdir(path2proj):
        path2id = os.path.join(path2proj, id)
        root[proj][id] = {}
        for prop in os.listdir(path2id):
            with open(os.path.join(path2id, prop)) as f:
                _prop = f.read().splitlines()
                root[proj][id][prop] = _prop[0] \
                                        if prop.startswith('cp') or \
                                            prop.startswith('dir') \
                                        else _prop

with open(path2output, 'w') as f:
    json.dump(root, f, indent=2)
