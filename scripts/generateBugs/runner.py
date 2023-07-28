import util
import ProjectManager as PM
import json
import os
import timeout_decorator

# status
COMMON = 0
UNSELECTABLE = 1
UNUSABLE = 2
class Hunk:
    def __init__(self, hunk_pattern:list):
        self.hunk_pattern = hunk_pattern
    def set_failing_tests(self, fts):
        self.failing_tests = fts
    def set_status(self, s):
        self.status = s
    def count(self):
        return self.hunk_pattern.count(True)
    def isSubHunkOf(self, other):
        if not len(other.hunk_pattern) == len(self.hunk_pattern):
            raise ValueError('Pattern length not equals')
        if other.hunk_pattern == self.hunk_pattern:
            raise ValueError('Unexpected equality of hunks')
        for idx, bl in enumerate(other.hunk_pattern):
            if self.hunk_pattern[idx] and not bl:
                return False
        return True
def allSame(fp, t):
    for i in fp:
        if not i == t:
            return False
    return True
_generator_run_timeout=3600
class Generator:
    def __init__(self, proj, bug_id):
        self.proj = proj
        self.bug_id = bug_id
        self.setting = 4
    def log(self, obj, console=True):
        if console:
            print('{}'.format(obj))
        self.logger.log('{}'.format(obj))
    def set_logger(self, logger):
        self.logger = logger
        self.setting -= 1
    def set_info_base(self, ib:dict):
        self.info_base = ib
        self.setting -= 1
    def set_patch_base(self, pb:dict):
        self.patch_base = pb
        self.setting -= 1
    def set_method_base(self, mb:dict):
        self.method_base = mb
        self.setting -= 1
    @timeout_decorator.timeout(_generator_run_timeout, timeout_exception=TimeoutError, exception_message='generator.run() timeout')
    def run(self):
        if self.setting > 0:
            raise ValueError('Not completed setting')
        self.log('---\nBegin generate bug_id: {}_{}'.format(self.proj, self.bug_id))
        hunk_num = self.patch_base['num_of_hunks']
        self.log('num_of_hunks: {}'.format(hunk_num))
        self.log(f'timeout for running: {_generator_run_timeout}')
        if hunk_num == 1:
            self.log('Skip')
        else:
            self.path = './working/data/{}_{}'.format(self.proj, self.bug_id)
            self.log('use working dir: {}'.format(self.path))
            if os.path.exists(self.path):
                self.cleanup()
            self.checkout()
            self.build_dir = []
            self.build_dir.append('{}/{}'.format(self.path, self.info_base['dir.bin.classes']))
            self.build_dir.append('{}/{}'.format(self.path, self.info_base['dir.bin.tests']))
            self.log('build dir: {}'.format(self.build_dir))
            self.hunk_num = hunk_num
            self.hunks = []
            self.newBugs = {}
            self.initFM()
            self._run()
            self.analyze('./working/{}_{}'.format(self.proj, self.bug_id))
    def checkout(self):
        self.log('Try to checkout {}_{}'.format(self.proj, self.bug_id))
        result = util.runCommand(['defects4j', 'checkout', '-p', str(self.proj), '-v', '{}b'.format(self.bug_id), '-w', self.path])
        if not result[0]:
            self.log('Failed to checkout:\n{}'.format(result[2]))
            raise ValueError('Could not checkout {}_{}'.format(self.proj, self.bug_id))
    def cleanup(self):
        util.cleanup(self.path, [''])
        self.log('clean up: {}'.format(self.path))
    def initFM(self):
        self.log('init FileManager')
        self.FM = PM.FileManager.FileManager(self.path, PM.FileTypes.EditCacheFile)
        for i in range(self.hunk_num):
            patch_hunk = self.patch_base[str(i)]
            self.log('trace file: {}'.format(patch_hunk['file_name']))
            self.FM.trace_file(patch_hunk['file_name'], 'h{}'.format(str(i)))
    def _run(self):
        self.useNewFailingTests()
        tasks = util.getFixPattern(self.hunk_num)
        start_time = 
        for task in tasks:
            self.taskSingleHunk(task)
    def hunk_block_to_edit(self, hb):
        patch_type = hb['patch_type']
        if patch_type == 'insert':
            self.log('insert before {} with {}'.format(hb['next_line_no'], hb['replaced_with']))
            return PM.EditTypes.createLineInsert(hb['next_line_no'], hb['replaced_with'])
        elif patch_type == 'delete':
            self.log('delete from {} with range {}'.format(hb['from_line_no'], hb['to_line_no']-hb['from_line_no']+1))
            return PM.EditTypes.createLineDelete(hb['from_line_no'], hb['to_line_no']-hb['from_line_no']+1)
        elif patch_type == 'replace':
            self.log('replace from {} with range {} to\n{}'.format(hb['from_line_no'], hb['to_line_no']-hb['from_line_no']+1, hb['replaced_with']))
            return PM.EditTypes.createLineReplace(hb['from_line_no'], hb['replaced_with'], hb['to_line_no']-hb['from_line_no']+1)
        else:
            self.log('patch type {} is unknown'.format(patch_type))
            raise ValueError('unk patch_type')
    def taskSingleHunk(self, fix_pattern):
        task_edits = []
        self.log('pattern: {}'.format(util.getLabel(fix_pattern)))
        for i in range(len(fix_pattern)):
            if fix_pattern[i]:
                self.log('try to fix hunk: {}'.format(i))
                hunk_block = self.patch_base[str(i)]
                task_edits.append(PM.FileManager.FileEdit(hunk_block['file_name'], self.hunk_block_to_edit(hunk_block)))
        for i in task_edits:
            self.FM.apply_edit(i)
        self.FM.write_to_file()
        self.FM.reset()
        self.log('patches are written to file')
        self.log('running tests...')
        failure = util.get_failing_tests(self.path, self.build_dir)
        if failure.tag == util.CMDFAIL:
            if 'see the compiler error output for details.' in failure.details or 'Compile failed' in  failure.details:
                self.log('seems testing failed, see output:\n<OUTPUT>\n{}\n<ENDOUTPUT>'.format('<Common Compile Failed>'))
            elif 'time out after' in failure.details:
                self.log('EXCEPTION: tests time out')
                # can raise an error there for pure testing
                raise TimeoutError("tests time out")
            else:
                self.log('seems testing failed, see output:\n<OUTPUT>\n{}\n<ENDOUTPUT>'.format(failure.details))
            if allSame(fix_pattern, False) or allSame(fix_pattern, True):
                self.log('ERROR: Looks like unexpected compilation failed, may be methods are incorrectly split')
                raise Exception('task should end')
            thisHunk = Hunk(fix_pattern)
            thisHunk.set_status(UNUSABLE)
            thisHunk.set_failing_tests(set())
            self.hunks.append(thisHunk)
        elif failure.tag == util.D4J_TEST:
            self.log('used time: {}'.format(failure.details))
            self.log('Failing tests: {}'.format(failure.number))
            for oneFT in failure.names:
                self.log('\t{}'.format(oneFT))
            if allSame(fix_pattern, False):
                if failure.number == 0:
                    self.log('EXCEPTION: Failing number equals to 0 before fixing, should check')
                if len(set(failure.names) - self.virtualHunk.failing_tests) > 0:
                    self.log('EXCEPTION: Raising new failing tests before fixing, should check')
            if allSame(fix_pattern, True):
                if not failure.number == 0:
                    self.log('EXCEPTION: Could not pass after all fixed, should check')
            ftInHunk = set(failure.names)
            thisHunk = Hunk(fix_pattern)
            thisHunk.set_failing_tests(ftInHunk)
            if thisHunk.count() == 0:
                thisHunk.set_status(UNSELECTABLE)
            else:
                # patch 29.7.2023 for new requirement that keeps signle hunk bugs
                thisHunk.set_status(COMMON)
                '''
                if thisHunk.count() == 1:
                    thisHunk.set_status(UNSELECTABLE)
                else:
                    thisHunk.set_status(COMMON)
                '''
                firstHunk = self.hunks[0]
                #firstHunk = self.virtualHunk
                newFT = thisHunk.failing_tests - firstHunk.failing_tests
                if not len(newFT) == 0:
                    self.log('Includes new failing tests, set to unusable')
                    thisHunk.set_status(UNUSABLE)
                elif thisHunk.count() > 1:
                    canFix = firstHunk.failing_tests - thisHunk.failing_tests
                    for preHunk in self.hunks:
                        if preHunk.status >= UNUSABLE:
                            continue
                        if not preHunk.isSubHunkOf(thisHunk):
                            continue
                        preCanFix = firstHunk.failing_tests - preHunk.failing_tests
                        if len(preCanFix) == 0:
                            continue
                        canFix = canFix - preCanFix
                    self.log('Can independently fix {}'.format(list(canFix)))
                    if not len(canFix) == 0:
                        self.log('select new bug')
                        self.log('Pattern: {}'.format(util.getLabel(fix_pattern)))
                        self.log('new failing tests:\n{}'.format('\n'.join(list(canFix))))
                        self.newBugs[util.getLabel(fix_pattern)] = canFix
                    else:
                        self.log('Could not fix independently')
                        thisHunk.set_status(UNSELECTABLE)
                else:
                    # patch 29.7.2023
                    # single hunk fixed and contains no new failing tests indicates 2 cases:
                    # failing tests are same as firstHunk 
                    # or part of failing tests of firstHunk are fixed
                    if len(thisHunk.failing_tests) == len(firstHunk.failing_tests):
                        self.log('No new failing tests but only 1 hunk')
                        thisHunk.set_status(UNSELECTABLE)
                    else:
                        assert len(thisHunk.failing_tests) < len(firstHunk.failing_tests)
                        self.log('select new bug')
                        self.log('Pattern: {}'.format(util.getLabel(fix_pattern)))
                        self.log('new failing tests:\n{}'.format('\n'.join(list(thisHunk.failing_tests))))
                        self.newBugs[util.getLabel(fix_pattern)] = thisHunk.failing_tests
            self.hunks.append(thisHunk)
        else:
            self.log('what tag it is? {}'.format(failure.tag))
            raise ValueError('what tag it is? {}'.format(failure.tag))
        self.log('processed: {}'.format(util.getLabel(fix_pattern)))
    def useNewFailingTests(self):
        self.log('trying to replace old failing tests')
        self.name_pattern = '{}$catena_{}'
        virtualFT = set()
        new_num = 0
        uFM = PM.FileManager.FileManager(self.path, PM.FileTypes.EditCacheFile)
        failing = self.method_base['failing_tests']
        ori_num = len(failing)
        file_names = set()
        edits = []
        for f in failing:
            # add original test
            virtualFT.add(f)
            if not f in self.method_base:
                self.log('NOTICE: skip {} for cannot find node in method_base'.format(f))
                continue
            block = self.method_base[f]
            new_num += len(block['splited'])
            if len(block['splited']) == 0:
                continue
            # has split tests, remove original for adding new ones
            virtualFT.remove(f)
            ori_num -= 1
            code_block = ' '.join(block['splited'])
            for idx in range(len(block['splited'])):
                newNameFT = self.name_pattern.format(f, idx).strip()
                # patch for flaky tests of Lang_34
                if newNameFT.split('::')[1] in ('testReflectionDoubleArrayArray$catena_2', 'testReflectionArrayArrayCycle$catena_1', 'testSimpleReflectionObjectCycle$catena_1'):
                    self.log('NOTICE: patch for flaky tests of Lang_34, rename {}'.format(newNameFT))
                    newNameFT = newNameFT.replace('$', '_')
                virtualFT.add(newNameFT)
                if not newNameFT.split('::')[1] in code_block:
                    self.log('EXCEPTION: test {} named incorrectly'.format(newNameFT))
            #fp = block['file_path'].replace('/root/workbench/exportInfo/d4j_buggy/{}_{}/'.format(self.proj, self.bug_id), '')
            fp = block['file_path']
            file_names.add(fp)
            edits.append(PM.FileManager.FileEdit(fp, PM.EditTypes.createLineReplace(block['begin_line_no'], code_block, block['end_line_no']-block['begin_line_no']+1)))
            self.log('edit: replace from {} range {} at {}'.format(block['begin_line_no'], block['end_line_no']-block['begin_line_no']+1, fp))
            self.log('to\n{}'.format(' '.join(block['splited'])), False)
        for i in file_names:
            self.log('trace file: {}'.format(i))
            uFM.trace_file(i)
        for i in edits:
            uFM.apply_edit(i)
        uFM.write_to_file()
        self.log('new test num: {}'.format(new_num))
        self.log('ori test num: {}'.format(ori_num))
        if not len(virtualFT) == new_num + ori_num:
            self.log('EXCEPTION: Lack some names after applying new failing tests')
        self.virtualHunk = Hunk([])
        self.virtualHunk.set_status(UNSELECTABLE)
        self.virtualHunk.set_failing_tests(virtualFT)
        self.new_num = new_num
        self.ori_num = ori_num
    def analyze(self, path):
        num1 = 0
        for i in self.hunks:
            if i.status == COMMON:
                num1 += 1
        num2 = 0
        for i in self.newBugs:
            num2 += 1
        if num1 != num2:
            self.log('EXCEPTION: Broken bugs finding')
            self.log('Find {} new bugs from inside hunks'.format(num1))
            self.log('Find {} new bugs from checking'.format(num2))
        else:
            self.log('Find {} new bugs'.format(num2))
        root = {}
        root['original'] = self.patch_base
        root['method'] = self.method_base
        for i in self.newBugs:
            root[i] = {}
            root[i]['failing_tests']  = list(self.newBugs[i])
        with open('{}/newBugs.json'.format(path), 'w') as f:
            f.write(json.dumps(root, indent=4))
