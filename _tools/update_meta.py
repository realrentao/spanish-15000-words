# -*- coding: utf-8 -*-
import json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(BASE, "data", "meta.js")
raw = open(META, encoding="utf-8").read()
k = raw.index("=") + 1
obj = json.loads(raw[k:].rstrip().rstrip(";"))

# 新计数（与 sec/0.js 实际内容一致）
upd = {"数词（2）": (23, 4, 7), "数词（3）": (19, 5, 6)}
found = set()
for g in obj["grupos"]:
    for p in g["partes"]:
        for s in p["secs"]:
            if s["name"] in upd:
                w, ss, e = upd[s["name"]]
                s["w"], s["s"], s["e"] = w, ss, e
                found.add(s["name"])
                print("updated", s["name"], "-> w/s/e", w, ss, e)
assert found == set(upd), "missing: " + str(set(upd) - found)

# 重新聚合
sw = ss_ = se = 0
for g in obj["grupos"]:
    for p in g["partes"]:
        for s in p["secs"]:
            sw += s["w"]; ss_ += s["s"]; se += s["e"]
obj["total"] = {"w": sw, "s": ss_, "e": se}
obj["totalAll"] = sw + ss_ + se
print("new total w/s/e =", sw, ss_, se, " totalAll =", obj["totalAll"])

with open(META, "w", encoding="utf-8") as f:
    f.write("window.BOOK_META=" + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";")
print("written meta.js")
