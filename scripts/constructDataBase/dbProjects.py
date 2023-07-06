import json
def config():
    # projs contains the vaild project_name; try to use projects not in this list would hit erro.
    projs = ['Chart', 'Lang', 'Math', 'Mockito', 'Time', 'Closure']
    # max_bug_id is a tag of maximum of the bug_id, so every bug_id bigger than that would be seen as out of range.
    max_bug_id = {}
    max_bug_id['Chart'] = 26
    max_bug_id['Closure'] = 133
    max_bug_id['Math'] = 106
    max_bug_id['Lang'] = 65
    max_bug_id['Mockito'] = 38
    max_bug_id['Time'] = 27
    return projs, max_bug_id
def len_ignore_empty(obj : list):
    count = 0
    for i in obj:
        if not type(i) == str:
            raise Exception("Only support string")
        if i.strip():
            count += 1
    return count
def test_len_ignore_empty():
    l = ['a', 'ab', 'a', 'c']
    assert len_ignore_empty(l) == 4
    l.append('')
    assert len_ignore_empty(l) == 4
    l[4] = ' '
    assert len_ignore_empty(l) == 4
    l[4] = '\n'
    assert len_ignore_empty(l) == 4
    l[4] = '\n '
    assert len_ignore_empty(l) == 4
    l[4] = ' \n'
    assert len_ignore_empty(l) == 4
    l.append(' ')
    assert len_ignore_empty(l) == 4
    l.append('s')
    assert len_ignore_empty(l) == 5
    l.append(1)
    try:
        len_ignore_empty(l)
    except Exception:
        pass
def rmEmpty(obj : list):
    ret = []
    for i in obj:
        if not type(i) == str:
            raise Exception("Only support string")
        if i.strip():
            ret.append(i)
    return ret
def testRmEmpty():
    l = ['a', 'b', 'c', 'd']
    assert len(rmEmpty(l)) == len_ignore_empty(l)
    l.append('')
    assert len(rmEmpty(l)) == len_ignore_empty(l)
    l[4] = ' '
    assert len(rmEmpty(l)) == len_ignore_empty(l)
    l[4] = '\n'
    assert len(rmEmpty(l)) == len_ignore_empty(l)
    l[4] = '\n '
    assert len(rmEmpty(l)) == len_ignore_empty(l)
    l[4] = ' \n'
    assert len(rmEmpty(l)) == len_ignore_empty(l)
    l.append(' ')
    assert len(rmEmpty(l)) == len_ignore_empty(l)
    l.append('s')
    assert len(rmEmpty(l)) == len_ignore_empty(l)
    try:
        len_ignore_empty(l)
    except Exception:
        pass
def exportManualRepairInfo_c4j(root=None):
    c4j = '/root/CatenaD4j/projects'
    projs, max_bug_id = config()
    if root == None:
        root={}
    d4j = {}
    for pName in projs:
        d4j[pName] = {}
        for idx in range(1, 1 + max_bug_id[pName]):
            _bugid = {}
            _manual = {}
            _manual['hunks'] = {}
            dPatch = '{}/{}/patches/{}.src.patch'.format(c4j, pName, idx)
            dLoc = '{}/{}/edited_files/{}'.format(c4j, pName, idx)
            with open(dPatch, 'r') as p:
                pat = p.read().splitlines()
            with open(dLoc, 'r') as p:
                loc = p.read().splitlines()
            assert len_ignore_empty(pat) == len_ignore_empty(loc)
            pat = rmEmpty(pat)
            loc = rmEmpty(loc)
            assert len(pat) == len(loc)
            _manual['hunks_num'] = len(pat)
            for i in range(len(pat)):
                hunk = {}
                pp = pat[i]
                pl = loc[i].split('$sl:')
                pf = pl[0]
                pl = pl[1]
                hunk['line'] = int(pl)
                hunk['file'] = pf
                hunk['patch'] = pp
                _manual['hunks'][i] = hunk
            _bugid['manual'] = _manual
            d4j[pName]['{}'.format(idx)] = _bugid
    root['defects4j'] = d4j
    return json.dumps(root, indent=4)
def runEMRIc4j(fp:str):
    with open(fp, 'w') as f:
        f.write(exportManualRepairInfo_c4j())
    return True
def runtests():
    test_len_ignore_empty()
    testRmEmpty()
    print('pass')
def exportInfoMerging(ori, target):
    with open(target, 'r') as target:
        target = json.load(target)
    with open(ori, 'r') as ori:
        ori = json.load(ori)
    for i in target:
        exportInfo = target[i]
        i = i.split('_')
        ori['defects4j'][i[0]][i[1]]['export'] = {}
        for j in exportInfo:
            ori['defects4j'][i[0]][i[1]]['export'][j] = exportInfo[j]
    return ori
def mergeExport(fp:str, ori:str, target:str):
    with open(fp, 'w') as f:
        f.write(json.dumps(exportInfoMerging(ori, target), indent=4))
    return True
if __name__ == '__main__':
    runtests()
    #runEMRIc4j('./database.json')
    mergeExport('./database.json', './database.json.ori', '../d4j_export/database.json')
