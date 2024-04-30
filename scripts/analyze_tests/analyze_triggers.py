import json
import tqdm
import sys
with open(sys.argv[1], 'r') as f:
    wait = f.read().splitlines()
d4j = '/root/defects4j/framework/projects/'
if len(sys.argv) > 2:
    d4j = f'{sys.argv[2]}/framework/projects/'
log = open('./names/tryTrigger', 'w')
first_level = set()
def tryTrigger(proj, bid):
    with open(d4j+proj+'/trigger_tests/'+bid, 'r') as tgt:
        tgt = tgt.read().splitlines()
    bugid = '{}_{}'.format(proj, bid)
    log.write('--------------------------\n')
    log.write(bugid+'\n')
    finish = False
    all_name = []
    for i in tgt:
        if i.startswith('---'):
            finish = False
            test_name = i.strip('---').strip().replace('::', '.')
        if not i.strip().startswith('at'):
            if 'exception' in i or 'Exception' in i or i.strip().startswith('java.'):
                finish = True
            continue
        if finish:
            continue
        if 'at '+test_name in i or 'sun.reflect.NativeMethodAccessorImpl.invoke' in i:
            log.write(i+'\n')
            finish = True
            if 'sun.reflect.NativeMethodAccessorImpl.invoke' in i:
                all_name = all_name[:-1]
            fl_c = all_name[-1].strip().strip('at').strip()
            first_level.add(fl_c[:fl_c.find('(')])
        else:
            log.write('--> ' + i.strip().strip('at')+'\n')
            all_name.append(i)
    for i in range(len(all_name)):
        name = all_name[i]
        name = name.strip().strip('at')
        all_name[i] = name[:name.find('(')]
    all_name_bak = all_name.copy()
    all_name = []
    for i in all_name_bak:
        if not '$' in i:
            all_name.append(i)
    log.write('--------------------------\n')
    for i in all_name:
        log.write(i+'\n')
    return all_name
def tryTrigger1(proj, bid):
    with open(d4j+proj+'/trigger_tests/'+bid, 'r') as tgt:
        tgt = tgt.read().splitlines()
    finish = False
    all_name = []
    for i in tgt:
        if i.startswith('---'):
            finish = False
            test_name = i.strip('---').strip().replace('::', '.')
        if not i.strip().startswith('at'):
            if 'Exception' in i or 'exception' in i:
                finish = True
            continue
        if finish:
            continue
        if 'at '+test_name in i or 'sun.reflect.NativeMethodAccessorImpl.invoke' in i:
            all_name.append(i)
            finish = True
        else:
            all_name.append('--> ' + i.strip().strip('at'))
    for i in range(3):
        print('*****************************')
    print(proj+'_'+bid)
    for i in all_name:
        print(i)
    check = input()
    if check == 'y':
        print('accept')
        for i in range(len(all_name)):
            name = all_name[i]
            if not name.startswith('-->'):
                continue
            name = name.strip('-->').strip()
            all_name[i] = name[:name.find('(')]
    elif check == 'n':
        print('wait for checking')
        all_name = ['checkFailed {}_{}'.format(proj, bid)]
    else:
        print('abort')
        all_name = []
    return all_name
def startswithOneOf(s, l):
    for i in l:
        if s.startswith(i):
            return True
    return False
res = []
for i in tqdm.tqdm(wait):
    i = i.split(':')[0].split('_')
    if i[0] == 'Time' and i[1] == '21':
        continue
    res.extend(tryTrigger(i[0], i[1]))
res = set(res)
pac = (
        'org.apache.tools',
        'java.',
        'sun.reflect',
        '$java'
        )
qualifiers = set()
members = set()
fl_q = set()
fl_m = set()
def parse(name):
    name = name.split('.')
    if len(name) == 1:
        return '', name[0]
    else:
        return name[-2], name[-1]
for i in res:
    if not startswithOneOf(i.strip(), pac):
        _q, _m = parse(i)
        qualifiers.add(_q)
        members.add(_m)
        print(i)
print('first level:')
for i in first_level:
    _q, _m = parse(i)
    fl_q.add(_q)
    fl_m.add(_m)
    print(i)
log.write('call:\n')
for i in res:
    if not startswithOneOf(i.strip(), pac):
        _q, _m = parse(i)
        log.write('{}.{}\n'.format(_q, _m))

log.write('\n\nfl call:\n')
for i in first_level:
    _q, _m = parse(i)
    log.write('{}.{}\n'.format(_q, _m))
log.write('\n\nqualifiers:\n')
for i in qualifiers:
    log.write('{}\n'.format(i))
log.write('\n\nmembers:\n')
for i in members:
    log.write('{}\n'.format(i))
log.write('\n\nfl_q:\n')
for i in fl_q:
    log.write('{}\n'.format(i))
log.write('\n\nfl_m:\n')
for i in fl_m:
    log.write('{}\n'.format(i))
