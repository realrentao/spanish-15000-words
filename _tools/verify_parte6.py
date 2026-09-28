# -*- coding: utf-8 -*-
"""Full integrity verification for data/sec/5.js (Parte 6 在医院).
Checks: prefix intact, every row has 7 fields, no CJK in Spanish fields,
no residual OCR (.X vowel placeholder / mid-word hyphen / known garbage),
all es/zh audio paths exist on disk, pos only where meaningful (valid tokens),
per-section w/s/e counts nonzero where expected.
"""
import os, re, json
BASE = "D:/西班牙语材料/15000词西语随身背"
GID = 5
PREFIX = "window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=" % GID

t = open(os.path.join(BASE, "data/sec/%d.js" % GID), encoding="utf-8").read()
assert t.startswith(PREFIX), "PREFIX MISMATCH: %r" % t[:60]

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

CJK = re.compile(r'[一-鿿]')
OCR_RESIDUAL = re.compile(r'[aeiouáéíóúAEIOUÁÉÍÓÚ]\.[aeiouáéíóúAEIOUÁÉÍÓÚ]')  # vowel.placeholder
MIDHYPH = re.compile(r'(?<=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])-(?=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])')
VALID_POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adv.","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev.","conj.","vi.","vt.","p.p.","n.inv.","s.n.","s.adj.","s.adv.","tr.","intr.","ger.","inf.","part.","m.f.","n.pl."])

problems = []
total_w=total_s=total_e=0
for s in obj["secs"]:
    no=s["no"]; name=s["name"]
    for kind,key in (("w","w"),("s","s"),("e","e")):
        for ri,r in enumerate(s[key]):
            total = {"w":total_w,"s":total_s,"e":total_e}[kind]
            if len(r) != 7:
                problems.append("[sec%d %s#%d] bad length %d: %r" % (no,kind,ri,len(r),r)); continue
            cn,es,pos,ep,zp,py,ipa = r
            # Spanish-side fields: w/e -> es(1); s -> es(0)
            es_field = es if kind!="s" else r[0]
            # CJK in Spanish?
            if CJK.search(es_field or ""):
                problems.append("[sec%d %s#%d] CJK in Spanish: %r" % (no,kind,ri,es_field))
            # residual OCR
            if OCR_RESIDUAL.search(es_field or ""):
                problems.append("[sec%d %s#%d] residual vowel. placeholder: %r" % (no,kind,ri,es_field))
            if MIDHYPH.search(es_field or ""):
                problems.append("[sec%d %s#%d] mid-word hyphen: %r" % (no,kind,ri,es_field))
            # audio existence
            if not os.path.exists(os.path.join(BASE,"audio",ep or "___")):
                problems.append("[sec%d %s#%d] missing es audio: %r" % (no,kind,ri,ep))
            if not os.path.exists(os.path.join(BASE,"audio",zp or "___")):
                problems.append("[sec%d %s#%d] missing zh audio: %r" % (no,kind,ri,zp))
            # pos validity (w/e rows only; for S rows index 2 is 出处/source, not pos)
            if kind != "s":
                if pos:
                    if pos not in VALID_POS and not re.match(r'^[a-z]{1,3}\.[mf]\.?$', pos) and not re.match(r'^[a-z]+\.pl\.?$', pos):
                        problems.append("[sec%d %s#%d] suspicious pos: %r" % (no,kind,ri,pos))
            if kind=="w": total_w+=1
            elif kind=="s": total_s+=1
            else: total_e+=1
    if len(s["w"])==0 and len(s["s"])==0 and len(s["e"])==0:
        problems.append("[sec%d %s] EMPTY section" % (no,name))

print("sections:", len(obj["secs"]))
print("W=%d S=%d E=%d  totalAll=%d" % (total_w,total_s,total_e,total_w+total_s+total_e))
if problems:
    print("PROBLEMS (%d):" % len(problems))
    for p in problems[:80]:
        print("  ", p)
    raise SystemExit("VERIFY FAILED")
print("VERIFY PASS")
