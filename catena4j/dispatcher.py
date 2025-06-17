from .commands import get_entry
from .env import Context
from argparse import Namespace

class ExecutionContext(Context):
    CLI = 0
    '''
        Run as normal command line interface
    '''
    API = 1
    '''
        Standard output and file output would be ignored
        
        Commands run in this mode would only do computation tasks and return
        the result.
    '''
    def __init__(self, args, mode, dispatcher):
        '''
            This function assumes users do not set general attribute names,
            and would override attributes args, mode and dispatcher if exists
        '''
        super().__init__(**dispatcher.context.as_dict())
        self.args: Namespace = args
        self.mode: int = mode
        self.dispatcher: CommandDispatcher = dispatcher

    def run(self, target: str):
        return get_entry(target)(self)

def dispatch(target: str, context: ExecutionContext):
    return context.run(target=target)

class CommandDispatcher:
    def __init__(self, context: Context=None):
        if context is None:
            self.context = Context.get_instance()
        self.context = context

    def get_execution_context(self, args, cli=False):
        return ExecutionContext(args=args,
                                mode=ExecutionContext.CLI if cli else \
                                        ExecutionContext.API,
                                dispatcher=self)

    def run(self, target: str, args: Namespace, cli=False):
        context = self.get_execution_context(args=args, cli=cli)
        return context.run(target=target)