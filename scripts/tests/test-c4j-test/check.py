import json
from pathlib import Path
import sys
sys.path.append('../../..')
from catena4j.bootstrap import initialize_system, system
initialize_system(system)
from catena4j import d4jutil
from catena4j.env import get_system_context
c = get_system_context()

log = open('./log').read().splitlines()


bugs = {}
idx = 0

class Namespace:
    pass

def sections(lines):
    _sections = []
    section = None
    subsection = None
    for line in lines:
        if line == 'VERSION START':
            assert section is None
            assert subsection is None
            section = Namespace()
            continue
        if line == 'VERSION END':
            _sections.append(section)
            section = None
            subsection = None
            continue
        if not hasattr(section, 'bug'):
            assert subsection is None
            section.bug = line
            continue
        if line.startswith('.'):
            name, t, _ = line[1:].split()
            subsection = Namespace()
            setattr(section, name, subsection)
            subsection.time_ns = int(t)
            subsection._reading = None
            continue
        if line == 'STDOUT START':
            assert subsection is not None
            subsection.stdout = []
            subsection._reading = 'stdout'
            continue
        if line == 'STDOUT END':
            assert subsection is not None
            subsection._reading = None
            continue
        if subsection is not None and subsection._reading == 'stdout':
            subsection.stdout.append(line)
            continue
    return _sections

bugs = sections(log)

checkout_tasks = []
compile_tasks = []
test_tasks = []
data = None
data_path = Path('/root/workbench/Archived/d4j_export/database.json')
if data_path.is_file():
    data = json.load(open(data_path))
for bug in bugs:
    name = bug.bug
    checkout_tasks.append((bug.checkout.time_ns, bug.bug))
    compile_tasks.append((bug.compile.time_ns, bug.bug))
    test_tasks.append((bug.test.time_ns, bug.bug))
    failing_tests = bug.test.stdout
    ftn = int(failing_tests[0].split(':')[1])
    fts = set()
    for ft in failing_tests[1:]:
        ft = ft.strip()
        if not ft:
            continue
        fts.add(ft)
    pid, bid = name.split('_')
    c4j_tt = set(map(lambda x:x.replace('::', '#', 1), d4jutil.get_tests_trigger(pid, bid, c)))
    extra = fts - c4j_tt
    missing = c4j_tt - fts
    if extra:
        print(f'{name} extra failing tests:')
        for ft in extra:
            print(ft)
        print('---')
    if missing:
        print(f'{name} missing failing tests:')
        for ft in missing:
            print(ft)
        print('---')
    if data is not None:
        d4j_tt = set(map(lambda x:x.replace('::', '#', 1), data[pid][bid]['tests.trigger']))
        if d4j_tt - c4j_tt:
            print(f'{name} missing tt in c4j')
        if c4j_tt - d4j_tt:
            print(f'{name} extra tt in c4j')
