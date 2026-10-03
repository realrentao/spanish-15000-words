# -*- coding: utf-8 -*-
import os, json, glob
BASE = "D:/西班牙语材料/15000词西语随身背"
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
tw=ts=te=0; nsec=0
for sp in sorted(glob.glob(os.path.join(BASE,"data/sec/*.js"))):
    o=load_sec(sp)
    for s in o.get("secs",[]):
        tw+=len(s.get("w",[])); ts+=len(s.get("s",[])); te+=len(s.get("e",[])); nsec+=1
print("sum over sec files: w=%d s=%d e=%d all=%d  secs=%d" % (tw,ts,te,tw+ts+te,nsec))
mt=open(os.path.join(BASE,"data/meta.js"),encoding="utf-8").read()
mi=mt.index("=")+1; m=json.loads(mt[mi:mt.index(";",mi)])
print("meta totalAll=", m["totalAll"], "w=%d s=%d e=%d"%(m["total.w"],m["total.s"],m["total.e"]))
print("MATCH" if (tw+ts+te)==m["totalAll"] else "MISMATCH")
