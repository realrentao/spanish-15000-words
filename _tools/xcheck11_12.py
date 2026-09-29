# -*- coding: utf-8 -*-
"""Cross-check: recompute sums from all sec files and compare with data/meta.js
(per-gid parte sec counts + global totals). Exits 0 on MATCH."""
import json, re, os, glob
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

sec_sums={}   # gid -> {no:(w,s,e)}
tw=ts=te=0
for sp in sorted(glob.glob(os.path.join(BASE,"data/sec/*.js"))):
    gid=int(re.search(r'(\d+)\.js$',sp).group(1))
    o=load_sec(sp)
    d={}
    for s in o.get("secs",[]):
        d[s["no"]]=(len(s.get("w",[])),len(s.get("s",[])),len(s.get("e",[])))
        tw+=d[s["no"]][0]; ts+=d[s["no"]][1]; te+=d[s["no"]][2]
    sec_sums[gid]=d

mt=open(os.path.join(BASE,"data/meta.js"),encoding="utf-8").read()
mi=mt.index("=")+1
m=json.loads(mt[mi:mt.index(";",mi)])

ok=True
for g in m["grupos"]:
    for p in g["partes"]:
        gid=p.get("gid")
        if gid not in sec_sums: continue
        for s in p["secs"]:
            want=sec_sums[gid].get(s["no"])
            got=(s.get("w"),s.get("s"),s.get("e"))
            if want and want!=got:
                print("MISMATCH gid=%d sec=%s meta=%s actual=%s"%(gid,s["no"],got,want)); ok=False

mtot=(m.get("total.w"),m.get("total.s"),m.get("total.e"),m.get("totalAll"))
actual=(tw,ts,te,tw+ts+te)
print("meta totals:",mtot)
print("sec  totals:",actual)
if mtot!=actual: ok=False
print("XCHECK MATCH" if ok else "XCHECK MISMATCH")
import sys; sys.exit(0 if ok else 1)
