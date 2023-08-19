import sys
root = sys.argv[0][:-9]
d4j = 'defects4j'
d4j_cmds = ['bids', 'checkout', 'compile', 'test', 'pids', 'coverage', 'env', 'export', 'monitor.test',  'mutation', 'query', 'info']
c4j_cmds = ['checkout', 'info', 'ver', 'export', 'reset', 'pids', 'bids', 'cids']
all_cmds = c4j_cmds + d4j_cmds
CONFIG_RESET_IN_CHECKOUT=0
CONFIG_GIT_TAG=1
if CONFIG_GIT_TAG:
    TAG_PATTERN = 'C4J_{pid}_{bid}_{cid}_{buggy}'
CONFIG_PRE_FIX=0
pyver = sys.version
version = '0.3.1'
validator_log_level=2
p_head = 'CatenaD4j# '
helper = '''usage: catana4j <command> [options]

Commands:
    checkout    Check out the specific version of a bug
    export      Export specific infomation of a bug
    reset       Reset all unstaged modification for a working directory
    pids        Print available project_names
    bids        Print available bug_ids that contains at least one cid
    cids        Print available catena ids for a bug_id
    info        Not implemented now
    test        Not implemented now
    compile     Not implemented now
    ver         Not implemented now
'''
