import runner
import util
import os
import traceback
import json
import joblib
import tqdm
import time
import argparse
from collections import ChainMap
ex_bugs = ['Cli_6','Collections_20','Collections_24','Collections_1', \
           'Collections_21','Collections_2','Collections_5','Collections_10', \
           'Collections_6','Collections_15','Collections_7','Collections_17', \
           'Collections_22','Collections_8','Collections_18', 'Collections_19', \
           'Collections_4', 'Time_21', 'Lang_2', 'Closure_63', 'Closure_93']
PATCHES = None
def task(bug_id, info, method):
    if os.path.exists('./working/{}'.format(bug_id)):
        print('clean up: ./working/{}'.format(bug_id))
        util.cleanup('./working/{}'.format(bug_id), [''])
    os.makedirs('./working/{}'.format(bug_id))
    logger = util.SimpleLogger('./working/{}/log'.format(bug_id))    
    tests_data = method
    bug_id_saved = bug_id
    modify_file = False
    try:
        if bug_id in ex_bugs:
            raise Exception('{} is a deprecated bug'.format(bug_id))
        if bug_id in ('Math_97', 'Lang_17'):
            raise Exception(f'{bug_id} would run forever with parallel')
        info = info[bug_id]
        method = method[bug_id]
        bug_id = bug_id.split('_')
        with open('{}/{}/{}.json'.format(PATCHES, bug_id[0], bug_id[1]), 'r') as f:
            patch = json.load(f)
        generator = runner.Generator(bug_id[0], bug_id[1])
        generator.set_logger(logger)
        generator.set_info_base(info)
        generator.set_patch_base(patch)
        generator.set_method_base(method)
        generator.run()
        modify_file = generator.modify_file
    except Exception as E:
        logger.log('EXCEPTION: Inside Exception {}'.format(E))
        logger.log(traceback.format_exc())
        print('EXCEPTION: Inside Exception {}'.format(E))
        print(traceback.format_exc())
        with open('./exceptions/EXCEPTION_{}'.format('_'.join(bug_id)), 'w') as f:
            f.write(traceback.format_exc())
    logger.end()
    if modify_file:
        return {bug_id_saved: tests_data[bug_id_saved]}, modify_file
    else:
        return {}, modify_file

def parallel(bug_ids, js1, js2, tests, n_jobs):
    results = joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(task)(bug_id, js1, js2) for bug_id in tqdm.tqdm(bug_ids))
    # modify res5.json if necessary
    modify_file = any([res[1] for res in results])
    if modify_file:
        js2_results = [res[0] for res in results]
        js2_results.append(js2)
        js2_results = [d for d in js2_results if d]
        js2 = dict(ChainMap(*js2_results))
        with open(tests, 'w') as f:
            f.write(json.dumps(js2, indent=4))
def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bug-id', required=False)
    parser.add_argument('-m', '--database', default='./database.json', required=False)
    parser.add_argument('-t', '--tests', default='./res5.json', required=False)
    parser.add_argument('-p', '--patches', default='./patches', required=False)
    parser.add_argument('-n', '--n-jobs', type=int, default=15, required=False)
    return parser.parse_args()

def main():
    args = init_args()
    with open(args.database, 'r') as f:
        js1 = json.load(f)
    with open(args.tests, 'r') as f:
        js2 = json.load(f)
    with open('./2toMore', 'r') as f:
        bug_ids = [args.bug_id] if args.bug_id is not None else f.read().splitlines()
    if not os.path.exists('./exceptions/'):
        os.makedirs('./exceptions/')
    global PATCHES
    PATCHES = args.patches
    parallel(bug_ids, js1, js2, args.tests, args.n_jobs)

def run_time(runnable):
    start = time.time()
    runnable()
    return time.time() - start

if __name__ == '__main__':
    print(f'Real time: {run_time(main)}s')
