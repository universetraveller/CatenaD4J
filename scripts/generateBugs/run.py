import runner
import util
import os
import traceback
import json
import joblib
import tqdm
import time
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
def parallel(bug_ids, js1, js2):
    joblib.Parallel(n_jobs=15)(joblib.delayed(task)(bug_id, js1, js2) for bug_id in tqdm.tqdm(bug_ids))
def main():
    with open('./database.json', 'r') as f:
        js1 = json.load(f)
    with open('./res5.json', 'r') as f:
        js2 = json.load(f)
    with open('./2toMore', 'r') as f:
        bug_ids = f.read().splitlines()
    if not os.path.exists('./exceptions/'):
        os.makedirs('./exceptions/')
    _debug = False
    if _debug:
        #bug_ids = ['Lang_34', 'Math_44']
        '''
        for bug_id in bug_ids:
            task(bug_id, js1, js2)
        '''
        '''
        bug_ids =  ['Lang_10', 'Math_29', 'Math_22', 'Math_12', 'Lang_8', 'Math_102', 'Math_43']
        parallel(bug_ids, js1, js2)
        '''
        bug_ids =  ['Lang_34']
        parallel(bug_ids, js1, js2)
    else:
        parallel(bug_ids, js1, js2)

def run_time(runnable):
    start = time.time()
    runnable()
    return time.time() - start
if __name__ == '__main__':
    print(f'Real time: {run_time(main)}s')
