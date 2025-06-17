from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import (
    read_properties,
    print_result,
    get_console_encoding,
    run_command,
    get_toolkit_command,
    get_cache_path,
    read_file,
    write_file
)
from argparse import RawDescriptionHelpFormatter
from os import linesep
from pathlib import Path

d4j_static = {
    'classes.relevant' : 'Classes loaded by the triggering tests',
    'dir.src.classes' : 'Source directory of classes',
    'dir.src.tests' : 'Source directory of tests',
    'tests.relevant' : 'Relevant tests that touch at least one of the modified sources',
}

c4j_props = {
    'classes.modified' : 'Classes modified by the bug fix',
    'tests.trigger' : 'Trigger tests that expose the bug'
}

d4j_dynamic = {
    'cp.compile' : 'Classpath to compile the project',
    'cp.test' : 'Classpath to compile and run the developer-written tests',
    'dir.bin.classes' : 'Target directory of classes',
    'dir.bin.tests' : 'Target directory of test classes',
    'tests.all' : 'List of all developer-written tests'
}

def get_desc(_props):
    return linesep.join([f'  {prop:<16}  {_props[prop]}' for prop in _props])

def get_desc_all():
    return linesep.join([get_desc(_props) for _props in (c4j_props, d4j_static, d4j_dynamic)])

_parser = None
def initialize():
    global _parser
    _parser = _create_command('export',
                              description=f'Properties:{linesep}{get_desc_all()}',
                              formatter_class=RawDescriptionHelpFormatter,
                              help='export a version-specific property',
                              add_help=False)
    _parser.add_argument('-p', required=True, metavar='property_name')
    _parser.add_argument('-o', metavar='output_file')
    _parser.add_argument('-w', metavar='work_dir')
    _parser.add_argument('--from-cache', action='store_true')
    _parser.add_argument('--update-cache', action='store_true')

def read_property_from(prop, path):
    result = read_file(path)
    if result is None:
        _parser.error(f'Could not find property {prop} from {str(path)}')
    return result.strip()

def query_c4j(prop, proj, bid, cid, wd, context=None):
    '''
        If cid is None, it would be ignored
    '''
    if cid is None:
        return query_d4j_static(prop=prop, proj=proj, bid=bid, wd=wd, context=context)

    path = Path(context.c4j_home, context.c4j_rel_projects, proj, bid, f'{cid}.{prop}')

    return read_property_from(prop, path)

def query_d4j_static(prop, proj, bid, wd, context=None):
    '''
        For all properties that could compute using files in defects4j's repository,
        including properties belong to c4j_props
    '''

    # in a defects4j working directory which may contain these properties
    cached = read_properties(Path(wd, context.c4j_version_co_props))
    d4j_prop = f'd4j.{prop}'
    if cached is not None and d4j_prop in cached:
        result = cached[d4j_prop]
        if prop.startswith('dir'):
            return result
        return linesep.join(result.split(','))

    return _query_d4j_static(prop=prop, proj=proj, bid=bid, context=context)

def _query_d4j_static(prop, proj, bid, context=None):
    '''
        Version without reading cache file

        This process could be used in checkout process

        See: defects4j/framework/core/Project.pm line 465 and line 1261
    '''
    path = None
    if prop == 'classes.modified':
        path = Path(context.d4j_home, context.d4j_rel_projects, proj, 'modified_classes', f'{bid}.src')
    elif prop == 'classes.relevant':
        path = Path(context.d4j_home, context.d4j_rel_projects, proj, 'loaded_classes', f'{bid}.src')
    elif prop == 'tests.relevant':
        path = Path(context.d4j_home, context.d4j_rel_projects, proj, 'relevant_tests', bid)
    
    if path is not None:
        return read_property_from(prop, path)

    if prop == 'tests.trigger':
        path = Path(context.d4j_home, context.d4j_rel_projects, proj, 'trigger_tests', bid)
        to_parse = read_property_from(prop, path)
        # TODO

    if prop == 'dir.src.classes':
        pass
    elif prop == 'dir.src.tests':
        pass

def query_d4j_dynamic(prop, proj, wd, context=None):
    '''
        For properties require information from the checked out files 
    '''
    enc = get_console_encoding()
    xml = Path(context.c4j_home, context.c4j_rel_project_export_xml.format(project=proj))
    main = context.c4j_toolkit_export_main
    cmd = get_toolkit_command(context, main, str(xml), prop, basedir=wd)
    ret, out, err = run_command(cmd=cmd, cwd=wd)
    if not ret:
        message = 'Failed to run command: {}\n\n{}\n\n{}'
        _parser.error(message.format(' '.join(cmd), out.decode(enc), err.decode(enc)))
    return out.decode(enc).strip()

def get_export_cache(prop, pid, vid, cid, context):
    parts = ['export', pid, vid]
    # TODO special optimization for shared properties, expected to remove in future
    if cid is not None and prop in c4j_props:
        parts.append(cid)
    parts.append(prop)
    return get_cache_path(context, *parts)

def _try_cache(prop, pid, vid, cid, context):
    return read_file(get_export_cache(prop, pid, vid, cid, context))

def try_cache(prop, version_info, context, args):
    if args.update_cache or not args.from_cache:
        return None
    return _try_cache(prop,
                      version_info['pid'],
                      version_info['vid'],
                      version_info['cid'],
                      context)

def _handle_cache(prop, pid, vid, cid, context, content):
    write_file(get_export_cache(prop, pid, vid, cid, context), content)

def handle_cache(prop, version_info, context, args, cache, content):
    if args.update_cache or (args.from_cache and cache is None):
        _handle_cache(prop,
                      version_info['pid'],
                      version_info['vid'],
                      version_info['cid'],
                      context,
                      content)

def parse_d4j_vid(vid):
    tag = 'BUGGY' if vid[-1] == 'b' else 'f'
    return vid[:-1], tag

def run(context: ExecutionContext):
    '''
        If option --from-cache is set would try to read property from cache file.
        If cache hit occurs, the normal computation process is skipped.
        Otherwise, when cache miss occurs, trigger the --update-cache option even
        it is not set.

        If --update-cache is set, it would override the --from-cache option. Which
        means the normal computation process would not be skipped and its result would
        be used to update the cache.
    '''
    args = context.args
    prop = args.p
    wd = args.w or context.cwd

    result = None

    version_info = read_properties(wd, context.d4j_version_props)
    if version_info is None:
        _parser.error('Could not find version info. '
                      'Please check if current directory '
                      'is a project from defects4j or catena4j.')

    vid, tag = parse_d4j_vid(version_info['vid'])
    version_info['vid'] = vid
    version_info['tag'] = tag 

    # check if the project is a catena4j project
    # TODO update the format of old c4j version properties file
    c4j_version_info = read_properties(wd, context.c4j_version_props)
    if c4j_version_info is None:
        version_info['cid'] = None
    else:
        version_info['pid'] = c4j_version_info['project']
        version_info['vid'] = c4j_version_info['bugid']
        version_info['cid'] = c4j_version_info['cid']
        version_info['tag'] = c4j_version_info['vtag']

    cache = try_cache(prop, version_info, context, args)

    if prop in c4j_props:
        # Trap to catena4j
        result = cache or query_c4j(prop,
                                    version_info['pid'],
                                    version_info['vid'],
                                    version_info['cid'],
                                    wd,
                                    context)
    elif prop in d4j_static:
        # Trap to re-implmented version of defects4j
        result = cache or query_d4j_static(prop,
                                           version_info['pid'],
                                           version_info['vid'],
                                           wd,
                                           context)
    elif prop in d4j_dynamic:
        # Call java toolkit
        result = cache or query_d4j_dynamic(prop,
                                            version_info['pid'],
                                            wd,
                                            context)
    else:
        _parser.error(f'Unknown property {prop}')
    
    handle_cache(prop, version_info, context, args, cache, result)

    if context.mode == ExecutionContext.CLI:
        # output to stdout or file
        output = None if args.o is None else open(args.o, 'w')
        print_result(result + linesep, output)
        if output is not None:
            output.close()

    return result