import json
def getHunksNum(fp:str):
    with open(fp, 'r') as f:
        root=json.load(f)
    d4j = root.get('defects4j')
    HunksWithNum={}
    for pName in d4j:
        proj = d4j.get(pName)
        for idx in proj:
            hunks_num=proj.get(idx).get('manual').get('hunks_num')
            HunksWithNum['{}_{}'.format(pName, idx)]=hunks_num
    return HunksWithNum
def find2to3(fp:str, target:str):
    Hunks = getHunksNum(fp)
    target=open(target, 'a')
    for i in Hunks:
        if Hunks.get(i) > 3 or Hunks.get(i) < 2:
            continue
        target.write(i+'\n')
        print('{} : {}'.format(i, Hunks.get(i)))
    target.close()
def find2to5(fp:str, target:str):
    Hunks = getHunksNum(fp)
    target=open(target, 'a')
    num = 0
    for i in Hunks:
        if Hunks.get(i) > 5 or Hunks.get(i) < 2:
            continue
        num += 1
        target.write(i+'\n')
        print('{} : {}'.format(i, Hunks.get(i)))
    target.close()
    print(num)
def moreThan5(fp:str, target:str):
    Hunks = getHunksNum(fp)
    target=open(target, 'a')
    num = 0
    for i in Hunks:
        if Hunks.get(i) <= 5:
            continue
        num += 1
        target.write(i+':'+str(Hunks.get(i))+'\n')
        print('{} : {}'.format(i, Hunks.get(i)))
    target.close()
    print(num)
def twoToMore(fp:str, target:str):
    Hunks = getHunksNum(fp)
    target=open(target, 'a')
    num = 0
    for i in Hunks:
        if Hunks.get(i) == 1:
            continue
        num += 1
        target.write(i+':'+str(Hunks.get(i))+'\n')
        print('{} : {}'.format(i, Hunks.get(i)))
    target.close()
    print(num)
if __name__=='__main__':
    #find2to5('./database.json', './2to5')
    #moreThan5('./database.json', './moreThan5')
    twoToMore('./database.json', './2toMore')
