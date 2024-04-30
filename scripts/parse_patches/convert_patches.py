import glob
import os
import json
import javalang
import sys
projs = ['Chart', 'Lang', 'Math', 'Time', 'Closure', 'Mockito']
base_dir = './patches/'
work_dir = '/tmp/'
if len(sys.argv) > 1:
    work_dir = os.path.abspath(sys.argv[1])
    if not work_dir.endswith('/'):
        work_dir += '/'
if len(sys.argv) > 2:
    projs = [sys.argv[2]]
if len(sys.argv) > 3:
    base_dir = sys.argv[2]
def convert_patches_to_comments_ignored_ver():
    if not os.path.exists('./patches_ci/'):
        os.makedirs('./patches_ci/')
    for proj in projs:
        if not os.path.exists(f'./patches_ci/{proj}/'):
            os.makedirs(f'./patches_ci/{proj}/')
        _convert_ci_proj(proj)
def _convert_ci_proj(proj):
    paths = glob.glob(f'{base_dir}{proj}/*')
    for path in paths:
        if 'Time/21.json' in path:
            continue
        idx = path.replace(f'{base_dir}{proj}/', '').replace('.json', '')
        with open(path, 'r') as f:
            patch = json.load(f)
        num = _convert_ci_patch(proj, idx, patch)
        patch['num_of_hunks_ci'] = num
        with open(path.replace(base_dir, './patches_ci/'), 'w') as f:
            f.write(json.dumps(patch, indent=4))
def parse_hunk_get_boundary(hunk):
    if hunk['patch_type'] == 'insert':
        return (int(hunk['next_line_no']), int(hunk['next_line_no'])-1)
    else:
        return (int(hunk['from_line_no']), int(hunk['to_line_no']))
def _convert_ci_patch(proj, idx, patch):
    file_map = {}
    working = f'{work_dir}{proj}_{idx}/'
    for hid in patch:
        if hid == 'num_of_hunks':
            num = int(patch['num_of_hunks'])
            continue
        hunk = patch[hid]
        if not hunk['file_name'] in file_map:
            file_map[hunk['file_name']] = []
        file_map[hunk['file_name']].append(hid)
    if num == 1:
        return num
    for file in file_map:
        hunks = file_map[file]
        with open(f'{working}{file}', 'r', encoding='latin-1') as f:
            src = f.read().splitlines()
        for i in range(1, len(hunks)):
            now = patch[hunks[i]]
            pre = patch[hunks[i-1]]
            now_begin = parse_hunk_get_boundary(now)[0]
            pre_end = parse_hunk_get_boundary(pre)[1]
            code = '\n'.join(src[pre_end:now_begin-1])
            if not len(list(javalang.tokenizer.tokenize(code))):
                patch[hunks[i]]['is_extra_hunk'] = True
                num -= 1
                print(f'{proj}_{idx} hunk {hunks[i]} code {code}')
                print('-'*50)
    return num
if __name__ == '__main__':
    convert_patches_to_comments_ignored_ver()
