from pathlib import Path
from .util import read_properties, Git
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
def parse_d4j_vid(vid: str):
    bid, tag = d4jutil.parse_vid(vid)
    return bid, BUGGY if tag == 'b' else FIXED

def read_version_info(wd, context):
    version_info = read_properties(wd, context.d4j_version_props)
    if version_info is None:
        raise Catena4JError('Could not find version info. '
                      'Please check if current directory '
                      'is a project from defects4j or catena4j.')

    vid, tag = parse_d4j_vid(version_info['vid'])
    version_info['vid'] = vid
    version_info['tag'] = tag 

    # check if the project is a catena4j project
    # TODO update the format of old c4j version properties file
    c4j_version_info = read_properties(wd, context.c4j_version_props)
    if c4j_version_info is None:
        version_info['cid'] = None
    else:
        version_info['pid'] = c4j_version_info['project']
        version_info['vid'] = c4j_version_info['bugid']
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

def create_post_fix_commit(tag_name, wd):
    Git.add_all(wd)
    Git.commit_all(tag_name)
    Git.tag(tag_name)