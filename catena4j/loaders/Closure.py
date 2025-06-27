from .project_loader import ProjectLoader
from ..util import Git

class ClosureLoader(ProjectLoader):
    version_control_system_class = Git
    def determine_layout(self):
        return {
            'src': 'src',
            'test': 'test'
        }