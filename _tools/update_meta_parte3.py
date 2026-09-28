# -*- coding: utf-8 -*-
"""Sync data/meta.js counts for Parte 3 (gid=2) from the rebuilt data/sec/2.js,
and recompute global totals. Preserves all other partes unchanged."""
import json, re, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 2

# load rebuilt sec/2.js
t = open(os.path.join(BASE, "data/sec/%d.js" % GID), encoding="utf-8").read()
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
obj = json.loads(t[i:j+1])
sec_counts = {s["no"]: (len(s["w"]), len(s["s"]), len(s["e"])) for s in obj["secs"]}

# load meta.js
mt = open(os.path.join(BASE, "data/meta.js"), encoding="utf-8").read()
mi = mt.index("=") + 1
mt2 = mt[mi:]
depth=0; k=0; ins=False; esc=False
while k < len(mt2):
    c=mt2[k]
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
    k+=1
meta = json.loads(mt2[:k+1])

# find parte gid=2 and update its sec counts
updated = 0
for g in meta["grupos"]:
    for p in g["partes"]:
        if p.get("gid") == GID:
            for sc in p["secs"]:
                no = sc["no"]
                if no in sec_counts:
                    w,s,e = sec_counts[no]
                    sc["w"]=w; sc["s"]=s; sc["e"]=e
                    updated += 1

# recompute totals
tw=ts=te=0
for g in meta["grupos"]:
    for p in g["partes"]:
        for sc in p["secs"]:
            tw+=sc.get("w",0); ts+=sc.get("s",0); te+=sc.get("e",0)
meta["total.w"]=tw; meta["total.s"]=ts; meta["total.e"]=te
meta["totalAll"]=tw+ts+te
# also per-parte totals
for g in meta["grupos"]:
    for p in g["partes"]:
        pw=ps=pe=0
        for sc in p["secs"]:
            pw+=sc.get("w",0); ps+=sc.get("s",0); pe+=sc.get("e",0)
        p["total"]=pw+ps+pe

open(os.path.join(BASE,"data/meta.js"),"w",encoding="utf-8").write(
    "window.BOOK_META=" + json.dumps(meta, ensure_ascii=False, separators=(",",":")) + ";")
print("updated secs:", updated, " totals: w=%d s=%d e=%d all=%d" % (tw,ts,te,meta["totalAll"]))
