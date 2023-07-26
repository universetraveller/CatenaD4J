import glob
import json
data = {}
alert = print
def new_bugs_num(log_list):
    last_line = log_list[-1]
    if not last_line.startswith('Find'):
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
    paths = glob.glob('./working/*/log')
    for i in paths:
        name = i.replace('./working/', '').replace('/log', '')
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
if __name__ == '__main__':
    parse_all_statstic1()
