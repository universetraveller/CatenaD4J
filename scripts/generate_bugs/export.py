import glob
import os
import json
import log_parser
import sys
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
        num = 0
        for i in f:
            if 'select new bug' in i:
                num += 1
        return num
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
def lst_in_use(lst):
    if len(lst) == 0:
        return ['']
    return lst
_db = json.load(open('./database.json', 'r'))
def getClz(fn, proj, bid):
    _dir = _db[f'{proj}_{bid}']['dir.src.classes']
    return fn.replace(f'{_dir}/', '').replace('.java', '').replace('/', '.')
arg_prefix = '-'
_args_alias  = {
        'm' : 'mode'
        }
def parse_args(args):
    if not args:
        raise ValueError('len(args) == 0')
    idx = -1
    name = None
    value = None
    while idx < len(args):
        idx += 1
        arg = args[idx]
        if arg.startswith(arg_prefix*2):
            if not name is None:
                raise ValueError('name is not None')
            name = arg[2:]
        elif arg.startswith(arg_prefix*1):
            if not name is None:
                raise ValueError('name is not None')
            name = _args_alias[arg[1:]]
        elif not arg.startswith(arg_prefix):
            if not value is None:
                raise ValueError('value is not None')
            if name is None:
                raise ValueError('name is None')
            value = arg
        else:
            if not name is None:
                raise ValueError('invalid')
        if name is None or value is None:
            continue
        else:
            if name == 'mode':
                return value
            name = None
            value = None
def test_mode():
    print(parse_args(sys.argv[1:]))
def _skip_0(col, mode):
    if len(col) > 1 or mode == 'all':
        return False
    if 'skip_indivisible' in mode.split(','):
        if '0' in col[0][0]:
            return False
        assert not col[0][0].replace('1', '')
        return True
    return False
def main():
    mode = parse_args(sys.argv[1:])
    print(mode)
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
            proj_root = './export/{}'.format(proj)
            projd = '{}/{}'.format(proj_root, bid)
            if not os.path.exists(proj_root):
                os.makedirs(proj_root)
            if not os.path.exists('./export/{}/bugs-registry.csv'.format(proj)):
                with open('./export/{}/bugs-registry.csv'.format(proj), 'a') as ab:
                    ab.write('bid,cid,loader\n')
            nb = json.load(open(t[1]+'/newBugs.json', 'r'))
            log = log_parser.read_log(f'{t[1]}/log')
            collection = []
            for i in nb:
                if i == 'original':
                    ori = nb[i]
                elif i == 'method':
                    met = nb[i]
                else:
                    collection.append((i, nb[i]))
            assert len(collection) == num
            if _skip_0(collection, mode):
                continue
            if not os.path.exists(projd):
                os.makedirs(projd)
            first_failing = log_parser.get_failing_tests(log, '0'*ori['num_of_hunks'])
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
                # add original should_passed tests
                # for fixing bugs like Chart_2
                for orit in met['failing_tests']:
                    if not orit in met:
                        print(f'skip {orit} in {proj}_{bid} at adding original tests')
                        continue
                    if len(met[orit]['func']) == 0:
                        assert len(met[orit]['splited']) == 0
                        assert not orit in __ed
                        if orit in first_failing and not orit in one[1]['failing_tests']:
                            __ed[orit] = {}
                            __ed[orit]['begin_line_no'] = met[orit]['begin_line_no']
                            __ed[orit]['end_line_no'] = met[orit]['end_line_no']
                            __ed[orit]['file_path'] = met[orit]['file_path']
                            __ed[orit]['to'] = ['']
                    else:
                        ori_lst = []
                        if not orit in __ed:
                            __ed[orit] = {}
                            __ed[orit]['begin_line_no'] = met[orit]['begin_line_no']
                            __ed[orit]['end_line_no'] = met[orit]['end_line_no']
                            __ed[orit]['file_path'] = met[orit]['file_path']
                            __ed[orit]['to'] = []
                        assert len(met[orit]['splited']) == len(met[orit]['func'])
                        for one_new_test in met[orit]['splited']:
                            add = True
                            for check_test in first_failing:
                                if not check_test.startswith(orit):
                                    continue
                                if check_test.split('::')[1]+'()' in one_new_test:
                                    add = False
                                    break
                                elif check_test.split('::')[1] in one_new_test:
                                    __inside_trunk_pos = one_new_test.find("(")
                                    __inside_trunk_check_pre = one_new_test[one_new_test.find(check_test.split('::')[1]):__inside_trunk_pos]
                                    assert __inside_trunk_check_pre.startswith(check_test.split('::')[1])
                                    __inside_trunk_check = __inside_trunk_check_pre.replace(check_test.split("::")[1], '')
                                    for __inside_trunk_check_ch in __inside_trunk_check:
                                        assert not __inside_trunk_check_ch > '9' and not __inside_trunk_check_ch < '0'
                            if add:
                                ori_lst.append(one_new_test)
                        __ed[orit]['to'].extend(ori_lst)
                        __ed[orit]['to'] = lst_in_use(__ed[orit]['to'])
                        assert len(__ed[orit]['to'])
                    '''
                    if not orit in __ed and not orit in one[1]['failing_tests']:
                        __ed[orit] = {}
                        __ed[orit]['begin_line_no'] = met[orit]['begin_line_no']
                        __ed[orit]['end_line_no'] = met[orit]['end_line_no']
                        __ed[orit]['file_path'] = met[orit]['file_path']
                        __ed[orit]['to'] = ['']
                    '''
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
if __name__ == '__main__':
    main()
