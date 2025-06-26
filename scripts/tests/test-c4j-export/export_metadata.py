import joblib
import json
import os
import tqdm
import subprocess
import multiprocessing as mp
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
            #if not proj in ('Closure', 'JxPath', 'Cli'):
            if not proj in ('Closure',):
                continue
            tasks.extend((proj, id) for id in all_bugs[proj])
    return tasks

def export_prop(path:str, prop:str):
    try:
        finished = subprocess.run(['c4j', 'clean', '-w', path], capture_output = True)
        finished.check_returncode()
        finished = subprocess.run(['c4j', 'export',  '-p', prop, '-w', path], capture_output = True)
        finished.check_returncode()
        return finished.stdout.decode('utf-8')
    except Exception as e:
        bid = path[path.rfind('/')+1:]
        with open(f'./exceptions/{bid}.{prop}', 'w') as f:
            f.write(str(e))
            f.write('\n')
            f.write('--------------')
            f.write('\n')
            f.write(prop)
            f.write('\n')
            f.write('---')
            f.write('\n')
            f.write(path)
            f.write('\n')
            f.write('---')
            f.write('\n')
            f.write(finished.stdout.decode('utf-8'))
            f.write('\n')
            f.write('---')
            f.write('\n')
            f.write(finished.stderr.decode('utf-8'))
            f.write('\n')
            f.write('--------------')
            f.write('\n')

_props = d4j_all_bugs.d4j_props
user_home = os.path.expanduser("~")

def task(bugid, props, root):
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
        res  = res.splitlines()
        root[bugid[0]][bugid[1]][prop] = res

if __name__ == '__main__':
    _manager = mp.Manager()
    _root = _manager.dict()
    for id in waitlist():
        if not id[0] in _root:
            _root[id[0]] = _manager.dict()
        _root[id[0]][id[1]] = _manager.dict()
    joblib.Parallel(n_jobs=14)(joblib.delayed(task)(i, _props, _root) for i in tqdm.tqdm(waitlist()))
