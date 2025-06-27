from .project_loader import ProjectLoader
from ..util import Git

class JacksonXmlLoader(ProjectLoader):
    version_control_system_class = Git
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }