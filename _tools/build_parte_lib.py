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

POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adj","adv.","adv","prnl.","n.","v.","s.m.","s.f.","m.","f.","prep.","abrev.","conj.","vi.","vt.","p.p.","n.inv.","s.n.","s.adj.","s.adv.","tr.","intr.","ger.","inf.","part.",
           "v.pr.","v.pr","v.refl.","v.refl","n.pl.","n.pl","pron.","n.m.pl.","n.f.pl.","n.m.pl","n.f.pl"])
HEAD_WORDS = ("终极分类词", "经典实用句", "词汇大拓展", "Sección", "Seccion", "Parte")
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
    # （**只在「终极分类词 / 词汇大拓展」块做**：「经典实用句」块拆了会把中文句尾的
    #   拉丁字母截掉，例如「…例如que, el uno。」被拆成「…例如」+「que, el uno。」）
    # 「标题关键字粘在正文行里」也要拆开（如 "… n.f.**经典实用句**"），
    # 放在拆行之前用，故这里先编译。
    HEADRE = re.compile(r'(\*\*)?(终极分类词|经典实用句|词汇大拓展)(\*\*)?')
    _HDR2 = re.compile(r'^\s*(?:\*\*\s*)?(终极分类词|经典实用句|词汇大拓展)(?:\*\*\s*)?$')
    _SEC2 = re.compile(r'^\s*Secci[oó]n\s*\d+\b')
    _MD = {"终极分类词": "w", "经典实用句": "s", "词汇大拓展": "e"}
    # 切成块：每块 = (正文行, 该块所属模式)。模式取「开启本块的那个标题」，
    # Sección 行会关掉当前块并把模式清空（否则上一个小节的模式会一路串到下一个
    # 「终极分类词」上，导致整节被当成 S 块丢弃）。
    # ⚠️ 关键：`_hdr` 存的是**归一化模式**（'w'/'s'/'e'），不是中文标题词。
    #    append 时必须直接存 _hdr；写成 _MD.get(_hdr) 会拿 'w' 去查以中文为键的 _MD，
    #    恒返回 None，导致每一行都判不出块模式、整节词条全部丢失（曾白屏）。
    _blocks=[]; _cur=[]; _hdr=None
    for _ln in txt.split("\n"):
        _m2=_HDR2.match(_ln)
        if _m2:
            _blocks.append((_cur,_hdr)); _cur=[]; _hdr=_MD.get(_m2.group(1))
        elif _SEC2.match(_ln):
            _blocks.append((_cur,_hdr)); _cur=[_ln]; _hdr=None
        else:
            _cur.append(_ln)
    _blocks.append((_cur,_hdr))
    # 行流：每行都带上自己的块模式（「经典实用句」块不做 CJK+latin 拆行，
    # 否则会截掉中文句尾的拉丁字母）
    _seq=[]
    for _body,_md in _blocks:
        for _ln in _body:
            _t = _ln if _md=="s" else re.sub(r'([一-鿿])([A-Za-z])', r'\1\n\2', _ln)
            for _x in _t.split("\n"):
                _seq.append((_x,_md))
    # 把粘在正文行里的标题关键字拆开，使 mode 判定 + 行文解析正确。
    # 行流保持「纯文本行 / 该行所属块模式」两路平行数组。
    lines=[]; lmode=[]
    for _ln,_md in _seq:
        mm = HEADRE.search(_ln)
        _parts = [(_ln,_md)] if not mm else []
        if mm:
            before = _ln[:mm.start()].strip(); after = _ln[mm.end():].strip()
            if before: _parts.append((before,_md))
            _parts.append((mm.group(0),_md))
            if after: _parts.append((after,_md))
        for _p,_pm in _parts:
            # 必须是二元组：下游主循环用 lines[i][0] / lines[i][1] 取文本与块模式
            lines.append((_p, _pm)); lmode.append(_pm)
    # 孤儿中文行合并：某些书里「西语 词性」与它的中文释文被 OCR 拆成两行
    # （如 "recientemente adv." + "最近，最新"）。这里把紧跟其后的纯中文行并回上一行。
    merged = []
    for idx, ln in enumerate(lines):
        s = ln[0].strip()
        # 「西语 词性」行 + 紧跟其后的纯中文释文行 -> 并回同一行
        # （条件写反过：原版判断「当前行不含汉字」，导致这条永远不生效）
        if (s and re.search(r"[一-鿿]", s)
                and merged
                and not re.search(r"[一-鿿]", merged[-1][0])
                and merged[-1][0].strip()
                and not any(merged[-1][0].strip().startswith(h) for h in HEAD_WORDS)
                and not any(s.startswith(h) for h in HEAD_WORDS)):
            merged[-1] = (merged[-1][0].rstrip() + " " + s, merged[-1][1])
            continue
        merged.append(ln)
    lines = merged
    secs = {}
    cur=None; mode=None
    i=0
    while i < len(lines):
        mode = lines[i][1]
        s = lines[i][0].strip()
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
                    lines[i] = (rest.lstrip('*').strip(), lines[i][1])
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
                        nl = lines[j][0].strip()
                        if not nl:
                            j+=1; continue
                        nc = _core(nl)
                        if nc.startswith(("终极分类词","经典实用句","词汇大拓展")) or _is_seccore(nc) or nc.startswith("Parte") or nl.startswith("例"):
                            break
                        body = body + " " + nl
                        j+=1
                    i = j
                    peeked = True
                # run-on: one line may carry several "例" -> split into separate S entries.
                # 只按「空白 + 例 + 西语字母」切，避免中文里的「破例」被当成例句分隔符。
                parts=[p.strip() for p in re.split(r"\s*例\s*(?=[A-Za-zÁÉÍÓÚÑÜáéíóúñü])", body) if p.strip()]
                for p in parts:
                    secs[cur]["s"].append(p)
                if peeked:
                    continue
                i+=1; continue
            else:
                i+=1; continue
        if mode in ("w","e") and "|" in s:
            # 「中文|西语 [词性]」写法（文案里「中文 西语」无词性时手动加竖线，
            # 否则 parse_raw 的 CJK+latin 拆行会把中文词头孤立成一行）
            a,_,bb = s.partition("|")
            a=a.strip(); bb=bb.strip()
            if a and re.search(r"[一-鿿]", a) and bb and not re.search(r"[一-鿿]", bb):
                tt=bb.split(); pt=[]; ii=len(tt)-1
                while ii>=0 and (is_pos(tt[ii]) or tt[ii] in ("&",",","y")):
                    pt.insert(0, tt[ii]); ii-=1
                ce=" ".join(tt[:ii+1]); po=" ".join(pt)
                secs[cur][mode].append((a,ce,po))
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
            # 中文起点 = 第一个含汉字的 token（中文里可能夹全角标点/分号，
            # 从后往前数会把 "filosofía n.f. 哲学；哲理" 误切成 es="filosofía n.f. 哲学；"）
            ke=None
            for _idx, _t in enumerate(toks):
                if re.search(r'[一-鿿]', _t): ke=_idx; break
            if ke is None:
                i+=1; continue
            cn=" ".join(toks[ke:]).strip()
            rest=toks[:ke]
            if ke==0:
                es=toks[0]; pos=""
            else:
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

def clean_es(t, keep_end=False):
    """keep_end=True: 保留末尾的「。」（例句用，clean_es 默认会把尾点吃掉）。"""
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
    if not keep_end:
        t = re.sub(r'[.…]+$', '', t)
    return t.strip()

def clean_cn(t):
    if not t: return t
    return t.strip().rstrip('。…').strip()

def norm(s):
    return re.sub(r'[^a-záéíóúñü]', '', (s or "").lower())

class Builder:
    def __init__(self, gid, bp_name, raw_file, ES_FIX=None, ES_TYPO=None, S_SUBS=None,
                 POS_FIX=None, CN_FIX=None, S_ZH_SUBS=None):
        self.gid=gid; self.bp_name=bp_name; self.raw_file=raw_file
        self.ES_FIX=ES_FIX or {}; self.ES_TYPO=ES_TYPO or {}; self.S_SUBS=S_SUBS or {}
        self.POS_FIX=POS_FIX or {}; self.CN_FIX=CN_FIX or {}; self.S_ZH_SUBS=S_ZH_SUBS or []
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
        cand=[p for p in bj["partes"] if p.get("name")==bp_name]
        if not cand:
            cand=[p for p in bj["partes"] if p.get("gid")==gid]
        self.bp=cand[0]
        self.bj_secs={s["no"]:s for s in self.bp["secs"]}
        self.sent_by_norm={}
        for s in self.bp["secs"]:
            for t2 in s.get("sents",[]):
                self.sent_by_norm.setdefault(norm(t2.get("es","")), t2)
        self.GES = self._load_global_audio()   # norm(es) -> (ae, az)

    def _load_global_audio(self):
        """全站「同一西语文本 -> 已有 es/zh 音频」索引，命中即复用（不再新录）。"""
        m={}
        for i2 in range(48):
            fp=os.path.join(BASE,"data/sec/%d.js"%i2)
            if not os.path.exists(fp): continue
            t2=open(fp,encoding="utf-8").read()
            i3=t2.index("={")+1
            d=0;j=i3;ins=False;esc=False
            while j<len(t2):
                c=t2[j]
                if ins:
                    if esc: esc=False
                    elif c=="\\": esc=True
                    elif c=='"': ins=False
                else:
                    if c=='"': ins=True
                    elif c=="{": d+=1
                    elif c=="}":
                        d-=1
                        if d==0: break
                j+=1
            try:
                o=json.loads(t2[i3:j+1])
            except Exception:
                continue
            for s in o.get("secs",[]):
                for r in s.get("w",[])+s.get("e",[]):
                    if len(r)>=7 and r[3] and r[4]:
                        m.setdefault(norm(r[1]), (r[3],r[4]))
                for r in s.get("s",[]):
                    if len(r)>=7 and r[3] and r[4]:
                        m.setdefault(norm(r[0]), (r[3],r[4]))
        return m

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
        for k,v in self.S_SUBS:
            t=t.replace(k,v)
        t=t.strip()
        # split_s 会把 ¿/¡ 当开头标点点掉，这里按句尾问号/叹号补回来；
        # 句中已含 ¿/¡ 就不补（否则 "¡…¡de la mano!" 会变成 "¡¡En los próximos…"）
        if t.endswith("?") and "¿" not in t:
            t = "¿" + t.lstrip("¿¡ ")
        if t.endswith("!") and "¡" not in t:
            t = "¡" + t.lstrip("¿¡ ")
        return t
    def find_book(self, cn, ces, words):
        for w in words:
            if w["cn"]==cn and norm(w["es"])==norm(ces): return w
        return None
    CLOSE_Q={"“":"”","«":"»","「":"」","『":"』","‘":"’","‚":"„"}
    def split_s(self, body):
        # 中文左引号/左括号也算「中文起点」，否则西语段会尾随一个孤立引号
        m=re.search(r'[\u4e00-\u9fff\u201c\u2018\u300c\u300e\uff08]', body)
        if not m: return body.strip(), "", ""
        cj=m.start()
        # 引号开头要小心：它可能是西语引语的开始（“西语” 中文），此时中文其实在引号之后
        if m.group(0) in ("“","«","「","『","‘"):
            _ci=body.find(self.CLOSE_Q.get(m.group(0),"”"), cj)
            if _ci>cj:
                _seg=body[cj:_ci+1]
                if len(re.findall(r'[\u4e00-\u9fff]', _seg))*3 < len(_seg):
                    _m3=re.search(r'[\u4e00-\u9fff]', body[_ci:])
                    if _m3: cj=_ci+_m3.start()
        # 只去左端标点（右端必须留 '.'，后面 clean_es(keep_end=True) 才保得住句尾句号）
        es_raw=body[:cj].strip().lstrip('.。¿¡·“「『『『"\'')
        rest=body[cj:]
        si=rest.find("——")
        # 「——」后面只有封闭书名号《…》，或 CJK ≤6 字且不以句号收尾，才算「出处」；
        # 否则（如「…未曾想象的色彩——一种伟大的蜕变的色彩。」）是中文正文的破折号，
        # 被当成出处会把半句话丢进第 3 字段。
        if si>=0:
            _tail=rest[si:]
            _ncjk=len(re.findall(r'[\u4e00-\u9fff]', _tail))
            if "《" in _tail or (_ncjk<=6 and not _tail.rstrip().endswith("。")):
                zh=rest[:si].strip(); src=_tail.strip()
            else:
                zh=rest.strip(); src=""
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
        gp=self.GES.get(norm(ces))
        if gp and os.path.exists(os.path.join(BASE,"audio",gp[0])):
            row=[cn,ces,pos,gp[0],gp[1],py(cn),text_ipa(ces)]
            self.built[key]=list(row)
            return row, "reuse"
        row=self.mkrow_missing(cn,ces,pos)
        self.built[key]=list(row)
        return row, "new"

    def run(self):
        secs=parse_raw(self.raw_file)
        out_secs=[]
        total_w=total_s=total_e=0
        stat={"book":0,"new":0,"dedup":0,"reuse":0,"s_book":0,"s_new":0,"s_reuse":0}
        for no in sorted(secs.keys()):
            rs=secs[no]
            bsec=self.bj_secs.get(no,{})
            bjw=bsec.get("words",[]); bje=bsec.get("extra",[])
            w_out=[]; e_out=[]; s_out=[]
            for (raw_cn,raw_es,raw_pos) in rs["w"]:
                cn=clean_cn(raw_cn); pos=norm_pos(raw_pos) if raw_pos else ""
                if cn in self.CN_FIX: cn=self.CN_FIX[cn]
                ces=clean_es(raw_es); ces=self.fix_es_typo(ces)
                if (cn,ces) in self.ES_FIX: ces=self.ES_FIX[(cn,ces)]
                elif cn in self.ES_FIX: ces=self.ES_FIX[cn]
                pos=self.POS_FIX.get((cn,ces), self.POS_FIX.get(cn, pos))
                row,how=self._row_for(cn,ces,pos,bjw)
                w_out.append(row); stat[how]+=1
            for (raw_es,raw_cn,raw_pos) in rs["e"]:
                cn=clean_cn(raw_cn); pos=norm_pos(raw_pos) if raw_pos else ""
                ces=clean_es(raw_es); ces=self.fix_es_typo(ces)
                if (cn,ces) in self.ES_FIX: ces=self.ES_FIX[(cn,ces)]
                elif cn in self.ES_FIX: ces=self.ES_FIX[cn]
                pos=self.POS_FIX.get((cn,ces), self.POS_FIX.get(cn, pos))
                row,how=self._row_for(cn,ces,pos,bje)
                e_out.append(row); stat[how]+=1
            for raw in rs["s"]:
                es_raw,zh,src=self.split_s(raw)
                for _a,_b in self.S_ZH_SUBS:
                    zh=zh.replace(_a,_b)
                ces=clean_es(es_raw, keep_end=True); ces=self.fix_es_typo(ces); ces=self.fix_s_es(ces)
                t=self.sent_by_norm.get(norm(ces))
                if t:
                    s_out.append([ces,zh,src,t.get("ae",""),t.get("az",""),t.get("py",""),t.get("ipa","")])
                    stat["s_book"]+=1
                else:
                    gp=self.GES.get(norm(ces))
                    if gp and os.path.exists(os.path.join(BASE,"audio",gp[0])):
                        s_out.append([ces,zh,src,gp[0],gp[1],py(zh),text_ipa(ces)])
                        stat["s_reuse"]+=1
                        continue
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
        print("rows: book=%d reuse=%d new=%d dedup=%d | sentences: book=%d reuse=%d new=%d | new audio jobs=%d"%(
            stat["book"],stat["reuse"],stat["new"],stat["dedup"],
            stat["s_book"],stat["s_reuse"],stat["s_new"],len(self.audio_jobs)))
        print("next es=%d zh=%d"%(self._es_n,self._zh_n))
