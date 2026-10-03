# -*- coding: utf-8 -*-
"""更新 gid15 人与人之间的关系：核对 pasted 文案 -> data/sec/15.js，并修正不符合西语习惯的表达。

文案存档 = _tools/parte15_raw.txt（与用户本次粘贴一致）。
核对：终极分类词 / 词汇大拓展 的 (中文, 西语, 词性)；经典实用句的 (西语, 中文)。
文案没标词性的保持不标（词性铁律）。

修正清单（只改西语文本 + es 音频 + IPA；中文 / zh 音频 / 拼音不动）：
  S1-4  Mi madre está telefoneando a mi padre
        -> Mi madre está hablando por teléfono con mi padre   (telefonear 生僻且不搭「和我爸打电话」)
  S2-1  ... en 1985 en el cual describe su tiempo pasado en Vietnam, Fue un gran éxito.
        -> ... en 1985; en él describe el tiempo que pasó en Vietnam. Fue un gran éxito.
                                                               (en el cual 悬垂；tiempo pasado 为法语直译；逗号连句)
  S2-3  sino mirar en la misma dirección
        -> sino mirar juntos hacia la misma dirección          (圣埃克苏佩里原句缺 juntos/hacia)
  S2-4  pero solo a tu lado
        -> pero sólo a tu lado                                 (solo 作副词「仅仅」必须加重音)
  S3-3  hacia nostros
        -> hacia nosotros                                      (OCR 漏 ñ)
  S4-1  Los casados viven con más escasez
        -> Los casados viven con mayor escasez                 (名词前比较级应用 mayor)

「文案 vs 数据」保留不回退的 4 处（按上一轮修正规则，西语里文案值不成立/义项不对）：
  亲近的  afecto(文案) -> cercano（afecto 是 n.m.「情感」，不能当 adj.）
  亲属    relación(文案) -> pariente（同节已有「关系 relación」，亲属应为 pariente）
  竞争的  competido(文案) -> competitivo（competido=势均力敌的，非「竞争的」）
  同等地  también(文案) -> igualmente（también=也，非「同等地」）
"""
import json, re, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from es_ipa import text_ipa

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 15
RAW = os.path.join(BASE, "_tools/parte15_raw.txt")
SEC = os.path.join(BASE, "data/sec/%d.js" % GID)

# ---------------------------------------------------------------- 修正表
S_SUBS = [
    ("Mi madre está telefoneando a mi padre",
     "Mi madre está hablando por teléfono con mi padre"),
    ("en 1985 en el cual describe su tiempo pasado en Vietnam, Fue un gran éxito",
     "en 1985; en él describe el tiempo que pasó en Vietnam. Fue un gran éxito"),
    ("sino mirar en la misma dirección",
     "sino mirar juntos hacia la misma dirección"),
    ("pero solo a tu lado", "pero sólo a tu lado"),
    ("hacia nostros", "hacia nosotros"),
    ("viven con más escasez", "viven con mayor escasez"),
]

# ---------------------------------------------------------------- 全局 es 文本 -> 音频（复用）
def norm(s):
    return re.sub(r"[^a-záéíóúñü]", "", (s or "").lower())


es_by_text, taken = {}, set()
for g in range(48):
    fp = os.path.join(BASE, "data/sec/%d.js" % g)
    if not os.path.exists(fp):
        continue
    t = open(fp, encoding="utf-8").read()
    for m in re.finditer(r"es/(\d{5})\.mp3", t):
        taken.add(int(m.group(1)))
    i = t.index("={") + 1
    d = 0; j = i; ins = False; esc = False
    while j < len(t):
        c = t[j]
        if ins:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == "{": d += 1
            elif c == "}":
                d -= 1
                if d == 0: break
        j += 1
    try:
        o = json.loads(t[i:j + 1])
    except Exception:
        continue
    for s in o.get("secs", []):
        for r in s.get("w", []) + s.get("e", []):
            if len(r) == 7 and r[3]:
                es_by_text.setdefault(norm(r[1]), r[3])
        for r in s.get("s", []):
            if len(r) == 7 and r[3]:
                es_by_text.setdefault(norm(r[0]), r[3])


def cur_max(folder):
    m = 0
    for f in os.listdir(os.path.join(BASE, folder)):
        mm = re.match(r"(\d{5})\.mp3$", f)
        if mm:
            m = max(m, int(mm.group(1)))
    return m


es_n = cur_max("audio/es") + 1


def next_es():
    global es_n
    while es_n in taken:
        es_n += 1
    n = es_n; es_n = n + 1; taken.add(n)
    return "es/%05d.mp3" % n


def assign(new_es):
    cand = es_by_text.get(norm(new_es))
    if cand and os.path.exists(os.path.join(BASE, "audio", cand)):
        return cand, "reuse"
    p = next_es()
    es_by_text[norm(new_es)] = p
    return p, "new"


def normcn(s):
    """中文侧归一化：留汉字与字母数字，去所有标点/空格（norm() 会连汉字一起删）。"""
    return re.sub(r"[^\w一-鿿]+", "", (s or "").lower())


# ---------------------------------------------------------------- 读 / 写 sec 文件
def load():
    t = open(SEC, encoding="utf-8").read()
    p = t.index("={")
    prefix = t[:p + 1]
    i = p + 1
    d = 0; j = i; ins = False; esc = False
    while j < len(t):
        c = t[j]
        if ins:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == "{": d += 1
            elif c == "}":
                d -= 1
                if d == 0: break
        j += 1
    return prefix, json.loads(t[i:j + 1])


def save(prefix, obj):
    open(SEC, "w", encoding="utf-8").write(
        prefix + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";")


prefix, obj = load()

# ---------------------------------------------------------------- 1) 文案核对
raw = open(RAW, encoding="utf-8").read()
POS_RE = re.compile(r"^(v|n|adj|adv|prep|conj|pron|interj|sust|num)(?:\.[a-z]{1,3})?\.?$", re.I)
POS_TOKENS = {"v.", "v.t.", "v.i.", "v.pron.", "n.", "n.m.", "n.f.", "n.pron.",
              "adj.", "adj2.", "adv.", "prep.", "conj.", "pron.", "interj."}

# 文案 OCR：把字母中间的「.」还原成正确的带音标点（compa.ero -> compañero …）
OCR_FIX = {"compa.ero": "compañero",
           "acompa.ar": "acompañar",
           "Espa.a": "España",
           "espa.ol": "español"}


def dehyphen(s):
    for k, v in OCR_FIX.items():
        s = s.replace(k, v)
    return re.sub(r"(?<=[^\s])-(?=\s)", "", s)


# 经典实用句：中文里尾部的「——《出处》」在数据中存到 r[2]，比对前先剥掉
FUEX = re.compile(r"\s*[—–-]{2,}\s*《[^》]*》\s*$")


def strip_source(cn):
    return FUEX.sub("", cn).strip()


canon = []
mode = None
sec = ""
for line in raw.splitlines():
    s = line.strip()
    if s.startswith("###"):
        sec = re.sub(r"^###\s*Sección\s*\d+\s*", "", s).strip()
        continue
    if s.startswith("例"):
        m = re.match(r"^例\s+(.*?)\s+([\u4e00-\u9fff].*)$", s)
        if m:
            canon.append(("S", sec, strip_source(m.group(2)), dehyphen(m.group(1)).strip(), ""))
        continue
    if not s or mode is None or sec == "":
        continue
    s = dehyphen(s)
    if s.startswith("**"):
        mode = {"终极分类词": "W", "经典实用句": "S", "词汇大拓展": "E"}.get(s.strip("*").strip(), mode)
        continue
    parts = s.split()
    if mode == "W":
        if len(parts) >= 3 and POS_RE.match(parts[-1]):
            cn, es, pos = parts[0], " ".join(parts[1:-1]), parts[-1]
        else:
            cn, es, pos = parts[0], " ".join(parts[1:]), ""
        canon.append((mode, sec, cn, es, pos))
    elif mode == "E":
        if len(parts) >= 3 and parts[1].lower() in POS_TOKENS:
            es, pos, cn = parts[0], parts[1], " ".join(parts[2:])
        else:
            es, pos, cn = parts[0], "", " ".join(parts[1:])
        canon.append((mode, sec, cn, es, pos))

# 「文案给得不合西语」而保留数据值的条目（不回退）
KEEP = {
    ("亲属关系", "w", "亲属"), ("亲属关系", "w", "亲近的"),
    ("恋人与朋友", "w", "同性恋"),
    ("敌人", "w", "竞争的"), ("敌人", "w", "同等地"),
}

mismatch = []
ok = 0
for kind, sec, cn, es, pos in canon:
    dsec = None
    for s in obj["secs"]:
        if s.get("name") == sec:
            dsec = s; break
    if dsec is None:
        mismatch.append(("NOSEC", kind, sec, cn, es)); continue
    rows = dsec.get(kind.lower(), [])
    r = None
    if kind == "S":
        for x in rows:
            if normcn(x[1]) == normcn(cn):
                r = x; break
    else:
        for x in rows:
            if normcn(x[0]) == normcn(cn):
                r = x; break
    if r is None:
        mismatch.append(("NOHIT", kind, sec, cn, "文案=%s" % es)); continue
    have_es = r[0] if kind == "S" else r[1]
    if norm(have_es) != norm(es):
        if (sec, kind.lower(), cn) in KEEP:
            continue
        mismatch.append(("ES", kind, sec, cn, "文案=%s | 数据=%s" % (es, have_es))); continue
    if kind != "S" and r[2] != pos:
        mismatch.append(("POS", kind, sec, cn, "文案=%r | 数据=%r" % (pos, r[2]))); continue
    if kind == "S" and normcn(r[1]) != normcn(cn):
        mismatch.append(("CN", kind, sec, cn, "文案=%s | 数据=%s" % (cn, r[1]))); continue
    ok += 1

print("=== 文案核对（%d 条 canonical）===" % len(canon))
for m in mismatch:
    print("  ", m)
print("  完全一致:", ok, "/", len(canon))

# ---------------------------------------------------------------- 2) 应用修正
changed = []
for s in obj["secs"]:
    for r in s.get("s", []):
        for old, new in S_SUBS:
            if old in r[0]:
                old_path = r[3]
                r[0] = r[0].replace(old, new)
                r[6] = text_ipa(r[0])
                r[3], how = assign(r[0])
                changed.append(("S", s["name"], r[1][:14], old_path, r[0], r[3], how))

save(prefix, obj)

print("\n=== 应用 %d 处修正 ===" % len(changed))
for c in changed:
    print("  [%s/%s] %s\n      old: %r\n      new: %r  -> %s (%s)" % (c[0], c[1], c[2], c[3], c[4], c[5], c[6]))
print("下一个可用 es 号:", es_n)
