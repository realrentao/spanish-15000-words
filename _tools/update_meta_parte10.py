# -*- coding: utf-8 -*-
"""Sync data/meta.js for gid=9 (常见商店): update each sec's w/s/e counts from
data/sec/9.js, then recompute global totals from ALL sec files (authoritative)."""
import json, re, os, glob
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 9

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

# load new counts from sec/9.js
o = load_sec(os.path.join(BASE, "data/sec/%d.js"%GID))
counts = {}
for s in o["secs"]:
    counts[s["no"]] = (len(s["w"]), len(s["s"]), len(s["e"]))

# load meta
mp = os.path.join(BASE, "data/meta.js")
mt = open(mp, encoding="utf-8").read()
mi = mt.index("=") + 1
m = json.loads(mt[mi:mt.index(";", mi)])

found=False
for g in m["grupos"]:
    for p in g["partes"]:
        if p.get("gid") == GID:
            found=True
            for s in p["secs"]:
                no = s["no"]
                if no in counts:
                    w,s2,e = counts[no]
                    s["w"]=w; s["s"]=s2; s["e"]=e
                    print("sec", no, "-> w=%d s=%d e=%d"%(w,s2,e))
assert found, "gid %d not found in meta"%GID

# recompute global totals from ALL sec files
tw=ts=te=0
for sp in sorted(glob.glob(os.path.join(BASE,"data/sec/*.js"))):
    so = load_sec(sp)
    for s in so.get("secs",[]):
        tw+=len(s.get("w",[])); ts+=len(s.get("s",[])); te+=len(s.get("e",[]))
m["total.w"]=tw; m["total.s"]=ts; m["total.e"]=te; m["totalAll"]=tw+ts+te

out = 'window.BOOK_META=' + json.dumps(m, ensure_ascii=False, separators=(",",":")) + ";"
open(mp,"w",encoding="utf-8").write(out)
print("updated totals: w=%d s=%d e=%d all=%d"%(tw,ts,te,tw+ts+te))
