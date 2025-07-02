from shutil import copy2
from .project_loader import ProjectLoader
from . import LoaderError
from pathlib import Path
from ..util import Git
from .post_checkout_util import (
    fix_missing_build_file,
    fix_java_encoding,
    replace_build_file
)

def _replace_build_file(text: str):
    return text.replace(
        '<pathelement location="${hamcrest.jar}"/>',
        '<pathelement location="${hamcrest.jar}"/>\n<pathelement location="src/main/resources/commons-lang3-3.8.1.jar"/>'
    )

class CodecLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'commons-codec'
    def determine_layout(self):
        cwd = Path(self.context.cwd)
        if (cwd / 'src' / 'main').is_dir():
            return {
                'src': 'src/main/java',
                'test': 'src/test/java'
            }

        if (cwd / 'src' / 'java').is_dir():
            return {
                'src': 'src/java',
                'test': 'src/test'
            }
        
        raise LoaderError(f'Unknown layout for working directory: {cwd}')

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        project_dir, wdp, modified, build_file = fix_missing_build_file(self.context,
                                                                        project,
                                                                        revision_id,
                                                                        wd)
        
        layout = self.determine_layout()
        if fix_java_encoding(layout,
                             'test',
                             'org/apache/commons/codec/language/DoubleMetaphoneTest.java',
                             wdp):
            modified = True

        if fix_java_encoding(layout,
                             'test',
                             'org/apache/commons/codec/language/SoundexTest.java',
                             wdp):
            modified = True
        
        resources = wdp / 'src/main/resources'
        if resources.is_dir():
            copy2(project_dir / 'lib/org/apache/commons/commons-lang3/3.8.1/commons-lang3-3.8.1.jar',
                  resources / 'commons-lang3-3.8.1.jar')
            modified = True
            replace_build_file(build_file, _replace_build_file)
        
        return modified