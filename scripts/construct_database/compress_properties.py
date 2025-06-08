import os
import sys
import compress
import d4j_all_bugs
import json
import gzip
import pickle

path2export =  sys.argv[1]
path2output = sys.argv[2]
approach = 'index'
if len(sys.argv) > 3:
    approach = sys.argv[3]
all_in_one = True
to_zip = True
if len(sys.argv) > 4:
    features = sys.argv[4].split(',')
    if 'create_index' in features:
        all_in_one = False
    if 'json' in features:
        to_zip = False

def _traverse():
    for proj in os.listdir(path2export):
        path2proj = os.path.join(path2export, proj)
        if not os.path.isdir(path2proj):
            continue
        for id in os.listdir(path2proj):
            path2id = os.path.join(path2proj, id)
            for prop in os.listdir(path2id):
                with open(os.path.join(path2id, prop)) as f:
                    _prop = f.read().splitlines()
                if prop.startswith('classes') or prop.startswith('tests'):
                    if prop == 'tests.trigger':
                        _prop = list(map(lambda x:x.replace('::', '.', 1), _prop))
                    _prop = list(map(lambda x:x.split('.'), _prop))
                elif prop.startswith('cp'):
                    _prop = _prop[0].split(':')
                    _prop = list(map(lambda x:x.split('/'), _prop))
                    # Patch to ensure order
                    for i in range(len(_prop)):
                        _prop[i].append(-i-1)
                        #_prop[i].append(str(i))
                        #_prop[i] = [i] + _prop[i]
                elif prop.startswith('dir'):
                    _prop = [_prop[0].split('/')]
                yield proj, id, prop, _prop

def traverse(get_id: lambda x:x):
    indexes = {}
    for proj in d4j_all_bugs.all_projs:
        indexes[get_id(proj, True)] = {}
    #    indexes[d4j_all_bugs.mapping[proj]] = {}
    for prop in d4j_all_bugs.d4j_props:
        get_id(prop, True)
    for proj, id, pn, p in _traverse():
        id = int(id)
        iproj = get_id(proj)
        #iproj = d4j_all_bugs.mapping[proj]
        if not id in indexes[iproj]:
            indexes[iproj][id] = {}
        root = compress.build_from_ll(p)
        iprop = get_id(pn)
        #iprop = d4j_all_bugs.mapping[pn]
        indexes[iproj][id][iprop] = root.to_tree(convert=get_id)
    return indexes

def dump(indexes):
    if not to_zip:
        with open(os.path.join(path2output, 'properties.json'), 'w') as f:
            json.dump(indexes, f)
    else:
        with open(os.path.join(path2output, 'properties.pkl.gz'), 'wb') as f:
            f.write(gzip.compress(pickle.dumps(indexes)))

if approach == 'index':
    registry = compress.Registry()
    indexes = traverse(registry.get_id)
    if all_in_one:
        indexes['index'] = registry.get_map()
    else:
        with open(os.path.join(path2output, 'index.json'), 'w') as f:
            json.dump(registry.get_map(), f)
    dump(indexes)

elif approach == 'huffman-token':
    tokens = []
    tokens.extend(d4j_all_bugs.all_projs)
    tokens.extend(d4j_all_bugs.d4j_props)
    for proj, id, pn, p in _traverse():
        for l in p:
            tokens.extend(l)
    huffman = compress.StaticHuffmanRegistry(tokens)
    tree, codes = huffman.dump_tree()
    indexes = traverse(lambda x:codes.get(x)[0])
    if all_in_one:
        indexes['tree'] = tree
    else:
        with open(os.path.join(path2output, 'tree.json'), 'w') as f:
            json.dump(tree, f)
    dump(indexes)

elif approach == 'huffman-char':
    tokens = []
    for proj in d4j_all_bugs.all_projs:
        tokens.extend(proj)
    for prop in d4j_all_bugs.d4j_props:
        tokens.extend(prop)
    for proj, id, pn, p in _traverse():
        for l in p:
            for identifier in l:
                tokens.extend(identifier)
    huffman = compress.StaticHuffmanRegistry(tokens)
    tree, codes = huffman.dump_tree()
    def get_id(x):
        id = 0b0
        for i in x:
            code = codes.get(i)
            id <<= code[1]
            id += code[0]
        return id

    indexes = traverse(get_id)
    if all_in_one:
        indexes['tree'] = tree
    else:
        with open(os.path.join(path2output, 'tree.json'), 'w') as f:
            json.dump(tree, f)
    dump(indexes)

