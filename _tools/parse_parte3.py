# -*- coding: utf-8 -*-
import json, re, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adv.","prnl.","n.","v.","s.m.","s.f.","m.","f."])
def is_pos(t):
    return t in POS or re.match(r'^[a-z]+\.[mf]\.?$', t) is not None

def parse():
    txt = open(os.path.join(BASE, "_tools/parte3_raw.txt"), encoding="utf-8").read()
    lines = txt.split("\n")
    secs = {}
    cur = None; mode = None
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        m = re.match(r'^Secci[oó]n\s+(\d+)\s+(.*)$', s)
        if m:
            cur = int(m.group(1)); secs[cur] = {"name": m.group(2).strip(), "w": [], "s": [], "e": []}
            mode = None; continue
        if s.startswith("终极分类词"): mode = "w"; continue
        if s.startswith("经典实用句"): mode = "s"; continue
        if s.startswith("词汇大拓展"): mode = "e"; continue
        if s.startswith("Parte"): continue
        if cur is None: continue
        if mode == "w":
            toks = s.split()
            if not toks: continue
            cn = toks[0]
            rest = toks[1:]
            pos = ""
            if rest and is_pos(rest[-1]):
                pos = rest[-1]; es = " ".join(rest[:-1])
            else:
                es = " ".join(rest)
            secs[cur]["w"].append((cn, es, pos))
        elif mode == "e":
            toks = s.split()
            if len(toks) < 2: continue
            cn = toks[-1]
            pre = toks[-2]
            pos = pre if is_pos(pre) else ""
            es = " ".join(toks[:-1] if pos else toks[:-1])  # es = all but cn
            if pos:
                es = " ".join(toks[:-2])
            secs[cur]["e"].append((es, cn, pos))
        elif mode == "s":
            if s.startswith("例"):
                body = s[1:].strip()
                # split spanish . from chinese; keep src attribution
                secs[cur]["s"].append(body)
    return secs

secs = parse()
bj = json.load(open(os.path.join(BASE, "data/book.json"), encoding="utf-8"))
bp = [x for x in bj["partes"] if x["no"] == 3][0]
bj_secs = {s["no"]: s for s in bp["secs"]}

total_missing_w = 0
total_missing_e = 0
for no in sorted(secs.keys()):
    w = secs[no]["w"]; e = secs[no]["e"]; s = secs[no]["s"]
    bw = bj_secs[no]["words"]; be = bj_secs[no].get("extra", []); bs = bj_secs[no].get("sents", [])
    wcn = {x["cn"] for x in bw}
    ecn = {x["cn"] for x in be}
    mw = [(cn,es,pos) for (cn,es,pos) in w if cn not in wcn]
    me = [(es,cn,pos) for (es,cn,pos) in e if cn not in ecn]
    total_missing_w += len(mw); total_missing_e += len(me)
    if mw or me:
        print(f"\n=== Sec{no} {secs[no]['name']} : MISSING in book: W{len(mw)} E{len(me)} ===")
        for cn,es,pos in mw:
            print(f"   W  cn={cn!r}  es={es!r}  pos={pos!r}")
        for es,cn,pos in me:
            print(f"   E  cn={cn!r}  es={es!r}  pos={pos!r}")

print("\nTOTAL missing W:", total_missing_w, " E:", total_missing_e)
