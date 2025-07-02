from pathlib import Path
import difflib
def export_props(props):
    aa = set()
    for line in props:
        if line.startswith('#'):
            continue
        if ',' in line:
            line = line.split('=')
            line = line[0] + ','.join(sorted(line[1].split(',')))
        aa.add(line.strip())
    return aa

def run(a, b):
    for d in a.iterdir():
        dd = b / d.name
        for f in d.iterdir():
            if f.name == 'defects4j.build.properties':
                df = dd / f.name
                dp = export_props(df.open().read().splitlines())
                cp = export_props(f.open().read().splitlines())
                if dp - cp:
                    print(f)
                    print('dp - cp')
                    print(dp - cp)

                if cp - dp:
                    print(f)
                    print('cp - dp')
                    print(cp - dp)
            elif f.name.startswith('.git'):
                continue
            elif f.name.startswith('.svn'):
                continue
            elif f.name.startswith('.mvn'):
                continue
            elif f.name.startswith('.'):
                df = dd / f.name
                ds = df.open().read()
                cs = f.open().read()
                if ds == cs:
                    continue
                dp = export_props(ds.splitlines())
                cp = export_props(cs.splitlines())
                if dp - cp:
                    print(f)

a=Path('/tmp/c4j_bugs')
b=Path('/tmp/d4j_bugs')
run(a, b)
run(b, a)

with open('./diff_files') as f:
    f = f.read().splitlines()

ignored = []
critical = []
for line in f:
    if line.startswith('Only in '):
        line = line[8:].split(':')
        if 'c4j_bugs' in line[0]:
            # no harm
            ignored.append(line)
            continue
        else:
            p = Path(line[0], line[1].strip())
            if str(p).endswith('.bak'):
                p1 = p.with_suffix('') 
                ps1 = p1.open(encoding='latin-1').read()
                ps = p.open(encoding='latin-1').read()
                if ps.strip() == ps1.strip():
                    ignored.append(line)
                    continue
            critical.append(line)
    elif line.startswith('Files '):
        a = line.split()[1]
        b = line.split()[3]
        a = a.open().readlines()
        b = b.open().readlines()
        matcher = difflib.SequenceMatcher(None, a, b)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue
            ac = a[i1:i2]
            bc = b[j1:j2]

        critical.append(line)
    else:
        print('unknown line', line)

print('ignored', len(ignored), 'files')
print('critical', len(critical), 'files')
print('total', len(f), 'files')
for i in critical:
    print(i)
