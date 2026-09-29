# -*- coding: utf-8 -*-
"""Audit: across all data/sec/*.js, every audio path must map to exactly ONE text
(no two different texts sharing a path), and report missing file count."""
import os, re, glob, collections
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import json

def load_sec2(path):
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

p2t = {}   # path -> set of texts
total=0; missing=0
for sp in sorted(glob.glob(os.path.join(BASE,"data/sec/*.js"))):
    o=load_sec2(sp)
    for s in o.get("secs",[]):
        for kind,arr in (("w",s.get("w",[])),("e",s.get("e",[])),("s",s.get("s",[]))):
            for r in arr:
                es_t = r[0] if kind=="s" else r[1]
                zh_t = r[1] if kind=="s" else r[0]
                for txt,p in ((es_t,r[3]),(zh_t,r[4])):
                    if not p: continue
                    total+=1
                    p2t.setdefault(p,set()).add(txt)
                    if not os.path.exists(os.path.join(BASE,"audio",p)): missing+=1
conf={p:ts for p,ts in p2t.items() if len(ts)>1}
print("total refs:", total, "| paths:", len(p2t), "| missing files:", missing)
print("PATH COLLISIONS (path -> multiple texts):", len(conf))
for p,ts in list(conf.items())[:10]:
    print("  COLLIDE", p, sorted(ts))
print("AUDIT PASS" if not conf else "AUDIT FAIL")
