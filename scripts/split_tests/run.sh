rm running/*
python3 run.py ./table6 -d /root/defects4j -f 2toMore6 -w /tmp
mv ./running/res5.json ./running/res5_6.json
mv ./running/log5 ./running/log5_6
python3 run.py ./table11 -d /root/defects4j -f 2toMore11 -w /tmp
mv ./running/res5.json ./running/res5_11.json
mv ./running/log5 ./running/log5_11
python3 merge_json.py ./running/res5_6.json ./running/res5_11.json ./running/res5.json
