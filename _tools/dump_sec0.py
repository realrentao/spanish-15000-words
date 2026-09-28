# -*- coding: utf-8 -*-
import json

t = open("data/sec/0.js", encoding="utf-8").read()
start = t.index("={") + 1
depth = 0
i = start
instr = False
esc = False
while i < len(t):
    c = t[i]
    if instr:
        if esc:
            esc = False
        elif c == "\\":
            esc = True
        elif c == '"':
            instr = False
    else:
        if c == '"':
            instr = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
    i += 1
obj = json.loads(t[start:i + 1])

for sec in obj["secs"]:
    print("=" * 70)
    print("SECCION %s  %s" % (sec["no"], sec["name"]))
    for arr, lab in (("w", "W"), ("s", "S"), ("e", "E")):
        if arr in sec:
            print("  --- %s (%d) ---" % (lab, len(sec[arr])))
            for row in sec[arr]:
                print("    %s | %s" % (lab, " | ".join(str(x) for x in row)))
