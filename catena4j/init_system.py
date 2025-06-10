from . import init_internal
from . import entries
# init parser arguments
parser = init_internal.init_parser()
parser.add_argument('command', type=str, help='A specific CatenaD4j command')
parser.add_argument('-p', metavar='project_name',required=False, help='The name of project you want to operate')
parser.add_argument('-v', metavar='bug_id_version', required=False, help='The version/bug-id you want to operate')
parser.add_argument('-w', metavar='working_dir', required=False, help='The working directory')
parser.add_argument('-o', metavar='output_file', required=False, help='The output file')
parser.add_argument('-b', metavar='bug_id', required=False, help='Integer id of a bug')
parser.add_argument('-r', action='store_const', const=1, required=False, help='Run the relevant tests')
parser.add_argument('-t', metavar='test_name', required=False, help='Run a single test method or a test class')
parser.add_argument('-s', metavar='test_suite', required=False, help='Run a test suite')

# init running function
def run_script():
    init_internal.check_help()
    init_internal.main(parser)
