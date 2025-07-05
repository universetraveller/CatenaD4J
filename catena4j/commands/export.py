from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import (
    read_properties,
    print_result,
    get_cache_path,
    read_file,
    write_file,
)
from argparse import RawDescriptionHelpFormatter
from os.path import abspath
from pathlib import Path
from .. import d4jutil
from ..c4jutil import read_version_info, Catena4JError, BUGGY, FIXED
from ..loaders import get_project_loader

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
    return '\n'.join([f'  {prop:<16}  {_props[prop]}' for prop in _props])

def get_desc_all():
    return '\n'.join([get_desc(_props) for _props in (c4j_props, d4j_static, d4j_dynamic)])

_parser = None
def initialize():
    global _parser
    _parser = _create_command('export',
                              description=f'Properties:\n{get_desc_all()}',
                              formatter_class=RawDescriptionHelpFormatter,
                              help='export a version-specific property',
                              add_help=False)
    _parser.add_argument('-p', required=True, metavar='property_name')
    _parser.add_argument('-o', metavar='output_file')
    _parser.add_argument('-w', metavar='work_dir')
    _parser.add_argument('--from-cache', action='store_true', help='Try to read the result directly from cache instead of computing it at runtime.')
    _parser.add_argument('--update-cache', action='store_true', help='Expire the current cache and update it.')
    _parser.__add_arguments_help__ = True

def query_c4j(prop, proj, bid, cid, wd, context=None, vtag=None):
    '''
        If cid is None, it would be ignored
    '''
    if cid is None:
        return query_d4j_static(prop=prop, proj=proj, bid=bid, wd=wd, context=context, vtag=vtag)

    loader = get_project_loader(proj)(context)
    return loader.get_property(prop, proj, bid, cid)

def query_d4j_static(prop, proj, bid, wd, context=None, vtag=None):
    '''
        For all properties that could compute using files in defects4j's repository,
        including properties belong to c4j_props
    '''

    # in a defects4j working directory which may contain these properties
    cached = read_properties(Path(wd, context.d4j_version_co_props))
    d4j_prop = f'd4j.{prop}'
    if cached is not None and d4j_prop in cached:
        result = cached[d4j_prop]
        if prop.startswith('dir'):
            return result
        return '\n'.join(result.split(','))

    return _query_d4j_static(prop=prop, proj=proj, bid=bid, context=context, vtag=vtag)

def _query_d4j_static(prop, proj, bid, context=None, vtag=None):
    '''
        Version without reading cache file

        This process could be used in checkout process

        See: defects4j/framework/core/Project.pm line 465 and line 1261
    '''
    if prop == 'classes.modified':
        return '\n'.join(d4jutil.get_classes_modified(proj, bid, context))
    elif prop == 'classes.relevant':
        return '\n'.join(d4jutil.get_classes_relevant(proj, bid, context))
    elif prop == 'tests.relevant':
        return '\n'.join(d4jutil.get_tests_relevant(proj, bid, context))
    elif prop == 'tests.trigger':
        return '\n'.join(d4jutil.get_tests_trigger(proj, bid, context))

    is_buggy = True
    if vtag == FIXED:
        is_buggy = False

    if prop == 'dir.src.classes':
        return d4jutil.get_dir_src_classes(proj, bid, is_buggy, context)
    elif prop == 'dir.src.tests':
        return d4jutil.get_dir_src_tests(proj, bid, is_buggy, context)

def query_d4j_dynamic(prop, proj, wd, context=None):
    '''
        For properties require information from the checked out files 
    '''
    loader = get_project_loader(proj)(context)
    xml_attr = 'c4j_rel_project_export_xml'
    main_attr = 'c4j_toolkit_export_main'
    return loader.toolkit_execute(prop, proj, wd, xml_attr=xml_attr, main_attr=main_attr)

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
                      version_info['bid'],
                      version_info['cid'],
                      context)

def _handle_cache(prop, pid, vid, cid, context, content):
    write_file(get_export_cache(prop, pid, vid, cid, context), content)

def handle_cache(prop, version_info, context, args, cache, content):
    if args.update_cache or (args.from_cache and cache is None):
        _handle_cache(prop,
                      version_info['pid'],
                      version_info['bid'],
                      version_info['cid'],
                      context,
                      content)

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

    if args.w:
        context.cwd = abspath(args.w)

    wd = context.cwd

    result = None

    version_info = read_version_info(wd, context)

    cache = try_cache(prop, version_info, context, args)

    if prop in c4j_props:
        # Trap to catena4j
        result = cache or query_c4j(prop,
                                    version_info['pid'],
                                    version_info['bid'],
                                    version_info['cid'],
                                    wd,
                                    context,
                                    version_info['tag'])
    elif prop in d4j_static:
        # Trap to re-implmented version of defects4j
        result = cache or query_d4j_static(prop,
                                           version_info['pid'],
                                           version_info['bid'],
                                           wd,
                                           context,
                                           version_info['tag'])
    elif prop in d4j_dynamic:
        # Call java toolkit
        result = cache or query_d4j_dynamic(prop,
                                            version_info['pid'],
                                            wd,
                                            context)
    else:
        raise Catena4JError(f'Unknown property {prop}')
    
    handle_cache(prop, version_info, context, args, cache, result)

    if context.mode == ExecutionContext.CLI:
        # output to stdout or file
        output = None if args.o is None else open(args.o, 'w')
        print_result(result + '\n', output)
        if output is not None:
            output.close()

    return result