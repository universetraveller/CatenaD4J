import runner
import util
import os
import traceback
import json
import joblib
import tqdm
import time
import argparse
def task(bug_id, info, method):
    if os.path.exists('./working/{}'.format(bug_id)):
        print('clean up: ./working/{}'.format(bug_id))
        util.cleanup('./working/{}'.format(bug_id), [''])
    os.makedirs('./working/{}'.format(bug_id))
    logger = util.SimpleLogger('./working/{}/log'.format(bug_id))
    try:
        if bug_id in ('Time_21', 'Lang_2', 'Closure_63', 'Closure_93'):
            raise Exception('{} is a deprecated bug'.format(bug_id))
        if bug_id in ('Math_97', 'Lang_17'):
            raise Exception(f'{bug_id} would run forever with parallel')
        info = info[bug_id]
        method = method[bug_id]
        bug_id = bug_id.split('_')
        with open('./patches/{}/{}.json'.format(bug_id[0], bug_id[1]), 'r') as f:
            patch = json.load(f)
        generator = runner.Generator(bug_id[0], bug_id[1])
        generator.set_logger(logger)
        generator.set_info_base(info)
        generator.set_patch_base(patch)
        generator.set_method_base(method)
        generator.run()
    except Exception as E:
        logger.log('EXCEPTION: Inside Exception {}'.format(E))
        logger.log(traceback.format_exc())
        print('EXCEPTION: Inside Exception {}'.format(E))
        print(traceback.format_exc())
        with open('./exceptions/EXCEPTION_{}'.format('_'.join(bug_id)), 'w') as f:
            f.write(traceback.format_exc())
    logger.end()

def parallel(bug_ids, js1, js2, n_jobs):
    joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(task)(bug_id, js1, js2) for bug_id in tqdm.tqdm(bug_ids))

def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bug-id', required=False)
    parser.add_argument('-n', '--n-jobs', type=int, default=15, required=False)
    return parser.parse_args()

def main():
    args = init_args()
    with open('./database.json', 'r') as f:
        js1 = json.load(f)
    with open('./res5.json', 'r') as f:
        js2 = json.load(f)
    with open('./2toMore', 'r') as f:
        bug_ids = f.read().splitlines()
    if not os.path.exists('./exceptions/'):
        os.makedirs('./exceptions/')
    if args.bug_id is not None:
        bug_ids =  [args.bug_id]
    parallel(bug_ids, js1, js2, args.n_jobs)

def run_time(runnable):
    start = time.time()
    runnable()
    return time.time() - start

if __name__ == '__main__':
    print(f'Real time: {run_time(main)}s')
