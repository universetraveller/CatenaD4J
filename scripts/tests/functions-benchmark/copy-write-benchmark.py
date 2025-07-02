from benchmark import test1
import shutil
def option1():
    shutil.copy2('file.txt', 'file.txt.bak')
    with open('file.txt', 'r') as f:
        data = f.read()
    # Simulate modification
    data += ""
    with open('file.txt', 'w') as f:
        f.write(data)

def option2():
    with open('file.txt', 'r') as f:
        data = f.read()
    with open('file.txt.bak', 'w') as bak:
        bak.write(data)
    # Simulate modification
    data += ""
    with open('file.txt', 'w') as f:
        f.write(data)

test1(option1, 1000)
test1(option2, 1000)
