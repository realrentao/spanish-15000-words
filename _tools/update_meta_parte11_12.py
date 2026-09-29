# -*- coding: utf-8 -*-
"""Sync data/meta.js for gids 11+12: update each parte's sec counts from
data/sec/11.js & 12.js, then recompute global totals from ALL sec files (authoritative)."""
import json, re, os, glob
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIDS = [11, 12]

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

counts = {}
for GID in GIDS:
    o = load_sec(os.path.join(BASE, "data/sec/%d.js"%GID))
    for s in o["secs"]:
        counts[(GID, s["no"])] = (len(s["w"]), len(s["s"]), len(s["e"]))

mp = os.path.join(BASE, "data/meta.js")
mt = open(mp, encoding="utf-8").read()
mi = mt.index("=") + 1
m = json.loads(mt[mi:mt.index(";", mi)])

for g in m["grupos"]:
    for p in g["partes"]:
        if p.get("gid") in GIDS:
            seen=0
            for s in p["secs"]:
                key=(p["gid"], s["no"])
                if key in counts:
                    w,ss,e = counts[key]
                    s["w"]=w; s["s"]=ss; s["e"]=e
                    seen+=1
                    print("gid=%d sec %d -> w=%d s=%d e=%d"%(p["gid"],s["no"],w,ss,e))
            if seen != len([k for k in counts if k[0]==p["gid"]]):
                print("WARN gid=%d: meta secs seen=%d, sec-file secs=%d"%(
                    p["gid"], seen, len([k for k in counts if k[0]==p["gid"]])))

tw=ts=te=0
for sp in sorted(glob.glob(os.path.join(BASE,"data/sec/*.js"))):
    so = load_sec(sp)
    for s in so.get("secs",[]):
        tw+=len(s.get("w",[])); ts+=len(s.get("s",[])); te+=len(s.get("e",[]))
m["total.w"]=tw; m["total.s"]=ts; m["total.e"]=te; m["totalAll"]=tw+ts+te

out = 'window.BOOK_META=' + json.dumps(m, ensure_ascii=False, separators=(",",":")) + ";"
open(mp,"w",encoding="utf-8").write(out)
print("updated totals: w=%d s=%d e=%d all=%d"%(tw,ts,te,tw+ts+te))
