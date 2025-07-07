data = open('./time_consumed').read().splitlines()

a = []
for line in data:
    line = line.split(',')
    a.append((int(line[2]), f'{line[0]}#{line[1]}'))
a = sorted(a, reverse=True)
b = 0
for i in a:
    b += i[0]
print('average: ', b * 10**-6 / len(a), 'ms')
for i in a[:]:
    print(i[1], i[0] * 10**-6, 'ms')
