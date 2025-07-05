from argparse import Namespace
from pathlib import Path
from typing import Callable, Iterable, Tuple
from shutil import which
from sys import stdout, stderr, getdefaultencoding, exit as sys_exit
from locale import getpreferredencoding
import subprocess
from .exceptions import Catena4JError
import os
from platform import system as get_system_name

ENCODINGS = ('utf-8', 'latin-1')
def set_encodings(encodings):
    global ENCODINGS
    ENCODINGS = encodings

def open_and_write(file: Path, content: str, mode: str, encoding=None):
    if not file.parent.is_dir():
        file.parent.mkdir(parents=True)
    for enc in ENCODINGS if encoding is None else (encoding,):
        try:
            with file.open(mode, encoding=enc) as f:
                f.write(content)
            # encounters bugs when writing files to Jsoup if no return is here
            # the second file writing raises error which makes no content written
            # while making the original file being empty
            return
        except UnicodeEncodeError:
            continue

def write_file(file: Path, content: str, encoding=None):
    '''
        Unified API used to write a file for better encoding control
    '''
    open_and_write(file, content, 'w', encoding)

def append_file(file: Path, content: str, encoding=None):
    open_and_write(file, content, 'a', encoding)

def read_file(file: Path, encoding=None):
    '''
        Unified API used to read a file for better encoding control
    '''
    if file.is_file():
        for enc in ENCODINGS if encoding is None else (encoding,):
            try:
                with file.open(encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
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
        raise Catena4JError('Cache miss occured but no fix function is provided')

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
        raise Catena4JError(f'Failed to find {target}')
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

def printc_flush():
    stderr.flush()

def printc_encoding():
    return stderr.encoding.lower()

def printc(content):
    stderr.write(content)

def print_result(result: str, out=None):
    if out is None:
        out = stdout
    out.write(result)

def get_console_encoding():
    return stdout.encoding or \
           getpreferredencoding() or \
           getdefaultencoding() or \
           stderr.encoding

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
        return (
                False,
                bytes('TIMEOUT', 'utf-8'),
                bytes(
                'Command <{}> timeout after {} seconds.'.format(' '.join(cmd), timeout),
                'utf-8'
                    )
                )

_META_EXEC_ERR_MSG = 'Failed to run command: {command}\n\n{stdout}\n\n{stderr}\n'
def run_command_task(cmd,
                     wd,
                     *,
                     meta_message=_META_EXEC_ERR_MSG,
                     task_printer=None):
    enc = get_console_encoding()

    if task_printer is not None:
        msg = ['Run command: ' + ' '.join(cmd)] if task_printer.verbose else []
        task_printer.start(*msg)

    ret, out, err = run_command(cmd=cmd, cwd=wd)

    out = out.decode(enc)

    if not ret:
        if task_printer is not None:
            task_printer.fail()

        raise Catena4JError(meta_message.format(command=' '.join(cmd),
                                                stdout=out,
                                                stderr=err.decode(enc)))

    if task_printer is not None:
        msg = [out, err.decode(enc)] if task_printer.verbose else []
        task_printer.done(*msg)

    return out.strip()

def toolkit_execute(main,
                    wd,
                    context,
                    *,
                    meta_message=_META_EXEC_ERR_MSG,
                    java_options=(),
                    args=(),
                    task_printer=None):
    cmd = get_toolkit_command(context,
                              *java_options,
                              main,
                              *args,
                              basedir=wd)

    return run_command_task(cmd,
                            wd,
                            meta_message=meta_message,
                            task_printer=task_printer)

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
    
def do_nothing(*args, **kwargs):
    pass

class TaskPrinter:
    START = None
    DONE = None
    FAIL = None
    ANCHOR = None
    PADDING = None

    @classmethod
    def configurate(cls,
                    start='RUNNING',
                    done='DONE',
                    fail='FAILED',
                    anchor=75,
                    padding='.'):
        cls.START = start
        lstart = len(start)
        cls.DONE = done + ' ' * (lstart - len(done))
        cls.FAIL = fail + ' ' * (lstart - len(fail))
        cls.ANCHOR = anchor
        cls.PADDING = padding

    @staticmethod
    def print_messages(messages):
        for i in messages:
            printc(i + '\n')

    @classmethod
    def _start(cls, msg):
        printc(msg + cls.START)
        printc_flush()

    @classmethod
    def _done(cls, msg):
        printc(f'\r{msg}{TaskPrinter.DONE}\n')

    @classmethod
    def _fail(cls, msg):
        printc(f'\r{msg}{TaskPrinter.FAIL}\n')

    def __init__(self, title, anchor=-1):
        if anchor < 0:
            anchor = TaskPrinter.ANCHOR
        length = len(title)
        self.msg = (title[:anchor] if length >= anchor else \
                    title + TaskPrinter.PADDING * (anchor - length)) + ' '
        self.verbose = False

    def start(self, *msg):
        TaskPrinter.print_messages(msg)
        TaskPrinter._start(self.msg)

    def done(self, *msg):
        TaskPrinter._done(self.msg)
        TaskPrinter.print_messages(msg)
    
    def fail(self, *msg):
        TaskPrinter._fail(self.msg)
        TaskPrinter.print_messages(msg)

    def adapt_no_done(self):
        self._ori_done = self.done
        self.done = do_nothing
        return self

    def adapt_no_start(self):
        self._ori_start = self.start
        self.start = do_nothing
        return self

    def adapt_done(self):
        self.done = self._ori_done
        return self

    def adapt_start(self):
        self.start = self._ori_start
        return self
    
    def adaptor(self):
        '''
            Adapt to allow one printer be used across multiple tasks

            There are four modes of the adapted printer

            the first access will adapt the printer to skip the done method
            coule be used for task at the beginning of the tasks chain

            the second access will adapt the printer to skip the start method
            coule be used for tasks at the middle of the tasks chain

            the third access will adapt the printer to resume the end method
            coule be used for tasks at the end of the tasks chain

            the final access will adapt the printer to resume the start method
            used to fully restore the printer
        '''
        yield self.adapt_no_done()
        yield self.adapt_no_start()
        yield self.adapt_done()
        yield self.adapt_start()

def auto_task_print(title, f, args=(), kwargs={}, reraise=True, **printer_args):
    printer = TaskPrinter(title, **printer_args)
    try:
        printer.start()
        result = f(*args, **kwargs)
    except:
        printer.fail()
        if reraise:
            raise
        return None
    printer.done()
    return result
    
def auto_task_no_print(a, f, args=(), kwargs={}, b=None, **c):
    return f(*args, **kwargs)

def get_auto_task_printer(context):
    '''
        get suitable printer function for different contexts

        this is a workaround and expected to address in another way
    '''
    # use context.CLI to avoid circular import
    if context.mode == context.CLI:
        return auto_task_print
    return auto_task_no_print

def noreturn(f, *args, **kwargs):
    try:
        f(*args, **kwargs)
        sys_exit(0)
    except Catena4JError as e:
        tb = e.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        
        frame = tb.tb_frame
        _globals = frame.f_globals
        code = frame.f_code
        if '__name__' in _globals:
            fullname = _globals.get('__name__') + '.' + code.co_name
        else:
            fullname = code.co_filename

        lineno = tb.tb_lineno
        message = str(e)

        printc(f'{message}\n  at {fullname}:{lineno}\n')

        sys_exit(1)

protected_directories = None
def build_protected_directories():
    global protected_directories
    protected_directories = set()
    
    os_env = os.environ

    protected_directories.add(str(Path.home()))
    if get_system_name() == 'Windows':
        keys = ("SystemDrive", "WINDIR", "ProgramFiles", "ProgramFiles(x86)",
                "APPDATA", "LOCALAPPDATA", "USERPROFILE")
        protected_directories.add('C:/')
        protected_directories.add('C:/Users')
        for key in keys:
            if key in os_env:
                protected_directories.add(str(Path(os_env.get(key)).resolve()))
    else:
        protected_directories.update(
            ("/", "/home", "/usr", "/etc", "/bin", "/sbin", "/lib", "/opt", "/var")
        )

def is_protected_directory(name: str):
    if protected_directories is None:
        build_protected_directories()
    return name in protected_directories

class Vcs:
    command = None
    def __init__(self, loader):
        if self.command is None:
            raise NotImplementedError('Subclasses must set a command')
        self.loader = loader

    @classmethod
    def format_name(cls, name):
        raise NotImplementedError(f'Subclasses should implement this method')

    @classmethod
    def run(cls, *args, wd, printer=None):
        return run_command_task([cls.command, *args], wd, task_printer=printer)

    def checkout_revision(self, revision_id, wd):
        raise NotImplementedError(f'Subclasses should implement this method')

    def export_diff(self, a, b, output: Path=None):
        raise NotImplementedError(f'Subclasses should implement this method')


class Git(Vcs):
    command = 'git'
    @classmethod
    def format_name(cls, name):
        return f'{name}.git'

    @classmethod
    def clone(cls, src, dest):
        return cls.run('clone', src, dest, wd=None)

    @classmethod
    def init(cls, wd):
        return cls.run('init', wd=wd)

    @classmethod
    def apply(cls, patch, n, wd):
        return cls.run('apply', f'-p{n}', patch, wd=wd)

    @classmethod
    def apply_check(cls, patch, n, wd):
        # do not use cls.run here because it will raise
        # exceptions when the check not passes
        return run_command(['git', 'apply', '--check', f'-p{n}', patch], cwd=wd)

    @classmethod
    def config(cls, name, value, wd):
        return cls.run('config', name, value, wd=wd)

    @classmethod
    def clean(cls, wd):
        return cls.run('clean', '-xdf', wd=wd)

    @classmethod
    def checkout(cls, commit, wd):
        return cls.run('checkout', commit, wd=wd)

    @classmethod
    def add_all(cls, wd):
        return cls.run('add', '-A', wd=wd)

    @classmethod
    def commit_all(cls, message, wd):
        return cls.run('commit', '-a', '-m', message, wd=wd)

    @classmethod
    def tag(cls, name, wd):
        return cls.run('tag', name, wd=wd)

    def export_diff(self, a, b, output: Path=None):
        # git supports --output to write the patch to a file
        # why defects4j do not use that?
        cmd = [f'--git-dir={str(self.loader.repo_path)}',
               'diff',
               '--no-ext-diff',
               '--binary']
        if output is not None:
            cmd.append('--output')
            cmd.append(str(output))
        out = self.run(*cmd, a, b)
        return out

    def checkout_revision_with_printer(self, revision_id, wd, printer):
        adaptor = printer.adaptor()
        path = self.loader.repo_path
        self.run('clone', str(path), wd,
                 wd=None,
                 printer=next(adaptor))
        next(adaptor)
        self.run('checkout', revision_id,
                 wd=wd,
                 task_printer=next(adaptor))
        next(adaptor)

    def checkout_revision(self, revision_id, wd):
        path = self.loader.repo_path
        self.clone(str(path), wd)
        self.checkout(revision_id, wd)

class Svn(Vcs):
    command = 'svn'
    @classmethod
    def format_name(cls, name):
        return f'{name}/trunk'

    def checkout_revision(self, revision_id, dest):
        path = self.loader.repo_path
        return self.run('-r', revision_id, 'co', path.as_uri(), dest, wd=None)

    def export_diff(self, a, b, output: Path=None):
        # svn supports --git option to output git style patches
        # why defects4j do not use that?
        path = self.loader.repo_path
        out = self.run('diff', f'-r{a}:{b}', path.as_uri(), wd=None)
        if output is not None:
            write_file(output, out + '\n')
        return out

def dict_to_properties(mapping: dict):
    return '\n'.join([f'{item[0]}={item[1]}' for item in mapping.items()])

def write_properties(file: Path, mapping: dict):
    write_file(file, dict_to_properties(mapping))

def detect_apply_layout(file: Path, wd: str):
    # defects4j checks n = (1, 0, 2) for git apply -p<n> patch
    
    #pattern = r'(?m)^diff --git a/(\S+)|^Index: (\S+)|^---\s(?!/dev/null)(\S+)'

    # near all patches could be applied using n=1 so it is not necessary to optimize
    # but if multiple types of patches are roughly the same number we can try to check
    # the existence of file to apply and the type of patch through part of the content

    patch = str(file)

    for i in (1, 0, 2):
        if Git.apply_check(patch, i, wd)[0]:
            return i

    raise Catena4JError(f'Failed to apply {patch} (n={i})')

def apply_patch(file: Path, wd: str, context=None):
    # context is a placeholder because we may add a cache for the
    # layout in future
    return Git.apply(str(file), detect_apply_layout(file, wd), wd)

def run_apply_patch_task(file: Path, wd: str, context=None):
    # a function in util module can print something, that is odd...
    # just transfer the core logic to another function
    auto_task_print = get_auto_task_printer(context)
    auto_task_print('Apply patch',
                    apply_patch,
                    (file, wd, context))
    
class FileSlice:
    '''
        Support operators << and >>
    '''
    def __init__(self, file: 'File', start, stop):
        self.file = file
        self.start = 0 if start is None else start
        self.stop = self.file.max_line if stop is None else stop

    def __lshift__(self, value):
        if isinstance(value, str):
            self.file.insert(value, self.stop - 1, False)
        elif isinstance(value, Iterable):
            self.file.insert_all(value, self.stop - 1, False)
        else:
            super().__lshift__(value)

    def __rrshift__(self, value):
        if isinstance(value, str):
            self.file.insert(value, self.start)
        elif isinstance(value, Iterable):
            self.file.insert_all(value, self.start)
        else:
            super().__lshift__(value)

    def __repr__(self):
        return ''.join([self.file.format_line(line) \
                        for line in self.file.content[self.start:self.stop]])

class File:
    '''
        File abstraction that supports insert, replace and delete operations

        Operators supported: =, del, << and >>

        f = File(path)

        # insert before
        f.insert(...)
        f.insert_all(..., False)
        str | Iterable >> f[...]

        # insert after
        f.insert(..., False)
        f.insert_all(..., False)
        f[...] << str | Iterable

        # replace
        f.replace(...)
        f[...] = str | Iterable

        # delete
        f.delete(...)
        del f[...]
    '''
    def __init__(self, path: Path):
        content = read_file(path)
        if content is None:
            raise Catena4JError(f'File {path} does not exist')
        
        self.initialize(content)
        

    def initialize(self, s: str):
        self._original = s.splitlines(True)
        self.content = [[[], line, []] for line in self._original]
        self.max_line = len(self.content)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.get(key.start, key.stop)
        elif isinstance(key, int):
            return self.get(key, key + 1)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            self.replace(key.start, key.stop, value)
        elif isinstance(key, int):
            self.replace(key, key + 1, value)
        else:
            super().__setitem__(key, value)
    
    def __delitem__(self, key):
        if isinstance(key, slice):
            self.delete(key.start, key.stop)
        elif isinstance(key, int):
            self.delete(key, key + 1)
        else:
            super().__delitem__(key)

    def __repr__(self):
        return self.to_s()

    def to_s_fixed_lineno(self):
        return '\n'.join([self.format_line(line).replace('\n', ' ') \
                          for line in self.content])

    def format_line(self, line):
        return ''.join(reversed(line[0])) + line[1] + ''.join(line[2])

    def to_s(self):
        return ''.join([self.format_line(line) for line in self.content])

    def insert_all(self, content, at_index, front=True):
        i = 0 if front else 2
        self.content[at_index][i].extend(content)

    def insert(self, content, at_index, front=True):
        i = 0 if front else 2
        self.content[at_index][i].append(content)

    def delete_line(self, index):
        self.delete(from_index=index, to_index=index + 1)

    def delete(self, from_index, to_index):
        while from_index < to_index:
            self.content[from_index][1] = ""
            from_index += 1

    def replace_line(self, index, with_content):
        self.replace(from_index=index, to_index=index + 1, with_content=with_content)

    def replace(self, from_index, to_index, with_content):
        if isinstance(with_content, str):
            self.content[from_index][1] = with_content
            self.delete(from_index + 1, to_index)
        elif isinstance(with_content, Iterable):
            length = len(with_content)
            to_index = min(from_index + length, to_index)
            i = 0
            while from_index < to_index:
                self.content[from_index][1] = with_content[i]
                from_index += 1
                i += 1
            if i < length:
                self.insert_all(with_content[i:], to_index - 1, False)
        else:
            raise TypeError('Argument with_content should be either str or Iterable '
                            f'(got {type(with_content)})')

    def get_line(self, index):
        return self.get(from_index=index, to_index=index + 1)

    def get(self, from_index, to_index):
        return FileSlice(self, from_index, to_index) 
    
    def reindex(self):
        self.initialize(self.to_s())

class Files:
    def __init__(self, base):
        self.base = Path(base).absolute()
        self.files = {}

    def get_file(self, path):
        files = self.files
        path = self.base / path
        if not path in files:
            files[path] = File(path)
        return files[path]
    
    def write_back(self):
        files = self.files
        for path in files:
            write_file(path, str(files[path]))