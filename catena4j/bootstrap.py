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
    create_context
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
        'workdir': os.getcwd()
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
    )
    export.initialize()
    _register('export', export.run)

register_bootstrap_function(initialize_commands)

def initialize_loaders():
    '''
        Deafult implementation of loaders initialization
    '''
    from .loaders import (
        register_loader,
        _register_loader,
        register_loader_lazy,
        project_loader
    )
    register_loader_lazy('default', 'project_loader', 'ProjectLoader', 1)

register_bootstrap_function(initialize_loaders)

def start_cli():
    '''
        Deafult implementation of the entry point
    '''
    args = cli_manager._root_parser.parse_args()
    target = getattr(args, env._config.command_dest)
    delattr(args, env._config.command_dest)
    dispatcher = CommandDispatcher(env._context)
    context = dispatcher.get_execution_context(args=args, cli=False)
    context.run(target=target)

register_entry_point(start_cli)

def initialize_system(system):
    '''
        Default definition of initialization order for the system
    '''
    system.initialize_environment
    system.initialize_cli
    system.initialize_commands
    system.initialize_loaders
    system.initialize_user_setup

register_initialization_order(initialize_system)

system = create_context()
'''
    This object serves as the entry of the system.

    To extend this package, change the entry point and/or the initialization process
    using the related functions.

    To use this package as a library, call related initialization functions before
    accessing the components.

    Before the start attribute is accessed, the order of initialization functions
    to be called and the entry point could be changed.
'''