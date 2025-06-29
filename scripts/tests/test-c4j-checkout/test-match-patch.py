import re

from pathlib import Path
import sys
import time

sys.path.append(f'{str(Path(__file__).parent)}/../../..')

from catena4j.bootstrap import initialize_system, system
from catena4j.env import get_system_context
from catena4j.commands import xids

initialize_system(system)

context = get_system_context()

aa = re.compile(r'^diff --git a/(\S+)')
bb = re.compile(r'^---\s(?!/dev/null)(\S+)')
def get_first_file_path(f):
    with f.open(encoding='latin-1') as g:
        while True:
            line = g.readline()
            if not line:
                break
            if line.startswith('diff --git a/'):
                line = line[13:]
                return line[:line.find(' ')].strip()
            elif line.startswith('Index:'):
                return line[7:].strip()
            elif line.startswith('--- '):
                line = line[4:]
                return line[:line.find(' ')].strip()
    return None

def get_first_file_path_with_regex(f):
    with f.open(encoding='latin-1') as g:
        patch_text = g.read()
    match = re.search(
        r'(?m)^diff --git a/(\S+)|^Index: (\S+)|^---\s(?!/dev/null)(\S+)',
        #r'(?m)^diff --git a/(\S+)|^Index: (\S+)',
        patch_text
    )
    if match:
        gs = match.groups()
        if gs[0]:
            return gs[0]
        elif gs[1]:
            return gs[1]
        else:
            return gs[2]
        #return next(g for g in match.groups() if g).strip()
    return None

ps = []
for project in xids.query_pids(context):
    patches = Path(context.d4j_home,
                            context.d4j_rel_projects,
                            project,
                            'patches')

    for p in patches.iterdir():
        ps.append(p)

def test(f):
    c = []
    start = time.perf_counter_ns()
    for i in ps:
        c.append(f(i))
    end = time.perf_counter_ns()
    return end - start, c

a, b = test(get_first_file_path)
c, d = test(get_first_file_path_with_regex)
print(a, c)

for i, j in zip(b, d):
    if i != j:
        print(i)
        print(j)