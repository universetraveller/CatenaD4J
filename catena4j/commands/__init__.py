from typing import Callable

_commands = {
}

class CommandError(Exception):
    pass

def has_command(command: str):
    '''
        Check if a command has been registered
    '''
    return command in _commands

def _register(command: str, entry: Callable):
    _commands[command] = entry

def register(command: str, entry: Callable, replace=False):
    '''
        Register a command entry
    '''
    if command in _commands and not replace:
        raise CommandError(f'Command {command} exists')

    _register(command=command, entry=entry)

'''
    @func0
    def func1(args):
        ...
    
    works like func1 = func0(func1)

    so:
    @func0(args)
    def func1(args):
        ...
    works like func1 = func0(args)(func1)
'''
def Command(name: str):
    '''
        [Experimental API]
        Decorator function for the entry method
        to register command at its definition
    '''
    def wrapper(entry: Callable):
        register(command=name, entry=entry)
        return entry

    return wrapper

def get_entry(command: str):
    '''
        Get the entry point of a command
    '''
    if command in _commands:
        return _commands.get(command)

    raise CommandError(f'Command {command} is not registered')

def remove_command(command: str):
    '''
        Remove a command from the registry
    '''
    _commands.pop(command, None)