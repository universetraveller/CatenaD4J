from pathlib import Path
from .project_loader import ProjectLoader
from ..util import Git
from .post_checkout_util import fix_missing_build_file

class GsonLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'gson'
    def determine_layout(self):
        return {
            'src': 'gson/src/main/java',
            'test': 'gson/src/test/java'
        }

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        wd = Path(wd, 'gson')
        project_dir, wdp, modified, build_file = fix_missing_build_file(self.context,
                                                                        project,
                                                                        revision_id,
                                                                        wd)
        return modified