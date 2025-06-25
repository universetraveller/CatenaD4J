from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import toolkit_execute
from pathlib import Path
from os.path import abspath
from ..c4jutil import read_version_info

_parser = None
_clean = None
def initialize():
    global _parser, _clean
    _parser = _create_command('compile',
                              help='compile a checked-out project version',
                              add_help=False)
    _parser.add_argument('-w', metavar='work_dir')
    _parser.add_argument('--target',
                         metavar='compilation_target',
                         required=False,
                         default='compile.tests')

    _clean = _create_command('clean',
                             help='clean the output directory',
                             add_help=False)
    _clean.add_argument('-w', metavar='work_dir')

def execute_compile(target, proj, wd, context, parser):
    xml = Path(context.c4j_home, context.c4j_rel_project_execute_xml.format(project=proj))
    toolkit_execute(context.c4j_toolkit_execute_main,
                    wd,
                    context,
                    parser=parser,
                    args=(str(xml), target))

def run(context: ExecutionContext, parser=None):
    args = context.args

    if args.w:
        context.cwd = abspath(args.w)

    wd = context.cwd

    if parser is None:
        parser = _parser

    # induced performace overhead here but it is minimal
    version_info = read_version_info(wd, context, parser)

    execute_compile(args.target,
                    version_info['pid'],
                    wd,
                    context,
                    parser)

def clean(context: ExecutionContext):
    context.args.target = 'clean'
    run(context, _clean)