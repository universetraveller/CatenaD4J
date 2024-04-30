import spliter
import json
import tqdm
import os
import logging
import traceback
import sys
class filelog:
    def __init__(self, filename):
        self.file = open(filename, 'a')
    def log(self, cont, console=False):
        self.file.write('{}\n'.format(cont))
        self.file.flush()
        if console:
            print(cont)
    def end(self):
        self.file.close()
def run(waitlist):
    logger = filelog('./running/log5')
    root = {}
    check_list = []
    exception_list = []
    for i in tqdm.tqdm(waitlist):
        logger.log('-'*20)
        logger.log('Run: {}'.format(i))
        root[i] = {}
        if i == 'Time_21':
            continue
        path = '{}/{}/{}/'.format(path2buggy, i, database.get(i).get('dir.src.tests'))
        failing_tests = database.get(i).get('tests.trigger')
        root[i]['failing_tests'] = failing_tests
        for failing_test in failing_tests:
            temp = {}
            logger.log('@'*3)
            logger.log('Split test: {}'.format(failing_test))
            test = failing_test.split('::')
            path2file = '{}/{}.java'.format(path, test[0].replace('.', '/'))
            logger.log('file: {}'.format(path2file))
            temp['file_path'] = '{}/{}.java'.format(database.get(i).get('dir.src.tests'), test[0].replace('.', '/'))
            try:
                fti, check = spliter.process_test_node_v2(path2file, test[1])
            except Exception as E:
                logger.log('# Exception:\n{}\n---'.format(traceback.format_exc()))
                exception_list.append('{}@{}'.format(i, failing_test))
                continue
            if len(check) > 0:
                check_list.append('{}@{}'.format(i, failing_test))
                temp['check'] = check
                logger.log('# check: {}'.format('\n'.join(check)))
            fti.split()
            logger.log(str(fti))
            temp['Instance'] = str(fti)
            temp['source'] = fti.source
            temp['name'] = fti.name
            temp['begin'] = str(fti.begin)
            temp['end'] = str(fti.end)
            temp['begin_line_no'] = fti.begin.row
            temp['end_line_no'] = fti.end.row
            temp['child'] = []
            for child_of_it in fti.child:
                temp['child'].append(str(child_of_it))
            temp['splited'] = fti.splited
            temp['func'] = {}
            for idx in range(len(fti.splited)):
                new = fti.splited[idx]
                temp['func'][idx] = new
                logger.log('---\n{}\n---'.format(new))
            root[i][failing_test] = temp
    logger.log('---\ncheck list:')
    for i in check_list:
        logger.log(i)
    logger.log('---\nexception list:')
    for i in exception_list:
        logger.log(i)
    return root
if __name__ == '__main__':
    _debug = len(sys.argv) > 3
    with open('./2toMore', 'r') as f:
        waitlist = f.read().splitlines()
    path2d4j = '/root/defects4j'
    if len(sys.argv) > 1:
        path2d4j = sys.argv[1]
    path2buggy = '/tmp'
    if len(sys.argv) > 2:
        path2buggy = sys.argv[2]
    with open('./database.json', 'r') as f:
        database = json.load(f)
    if _debug:
        run([sys.argv[3]])
        exit()
    root = run(waitlist)
    with open('./running/res5.json', 'w') as f:
        f.write(json.dumps(root, indent=4))
