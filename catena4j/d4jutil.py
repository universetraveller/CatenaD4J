from .util import read_file, get_project_cache
from pathlib import Path
from .loaders import get_project_loader
import re
from .exceptions import Defects4JError

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
def _parse_failing_tests(lines, full=False):
    '''
        From defects4j/framework/core/Utils.pm get_failing_tests
    '''
    if full:
        classname_matcher = re.compile(r'(?:.*\.)?([^.]+)')

    idx = -1
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
    a, b, c = _parse_failing_tests(content.splitlines())
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

def _get_rev_id(proj, bid, is_buggy, context):
    active_bugs = get_project_cache(context.__d4j_cache__,
                                    proj,
                                    'active-bugs',
                                    read_active_bugs,
                                    (context, proj))
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
    rev = _get_rev_id(proj, bid, is_buggy, context)
    dir_layout = get_dir_layout(context, proj)
    return dir_layout[rev] if rev in dir_layout else None

def get_dir_src_classes(proj, bid, wd, is_buggy, context):
    dir_src = get_dir_src_cache(proj, bid, is_buggy, context)

    if dir_src is not None:
        return dir_src[0]

    loader = get_project_loader(proj)(context)

    return loader.src_layout

def get_dir_src_tests(proj, bid, wd, is_buggy, context):
    dir_src = get_dir_src_cache(proj, bid, is_buggy, context)

    if dir_src is not None:
        return dir_src[1]

    loader = get_project_loader(proj)(context)

    return loader.test_layout
