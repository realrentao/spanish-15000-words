import re, json, sys

path = sys.argv[1]
keys = sys.argv[2:]
txt = open(path, encoding='utf-8').read()
start = txt.index('={') + 1
depth = 0
i = start
instr = False
esc = False
while i < len(txt):
    c = txt[i]
    if instr:
        if esc:
            esc = False
        elif c == '\\':
            esc = True
        elif c == '"':
            instr = False
    else:
        if c == '"':
            instr = True
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
    i += 1
obj = txt[start:i + 1]
data = json.loads(obj)
print("gname:", data.get("gname"), "name:", data.get("name"))
for sec in data["secs"]:
    print("=== sec no", sec.get("no"), "name", sec.get("name"))
    for arr, label in (("w", "W"), ("s", "S"), ("e", "E")):
        if arr in sec:
            for idx, row in enumerate(sec[arr]):
                joined = " | ".join(str(x) for x in row)
                if any(k in joined for k in keys):
                    print("  [%s%d] %s" % (label, idx, joined))
