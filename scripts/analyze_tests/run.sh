python3 extract_junit_asserts.py
python3 analyze_ver_5.py ../construct_database/d4j_export/database.json ../construct_database/2toMore /tmp
python3 analyze_triggers.py ../construct_database/2toMore /root/defects4j
cd ./names && python3 table.py && cd ..
