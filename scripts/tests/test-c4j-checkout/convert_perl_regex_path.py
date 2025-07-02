a = '''
'''.strip().splitlines()
def parse(s):
    idx = 0
    a = []
    b = []
    active = None
    while idx < len(s):
        ch = s[idx]
        if ch == 's' and s[idx+1] == '/':
            active = a
            idx += 1
        elif ch == '/' and s[idx - 1] != '\\':
            if s[idx + 1] == 'g' and s[idx + 2] == ';':
                break
            active = b
        elif ch == '\\':
            idx += 1
            continue
        else:
            if active is not None:
                active.append(ch)
        idx += 1
    return ''.join(a), ''.join(b)

for line in a:
    a, b = parse(line.strip())
    print(' '* 16 + f'\'{a}\':\n' + ' '* 16 + '\'' + b.replace('$PROJECTS_DIR/$PID', '{project_dir}') + '\',')
