# -*- coding: utf-8 -*-
"""Surgical 词性 recalibration for Parte 1 (时间, gid 0) and Parte 2 (衣, gid 1).
- Source of truth for 词性 = pasted 文案 (parte1_raw.txt / parte2_raw.txt).
- Only the pos field (row[2] for W/E) is changed; audio + cn + es + py + ipa preserved.
- Match existing rows to 文案 by normalized Spanish. Unmatched rows keep their existing pos (reported).
"""
import json, re, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adv.","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev.","conj.","vi.","vt.","p.p.","n.inv.","s.n.","s.adj.","s.adv.","tr.","intr.","ger.","inf.","part."])
def is_pos(t):
    if t in POS: return True
    # only the short grammatical abbreviations X.m. / X.f. (NOT OCR dots like oto.o)
    if re.match(r'^[a-z]{1,3}\.[mf]\.?$', t): return True
    return False
def norm(s):
    return re.sub(r'[^a-záéíóúñü]', '', (s or "").lower())
def cn_norm(s):
    # Chinese term key: keep CJK + latin + digits, drop punctuation/spaces so
    # '成功，成就；结果' == '成功成就结果' etc.
    return re.sub(r'[^\w一-鿿]', '', (s or ""))
def clean_es(t):
    if not t: return t
    t = re.sub(r'(?<=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])-(?=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])', '', t)
    t = re.sub(r'(?<=[aeiouáéíóúAEIOUÁÉÍÓÚ])[.](?=[aeiouáéíóúAEIOUÁÉÍÓÚ])', 'ñ', t)
    t = re.sub(r'[.…]+$', '', t).strip()
    return t

def parse_we_line(s):
    s = s.strip()
    if not s: return None
    if '一'<=s[0]<='鿿':
        # Chinese-first: cn = leading CJK run, rest = Spanish + trailing pos
        k=0
        while k<len(s) and _is_cjk(s[k]): k+=1
        cn=s[:k].strip(PUNCT+" ")
        rest=s[k:].strip()
    else:
        # Spanish-first: cn = trailing CJK run, rest = everything before it
        last=-1
        for i,ch in enumerate(s):
            if _is_cjk(ch): last=i
        if last<0:
            return None
        j=last
        while j>=0 and _is_cjk(s[j]): j-=1
        cn=s[j+1:].strip(PUNCT+" ")
        rest=s[:j+1].strip()
    toks = rest.split()
    pos_toks=[]; i=len(toks)-1
    while i>=0 and (is_pos(toks[i]) or toks[i] in ('&',',','y')):
        pos_toks.insert(0, toks[i]); i-=1
    es = " ".join(toks[:i+1])
    pos = " ".join(pos_toks)
    if es=="":
        mm=re.search(r'([A-Za-záéíóúñüÁÉÍÓÚÑÜ]+)$', cn)
        if mm:
            es=mm.group(1); cn=cn[:mm.start()].strip(PUNCT+" ")
    return cn, es, pos

CJK = "一-鿿"
PUNCT = "，、，。·；;：:（）()…—-"
def _is_cjk(ch):
    return ('一'<=ch<='鿿') or ch in PUNCT

def parse_raw(path):
    txt = open(path, encoding="utf-8").read()
    w=[]; e=[]; cur=None; mode=None
    for ln in txt.split("\n"):
        s=ln.strip()
        if not s: continue
        m=re.match(r'^Secci[oó]n\s+(\d+)\s+(.*)$', s)
        if m:
            cur=int(m.group(1)); mode=None; continue
        if s.startswith("终极分类词"): mode="w"; continue
        if s.startswith("经典实用句"): mode="s"; continue
        if s.startswith("词汇大拓展"): mode="e"; continue
        if s.startswith("Parte"): continue
        if cur is None: continue
        if mode in ("w","e"):
            r=parse_we_line(s)
            if not r: continue
            cn,es,pos=r
            es=clean_es(es)
            if mode=="w": w.append((cn,es,pos))
            else: e.append((cn,es,pos))
    return w,e

def build_lookup(w,e):
    lut={}
    cn_lut={}
    for cn,es,pos in (w+e):
        k=norm(es)
        if k:
            if k in lut:
                if not lut[k] and pos: lut[k]=pos
            else:
                lut[k]=pos
        ck=cn_norm(cn)
        if ck:
            # cn-key fallback (handles book/existing es synonyms; 文案 pos wins, blank if unmarked)
            if ck in cn_lut:
                if not cn_lut[ck] and pos: cn_lut[ck]=pos
            else:
                cn_lut[ck]=pos
    return lut, cn_lut

def load_sec(gid):
    p=os.path.join(BASE,"data/sec/%d.js"%gid)
    s=open(p,encoding="utf-8").read()
    eq=s.index("window.BOOK_DATA[%d]="%gid)
    obj=s[eq+len("window.BOOK_DATA[%d]="%gid):].strip()
    if obj.endswith(";"): obj=obj[:-1]
    data=json.loads(obj)
    return s, data

def recalibrate(gid, raw_path):
    w,e=parse_raw(raw_path)
    lut,cn_lut=build_lookup(w,e)
    src,data=load_sec(gid)
    matched=unmatched=n_w=n_e=0
    blank_after=nonblank_after=0
    unmatched_es=[]
    for sec in data["secs"]:
        for mode in ("w","e"):
            for row in sec.get(mode,[]):
                es=row[1] if len(row)>1 else ""
                k=norm(es)
                if k in lut:
                    newpos=lut[k]
                    if row[2]!=newpos:
                        row[2]=newpos
                    matched+=1
                else:
                    # fallback: match by Chinese term (handles differing Spanish synonyms)
                    ck=cn_norm(row[0]) if len(row)>0 else ""
                    if ck in cn_lut:
                        newpos=cn_lut[ck]
                        if row[2]!=newpos:
                            row[2]=newpos
                        matched+=1
                    else:
                        # not in 文案 at all (book extra) -> blank pos per "没有的就不标词性"
                        if row[2]!="":
                            row[2]=""
                        unmatched+=1
                        if k not in [u[0] for u in unmatched_es]:
                            unmatched_es.append((k, es, row[0] if len(row)>0 else ""))
                if len(row)>2:
                    if row[2].strip(): nonblank_after+=1
                    else: blank_after+=1
                if mode=="w": n_w+=1
                else: n_e+=1
    out='window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]='%gid + json.dumps(data, ensure_ascii=False, separators=(",",":")) + ";"
    open(os.path.join(BASE,"data/sec/%d.js"%gid),"w",encoding="utf-8").write(out)
    print("=== gid %d (%s) ==="%(gid, raw_path.split('/')[-1]))
    print("  W rows=%d E rows=%d ; matched=%d unmatched=%d"%(n_w, n_e, matched, unmatched))
    print("  pos after: blank=%d nonblank=%d"%(blank_after, nonblank_after))
    print("  UNMATCHED es (showing up to 40):")
    for k,es,cn in unmatched_es[:40]:
        print("    es=%r cn=%r"%(es, cn))
    print()

for gid,raw in ((0,"_tools/parte1_raw.txt"),(1,"_tools/parte2_raw.txt")):
    recalibrate(gid, os.path.join(BASE,raw))
print("DONE")
