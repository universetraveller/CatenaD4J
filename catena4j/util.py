from argparse import Namespace
from pathlib import Path
from typing import Callable, Tuple
from shutil import which

def search_cache(cache: Path, check: Callable=None, fix: Tuple=None, args=(), kwargs={}):
    '''
        Find result from the cache path or find it using the
        provided function and then store the result to the cache

        cache: Path to cache file

        check: Function to check if the result should be updated

        fix: Function to get a updated result

        args and kwargs: arguments of the fix function
    '''
    if cache.is_file():
        with cache.open() as f:
            content = f.read()

        if check and check(content):
            return content

    if not fix:
        raise TypeError('Cache miss occured but no fix function is provided')
    content = fix(*args, **kwargs)
    if not cache.parent.is_dir():
        cache.parent.mkdir()
    with cache.open('w') as f:
        f.write(content)
    return content

def find_path(target, parent_level=None, mode=1, path=None):
    '''
        Find a file or the directory it is placed from path (default: PATH)
    '''
    # ensure it is not a symlink
    result = Path(which(target, mode=mode, path=path)).resolve()
    if result is None:
        raise FileNotFoundError(f'Failed to find {target}')
    if parent_level:
        result = result.parents[parent_level]
    return str(result)

def get_constant_class(name='Constant', namespace={}, slots=(), bases=()):
    '''
        Get a constant class whose instances' attributes outside
        slots are not allowed to modify

        Internal attributes could be accessed using __class__
    '''
    namespace['__slots__'] = slots
    return type(name, bases, namespace)

def build_args(**kwargs):
    '''
        Tool function to create args object
    '''
    return Namespace(**kwargs)
