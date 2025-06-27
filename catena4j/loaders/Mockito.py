from .project_loader import ProjectLoader
from . import LoaderError
from pathlib import Path
from ..util import Git

class MockitoLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'mockito'
    def determine_layout(self):
        cwd = Path(self.context.cwd)
        if (cwd / 'src' / 'main' / 'java').is_dir():
            return {
                'src': 'src/main/java',
                'test': 'src/test/java'
            }

        if (cwd / 'src').is_dir():
            return {
                'src': 'src',
                'test': 'test'
            }
        
        raise LoaderError(f'Unknown layout for working directory: {cwd}')