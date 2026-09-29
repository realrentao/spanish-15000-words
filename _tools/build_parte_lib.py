# -*- coding: utf-8 -*-
"""Shared engine: rebuild data/sec/<gid>.js from a pasted Parte 文案 (raw txt).
- Content authority = 文案 (words/sentences/extra + 词性 only where 文案 marks it).
- Reuse book.json clean Spanish+audio where cn matches AND book es == cleaned 文案 es.
- Everything else: new audio numbers (edge-tts generated later by the site-wide generator).
- OCR cleaning: mid-word hyphens, '.'->'ñ' only between vowels, stray dots, whitespace,
  space-before-punct cosmetic fix.
- S run-on: a line may contain several "例" -> split into separate S entries.
- Dedup: identical (cn, norm(es)) entries within the build share one audio allocation.
Used by build_parte11.py / build_parte12.py (thin wrappers with per-parte tables).
"""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from es_ipa import text_ipa
from pypinyin import pinyin, Style

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adj","adv.","adv","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev.","conj.","vi.","vt.","p.p.","n.inv.","s.n.","s.adj.","s.adv.","tr.","intr.","ger.","inf.","part."])
def is_pos(t):
    if t in POS: return True
    if re.match(r'^[a-z]{1,3}\.[mf]\.?$', t): return True
    if re.match(r'^[a-z]+\.pl\.?$', t): return True
    if re.match(r'^[a-z]+\.[mf]\.[mf]\.?$', t): return True
    return False
def norm_pos(t):
    return {"vi.":"v.i.","vt.":"v.t.","conj.":"conj."}.get(t, t)

def _core(s):
    return s.strip().strip('#').strip('*').strip()

def _is_seccore(core):
    return re.match(r'^Secci[oó]n\s*(\d+)\s+(.*)$', core)

HEAD_KW = (("终极分类词","w"),("经典实用句","s"),("词汇大拓展","e"))

def parse_raw(raw_file):
    txt = open(os.path.join(BASE, raw_file), encoding="utf-8").read()
    txt = re.sub(r'<[^>]*>', '', txt)
    txt = txt.replace('\\', '')
    # split malformed run-on where a CJK cn is glued to the next entry's latin es
    txt = re.sub(r'([一-鿿])([A-Za-z])', r'\1\n\2', txt)
    lines = txt.split("\n")
    # split a heading keyword glued onto a content line (e.g. a W/E row ending in
    # "... n.f.**经典实用句**", or "**经典实用句**例 ...") into separate lines so mode
    # detection + row parsing work correctly.
    HEADRE = re.compile(r'(\*\*)?(终极分类词|经典实用句|词汇大拓展)(\*\*)?')
    expanded = []
    for ln in lines:
        mm = HEADRE.search(ln)
        if not mm:
            expanded.append(ln); continue
        before = ln[:mm.start()].strip()
        after = ln[mm.end():].strip()
        if before: expanded.append(before)
        expanded.append(mm.group(0))
        if after: expanded.append(after)
    lines = expanded
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
        hit=False
        for kw,md in HEAD_KW:
            if core.startswith(kw):
                rest = core[len(kw):].strip()
                if rest:
                    # heading glued to first 例 on same line -> reprocess remainder
                    lines[i] = rest.lstrip('*').strip()
                    mode = md
                    hit=True
                    break
                else:
                    mode = md
                    i+=1
                    hit=True
                    break
        if hit:
            continue
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
                # run-on: one line may carry several "例" -> split into separate S entries
                parts=[p.strip() for p in body.split("例") if p.strip()]
                for p in parts:
                    secs[cur]["s"].append(p)
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

def py(text):
    return " ".join(ch[0] for ch in pinyin(text, style=Style.TONE, heteronym=False, errors="ignore"))

def clean_es(t):
    if not t: return t
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'([A-Za-zÁÉÍÓÚÑÜáéíóúñü])-([A-Za-zÁÉÍÓÚÑÜáéíóúñü])', r'\1\2', t)
    t = re.sub(r'(?<=[aeiouáéíóúAEIOUÁÉÍÓÚ])[.](?=[aeiouáéíóúAEIOUÁÉÍÓÚ])', 'ñ', t)
    t = t.replace("construción","construcción").replace("vidria","vidrio")
    t = re.sub(r'(?<=[\s,;.])[.](?=[a-záéíóúñü])', '', t)
    t = re.sub(r'(?<=[\s.])\.(?=[A-ZÁÉÍÓÚÑÜ])', '', t)
    # remove a dot wedged between two letters when the two chars before it are both
    # letters (mid-word OCR, e.g. "sis.tema"->"sistema"); the 2-letter-ahead guard
    # keeps abbreviations like "n.pl." (char before the dot is a single letter) intact.
    t = re.sub(r'(?<=[A-Za-zÁÉÍÓÚÑÜáéíóúñü][A-Za-zÁÉÍÓÚÑÜáéíóúñü])[.](?=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])', '', t)
    t = re.sub(r'\s+([,;:!?])', r'\1', t)
    t = re.sub(r'[.…]+$', '', t).strip()
    return t

def clean_cn(t):
    if not t: return t
    return t.strip().rstrip('。…').strip()

def norm(s):
    return re.sub(r'[^a-záéíóúñü]', '', (s or "").lower())

class Builder:
    def __init__(self, gid, bp_name, raw_file, ES_FIX=None, ES_TYPO=None, S_SUBS=None):
        self.gid=gid; self.bp_name=bp_name; self.raw_file=raw_file
        self.ES_FIX=ES_FIX or {}; self.ES_TYPO=ES_TYPO or {}; self.S_SUBS=S_SUBS or {}
        # audio allocator continues from true disk max
        def cur_max(folder):
            m=0
            for f in os.listdir(os.path.join(BASE,folder)):
                mm=re.match(r'(\d{5})\.mp3$', f)
                if mm: m=max(m,int(mm.group(1)))
            return m
        self.EXIST_ES=set(); self.EXIST_ZH=set()
        for f in os.listdir(os.path.join(BASE,"audio/es")):
            mm=re.match(r'(\d{5})\.mp3$', f)
            if mm: self.EXIST_ES.add(int(mm.group(1)))
        for f in os.listdir(os.path.join(BASE,"audio/zh")):
            mm=re.match(r'(\d{5})\.mp3$', f)
            if mm: self.EXIST_ZH.add(int(mm.group(1)))
        # ALSO treat every path referenced by ANY existing sec file as taken:
        # sec files may claim numbers whose audio is not generated yet (batched builds).
        for i2 in range(48):
            fp=os.path.join(BASE,"data/sec/%d.js"%i2)
            if not os.path.exists(fp): continue
            t2=open(fp,encoding="utf-8").read()
            for mm in re.finditer(r'es/(\d{5})\.mp3', t2): self.EXIST_ES.add(int(mm.group(1)))
            for mm in re.finditer(r'zh/(\d{5})\.mp3', t2): self.EXIST_ZH.add(int(mm.group(1)))
        self._es_n=cur_max("audio/es")+1; self._zh_n=cur_max("audio/zh")+1
        while self._es_n in self.EXIST_ES: self._es_n+=1
        while self._zh_n in self.EXIST_ZH: self._zh_n+=1
        self.audio_jobs=[]
        self.built={}   # (cn, norm(es)) -> row (dedup identical entries)
        bj=json.load(open(os.path.join(BASE,"data/book.json"),encoding="utf-8"))
        self.bp=[p for p in bj["partes"] if p.get("name")==bp_name][0]
        self.bj_secs={s["no"]:s for s in self.bp["secs"]}
        self.sent_by_norm={}
        for s in self.bp["secs"]:
            for t2 in s.get("sents",[]):
                self.sent_by_norm.setdefault(norm(t2.get("es","")), t2)

    def _next_es(self):
        n=self._es_n
        while n in self.EXIST_ES: n+=1
        self._es_n=n+1; self.EXIST_ES.add(n)
        return "es/%05d.mp3"%n
    def _next_zh(self):
        n=self._zh_n
        while n in self.EXIST_ZH: n+=1
        self._zh_n=n+1; self.EXIST_ZH.add(n)
        return "zh/%05d.mp3"%n

    def fix_es_typo(self, t):
        for k,v in self.ES_TYPO.items():
            t=t.replace(k,v)
        return t
    def fix_s_es(self, t):
        for k,v in self.S_SUBS.items():
            t=t.replace(k,v)
        return t
    def find_book(self, cn, ces, words):
        for w in words:
            if w["cn"]==cn and norm(w["es"])==norm(ces): return w
        return None
    def split_s(self, body):
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
    def mkrow_missing(self, cn, es, pos):
        ep=self._next_es(); zp=self._next_zh()
        self.audio_jobs.append((es, ep, cn, zp))
        return [cn, es, pos, ep, zp, py(cn), text_ipa(es)]
    def _row_for(self, cn, ces, pos, book_words):
        key=(cn, norm(ces))
        if key in self.built:
            row=list(self.built[key]); row[2]=pos
            return row, "dedup"
        b=self.find_book(cn,ces,book_words)
        if b:
            ces_b=clean_es(b["es"])   # book es may carry stray hyphen/OCR too -> normalize display
            if ces_b==b["es"]:
                row=[cn,b["es"],pos,b["ae"],b["az"],b["py"],b["ipa"]]
            else:
                row=[cn,ces_b,pos,b["ae"],b["az"],b["py"],text_ipa(ces_b)]
            self.built[key]=list(row)
            return row, "book"
        row=self.mkrow_missing(cn,ces,pos)
        self.built[key]=list(row)
        return row, "new"

    def run(self):
        secs=parse_raw(self.raw_file)
        out_secs=[]
        total_w=total_s=total_e=0
        stat={"book":0,"new":0,"dedup":0,"s_book":0,"s_new":0}
        for no in sorted(secs.keys()):
            rs=secs[no]
            bsec=self.bj_secs.get(no,{})
            bjw=bsec.get("words",[]); bje=bsec.get("extra",[])
            w_out=[]; e_out=[]; s_out=[]
            for (raw_cn,raw_es,raw_pos) in rs["w"]:
                cn=clean_cn(raw_cn); pos=norm_pos(raw_pos) if raw_pos else ""
                ces=clean_es(raw_es); ces=self.fix_es_typo(ces)
                if cn in self.ES_FIX: ces=self.ES_FIX[cn]
                row,how=self._row_for(cn,ces,pos,bjw)
                w_out.append(row); stat[how]+=1
            for (raw_es,raw_cn,raw_pos) in rs["e"]:
                cn=clean_cn(raw_cn); pos=norm_pos(raw_pos) if raw_pos else ""
                ces=clean_es(raw_es); ces=self.fix_es_typo(ces)
                if cn in self.ES_FIX: ces=self.ES_FIX[cn]
                row,how=self._row_for(cn,ces,pos,bje)
                e_out.append(row); stat[how]+=1
            for raw in rs["s"]:
                es_raw,zh,src=self.split_s(raw)
                ces=clean_es(es_raw); ces=self.fix_es_typo(ces); ces=self.fix_s_es(ces)
                t=self.sent_by_norm.get(norm(ces))
                if t:
                    s_out.append([ces,zh,src,t.get("ae",""),t.get("az",""),t.get("py",""),t.get("ipa","")])
                    stat["s_book"]+=1
                else:
                    ep=self._next_es(); zp=self._next_zh()
                    self.audio_jobs.append((ces,ep,zh,zp))
                    s_out.append([ces,zh,src,ep,zp,py(zh),text_ipa(ces)])
                    stat["s_new"]+=1
            out_secs.append({"no":no,"name":rs["name"],"w":w_out,"s":s_out,"e":e_out})
            total_w+=len(w_out); total_s+=len(s_out); total_e+=len(e_out)
            print("sec %-2d %-14s W=%-3d S=%-3d E=%-3d"%(no,rs["name"],len(w_out),len(s_out),len(e_out)))
        obj={"secs":out_secs}
        out='window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]='%self.gid + json.dumps(obj, ensure_ascii=False, separators=(",",":")) + ";"
        open(os.path.join(BASE,"data/sec/%d.js"%self.gid),"w",encoding="utf-8").write(out)
        print("sec/%d.js written. W=%d S=%d E=%d totalAll=%d"%(self.gid,total_w,total_s,total_e,total_w+total_s+total_e))
        print("rows: book-reuse=%d new=%d dedup=%d | sentences: book=%d new=%d | new audio jobs=%d"%(
            stat["book"],stat["new"],stat["dedup"],stat["s_book"],stat["s_new"],len(self.audio_jobs)))
        print("next es=%d zh=%d"%(self._es_n,self._zh_n))
