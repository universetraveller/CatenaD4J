from .import util
from .import config
__INVALID = -1
__VALID = 0
__C4J_RESET = 1
__D4J_RESET = 2
def search_config_file(wd):
    if util.exists(f'{wd}/.catena4j.info'):
        return __C4J_RESET
    elif util.exists(f'{wd}/.defects4j.config'):
        return __D4J_RESET
    else:
        return __INVALID
def validate(args):
    if not (args.p == None and args.o == None and args.v == None):
        return __INVALID
    return __VALID
def git_clean(wd):
    clean_task = util.task_printc(f'Clean files')
    res = util.run_and_get(['git', 'clean', '-xdf'], at=wd)
    if res[0]:
        clean_task.finish()
        return 0
    else:
        clean_task.fail()
        util.printc(res[1])
        util.printc('Fail to clean files, see error info')
        return -1
def git_reset(wd, commit):
    reset_task = util.task_printc(f'Reset to {commit}')
    res = util.run_and_get(['git', 'reset', '--hard', commit], at=wd)
    if res[0]:
        reset_task.finish()
        '''
        if not res[1].startswith('HEAD is now at'):
            util.printc(res[1], head='')
        '''
        return git_clean(wd)
    else:
        reset_task.fail()
        util.printc(res[1])
        util.printc('Fail to reset, see error info.')
        return -1
def get_line_attr(line):
    return line.split('=')[1].strip()
def reset_c4j_tag(info, wd):
    for line in info.splitlines():
        if 'project' in line:
            pid = get_line_attr(line)
        if 'bugid' in line:
            bid = get_line_attr(line)
        if 'cid' in line:
            cid = get_line_attr(line)
        if 'vtag' in line:
            vtag = get_line_attr(line)
    tag = config.TAG_PATTERN.format(pid=pid, bid=bid, cid=cid, buggy=vtag)
    return git_reset(wd, tag)
def reset_c4j(wd):
    with open(f'{wd}/.catena4j.info', 'r') as f:
        info = f.read()
    if config.CONFIG_GIT_TAG:
        return reset_c4j_tag(info, wd)
    catch_task = util.task_printc('Catch commit id')
    commit = None
    for line in info.splitlines():
        if 'commit' in line:
            commit = line.split('=')[1].strip()
            break
    if commit == None:
        catch_task.fail()
        util.printc('Invalid config file; cannot find commit id')
        return -1
    else:
        catch_task.finish()
        ret_v = git_reset(wd, commit)
        end_task = util.task_printc('Rewrite config file')
        with open(f'{wd}/.catena4j.info', 'w') as f:
            f.write(info)
        end_task.finish()
        return ret_v
def reset_d4j(wd, pre_defined_tag=None):
    with open(f'{wd}/.defects4j.config', 'r') as f:
        info = f.read()
    catch_task = util.task_printc('Catch program version')
    for line in info.splitlines():
        if 'pid' in line:
            pid = line.split('=')[1].strip()
        elif 'vid' in line:
            vid = line.split('=')[1].strip()
    if pre_defined_tag == None:
        v_tag = vid[-1]
        if not v_tag in ('b', 'f'):
            catch_task.fail()
            util.printc(f'Invalid vid {vid}')
            return -1
        ver_tag = 'BUGGY' if v_tag == 'b' else 'FIXED'
    else:
        ver_tag = pre_defined_tag
    catch_task.finish()
    commit = 'D4J_{}_{}_{}_VERSION'.format(pid, vid[:-1], ver_tag)
    return git_reset(wd, commit)
__reset_functions = {
        __C4J_RESET : reset_c4j,
        __D4J_RESET : reset_d4j
        }
def reset_internal(wd):
    search_task = util.task_printc('Search config file')
    stat = search_config_file(wd)
    if stat == __INVALID:
        search_task.fail()
        util.printc(f'Not a valid working_dir; cannot find <.catena4j.info> or <.defects4j.config> under directory {wd}')
        return
    else:
        search_task.finish()
        ret_v = __reset_functions[stat](wd)
        done_task = util.task_printc('Reset tasks done')
        if ret_v:
            done_task.fail()
            return
        done_task.finish()
def print_help():
    util.printc('usage: catena4j reset [-w working_dir]')
def RESET(args):
    if validate(args):
        print_help()
    else:
        reset_internal('.' if args.w == None else args.w)
