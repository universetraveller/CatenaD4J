from .project_loader import ProjectLoader
from . import LoaderError
from pathlib import Path
from ..util import Git
from .post_checkout_util import (
    fix_java_encoding,
    replace_build_file
)

class CollectionsLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'commons-collections'
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

    def build_file_replace(self):
        if not hasattr(self, '_replace_build_file'):
            old = (
                '<javac srcdir="${source.home}" destdir="${build.home}/classes" debug="${compile.debug}" '
                'deprecation="${compile.deprecation}" target="${compile.target}" source="${compile.source}" '
                'excludes="${compile.excludes}" optimize="${compile.optimize}" includeantruntime="false" '
                'encoding="${compile.encoding}">'
            )

            new = (
                '<javac fork="true" srcdir="${source.home}" destdir="${build.home}/classes" debug="${compile.debug}" '
                'deprecation="${compile.deprecation}" target="1.7" source="1.7" excludes="${compile.excludes}" '
                'optimize="${compile.optimize}" includeantruntime="false" encoding="${compile.encoding}">'
            )

            def replace(text: str):
                return text.replace(old, new)
            
            self._replace_build_file = replace
        
        return self._replace_build_file

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        # defects4j try to copy files but there is no build_files directory
        # for project Collections
        #project_dir, wdp, modified, build_file = fix_missing_build_file(self.context,
        #                                                                project,
        #                                                                revision_id,
        #                                                                wd)

        wdp = Path(wd)
        modified = False

        build_file = wdp / 'build.xml'


        m1 = replace_build_file(build_file, self.build_file_replace())

        layout = self.determine_layout()
        m2 = fix_java_encoding(layout,
                               'src',
                               'org/apache/commons/collections/functors/ComparatorPredicate.java',
                               wdp)
        
        return modified or m1 or m2
