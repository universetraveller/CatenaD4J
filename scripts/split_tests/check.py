my = open('./2toMore', 'r').read().splitlines()
tt = open('./temp', 'r').read().splitlines()
for i in my:
    if not i in tt:
        print('only in my result ' + i)
for i in tt:
    if not i in my:
        print('only in online list ' + i)
