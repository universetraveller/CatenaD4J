from .loader import ContextAwareLoader
from pathlib import Path

class ProjectLoader(ContextAwareLoader):
    version_control_system_class = None
    project_name = None

    def __init__(self, context):
        super().__init__(context=context)
        self._layout = None
        if self.version_control_system_class is None:
            raise NotImplementedError("Subclasses must set a version control system class")

        if self.project_name is None:
            raise NotImplementedError("Subclasses must set a project name")

    @property
    def version_control_system(self):
        if not hasattr(self, '_version_control_system'):
            self._version_control_system = self.version_control_system_class(self)
        return self._version_control_system

    def checkout_revision(self, revision_id: str, wd: str):
        return self.version_control_system.checkout_revision(revision_id, wd)

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

    @property
    def repo_path(self):
        if not hasattr(self, 'rel_to_repo'):
            self.rel_to_repo = self.version_control_system_class \
                                   .format_name(self.project_name)

        return Path(self.context.d4j_home,
                    self.context.d4j_rel_repositories,
                    self.rel_to_repo)
    
    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        '''
            Project specific works, return a boolean indicating if there
            are file changes
        '''
        return False