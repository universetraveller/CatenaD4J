import re
from ..util import read_file, write_file, run_apply_patch_task
from pathlib import Path
from shutil import copy2, copytree
from ..d4jutil import get_project_dir as d4j_get_project_dir


def fix_compilation_errors(context, project, revision_id, wd):
    compile_errors = d4j_get_project_dir(project, 'compile-errors', context)

    revision_id = int(revision_id)

    modified = False
    for file in compile_errors.iterdir():
        _min, _max = map(int, file.name[:-5].rsplit('-', 2)[-2:])
        if revision_id < _min:
            continue

        if revision_id > _max:
            continue

        run_apply_patch_task(file, wd, context)

        # reaching here means there are file changes
        modified = True
    
    return modified

def fix_missing_build_file(context, project: str, revision_id:str, wd: str):
    project_dir = d4j_get_project_dir(project, '', context)
    wdp = Path(wd)
    modified = False

    build_file = wdp / 'build.xml'

    # ensure the build.xml file
    if not build_file.is_file():
        build_files = project_dir / 'build_files' / revision_id

        if build_files.is_dir():
            for f in build_files.iterdir():
                if f.is_file():
                    copy2(f, wdp)
                else:
                    # defects4j includes an extra directory for two of the 
                    # revision ids in project Cli, that seems to be a bug
                    copytree(f, wdp / f.name)
            modified = True
    
    return project_dir, wdp, modified, build_file

def fix_java_encoding(layout, layout_key: str, file_name: str, wdp: Path):
    f = wdp / layout[layout_key] / file_name
    if f.is_file():
        text = read_file(f, encoding='iso-8859-1')
        write_file(f.with_suffix('.java.bak'), text, encoding='iso-8859-1')
        write_file(f, text, encoding='utf-8')
        return True
    return False

def replace_build_file(build_file: Path, replace):
    if build_file.is_file():
        text = read_file(build_file)
        write_file(build_file.with_suffix('.xml.bak'), text)
        write_file(build_file, replace(text))
        return True
    return False

def replace_factory(replacements):
    def replacement(m):
        return replacements[m.group(0)]
    
    pattern = re.compile("|".join(re.escape(s) for s in replacements))

    def replace(text):
        return pattern.sub(replacement, text)
    
    return replace

def fix_jackson_version(wdp: Path, project_dir: Path, file_name: str, version_pos=2):
    text = read_file(wdp / 'maven-build.properties')
    if text is None:
        return False
    for line in text.splitlines():
        if 'maven.build.finalName' in line:
            # fast enough though it is not the best solution
            version = line.split('-')[version_pos]
            copy2(project_dir / 'generated_sources' / version / 'PackageVersion.java',
                    wdp / file_name)
            return True
    return False
    