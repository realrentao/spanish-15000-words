# -*- coding: utf-8 -*-
import pickle, sys, re, os
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = pickle.load(open(os.path.join(ROOT, "_tools", "_ipa_pairs.pkl"), "rb"))

def find(pat, n=4):
    r = [(k, v) for k, v in p.items() if re.search(pat, k) and " " not in k]
    print("##", pat, "hits:", len(r))
    for k, v in r[:n]:
        print("   ", k, "->", v)

for pat in [r'cia$', r'familia', r'oficina', r'historia', r'memoria', r'^limpio', r'^sucio',
            r'^premio', r'^serio', r'cuidad', r'^viuda', r'^agua$', r'io$',
            r'ey$', r'ay$', r'oy$', r'uy$', r'^club', r'^algo', r'^falda', r'^caldo',
            r'^M', r'^cuando', r'^aunque', r'^guante', r'^quiero', r'^tierra', r'^viejo',
            r'^mujer', r'^taxi', r'^oxi', r'^abogado', r'^subray']:
    find(pat)
