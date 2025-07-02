from shutil import copy2, move
from .project_loader import ProjectLoader
from . import LoaderError
from pathlib import Path
from ..util import Git
from .post_checkout_util import fix_missing_build_file

class TimeLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'joda-time'
    def determine_layout(self):
        cwd = Path(self.context.cwd)
        if (cwd / 'src' / 'main' / 'java').is_dir():
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
        wdp = Path(wd)

        modified = False

        jtd = wdp / 'JodaTime'
        if jtd.is_dir():
            for p in jtd.iterdir():
                move(str(p), wd)
            modified = True
        
        project_dir, wdp, m1, build_file = fix_missing_build_file(self.context,
                                                                        project,
                                                                        revision_id,
                                                                        wd)
        
        f = project_dir / 'broken-builds' / f'build-{revision_id}.xml'
        if f.is_file():
            copy2(f, build_file)
            modified = True
        
        return modified or m1

    # defects4j contains a custom export_diff for Time but it is not actually
    # called int the checkout command for unknown reason
    # but it seems to be called in the bug-mining process
    #def export_diff(self, a: str, b: str, output: Path=None):
    #    pass