from pathlib import Path
from .util import read_properties, read_file, Git, File, Files
from . import d4jutil
from .exceptions import Catena4JError
import re

D4J = 1
C4J = 2
ERR = 3
def check_d4j_working_directory(wd: Path, context, strict=False):
    d4j = wd / context.d4j_version_props
    if not d4j.is_file():
        if strict:
            raise Catena4JError(f'{str(wd)}  is not a valid working directory!')
        return ERR
    return D4J

def check_working_directory(wd: Path, context, strict=False):

    d4j_or_err = check_d4j_working_directory(wd, context, strict)

    c4j = wd / context.c4j_version_props

    return C4J if c4j.is_file() else d4j_or_err

BUGGY = 'BUGGY'
FIXED = 'FIXED'
def normalize_tag(tag: str):
    return BUGGY if tag == 'b' else FIXED

def parse_d4j_vid(vid: str):
    bid, tag = d4jutil.parse_vid(vid)
    return bid, normalize_tag(tag)

def read_version_info(wd, context):
    version_info = read_properties(wd, context.d4j_version_props)
    if version_info is None:
        raise Catena4JError('Could not find version info. '
                            'Please check if current directory '
                            'is a project from defects4j or catena4j.')

    bid, tag = parse_d4j_vid(version_info['vid'])
    version_info['bid'] = bid
    version_info['tag'] = tag 

    # check if the project is a catena4j project
    # TODO update the format of old c4j version properties file
    c4j_version_info = read_properties(wd, context.c4j_version_props)
    if c4j_version_info is None:
        version_info['cid'] = None
    else:
        version_info['pid'] = c4j_version_info['project']
        version_info['bid'] = c4j_version_info['bugid']
        version_info['cid'] = c4j_version_info['cid']
        version_info['tag'] = c4j_version_info['vtag']
    
    return version_info

vid_parser = re.compile(r'^([1-9][0-9]*)([bf])([1-9][0-9]*)?$')
def parse_vid(vid: str):
    m = vid_parser.match(vid)

    if m:
        return m.groups()

    raise Catena4JError(f'Wrong version_id: {vid} -- expected {vid_parser.pattern}')

def init_git_repository(wd):
    Git.init(wd)
    Git.config('user.name', 'catena4j', wd)
    Git.config('user.email', 'catena4j@localhost', wd)
    Git.config('core.autocrlf', 'false', wd)

def create_commit_and_tag(tag_name, wd):
    Git.add_all(wd)
    Git.commit_all(tag_name, wd)
    Git.tag(tag_name, wd)

def get_tag_name_from_ver(version_info, context):
    project = version_info['pid']
    bid = version_info['bid']
    cid = version_info['cid']
    tag = version_info['tag']
    if cid is None:
        # is a defects4j directory
        tag = 'BUGGY_VERSION' if tag == BUGGY else 'FIXED_VERSION'
        return context.d4j_tag.format(project=project, bid=bid, suffix=tag)
    else:
        # is a catena4j directory
        return context.c4j_tag.format(project=project, bid=bid, cid=cid, suffix=tag)

def get_property(name, project, bid, cid, context):
    path = Path(context.c4j_home, context.c4j_rel_projects, project, bid, f'{cid}.{name}')

    value = read_file(path)
    if value is None:
        raise Catena4JError(f'Could not find property {name} from {path}')
    
    return value.strip()

def apply_json_patch(patch: dict, files: Files=None):
    '''
        adapt and apply catena4j's src and test patches
    '''
    file_name = patch['file_name'] if 'file_name' in patch else patch['file_path']

    content = '\n'.join(patch['to']) + '\n' if 'to' in patch else patch['replaced_with']


    file = files.get_file(file_name)

    _edit_type = patch.get('patch_type', 'replace')
    if _edit_type == 'insert':
        # 1-based line number
        pos = patch['next_line_no'] - 1
        content >> file[pos]
    else:
        # 1-based line number
        start = (
                    patch['begin_line_no'] if 'begin_line_no' in patch else \
                    patch['from_line_no']
                ) - 1

        stop = patch['end_line_no'] if 'end_line_no' in patch else patch['to_line_no']

        if _edit_type == 'replace':
            file[start:stop] = content
        elif _edit_type == 'delete':
            del file[start:stop]
        else:
            raise Catena4JError(f'Unknown patch type {_edit_type}')
    
    return file