# -*- coding: utf-8 -*-
"""Full integrity check for data/sec/8.js (Parte 9 在理发店 / gid=8)."""
import json, re, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 8

def load_sec(path):
    t = open(path, encoding="utf-8").read()
    i = t.index("={") + 1
    depth = 0; j = i; ins = False; esc = False
    while j < len(t):
        c = t[j]
        if ins:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
        j += 1
    return t, json.loads(t[i:j+1])

txt, o = load_sec(os.path.join(BASE, "data/sec/%d.js" % GID))
prefix = "window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=" % GID
ok = True
if not txt.startswith(prefix):
    print("FAIL prefix"); ok = False

POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adj","adv.","adv","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev.","conj.","vi.","vt.","p.p.","n.inv.","s.n.","s.adj.","s.adv.","tr.","intr.","ger.","inf.","part."])
def is_pos(t):
    if t in POS: return True
    if re.match(r'^[a-z]{1,3}\.[mf]\.?$', t): return True
    if re.match(r'^[a-z]+\.pl\.?$', t): return True
    if re.match(r'^[a-z]+\.[mf]\.[mf]\.?$', t): return True
    # multi-unit pos joined by & / , / space e.g. "prep. & adv."
    if re.match(r'^([a-z]{1,4}\.?)([ &,][a-z]{1,4}\.?)+$', t): return True
    return False

tw = ts = te = 0
for s in o["secs"]:
    for kind, arr in (("w", s["w"]), ("e", s["e"]), ("s", s["s"])):
        for r in arr:
            if len(r) != 7:
                print("FAIL len!=7", kind, r); ok = False
            if kind == "s":
                es, zh = r[0], r[1]
            else:
                es, zh = r[1], r[0]
            if re.search(r'[一-鿿]', es):
                print("FAIL CJK in Spanish", kind, r); ok = False
            if re.search(r'(?<=[A-Za-z])-(?=[A-Za-z])', es):
                print("FAIL midword hyphen", kind, r); ok = False
            if re.search(r'[aeiouáéíóúAEIOUÁÉÍÓÚ]\.[aeiouáéíóúAEIOUÁÉÍÓÚ]', es):
                print("FAIL vowel.vowel", kind, r); ok = False
            if re.search(r'(?<=[A-Za-z])\.(?=[A-Za-z])', es):
                print("FAIL stray dot", kind, r); ok = False
            # pos validity only for w/e (s row[2] is 出处/source, not pos)
            if kind != "s":
                pos = r[2]
                if pos and not is_pos(pos):
                    print("FAIL pos", kind, r); ok = False
            # audio paths exist
            for p in (r[3], r[4]):
                fp = os.path.join(BASE, "audio", p)
                if not os.path.exists(fp):
                    print("FAIL missing audio", p, r); ok = False
    tw += len(s["w"]); ts += len(s["s"]); te += len(s["e"])

print("sections: %d / W=%d S=%d E=%d totalAll=%d" % (len(o["secs"]), tw, ts, te, tw+ts+te))
print("VERIFY PASS" if ok else "VERIFY FAIL")
