import difflib
from pathlib import Path
c4j = Path('./c4j_export')
for proj in c4j.iterdir():
    for id in proj.iterdir():
        for prop in id.iterdir():
            d4j_prop = list(prop.parts)
            d4j_prop = Path('/root/workbench/Archived/d4j_export/', *d4j_prop[1:])
            with prop.open() as f:
                c = f.read().strip()
            with d4j_prop.open() as f:
                d = f.read()
            if 'JxPath' in str(proj) and 'cp.' in str(prop):
                c = set(c.split(':'))
                d = set(d.split(':'))
                if c - d:
                    print(str(prop), '-', str(d4j_prop))
                    print(c - d)
                    print(' ')
                if d - c:
                    print(str(d4j_prop), '-', str(prop))
                    print(d - c)
                    print(' ')
            elif 'tests.all' in str(prop):
                c = set(c.splitlines())
                d = set(d.splitlines())
                if c - d:
                    print(str(prop), '-', str(d4j_prop))
                    print(c - d)
                    print(' ')
                if d - c:
                    print(str(d4j_prop), '-', str(prop))
                    print(d - c)
                    print(' ')
            elif c.strip() != d.strip():
                print(' ')
                print(prop)
                print('\n'.join(list(difflib.unified_diff(c.splitlines(), d.splitlines()))))
