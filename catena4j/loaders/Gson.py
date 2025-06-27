from .project_loader import ProjectLoader
from ..util import Git

class GsonLoader(ProjectLoader):
    version_control_system_class = Git
    def determine_layout(self):
        return {
            'src': 'gson/src/main/java',
            'test': 'gson/src/test/java'
        }