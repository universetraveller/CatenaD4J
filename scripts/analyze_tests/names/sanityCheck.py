import readAll

def containsTest():
    pure2bak = getattr(readAll, 'pure2bak')
    mess2bak = getattr(readAll, 'mess2bak')
    pure2 = getattr(readAll, 'pure2')
    mess2 = getattr(readAll, 'mess2')
    for i in pure2bak:
        assert i in pure2
    for i in mess2bak:
        assert i in mess2
    empty_qualifier = getattr(readAll, 'empty_qualifier')
    pure1 = getattr(readAll, 'pure1')
    for i in pure1:
        assert i in empty_qualifier

def singleDiff(a, b):
    aset = set(a)
    bset = set(b)
    intersection = aset & bset
    onlya = aset - intersection
    onlyb = bset - intersection
    return intersection, onlya, onlyb

def printSingleDiff(a, b):
    aset = getattr(readAll, a)
    bset = getattr(readAll, b)
    u, oa, ob = singleDiff(aset, bset)
    print('Intersection of {} and {}: {}'.format(a, b, u))
    print('')
    print('Only in {}: {}'.format(a, oa))
    print('')
    print('Only in {}: {}'.format(b, ob))

def printDiff():
    printSingleDiff('pure1', 'pure2')
    print('---')
    printSingleDiff('mess1', 'mess2')
    print('---')
    printSingleDiff('junit', 'pure1')
    print('---')
    printSingleDiff('junit', 'mess1')
    print('---')
    printSingleDiff('pure1', 'mess1')
    print('---')
    printSingleDiff('first_level', 'first_level1')
    print('---')
    printSingleDiff('first_level1_members', 'table_bak')
    print('---')
    printSingleDiff('table', 'table_bak')

if __name__ == '__main__':
    containsTest()
    printDiff()
