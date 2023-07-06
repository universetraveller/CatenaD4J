import joblib
import  tqdm
import subprocess
with open('./research/2toMore', 'r') as f:
    waitlist = f.read().splitlines()
def task(bugid):
    bugid = bugid.split(':')[0].split('_')
    try:
        finished = subprocess.run(['defects4j', 'checkout', '-p', bugid[0], '-v', '{}b'.format(bugid[1]), '-w', './d4j_buggy/{}_{}'.format(bugid[0], bugid[1])], capture_output=True)
        finished.check_returncode()
    except Exception as E:
        with open('./exception_{}'.format(bugid), 'w') as f:
            try:
                f.write(str(E))
            except:
                try:
                    f.write(E.stderr)
                except Exception as F:
                    print(F)
            f.write(finished.stdout.decode("utf-8"))
            f.write(finished.stderr.decode("utf-8"))
joblib.Parallel(n_jobs=14)(joblib.delayed(task)(i) for i in tqdm.tqdm(waitlist))
