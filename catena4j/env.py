'''
    Configurations which require dynamic evaluation
    and system level environment initialization
'''
from argparse import Namespace
from typing import Callable
from util import get_constant_class

_config = None
_config_mapping: dict = None

_env = None
_env_mapping: dict = None
_initialize_env: Callable = None

_context = None
_context_mapping: dict = None

def _build_system_read_only_obj(name, env):
    env['as_dict'] = lambda self:env
    t = get_constant_class(name, env)
    return t()

def initialize_config():
    import config
    global _config_mapping
    _config_mapping = config.__dict__.copy()
    for name in config.__dict__:
        if name.startswith('__') and name.endswith('__'):
            _config_mapping.pop(name)

    global _config
    _config = _build_system_read_only_obj('SystemConfig', _config_mapping)

def register_env_constructor(constructor: Callable):
    global _initialize_env
    _initialize_env = constructor

def initialize_env():
    global _env_mapping
    _env_mapping = _initialize_env()

    global _env
    _env = _build_system_read_only_obj('SystemEnv', _env_mapping)
    

def get_system_config():
    return _config

def get_system_env():
    return _env

def initialize_system_context():
    global _context_mapping
    _context_mapping = _env_mapping.copy()
    _context_mapping.update(_config_mapping)

    global _context
    _context = _build_system_read_only_obj('SystemContext', _context_mapping)


def get_system_context(copy=True):
    '''
        If copy is True, the return value would be the copied version
        of system context so that it could be modified
    '''
    if copy:
        return Context.get_instance()
    return _context

class Context(Namespace):
    def as_dict(self):
        return self.__dict__

    @staticmethod
    def get_instance():
        '''
            Get a modifiable version of system context
        '''
        return Context(**_context_mapping)
