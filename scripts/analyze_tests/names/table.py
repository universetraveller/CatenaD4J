ids = ['6', '11']
for id in ids:
    with open('./checking.bak' + id, 'r') as f:
        f = f.read().splitlines()
    table = set()
    for i in f:
        if i.startswith('$') or i.startswith('#'):
            continue
        if '@' in i:
            table.add(i[:i.find('@')])
        else:
            table.add(i)
    with open('./first_level' + id, 'r') as f:
        f = f.read().splitlines()
    fl = set(f)
    fl_m = set()
    for i in fl:
        if i.startswith('$') or i.startswith('#'):
            continue
        if id == '6':
            fl_m.add(i.split('.')[1])
        else:
            fl_m.add(i)
    if id == '6':
        table = table - {'chiSquareTest', 'chiSquare'} | {'checkState', 'validate'}
    fl_mItable = fl_m & table
    oif = fl_m - fl_mItable
    oit = table - fl_mItable
    print(oif)
    print(oit)
    print(len(fl_mItable) + len(oif) + len(oit))
    with open('./table' + id, 'w') as f:
        for i in fl_m | table:
            f.write(i)
            f.write('\n')
