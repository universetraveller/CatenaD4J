from .loader import Loader

_loaders = {
}

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


_globals = None
def register_loader_lazy(name, package, clazz, level):
    '''
        Experimental lazy import implementation for loaders
    '''
    global _globals
    if _globals is None:
        _globals = globals()

    def __new__(cls, *args, **kwargs):
        _loaders.pop(name)
        from importlib import __import__
        m = __import__(package, globals=_globals, level=level)
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