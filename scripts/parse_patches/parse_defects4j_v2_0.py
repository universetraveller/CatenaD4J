import parser_defects4j
import glob
import os
import sys
root = '/root/defects4j/framework/projects/'
projs = ['Cli', 'Codec', 'Collections', 'Compress', 'Csv', 'Gson', \
         'JacksonCore', 'JacksonDatabind', 'JacksonXml', 'Jsoup', 'JxPath', \
         'Chart', 'Lang', 'Math', 'Time', 'Closure', 'Mockito']
if len(sys.argv) > 1:
    root = f'{sys.argv[1]}/framework/projects/'
if len(sys.argv) > 2:
    projs = [sys.argv[2]]
hunks_equals_1 = []
hunks_more_than_1 = []
hunks_more_than_5 = []
hunks_from_2_to_5 = []
max_hunk_num = {}
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
    max_hunk_num[proj] = -1
    if not os.path.exists('./patches/{}/'.format(proj)):
        os.makedirs('./patches/{}/'.format(proj))
    for i in paths:
        enc = assertion(i)
        if enc == '?':
            print('skip '+i)
            continue
        idx = i.replace('{}{}/patches/'.format(root, proj), '').replace('.src.patch', '')
        parser = parser_defects4j.Parser(i, encoding=enc)
        try:
            parser.parse()
        except Exception as E:
            print('Error at ' + i)
            print(E)
            continue
        with open('./patches/{}/{}.json'.format(proj, idx), 'w') as w:
            w.write(parser.dump_d4j_patch())
        bid = '{}_{}'.format(proj, idx)
        hunks_num = parser.root['num_of_hunks']
        if hunks_num == 1:
            hunks_equals_1.append(bid)
        if hunks_num > 5:
            hunks_more_than_5.append(bid)
        if hunks_num > 1:
            hunks_more_than_1.append(bid)
        if hunks_num > 1 and hunks_num < 6:
            hunks_from_2_to_5.append(bid)
        if hunks_num > max_hunk_num[proj]:
            max_hunk_num[proj] = hunks_num
def printF(f, obj):
    f.write('{}\n'.format(obj))
with open('./analysis', 'w') as w:
    printF(w, 'Max hunks:')
    for i in max_hunk_num:
        printF(w, '{}: {}'.format(i, max_hunk_num[i]))
    printF(w, '-'*20)
    printF(w, 'Contains only 1 hunk:')
    for i in hunks_equals_1:
        printF(w, i)
    printF(w, '-'*20)
    printF(w, 'Multi hunk:')
    for i in hunks_more_than_1:
        printF(w, i)
    printF(w, '-'*20)
    printF(w, 'More than 5 hunks:')
    for i in hunks_more_than_5:
        printF(w, i)
    printF(w, '-'*20)
    printF(w, '2 to 5 hunks:')
    for i in hunks_from_2_to_5:
        printF(w, i)
