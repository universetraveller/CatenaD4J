from pathlib import Path
from .project_loader import ProjectLoader
from ..util import Git
from .post_checkout_util import replace_build_file
import re

def _replace_build_file(text):
    text = re.sub(r'\bdebug\s*=\s*"[^"]*"', '', text)
    return re.sub(r'<javac\s+', '<javac debug="true" ', text)

class ClosureLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'closure-compiler'
    def determine_layout(self):
        return {
            'src': 'src',
            'test': 'test'
        }

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        return replace_build_file(Path(wd) / 'build.xml', _replace_build_file)