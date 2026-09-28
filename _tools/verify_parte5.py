# -*- coding: utf-8 -*-
import re, json, os
BASE = "D:/西班牙语材料/15000词西语随身背"
GID = 4
p = os.path.join(BASE, "data/sec/%d.js" % GID)
src = open(p, encoding="utf-8").read()
prefix = "window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=" % GID
assert src.startswith(prefix), "PREFIX MISMATCH"
eq = src.index("window.BOOK_DATA[%d]=" % GID)
obj = src[eq+len("window.BOOK_DATA[%d]=" % GID):].strip()
if obj.endswith(";"): obj = obj[:-1]
data = json.loads(obj)

span_idx = {'w':1,'e':1,'s':0}
cjk = re.compile(r'[一-鿿]')
hyph = re.compile(r'[a-záéíóúñüA-ZÁÉÍÓÚÑÜ]-[a-záéíóúñü]')
bad_len=[]; cjkbad=[]; hyphbad=[]; residual=[]
bad_tokens=['ba.o','se.al','ca.a','u.a','construción','vidria','da.o','esplio','admitir','fortuna','depilación','cuadro de gasolina','carmino','izquerida','contigente','ferrocaril','añanido','n.pl.','vnt','nnm']
missing=[]; wpb=wpnb=epb=epnb=0
for sec in data["secs"]:
    for mode in ('w','e','s'):
        for row in sec.get(mode,[]):
            if len(row)!=7: bad_len.append((sec['no'],mode,len(row)))
            si=span_idx[mode]; es=row[si] if len(row)>si else ""
            if cjk.search(es): cjkbad.append((sec['no'],mode,es[:40]))
            for h in hyph.findall(es): hyphbad.append((sec['no'],mode,h,es[:40]))
            low=es.lower()
            for bt in bad_tokens:
                if bt in low: residual.append((sec['no'],mode,bt,es[:40]))
            for idx in (3,4):
                if len(row)>idx and row[idx]:
                    fp=os.path.join(BASE,"audio",row[idx])
                    if not os.path.exists(fp): missing.append(row[idx])
            if mode=='w':
                pos=row[2] if len(row)>2 else ""
                if pos.strip(): wpnb+=1
                else: wpb+=1
            if mode=='e':
                pos=row[2] if len(row)>2 else ""
                if pos.strip(): epnb+=1
                else: epb+=1
tw=te=ts=0
for sec in data['secs']:
    tw+=len(sec.get('w',[])); te+=len(sec.get('e',[])); ts+=len(sec.get('s',[]))
print("secs:",len(data['secs']), "W=%d E=%d S=%d TOTAL=%d"%(tw,te,ts,tw+te+ts))
print("BAD LEN:",len(bad_len))
print("CJK-IN-SPANISH:",len(cjkbad))
print("HYPHEN:",len(hyphbad))
print("RESIDUAL:",len(residual), residual[:10])
print("MISSING AUDIO:",len(missing), missing[:10])
print("W pos blank=%d nonblank=%d"%(wpb,wpnb))
print("E pos blank=%d nonblank=%d"%(epb,epnb))
ok = (not bad_len) and (not cjkbad) and (not hyphbad) and (not residual) and (not missing)
print("VERIFY:", "PASS" if ok else "FAIL")
