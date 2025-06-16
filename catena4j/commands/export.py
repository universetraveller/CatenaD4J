from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from argparse import RawDescriptionHelpFormatter

_desc = '''Properties:
  classes.modified  Classes modified by the bug fix
  classes.relevant  Classes loaded by the triggering tests
  cp.compile        Classpath to compile the project
  cp.test           Classpath to compile and run the developer-written tests
  dir.bin.classes   Target directory of classes
  dir.bin.tests     Target directory of test classes
  dir.src.classes   Source directory of classes
  dir.src.tests     Source directory of tests
  tests.all         List of all developer-written tests
  tests.relevant    Relevant tests that touch at least one of the modified sources
  tests.trigger     Trigger tests that expose the bug'''
  
def initialize():
    parser = _create_command('export', description=_desc, formatter_class=RawDescriptionHelpFormatter, help='export a version-specific property', add_help=False)
    parser.add_argument('-p', required=True, metavar='property_name')
    parser.add_argument('-o', metavar='output_file')
    parser.add_argument('-w', metavar='work_dir')

def run(context: ExecutionContext):
    pass