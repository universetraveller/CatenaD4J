import os
import sys
sys.path.append('../../construct_database')
import d4j_all_bugs
sys.path.append('../../..')
from catena4j.bootstrap import initialize_system, system
initialize_system(system)
from catena4j import d4jutil
from catena4j.env import get_system_context
from catena4j.loaders import get_project_loader
c = get_system_context()

tasks = []
all_bugs = d4j_all_bugs.all_bugs
for proj in all_bugs:
    tasks.extend((proj, id) for id in all_bugs[proj])

for task in tasks:
    proj, id = task
    id = str(id)
    wd = os.path.join('/tmp/bugs_static/', f'{proj}_{id}')
    c.cwd = wd

    def test(is_buggy):
        layout = d4jutil.get_dir_src_cache(proj, id, is_buggy, c)
        loader = get_project_loader(proj)(c)
        src = loader.src_layout
        _test = loader.test_layout
        rebuild = get_project_loader(proj)(c).src_layout
        p = False
        if layout is not None:
            if layout[0] != src or layout[1] != _test:
                p = True
        if rebuild != src:
            p = True
        if p:
            print(proj, id, is_buggy)
            print(' ')

    test(True)
    test(False)

