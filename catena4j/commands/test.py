from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import TaskPrinter, print_result
from os.path import abspath
from ..c4jutil import read_version_info, Catena4JError
from ..loaders import get_project_loader
from .compile import execute_compile
from .export import query_d4j_static

_parser = None
def initialize():
    global _parser
    _parser = _create_command('test',
                              help='run tests on a checked-out project version',
                              add_help=False)
    _parser.add_argument('-w', metavar='work_dir', help='The working directory to run the tests. Default is the current directory.')
    _parser.add_argument('-a', action='store_true', help='Collect all failed assertions without breaking the process (not implemented now).')
    _parser.add_argument('-l', '--list', action='store_true', dest='l', help='List all tests to run but do not actually execute them (written to <work_dir>/all_tests).')
    _parser.add_argument('-c', '--compile', action='store_true', dest='c', help='Run compilation tasks before running tests')
    _parser.add_argument('-i', '--isolation', type=int, dest='i', required=False, help='Specify the isolation level of testcases. Options: 1 (reused isolated classloader), 2 (isolated classloader for each test class), 3 (use ant\'s junit task) Default: config.c4j_test_isolation_level')
    group = _parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-t', metavar='test', action='append', help='Specify a test class or method to run. This option could be duplicate. Format: <class name>#<method name>')
    group.add_argument('-r', action='store_true', help='Only run relevant tests')
    group.add_argument('--trigger', action='store_true', help='Only run trigger tests')
    _parser.__add_arguments_help__ = True

def run_tests(tests, project, wd, context, list_only=False, assertions=False, isolation=1, *, test_name=None):
    printer = TaskPrinter(f'Run tests' if test_name is None else f'Run tests ({test_name})') \
                if context.mode == ExecutionContext.CLI else None

    loader = get_project_loader(project)(context)

    if tests is None:
        tests = []

    java_options = []
    if assertions:
        # TODO add an java agent to store all assertion without breaking the running test
        pass

    if list_only:
        java_options.append(f'-Dc4j.tests.printer.out={wd}/all_tests')
    else:
        java_options.append(f'-DOUTFILE={wd}/failing_tests')

    if isolation == 1:
        java_options.append(f'-Dc4j.test.helper=io.github.universetraveller.util.JUnit4Helper')
    elif isolation == 2:
        java_options.append(f'-Dc4j.test.helper=io.github.universetraveller.util.JUnit4Helper1')
    elif isolation == 3:
        java_options.append(f'-Dc4j.test.runner=ant')
    else:
        raise Catena4JError(f'Unknown isolation level: {isolation}')

    result = loader.toolkit_execute(tests,
                                    project,
                                    wd,
                                    xml_attr='c4j_rel_project_test_xml',
                                    main_attr='c4j_toolkit_test_main',
                                    task_printer=printer,
                                    java_options=java_options)

    if context.mode == ExecutionContext.CLI:
        result = result.strip()
        print_result(result + '\n' if result else '')
    
    return result

def run(context: ExecutionContext):
    args = context.args

    if args.w:
        context.cwd = abspath(args.w)

    wd = context.cwd

    # induced performace overhead here but it is minimal
    version_info = read_version_info(wd, context)


    if args.c:
        printer = TaskPrinter(f'Execute target (compile.tests)') \
                    if context.mode == ExecutionContext.CLI else None

        execute_compile('compile.tests',
                        version_info['pid'],
                        wd,
                        context,
                        task_printer=printer)
    
    tests = args.t

    attr = None
    if args.r :
        attr = 'tests.relevant'
    elif args.trigger:
        attr = 'tests.trigger'

    if attr is not None:
        _tests = query_d4j_static(attr,
                                  version_info['pid'],
                                  version_info['bid'],
                                  wd,
                                  context,
                                  version_info['tag'])
        
        tests = _tests.split('\n')
        # workaround to convert defects4j test format to junit test format
        if attr == 'tests.trigger':
            tests = list(map(lambda x:x.replace('::', '#', 1), tests))
    else:
        attr = 'tests.input' if tests else 'tests.all'
    
    run_tests(tests=tests,
              project=version_info['pid'],
              wd=wd,
              context=context,
              list_only=args.l,
              assertions=args.a,
              isolation=args.i or context.c4j_test_isolation_level,
              test_name=attr)
