import json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = open(os.path.join(BASE, "data/sec/1.js"), encoding="utf-8").read()
i = t.index("={") + 1; d = 0; j = i; s = False; e = False
while j < len(t):
    c = t[j]
    if s:
        if e: e = False
        elif c == "\\": e = True
        elif c == '"': s = False
    else:
        if c == '"': s = True
        elif c == "{": d += 1
        elif c == "}":
            d -= 1
            if d == 0: break
    j += 1
o = json.loads(t[i:j+1])
s4 = [x for x in o["secs"] if x["no"] == 4][0]
print("SEC4 S[2]:", s4["s"][2])
s3 = [x for x in o["secs"] if x["no"] == 3][0]
print("SEC3 W[1..5]:")
for r in s3["w"][1:6]: print("  ", r[0], "|", r[1], "|", r[3], r[4])
s12 = [x for x in o["secs"] if x["no"] == 12][0]
print("SEC12 W[5..7]:")
for r in s12["w"][5:8]: print("  ", r[0], "|", r[1], "|", r[3], r[4])
# scan corruption check across all new entries
bad = []
for sec in o["secs"]:
    for arr in ("w", "s", "e"):
        for r in sec.get(arr, []):
            zh = r[0] or ""
            es = r[1] or ""
            # detect leftover scan artifacts
            if any(a in es for a in ["ba.o", "tama.o", "pa.uelo", "dise.o", "sue.o", "mos-taza", "mos ta", ".o "]) or "EI " in es:
                bad.append((sec["no"], arr, es))
            if "mini" in zh or "  mini" in zh:
                bad.append((sec["no"], arr, zh))
print("\nScan-artifact suspects:", bad)
