import os
import sys
sys.path.append('../../construct_database')
import d4j_all_bugs
sys.path.append('../../..')
from catena4j.bootstrap import initialize_system, system
initialize_system(system)
from catena4j.commands import export
from catena4j.env import get_system_context
c = get_system_context()

tasks = []
all_bugs = d4j_all_bugs.all_bugs
for proj in all_bugs:
    tasks.extend((proj, id) for id in all_bugs[proj])

f = lambda *a, **b:None
g = None
for task in tasks:
    proj, id = task
    id = str(id)
    wd = os.path.join('/tmp/bugs_static/', f'{proj}_{id}')
    c.cwd = wd
    for prop in export.d4j_static:
        g = export._query_d4j_static
        export._query_d4j_static = f
        a = export.query_d4j_static(prop, proj, id, wd, c, 'BUGGY')
        export._query_d4j_static = g
        b = export._query_d4j_static(prop, proj, id, wd, c, 'BUGGY')
        if prop == 'tests.relevant':
            assert a is None and b is not None
        elif a != b:
            print(proj, id, prop)
