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
from .util import printc_encoding, TaskPrinter

class BootstrapError(Exception):
    pass

_start = None
_initialize = None

def start():
    '''
        The true entry point of the program

        Using this function after bootstrap is imported is fine
        but invoking it directly would cause BootstrapError raised
        bacause the entry point and the initialization order are
        both set using the high level initialization API.
    '''
    if _start is None:
        raise BootstrapError(f'Entry point of the program is not set')

    if _initialize is None:
        raise BootstrapError(f'Intialization order is not set')

    _initialize(StartupContext)
    _start()

_reserved_bootstrap_functions = {
    'start': start
}
_bootstrap_functions = _reserved_bootstrap_functions.copy()

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

class _StartupContext(type):
    def __getattribute__(cls, name: str):
        if name.startswith('__') and name.endswith('__'):
            return super().__getattribute__(name)
        if name not in _bootstrap_functions:
            raise BootstrapError(f'Could not find bootstrap function {name}')
        return _bootstrap_functions[name]()

class StartupContext(metaclass=_StartupContext):
    '''
        This class serves as the entry of the system.

        To extend this package, change the entry point and/or the initialization process
        using the related functions.

        To use this package as a library, call related initialization functions before
        accessing the components.

        Before the start attribute is accessed, the order of initialization functions
        to be called and the entry point could be changed.
    '''
    def __new__(cls):
        '''
            For setuptools's entry_points setting
        '''
        cls.start

def initialize_cli():
    config = env._config

    init_root_parser(name=config.cli_program,
                     usage=config.cli_usage,
                     description=config.cli_description)

    _init_subcommands(title='Commands',
                      dest=config.cli_command_dest,
                      required=True)

    if config.rich_output:
        PRINT_START = '\033[1;34mRUNNING\033[0m'
        PRINT_DONE = '\033[1;32mDONE\033[0m'
        PRINT_FAIL = '\033[1;31mFAILED\033[0m'
        if 'utf' in printc_encoding():
            PRINT_START = '⏳ ' + PRINT_START
            PRINT_DONE = '✅ ' + PRINT_DONE
            PRINT_FAIL = '❌ ' + PRINT_FAIL
    else:
        PRINT_START = 'RUNNING'
        PRINT_DONE = 'DONE'
        PRINT_FAIL = 'FAILED'

    TaskPrinter.configurate(start=PRINT_START,
                            done=PRINT_DONE,
                            fail=PRINT_FAIL,
                            anchor=config.printer_message_length,
                            padding=config.printer_padding_character)

def initialize_environment():
    initialize_config()
    initialize_env()
    initialize_system_context()

def initialize_user_setup():
    from . import user_setup

register_bootstrap_function(initialize_environment)
register_bootstrap_function(initialize_cli)
register_bootstrap_function(initialize_user_setup)