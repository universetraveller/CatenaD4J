python3 extract_junit_asserts.py
rm ./logs/*
python3 analyze_ver_5.py ../construct_database/d4j_export/database.json ../construct_database/2toMore6 /tmp
mv ./logs/log5 ./logs/log5_6
python3 analyze_ver_5.py ../construct_database/d4j_export/database.json ../construct_database/2toMore11 /tmp
mv ./logs/log5 ./logs/log5_11
python3 analyze_triggers.py ../construct_database/2toMore6 /root/defects4j
mv ./names/tryTrigger ./names/tryTrigger6
python3 analyze_triggers.py ../construct_database/2toMore11 /root/defects4j
mv ./names/tryTrigger ./names/tryTrigger11
cd ./names && python3 table.py && cd ..
