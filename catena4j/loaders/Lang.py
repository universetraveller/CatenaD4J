from .project_loader import ProjectLoader
from . import LoaderError
from ..util import read_properties, Git

class LangLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'commons-lang'
    def _search_layout(self, cwd, file, src_prop, test_prop):
        # this function will scan all lines but this overhead is minimal
        props = read_properties(cwd, file)

        if props is None:
            return None

        return {
            'src': props[src_prop],
            'test': props[test_prop]
        }

    def determine_layout(self):
        cwd = self.context.cwd

        layout = self._search_layout(cwd, 'default.properties', 'source.home', 'test.home') \
                    or self._search_layout(cwd, 'maven-build.properties', 'maven.build.srcDir.0', 'maven.build.testDir.0')

        if layout is None:
            raise LoaderError(f'Unknown layout for working directory: {cwd}')
        
        return layout