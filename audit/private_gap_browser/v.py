# usage: v.py <state>_private '<json>'  -> appends a verdict line to audit/<state>_private/verdicts.jsonl
import sys, json, os, datetime
d = json.loads(sys.argv[2]); d.setdefault("decided", datetime.date.today().isoformat())
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", sys.argv[1], "verdicts.jsonl")
open(path, "a").write(json.dumps(d, ensure_ascii=False) + "\n")
print("ok", d["name"], d["decision"])
