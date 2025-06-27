from pathlib import Path
import shutil
import sys
import os
import difflib

sys.path.append('../..')

from catena4j.bootstrap import initialize_system, system
from catena4j.d4jutil import fix_tests, get_flaky_tests, get_dir_src_tests
from catena4j.env import get_system_context

initialize_system(system)

def test(project, bid):
    os.system(f'cp -r /tmp/bugs_static/{project}_{bid} ./{project}_{bid}')
    wd = os.path.abspath(f'./{project}_{bid}')
    context = get_system_context()
    a, b, c = get_flaky_tests(project, bid, True, context)
    test_dir = get_dir_src_tests(project, bid, wd, True, context)
    base_dir = Path(wd, test_dir)
    d4j = []
    c4j = []
    for method in b:
        # defects4j directly convert class name to file path
        # that would be not precise, for example, for embedded
        # classes there is no source file available
        clz, _, met = method.partition('::')
        f: Path = base_dir / (clz.replace('.', '/') + '.java.bak')
        if f.is_file():
            g = f.with_suffix('')
            h = g.with_suffix('.bak1')
            shutil.copy2(g, h)
            shutil.copy2(f, g)
            d4j.append(h)
            c4j.append(g)
    fix_tests(project, bid, wd, True, context)
    for i, j in zip(d4j, c4j):
        with i.open() as f:
            a = f.readlines()
        with j.open() as f:
            b = f.readlines()
        print('---')
        print(str(i))
        print(''.join(list(difflib.unified_diff(a, b))))
        print('---')

if __name__ == '__main__':
    test(sys.argv[1], sys.argv[2])