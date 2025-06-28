from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import (
    apply_patch,
    is_protected_directory,
    auto_task_print,
    read_properties,
    write_properties,
    append_file,
    Git
)
from pathlib import Path
from os import linesep
from os.path import abspath
from ..c4jutil import (
    read_version_info,
    parse_vid,
    check_working_directory,
    ERR,
    init_git_repository,
    create_commit_and_tag
)
from ..exceptions import Catena4JError
from shutil import rmtree
from ..loaders import get_project_loader
from ..d4jutil import (
    get_revision_id,
    check_d4j_vid,
    fix_tests,
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
    _parser.add_argument('-v', required=True, metavar='version_id')
    _parser.add_argument('-w', required=True, metavar='work_dir')

def d4j_checkout_vid(project: str, bid: str, tag: str, wd: str, context, loader=None):
    '''
        This function implements the main logic of defects4j's checkout command

        while bid is a positive integer, and tag is either \'b\' of \'f\'

        context is expected to be not None 
        
        type: env.Context or SystemContext

        loader is used to do project specific tasks, if it is None a new one
        would be created and returned

        type: ProjectLoader
    '''
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

    tag_pf = context.d4j_tag.format(project=project, bid=bid, suffix='POST_FIX_REVISION')

    append_file(wdp / '.gitignore', linesep + '.svn' + linesep)

    auto_task_print('Tag post-fix revision',
                    create_commit_and_tag,
                    (tag_pf, wd))

    # defects4j uses git status to detect changes
    # if there is change, commit and tag a post-fix-compilable version
    if project_loader.d4j_checkout_hook(project, revision_id, wd):
        d4j_tag = context.d4j_tag.format(project=project,
                                         bid=bid,
                                         suffix='POST_FIX_COMPILABLE')
        auto_task_print('Run post-checkout hook',
                        create_commit_and_tag,
                        (d4j_tag, wd))

    config = fix_tests(project,
                       bid,
                       wd,
                       False,
                       context,
                       loader=project_loader,
                       revision_id=revision_id)


    path2props = wdp / context.d4j_version_co_props

    if path2props.is_file():
        config.update(read_properties(path2props))

    fill_properties(config, project, bid, False, context, project_loader)

    write_properties(path2props, config)

    d4j_tag = context.d4j_tag.format(project=project, bid=bid, suffix='FIXED_VERSION')
    auto_task_print('Initialize fixed program version',
                    create_commit_and_tag,
                    (d4j_tag, wd))
    
    # apply patch to obtain buggy version
    patch = get_src_patch_dir(project, bid, context)
    if apply_patch(patch, wd, context)[0]:
        return -1

    write_properties(
        wdp / context.d4j_version_props,
        {
            'pid': project,
            'vid': bid + 'b'
        }
    )

    d4j_tag = context.d4j_tag.format(project=project, bid=bid, suffix='BUGGY_VERSION')
    auto_task_print('Initialize buggy program version',
                    create_commit_and_tag,
                    (d4j_tag, wd))
    Git.checkout(tag_pf, wd) 
    buggy_rev = get_revision_id(project, bid, True, context)
    diff = wdp / '.defects4j.diff'
    # TODO export diff

    return project_loader


def run(context: ExecutionContext):
    args = context.args

    if args.w:
        context.cwd = abspath(args.w)

    wd = context.cwd

    project = args.p

    if is_protected_directory(wd):
        raise Catena4JError(f'Access restricted: could not select a protected directory '
                            'as working directory')


    bid, tag, cid = parse_vid(args.v)

    check_d4j_vid(project, bid, context)

    wdp = Path(wd)
    if (wdp / context.d4j_version_props).is_file():
        # TODO
        pass

    loader = get_project_loader(project)(context)

    d4j_checkout_vid(project, bid, tag, wd, context, loader)