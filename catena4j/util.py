from argparse import Namespace
from pathlib import Path
from typing import Callable, Iterable, Tuple
from shutil import which
from sys import stdout, stderr, getdefaultencoding
from locale import getpreferredencoding
import subprocess

def write_file(file: Path, content: str):
    if not file.parent.is_dir():
        file.parent.mkdir(parents=True)
    with file.open('w') as f:
        f.write(content)

def read_file(file: Path):
    if file.is_file():
        with file.open() as f:
            return f.read()
    return None

def get_cache_path(context: Namespace, *parts):
    return Path(context.c4j_home, context.rel_cache_dir, *parts)

def search_cache(cache: Path, check: Callable=None, fix: Tuple=None, args=(), kwargs={}):
    '''
        Find result from the cache path or find it using the
        provided function and then store the result to the cache

        cache: Path to cache file

        check: Function to check if the result should be updated

        when check is None, the default behaviour is cache miss

        fix: Function to get a updated result

        when fix is None, the default behaviour is raising error

        args and kwargs: arguments of the fix function
    '''
    content = read_file(cache)
    if content and check and check(content):
        return content

    if not fix:
        raise TypeError('Cache miss occured but no fix function is provided')

    content = fix(*args, **kwargs)
    write_file(cache, content)
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

def read_properties(*path_parts):
    props = {}
    content = read_file(Path(*path_parts))
    if content is None:
        return None
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        index = line.find('=')
        if index != -1:
            props[line[:index].rstrip()] = line[index + 1:].lstrip()
    return props

def printc():
    pass

def print_result(result: str, out=None):
    if out is None:
        out = stdout
    out.write(result)

def get_console_encoding():
    return stdout.encoding or getpreferredencoding() or getdefaultencoding() or stderr.encoding

def get_toolkit_command(context: Namespace, *args, basedir=None):
    if basedir is None:
        basedir = context.cwd
    d4j_home = context.d4j_home
    c4j_home = context.c4j_home
    ant_cp = str(Path(d4j_home, context.d4j_rel_ant_lib))
    toolkit_cp = str(Path(c4j_home, context.c4j_rel_toolkit_lib))
    d4j_props = str(Path(c4j_home, context.c4j_rel_d4j_properties))
    cmd = ['java', '-cp', f':{ant_cp}:{toolkit_cp}', f'-Dbasedir={basedir}',
           f'-Dd4j.home={d4j_home}', f'-Dc4j.d4j.properties={d4j_props}']
    cmd.extend(args)
    return cmd

def run_command(cmd, cwd=None, timeout=None):
    try:
        finished = subprocess.run(cmd,
                                  capture_output=True,
                                  cwd=cwd,
                                  timeout=timeout)
        finished.check_returncode()
        return True, finished.stdout, finished.stderr
    except subprocess.CalledProcessError:
        return False, finished.stdout, finished.stderr
    except subprocess.TimeoutExpired:
        return (False,
                bytes('TIMEOUT', 'utf-8'),
                bytes('Command <{}> timeout after {} seconds.'.format(' '.join(cmd), timeout), 'utf-8'))

def get_project_cache(cache, proj, name, fallback, args=(), kwargs={}):
    if proj not in cache:
        cache[proj] = {}

    if name not in cache[proj]:
        cache[proj][name] = fallback(*args, **kwargs)

    return cache[proj][name]

def close_project_cache(cache, proj, name):
    if name:
        cache[proj].pop(name)
    else:
        cache.pop(proj)

def read_simple_csv(path, sep=',', remove_header=True):
    f = read_file(path)
    if f is None:
        return None
    return list(map(lambda l : l.split(sep), f.splitlines()[1 if remove_header else 0:]))