# -*- coding: utf-8 -*-
import json, re, sys
BASE = "."
t = open("data/meta.js", encoding="utf-8").read()
i = t.index("=") + 1
# balanced brace scan respecting strings
d = 0; inq = False; esc = False; end = None
for k in range(i, len(t)):
    c = t[k]
    if inq:
        if esc: esc = False
        elif c == "\\": esc = True
        elif c == '"': inq = False
    else:
        if c == '"': inq = True
        elif c == "{": d += 1
        elif c == "}":
            d -= 1
            if d == 0:
                end = k + 1; break
mt = json.loads(t[i:end])

def find(o, target):
    out = []
    if isinstance(o, dict):
        if o.get("gid") == target or o.get("id") == target:
            out.append(o)
        for v in o.values():
            out += find(v, target)
    elif isinstance(o, list):
        for v in o:
            out += find(v, target)
    return out

for e in find(mt, int(sys.argv[1]) if len(sys.argv) > 1 else 13):
    print(json.dumps(e, ensure_ascii=False, indent=1))
