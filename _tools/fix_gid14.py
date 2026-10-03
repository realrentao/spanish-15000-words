# -*- coding: utf-8 -*-
"""更新 gid14 人类交流的方式：核对 pasted 文案 -> data/sec/14.js，并修正不符合西语习惯的表达。

文案存档 = _tools/parte14_raw.txt（与用户本次粘贴一致）。
核对：终极分类词 / 词汇大拓展 的 (中文, 西语, 词性)；经典实用句的 (西语, 中文)。
文案没标词性的保持不标（词性铁律）。

修正清单（只改西语文本 + es 音频 + IPA；中文 / zh 音频 / 拼音不动）：
  S1-4  Cuál es tu número de teléfono?
        -> ¿Cuál es tu número de teléfono?                    (西语问句缺开问号 ¿)
  S1-7  Han dejado algún mensaje para mi?
        -> ¿Han dejado algún mensaje para mí?                 (缺 ¿；mí 重音符号缺失)
  S2-1  Invadí **en** su ordenador de casa
        -> Invadí su ordenador de casa                        (invadir 是及物动词，不带 en)
  S2-2  No sé cómo **reparo** mi ordenador
        -> No sé cómo reparar mi ordenador                    (no sé cómo 后接原形动词)
  W    点击数 | número de clíc  -> número de clics            (clíc 不是西语词，文案被 OCR 截断)
  W    主页   | página          -> página de inicio           (página 单独是"页面"，不等于"主页")
  E    词汇大拓展「mejor」行是被上一次解析器写坏的行：
        cn="的比较级]较好地，更好地" / es="mejor adv. [bien" / pos=""
        -> cn="较好地，更好地" / es="mejor" / pos="adv."
"""
import json, re, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from es_ipa import text_ipa

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 14
RAW = os.path.join(BASE, "_tools/parte14_raw.txt")
SEC = os.path.join(BASE, "data/sec/%d.js" % GID)

# ---------------------------------------------------------------- 修正表
S_SUBS = [
    ("Cuál es tu número de teléfono?", "¿Cuál es tu número de teléfono?"),
    ("Han dejado algún mensaje para mi?", "¿Han dejado algún mensaje para mí?"),
    ("Invadí en su ordenador de casa", "Invadí su ordenador de casa"),
    ("No sé cómo reparo mi ordenador", "No sé cómo reparar mi ordenador"),
]
# (小节名, 中文, 旧西语, 新西语)
W_FIX = [
    ("网站", "点击数", "número de clíc", "número de clics"),
    ("网站", "主页", "página", "página de inicio"),
]
# 被写坏的「mejor」拓展行：(小节名, 坏的中文前缀)
E_REPAIR = [("网站", "的比较级")]


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
POS_RE = re.compile(r"^(v|n|adj|adv|prep|conj|pron|interj|sust|num)(?:\.[a-z]{1,3})?\.?$", re.I)
POS_TOKENS = {"v.", "v.t.", "v.i.", "v.pron.", "n.", "n.m.", "n.f.", "n.pron.",
              "adj.", "adj2.", "adv.", "prep.", "conj.", "pron.", "interj."}


def dehyphen(s):
    return re.sub(r"(?<=[^\s])-(?=\s)", "", s)


canon = []
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
        done = []
        for old, new in S_SUBS:
            if old in r[0] and new not in done:
                old_path = r[3]
                r[0] = r[0].replace(old, new)
                r[6] = text_ipa(r[0])
                r[3], how = assign(r[0])
                done.append(new)
                changed.append(("S", s["name"], r[1][:14], old_path, r[0], r[3], how))
    for r in s.get("w", []):
        for secname, cn, old_es, new_es in W_FIX:
            if s.get("name") == secname and norm(r[0]) == norm(cn) and norm(r[1]) == norm(old_es):
                old_path = r[3]
                r[1] = new_es
                r[6] = text_ipa(new_es)
                r[3], how = assign(new_es)
                changed.append(("W", s["name"], cn, old_path, new_es, r[3], how))
                break
    for r in s.get("e", []):
        for secname, bad in E_REPAIR:
            if s.get("name") == secname and r[0].startswith(bad):
                old = (r[0], r[1], r[2])
                r[0], r[1], r[2] = "较好地，更好地", "mejor", "adv."
                r[6] = text_ipa("mejor")
                r[3], _ = assign("mejor")
                changed.append(("E", s["name"], "mejor 行损坏修复",
                                "cn=%r es=%r pos=%r" % old,
                                "cn=%r es=%r pos=%r" % (r[0], r[1], r[2]), r[3], "reuse"))
                break

save(prefix, obj)

print("\n=== 应用 %d 处修正 ===" % len(changed))
for c in changed:
    print("  [%s/%s] %s\n      old: %r\n      new: %r  -> %s (%s)" % (c[0], c[1], c[2], c[3], c[4], c[5], c[6]))
print("下一个可用 es 号:", es_n)
