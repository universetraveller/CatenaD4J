from .parser import RootArgumentParser, LeafArgumentParser, RootHelpFormatter
from argparse import _SubParsersAction

_root_parser: RootArgumentParser = None
_subcommands: _SubParsersAction = None

class CommandLineError(Exception):
    pass

def get_root_parser():
    '''
        Get the parser used for the whole program
    '''
    return _root_parser

def init_root_parser(parser_class=RootArgumentParser,
                     name=None,
                     usage=None,
                     description=None,
                     formatter_class=RootHelpFormatter,
                     add_help=False,
                     **kwargs):
    '''
        Initialize the root parser
    '''
    global _root_parser
    _root_parser = parser_class(prog=name,
                                usage=usage,
                                description=description,
                                formatter_class=formatter_class,
                                add_help=add_help,
                                **kwargs)

def _check_root_parser_initialized():
    if _root_parser is None:
        raise CommandLineError(f'The root parser is not initialized')

def _init_subcommands(title="commands",
                      dest="command",
                      desc=None,
                      required=True,
                      parser_class=LeafArgumentParser,
                      **kwargs):
    global _subcommands
    _subcommands = _root_parser.add_subparsers(title=title,
                                               dest=dest,
                                               description=desc,
                                               required=required,
                                               parser_class=parser_class,
                                               **kwargs)

def init_subcommands(title="commands", dest="command", desc=None, **kwargs):
    '''
        Allow the root parser to manage subcommands
    '''
    _check_root_parser_initialized()
    _init_subcommands(title=title, dest=dest, desc=desc, **kwargs)

def _create_command(name: str, **kwargs) -> RootArgumentParser:
    return _subcommands.add_parser(name=name, **kwargs)

def _check_subcommands_initialized():
    if _subcommands is None:
        raise CommandLineError(f'Manager of subcommands is not initialized')

def _check_command_does_not_exist(name):
    if name in _subcommands.choices:
        raise CommandLineError(f'Command {name} exists')

def create_command(name: str, **kwargs) -> RootArgumentParser:
    '''
        Create a new subcommand managed by the root parser

        This function returns the parser that the new
        subcommand would use for further configuration
    '''
    _check_subcommands_initialized()
    _check_command_does_not_exist(name)
    return _create_command(name=name, **kwargs)

def get_command_parser(name: str) -> RootArgumentParser:
    '''
        Get the parser used by a subcommand
    '''
    _check_subcommands_initialized()
    return _subcommands.choices.get(name, None)

def register_command(parser: RootArgumentParser, alias=(), help=None):
    '''
        Experimental API to add an existing command parser
        as subcommand
    '''
    _check_subcommands_initialized()
    if help is not None:
        action = _subcommands._ChoicesPseudoAction(parser.prog, alias, help)
        _subcommands._choices_actions.append(action)
    
    for name in alias + (parser.prog,):
        _check_command_does_not_exist(name)
        _subcommands._name_parser_map[name] = parser


def parse_args(args=None, namespace=None):
    _check_root_parser_initialized()
    return _root_parser.parse_args(args=args, namespace=namespace)