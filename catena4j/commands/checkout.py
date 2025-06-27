from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import (
    is_protected_directory,
    auto_task_print,
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
    create_post_fix_commit
)
from ..exceptions import Catena4JError
from shutil import rmtree
from ..loaders import get_project_loader
from ..d4jutil import get_revision_id, check_d4j_vid

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

    revision_id = get_revision_id(project, bid, tag == 'b', context)

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

    d4j_tag = context.d4j_tag.format(project=project, bid=bid, suffix='POST_FIX_REVISION')

    append_file(wdp / '.gitignore', linesep + '.svn' + linesep)

    auto_task_print('Tag post-fix revision',
                    create_post_fix_commit,
                    (d4j_tag, wd))

    # defects4j uses git status to detect changes
    # if there is change, commit and tag a post-fix-compilable version
    if project_loader.d4j_checkout_hook(project, revision_id, wd):
        _tag = context.d4j_tag.format(project=project,
                                      bid=bid,
                                      suffix='POST_FIX_COMPILABLE')
        auto_task_print('Run post-checkout hook',
                        create_post_fix_commit,
                        (_tag, wd))

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