from .util import read_file, get_project_cache, printc, write_file
from pathlib import Path
from .loaders import get_project_loader, is_valid_loader_name
import re
from .exceptions import Defects4JError
from shutil import move as move_file

def get_project_dir(project, bid, context, folder='', suffix=None):
    file_name = bid if suffix is None else f'{bid}{suffix}'
    return Path(context.d4j_home,
                context.d4j_rel_projects,
                project,
                folder,
                file_name)

def _get_from_project(proj, bid, context, folder, suffix):
    path = get_project_dir(proj, bid, context, folder, suffix)
    content = read_file(path)
    if content is None:
        raise Defects4JError(f'Failed to read {path}')
    # performance overhead induced here if this function is used for export command
    # but this overhead is minimal
    return content.strip()

def get_classes_modified(proj, bid, context):
    return _get_from_project(proj, bid, context, 'modified_classes', '.src').splitlines()

def get_classes_relevant(proj, bid, context):
    return _get_from_project(proj, bid, context, 'loaded_classes', '.src').splitlines()

def get_tests_relevant(proj, bid, context):
    return _get_from_project(proj, bid, context, 'relevant_tests', None).splitlines()

def get_patch_dir(project, bid, context, patch_type):
    return get_project_dir(project, bid, context, 'patches', f'.{patch_type}.patch')

def get_src_patch_dir(project, bid, context):
    return get_patch_dir(project, bid, context, 'src')
    
def get_test_patch_dir(project, bid, context):
    return get_patch_dir(project, bid, context, 'test')

def get_src_patch(project, bid, context):
    return _get_from_project(project, bid, context, 'patches', '.src.patch')

def get_test_patch(project, bid, context):
    return _get_from_project(project, bid, context, 'patches', '.test.patch')

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
    path = get_project_dir(proj, 'active-bugs.csv', context)
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
        The original regex version is slower than version using isnumeric

        Performance testing: 1000 times for 30000 items checking

        regex: 7s

        isnumeric: 4-5s

        to ensure the precision, use new regex pattern here
    '''
    m = vid_parser.match(vid)
    if m:
        return m.groups()

    raise Defects4JError(f'Wrong version_id: {vid} -- expected {vid_parser.pattern}!')

def get_active_bugs(project, context):
    return get_project_cache(context.d4j_cache,
                             project,
                             'active-bugs',
                             read_active_bugs,
                             (context, project))

def get_revision_id(proj, bid, is_buggy, context):
    active_bugs = get_active_bugs(proj, context)
    return lookup_revision_id(active_bugs, bid, is_buggy)

def lookup_vid(active_bugs, revision_id):
    # is there faster way to find vid for a revision_id
    for bid in active_bugs:
        line = active_bugs[bid]
        if line['buggy'] == revision_id:
            return bid, True
        elif line['fixed'] == revision_id:
            return bid, False

    raise Defects4JError(f'Version id does not exist for revision id {revision_id}')
    
def get_vid(project, revision_id, context):
    active_bugs = get_active_bugs(project, context)
    return lookup_vid(active_bugs, revision_id)

def read_dir_layout(context, proj):
    path = get_project_dir(proj, 'dir-layout.csv', context)
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
    return get_project_cache(context.d4j_cache,
                             proj,
                             'dir-layout',
                             read_dir_layout,
                             (context, proj))

def get_dir_src_cache(proj, bid, is_buggy, context):
    rev = get_revision_id(proj, bid, is_buggy, context)
    dir_layout = get_dir_layout(context, proj)
    return dir_layout[rev] if rev in dir_layout else None

def get_dir_src_classes(proj, bid, is_buggy, context, loader=None):
    dir_src = get_dir_src_cache(proj, bid, is_buggy, context)

    if dir_src is not None:
        return dir_src[0]

    project_loader = loader or get_project_loader(proj)(context)

    return project_loader.src_layout

def get_dir_src_tests(proj, bid, is_buggy, context, loader=None):
    dir_src = get_dir_src_cache(proj, bid, is_buggy, context)

    if dir_src is not None:
        return dir_src[1]

    project_loader = loader or get_project_loader(proj)(context)

    return project_loader.test_layout

def check_d4j_vid(project: str, id: str, context):
    # instead of checking file system, check if there is a loader for the project
    if not is_valid_loader_name(project):
        path = get_project_dir(project, '', context)
        raise Defects4JError(f'Error: {project} is not a valid project name; '
                             f'full list could be found at {str(path)} directory')

    if not id in get_active_bugs(project, context):
        path = get_project_dir(project, 'active-bugs.csv', context)
        raise Defects4JError(f'Error: {project}-{id} is not an active bug id; '
                             f'full list could be found at {str(path)}')

class JavaRegex:
    def __init__(self):
        self.HexDigit = r'[0-9a-fA-F]'
        self.EscapeSequence = fr'\\(?:(?:u005c)?(?:[btnfr"i\'\\]|(?:[0-3]?[0-7])?[0-7])|u{self.HexDigit}{{4}})'
        self.COMMENT = r'/\*.*?\*/'
        self.LINE_COMMENT = r'//[^\r\n]*'
        self.CHAR_LITERAL = fr"'(?:[^'\\\r\n]|{self.EscapeSequence})'"
        self.STRING_LITERAL = fr'"(?:[^"\\\r\n]|{self.EscapeSequence})*"'
        self.LINE_COMMENT_PATTERN_STRING = f'({self.LINE_COMMENT})|({self.STRING_LITERAL})'
        self.COMMENT_PATTERN_STRING = f'({self.COMMENT})|{self.LINE_COMMENT_PATTERN_STRING}'
        self.STRING_LIKE_STRING = f'{self.COMMENT_PATTERN_STRING}|({self.CHAR_LITERAL})'
        self.NON_LINEBREAK = re.compile(r'[^\r\n]')
    
    def replace_non_linebreak_characters(self, s, replacement):
        return self.NON_LINEBREAK.sub(replacement, s)

    def _replacement_for_comments(self, m):
        # using \n seems to be ok
        # not required to change to linesep
        s = m.group(1)
        if s:
            # block comment
            return '/*' + self.replace_non_linebreak_characters(s[2:-2], ';') + '*/'
        s = m.group(3)
        if s:
            # string literal
            return s
        s = m.group(0)
        # line comment
        return '//' + ';' * (len(s) - 2)

    def _replacement_for_string_like(self, m):
        s = m.group(1)
        if s:
            # block comment
            return '/*' + self.replace_non_linebreak_characters(s[2:-2], ';') + '*/'
        s = m.group(3)
        if s:
            # string literal
            return '"' + ';' * (len(s) - 2) + '"'
        s = m.group(4)
        if s:
            # character literal
            return '\'' + ';' * (len(s) - 2) + '\''
        s = m.group(0)
        # line comment
        return '//' + ';' * (len(s) - 2)

    def remove_comments(self, s):
        if not hasattr(self, 'COMMENT_PATTERN'):
            self.COMMENT_PATTERN = re.compile(self.COMMENT_PATTERN_STRING, re.S)
        return self.COMMENT_PATTERN.sub(self._replacement_for_comments, s)
    
    def remove_string_like(self, s):
        if not hasattr(self, 'STRING_LIKE_PATTERN'):
            self.STRING_LIKE_PATTERN = re.compile(self.STRING_LIKE_STRING, re.S)
        return self.STRING_LIKE_PATTERN.sub(self._replacement_for_string_like, s)


java_regex: JavaRegex = None
def get_java_regex():
    global java_regex
    if java_regex is None:
        java_regex = JavaRegex()
    return java_regex

def _get_flaky_test_files(project, bid, is_buggy, context, revision_id=None):
    files = []

    base = get_project_dir(project, '', context)

    revision_id = revision_id or get_revision_id(project, bid, is_buggy, context)
    failing_tests = base / 'failing_tests' / revision_id
    files.append(failing_tests)

    dependent_tests = base / 'dependent_tests'
    files.append(dependent_tests)

    random_tests = base / 'random_tests'
    files.append(random_tests)

    return files

def get_flaky_test_files(project, bid, is_buggy, context, revision_id=None):
    return get_project_cache(context.d4j_cache,
                             project,
                             'flaky_test_files',
                             _get_flaky_test_files,
                             (project, bid, is_buggy, context, revision_id))

def get_flaky_tests(project,
                    bid,
                    is_buggy,
                    context,
                    *,
                    revision_id=None,
                    full=False):
    files = get_flaky_test_files(project, bid, is_buggy, context, revision_id)
    classes = set()
    methods = set()
    assertions = set()
    for file in files:
        # defects4j processes one line each iteration which induced extra checking
        # overhead that could avoid
        if not file.is_file():
            continue
        # defects4j calls rm_broken_tests.pl here which is very slow
        # why defects4j doesn't just reuse code to parse failing tests here?
        lines = read_file(file).splitlines()

        a, b, c = parse_failing_tests(lines, full)
        classes.update(a)
        methods.update(b)
        assertions.update(c)

    return classes, methods, assertions

class FixTests:
    '''
        Implementation of fix_tests function in defects4j/framework/core/Project.pm

        Defects4J only considers test classes whose name matches the directory
        while there are some exceptions in the real world.

        Defects4J's version will add redundant comments in some cases while this
        implementation will not
        Performance analysis:
            average elapsed time of 100 runs
            Chart: 4.80 ms
            Lang: 6.46 ms
            Math: 6.38 ms
            Time: 15.08 ms
            Mockito: 9.40 ms
            Closure: 7.43 ms
    '''
    @classmethod
    def find_keyword(cls, keyword: str, content: str):
        index = 0

        kw_len = len(keyword)
        content_len = len(content)

        while True:
            index = content.find(keyword, index)
            if index == -1:
                return -1

            if index > 0:
                # check previous character
                # ensure the keyword is not in a identifier
                pch: str = content[index - 1]
                if pch.isalnum() or pch in ('_', '$'):
                    index += 1
                    continue
            
            after = index + kw_len
            if after < content_len:
                nch = content[after]
                if nch.isalnum() or nch in ('_', '$'):
                    index += 1
                    continue
            
            return index

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

            write_file(file, self.files[file])

    def read_file(self, file: Path):
        if file in self.files:
            return True

        content = read_file(file)
        if content is None:
            return False

        self.files[file] = content
        # TODO could try to use a simple parser and check its performance
        noc = self.regex.remove_string_like(content)
        self.noc_files[file] = noc

        return True


    def remove_test_method(self, file: Path, clz: str, met: str):
        # defects4j uses regex to catch the method rather than ast
        # and symbol resolver, which will cause inaccurate results,
        # for example, inherited methods could not be found using this
        # approach
        # further, this way could not handle situation where code is in
        # block comments

        noc = self.noc_files[file]
        # TODO replace regex matching with simple parser
        # and check its performance
        # another option: com.sun.source, which is used for javac
        # .+ used by defects4j would encounter probolem
        # if the method is overridden in the same file
        # defects4j's implementation also could not handle annotations
        # with arguments or multiple lines code snippets
        # this regex is not suitable for parsing junit 5 tests
        _method = fr'\bpublic[\s\n]+void[\s\n]+{re.escape(met)}\(\s*\)'
        method_matcher = re.compile(_method, re.S)
        m = method_matcher.search(noc)
        if m:
            # found a test method
            # end is the next character to the match
            # using end + 1 will cause bug in Mockito that no space is between
            # method header and method body
            end = m.end()

            index = noc.find('{', end)
            if index == -1:
                raise Defects4JError(f'Could not extract method body for {clz}::{met}')

            # next to {
            length = len(noc)
            balance = -1
            while True:
                index += 1
                if index >= length:
                    raise Defects4JError(f'Could not extract method body for {clz}::{met}')
                ch = noc[index]
                if ch == '}':
                    balance += 1
                if ch == '{':
                    balance -= 1
                if balance == 0:
                    break
                
            # now index is at the closing }
            start = m.start()

            dummy = []

            # points to \n
            line_start = noc.rfind('\n', 0, start)

            # points to the first character of line
            pre_line_start = noc.rfind('\n', 0, line_start) + 1

            # not a good solution but to keep the same format
            # with defects4j's implementation
            pre_line = noc[pre_line_start:line_start]
            annotated = '@Test' in pre_line

            # points to the first character of line
            line_start += 1
            dummy_start = line_start

            # what called space in defects4j's code is not always empty string
            # because there may be annotations or even other code
            # and defects4j's implementation failed to catch them and directly adds
            # it before the inserted @Test annotation
            ori = self.files[file]
            space = ori[line_start:start]
            if annotated:
                # defects4j directly adds @Test
                # it may be used to avoid checking via annotation parameters
                dummy_start = pre_line_start
                # is it better to use ' ' * (start - line_start)?
                dummy.append(f'{space}@Test')
            dummy.append(f'{space}public void {met}() {{}}\n// Defects4J: flaky method')

            linebreak = noc.find('\n', start)

            # it is not good to directly comment the whole line
            # because there may be code before the method declaration
            # however, to keep the same format with defects4j
            # just follow their bad practice
            if annotated:
                dummy.append('// ' + pre_line)
            dummy.append('// ' + ori[line_start:linebreak])

            while True:
                pre = linebreak + 1
                linebreak = noc.find('\n', pre)
                if linebreak == -1:
                    break
                dummy.append('// ' + ori[pre:linebreak])
                if linebreak > index:
                    break

            dummy_end = linebreak
            dummy = '\n'.join(dummy)
            #print('==========')
            #print('dummy:')
            #print(dummy)
            #print('----------')
            #print('dummy origin:')
            #print(ori[dummy_start:dummy_end])
            #print('==========')
            self.noc_files[file] = noc[:dummy_start] + dummy + noc[dummy_end:]
            self.files[file] = ori[:dummy_start] + dummy + ori[dummy_end:]
            return

        # test method not found

        # self.junit4 only used here, why defects4j computes it when reading file?
        if file not in self.junit4:
            stop = self.find_keyword('class', noc)

            # what if there are org.junit.TestXXX?
            # or org.junit has proved that it is junit 4?
            self.junit4[file] = 'import org.junit.Test' in noc[:stop]

        # to keep the same format with defects4j
        override = '\n    @Test\n' if self.junit4[file] else '\n'
        override += f'    public void {met}() {{}} // Fails in super class\n'

        index = noc.rfind('}')
        
        self.noc_files[file] = noc[:index] + override + noc[index:]
        ori = self.files[file]
        self.files[file] = ori[:index] + override + ori[index:]
        return

    def remove_test_methods(self, methods: list, base_dir: Path, verbose=False):
        for method in methods:
            # defects4j directly convert class name to file path
            # that would be not precise, for example, for embedded
            # classes there is no source file available
            clz, _, met = method.partition('::')
            f = base_dir / (clz.replace('.', '/') + '.java')
            if not self.read_file(f):
                if verbose:
                    # use unix line separator directly
                    # because the code here are not expected to reach
                    printc(f'fix_tests: {str(f)} does not exist -> SKIP ({method})\n')
                continue
                
            self.remove_test_method(f, clz, met)

    def __init__(self):
        self.files = {}
        self.junit4 = {}
        self.noc_files = {}
        self.regex = get_java_regex()

def fix_tests(project,
              bid,
              wd,
              is_buggy,
              context,
              *,
              loader=None,
              revision_id=None,
              _except=set(),
              verbose=False):
    # RM_ASSERTS environment variable in the original script
    # when it is called for checkout command it is always not set
    # simply skip its implementation
    full = False

    classes, methods, assertions = get_flaky_tests(project,
                                                   bid,
                                                   is_buggy,
                                                   context,
                                                   revision_id=revision_id,
                                                   full=full)

    fixer = FixTests()

    if not methods:
        # defects4j does not implement this function
        fixer.exclude_test_classes(classes)

    if _except:
        # never reach here when called for checkout command
        methods -= _except
        
    if full:
        # never reach here when called for checkout command
        # defects4j record the full line and parse again which induced overhead
        # perl is not readable...
        # why expressions like $_ with bad readability are allowed?
        # unless ($RM_ASSERTS && _remove_assertion($class, $method)) {
        #     push(@method_list, $_);
        # }
        methods = fixer.remove_assertions(methods, assertions)
    
    test_dir = get_dir_src_tests(project, bid, is_buggy, context, loader)
    base_dir = Path(wd, test_dir)

    fixer.remove_test_methods(methods, base_dir, verbose)
    
    fixer.write_files()

    # defects4j write properties file to record the excluded tests
    # but their code is odd, each time exclude_tests_in_file is called it will try
    # to write d4j.tests.exclude property which contains classes parsed from the
    # argument file (not methods, odd again), and this write behavior will overwrite
    # the original property value with a same name
    # in fix_tests exclude_tests_in_file is called three times, and finally
    # only the last call could keep the property, which means the first two calls
    # would not have their excluded classes in the properties file 
    # though classes are mostly empty so the code is not reached, why they design
    # this behavior? or it is just a bug?

    # avoid writing the file again and again
    config = {}
    if classes:
        excluded = ','.join(map(lambda x : x.replace('.', '/') + '.*', classes))
        config['d4j.tests.exclude'] = excluded

    return config

def fill_properties(properties: dict,
                    project: str,
                    bid: str,
                    is_buggy,
                    context,
                    loader=None):
    loader = loader or get_project_loader(project)(context)

    # skip the check of is_bugmine
    # not planned to implement defects4j's bug mining

    properties['d4j.project.id'] = project
    properties['d4j.bug.id'] = bid

    # why defects4j add this property two times?
    properties['d4j.dir.src.classes'] = get_dir_src_classes(project,
                                                            bid,
                                                            is_buggy,
                                                            context,
                                                            loader)
    #properties['d4j.dir.src.classes'] = get_dir_src_classes(project,
    #                                                        bid,
    #                                                        is_buggy,
    #                                                        context,
    #                                                        loader)

    properties['d4j.dir.src.tests'] = get_dir_src_tests(project,
                                                        bid,
                                                        is_buggy,
                                                        context,
                                                        loader)

    properties['d4j.classes.modified'] = ','.join(get_classes_modified(project,
                                                                       bid,
                                                                       context))

    properties['d4j.classes.relevant'] = ','.join(get_classes_relevant(project,
                                                                       bid,
                                                                       context))

    properties['d4j.tests.trigger'] = ','.join(get_tests_trigger(project,
                                                                 bid,
                                                                 context))