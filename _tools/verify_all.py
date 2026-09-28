# -*- coding: utf-8 -*-
import os, glob, re, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1) missing audio check across all sec files
refs=set()
for f in glob.glob(os.path.join(BASE,"data","sec","*.js")):
    t=open(f,encoding="utf-8").read()
    for m in re.findall(r'"(?:es|zh)/\d{5}\.mp3"', t):
        refs.add(m.strip('"'))
missing=[r for r in refs if not os.path.exists(os.path.join(BASE,"audio",r))]
print("total audio refs:", len(refs), "missing:", len(missing))
for r in missing[:50]:
    print("  MISSING", r)

# 2) prefix check sec/0.js
t=open(os.path.join(BASE,"data","sec","0.js"),encoding="utf-8").read()
print("sec0 prefix OK:", t.startswith('window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[0]='))

# 3) meta parse
mt=open(os.path.join(BASE,"data","meta.js"),encoding="utf-8").read()
i=mt.index("={")+1; d=0; j=i; s=False; e=False
while j<len(mt):
    c=mt[j]
    if s:
        if e: e=False
        elif c=='\\': e=True
        elif c=='"': s=False
    else:
        if c=='"': s=True
        elif c=='{': d+=1
        elif c=='}':
            d-=1
            if d==0: break
    j+=1
meta=json.loads(mt[i:j+1])
print("meta total:", meta.get("total"), "totalAll:", meta.get("totalAll"))

# 4) gid0 counts
g0=meta["grupos"][0]
for sc in g0["partes"][0]["secs"]:
    print(f"  sec{sc['no']:>2} w={sc.get('w',0)} s={sc.get('s',0)} e={sc.get('e',0)}")
