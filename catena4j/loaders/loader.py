from ..dispatcher import ExecutionContext

class Loader:
    pass

class ContextAwareLoader(Loader):
    def __init__(self, context: ExecutionContext):
        self.context = context