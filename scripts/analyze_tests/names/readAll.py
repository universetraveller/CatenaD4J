def readFile(name):
    with open(name, 'r') as f:
        return f.read()
junit = readFile('./junit').splitlines()
mess1 = readFile('./mess_names1').splitlines()
mess2 = readFile('./mess_names2').splitlines()
mess2bak = readFile('./mess_names2.bak').splitlines()
pure1 = readFile('./pure_names1').splitlines()
pure2 = readFile('./pure_names2').splitlines()
pure2bak = readFile('./pure_names2.bak').splitlines()
empty_qualifier = readFile('./empty_qualifier').splitlines()
pure = set(junit) | set(pure1) | set(pure2)
first_level = readFile('./first_level').splitlines()
first_level1 = readFile('./first_level1').splitlines()
first_level1_members = set()
for i in first_level1:
    first_level1_members.add(i[i.find('.')+1:])
table_bak = readFile('./table.bak').splitlines()
table = readFile('./table').splitlines()
