import joblib
import tqdm
import subprocess
import sys
import os
sys.path.append('../../construct_database')
import d4j_all_bugs
import time

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

log = open('./c4j_time', 'w')
def task(bugid):
    try:
        start = time.perf_counter_ns()
        finished = subprocess.run(['/root/workbench/CatenaD4J/c4j', 'checkout', '-p', bugid[0], '-v', '{}b'.format(bugid[1]), '-w', '{}/{}_{}'.format(sys.argv[2], bugid[0], bugid[1])], capture_output=True)
        finished.check_returncode()
        end = time.perf_counter_ns()
        log.write('_'.join(bugid))
        log.write(' ')
        log.write(f'{end - start}\n')
    except Exception as E:
        with open('./exceptions_c4j'.format(), 'a') as f:
            try:
                f.write('_'.join(bugid))
                f.write(' ')
                f.write(str(E))
                f.write('\n')
            except:
                try:
                    f.write(E.stderr)
                except Exception as F:
                    print(F)
            f.write(finished.stdout.decode("utf-8"))
            f.write(finished.stderr.decode("utf-8"))
            f.write('----------\n')

for i in tqdm.tqdm(waitlist()):
    task(i)
log.close()
#joblib.Parallel(n_jobs=14)(joblib.delayed(task)(i) for i in tqdm.tqdm(waitlist()))
