from .util import read_file, get_project_cache, printc
from pathlib import Path
from .loaders import get_project_loader
import re
from .exceptions import Defects4JError
from .loaders import is_valid_loader_name
from shutil import move as move_file

def _get_from_project(proj, bid, context, folder, suffix):
    file_name = bid if suffix is None else f'{bid}{suffix}'
    path = Path(context.d4j_home, context.d4j_rel_projects, proj, folder, file_name)
    content = read_file(path)
    if content is None:
        raise Defects4JError(f'Failed to read {path}')
    # performance overhead induced here if this function is used for export command
    # but this overhead is minimal
    return content.strip().splitlines()

def get_classes_modified(proj, bid, context):
    return _get_from_project(proj, bid, context, 'modified_classes', '.src')

def get_classes_relevant(proj, bid, context):
    return _get_from_project(proj, bid, context, 'loaded_classes', '.src')

def get_tests_relevant(proj, bid, context):
    return _get_from_project(proj, bid, context, 'relevant_tests', None)

_failing_test_parser = re.compile(r'--- ([^:]+)(?:::([^:]+))?')
def parse_failing_tests(lines, full=False):
    '''
        From defects4j/framework/core/Utils.pm get_failing_tests
    '''
    if full:
        classname_matcher = re.compile(r'(?:.*\.)?([^.]+)')

    idx = -1
    
    # why do not use set here? 
    # though the failing tests seem to be naturally not duplicated
    classes = []
    methods = []
    asserts = {}

    _max = len(lines) - 1
    while idx < _max:
        idx += 1
        line = lines[idx]

        m = _failing_test_parser.match(line)
        if not m:
            continue

        clazz = m.group(1)
        method = m.group(2)

        if method:
            # TODO replace using # (junit style)
            failing_test = f'{clazz}::{method}'
            methods.append(failing_test)

            if not full or idx >= _max:
                continue

            reason = lines[idx + 1]

            m = classname_matcher.match(reason)
            if not m:
                raise Defects4JError(f'Couldn\'t determine class name from {reason}')

            assert_matcher = re.compile(rf'{m.group(1)}\.java:(\d+)')

            if not 'junit.framework.AssertionFailedError' in reason:
                continue

            while idx < _max:
                idx += 1

                line = lines[idx]

                if '---' not in line:
                    break

                if 'junit.' in line:
                    continue

                m = assert_matcher.match(line)
                if not m:
                    continue
                asserts[failing_test] = m.group(1)
        else:
            classes.append(clazz)

    return classes, methods, asserts

def get_tests_trigger(proj, bid, context):
    content = _get_from_project(proj, bid, context, 'trigger_tests', None)
    a, b, c = parse_failing_tests(content.splitlines())
    return a + b

def read_active_bugs(context, proj):
    path = Path(context.d4j_home, context.d4j_rel_projects, proj, 'active-bugs.csv')
    content = read_file(path)
    if content is None:
        raise Defects4JError(f'Cannot open active bugs file {path}')
    
    lines = content.splitlines()

    bugs = {}

    for line in lines[1:]:
        line = line.split(',')
        bug = {
            'buggy': line[1],
            'fixed': line[2],
            'report': line[3],
            'link': line[4]
        }
        bugs[line[0]] = bug

    return bugs

def lookup_revision_id(bugs, bid, is_buggy):
    if bid not in bugs:
        raise Defects4JError(f'Version id does not exist: {bid}')

    return bugs[bid]['buggy'] if is_buggy else bugs[bid]['fixed']

vid_parser = re.compile(r'^([1-9][0-9]*)([bf])$')
def parse_vid(vid):
    '''
        Original regex version are slower than version using isnumeric

        Performance testing: 1000 times for 30000 items checking

        regex: 7s

        vid_parser = re.compile(r'^(\d+)([bf])$')

        isnumeric: 4-5s

        bid, tag = vid[:-1], vid[-1]
        if bid.isnumeric() and tag in {'b', 'f'}:
            return bid, tag

        to ensure precision, use new regex version here
    '''
    m = vid_parser.match(vid)
    if m:
        return m.groups()

    raise Defects4JError(f'Wrong version_id: {vid} -- expected {vid_parser.pattern}!')

def get_active_bugs(project, context):
    return get_project_cache(context.__d4j_cache__,
                             project,
                             'active-bugs',
                             read_active_bugs,
                             (context, project))

def get_revision_id(proj, bid, is_buggy, context):
    active_bugs = get_active_bugs(proj, context)
    return lookup_revision_id(active_bugs, bid, is_buggy)

def read_dir_layout(context, proj):
    path = Path(context.d4j_home, context.d4j_rel_projects, proj, 'dir-layout.csv')
    content = read_file(path)
    if content is None:
        raise Defects4JError(f'Cannot open {path}')
    
    lines = content.splitlines()

    dir_layout = {}

    for line in lines:
        line = line.split(',')
        dir_layout[line[0]] = (line[1], line[2])
    
    return dir_layout

def get_dir_layout(context, proj):
    return get_project_cache(context.__d4j_cache__,
                             proj,
                             'dir-layout',
                             read_dir_layout,
                             (context, proj))

def get_dir_src_cache(proj, bid, is_buggy, context):
    rev = get_revision_id(proj, bid, is_buggy, context)
    dir_layout = get_dir_layout(context, proj)
    return dir_layout[rev] if rev in dir_layout else None

def get_dir_src_classes(proj, bid, wd, is_buggy, context, loader=None):
    dir_src = get_dir_src_cache(proj, bid, is_buggy, context)

    if dir_src is not None:
        return dir_src[0]

    project_loader = loader or get_project_loader(proj)(context)

    return project_loader.src_layout

def get_dir_src_tests(proj, bid, wd, is_buggy, context, loader=None):
    dir_src = get_dir_src_cache(proj, bid, is_buggy, context)

    if dir_src is not None:
        return dir_src[1]

    project_loader = loader or get_project_loader(proj)(context)

    return project_loader.test_layout

def check_d4j_vid(project: str, id: str, context):
    # instead of checking file system, check if there is a loader for the project
    if not is_valid_loader_name(project):
        path = Path(context.d4j_home, context.d4j_rel_projects)
        raise Defects4JError(f'Error: {project} is not a valid project name; '
                             f'full list could be found at {str(path)} directory')

    if not id in get_active_bugs(project, context):
        path = Path(context.d4j_home,
                    context.d4j_rel_projects,
                    project,
                    'active-bugs.csv')
        raise Defects4JError(f'Error: {project}-{id} is not a active bug id; '
                             f'full list could be found at {str(path)}')

class FixTests:
    def exclude_test_classes(self, classes):
        pass

    def remove_assertions(self, methods, assertions):
        raise NotImplementedError(f'Should not reach here')

    def write_files(self):
        for file in self.files:
            # moved backup logic here 
            # optimize to copy-on-write
            bak = file.with_name(file.name + '.bak')
            if not bak.is_file():
                # directly remove the original file to avoid write behavior
                # if the process is broken the original file
                # would not exist, but usually we should checkout
                # again even we use copy2 here
                move_file(file, bak)

            with file.open('w') as f:
                f.write(self.files[file])

    def read_file(self, file: Path):
        if file in self.files:
            return True

        content = read_file(file)
        if content is None:
            return False

        self.files[file] = content
        # TODO detect junit4
        return True


    def remove_test_method(self, file: Path, clz: str, met: str):
        # TODO
        pass

    def __init__(self,
                 project,
                 bid,
                 wd,
                 is_buggy,
                 context,
                 *,
                 loader=None,
                 revision_id=None,
                 _except=set(),
                 verbose=False):
        '''
            Implementation of fix_tests function in defects4j/framework/core/Project.pm

            Defects4J only considers test classes whose name matches the directory
            while there are some exceptions in the real world.
        '''
        files = []

        base = Path(context.d4j_home,
                    context.d4j_d4j_rel_projects,
                    project)

        revision_id = revision_id or get_revision_id(project, bid, is_buggy, context)
        failing_tests = base / 'failing_tests' / revision_id
        files.append(failing_tests)

        dependent_tests = base / 'dependent_tests'
        files.append(dependent_tests)

        random_tests = base / 'random_tests'
        files.append(random_tests)

        # RM_ASSERTS environment variable in the original script
        # when it is called for checkout command it is not set forever
        # simply skip its implementation
        full = False

        classes = []
        methods = []
        assertions = []
        for file in files:
            # defects4j processes one line each iteration which induced extra checking
            # overhead that could avoid
            if not file.is_file():
                continue
            # defects4j calls rm_broken_tests.pl here which is very slow
            # why defects4j doesn't just reuse code to parse failing tests here?
            file: Path
            with file.open() as f:
                lines = f.read().splitlines()

            a, b, c = parse_failing_tests(lines, full)
            classes.extend(a)
            methods.extend(b)
            assertions.extend(c)

        if not methods:
            # defects4j does not implement this function
            self.exclude_test_classes(classes)

        if _except:
            # never reach here when called for checkout command
            methods = list(set(methods) - _except)
            
        if full:
            # never reach here when called for checkout command
            # defects4j record the full line and parse again which induced overhead
            # perl is not readable...
            # why expressions like $_ with bad readability are allowed?
            # unless ($RM_ASSERTS && _remove_assertion($class, $method)) {
            #     push(@method_list, $_);
            # }
            methods = self.remove_assertions(methods, assertions)
        
        self.files = {}
        self.junit4 = {}
        test_dir = get_dir_src_tests(project, bid, wd, is_buggy, context, loader)
        base_dir = Path(wd, test_dir)
        for method in methods:
            clz, _, met = method.partition('::')
            f = base_dir / (clz.replace('.', '/') + '.java')
            if not self.read_file(f):
                if verbose:
                    # use unix line separator directly
                    # because the code here are not expected to reach
                    printc(f'fix_tests: {str(f)} does not exist -> SKIP ({method})\n')
                continue
                
            self.remove_test_method(f, clz, met)
        
        self.write_files()

fix_tests = FixTests