# -*- coding: utf-8 -*-
"""Probe book/meta state for gid=11 (人的特征) / gid=12 (人身体的行为) and
current audio numbering + fix9 reuse candidates."""
import json, re, os

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

def norm(s):
    return re.sub(r'[^a-záéíóúñü]', '', (s or "").lower())

bj=json.load(open(os.path.join(BASE,"data/book.json"),encoding="utf-8"))
for idx in (9,10,11,12):
    p=bj["partes"][idx]
    print("book parte[%d] name=%r secs=%s"%(idx,p.get("name"),[(s["no"],s.get("name",""),len(s.get("words",[])),len(s.get("sents",[])),len(s.get("extra",[]))) for s in p["secs"]]))

mt=open(os.path.join(BASE,"data/meta.js"),encoding="utf-8").read()
mi=mt.index("=")+1
m=json.loads(mt[mi:mt.index(";",mi)])
for g in m["grupos"]:
    for p in g["partes"]:
        if p.get("gid") in (10,11,12):
            print("meta gid=%d name=%r secs=%s"%(p["gid"],p.get("name"),[(s["no"],s.get("name",""),s.get("w"),s.get("s"),s.get("e")) for s in p["secs"]]))

esmax=zhmax=0
for d,tag in (("audio/es","es"),("audio/zh","zh")):
    mx=0
    for f in os.listdir(os.path.join(BASE,d)):
        mm=re.match(r'(\d{5})\.mp3$',f)
        if mm: mx=max(mx,int(mm.group(1)))
    print("max %s = %d (%d files)"%(tag,mx,len(os.listdir(os.path.join(BASE,d)))))

# fix9 rows current state + global reuse candidates
o9=load_sec(os.path.join(BASE,"data/sec/9.js"))
for s in o9["secs"]:
    for r in s["w"]:
        if r[0] in ("蔬菜水果店","寄卖商店"):
            print("sec9 W row:", r[:5])
targets={norm("mercado de hortalizas"), norm("tienda de consignación")}
hits=set()
for i in range(48):
    fp=os.path.join(BASE,"data/sec/%d.js"%i)
    if not os.path.exists(fp): continue
    o=load_sec(fp)
    for s in o.get("secs",[]):
        for kind,arr in (("w",s.get("w",[])),("e",s.get("e",[])),("s",s.get("s",[]))):
            for r in arr:
                es=r[1] if kind!="s" else r[0]
                if norm(es) in targets:
                    p=r[3]
                    exists=os.path.exists(os.path.join(BASE,"audio",p))
                    print("reuse candidate: gid=%d sec%s kind=%s es=%r path=%s exists=%s"%(i,s["no"],kind,es,p,exists))
                    if exists: hits.add(norm(es))
print("norm targets covered by existing audio:", sorted(hits))
