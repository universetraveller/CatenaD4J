import joblib
import json
import os
import tqdm
import subprocess
import multiprocessing as mp
import time
import sys
sys.path.append('../../construct_database')
import d4j_all_bugs

def waitlist():
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1]) as f:
            tasks = list(map(lambda x:x.split('_'), f.read().splitlines()))
    else:
        tasks = []
        all_bugs = d4j_all_bugs.all_bugs
        for proj in all_bugs:
            tasks.extend((proj, id) for id in all_bugs[proj])
    return tasks

a = open('./time_consumed', 'w')
def export_prop(path:str, prop:str):
    try:
        start = time.perf_counter_ns()
        finished = subprocess.run(['/root/workbench/CatenaD4J/c4j', 'export',  '-p', prop, '-w', path], capture_output = True)
        end = time.perf_counter_ns()
        bid = path[path.rfind('/')+1:]
        a.write(','.join([bid, prop, str(end - start)]))
        a.write('\n')
        finished.check_returncode()
        return finished.stdout.decode('utf-8')
    except Exception as e:
        bid = path[path.rfind('/')+1:]
        print(str(e))
        print('\n')
        print('--------------')
        print('\n')
        print(prop)
        print('\n')
        print('---')
        print('\n')
        print(path)
        print('\n')
        print('---')
        print('\n')
        print(finished.stdout.decode('utf-8'))
        print('\n')
        print('---')
        print('\n')
        print(finished.stderr.decode('utf-8'))
        print('\n')
        print('--------------')
        print('\n')
        print(bid, prop, str(e))
        return ''

_props = d4j_all_bugs.d4j_props
user_home = os.path.expanduser("~")

def task(bugid, props):
    _dir = './c4j_export/{}/{}'.format(bugid[0], bugid[1])
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    workdir = os.path.join(sys.argv[2], '_'.join(bugid))
    for prop in props:
        res = export_prop(workdir, prop)
        if prop in ('cp.compile', 'cp.test'):
            res = ':'.join(map(lambda cp : \
                                cp.replace(d4j_all_bugs.d4j_home, '{d4j_home}', 1)
                                    .replace(workdir, '{d4j_workdir}', 1)
                                    .replace(user_home, '{user_home}', 1),
                    res.split(':')))
        with open(os.path.join(_dir, prop),  'w')  as f:
            f.write(res)

for i in tqdm.tqdm(waitlist()):
    task(i, _props)

a.close()
