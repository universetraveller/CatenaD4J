with open('./checking.bak', 'r') as f:
    f = f.read().splitlines()
table = set()
for i in f:
    if i.startswith('$') or i.startswith('#'):
        continue
    if '@' in i:
        table.add(i[:i.find('@')])
    else:
        table.add(i)
with open('./first_level', 'r') as f:
    f = f.read().splitlines()
fl = set(f)
fl_m = set()
for i in fl:
    if i.startswith('$') or i.startswith('#'):
        continue
    fl_m.add(i.split('.')[1])
fl_mItable = fl_m & table
oif = fl_m - fl_mItable
oit = table - fl_mItable
print(oif)
print(oit)
print(len(fl_mItable) + len(oif) + len(oit))
with open('./table', 'w') as f:
    for i in fl_m | table:
        f.write(i)
        f.write('\n')
