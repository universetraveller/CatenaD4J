import glob
import json
data = {}
alert = print
patches_ci = '../../parsePatches/patches_ci/'
DEFINE_CI = 1
def new_bugs_num(log_list):
    last_line = log_list[-1]
    if not last_line.startswith('Find'):
        num = 0
        for i in log_list:
            if 'select new bug' in i:
                num += 1
        if not num == 0:
            return num
        return -1
    return int(last_line.replace('Find', '').replace('new bugs', ''))
def new_bugs_from_bgdict(bgdict):
    res = []
    for name in bgdict:
        if name in ('original', 'method'):
            continue
        res.append(name)
    return res
def is_all(p, l):
    for i in l:
        if not i == p:
            return False
    return True
def get_data():
    paths = glob.glob('../working/*/log')
    for i in paths:
        name = i.replace('../working/', '').replace('/log', '')
        if name == 'Time_21':
            continue
        with open(i, 'r') as f:
            f = f.read().splitlines()
        if new_bugs_num(f) > -1:
            with open(i.replace('/log', '/newBugs.json'), 'r') as f1:
                bgdict = json.load(f1)
        else:
            bgdict = {}
        if len(f) == 0:
            alert(f"ALERT length 0 file at {name}")
        else:
            data[name] = (f, bgdict)
    return 0
INDIVISIBLE = 'INDIVISIBLE'
INVALID_DIVISIBLE_BUG = 'INVALID_DIVISIBLE_BUG'
VALID_DIVISIBLE_BUG = 'VALID_DIVISIBLE_BUG'
NO_DATA = 'NO_DATA'
def parse_max_timeout():
    assert not get_data()
    time_list = []
    for i in data:
        f = data[i][0]
        for j in f:
            if 'used time: Finished in' in j:
                time_list.append(float(j.replace('used time: Finished in', '').replace('seconds', '')))
                print(time_list[-1])
    time_list.sort()
    max_5 = time_list[-5:]
    print('max 5:')
    for i in max_5[::-1]:
        print(i)
    print(f'min: {time_list[0]}')
    print(f'avg: {sum(time_list)/len(time_list)}')
def do_ci(s):
    return s if DEFINE_CI else ''
def num_ci(pci):
    return ', {}, {}'.format(pci['num_of_hunks'], pci['num_of_hunks_ci'])
def head_ci():
    return do_ci(', hunks_multi_hunk_ci, num_of_hunks, num_of_hunks_ci')
def ne_ci(pci):
    return do_ci(', NONE{}'.format(num_ci(pci)))
def match_pci(pat, pci):
    pci_c = 0
    for i in range(len(pat)):
        if pat[i] == '1' and not 'is_extra_hunk' in pci[f'{i}']:
            pci_c += 1
    return pci_c
def indiv_ci(pat, pci):
    return do_ci(', {}{}'.format(match_pci(pat, pci), num_ci(pci)))
def div_ci(multi, pci):
    s = ', /'
    for fix in multi:
        s += f'{match_pci(fix, pci)}/'
    s += num_ci(pci)
    return do_ci(s)
def tail_ci(th, thci):
    return do_ci(f', Hunks_total={th}, Hunks_total_ci={thci}')
def parse_all_statstic2():
    assert not get_data()
    locale = open(f'./statstics2.csv', 'a')
    locale.write(f'bug_id, category, num_divided_into_single_hunk, num_divided_into_multi_hunk, hunks_multi_hunk{head_ci()}\n')
    isolated = 0
    divisible = 0
    indivisible = 0
    into_single=0
    timeout=0
    total_hunks=0
    total_hunks_ci=0
    for name in data:
        tp = data[name]
        log = tp[0]
        nbn = new_bugs_num(log)
        name_arr = name.split('_')
        with open(f'{patches_ci}{name_arr[0]}/{name_arr[1]}.json', 'r') as f:
            pci = json.load(f)
        total_hunks += pci['num_of_hunks']
        total_hunks_ci += pci['num_of_hunks_ci']
        if not nbn:
            print('WARNNING: nbn==0')
        if nbn == -1:
            locale.write(f'{name}, {NO_DATA}, NONE, NONE, NONE{ne_ci(pci)}\n')
            timeout+=1
            alert(f'{name} no ending')
        else:
            bgdict = tp[1]
            bl = new_bugs_from_bgdict(bgdict)
            if not len(bl):
                alert(f'Empty new BUGS at {name}')
                if not -1 == nbn:
                    alert(f'Two bugs num not equals {name}')
                continue
            if not len(bl) == nbn:
                alert(f'Two bugs num not equals {name}')
            if len(bl) == 1 and is_all('1', bl[0]):
                locale.write(f'{name}, {INDIVISIBLE}, 0, 0, {len(bl[0])}{indiv_ci(bl[0], pci)}\n') 
                indivisible += 1
                continue
            single = 0
            multi = []
            for fix in bl:
                if fix.count('1') == 1:
                    single += 1
                else:
                    assert fix.count('1') > 1
                    multi.append(fix)
            divisible += 1
            isolated += len(multi)
            into_single += single
            if len(multi) == 0:
                stat = 'INVALID_DIVISIBLE_BUG'
            elif single == 0:
                stat = 'VALID_DIVISIBLE_BUG'
            else:
                stat = 'MIXED_DIVISIBLE_BUG'
            hs = '/'
            for i in bl:
                if i.count('1') > 1:
                    hs+='{}/'.format(i.count('1'))
            locale.write(f'{name}, {stat}, {single}, {len(multi)}, {hs}{div_ci(multi, pci)}\n')
    locale.write(f'STATSTICS, No_data={timeout}, Divisible={divisible}, Indivisible={indivisible}, Isolated={isolated}, Single_divided={into_single}{tail_ci(total_hunks, total_hunks_ci)}\n')
    locale.close()
    print(f'statstics2 ends')
    return 0
def parse_all_statstic2_name(pname):
    locale = open(f'./statstics2_{pname}.csv', 'a')
    locale.write('bug_id, category, num_divided_into_single_hunk, num_divided_into_multi_hunk, hunks_multi_hunk\n')
    isolated = 0
    divisible = 0
    indivisible = 0
    into_single=0
    timeout=0
    total_hunks=0
    total_hunks_ci=0
    for name in data:
        if not pname in name:
            continue
        tp = data[name]
        name_arr = name.split('_')
        with open(f'{patches_ci}{name_arr[0]}/{name_arr[1]}.json', 'r') as f:
            pci = json.load(f)
        total_hunks += pci['num_of_hunks']
        total_hunks_ci += pci['num_of_hunks_ci']
        name = name.replace(pname+'_', '')
        log = tp[0]
        nbn = new_bugs_num(log)
        if nbn == -1:
            locale.write(f'{name}, {NO_DATA}, NONE, NONE, NONE{ne_ci(pci)}\n')
            timeout+=1
            alert(f'{name} no ending')
        else:
            bgdict = tp[1]
            bl = new_bugs_from_bgdict(bgdict)
            if not len(bl):
                alert(f'Empty new BUGS at {pname}_{name}')
                if not -1 == nbn:
                    alert(f'Two bugs num not equals {pname}_{name}')
                continue
            if not len(bl) == nbn:
                alert(f'Two bugs num not equals {pname}_{name}')
            if len(bl) == 1 and is_all('1', bl[0]):
                locale.write(f'{name}, {INDIVISIBLE}, 0, 0, {len(bl[0])}{indiv_ci(bl[0], pci)}\n') 
                indivisible += 1
                continue
            single = 0
            multi = []
            for fix in bl:
                if fix.count('1') == 1:
                    single += 1
                else:
                    assert fix.count('1') > 1
                    multi.append(fix)
            divisible += 1
            isolated += len(multi)
            into_single += single
            if len(multi) == 0:
                stat = 'INVALID_DIVISIBLE_BUG'
            elif single == 0:
                stat = 'VALID_DIVISIBLE_BUG'
            else:
                stat = 'MIXED_DIVISIBLE_BUG'
            hs = '/'
            for i in bl:
                if i.count('1') > 1:
                    hs+='{}/'.format(i.count('1'))
            locale.write(f'{name}, {stat}, {single}, {len(multi)}, {hs}{div_ci(multi, pci)}\n')
    locale.write(f'STATSTICS, No_data={timeout}, Divisible={divisible}, Indivisible={indivisible}, Isolated={isolated}, Single_divided={into_single}{tail_ci(total_hunks, total_hunks_ci)}\n')
    locale.close()
    print(f'statstics2_{pname} ends')
    return 0
def parse_all_statstic2_all_proj():
    assert not get_data()
    projs = ['Chart', 'Lang', 'Math', 'Time', 'Closure', 'Mockito']
    for i in projs:
        assert not parse_all_statstic2_name(i)
def print_short_logs(num_of_line, spec=''):
    assert not get_data()
    for name in data:
        if spec and spec != name:
            continue
        log = data[name][0]
        if spec:
            print(log[-num_of_line:])
        if len(log) < num_of_line:
            print(name)
    print(len(data))
def print_no_ending_bugs():
    assert not get_data()
    unk = 0
    div = 0
    for name in data:
        tp = data[name]
        log = tp[0]
        nbn = new_bugs_num(log)
        if not nbn:
            print('WARNNING: nbn==0')
        if nbn == -1:
            print(f'{name}: Timeout / Unknown')
            unk += 1
        else:
            bgdict = tp[1]
            bl = new_bugs_from_bgdict(bgdict)
            if not len(bl):
                alert(f'Empty new BUGS at {name}')
                if not -1 == nbn:
                    alert(f'Two bugs num not equals {name}')
                continue
            if not len(bl) == nbn:
                alert(f'Two bugs num not equals {name}')
            if len(bl) == 1 and is_all('1', bl[0]):
                continue
            if 'TimeoutError' in '\n'.join(log[-2:]):
                print(f'{name}: Timeout / Divisible')
                div += 1
    print(f'unk: {unk}, div: {div}')
if __name__ == '__main__':
    parse_all_statstic2()
    parse_all_statstic2_all_proj()
