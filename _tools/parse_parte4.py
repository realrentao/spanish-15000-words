# -*- coding: utf-8 -*-
import json, re, os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adv.","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev."])
def is_pos(t):
    return t in POS or re.match(r'^[a-z]+\.[mf]\.?$', t) is not None

def parse():
    txt = open(os.path.join(BASE, "_tools/parte4_raw.txt"), encoding="utf-8").read()
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
            cn = toks[0]; rest = toks[1:]
            pos = ""
            if rest and is_pos(rest[-1]):
                pos = rest[-1]; es = " ".join(rest[:-1])
            else:
                es = " ".join(rest)
            # peel Latin run stuck to cn when es empty
            if es == "":
                mm = re.search(r'([A-Za-záéíóúñüÁÉÍÓÚÑÜ]+)$', cn)
                if mm:
                    es = mm.group(1); cn = cn[:mm.start()]
            secs[cur]["w"].append((cn, es, pos))
        elif mode == "e":
            if s.startswith("DNI"):
                secs[cur]["e"].append(("DNI","身份证（西班牙）","abrev.")); continue
            toks = s.split()
            if len(toks) < 2: continue
            cn = toks[-1]; pre = toks[-2]
            if is_pos(pre):
                pos = pre; es = " ".join(toks[:-2])
            else:
                pos = ""; es = " ".join(toks[:-1])
            secs[cur]["e"].append((es, cn, pos))
        elif mode == "s":
            if s.startswith("例"):
                secs[cur]["s"].append(s[1:].strip())
    return secs

secs = parse()
bj = json.load(open(os.path.join(BASE, "data/book.json"), encoding="utf-8"))
# locate 住: flat partes index 3 (grupo 基本生活, no=4) — verify by name
bp = None
for i,p in enumerate(bj["partes"]):
    if p.get("name")=="住":
        bp = p; bp_index=i; break
print("住 parte: index=%s no=%s secs=%d"%(bp_index, bp.get("no"), len(bp["secs"])))
bj_secs = {s["no"]: s for s in bp["secs"]}

# align section names
print("\n=== Section name alignment (文案 vs book) ===")
for no in sorted(secs.keys()):
    bn = bj_secs.get(no,{}).get("name") if no in bj_secs else "MISSING"
    print("  Sec%-2d 文案=%-12s book=%s"%(no, secs[no]["name"], bn))

total_missing_w=0; total_missing_e=0
print("\n=== W/E MISSING in book (need new audio) + book-es for present ===")
for no in sorted(secs.keys()):
    w=secs[no]["w"]; e=secs[no]["e"]
    bw=bj_secs[no]["words"]; be=bj_secs[no].get("extra",[])
    wcn={x["cn"] for x in bw}; ecn={x["cn"] for x in be}
    mw=[(cn,es,pos) for (cn,es,pos) in w if cn not in wcn]
    me=[(es,cn,pos) for (es,cn,pos) in e if cn not in ecn]
    total_missing_w+=len(mw); total_missing_e+=len(me)
    if mw or me:
        print("\n--- Sec%d %s : Wmissing=%d Emissing=%d ---"%(no,secs[no]["name"],len(mw),len(me)))
        for cn,es,pos in mw:
            print("   W  cn=%-20r 文案es=%-30r pos=%r"%(cn,es,pos))
        for es,cn,pos in me:
            print("   E  cn=%-20r 文案es=%-30r pos=%r"%(cn,es,pos))
    # also dump present W where book-es differs from 文案-es (potential OCR in book)
    for cn,es,pos in w:
        if cn in wcn:
            b=[x for x in bw if x["cn"]==cn][0]
            if b["es"]!=es:
                print("   [diff] Sec%d W cn=%-18r 文案es=%-28r BOOKes=%r"%(no,cn,es,b["es"]))

print("\nTOTAL missing W=%d E=%d"%(total_missing_w,total_missing_e))

# S comparison
print("\n=== S sentence counts (文案 vs book) ===")
tot_s_txt=0; tot_s_book=0
for no in sorted(secs.keys()):
    st=len(secs[no]["s"]); sb=len(bj_secs[no].get("sents",[]))
    tot_s_txt+=st; tot_s_book+=sb
    if st!=sb:
        print("   Sec%-2d 文案S=%d bookS=%d"%(no,st,sb))
print("TOTAL 文案S=%d bookS=%d"%(tot_s_txt,tot_s_book))
