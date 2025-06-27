from .project_loader import ProjectLoader
from . import LoaderError
from pathlib import Path
from ..util import Git

class TimeLoader(ProjectLoader):
    version_control_system_class = Git
    def determine_layout(self):
        cwd = Path(self.context.cwd)
        if (cwd / 'src' / 'main' / 'java').is_dir():
            return {
                'src': 'src/main/java',
                'test': 'src/test/java'
            }

        if (cwd / 'src' / 'java').is_dir():
            return {
                'src': 'src/java',
                'test': 'src/test'
            }
        
        raise LoaderError(f'Unknown layout for working directory: {cwd}')