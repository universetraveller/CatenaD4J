from .project_loader import ProjectLoader
from . import LoaderError
from pathlib import Path
from ..util import Git
from .post_checkout_util import (
    fix_missing_build_file,
    fix_java_encoding,
    replace_build_file,
    replace_factory
)

class CliLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'commons-cli'
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

    def build_file_replace(self, project_dir):
        if not hasattr(self, '_build_file_replace'):
            replacements = {
                'compile-tests': 'compile.tests',
                'build.classpath': 'compile.classpath',
                'classesdir': 'classes.dir',
                'testclassesdir': 'test.classes.dir',
                'http://repo1.maven.org/maven/commons-lang/jars/commons-lang-2.1.jar':
                f'file://{project_dir}/lib/commons-lang/commons-lang/2.1/commons-lang-2.1.jar',
                'http://www.ibiblio.org/maven/commons-lang/jars/commons-lang-2.1.jar':
                f'file://{project_dir}/lib/commons-lang/commons-lang/2.1/commons-lang-2.1.jar',
                'http://repo1.maven.org/maven/junit/jars/junit-3.8.1.jar':
                f'file://{project_dir}/lib/junit/junit/3.8.1/junit-3.8.1.jar',
                'http://www.ibiblio.org/maven/junit/jars/junit-3.8.1.jar':
                f'file://{project_dir}/lib/junit/junit/3.8.1/junit-3.8.1.jar',
                'http://www.ibiblio.org/maven/jdepend/jars/jdepend-2.5.jar':
                f'file://{project_dir}/lib/jdepend/jdepend/2.5/jdepend-2.5.jar'
            }
            
            self._build_file_replace = replace_factory(replacements)

        return self._build_file_replace
    
    def maven_build_file_replace(self, project_dir):
        if not hasattr(self, '_maven_build_file_replace'):
            replacements = {
                'compile-tests': 'compile.tests',
                'build.classpath': 'compile.classpath',
                'http://repo1.maven.org/maven/commons-lang/jars/commons-lang-2.1.jar':
                f'file://{project_dir}/lib/commons-lang/commons-lang/2.1/commons-lang-2.1.jar',
                'http://www.ibiblio.org/maven/commons-lang/jars/commons-lang-2.1.jar':
                f'file://{project_dir}/lib/commons-lang/commons-lang/2.1/commons-lang-2.1.jar',
                'http://repo1.maven.org/maven/junit/jars/junit-3.8.1.jar':
                f'file://{project_dir}/lib/junit/junit/3.8.1/junit-3.8.1.jar',
                'http://www.ibiblio.org/maven/junit/jars/junit-3.8.1.jar':
                f'file://{project_dir}/lib/junit/junit/3.8.1/junit-3.8.1.jar',
                'http://www.ibiblio.org/maven/jdepend/jars/jdepend-2.5.jar':
                f'file://{project_dir}/lib/jdepend/jdepend/2.5/jdepend-2.5.jar'
            }
            
            self._maven_build_file_replace = replace_factory(replacements)

        return self._maven_build_file_replace

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        project_dir, wdp, modified, build_file = fix_missing_build_file(self.context,
                                                                        project,
                                                                        revision_id,
                                                                        wd)
        
        if replace_build_file(build_file, self.build_file_replace(str(project_dir))):
            modified = True

        maven_build_file = wdp / 'maven-build.xml'
        if replace_build_file(maven_build_file, self.maven_build_file_replace(str(project_dir))):
            modified = True
        
        if fix_java_encoding(self.determine_layout(),
                             'test',
                             'org/apache/commons/cli2/bug/BugLoopingOptionLookAlikeTest.java',
                             wdp):
            modified = True
        
        return modified