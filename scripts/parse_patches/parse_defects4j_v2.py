import parser_defects4j
import os
import json
import d4jpath
import sys

root = d4jpath.d4j_home
projs = d4jpath.all_projs
all_bugs = d4jpath.all_bugs

hunks_info = []
max_hunk_num = {}

parser = parser_defects4j.Parser(encoding='latin-1')

patch_source = f'{root}/framework/projects'
if len(sys.argv) > 1:
    patch_source = sys.argv[1]

for proj in projs:
    paths = ['{}/{}/patches/{}.src.patch'.format(patch_source, proj, id)\
                                                                for id in all_bugs[proj]]
    max_hunk_num[proj] = -1
    if not os.path.exists('./patches/{}/'.format(proj)):
        os.makedirs('./patches/{}/'.format(proj))
    for i in paths:
        idx = i[i.rfind('/') + 1:]
        idx = idx[:idx.find('.')]
        try:
            edits = parser.parse(i)
            patch = parser_defects4j.d4j_patch_to_map(edits)
        except Exception as E:
            print('Error at ' + i)
            print(E)
            continue
        with open('./patches/{}/{}.json'.format(proj, idx), 'w') as f:
            json.dump(patch, f, indent=2)
        hunks_num = patch['num_of_hunks']
        hunks_info.append((proj, idx, hunks_num))
        if hunks_num > max_hunk_num[proj]:
            max_hunk_num[proj] = hunks_num

hunks_info.sort(key=lambda x:x[2])
with open('hunks.txt', 'w') as f:
    f.write('Max hunks number\n')
    for name in max_hunk_num:
        f.write('{}: {}\n'.format(name, max_hunk_num[name]))
    f.write('\n')
    f.write('Hunks information\n')
    f.write('Project,BugID,HunksNumber\n')
    for i in hunks_info:
        f.write('{},{},{}\n'.format(*i))
