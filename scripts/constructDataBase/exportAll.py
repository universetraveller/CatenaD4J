import joblib
import json
import  os
import  tqdm
import subprocess
import multiprocessing as mp
with open('./research/2toMore', 'r') as f:
    waitlist = f.read().splitlines()
def exportProp(path:str, prop:str):
    try:
        finished = subprocess.run(['defects4j', 'export',  '-p', prop, '-w', path], capture_output = True)
        finished.check_returncode()
        return finished.stdout.decode('utf-8')
    except Exception as E:
        try:
            with open('./exceptions/exception_{}'.format(path), 'a') as f:
                f.write(str(E))
                f.write(finished.stdout.decode("utf-8"))
                f.write(finished.stderr.decode("utf-8"))
        except:
            print('unhandle: {}'.format(path))
_props = ['classes.modified', 'classes.relevant', 'cp.compile', 'cp.test', 'dir.bin.classes', 'dir.bin.tests',  'dir.src.classes', 'dir.src.tests', 'tests.all', 'tests.relevant', 'tests.trigger']
def task(bugid, props, root):
    bugid = bugid.split(':')[0]
    if bugid == 'Time_21':
        return
    root[bugid] = {}
    if not os.path.exists('./d4j_export/{}'.format(bugid)):
        os.makedirs('./d4j_export/{}'.format(bugid))
    for prop in props:
        res = exportProp('./d4j_buggy/{}'.format(bugid), prop)
        with open('./d4j_export/{}/{}'.format(bugid, prop),  'w')  as f:
            f.write(res)
        res  = res.splitlines()
        root[bugid][prop] = res
_root = mp.Manager().dict()
joblib.Parallel(n_jobs=14)(joblib.delayed(task)(i, _props, _root) for i in tqdm.tqdm(waitlist))
with open('./d4j_export/database.json', 'w') as f:
    f.write(json.dumps(_root.copy(), indent=4))
