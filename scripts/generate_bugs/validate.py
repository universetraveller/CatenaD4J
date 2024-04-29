import glob


validation = {}
def tryAdd(a, b):
    if not b in validation:
        validation[b] = []
    validation[b].append(a)
with open('./2to5', 'r') as f:
    needs = f.read().splitlines()
actual = []
def validate_exceptions():
    paths = glob.glob('./exceptions/*')
    for i in paths:
        name = i.replace('./exceptions/EXCEPTION_', '')
        with open(i, 'r') as f:
            tryAdd(f.read().splitlines()[-1], name)
def is_outside_error(j):
    if not j.split(' ')[0].strip().endswith(':'):
        return False
    if 'exception' in j.split(' ')[0].strip().lower() or 'error' in j.split(' ')[0].strip().lower():
        return True
    return False
def validate_logs():
    paths = glob.glob('./working/*/log')
    for i in paths:
        name = i.replace('./working/', '').replace('/log', '')
        with open(i, 'r') as f:
            f = f.read().splitlines()
            if not len(f) == 0:
                actual.append(name)
                if not f[-1].startswith('Find'):
                    tryAdd('No ending', name)
            for j in f:
                if 'EXCEPTION:' in j or 'ERROR:' in j or is_outside_error(j) or 'NOTICE' in j:
                    tryAdd(j, name)
def validate():
    validate_exceptions()
    validate_logs()
    with open('validation', 'w') as f:
        f.write('not in map:\n')
        for i in needs:
            if not i in actual:
                f.write('{}\n'.format(i))
        f.write('---\n')
        for i in validation:
            f.write('{}\n'.format(i))
            for j in validation[i]:
                f.write('{}\n'.format(j))
            f.write('---\n')
validate()
