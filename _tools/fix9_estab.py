# -*- coding: utf-8 -*-
"""Surgical ES_FIX on data/sec/9.js (Parte 10 常见商店), user-confirmed 2026-09-29:
蔬菜水果店 mercantes de hortalizas -> mercado de hortalizas
寄卖商店   comisión de comercio  -> tienda de consignación
Only es text + es audio path + IPA change (cn + zh audio unchanged). Old es audio files
(es/06832.mp3, es/06834.mp3) become unreferenced; left on disk harmlessly."""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from es_ipa import text_ipa

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 9
FIXES = {"蔬菜水果店":"mercado de hortalizas", "寄卖商店":"tienda de consignación"}

path = os.path.join(BASE, "data/sec/%d.js" % GID)
t = open(path, encoding="utf-8").read()
p = t.index("={")
prefix = t[:p+1]           # includes the '='
i = p + 1                  # index of '{'
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

def cur_max(folder):
    m=0
    for f in os.listdir(os.path.join(BASE,folder)):
        mm=re.match(r'(\d{5})\.mp3$', f)
        if mm: m=max(m,int(mm.group(1)))
    return m
es_n = cur_max("audio/es") + 1

changed=[]
for s in obj["secs"]:
    for r in s["w"]:
        if r[0] in FIXES:
            new_es = FIXES[r[0]]
            old_es, old_ep = r[1], r[3]
            r[1] = new_es
            r[6] = text_ipa(new_es)
            r[3] = "es/%05d.mp3" % es_n; es_n += 1
            changed.append((r[0], old_es, old_ep, new_es, r[3]))
assert len(changed) == 2, "expected exactly 2 rows, got %r" % (changed,)

out = prefix + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";"
open(path, "w", encoding="utf-8").write(out)
for c in changed:
    print("FIXED cn=%r  es %r (%s) -> %r (%s)" % c)
