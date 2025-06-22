from .loader import ContextAwareLoader

class ProjectLoader(ContextAwareLoader):
    def __init__(self, context):
        super().__init__(context=context)
        self._layout = None

    @property
    def src_layout(self):
        '''
            get the src directory layout of current context

            subclasses should implement method determine_src_layout
        '''
        if self._layout is None:
            self._layout = self.determine_layout()

        return self._layout['src']

    @property
    def test_layout(self):
        '''
            get the test directory layout of current context

            subclasses should implement method determine_test_layout
        '''
        if self._layout is None:
            self._layout = self.determine_layout()
        
        return self._layout['test']

    def determine_layout(self):
        '''
            Should return a dict with keys src and test,
            
            and the values mapped are the src and test directory layout
        '''
        raise NotImplementedError('This method should be implemented by subclasses')