from loaders.loader import Loader
import util

_loaders = {
}

_default_loader = None

class LoaderError(Exception):
    pass

def _register_loader(name: str, loader: Loader):
    _loaders[name] = loader

def register_loader(name: str, loader: Loader):
    '''
        Register a loader class

        Typically only one or no loader would be used.
        Would a lazy import version be better?
    '''
    if name in _loaders:
        raise LoaderError(f'Loader for {name} exists')

    _register_loader(name=name, loader=loader)


def register_loader_lazy(name, package, clazz):
    '''
        Experimental lazy import implementation for loaders
    '''
    def __new__(cls, *args, **kwargs):
        _loaders.pop(name)
        m = __import__(package)
        clz = getattr(m, clazz)
        _loaders[name] = clz
        return clz(*args, **kwargs)
    
    t = type(clazz, (), {'__new__': __new__})
    _loaders[name] = t

def get_loader(name: str):
    '''
        Get a loader class
    '''
    if name in _loaders:
        return _loaders.get(name)
    
    raise LoaderError(f'Loader for {name} is not registered')

def remove_loader(name: str):
    _loaders.pop(name, None)
    
def register_default_loader(loader: Loader):
    global _default_loader
    _default_loader = loader

def get_default_loader():
    if _default_loader is None:
        register_default_loader(get_loader("default"))
    return _default_loader
