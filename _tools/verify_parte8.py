# -*- coding: utf-8 -*-
"""Full integrity check for data/sec/7.js (Parte 8 在银行 / gid=7)."""
import json, re, os
BASE = "D:/西班牙语材料/15000词西语随身背"
GID = 7
POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adj","adv.","adv","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev.","conj.","vi.","vt.","p.p.","n.inv.","s.n.","s.adj.","s.adv.","tr.","intr.","ger.","inf.","part."])
def is_pos(t):
    if t in POS: return True
    if re.match(r'^[a-z]{1,3}\.[mf]\.?$', t): return True
    if re.match(r'^[a-z]+\.pl\.?$', t): return True
    if re.match(r'^[a-z]+\.[mf]\.[mf]\.?$', t): return True
    return False

t = open(os.path.join(BASE,"data/sec/%d.js"%GID), encoding="utf-8").read()
prefix = "window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=" % GID
ok = True
if not t.startswith(prefix):
    print("FAIL prefix"); ok = False
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
o = json.loads(t[i:j+1])

CJK = re.compile(r'[一-鿿]')
OCR = re.compile(r'(ba\.o|se\.al|ca\.a|u\.a|construción|vidria|da\.o|esplio|admitir|fortuna|depilación|cuadro de gasolina|carmino|izquerida|contigente|ferrocaril|fartidiar|agricultural)')
suspect_pos = re.compile(r'^[A-Za-z]')

tw=ts=te=0; nsec=0
for s in o["secs"]:
    nsec+=1
    for kind, arr, esi in (("w",s["w"],1),("e",s["e"],1),("s",s["s"],0)):
        for r in arr:
            if len(r)!=7:
                print("FAIL len", kind, r); ok=False
            es = r[esi]
            if CJK.search(es):
                print("FAIL cjk-in-es", kind, r); ok=False
            if OCR.search(es):
                print("FAIL ocr-residue", kind, r); ok=False
            if re.search(r'(?<=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])-(?=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])', es):
                print("FAIL hyphen", kind, r); ok=False
            # pos validity only for w/e (s row[2] is 出处/source, not pos)
            if kind != "s":
                pos = r[2]
                if pos:
                    units = re.split(r'[&\s,]+', pos.strip())
                    if any(u and not is_pos(u) for u in units):
                        print("FAIL pos", kind, r); ok=False
            # audio paths exist
            for p in (r[3], r[4]):
                if p and not os.path.exists(os.path.join(BASE,"audio",p)):
                    print("FAIL missing-audio", kind, p, r); ok=False
            if kind=="w": tw+=1
            elif kind=="s": ts+=1
            else: te+=1

print("sections: %d / W=%d S=%d E=%d totalAll=%d" % (nsec, tw, ts, te, tw+ts+te))
print("VERIFY PASS" if ok else "VERIFY FAIL")
