from shutil import copy2
from .project_loader import ProjectLoader
from . import LoaderError
from pathlib import Path
from ..util import Git
from .post_checkout_util import (
    fix_missing_build_file,
    replace_build_file,
    replace_factory
)

class JxPathLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'commons-jxpath'
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

    def build_file_replacements(self, project_dir):
        if not hasattr(self, '_build_file_replacements'):
            self._build_file_replacements = {
                'compile-tests': 'compile.tests',
                'classesdir': 'classes.dir',
                'testclassesdir': 'test.classes.dir',
                'http://www.ibiblio.org/maven2/com/mockrunner/mockrunner-jdk1.3-j2ee1.3/0.4/mockrunner-jdk1.3-j2ee1.3-0.4.jar':
                f'file://{project_dir}/lib/mockrunner-0.4.1.jar',
                'http://www.ibiblio.org/maven/servletapi/jars/servletapi-2.4.jar':
                f'file://{project_dir}/lib/servletapi/servletapi/2.4/servletapi-2.4.jar',
                'http://www.ibiblio.org/maven/jspapi/jars/jsp-api-2.0.jar':
                f'file://{project_dir}/lib/jspapi/jsp-api/2.0/jsp-api-2.0.jar',
                'http://www.ibiblio.org/maven/commons-beanutils/jars/commons-beanutils-1.7.0.jar':
                f'file://{project_dir}/lib/commons-beanutils/commons-beanutils/1.7.0/commons-beanutils-1.7.0.jar',
                'http://www.ibiblio.org/maven/commons-logging/jars/commons-logging-1.1.jar':
                f'file://{project_dir}/lib/commons-logging/commons-logging/1.1/commons-logging-1.1.jar',
                'http://www.ibiblio.org/maven/junit/jars/junit-3.8.2.jar':
                f'file://{project_dir}/lib/junit/junit/3.8.2/junit-3.8.2.jar',
                'http://www.ibiblio.org/maven/ant/jars/ant-optional-1.5.1.jar':
                f'file://{project_dir}/lib/ant/ant-optional/1.5.1/ant-optional-1.5.1.jar',
                'http://www.ibiblio.org/maven/ant/jars/ant-1.5.jar':
                f'file://{project_dir}/lib/ant/ant/1.5/ant-1.5.jar',
                'http://www.ibiblio.org/maven/ant/jars/ant-optional-1.5.jar':
                f'file://{project_dir}/lib/ant/ant-optional/1.5/ant-optional-1.5.jar',
                'http://www.ibiblio.org/maven/xerces/jars/xerces-1.2.3.jar':
                f'file://{project_dir}/lib/xerces/xerces/1.2.3/xerces-1.2.3.jar',
                'http://www.ibiblio.org/maven/xerces/jars/xerces-2.4.0.jar':
                f'file://{project_dir}/lib/xerces/xerces/2.4.0/xerces-2.4.0.jar',
                'http://www.ibiblio.org/maven/servletapi/jars/servletapi-2.2.jar':
                f'file://{project_dir}/lib/servletapi/servletapi/2.2/servletapi-2.2.jar',
                'http://www.ibiblio.org/maven/junit/jars/junit-3.8.jar':
                f'file://{project_dir}/lib/junit/junit/3.8/junit-3.8.jar',
                'http://www.ibiblio.org/maven/xml-apis/jars/xml-apis-2.0.2.jar':
                f'file://{project_dir}/lib/xml-apis/xml-apis/2.0.2/xml-apis-2.0.2.jar',
                'http://www.ibiblio.org/maven/jdom/jars/jdom-1.0.jar':
                f'file://{project_dir}/lib/jdom/jdom/1.0/jdom-1.0.jar',
                'http://www.ibiblio.org/maven/commons-beanutils/jars/commons-beanutils-1.4.jar':
                f'file://{project_dir}/lib/commons-beanutils/commons-beanutils/1.4/commons-beanutils-1.4.jar',
                'http://www.ibiblio.org/maven/commons-logging/jars/commons-logging-1.0.4.jar':
                f'file://{project_dir}/lib/commons-logging/commons-logging/1.0.4/commons-logging-1.0.4.jar',
                'http://www.ibiblio.org/maven/commons-collections/jars/commons-collections-2.0.jar':
                f'file://{project_dir}/lib/commons-collections/commons-collections/2.0/commons-collections-2.0.jar',
                'http://www.ibiblio.org/maven/junit/jars/junit-3.8.1.jar':
                f'file://{project_dir}/lib/junit/junit/3.8.1/junit-3.8.1.jar',
            }

        return self._build_file_replacements

    def build_file_replace(self, project_dir):
        if not hasattr(self, '_build_file_replace'):
            replacements = self.build_file_replacements(project_dir)
            self._build_file_replace = replace_factory(replacements)

        return self._build_file_replace
    
    def maven_build_file_replace(self, project_dir):
        if not hasattr(self, '_maven_build_file_replace'):
            replacements = self.build_file_replacements(project_dir)
            self._maven_build_file_replace = replace_factory(replacements)

        return self._maven_build_file_replace

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        project_dir, wdp, modified, build_file = fix_missing_build_file(self.context,
                                                                        project,
                                                                        revision_id,
                                                                        wd)
        
        (wdp / 'target/lib').mkdir(parents=True)
        copy2(project_dir / 'lib/mockrunner-0.4.1.jar',
              wdp / 'target/lib/mockrunner-0.4.1.jar')

        replace_build_file(build_file, self.build_file_replace(str(project_dir)))

        maven_build_file = wdp / 'maven-build.xml'
        replace_build_file(maven_build_file, self.maven_build_file_replace(str(project_dir)))

        return True