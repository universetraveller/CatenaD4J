from pathlib import Path
import shutil
import sys
import os
import difflib
import time

sys.path.append(f'{str(Path(__file__).parent)}/../../../..')

from catena4j.bootstrap import initialize_system, system
from catena4j.d4jutil import fix_tests, get_flaky_tests, get_dir_src_tests
from catena4j.env import get_system_context

initialize_system(system)

def diff_strings_with_invisibles(s1: str, s2: str) -> None:
    def show_invisibles(s):
        return ''.join(
            f'\\u{ord(c):04x}' if c.isspace() or ord(c) < 32 or ord(c) > 126 else c
            for c in s
        )

    v1 = show_invisibles(s1)
    v2 = show_invisibles(s2)

    diff = list(difflib.ndiff([v1], [v2]))
    print("String 1:", repr(s1))
    print("String 2:", repr(s2))
    print("Diff with invisibles:")
    print('\n'.join(diff))

bugs = '/tmp/bugs_static'
def test(project, bid):
    cwd = f'{str(Path(__file__).parent)}/{project}_{bid}'
    cwd = os.path.abspath(cwd)
    if not os.path.exists(str(cwd)):
        os.system(f'cp -r {bugs}/{project}_{bid} {cwd}')
    context = get_system_context()
    a, b, c = get_flaky_tests(project, bid, False, context)
    test_dir = get_dir_src_tests(project, bid, False, context)
    base_dir = Path(cwd, test_dir)
    d4j = []
    c4j = []
    ff = set()
    files = {}
    for method in b:
        # defects4j directly convert class name to file path
        # that would be not precise, for example, for embedded
        # classes there is no source file available
        clz, _, met = method.partition('::')
        f: Path = base_dir / (clz.replace('.', '/') + '.java.bak')
        if f not in ff and f.is_file():
            ff.add(f)
            g = f.with_suffix('')
            h = f.with_suffix('.bak1')
            shutil.copy2(g, h)
            shutil.copy2(f, g)
            d4j.append(h)
            c4j.append(g)
        g = f.with_suffix('')
        if str(g) not in files:
            files[str(g)] = set()
        files[str(g)].add(met)
    args = []
    for f in files:
        methods = files[f]
        args.append(f'{f}:{",".join(methods)}')
    args = ' '.join(args)
    start = time.perf_counter_ns()
    os.system(f'java -cp :/usr/lib/jvm/java-8-openjdk-amd64/lib/tools.jar FixTests {args}')
    end = time.perf_counter_ns()
    for i, j in zip(d4j, c4j):
        with i.open() as f:
            a = f.readlines()
        with j.open() as f:
            b = f.readlines()
        for k, l in zip(a, b):
            if k != l:
                #diff_strings_with_invisibles(k, l)
                pass
        print(''.join(list(difflib.unified_diff(a, b, str(i), str(j)))))
    for f in ff:
        g = f.with_suffix('')
        h = f.with_suffix('.bak1')
        shutil.copy2(h, g)
    return end - start

def test_average(project, id, n):
    cwd = f'{str(Path(__file__).parent)}/{project}_{id}'
    cwd = os.path.abspath(cwd)
    os.system(f'cp -r {bugs}/{project}_{id} {cwd}')
    _t = 0
    for i in range(n):
        _t += test(project, id)
    print(f'average:', _t * 10**-6 / n, 'ms')
    os.system(f'rm -r {cwd}')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test(sys.argv[1], sys.argv[2])
    else:
        test_average('Chart', '1', 10)
