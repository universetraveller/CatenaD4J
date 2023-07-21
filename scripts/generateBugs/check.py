import json
with open('./res3.json', 'r') as f:
    r3 = json.load(f)
with open('./res4.json', 'r') as f:
    r4 = json.load(f)
for i in r3:
    assert i in r4
    if i == 'Time_21':
        continue
    fts = r3[i]['failing_tests']
    for j in fts:
        if j in r3:
            assert len(r3[i][j]['splited']) == len(r4[i][j]['splited'])
