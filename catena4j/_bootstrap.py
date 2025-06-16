'''
    Low level system initialization APIs
'''
from . import env
from .env import (
    initialize_config,
    initialize_env,
    initialize_system_context,
)
from .cli.manager import init_root_parser, _init_subcommands
class BootstrapError(Exception):
    pass

class _StartupContext:
    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])
        super().__setattr__('functions', kwargs)

    def __getattribute__(self, name: str):
        if name.startswith('__') and name.endswith('__'):
            return super().__getattribute__(name)
        if name not in super().__getattribute__('functions'):
            raise BootstrapError(f'Could not find bootstrap function {name}')
        return super().__getattribute__(name)()


def initialize_cli():
    config = env._config
    init_root_parser(name=config.cli_program,
                     usage=config.cli_usage,
                     description=config.cli_description)
    _init_subcommands(title='Commands',
                      dest=config.cli_command_dest,
                      required=True)

def initialize_environment():
    initialize_config()
    initialize_env()
    initialize_system_context()

def initialize_user_setup():
    from . import user_setup

_reserved_bootstrap_functions = {
    'start': None
}
_bootstrap_functions = _reserved_bootstrap_functions.copy()
_start = None
_initialize = None
def register_bootstrap_function(f):
    name = f.__name__
    if name in _reserved_bootstrap_functions:
        raise BootstrapError(f'Name {name} is reserved and could not be registered')
    _bootstrap_functions[name] = f

def register_entry_point(f):
    global _start
    _start = f

def register_initialization_order(f):
    global _initialize
    _initialize = f

def create_context():
    '''
        Create a context object representing the abstract startup process,
        which has a entry to call in the startup script using context.start

        Variables _start, _initialize and _bootstrap_functions are hard coded
        in the function code because in most cases this function would be called
        only once.
    '''
    if _start is None:
        raise BootstrapError(f'Entry point of the program is not set')

    if _initialize is None:
        raise BootstrapError(f'Intialization order is not set')

    context = _StartupContext(**_bootstrap_functions)

    def start():
        _initialize(context)
        _start()

    context.start = start
    return context

register_bootstrap_function(initialize_environment)
register_bootstrap_function(initialize_cli)
register_bootstrap_function(initialize_user_setup)