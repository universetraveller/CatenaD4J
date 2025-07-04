import argparse
import os
from pathlib import Path
import sys
from catena4j.bootstrap import register_entry_point
from catena4j.util import run_command_task, auto_task_print
from catena4j.env import get_system_context

def build_toolkit(c4j_home, d4j_home):
    toolkit = c4j_home / 'toolkit'
    target = toolkit / 'target'
    if not target.is_dir():
        target.mkdir(parents=True)

    javac_base = ['javac', '-cp', f'{d4j_home}/major/lib/*', '-sourcepath', './src', '-d', './target']

    src = []
    for root, _, files in os.walk(f'{toolkit}/src/io/github/universetraveller/'):
        for file in files:
            if file.endswith('.java'):
                src.append(os.path.join(root, file))

    cmd = javac_base + src
    run_command_task(cmd, str(toolkit))

    jar_cmd = ['jar', 'cf', './target/toolkit.jar', '-C', './target', '.']
    run_command_task(jar_cmd, str(toolkit))

def generate_startup_script(file_name, python, c4j_home):
    SCRIPT = f'''#! {python}
from catena4j.bootstrap import system
system.start
'''
    with open(c4j_home / file_name, 'w', encoding=sys.getdefaultencoding()) as f:
        f.write(SCRIPT)

def add_path(c4j_home):
    shell = os.environ.get("SHELL", "")
    home = Path.home()

    # Choose config file based on shell
    if "zsh" in shell:
        rc_file = home / ".zshrc"
    elif "bash" in shell:
        rc_file = home / ".bashrc"
    else:
        rc_file = home / ".profile"

    export_line = f'export PATH=$PATH:{c4j_home}'

    # Avoid duplicate entry
    if rc_file.exists():
        content = rc_file.read_text()
        if export_line in content:
            return f'Found {export_line} in {rc_file} so it is not added again'

    current_path_entries = os.environ.get("PATH", "").split(os.pathsep)

    if str(c4j_home) in current_path_entries:
        return f'Found {c4j_home} in PATH so it is not added to {rc_file}'

    with open(rc_file, "a") as f:
        f.write(f'\n# Added by catena4j setup script\n{export_line}\n')
    
    return ('To make changes take effect, open a new terminal or run:'
            f'\n\n   source {rc_file}\n')

def main():
    context = get_system_context()
    c4j_home = Path(context.c4j_home).resolve()

    parser = argparse.ArgumentParser()
    parser.add_argument('-n',
                        '--name',
                        help='the name of startup script to generate',
                        dest='name',
                        required=False,
                        default='c4j')
    parser.add_argument('-p',
                        '--python',
                        help='the path of python interpreter',
                        dest='python',
                        required=False,
                        default=sys.executable)

    args = parser.parse_args()
    auto_task_print('Build the toolkit', build_toolkit, (c4j_home, context.d4j_home))
    auto_task_print(f'Generate the startup script to {c4j_home / args.name}',
                    generate_startup_script,
                    (args.name, args.python, c4j_home))
    output = auto_task_print('Add executable to PATH', add_path, (c4j_home,))
    print(output)


if __name__ == '__main__':
    from catena4j.bootstrap import system
    register_entry_point(main)
    system.start
