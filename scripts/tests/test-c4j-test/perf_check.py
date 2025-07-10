



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

tests = {}
def parse(f):
    with open(f) as _f:
        log = sections(_f.read().splitlines())
    
    if f.startswith('./'):
        f = f[2:]

    if f.startswith('log.'):
        f = f[4:]

    for bug in log:
        pid, bid = bug.bug.split('_')
        time = bug.test.time_ns

        p = tests.setdefault(pid, {})
        b = p.setdefault(bid, {})
        b[f] = time * 10**-9

parse('./log.ant')
parse('./log.HashMap')
parse('./log.LinkedHashMap')
parse('./log.IsolatedClassLoader')

# project average
for p in tests:
    print(p)
    bugs = tests[p]
    fs = {}
    for bug in bugs:
        for f in bugs[bug]:
            if f not in fs:
                fs[f] = 0
            fs[f] += bugs[bug][f]
    for f in fs:
        print(f'{f} {fs[f] / len(bugs)}s')
    print('---')

def check(base, error):
    for p in tests:
        bugs = tests[p]
        for bug in bugs:
            b = bugs[bug][base]
            for f in bugs[bug]:
                if f == base:
                    continue
                c = bugs[bug][f]
                d = (c - b) / b
                if abs(d) > error:
                    print(f'[{p}_{bug}] {f} performance loss: {d*100}%')

check('HashMap', 0.05)