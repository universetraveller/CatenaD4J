from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import (
    run_apply_patch_task,
    is_protected_directory,
    get_auto_task_printer,
    read_properties,
    write_properties,
    append_file,
    do_nothing,
    Git
)
from pathlib import Path
from os.path import abspath
from ..c4jutil import (
    read_version_info,
    parse_vid,
    check_working_directory,
    ERR,
    init_git_repository,
    create_commit_and_tag,
    get_tag_name_from_ver,
    normalize_tag,
    check_vid
)
from ..exceptions import Catena4JError
from shutil import rmtree
from ..loaders import get_project_loader
from ..d4jutil import (
    get_revision_id,
    fill_properties,
    get_src_patch_dir
)

_parser = None
def initialize():
    global _parser
    # is it better to add an alias co?
    _parser = _create_command('checkout',
                              help='checkout a particular project version',
                              add_help=False)
    _parser.add_argument('-p', required=True, metavar='project_id')
    _parser.add_argument('-v', required=True, metavar='version_id', help='Specify a version id to check out, format: <bid: int><tag: \'b\' or \'f\'>[<cid: int>].')
    _parser.add_argument('-w', required=True, metavar='work_dir')
    _parser.add_argument('--full-history', action='store_true', help='Generate more commits, for example, the post-fix, post-fix-compilable, pre-fix revisions.')
    _parser.__add_arguments_help__ = True

    _reset = _create_command('reset',
                              help='reset a working directory',
                              add_help=False)
    _reset.add_argument('-w', required=False, metavar='work_dir')

def d4j_checkout_vid(project: str, bid: str, tag: str, wd: str, context, loader=None):
    '''
        This function implements the main logic of defects4j's checkout command

        while bid is a positive integer, and tag is either \'b\' of \'f\'

        context is expected to be not None 
        
        type: env.Context or SystemContext

        loader is used to do project specific tasks, if it is None a new one
        would be created and returned

        type: ProjectLoader

        This function will not check if the current directory is a previous used one,
        and treat it as a non-project directory

        The checking process is done by another function to handle both defects4j and
        catena4j working directories (see try_to_reuse_working_directory)
    '''
    auto_task_print = get_auto_task_printer(context)

    wdp = Path(wd)

    if wdp.is_file():
        raise Catena4JError(f'Working directory {wd} should not be a file')

    # ensure the working directory exists
    not_empty = any(wdp.iterdir()) if wdp.is_dir() else wdp.mkdir(parents=True)
    
    # if the directory is not empty, clean it
    if not_empty:
        # that means if I create a config file in a directory
        # it would be completely cleaned?
        if check_working_directory(wdp, context) == ERR:
            raise Catena4JError(f'Directory exists but is not a previously used working '
                                'directory: {wd}')

        # any will consume the first path if exists so create it again
        # do not change the iterator to list to avoid case that multiple folders
        # exist but it is not a working directory
        for entry in wdp.iterdir():
            if entry.is_file():
                entry.unlink()
            else:
                rmtree(entry)
    
    project_loader = loader or get_project_loader(project)(context)

    revision_id = get_revision_id(project, bid, False, context)

    auto_task_print(f'Checking out {revision_id[:8]} to {wd}',
                    project_loader.checkout_revision,
                    (revision_id, wd))

    # why defects4j has a redundant write_config_file here?
    #write_properties(
    #    wdp / context.d4j_version_props,
    #    {
    #        'pid': project,
    #        'vid': bid + tag
    #    }
    #)

    auto_task_print('Init local repository',
                    init_git_repository,
                    (wd,))

    write_properties(
        wdp / context.d4j_version_props,
        {
            'pid': project,
            'vid': bid + 'f'
        }
    )


    append_file(wdp / '.gitignore', '\n.svn\n')

    d4j_tag = context.d4j_tag
    if not context.minimal_checkout:
        post_fix_tag = d4j_tag.format(project=project,
                                      bid=bid,
                                      suffix='POST_FIX_REVISION')

        # skip commits that users usually do not use 
        auto_task_print('Tag post-fix revision',
                        create_commit_and_tag,
                        (post_fix_tag, wd))

    # defects4j uses git status to detect changes
    # if there is change, commit and tag a post-fix-compilable version
    if project_loader.d4j_checkout_hook(project, revision_id, wd) \
        and not context.minimal_checkout:
        post_fix_compilable_tag = d4j_tag.format(project=project,
                                                 bid=bid,
                                                 suffix='POST_FIX_COMPILABLE')
        auto_task_print('Run post-checkout hook',
                        create_commit_and_tag,
                        (post_fix_compilable_tag, wd))

    config = project_loader.fix_tests(project,
                                      bid,
                                      wd,
                                      False,
                                      revision_id=revision_id)


    path2props = wdp / context.d4j_version_co_props

    if path2props.is_file():
        config.update(read_properties(path2props))

    fill_properties(config, project, bid, False, context, project_loader)

    write_properties(path2props, config)

    fixed_tag = d4j_tag.format(project=project, bid=bid, suffix='FIXED_VERSION')
    auto_task_print('Initialize fixed program version',
                    create_commit_and_tag,
                    (fixed_tag, wd))
    
    # apply patch to obtain buggy version
    patch = get_src_patch_dir(project, bid, context)

    run_apply_patch_task(patch, wd, context)

    write_properties(
        wdp / context.d4j_version_props,
        {
            'pid': project,
            'vid': bid + 'b'
        }
    )

    buggy_tag = d4j_tag.format(project=project, bid=bid, suffix='BUGGY_VERSION')
    auto_task_print('Initialize buggy program version',
                    create_commit_and_tag,
                    (buggy_tag, wd))

    # no untracked files, skip the clean step
    final_checkout = Git.checkout
    final_tag = fixed_tag
    if not context.minimal_checkout:
        Git.checkout(post_fix_tag, wd) 

        buggy_rev = get_revision_id(project, bid, True, context)
        diff = wdp / '.defects4j.diff'
        auto_task_print(f'Diff {revision_id[:8]}:{buggy_rev[:8]}',
                        loader.export_diff,
                        (revision_id, buggy_rev, diff))

        run_apply_patch_task(diff, wd, context)
        diff.unlink()

        pre_fix_tag = d4j_tag.format(project=project, bid=bid, suffix='PRE_FIX_REVISION')
        auto_task_print('Tag pre-fix revision',
                        create_commit_and_tag,
                        (pre_fix_tag, wd))

        # why defects4j does not reuse the tag name here?
        final_tag = buggy_tag if tag == 'b' else fixed_tag
    elif tag == 'b':
        # if it is minimal mode and the tag is b
        # the final checkout could be skipped
        final_checkout = do_nothing

    auto_task_print(f'Check out program version: {project}-{bid}{tag}',
                    final_checkout,
                    (final_tag, wd))

    return project_loader


def load_version(project: str, bid: str, cid: str, tag: str, wd, context):
    auto_task_print = get_auto_task_printer(context)

    wdp = Path(wd)

    loader = get_project_loader(project)(context)

    if cid is None:
        # fallback to defects4j checkout
        d4j_checkout_vid(project, bid, tag, wd, context, loader)
        return

    # the following tasks are based on the buggy version
    d4j_checkout_vid(project, bid, 'b', wd, context, loader)

    # delegate checkout tasks to loaders to support custom checkout behavior
    auto_task_print(f'Load buggy version for {project}-{bid}-{cid}',
                    loader.load_buggy_version,
                    (project, bid, cid, wd))

    version_info = {
                        'pid': project,
                        'bid': bid,
                        'cid': cid,
                        'tag': normalize_tag('b'),
                        # TODO expected to replace the old format
                        'project': project,
                        'bugid': bid,
                        'cid': cid,
                        'vtag': normalize_tag('b')
                    }
    write_properties(wdp / context.c4j_version_props, version_info)

    buggy_tag = get_tag_name_from_ver(version_info, context)

    auto_task_print(f'Commit buggy version {buggy_tag}',
                    create_commit_and_tag,
                    (buggy_tag, wd))
    
    auto_task_print(f'Load fixed version for {project}-{bid}-{cid}',
                    loader.load_fixed_version,
                    (project, bid, cid, wd))

    version_info['vtag'] = normalize_tag('f')
    version_info['tag'] = normalize_tag('f')
    write_properties(wdp / context.c4j_version_props, version_info)

    fixed_tag = get_tag_name_from_ver(version_info, context)

    auto_task_print(f'Commit fixed version {fixed_tag}',
                    create_commit_and_tag,
                    (fixed_tag, wd))
    
    final_checkout = Git.checkout
    final_tag = buggy_tag
    if tag == 'f':
        final_checkout = do_nothing
    
    auto_task_print(f'Check out program version: {project}-{bid}{tag}{cid}',
                    final_checkout,
                    (final_tag, wd))
    
    return loader

def checkout_to(tag_or_commit, wd):
    Git.checkout(tag_or_commit, wd)
    Git.clean(wd)

def reset_working_directory(wd, context):
    auto_task_print = get_auto_task_printer(context)
    version_info = read_version_info(wd, context)
    tag_name = get_tag_name_from_ver(version_info, context)
    auto_task_print('Reset the working directory',
                    checkout_to,
                    (tag_name, wd))

def reset(context):
    args = context.args
    if args.w:
        context.cwd = abspath(args.w)

    wd = context.cwd

    reset_working_directory(wd, context)

def try_to_reuse_working_directory(project, bid, tag, cid, wd, context):
    '''
        defects4j only checks if it is the same project with a same bid

        could we optimize that to further check the previous commit ids
        so that we can make it possible to avoid the clone process if the
        current directory is a working directory but do not match the pid and bid?
    '''
    auto_task_print = get_auto_task_printer(context)
    
    try:
        version_info = read_version_info(wd, context)
    except Catena4JError:
        # no version file exists
        return False
    
    if version_info['pid'] != project:
        return False
    
    if version_info['bid'] != bid:
        return False

    if version_info['cid'] != cid:
        return False

    version_info['tag'] = normalize_tag(tag)

    # cid is either None (defects4j project) or an actual value (catena4j project)
    tag_name = get_tag_name_from_ver(version_info, context)

    auto_task_print(f'Check out program version: {tag_name}',
                    checkout_to,
                    (tag_name, wd))

    return True


def run(context: ExecutionContext):
    '''
        This function implements the checkout command for catena4j and defects4j

        Option --full-history indicates whether to add intermediate commits to make
        the project structure cleaner

        These commits may be useful for changes analysis but usually users only use
        the buggy and fixed version

        If --full-history is not set, the minimal_checkout configuration (in config.py)
        would be used, --full-history will overwrite this configuration to False if set

        When minimal_checkout is True, extra commits are skipped, only basic buggy and
        fixed commits are created, which could make the command faster

        However, commits before the revision used to create the project are not removed,
        because git's local clone doesn't support --depth option and be faster than use
        the file:// prefix (which supports --depth)

        Difference: Using file:// as the source link would be treated as a remote link,
        which causes git to index the whole project again
    '''
    args = context.args

    if args.w:
        context.cwd = abspath(args.w)

    wd = context.cwd

    project = args.p

    if is_protected_directory(wd):
        raise Catena4JError(f'Access restricted: could not select a protected directory '
                            'as working directory')

    if args.full_history:
        context.minimal_checkout = False

    bid, tag, cid = parse_vid(args.v)

    check_vid(project, bid, cid, context)

    if try_to_reuse_working_directory(project, bid, tag, cid, wd, context):
        return

    load_version(project, bid, cid, tag, wd, context)