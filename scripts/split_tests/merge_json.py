import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f1:
    data1 = json.load(f1)

with open(sys.argv[2], "r", encoding="utf-8") as f2:
    data2 = json.load(f2)

merged = {**data1, **data2}

with open(sys.argv[3], "w", encoding="utf-8") as f:
    f.write(json.dumps(merged, indent=4))