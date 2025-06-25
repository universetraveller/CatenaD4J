from pathlib import Path
from .util import read_properties
from . import d4jutil

D4J = 1
C4J = 2
def check_d4j_working_directory(wd: Path, context, parser):
    d4j = wd / context.d4j_version_props
    if not d4j.is_file():
        parser.error(f'{str(wd)}  is not a valid working directory!')

def check_working_directory(wd: Path, context, parser):

    check_d4j_working_directory(wd, context, parser)

    c4j = wd / context.c4j_version_props

    return C4J if c4j.is_file() else D4J

def parse_d4j_vid(vid):
    bid, tag = d4jutil.parse_vid(vid)
    return bid, 'BUGGY' if tag == 'b' else 'FIXED'

def read_version_info(wd, context, parser):
    version_info = read_properties(wd, context.d4j_version_props)
    if version_info is None:
        parser.error('Could not find version info. '
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