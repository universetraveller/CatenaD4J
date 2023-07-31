with open('./validation', 'r') as f:
    f = f.read().splitlines()
for i in range(len(f)):
    it = f[i]
    if 'TimeoutError: generator.run() timeout' in f[i+1]:
        if 'No ending' in f[i+2]:
            if not f[i+3].startswith('NOTICE'):
                print(it)
