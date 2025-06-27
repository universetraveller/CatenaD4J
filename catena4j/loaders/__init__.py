from .loader import Loader

_loaders = {
}

_loader_mapping = {
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

def set_project_loader(proj: str, loader: str):
    '''
        Set the name of loader used to load a project
    '''
    _loader_mapping[proj] = loader

def get_project_loader(proj: str):
    '''
        Get the loader used to load a project

        Search list: registered name, project's name and default
    '''
    # use a registered name or the project's name
    loader_name = resolve_loader_name(proj)

    if loader_name in _loaders:
        return _loaders.get(loader_name)

    # fallback to default loader
    if 'default' in _loaders:
        return _loaders.get('default')

    raise LoaderError(f'No loader found for project {proj}')
        
def resolve_loader_name(name: str):
    '''
        Resolve the final mapping of a provided name
        and avoid circular reference
    '''
    # optimization here because most time there is no mapping chain
    if name in _loader_mapping:
        visited = set([name])
        name = _loader_mapping.get(name)
        while name in _loader_mapping:
            if name in visited:
                raise LoaderError(f'Circular loader mapping detected from {name}')
            visited.add(name)
            name = _loader_mapping.get(name)
    return name

def is_valid_loader_name(project: str):
    '''
        Check if a loader could be retrieved using the provided name
    '''
    return resolve_loader_name(project) in _loaders