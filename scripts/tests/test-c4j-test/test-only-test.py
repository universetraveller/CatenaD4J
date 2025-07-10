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

log = open('./log', 'w')
def run(cmd, log, name):
    try:
        start = time.perf_counter_ns()
        finished = subprocess.run(cmd, capture_output=True)
        end = time.perf_counter_ns()
        finished.check_returncode()
        log.write(f'.{name} ')
        log.write(f'{end - start} ns\n')
        stdout = finished.stdout.decode()
        log.write('STDOUT START\n')
        if stdout.strip():
            log.write(stdout)
            log.write('\n')
        log.write('STDOUT END\n')
        #log.write('STDERR START\n')
        #log.write(finished.stderr.decode())
        #log.write('\n')
        #log.write('STDERR END\n')
        log.flush()
        return 0
    except Exception as E:
        with open('./exceptions'.format(), 'a') as f:
            try:
                f.write(' '.join(cmd))
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
        return 1

def task(bugid):
    log.write('VERSION START\n')
    log.write('_'.join(bugid))
    log.write('\n')
    wd = '{}/{}_{}'.format(sys.argv[2], bugid[0], bugid[1])
    run(['/root/workbench/CatenaD4J/c4j', 'test', '-w', wd], log, 'test')
    log.write('VERSION END\n')
    log.flush()

for i in tqdm.tqdm(waitlist()):
    task(i)
log.close()
