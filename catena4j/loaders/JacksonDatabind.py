from .project_loader import ProjectLoader
from ..util import Git
from .post_checkout_util import (
    fix_compilation_errors,
    fix_missing_build_file,
    fix_jackson_version
)
from ..d4jutil import get_vid

class JacksonDatabindLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'jackson-databind'
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        context = self.context
        bid, is_buggy = get_vid(project, revision_id, context)
        modified = fix_compilation_errors(context, project, bid, wd)

        project_dir, wdp, m1, build_file = fix_missing_build_file(context,
                                                                  project,
                                                                  revision_id,
                                                                  wd)
        m2 = fix_jackson_version(wdp,
                                 project_dir,
                                 'src/main/java/com/fasterxml/jackson/databind/cfg/PackageVersion.java')
        
        return modified or m1 or m2