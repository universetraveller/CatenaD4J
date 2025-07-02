from .project_loader import ProjectLoader
from ..util import Git
from .post_checkout_util import fix_missing_build_file

class JsoupLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'jsoup'
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        project_dir, wdp, modified, build_file = fix_missing_build_file(self.context,
                                                                        project,
                                                                        revision_id,
                                                                        wd)
        
        return modified