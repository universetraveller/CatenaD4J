from .project_loader import ProjectLoader
from ..util import Git
from .post_checkout_util import fix_missing_build_file, fix_jackson_version

class JacksonXmlLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'jackson-dataformat-xml'
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        project_dir, wdp, m1, build_file = fix_missing_build_file(self.context,
                                                                  project,
                                                                  revision_id,
                                                                  wd)
        
        m2 = fix_jackson_version(wdp,
                                 project_dir,
                                 'src/main/java/com/fasterxml/jackson/dataformat/xml/PackageVersion.java',
                                 3)
        
        return m1 or m2