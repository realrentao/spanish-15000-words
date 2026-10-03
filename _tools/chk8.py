# -*- coding: utf-8 -*-
import json, re
t = open("data/sec/7.js", encoding="utf-8").read()
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

def find(o, sub, field=0):
    for s in o["secs"]:
        for kind, arr in (("w", s["w"]), ("e", s["e"]), ("s", s["s"])):
            for r in arr:
                if sub in r[field]:
                    print(kind, r)

print("== W 农业银行 ==")
find(o, "农业银行")
print("== W 手续费 ==")
find(o, "手续费")
print("== W 自动取款机 (es field) ==")
find(o, "自动取款机")
print("== S cleaned samples ==")
for s in o["secs"]:
    for r in s["s"]:
        if "auto" in r[0] or "diferen" in r[0] or "extranj" in r[0]:
            print("S", r[0])
