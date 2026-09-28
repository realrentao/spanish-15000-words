import json, sys

gid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
t = open(f"data/sec/{gid}.js", encoding="utf-8").read()
start = t.index("={") + 1
depth = 0; i = start; instr = False; esc = False
while i < len(t):
    c = t[i]
    if instr:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': instr = False
    else:
        if c == '"': instr = True
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
    i += 1
obj = json.loads(t[start:i+1])

for sec in obj["secs"]:
    print("=" * 72)
    print(f"SEC {sec['no']}  {sec['name']}")
    for arr, lab in (("w", "W"), ("s", "S"), ("e", "E")):
        if arr in sec:
            print(f"  --- {lab} ({len(sec[arr])}) ---")
            for idx, row in enumerate(sec[arr]):
                print(f"    [{idx}] " + " | ".join(str(x) for x in row))
