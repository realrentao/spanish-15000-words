# -*- coding: utf-8 -*-
import json, os, re, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 1

def read_obj(path):
    t = open(path, encoding="utf-8").read()
    p = t.index("={"); start = p + 1
    depth = 0; i = start; instr = False; esc = False
    while i < len(t):
        c = t[i]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': instr = False
        else:
            if c == '"': instr = True
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0: break
        i += 1
    return t[:p+1], json.loads(t[start:i+1]), t[i+1:]

prefix, obj, suffix = read_obj(os.path.join(BASE, f"data/sec/{GID}.js"))
print("PREFIX OK:", prefix.startswith("window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[1]="))
print("SUFFIX:", repr(suffix))

expect = {1:(14,4,4),2:(14,4,6),3:(15,3,7),4:(21,6,6),5:(16,4,4),6:(15,4,8),
          7:(15,3,5),8:(11,4,6),9:(18,4,5),10:(18,4,4),11:(13,3,4),12:(16,3,3),
          13:(15,3,3),14:(15,3,4)}
total_ok = True
for sec in obj["secs"]:
    no = sec["no"]
    w=len(sec.get("w",[])); s=len(sec.get("s",[])); e=len(sec.get("e",[]))
    ok = expect.get(no)==(w,s,e)
    total_ok &= ok
    print(f"SEC{no:2d} w={w:2d} s={s} e={e}  expect={expect.get(no)}  {'OK' if ok else 'MISMATCH'}")

# fixes
def find(secno, zh_sub=None, es_sub=None):
    sec=[x for x in obj["secs"] if x["no"]==secno][0]
    rows=[]
    for arr in ("w","s","e"):
        for r in sec.get(arr,[]):
            if zh_sub and zh_sub in (r[0] or ""): rows.append((arr,r))
            if es_sub and es_sub in (r[1] or ""): rows.append((arr,r))
    return rows

print("\n--- fix checks ---")
print("sec1 时尚的/de moda:", find(1, zh_sub="时尚的"))
print("sec11 迷你短裙/mini falda:", find(11, zh_sub="迷你短裙"))
print("sec4 El violado:", find(4, es_sub="El violado"))
print("sec4 EI (should be gone):", find(4, es_sub="EI violado"))

# manifest
m = json.load(open(os.path.join(BASE,"_tools/audio_manifest.json"),encoding="utf-8"))
jobs = m["jobs"]
real = [j for j in jobs if (j[1] and not os.path.exists(os.path.join(BASE,"audio",j[1]))) or (j[3] and not os.path.exists(os.path.join(BASE,"audio",j[3])))]
print("\nmanifest total jobs:", len(jobs), " still missing on disk:", len(real))
print("TOTAL_OK:", total_ok)
