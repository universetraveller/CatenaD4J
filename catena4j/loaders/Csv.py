from .project_loader import ProjectLoader
from . import LoaderError
from pathlib import Path
from ..util import Git
from .post_checkout_util import fix_missing_build_file

class CsvLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'commons-csv'
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
        return modified