from .project_loader import ProjectLoader
from ..util import Svn

class ChartLoader(ProjectLoader):
    version_control_system_class = Svn
    def determine_layout(self):
        return {
            'src': 'source',
            'test': 'tests'
        }