from .loader import ContextAwareLoader

class ProjectLoader(ContextAwareLoader):
    def __init__(self, context):
        super().__init__(context=context)