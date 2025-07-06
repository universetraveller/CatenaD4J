import os
from .project_loader import ProjectLoader
from . import LoaderError
from pathlib import Path
from ..util import Git, read_file, run_apply_patch_task, write_file
from ..d4jutil import get_vid as d4j_get_vid, get_project_dir as d4j_get_project_dir

class MockitoLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'mockito'
    def determine_layout(self):
        cwd = Path(self.context.cwd)
        if (cwd / 'src' / 'main' / 'java').is_dir():
            return {
                'src': 'src/main/java',
                'test': 'src/test/java'
            }

        if (cwd / 'src').is_dir():
            return {
                'src': 'src',
                'test': 'test'
            }
        
        raise LoaderError(f'Unknown layout for working directory: {cwd}')
    
    def toolkit_execute(self,
                        target: str,
                        project: str,
                        wd: str,
                        *,
                        task_printer=None,
                        xml_attr: str='c4j_rel_project_compile_xml',
                        main_attr: str='c4j_toolkit_execute_main',
                        java_options=()):
        self.context.os_env['GRADLE_USER_HOME'] = os.path.join(wd, self.context.GRADLE_LOCAL_HOME_DIR)
        return super().toolkit_execute(target,
                                       project,
                                       wd,
                                       task_printer=task_printer,
                                       xml_attr=xml_attr,
                                       main_attr=main_attr,
                                       java_options=java_options)

    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        context = self.context
        bid, is_buggy = d4j_get_vid(project, revision_id, context)
        bid = int(bid)
        modified = False
        if bid in (16, 17) or (bid >= 34 and bid <= 38):
            patch = d4j_get_project_dir(project, 'mockito_test_runners.patch', context)
            run_apply_patch_task(patch, wd, context)
            modified = True
        
        wdp = Path(wd)

        props = wdp / 'gradle/wrapper/gradle-wrapper.properties'
        build_system_lib_dir = Path(context.BUILD_SYSTEMS_LIB_DIR, 'gradle')
        lib_dir = build_system_lib_dir / 'dists'

        text = read_file(props)
        if text is None:
            return modified

        to_write = []
        for line in text.splitlines():
            if 'distributionUrl=' in line:
                left, _, right = line.partition('=')
                gradle = 'gradle-2.2.1-all.zip' if 'gradle-2' in right else 'gradle-1.12-bin.zip'
                line = f'{left}=file\\:{str(lib_dir)}/{gradle}'

            to_write.append(line)

        write_file(props, '\n'.join(to_write))
        modified = True

        props = wdp / 'gradle.properties'
        if props.is_file():
            text = read_file(props)
            write_file(props.with_suffix('.properties.bak'), text)
            text = text.replace('org.gradle.daemon=true', 'org.gradle.daemon=false')
            write_file(props, text)
            modified = True
        
        replacement = (f'maven {{ url "{build_system_lib_dir}/deps" }}\n'
                       ' maven { url "https://jcenter.bintray.com/" }\n')
        for root, _, files in os.walk(wd):
            for f in files:
                if f != 'build.gradle':
                    continue

                modified = True

                fp = Path(root, f)
                text = read_file(fp)
                write_file(fp.with_suffix('.gradle.bak'), text)
                text = text.replace('jcenter()', replacement)
                write_file(fp, text)
        
        return modified


        

