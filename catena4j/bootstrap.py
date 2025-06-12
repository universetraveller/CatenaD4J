'''
    High level initialization methods including entry point
    of the program
'''
import cli.manager
import env
from env import register_env_constructor
from dispatcher import CommandDispatcher
import _bootstrap

def _initialize_env():
    return {}

register_env_constructor(_initialize_env)

def initialize_commands():
    pass

def initialize_loaders():
    pass

def start_cli():
    args = cli.manager._root_parser.parse_args()
    target = getattr(args, env._config.command_dest)
    delattr(args, env._config.command_dest)
    dispatcher = CommandDispatcher(env._context)
    context = dispatcher.get_execution_context(args=args, cli=False)
    context.run(target=target)

_bootstrap.register_bootstrap_function(initialize_commands)
_bootstrap.register_bootstrap_function(initialize_loaders)
_bootstrap.register_entry_point(start_cli)

def ordered_init(Bootstrap):
    Bootstrap.initialize_environment
    Bootstrap.initialize_cli
    Bootstrap.initialize_commands
    Bootstrap.initialize_loaders
    Bootstrap.initialize_user_setup

Bootstrap = _bootstrap.build(ordered_init)