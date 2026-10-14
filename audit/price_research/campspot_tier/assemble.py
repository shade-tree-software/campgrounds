"""assemble.py FINDINGS HAND: fold hand findings into the builder's findings, in place.
HAND items are whole findings ({id, fees, source}, added or replacing the builder's) or {id, _patch: {...}}:
note_add appends to fees.note, note_sub [old, new] edits it, source_add appends to source, source_sub [old, new] edits
source, any other key sets fees[key]."""
import json, sys

path, hand_path = sys.argv[1], sys.argv[2]
out = {f["id"]: f for f in json.load(open(path, encoding="utf-8"))}
for h in json.load(open(hand_path, encoding="utf-8")):
    if "_patch" not in h:
        out[h["id"]] = h
        print("hand", h["id"])
        continue
    f = out[h["id"]]
    for k, v in h["_patch"].items():
        if k == "note_add":
            f["fees"]["note"] = f["fees"]["note"].rstrip() + " " + v
        elif k == "note_sub":
            assert v[0] in f["fees"]["note"], (h["id"], v[0])
            f["fees"]["note"] = f["fees"]["note"].replace(v[0], v[1])
        elif k == "source_add":
            f["source"] += v
        elif k == "source_sub":
            assert v[0] in f["source"], (h["id"], v[0])
            f["source"] = f["source"].replace(v[0], v[1])
        else:
            f["fees"][k] = v
    print("patched", h["id"], sorted(h["_patch"]))
json.dump(sorted(out.values(), key=lambda f: f["id"]), open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "findings")
