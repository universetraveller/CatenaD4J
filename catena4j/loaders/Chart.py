from pathlib import Path
from .project_loader import ProjectLoader
from ..util import Svn
from .post_checkout_util import fix_compilation_errors

class ChartLoader(ProjectLoader):
    version_control_system_class = Svn
    project_name = 'jfreechart'
    def determine_layout(self):
        return {
            'src': 'source',
            'test': 'tests'
        }

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        return fix_compilation_errors(self.context, project, revision_id, wd)