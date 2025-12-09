import joblib
import json
import os
import tqdm
import subprocess
import multiprocessing as mp
import sys
ex_bugs = ['Cli_6','Collections_20','Collections_24','Collections_1', \
           'Collections_21','Collections_2','Collections_5','Collections_10', \
           'Collections_6','Collections_15','Collections_7','Collections_17', \
           'Collections_22','Collections_8','Collections_18', 'Collections_19', \
           'Collections_4', 'Time_21']
with open(sys.argv[1], 'r') as f:
    waitlist = f.read().splitlines()
def exportProp(path:str, prop:str):
    try:
        finished = subprocess.run(['defects4j', 'export',  '-p', prop, '-w', path], capture_output = True)
        finished.check_returncode()
        return finished.stdout.decode('utf-8')
    except Exception as E:
        try:
            if not os.path.exists('./exceptions'):
                os.makedirs('./exceptions')
            with open('./exceptions/exception_{}'.format(path), 'a') as f:
                f.write(str(E))
                f.write(finished.stdout.decode("utf-8"))
                f.write(finished.stderr.decode("utf-8"))
        except:
            print('Unhandled: {}'.format(path))
_props = ['classes.modified', 'classes.relevant', 'cp.compile', 'cp.test', 'dir.bin.classes', 'dir.bin.tests',  'dir.src.classes', 'dir.src.tests', 'tests.all', 'tests.relevant', 'tests.trigger']
def task(bugid, props, root):
    bugid = bugid.split(':')[0]
    if any(bug == bugid for bug in ex_bugs):
        return
    root[bugid] = {}
    if not os.path.exists('./d4j_export/{}'.format(bugid)):
        os.makedirs('./d4j_export/{}'.format(bugid))
    for prop in props:
        res = exportProp('{}/{}'.format(sys.argv[2], bugid), prop)
        with open('./d4j_export/{}/{}'.format(bugid, prop),  'w')  as f:
            f.write(res)
        res  = res.splitlines()
        root[bugid][prop] = res
_root = mp.Manager().dict()
joblib.Parallel(n_jobs=14)(joblib.delayed(task)(i, _props, _root) for i in tqdm.tqdm(waitlist))
with open('./d4j_export/database.json', 'w') as f:
    f.write(json.dumps(_root.copy(), indent=4))
