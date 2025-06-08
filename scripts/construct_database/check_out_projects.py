import joblib
import tqdm
import subprocess
import sys
import os
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

def task(bugid):
    try:
        finished = subprocess.run(['defects4j', 'checkout', '-p', bugid[0], '-v', '{}b'.format(bugid[1]), '-w', '{}/{}_{}'.format(sys.argv[2], bugid[0], bugid[1])], capture_output=True)
        finished.check_returncode()
        finished = subprocess.run(['defects4j', 'compile'], cwd='{}/{}_{}'.format(sys.argv[2], bugid[0], bugid[1]), capture_output=True)
        finished.check_returncode()
    except Exception as E:
        with open('./exception_{}'.format('_'.join(bugid)), 'w') as f:
            try:
                f.write(str(E))
            except:
                try:
                    f.write(E.stderr)
                except Exception as F:
                    print(F)
            f.write(finished.stdout.decode("utf-8"))
            f.write(finished.stderr.decode("utf-8"))

joblib.Parallel(n_jobs=14)(joblib.delayed(task)(i) for i in tqdm.tqdm(waitlist()))
