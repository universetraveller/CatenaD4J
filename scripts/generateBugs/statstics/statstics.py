import glob
import json
data = {}
alert = print
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
def parse_all_statstic1():
    assert not get_data()
    locale = open('./statstics1.csv', 'a')
    locale.write('bug_id, status, num_new_bugs, hunks_new_bugs\n')
    isolated = 0
    divisible = 0
    indivisible = 0
    for name in data:
        tp = data[name]
        log = tp[0]
        nbn = new_bugs_num(log)
        if nbn == -1:
            locale.write(f'{name}, {NO_DATA}, 0, NONE\n')
            alert(f'{name} no ending')
        elif nbn == 0:
            locale.write(f'{name}, {INVALID_DIVISIBLE_BUG}, {NO_DATA}, NONE\n')
            divisible += 1
        else:
            bgdict = tp[1]
            bl = new_bugs_from_bgdict(bgdict)
            if not len(bl):
                alert(f'Empty new BUGS at {name}')
                continue
            if nbn == 1:
                if is_all('1', bl[0]):
                    locale.write(f'{name}, {INDIVISIBLE}, 0, {len(bl[0])}\n')
                    indivisible += 1
                else:
                    locale.write(f'{name}, {VALID_DIVISIBLE_BUG}, 1, {len(bl[0])}\n')
                    divisible += 1
                    isolated += 1
            else:
                hs = ''
                for i in bl:
                    hs += ('{}.'.format(i.count('1')))
                locale.write(f'{name}, {VALID_DIVISIBLE_BUG}, {len(bl)}, {hs}\n')
                divisible += 1
                isolated += len(bl)
    locale.write(f'STATSTICS, Divisible={divisible}, Indivisible={indivisible}, Isolated={isolated}\n')
    locale.close()
    print('statstics1 ends')
    return 0
def parse_all_statstic1_name(pname):
    locale = open(f'./statstics1_{pname}.csv', 'a')
    locale.write('bug_id, status, num_new_bugs, hunks_new_bugs\n')
    isolated = 0
    divisible = 0
    indivisible = 0
    for name in data:
        if not pname in name:
            continue
        tp = data[name]
        name = name.replace(pname+'_', '')
        log = tp[0]
        nbn = new_bugs_num(log)
        if nbn == -1:
            locale.write(f'{name}, {NO_DATA}, 0, NONE\n')
            alert(f'{name} no ending')
        elif nbn == 0:
            locale.write(f'{name}, {INVALID_DIVISIBLE_BUG}, {NO_DATA}, NONE\n')
            divisible += 1
        else:
            bgdict = tp[1]
            bl = new_bugs_from_bgdict(bgdict)
            if not len(bl):
                alert(f'Empty new BUGS at {name}')
                continue
            if nbn == 1:
                if is_all('1', bl[0]):
                    locale.write(f'{name}, {INDIVISIBLE}, 0, {len(bl[0])}\n')
                    indivisible += 1
                else:
                    locale.write(f'{name}, {VALID_DIVISIBLE_BUG}, 1, {len(bl[0])}\n')
                    divisible += 1
                    isolated += 1
            else:
                hs = ''
                for i in bl:
                    hs += ('{}.'.format(i.count('1')))
                locale.write(f'{name}, {VALID_DIVISIBLE_BUG}, {len(bl)}, {hs}\n')
                divisible += 1
                isolated += len(bl)
    locale.write(f'STATSTICS, Divisible={divisible}, Indivisible={indivisible}, Isolated={isolated}\n')
    locale.close()
    print(f'statstics1_{pname} ends')
    return 0
def parse_all_statstic1_all_proj():
    assert not get_data()
    projs = ['Chart', 'Lang', 'Math', 'Time', 'Closure', 'Mockito']
    for i in projs:
        assert not parse_all_statstic1_name(i)
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
def parse_all_statstic2():
    locale = open(f'./statstics2.csv', 'a')
    locale.write('bug_id, category, num_divided_into_single_hunk, num_divided_into_multi_hunk, hunks_multi_hunk\n')
    isolated = 0
    divisible = 0
    indivisible = 0
    into_single=0
    for name in data:
        tp = data[name]
        log = tp[0]
        nbn = new_bugs_num(log)
        if nbn == -1:
            locale.write(f'{name}, {NO_DATA}, NONE, NONE, NONE\n')
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
                locale.write(f'{name}, {INDIVISIBLE}, 0, 0, {len(bl[0])}\n') 
                indivisible += 1
            single = 0
            multi = []
            for fix in bl:
                if fix.count('1') == 1:
                    single += 1
                elif fix.count('1') > 1 and not is_all('1', fix):
                    multi.append(fix)
                else:
                    print(f'invalid arg {fix}')
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
            locale.write(f'{name}, {stat}, {single}, {len(multi)}, {hs}\n')
    locale.write(f'STATSTICS, Divisible={divisible}, Indivisible={indivisible}, Isolated={isolated}, Divide_into_single={into_single}\n')
    locale.close()
    print(f'statstics2 ends')
    return 0
def parse_all_statstic2_name(name):
    locale = open(f'./statstics2_{pname}.csv', 'a')
    locale.write('bug_id, category, num_divided_into_single_hunk, num_divided_into_multi_hunk, hunks_multi_hunk\n')
    isolated = 0
    divisible = 0
    indivisible = 0
    into_single=0
    for name in data:
        if not pname in name:
            continue
        tp = data[name]
        name = name.replace(pname+'_', '')
        log = tp[0]
        nbn = new_bugs_num(log)
        if nbn == -1:
            locale.write(f'{name}, {NO_DATA}, NONE, NONE, NONE\n')
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
                locale.write(f'{name}, {INDIVISIBLE}, 0, 0, {len(bl[0])}\n') 
                indivisible += 1
            single = 0
            multi = []
            for fix in bl:
                if fix.count('1') == 1:
                    single += 1
                elif fix.count('1') > 1 and not is_all('1', fix):
                    multi.append(fix)
                else:
                    print(f'invalid arg {fix}')
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
            locale.write(f'{name}, {stat}, {single}, {len(multi)}, {hs}\n')
    locale.write(f'STATSTICS, Divisible={divisible}, Indivisible={indivisible}, Isolated={isolated}, Divide_into_single={into_single}\n')
    locale.close()
    print(f'statstics2_{pname} ends')
    return 0
def parse_all_statstic2_all_proj():
    assert not get_data()
    projs = ['Chart', 'Lang', 'Math', 'Time', 'Closure', 'Mockito']
    for i in projs:
        assert not parse_all_statstic1_name(i)
if __name__ == '__main__':
    parse_max_timeout()
