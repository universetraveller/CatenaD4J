import glob
import os
import json
def get_all_works():
    works = []
    paths = glob.glob('./working/*')
    for p in paths:
        name = p.replace('./working/', '')
        works.append((name, p))
    return works
def check_log(p):
    with open(p+'/log', 'r') as f:
        f = f.read().splitlines()
    if not f[-1].startswith('Find'):
        return 0
    return int(f[-1].replace('Find', '').replace('new bugs', ''))
def moreCheck(name, l):
    c = 0
    s = ''
    for i in l:
        if name+'()' in i:
            s = i
            c+=1
    assert c == 1
    return s
_db = json.load(open('./database.json', 'r'))
def getClz(fn, proj, bid):
    _dir = _db[f'{proj}_{bid}']['dir.src.classes']
    return fn.replace(f'{_dir}/', '').replace('.java', '').replace('/', '.')
def main():
    if not os.path.exists('./export'):
        os.makedirs('./export')
    tasks = get_all_works()
    for t in tasks:
        name = t[0]
        if name == 'data':
            continue
        proj = name.split('_')
        bid = proj[1]
        proj = proj[0]
        num = check_log(t[1])
        if num:
            print('{}:{}'.format(name, num))
            projd = './export/{}/{}'.format(proj, bid)
            if not os.path.exists(projd):
                os.makedirs(projd)
            if not os.path.exists('./export/{}/bugs-registry.csv'.format(proj)):
                with open('./export/{}/bugs-registry.csv'.format(proj), 'a') as ab:
                    ab.write('bid,cid,loader\n')
            nb = json.load(open(t[1]+'/newBugs.json', 'r'))
            collection = []
            for i in nb:
                if i == 'original':
                    ori = nb[i]
                elif i == 'method':
                    met = nb[i]
                else:
                    collection.append((i, nb[i]))
            assert len(collection) == num
            for i in range(1, num+1):
                with open('./export/{}/bugs-registry.csv'.format(proj), 'a') as ab:
                    ab.write('{},{},default\n'.format(bid, i))
                node = {}
                one = collection[i-1]
                #node['trigger_tests'] = one[1]['failing_tests']
                clz = set()
                with open('./export/{}/{}/{}.tests.trigger'.format(proj, bid, i), 'w') as wtg:
                    for otg in one[1]['failing_tests']:
                        wtg.write(f'{otg}\n')
                node['patch'] = []
                __ed = {}
                for idx, ch in enumerate(one[0]):
                    if ch == '1':
                        node['patch'].append(ori[str(idx)])
                        clz.add(getClz(ori[str(idx)]['file_name'], proj, bid))
                for ft in one[1]['failing_tests']:
                    if not '$catena_' in ft and not '_catena_' in ft:
                        pass
                    else:
                        _s_pattern = '$catena_'
                        if not _s_pattern in ft and '_catena_' in ft:
                            _s_pattern = '_catena_'
                        arr = ft.split(_s_pattern)
                        if not arr[0] in met:
                            print(f'skip {ft} in {proj}_{bid}')
                            continue
                        assert len(arr) == 2
                        if not arr[0] in __ed:
                            __ed[arr[0]] = {}
                            __ed[arr[0]]['begin_line_no'] = met[arr[0]]['begin_line_no']
                            __ed[arr[0]]['end_line_no'] = met[arr[0]]['end_line_no']
                            __ed[arr[0]]['file_path'] = met[arr[0]]['file_path']
                            __ed[arr[0]]['to'] = []
                        new = met[arr[0]]['func'][str(arr[1])]
                        assert ft.split('::')[1] in new
                        assert new.strip() == moreCheck(ft.split('::')[1], met[arr[0]]['splited']).strip()
                        __ed[arr[0]]['to'].append(new)
                #node['edit'] = __ed
                with open('./export/{}/{}/{}.classes.modified'.format(proj, bid, i), 'w') as w:
                    for oclz in clz:
                        w.write(f'{oclz}\n')
                eds = json.dumps(__ed, indent=4)
                with open('./export/{}/{}/{}.test.patch'.format(proj, bid, i), 'w') as w:
                    w.write(eds)
                s = json.dumps(node, indent=4)
                with open('./export/{}/{}/{}.src.patch'.format(proj, bid, i), 'w') as w:
                    w.write(s)
main()
