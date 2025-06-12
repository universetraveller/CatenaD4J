'''
    System initialization
'''
import env
from env import (
    initialize_config,
    initialize_env,
    initialize_system_context,
)
from cli.manager import init_root_parser, _init_subcommands
class BootstrapError(Exception):
    pass

_preserved_bootstrap_functions = {'start'}
class _Bootstrap:
    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])
        for name in _preserved_bootstrap_functions:
            kwargs[name] = None
        super().__setattr__('functions', kwargs)

    def __getattribute__(self, name: str):
        if name.startswith('__') and name.endswith('__'):
            return super().__getattribute__(name)
        if name not in super().__getattribute__('functions'):
            raise BootstrapError(f'Could not found bootstrap function {name}')
        return super().__getattribute__(name)()


def initialize_cli():
    config = env._config
    init_root_parser(name=config.program,
                     usage=config.usage,
                     description=config.description)
    _init_subcommands(title='Commands',
                      dest=config.command_dest)

def initialize_environment():
    initialize_config()
    initialize_env()
    initialize_system_context()

def initialize_user_setup():
    import user_setup

_bootstrap_functions = {}
_system_start = None
def register_bootstrap_function(f):
    name = f.__name__
    if name in _preserved_bootstrap_functions:
        raise BootstrapError(f'Function {name} is a preserved bootstrap function')
    _bootstrap_functions[name] = f

def register_entry_point(f):
    global _system_start
    _system_start = f

def build(sys_load):
    if _system_start is None:
        raise BootstrapError(f'Entry point of the program is not set')

    bootstrap = _Bootstrap(**_bootstrap_functions)

    def start():
        sys_load(bootstrap)
        _system_start()

    bootstrap.start = start
    return bootstrap

register_bootstrap_function(initialize_environment)
register_bootstrap_function(initialize_cli)
register_bootstrap_function(initialize_user_setup)