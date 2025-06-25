from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from pathlib import Path
from ..util import print_result, get_project_cache, read_simple_csv, close_project_cache
from os import linesep
from ..c4jutil import Catena4JError

_pids = None
_bids = None
_cids = None

def initialize():
    global _pids, _bids, _cids
    _pids = _create_command('pids',
                            help='prints all available project ids',
                            add_help=False)

    _bids = _create_command('bids',
                            help='print all active bug IDs for a specific project',
                            add_help=False)
    _bids.add_argument('-p', required=True, metavar='project_id')
    _bids.add_argument('--with-cids', action='store_true')
    group = _bids.add_mutually_exclusive_group(required=False)
    group.add_argument('-D', action='store_true')
    group.add_argument('-A', action='store_true')

    _cids = _create_command('cids',
                            help='print available catena ids for a bug id',
                            add_help=False)
    _cids.add_argument('-p', required=True, metavar='project_id')
    _cids.add_argument('-b', required=True, metavar='bug_id')

def query_pids(context):
    cache = context.__c4j_cache__

    if 'pids' not in cache:
        path_to_projects = Path(context.c4j_home, context.c4j_rel_projects)
        pids = [project.name for project in path_to_projects.iterdir() if project.is_dir()]
        cache['pids'] = sorted(pids)
        
    return cache['pids']

def run_pids(context: ExecutionContext):
    result = query_pids(context)

    if context.mode == ExecutionContext.CLI:
        print_result(linesep.join(result) + linesep if result else '')

    return result

def _query_csv(project, context, cache_attr, home_attr, rel_attr, file_name, parser):
    cache = getattr(context, cache_attr)
    path = Path(getattr(context, home_attr),
                getattr(context, rel_attr),
                project,
                file_name)
    bugs = get_project_cache(cache, project, file_name, read_simple_csv, (path,))
    if bugs is None:
        close_project_cache(cache, project, file_name)
        raise Catena4JError(f'Failed to read {file_name} from project {project}')
    return bugs

def _query_bids(project, context, cache_attr, home_attr, rel_attr, file_name):
    bugs = _query_csv(project, context, cache_attr, home_attr, rel_attr, file_name, _bids)
    return set(map(lambda b : b[0], bugs))

def query_bids_with_cids(project, context):
    return _query_bids(project,
                       context,
                       '__c4j_cache__',
                       'c4j_home',
                       'c4j_rel_projects',
                       'bugs-registry.csv')

def query_deprecated_bids(project, context):
    return _query_bids(project,
                       context,
                       '__d4j_cache__',
                       'd4j_home',
                       'd4j_rel_projects',
                       'deprecated-bugs.csv')

def query_active_bids(project, context):
    return _query_bids(project,
                       context,
                       '__d4j_cache__',
                       'd4j_home',
                       'd4j_rel_projects',
                       'active-bugs.csv')

def run_bids(context: ExecutionContext):
    args = context.args
    project = args.p
    if args.with_cids:
        result = query_bids_with_cids(project, context)
    else:
        deprecated = set()
        active = set()
        if args.D:
            deprecated = query_deprecated_bids(project, context)
        else:
            active = query_active_bids(project, context)
        if args.A:
            deprecated = query_deprecated_bids(project, context)
        result = deprecated | active

    result = sorted(list(result), key=lambda x:int(x))

    if context.mode == ExecutionContext.CLI:
        print_result(linesep.join(result) + linesep if result else '')

    return result

def query_cids(project, id, context):
    bugs = _query_csv(project,
                       context,
                       '__c4j_cache__',
                       'c4j_home',
                       'c4j_rel_projects',
                       'bugs-registry.csv',
                       _cids)
    return [line[1] for line in bugs if line[0] == id]

def run_cids(context: ExecutionContext):
    args = context.args
    project = args.p
    bid = args.b
    
    result = sorted(query_cids(project, bid, context), key=lambda x:int(x))

    if context.mode == ExecutionContext.CLI:
        print_result(linesep.join(result) + linesep if result else '')

    return result
