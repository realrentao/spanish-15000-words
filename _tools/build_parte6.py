# -*- coding: utf-8 -*-
"""Build data/sec/5.js (Parte 6 在医院) from _tools/parte6_raw.txt.
- Content authority = 文案 (word/sentence/extra + 词性).
- Reuse book.json clean Spanish + audio where cn matches AND book es == cleaned 文案 es.
- Correct shared 文案/book errors via ES_FIX; fix garbled S sentence via S_SUBS.
- OCR cleaning: mid-word hyphens, '.'->'ñ' only between vowels, stray mid dot.
- 词性 kept only where 文案 explicitly marked it.
"""
import json, re, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from es_ipa import text_ipa
from pypinyin import pinyin, Style

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 5

POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adv.","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev.","conj.","vi.","vt.","p.p.","n.inv.","s.n.","s.adj.","s.adv.","tr.","intr.","ger.","inf.","part."])
def is_pos(t):
    if t in POS: return True
    if re.match(r'^[a-z]{1,3}\.[mf]\.?$', t): return True
    if re.match(r'^[a-z]+\.pl\.?$', t): return True   # plural abbrev e.g. n.pl.
    if re.match(r'^[a-z]+\.[mf]\.[mf]\.?$', t): return True  # e.g. m.f.
    return False
def norm_pos(t):
    return {"vi.":"v.i.","vt.":"v.t.","conj.":"conj."}.get(t, t)

# ---------- parse 文案 ----------
def _core(s):
    return s.strip().strip('#').strip('*').strip()

def _is_seccore(core):
    return re.match(r'^Secci[oó]n\s+(\d+)\s+(.*)$', core)

def parse_raw():
    txt = open(os.path.join(BASE, "_tools/parte6_raw.txt"), encoding="utf-8").read()
    # light cleanup of any residual OCR garbage tokens
    txt = re.sub(r'<[^>]*>', '', txt)
    txt = txt.replace('\\', '')
    lines = txt.split("\n")
    secs = {}
    cur=None; mode=None
    i=0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i+=1; continue
        core = _core(s)
        m = _is_seccore(core)
        if m:
            cur=int(m.group(1)); secs[cur]={"name":m.group(2).strip(),"w":[],"s":[],"e":[]}
            mode=None; i+=1; continue
        if core.startswith("终极分类词"): mode="w"; i+=1; continue
        if core.startswith("经典实用句"): mode="s"; i+=1; continue
        if core.startswith("词汇大拓展"): mode="e"; i+=1; continue
        if core.startswith("Parte"): i+=1; continue
        if cur is None: i+=1; continue
        if mode=="s":
            if s.startswith("例"):
                body = s[1:].strip()
                peeked = False
                # Some 文案 S lines put the Chinese translation on the NEXT line.
                if not re.search(r'[一-鿿]', body):
                    j=i+1
                    while j < len(lines):
                        nl = lines[j].strip()
                        if not nl:
                            j+=1; continue
                        nc = _core(nl)
                        if nc.startswith(("终极分类词","经典实用句","词汇大拓展")) or _is_seccore(nc) or nc.startswith("Parte") or nl.startswith("例"):
                            break
                        body = body + " " + nl
                        j+=1
                    i = j          # next iteration processes the line j now points at
                    peeked = True
                secs[cur]["s"].append(body)
                if peeked:
                    continue
                i+=1; continue
            else:
                i+=1; continue
        if mode=="w":
            toks=s.split()
            if not toks: i+=1; continue
            if re.search(r'[一-鿿]', toks[0]):
                k=0
                while k<len(toks) and re.search(r'[一-鿿]', toks[k]): k+=1
                cn=" ".join(toks[:k]).strip()
                rest=toks[k:]
                pos_toks=[]; ii=len(rest)-1
                while ii>=0 and (is_pos(rest[ii]) or rest[ii] in ("&",",","y")):
                    pos_toks.insert(0, rest[ii]); ii-=1
                es=" ".join(rest[:ii+1])
                pos=" ".join(pos_toks)
                if es=="":
                    mm=re.search(r'([A-Za-záéíóúñüÁÉÍÓÚÑÜ]+)$', cn)
                    if mm:
                        es=mm.group(1); cn=cn[:mm.start()].strip()
                secs[cur]["w"].append((cn,es,pos))
            else:
                k=len(toks)-1
                while k>=0 and re.search(r'[一-鿿]', toks[k]): k-=1
                cn=" ".join(toks[k+1:]).strip()
                rest=toks[:k+1]
                pos_toks=[]; ii=len(rest)-1
                while ii>=0 and (is_pos(rest[ii]) or rest[ii] in ("&",",","y")):
                    pos_toks.insert(0, rest[ii]); ii-=1
                es=" ".join(rest[:ii+1])
                pos=" ".join(pos_toks)
                secs[cur]["w"].append((cn,es,pos))
        elif mode=="e":
            toks=s.split()
            if not toks: i+=1; continue
            if re.search(r'[一-鿿]', toks[0]):
                k=0
                while k<len(toks) and re.search(r'[一-鿿]', toks[k]): k+=1
                cn=" ".join(toks[:k]).strip()
                rest=toks[k:]
                pos_toks=[]; ii=len(rest)-1
                while ii>=0 and (is_pos(rest[ii]) or rest[ii] in ("&",",","y")):
                    pos_toks.insert(0, rest[ii]); ii-=1
                es=" ".join(rest[:ii+1])
                pos=" ".join(pos_toks)
                secs[cur]["e"].append((es,cn,pos))
            else:
                k=len(toks)-1
                while k>=0 and re.search(r'[一-鿿]', toks[k]): k-=1
                cn=" ".join(toks[k+1:]).strip()
                rest=toks[:k+1]
                pos_toks=[]; ii=len(rest)-1
                while ii>=0 and (is_pos(rest[ii]) or rest[ii] in ("&",",","y")):
                    pos_toks.insert(0, rest[ii]); ii-=1
                es=" ".join(rest[:ii+1])
                pos=" ".join(pos_toks)
                secs[cur]["e"].append((es,cn,pos))
        i+=1
    return secs

# ---------- pinyin ----------
def py(text):
    return " ".join(ch[0] for ch in pinyin(text, style=Style.TONE, heteronym=False, errors="ignore"))

# ---------- OCR / typo cleaning for Spanish ----------
def clean_es(t):
    if not t: return t
    t = re.sub(r'(?<=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])-(?=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])', '', t)
    # '.' used as 'ñ' placeholder ONLY between two vowels (OCR)
    t = re.sub(r'(?<=[aeiouáéíóúAEIOUÁÉÍÓÚ])[.](?=[aeiouáéíóúAEIOUÁÉÍÓÚ])', 'ñ', t)
    t = t.replace("construción","construcción").replace("vidria","vidrio")
    # stray dot after whitespace/comma/semicolon immediately before a lowercase letter (OCR noise)
    t = re.sub(r'(?<=[\s,;.])[.](?=[a-záéíóúñü])', '', t)
    t = re.sub(r'[.…]+$', '', t).strip()
    return t

# sentence typo / grammar fixes
S_SUBS = {
 "añanido":"añadido",
 "carmino":"camino",
 "cobrador a":"cobradora",
 "censor te":"censora te",
 "izquerida":"izquierda",
 "contigente":"contingente",
 "ferrocaril":"ferrocarril",
 " do ":" de ",
 # Parte 6 garbled sentence reconstruction
 "gne uama":"que llama",
 "atenlión":"atención",
}
def fix_s_es(t):
    for k,v in S_SUBS.items():
        t=t.replace(k,v)
    return t

def clean_cn(t):
    if not t: return t
    return t.strip().rstrip('。…').strip()

def norm(s):
    return re.sub(r'[^a-záéíóúñü]', '', (s or "").lower())

# ---------- hand-corrected Spanish for wrong/garbage 文案 es (book shares the error) ----------
ES_FIX = {
 "颌":"mandíbula",                       # 文案/book mordaza (gag) -> jaw = mandíbula
 "脊椎":"vértebra",                       # 文案/book vertebral (adj) -> 脊椎 noun = vértebra
 "不舒服的":"incómodo",                   # 文案/book avergonzado (ashamed) -> uncomfortable = incómodo
 "裤子，长裤":"pantalón",                  # 文案/book pantaloon (OCR) -> pantalón
}

# ---------- new audio allocator ----------
EXIST_ES=set(); EXIST_ZH=set()
for f in os.listdir(os.path.join(BASE,"audio/es")):
    m=re.match(r'(\d{5})\.mp3$', f)
    if m: EXIST_ES.add(int(m.group(1)))
for f in os.listdir(os.path.join(BASE,"audio/zh")):
    m=re.match(r'(\d{5})\.mp3$', f)
    if m: EXIST_ZH.add(int(m.group(1)))

es_n=6693; zh_n=7466
audio_jobs=[]
def next_es():
    global es_n
    while es_n in EXIST_ES: es_n+=1
    p="es/%05d.mp3"%es_n; EXIST_ES.add(es_n); es_n+=1; return p
def next_zh():
    global zh_n
    while zh_n in EXIST_ZH: zh_n+=1
    p="zh/%05d.mp3"%zh_n; EXIST_ZH.add(zh_n); zh_n+=1; return p

def mkrow_missing(cn, es, pos):
    ep=next_es(); zp=next_zh()
    audio_jobs.append((es, ep, cn, zp))
    return [cn, es, pos, ep, zp, py(cn), text_ipa(es)]

# ---------- load book.json parte 行 ----------
bj=json.load(open(os.path.join(BASE,"data/book.json"),encoding="utf-8"))
bp=[p for p in bj["partes"] if p.get("name")=="在医院"][0]
bj_secs={s["no"]:s for s in bp["secs"]}
all_sents=[]
for s in bp["secs"]:
    for t in s.get("sents",[]):
        all_sents.append(t)
sent_by_norm={}
for t in all_sents:
    sent_by_norm.setdefault(norm(t.get("es","")), t)

def find_book(cn, words):
    for w in words:
        if w["cn"]==cn: return w
    for w in words:
        if w["cn"].startswith(cn+" "): return w
    return None

def split_s(body):
    m=re.search(r'[一-鿿]', body)
    if not m: return body.strip(), "", ""
    cj=m.start()
    es_raw=body[:cj].strip().lstrip('.。¿¡·')
    rest=body[cj:]
    si=rest.find("——")
    if si>=0:
        zh=rest[:si].strip(); src=rest[si:]
    else:
        zh=rest.strip(); src=""
    return es_raw, zh, src

# ---------- build ----------
secs=parse_raw()
out_secs=[]
total_w=total_s=total_e=0
for no in sorted(secs.keys()):
    rs=secs[no]
    bjw=bj_secs[no]["words"]; bje=bj_secs[no].get("extra",[]); bjs=bj_secs[no].get("sents",[])
    w_out=[]; e_out=[]; s_out=[]
    for (raw_cn,raw_es,raw_pos) in rs["w"]:
        cn=clean_cn(raw_cn); pos=norm_pos(raw_pos) if raw_pos else ""
        ces=clean_es(raw_es)
        if cn in ES_FIX:
            es=ES_FIX[cn]; b=find_book(cn,bjw)
            if b and norm(b["es"])==norm(es):
                w_out.append([cn,es,pos,b["ae"],b["az"],b["py"],b["ipa"]])
            else:
                w_out.append(mkrow_missing(cn,es,pos))
            continue
        b=find_book(cn,bjw)
        if b and norm(b["es"])==norm(ces):
            w_out.append([cn,b["es"],pos,b["ae"],b["az"],b["py"],b["ipa"]])
        else:
            w_out.append(mkrow_missing(cn,ces,pos))
    for (raw_es,raw_cn,raw_pos) in rs["e"]:
        cn=clean_cn(raw_cn); pos=norm_pos(raw_pos) if raw_pos else ""
        ces=clean_es(raw_es)
        if cn in ES_FIX:
            e2=ES_FIX[cn]; b=find_book(cn,bje)
            if b and norm(b["es"])==norm(e2):
                e_out.append([cn,e2,pos,b["ae"],b["az"],b["py"],b["ipa"]])
            else:
                e_out.append(mkrow_missing(cn,e2,pos))
            continue
        b=find_book(cn,bje)
        if b and norm(b["es"])==norm(ces):
            e_out.append([cn,b["es"],pos,b["ae"],b["az"],b["py"],b["ipa"]])
        else:
            e_out.append(mkrow_missing(cn,ces,pos))
    for raw in rs["s"]:
        es_raw,zh,src=split_s(raw)
        ces=clean_es(es_raw); ces=fix_s_es(ces)
        t=sent_by_norm.get(norm(ces))
        if t:
            s_out.append([ces,zh,src,t.get("ae",""),t.get("az",""),t.get("py",""),t.get("ipa","")])
        else:
            ep=next_es(); zp=next_zh()
            audio_jobs.append((ces,ep,zh,zp))
            s_out.append([ces,zh,src,ep,zp,py(zh),text_ipa(ces)])
    out_secs.append({"no":no,"name":rs["name"],"w":w_out,"s":s_out,"e":e_out})
    total_w+=len(w_out); total_s+=len(s_out); total_e+=len(e_out)

obj={"secs":out_secs}
out='window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]='%GID + json.dumps(obj, ensure_ascii=False, separators=(",",":")) + ";"
open(os.path.join(BASE,"data/sec/%d.js"%GID),"w",encoding="utf-8").write(out)
print("sec/%d.js written. W=%d S=%d E=%d  new audio jobs=%d"%(GID,total_w,total_s,total_e,len(audio_jobs)))
print("totalAll this parte:", total_w+total_s+total_e)

# ---------- manifest merge ----------
mj=os.path.join(BASE,"_tools/audio_manifest.json")
existing=[]
if os.path.exists(mj):
    try: existing=json.load(open(mj,encoding="utf-8")).get("jobs",[])
    except Exception: existing=[]
def add_job(es,esp,zh,zhp):
    key=esp or zhp
    if not key or key in seen: return
    seen.add(key); merged.append({"es":es,"esPath":esp,"zh":zh,"zhPath":zhp})
seen=set(); merged=[]
for j in existing:
    if isinstance(j,dict): add_job(j.get("es"),j.get("esPath"),j.get("zh"),j.get("zhPath"))
    else: add_job(j[0],j[1],j[2],j[3])
for j in audio_jobs:
    add_job(j[0],j[1],j[2],j[3])
json.dump({"jobs":merged}, open(mj,"w",encoding="utf-8"), ensure_ascii=False, indent=0)
print("manifest jobs now:", len(merged))
