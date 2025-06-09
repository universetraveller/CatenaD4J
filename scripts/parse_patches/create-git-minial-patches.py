import multiprocessing
import subprocess
import os
import d4jpath
import sys

'''
There are a lots of bugs in defects4j whose patch file is not correct.

List of bugs whose patch file contains line offsets:
    Files patches/Chart/7.json and patches-git/Chart/7.json differ
    Files patches/Codec/12.json and patches-git/Codec/12.json differ
    Files patches/JacksonDatabind/68.json and patches-git/JacksonDatabind/68.json differ
    Files patches/Jsoup/30.json and patches-git/Jsoup/30.json differ
    Files patches/Jsoup/56.json and patches-git/Jsoup/56.json differ

Create the latest patch files using the git diff command to ensure the created
patch json file matches to the source file.
'''

path2bugs = sys.argv[1]

BUGGY = 'D4J_{}_BUGGY_VERSION'
FIXED = 'D4J_{}_FIXED_VERSION'

tasks = []
for proj in d4jpath.all_bugs:
    with open(os.path.join(d4jpath.d4j_home, 'framework', 'projects', proj, 'dir-layout.csv')) as f:
        src = f.read().splitlines()[0].split(',')[1].split('/')[0]
    for id in d4jpath.all_bugs[proj]:
        path2patch = os.path.join('./', 'projects', proj, 'patches')
        if not os.path.exists(path2patch):
            os.makedirs(path2patch)
        patch_file = os.path.join(os.path.abspath(path2patch), f'{id}.src.patch')
        bid = f'{proj}_{id}'
        path2bug = os.path.join(path2bugs, bid)
        buggy = BUGGY.format(bid)
        fixed = FIXED.format(bid)
        tasks.append(((['git', 'diff', '--minimal', f'--output={patch_file}', fixed, buggy, '--', src],),
                      {'cwd': path2bug}))

def execute(task):
    subprocess.run(*task[0], **task[1])

with multiprocessing.Pool() as pool:
    pool.map(execute, tasks)
