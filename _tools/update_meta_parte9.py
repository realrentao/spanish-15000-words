# -*- coding: utf-8 -*-
"""Sync data/meta.js: update gid=8 (在理发店) sec counts from data/sec/8.js,
then recompute global totals by summing ALL sec files (source of truth)."""
import json, re, os, glob
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 8

def load_sec(path):
    t = open(path, encoding="utf-8").read()
    i = t.index("={") + 1
    depth = 0; j = i; ins = False; esc = False
    while j < len(t):
        c = t[j]
        if ins:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
        j += 1
    return json.loads(t[i:j+1])

# load meta
mt = open(os.path.join(BASE, "data/meta.js"), encoding="utf-8").read()
mi = mt.index("=") + 1
mj = mt.rindex(";")
m = json.loads(mt[mi:mj])

# update gid=8 sec counts
o = load_sec(os.path.join(BASE, "data/sec/%d.js" % GID))
sec_counts = {s["no"]: (len(s["w"]), len(s["s"]), len(s["e"])) for s in o["secs"]}
for grp in m["grupos"]:
    for p in grp["partes"]:
        if p.get("gid") == GID:
            for s in p["secs"]:
                no = s.get("no")
                if no in sec_counts:
                    w, ss, e = sec_counts[no]
                    s["w"], s["s"], s["e"] = w, ss, e
            print("updated parte gid=%d name=%s" % (GID, p.get("name")))

# recompute global totals from all sec files
tw = ts = te = 0
for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js"))):
    so = load_sec(sp)
    for s in so.get("secs", []):
        tw += len(s.get("w", [])); ts += len(s.get("s", [])); te += len(s.get("e", []))
m["total.w"], m["total.s"], m["total.e"] = tw, ts, te
m["totalAll"] = tw + ts + te

out = "window.BOOK_META=" + json.dumps(m, ensure_ascii=False, separators=(",", ":")) + ";"
open(os.path.join(BASE, "data/meta.js"), "w", encoding="utf-8").write(out)
print("totals: w=%d s=%d e=%d all=%d" % (tw, ts, te, tw+ts+te))
