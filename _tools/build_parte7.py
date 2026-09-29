# -*- coding: utf-8 -*-
"""Build data/sec/6.js (Parte 7 在邮局 / book gid=6) from _tools/parte7_raw.txt.
- Content authority = 文案 (word/sentence/extra + 词性).
- Reuse book.json clean Spanish + audio where cn matches AND book es == cleaned 文案 es.
- OCR cleaning: mid-word hyphens, '.'->'ñ' only between vowels, stray mid dot.
- typo fix: fartidiar -> fastidiar (E row es typo).
- malformed multi-sense E line normalized: "certificado adj. 挂号的 n.m. 挂号邮件" -> "certificado adj. 挂号的；挂号邮件".
- 词性 kept only where 文案 explicitly marked it (incl. "adj" without period).
- S text kept faithful to 文案 (comigo / missing ¿ preserved) to maximize book audio reuse.
"""
import json, re, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from es_ipa import text_ipa
from pypinyin import pinyin, Style

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 6

POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adj","adv.","adv","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev.","conj.","vi.","vt.","p.p.","n.inv.","s.n.","s.adj.","s.adv.","tr.","intr.","ger.","inf.","part."])
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
    return re.match(r'^Secci[oó]n\s*(\d+)\s+(.*)$', core)

CERT_RE = re.compile(r'certificado\s+adj\.\s+挂号的\s+n\.m\.\s+挂号邮件')

def parse_raw():
    txt = open(os.path.join(BASE, "_tools/parte7_raw.txt"), encoding="utf-8").read()
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
        # normalize malformed multi-sense E line
        s = CERT_RE.sub('certificado  adj.  挂号的；挂号邮件', s)
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
                    i = j
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
    t = re.sub(r'(?<=[aeiouáéíóúAEIOUÁÉÍÓÚ])[.](?=[aeiouáéíóúAEIOUÁÉÍÓÚ])', 'ñ', t)
    t = t.replace("construción","construcción").replace("vidria","vidrio")
    t = re.sub(r'(?<=[\s,;.])[.](?=[a-záéíóúñü])', '', t)
    t = re.sub(r'[.…]+$', '', t).strip()
    return t

ES_TYPO = {"fartidiar":"fastidiar"}   # E-row es typo (讨厌)
def fix_es_typo(t):
    for k,v in ES_TYPO.items():
        t=t.replace(k,v)
    return t

# sentence text kept faithful to 文案 (no typo/¿ fixes) -> maximize book audio reuse
S_SUBS = {}
def fix_s_es(t):
    for k,v in S_SUBS.items():
        t=t.replace(k,v)
    return t

def clean_cn(t):
    if not t: return t
    return t.strip().rstrip('。…').strip()

def norm(s):
    return re.sub(r'[^a-záéíóúñü]', '', (s or "").lower())

# ---------- new audio allocator (continues from true disk max) ----------
def cur_max(folder):
    m=0
    for f in os.listdir(os.path.join(BASE,folder)):
        mm=re.match(r'(\d{5})\.mp3$', f)
        if mm: m=max(m,int(mm.group(1)))
    return m
EXIST_ES=set(); EXIST_ZH=set()
for f in os.listdir(os.path.join(BASE,"audio/es")):
    mm=re.match(r'(\d{5})\.mp3$', f)
    if mm: EXIST_ES.add(int(mm.group(1)))
for f in os.listdir(os.path.join(BASE,"audio/zh")):
    mm=re.match(r'(\d{5})\.mp3$', f)
    if mm: EXIST_ZH.add(int(mm.group(1)))

es_n=cur_max("audio/es")+1; zh_n=cur_max("audio/zh")+1
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
bp=[p for p in bj["partes"] if p.get("name")=="在邮局"][0]
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
        ces=clean_es(raw_es); ces=fix_es_typo(ces)
        b=find_book(cn,bjw)
        if b and norm(b["es"])==norm(ces):
            w_out.append([cn,b["es"],pos,b["ae"],b["az"],b["py"],b["ipa"]])
        else:
            w_out.append(mkrow_missing(cn,ces,pos))
    for (raw_es,raw_cn,raw_pos) in rs["e"]:
        cn=clean_cn(raw_cn); pos=norm_pos(raw_pos) if raw_pos else ""
        ces=clean_es(raw_es); ces=fix_es_typo(ces)
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
print("next es=%d zh=%d"%(es_n,zh_n))
