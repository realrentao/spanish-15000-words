# -*- coding: utf-8 -*-
"""Sync gid=7 (在银行) sec counts into data/meta.js and recompute global totals."""
import json, re, os
BASE = "D:/西班牙语材料/15000词西语随身背"
GID = 7

def load_sec(path):
    t = open(path, encoding="utf-8").read()
    i = t.index("={") + 1
    depth=0; j=i; ins=False; esc=False
    while j < len(t):
        c=t[j]
        if ins:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c=='"': ins=False
        else:
            if c=='"': ins=True
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0: break
        j+=1
    return json.loads(t[i:j+1])

# recount gid=7 from its sec file
o = load_sec(os.path.join(BASE, "data/sec/%d.js" % GID))
counts = {}
for s in o["secs"]:
    counts[s["no"]] = (len(s["w"]), len(s["s"]), len(s["e"]))

t = open(os.path.join(BASE, "data/meta.js"), encoding="utf-8").read()
i = t.index("=") + 1
j = t.rindex(";")
m = json.loads(t[i:j])

total_w = total_s = total_e = 0
updated_secs = 0
for g in m["grupos"]:
    for p in g["partes"]:
        if p.get("gid") == GID:
            for sec in p["secs"]:
                no = sec["no"]
                if no in counts:
                    w, s, e = counts[no]
                    sec["w"], sec["s"], sec["e"] = w, s, e
                    updated_secs += 1
        # recompute every parte total and global totals
        ptotal = 0
        for sec in p["secs"]:
            ptotal += sec["w"] + sec["s"] + sec["e"]
        p["total"] = ptotal
        total_w += sum(sec["w"] for sec in p["secs"])
        total_s += sum(sec["s"] for sec in p["secs"])
        total_e += sum(sec["e"] for sec in p["secs"])

m["total.w"] = total_w
m["total.s"] = total_s
m["total.e"] = total_e
m["totalAll"] = total_w + total_s + total_e

out = t[:i] + json.dumps(m, ensure_ascii=False, separators=(",", ":")) + ";"
open(os.path.join(BASE, "data/meta.js"), "w", encoding="utf-8").write(out)
print("updated secs: %d totals: w=%d s=%d e=%d all=%d" % (updated_secs, total_w, total_s, total_e, m["totalAll"]))
