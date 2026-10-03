# -*- coding: utf-8 -*-
"""更新 gid13 人的情绪：核对 pasted 文案 -> data/sec/13.js，并修正不符合西语习惯的表达。

核对范围（以用户本次粘贴的文案为权威，_tools/parte13_raw.txt 即其内容）：
  * 终极分类词 / 词汇大拓展 的 (中文, 西语, 词性) 三元组
  * 经典实用句的 (西语, 中文)
文案里没有标词性的（谨慎地 con cautela / 偏袒 ponerse al lado）保持不标。

修正清单（只改西语文本 + es 音频 + IPA；中文 / zh 音频 / 拼音不动）：
  S  El amor es paciente, cuidadoso; amor ignora odio.
     -> El amor es paciente y cuidadoso; el amor ignora el odio.    (缺冠词；并列形容词用 y)
  S  Tomar un viaje en bicicleta o en coche ...
     -> Ir en bicicleta o en coche ...                              (tomar un viaje 不用于西语骑车/开车)
  S  ... que quiere hacerse amigos contigo.
     -> ... que quiere hacer amistad contigo.                       (hacerse amigos con 非西语搭配)
  S  La busca desesperante y no la encuentra.
     -> Busca deseperadamente... -> Busca desesperadamente y no la encuentra. (busca 非名词；缺变位动词)
  E  友好的 | amigos | adj.  ->  amigable                            (amigos 是名词"朋友"，非形容词)
"""
import json, re, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from es_ipa import text_ipa

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 13
RAW = os.path.join(BASE, "_tools/parte13_raw.txt")
SEC = os.path.join(BASE, "data/sec/%d.js" % GID)

# ---------------------------------------------------------------- 修正表
S_SUBS = [
    # 顺序要紧：每句只替换命中的第一条，despreciará 必须先于 preciar（否则 "apreciar " 里
    # 含 "preciar "，会在替换成自身后 break，despreciará 就永远修不到）
    ("despreciará",               "despreciar"),
    ("es paciente, cuidadoso", "es paciente y cuidadoso"),
    ("amor ignora odio",       "el amor ignora el odio"),
    ("Tomar un viaje en bicicleta", "Ir en bicicleta"),
    ("hacerse amigos contigo", "hacer amistad contigo"),
    ("La busca desesperante",  "Busca desesperadamente"),
]
W_FIX = [("友好的", "amigos", "amigable")]


def norm(s):
    return re.sub(r"[^a-záéíóúñü]", "", (s or "").lower())


# ---------------------------------------------------------------- 全局 es 文本 -> 音频（复用）
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
# 词性标记：v. / v.t. / v.i. / n. / n.m. / n.f. / adj. / adj2. / adv. …
POS_RE = re.compile(r"^(v|n|adj|adv|prep|conj|pron|interj|sust|num)(?:\.[a-z]{1,3})?\.?$", re.I)
POS_TOKENS = {"v.", "v.t.", "v.i.", "v.pron.", "n.", "n.m.", "n.f.", "n.pron.",
              "adj.", "adj2.", "adv.", "prep.", "conj.", "pron.", "interj."}


def dehyphen(s):
    """123 排版折行：cuida-doso -> cuidadoso, bici-cleta -> bicicleta"""
    return re.sub(r"(?<=[^\s])-(?=\s)", "", s)


canon = []          # (kind, sec, cn, es, pos)
mode = None
sec = ""
for line in raw.splitlines():
    s = line.strip()
    if s.startswith("###"):
        sec = re.sub(r"^###\s*Sección\s*\d+\s*", "", s).strip()
        continue
    if s.startswith("**终极分类词**"):
        mode = "W"; continue
    if s.startswith("**经典实用句**"):
        mode = "S"; continue
    if s.startswith("**词汇大拓展**"):
        mode = "E"; continue
    if s.startswith("例"):
        m = re.match(r"^例\s+(.*?)\s+([\u4e00-\u9fff].*)$", s)
        if m:
            canon.append(("S", sec, m.group(2).strip(), dehyphen(m.group(1)).strip(), ""))
        continue
    if not s or mode is None or sec == "":
        continue
    s = dehyphen(s)
    if s.startswith("**"):          # 上一行没换行直接粘上来的小节标题
        mode = {"终极分类词": "W", "经典实用句": "S", "词汇大拓展": "E"}.get(s.strip("*").strip(), mode)
        continue
    parts = s.split()
    if mode == "W":
        # 中文 西语[ 西语…] [词性]
        if len(parts) >= 3 and POS_RE.match(parts[-1]):
            cn, es, pos = parts[0], " ".join(parts[1:-1]), parts[-1]
        else:
            cn, es, pos = parts[0], " ".join(parts[1:]), ""
        canon.append((mode, sec, cn, es, pos))
    elif mode == "E":
        # 西语 词性 中文[ 中文…]
        if len(parts) >= 3 and parts[1].lower() in POS_TOKENS:
            es, pos, cn = parts[0], parts[1], " ".join(parts[2:])
        else:
            es, pos, cn = parts[0], "", " ".join(parts[1:])
        canon.append((mode, sec, cn, es, pos))

# 按 小节 + 类型 分组，顺序一一比对（文案里 赞成/愤怒的 等重名条目靠顺序对齐）
grp = {}
for kind, sec, cn, es, pos in canon:
    grp.setdefault((sec, kind.lower()), []).append((cn, es, pos))

mismatch = []
ok = 0
for (sec, kind), items in grp.items():
    dsec = None
    for s in obj["secs"]:
        if s.get("name") == sec:
            dsec = s; break
    if dsec is None:
        mismatch.append(("NOSEC", kind, sec, "", "")); continue
    rows = dsec.get(kind, [])
    if len(rows) != len(items):
        mismatch.append(("COUNT", kind, sec, "文案=%d 数据=%d" % (len(items), len(rows)), ""))
    for (cn, es, pos), r in zip(items, rows):
        have_es = r[0] if kind == "s" else r[1]
        if norm(have_es) != norm(es):
            mismatch.append(("ES", kind, sec, cn, "文案=%s | 数据=%s" % (es, have_es))); continue
        if kind != "s" and r[2] != pos:
            mismatch.append(("POS", kind, sec, cn, "文案=%r | 数据=%r" % (pos, r[2]))); continue
        if kind == "s" and norm(r[1]) != norm(cn):
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
        done = []          # 本行本次已替换出的新串，用于幂等；不能用 "new not in r[0]"
        # （despreciará 本身包含 despreciar，子串判断会把修正挡掉）
        for old, new in S_SUBS:
            if old in r[0] and new not in done:
                old_path = r[3]
                r[0] = r[0].replace(old, new)
                r[6] = text_ipa(r[0])
                r[3], how = assign(r[0])
                done.append(new)
                changed.append(("S", s["name"], r[1][:14], old_path, r[0], r[3], how))
    for r in s.get("e", []):
        for cn, old_es, new_es in W_FIX:
            if norm(r[0]) == norm(cn) and norm(r[1]) == norm(old_es):
                old_path = r[3]
                r[1] = new_es
                r[6] = text_ipa(new_es)
                r[3], how = assign(new_es)
                changed.append(("E", s["name"], cn, old_path, new_es, r[3], how))
                break

save(prefix, obj)

print("\n=== 应用 %d 处修正 ===" % len(changed))
for c in changed:
    print("  [%s/%s] %s\n      old: %r\n      new: %r  -> %s (%s)" % (c[0], c[1], c[2], c[3], c[4], c[5], c[6]))
print("下一个可用 es 号:", es_n)
