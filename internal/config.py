import sys
root = sys.argv[0][:-9]
d4j = 'defects4j'
d4j_cmds = ['bids', 'checkout', 'compile', 'test', 'pids', 'coverage', 'env', 'export', 'monitor.test',  'mutation', 'query', 'info']
c4j_cmds = ['checkout', 'info', 'ver', 'export']
all_cmds = c4j_cmds + d4j_cmds
pyver = sys.version
version = '0.0.1'
p_head = 'CatenaD4j# '
helper = '''
'''
