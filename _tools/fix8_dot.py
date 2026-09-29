# -*- coding: utf-8 -*-
"""Text-only cleanup for sec/7.js: remove stray '.' directly preceding an uppercase
letter at a sentence boundary (e.g. 'cierre. .Se cuenta' -> 'cierre. Se cuenta').
Does NOT change any audio paths. The referenced audio is already correct."""
import json, re, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(BASE, "data/sec/7.js")
t = open(path, encoding="utf-8").read()
i = t.index("={") + 1
depth = 0; j = i; ins = False; esc = False
while j < len(t):
    c = t[j]
    if ins:
        if esc:
            esc = False
        elif c == '\\':
            esc = True
        elif c == '"':
            ins = False
    else:
        if c == '"':
            ins = True
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
    j += 1
o = json.loads(t[i:j + 1])

DOT = re.compile(r'(?<=[\s.])\.(?=[A-ZÁÉÍÓÚÑÜ])')
n = 0
for s in o["secs"]:
    for r in s["w"]:
        if DOT.search(r[1]):
            r[1] = DOT.sub('', r[1]); n += 1
    for r in s["e"]:
        if DOT.search(r[1]):
            r[1] = DOT.sub('', r[1]); n += 1
    for r in s["s"]:
        if DOT.search(r[0]):
            r[0] = DOT.sub('', r[0]); n += 1

out = t[:i] + json.dumps(o, ensure_ascii=False, separators=(",", ":")) + ";"
open(path, "w", encoding="utf-8").write(out)
print("stray-dot fixes applied:", n)
