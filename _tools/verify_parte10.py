# -*- coding: utf-8 -*-
"""Verify data/sec/9.js (Parte 10 常见商店). Checks: prefix intact, all rows 7 fields,
no CJK in Spanish field, no mid-word hyphen, no stray OCR tokens, all audio paths exist
(under audio/), valid pos only for w/e rows. Exits 0 on PASS."""
import json, re, os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 9

POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adj","adv.","adv","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev.","conj.","vi.","vt.","p.p.","n.inv.","s.n.","s.adj.","s.adv.","tr.","intr.","ger.","inf.","part."])
def is_pos(t):
    if t in POS: return True
    if re.match(r'^[a-z]{1,3}\.[mf]\.?$', t): return True
    if re.match(r'^[a-z]+\.pl\.?$', t): return True
    if re.match(r'^[a-z]+\.[mf]\.[mf]\.?$', t): return True
    return False

def load_sec(path):
    t = open(path, encoding="utf-8").read()
    if not t.startswith('window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=' % GID):
        print("FAIL prefix", path); return None
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

OCR = ["ba.o","se.al","ca.a","u.a","construción","vidria","da.o","esplio","carmino",
       "izquerida","contigente","ferrocaril","alma-cenes","empe.o","mas-cotas","jo-yer",
       "vebde","tra-baja","se.ora","es-pecial","desmesu-","clara-","trans-porte",
       "incre-mento","co-mestibles","su-bida","mer-canc","es-trella","importante.Tú"]

ok=True
o=load_sec(os.path.join(BASE,"data/sec/%d.js"%GID))
secs=o["secs"]
tw=ts=te=0
for s in secs:
    for kind,arr in (("w",s["w"]),("e",s["e"]),("s",s["s"])):
        for r in arr:
            if len(r)!=7:
                print("FAIL len",kind,r); ok=False
                continue
            es = r[1] if kind!="s" else r[0]
            zh = r[0] if kind!="s" else r[1]
            if re.search(r'[一-鿿]', es):
                print("FAIL cjk in es",kind,es); ok=False
            if re.search(r'[A-Za-zÁÉÍÓÚÑÜáéíóúñü]-[A-Za-zÁÉÍÓÚÑÜáéíóúñü]', es):
                print("FAIL hyphen",kind,es); ok=False
            if re.search(r'[A-Za-zÁÉÍÓÚÑÜáéíóúñü]\.[A-Za-zÁÉÍÓÚÑÜáéíóúñü]', es):
                print("FAIL middot",kind,es); ok=False
            low=es.lower()
            for bad in OCR:
                if bad in low:
                    print("FAIL ocr",bad,kind,es); ok=False
            for p in (r[3], r[4]):
                if p and not os.path.exists(os.path.join(BASE,"audio",p)):
                    print("FAIL audio missing",p,kind,es); ok=False
            # pos validity only for w/e (s row[2] is 出处/source, not pos)
            if kind != "s":
                pos = r[2]
                if pos:
                    for unit in re.split(r'[ &\/,]', pos):
                        if unit and not is_pos(unit):
                            print("FAIL pos", kind, r); ok=False
            if kind=="w": tw+=1
            elif kind=="s": ts+=1
            else: te+=1
print("sections:", len(secs), "/ W=%d S=%d E=%d totalAll=%d"%(tw,ts,te,tw+ts+te))
print("VERIFY PASS" if ok else "VERIFY FAIL")
sys.exit(0 if ok else 1)
