# -*- coding: utf-8 -*-
"""Final verification for Parte 4 (gid=3) after audio generation.
Checks: prefix, field lengths, Spanish-field CJK/hyphen/residual-OCR leaks,
pos-blanking, all audio refs exist on disk, gid=3 meta matches sec/3.js,
and no orphan audio in the new ranges."""
import re, os, json, glob
BASE = "D:/西班牙语材料/15000词西语随身背"
GID = 3
PREFIX = "window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=" % GID

p = os.path.join(BASE, "data/sec/%d.js" % GID)
src = open(p, encoding="utf-8").read()
assert src.startswith(PREFIX), "PREFIX MISMATCH"
eq = src.index("window.BOOK_DATA[%d]=" % GID)
obj = src[eq + len("window.BOOK_DATA[%d]=" % GID):].strip()
if obj.endswith(";"): obj = obj[:-1]
data = json.loads(obj)

span_idx = {'w':1,'e':1,'s':0}
cjk = re.compile(r'[一-鿿]')
hyph = re.compile(r'[a-záéíóúñüA-ZÁÉÍÓÚÑÜ]-[a-záéíóúñü]')
bad_tokens = ['ba.o','se.al','ca.a','u.a','construción','vidria','monu-mento','ca-llejón']
bad_len=[]; cjkbad=[]; hyphbad=[]; residual=[]; refs=set()
wpb=wpnb=epb=epnb=0
for sec in data["secs"]:
    for mode in ('w','e','s'):
        for row in sec.get(mode,[]):
            if len(row)!=7: bad_len.append((sec['no'],mode,len(row)))
            si=span_idx[mode]; es=row[si] if len(row)>si else ""
            if cjk.search(es): cjkbad.append((sec['no'],mode,es[:50]))
            for h in hyph.findall(es): hyphbad.append((sec['no'],mode,h,es[:60]))
            low=es.lower()
            for bt in bad_tokens:
                if bt in low: residual.append((sec['no'],mode,bt,es[:50]))
            for idx in (3,4):
                if len(row)>idx and row[idx]: refs.add(row[idx])
            if mode=='w':
                pos=row[2] if len(row)>2 else ""
                if pos.strip(): wpnb+=1
                else: wpb+=1
            if mode=='e':
                pos=row[2] if len(row)>2 else ""
                if pos.strip(): epnb+=1
                else: epb+=1
missing=[r for r in refs if not os.path.exists(os.path.join(BASE,"audio",r))]
print("PREFIX OK, secs=%d, W=%d E=%d S=%d"%(len(data['secs']),
      sum(len(s.get('w',[])) for s in data['secs']),
      sum(len(s.get('e',[])) for s in data['secs']),
      sum(len(s.get('s',[])) for s in data['secs'])))
print("BAD LEN:",len(bad_len),"| CJK:",len(cjkbad),"| HYPHEN:",len(hyphbad),"| RESIDUAL:",len(residual))
print("MISSING AUDIO:",len(missing), missing[:10])
print("W pos blank=%d nonblank=%d | E pos blank=%d nonblank=%d"%(wpb,wpnb,epb,epnb))

# gid=3 meta match
mt=open(os.path.join(BASE,"data/meta.js"),encoding="utf-8").read()
mi=mt.index("=")+1; m2=mt[mi:]; d=0;k=0;ins=False;esc=False
while k<len(m2):
    c=m2[k]
    if ins:
        if esc: esc=False
        elif c=='\\': esc=True
        elif c=='"': ins=False
    else:
        if c=='"': ins=True
        elif c=='{': d+=1
        elif c=='}':
            d-=1
            if d==0: break
    k+=1
meta=json.loads(m2[:k+1])
g3=[p for g in meta["grupos"] for p in g["partes"] if p.get("gid")==GID][0]
mmatch=True
for sc in g3["secs"]:
    sec=[s for s in data["secs"] if s["no"]==sc["no"]][0]
    if (sc["w"],sc["s"],sc["e"])!=(len(sec["w"]),len(sec["s"]),len(sec["e"])):
        mmatch=False; print("  META MISMATCH sec",sc["no"],sc, (len(sec["w"]),len(sec["s"]),len(sec["e"])))
print("GID3 META MATCH:", mmatch)

# orphan check in new ranges (referenced by sec/3.js only)
new_es=list(range(6447,6525)); new_zh=list(range(7220,7298))
orph=[]
for n in new_es:
    rel="es/%05d.mp3"%n
    if rel not in refs and os.path.exists(os.path.join(BASE,"audio",rel)): orph.append(rel)
for n in new_zh:
    rel="zh/%05d.mp3"%n
    if rel not in refs and os.path.exists(os.path.join(BASE,"audio",rel)): orph.append(rel)
print("ORPHAN new-range audio (unreferenced):", len(orph), orph)

ok = (len(bad_len)==0 and len(cjkbad)==0 and len(hyphbad)==0 and len(residual)==0
      and len(missing)==0 and mmatch and len(orph)==0)
print("VERIFY RESULT:", "PASS ✓" if ok else "FAIL ✗")
