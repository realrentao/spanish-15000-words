# -*- coding: utf-8 -*-
"""Surgical corrections on data/sec/10.js (Parte 6 其他常见设施), user-confirmed 2026-09-30.

W rows are keyed by (cn, old_es) because 花坛 appears twice with different Spanish.
S rows are keyed by an exact substring of the old Spanish sentence.
Only the Spanish text + its es audio path + IPA change; cn / zh audio / pinyin stay.
Kept as-is on purpose: 阉割 emasculación (user marked it correct, castración is just
more frequent), and every other word the user did not list.

New es audio numbers: reuse an existing on-disk audio when some sec file already
references the SAME normalized Spanish text (avoids duplicate mp3s); otherwise allocate
from disk max+1, also skipping every number already referenced by any sec file.
"""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from es_ipa import text_ipa

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 10

# (cn, old_es, new_es)
W_FIX = [
    ("花坛",   "terraza",               "parterre"),
    ("花坛",   "lecho de flores",       "macizo de flores"),
    ("堆",     "meter",                 "amontonar"),
    ("处理",   "organizar",             "gestionar"),
    ("清除",   "barrer",                "eliminar"),
    ("分解",   "disociar",              "descomponer"),
    ("使畅通", "descongestionar",       "desobstruir"),
    ("成衣",   "vestimenta",            "ropa confeccionada"),
    ("垃圾场", "botadero de vertedero", "vertedero"),
]

# (old_es_substring, new_es_full_replacement_of_that_substring)
S_FIX = [
    ("la llevó a la los correos", "la llevó a la oficina de correos"),
    ("nunca he rendido en búsqueda del sueño", "nunca me he rendido en la búsqueda del sueño"),
]

def norm(s):
    return re.sub(r'[^a-záéíóúñü]', '', (s or "").lower())

# ---- global es-text -> audio path map (for reuse) + taken numbers -------------------
es_by_text = {}
taken = set()
for i2 in range(48):
    fp = os.path.join(BASE, "data/sec/%d.js" % i2)
    if not os.path.exists(fp): continue
    t2 = open(fp, encoding="utf-8").read()
    for mm in re.finditer(r'es/(\d{5})\.mp3', t2): taken.add(int(mm.group(1)))
    for mm in re.finditer(r'zh/(\d{5})\.mp3', t2): pass
    i = t2.index("={") + 1
    d = 0; j = i; ins = False; esc = False
    while j < len(t2):
        c = t2[j]
        if ins:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == '{': d += 1
            elif c == '}':
                d -= 1
                if d == 0: break
        j += 1
    try:
        o2 = json.loads(t2[i:j+1])
    except Exception:
        continue
    for s in o2.get("secs", []):
        for r in s.get("w", []) + s.get("e", []):
            if len(r) == 7 and r[3]:
                es_by_text.setdefault(norm(r[1]), r[3])
        for r in s.get("s", []):
            if len(r) == 7 and r[3]:
                es_by_text.setdefault(norm(r[0]), r[3])

def cur_max(folder):
    m = 0
    for f in os.listdir(os.path.join(BASE, folder)):
        mm = re.match(r'(\d{5})\.mp3$', f)
        if mm: m = max(m, int(mm.group(1)))
    return m

es_n = cur_max("audio/es") + 1
def next_es():
    global es_n
    while es_n in taken: es_n += 1
    n = es_n; es_n = n + 1; taken.add(n)
    return "es/%05d.mp3" % n

def assign(new_es):
    """reuse an existing audio for identical Spanish text, else allocate a new number"""
    cand = es_by_text.get(norm(new_es))
    if cand and os.path.exists(os.path.join(BASE, "audio", cand)):
        return cand, "reuse"
    return next_es(), "new"

# ---- load sec/10.js ----------------------------------------------------------------
path = os.path.join(BASE, "data/sec/%d.js" % GID)
t = open(path, encoding="utf-8").read()
p = t.index("={")
prefix = t[:p+1]
i = p + 1
d = 0; j = i; ins = False; esc = False
while j < len(t):
    c = t[j]
    if ins:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': ins = False
    else:
        if c == '"': ins = True
        elif c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: break
    j += 1
obj = json.loads(t[i:j+1])

changed = []
for s in obj["secs"]:
    for r in s["w"]:
        for cn, old_es, new_es in W_FIX:
            if r[0] == cn and norm(r[1]) == norm(old_es):
                old_path = r[3]
                r[1] = new_es
                r[6] = text_ipa(new_es)
                r[3], how = assign(new_es)
                changed.append(("W", cn, old_es, old_path, new_es, r[3], how))
                break
    for r in s["s"]:
        for old_sub, new_sub in S_FIX:
            if old_sub in r[0]:
                new_es = r[0].replace(old_sub, new_sub)
                old_path = r[3]
                r[0] = new_es
                r[6] = text_ipa(new_es)
                r[3], how = assign(new_es)
                changed.append(("S", r[1][:12], old_sub, old_path, new_es, r[3], how))
                break

expect = len(W_FIX) + len(S_FIX)
assert len(changed) == expect, "expected %d fixes, got %d: %r" % (expect, len(changed), changed)

out = prefix + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";"
open(path, "w", encoding="utf-8").write(out)
for c in changed:
    print("FIXED %s %-8s %r (%s) -> %r (%s) [%s]" % c)
print("next es=%d" % es_n)
