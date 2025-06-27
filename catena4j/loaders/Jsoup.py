from .project_loader import ProjectLoader
from ..util import Git

class JsoupLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'jsoup'
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }