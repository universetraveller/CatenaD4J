import os
import shutil
d4j_home = ''
if not d4j_home:
    d4j_home = os.path.abspath(os.path.join(shutil.which('defects4j'), '..', '..', '..'))
assert d4j_home

d4j_projs = f'{d4j_home}/framework/projects/'
all_projs = [name for name in os.listdir(d4j_projs) if os.path.isdir(os.path.join(d4j_projs, name)) and name != 'lib']
all_bugs = {}
for proj in all_projs:
    with open(f'{d4j_projs}/{proj}/active-bugs.csv') as f:
        all_bugs[proj] = [id.split(',')[0] for id in f.read().splitlines()[1:]]
