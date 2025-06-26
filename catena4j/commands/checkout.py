from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import toolkit_execute, TaskPrinter
from pathlib import Path
from os.path import abspath
from ..c4jutil import read_version_info, parse_vid
from ..exceptions import Catena4JError

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

def run(context: ExecutionContext):
    args = context.args

    if args.w:
        context.cwd = abspath(args.w)

    wd = context.cwd

    bid, tag, cid = parse_vid(args.v)