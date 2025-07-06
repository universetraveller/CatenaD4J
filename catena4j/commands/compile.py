from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import TaskPrinter
from pathlib import Path
from os.path import abspath
from ..c4jutil import read_version_info
from ..exceptions import Catena4JError
from ..loaders import get_project_loader

_parser = None
_clean = None
def initialize():
    global _parser, _clean
    _parser = _create_command('compile',
                              help='compile a checked-out project version',
                              add_help=False)
    _parser.add_argument('-w', metavar='work_dir')
    _parser.add_argument('--verbose', action='store_true')
    _parser.add_argument('--target',
                         metavar='compilation_target',
                         required=False,
                         default='compile.tests',
                         help=('Run a specific compilation target. '
                               'Valid target should contain \'compile\' (compile, compile.tests, gradle.compile etc.) '
                               'or be \'clean\'. Default value: \'compile.tests\'. ')
                            )
    _parser.__add_arguments_help__ = True

    _clean = _create_command('clean',
                             help='clean the output directory',
                             add_help=False)
    _clean.add_argument('-w', metavar='work_dir')
    _clean.add_argument('--verbose', action='store_true')

def execute_compile(target, proj, wd, context, task_printer=None):
    loader = get_project_loader(proj)(context)
    loader.toolkit_execute(target, proj, wd, task_printer=task_printer)

def run(context: ExecutionContext):
    args = context.args

    target = args.target
    
    if 'compile' not in target and target != 'clean':
        raise Catena4JError('Access restricted: you may only run the \'clean\' target '
                            'or targets contain \'compile\' using this command.')

    if args.w:
        context.cwd = abspath(args.w)

    wd = context.cwd

    # induced performace overhead here but it is minimal
    version_info = read_version_info(wd, context)

    printer = None
    if context.mode == ExecutionContext.CLI:
        printer = TaskPrinter(f'Execute target ({target})')
        if args.verbose:
            printer.verbose = True

    execute_compile(target,
                    version_info['pid'],
                    wd,
                    context,
                    task_printer=printer)

def clean(context: ExecutionContext):
    context.args.target = 'clean'
    run(context)