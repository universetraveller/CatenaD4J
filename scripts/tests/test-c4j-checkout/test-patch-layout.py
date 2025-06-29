from pathlib import Path
import shutil
import sys
import os
import difflib
import time

sys.path.append(f'{str(Path(__file__).parent)}/../../..')

from catena4j.bootstrap import initialize_system, system
from catena4j.env import get_system_context
from catena4j.util import detect_apply_layout, Git, run_command
from catena4j.commands import xids

initialize_system(system)

context = get_system_context()
bugs = '/tmp/bugs_static'
@classmethod
def apply_check1(cls, patch, n, wd):
    return run_command(['git', 'apply', '--check', '-R', f'-p{n}', patch], cwd=wd)

Git.apply_check = apply_check1

failed = [
    #'/root/defects4j/framework/projects/Codec/patches/13.src.patch',
    #'/root/defects4j/framework/projects/Jsoup/patches/71.src.patch',
    '/root/defects4j/framework/projects/Jsoup/patches/24.src.patch'
]
def test():
    n1 = 0
    n = 0
    for project in xids.query_pids(context):
        deprecated = xids.query_deprecated_bids(project, context)
        patches = Path(context.d4j_home,
                                context.d4j_rel_projects,
                                project,
                                'patches')

        for p in patches.iterdir():
            id = p.name.split('.')[0]
            if id in deprecated:
                continue
            if p.name.split('.')[1] == 'test':
                continue
            wd = os.path.join(bugs, f'{project}_{id}')
            start = time.perf_counter_ns()
            detect_apply_layout(p, wd)
            end = time.perf_counter_ns()
            n1 += end - start
            n += 1
    print(n1, n1/n)

test()