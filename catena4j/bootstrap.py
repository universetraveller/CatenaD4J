'''
    High level initialization methods including entry point of the program

    Default implementations are provided but the code could be modified by
    users on demand
'''
from .cli import manager as cli_manager
from . import env
from .env import register_env_constructor
from .dispatcher import CommandDispatcher
from ._bootstrap import (
    register_bootstrap_function,
    register_entry_point,
    register_initialization_order,
    StartupContext as system
)
import os
from . import util
from pathlib import Path

def _initialize_env():
    '''
        Default implementation of system env initialization
    '''
    c4j_home = env._c4j_home
    _env = {
        'c4j_home': str(c4j_home),
        # when this function is called, the system config has been initialized
        # this cache could speed up the startup time by about 100000 ns
        'd4j_home': util.search_cache(c4j_home / env._config.rel_cache_dir / 'd4j_home',
                                      lambda p : Path(p, 'framework', 'bin', 'defects4j').is_file(),
                                      util.find_path,
                                      ('defects4j', 2)),
        'cwd': os.getcwd(),
        # cache for each run
        '__d4j_cache__': {},
        '__c4j_cache__': {}
    }
    return _env

register_env_constructor(_initialize_env)

def initialize_commands():
    '''
        Deafult implementation of commands initialization
    '''
    from .commands import (
        register,
        _register,
        export,
        xids,
        compile as c4j_compile,
        checkout
    )
    export.initialize()
    _register('export', export.run)
    xids.initialize()
    _register('pids', xids.run_pids)
    _register('bids', xids.run_bids)
    _register('cids', xids.run_cids)
    c4j_compile.initialize()
    _register('compile', c4j_compile.run)
    _register('clean', c4j_compile.clean)
    checkout.initialize()
    _register('checkout', checkout.run)

register_bootstrap_function(initialize_commands)

def initialize_loaders():
    '''
        Deafult implementation of loaders initialization
    '''
    from .loaders import (
        register_loader,
        _register_loader,
        register_loader_lazy,
    )
    def register_project_loader(proj: str):
        register_loader_lazy(proj, proj, f'{proj}Loader', 1)

    register_loader_lazy('default', 'project_loader', 'ProjectLoader', 1)
    register_project_loader('Chart')
    register_project_loader('Cli')
    register_project_loader('Closure')
    register_project_loader('Codec')
    register_project_loader('Collections')
    register_project_loader('Compress')
    register_project_loader('Csv')
    register_project_loader('Gson')
    register_project_loader('JacksonCore')
    register_project_loader('JacksonDatabind')
    register_project_loader('JacksonXml')
    register_project_loader('Jsoup')
    register_project_loader('JxPath')
    register_project_loader('Lang')
    register_project_loader('Math')
    register_project_loader('Mockito')
    register_project_loader('Time')

register_bootstrap_function(initialize_loaders)

def start_cli():
    '''
        Deafult implementation of the entry point
    '''
    args = cli_manager._root_parser.parse_args()
    dest = env._config.cli_command_dest
    target = getattr(args, dest)
    delattr(args, dest)
    dispatcher = CommandDispatcher(env._context)
    context = dispatcher.get_execution_context(args=args, cli=True)
    util.cli_run(context, target)

register_entry_point(start_cli)

def initialize_system(system):
    '''
        Default definition of initialization order for the system

        Example: Change the bootstrap process without modifying this module
        
        from bootstrap import (
            register_bootstrap_function,
            initialize_system,
            register_initialization_order
        )

        def custom_initialization():
            print('hello')

        register_bootstrap_function(custom_initialization)

        def updated_order(system):
            initialize_system(system)
            system.custom_initialization

        register_initialization_order(updated_order)

        The previous code should be executed before accessing system.start
    '''
    system.initialize_environment
    system.initialize_cli
    system.initialize_commands
    system.initialize_loaders
    system.initialize_user_setup

register_initialization_order(initialize_system)