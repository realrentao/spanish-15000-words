# -*- coding: utf-8 -*-
"""Reconcile data/sec/0.js (Parte 1 时间) with the provided book text.
- Add missing entries (sec1E, sec2W/E, sec3W/E, sec8W, sec9W, sec10W/S)
- Fix corrupted entry sec2[14] "及时地 a"
- Fix display pinyin/ipa for sec10 S0/S1/S3 (earlier text fixes left fields stale)
- Rebuild sec9 W in book order (preserving existing audio paths)
- Compute pinyin (pypinyin) + IPA (es_ipa) for new/edited entries
- Update data/meta.js counts + totals
- Emit _tools/audio_manifest.json for audio generation
"""
import json, os, sys, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "_tools"))
from es_ipa import text_ipa

from pypinyin import pinyin, Style

def py(text):
    syl = pinyin(text, style=Style.TONE, heteronym=False)
    return " ".join(s[0] for s in syl)

# ---- load current sec/0.js ----
path = os.path.join(BASE, "data", "sec", "0.js")
t = open(path, encoding="utf-8").read()
assert t.startswith('window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[0]='), "prefix mismatch"
start = t.index("={") + 1
depth = 0; i = start; instr = False; esc = False
while i < len(t):
    c = t[i]
    if instr:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': instr = False
    else:
        if c == '"': instr = True
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
    i += 1
obj = json.loads(t[start:i+1])
trailing = t[i+1:]

# ---- audio number allocator ----
es_next = 6219
zh_next = 6996
audio_jobs = []  # (es_text, es_path, zh_text, zh_path) for generation

def new_row(zh, es, pos):
    global es_next, zh_next
    ep = "es/%05d.mp3" % es_next; zp = "zh/%05d.mp3" % zh_next
    es_next += 1; zh_next += 1
    audio_jobs.append((es, ep, zh, zp))
    return [zh, es, pos, ep, zp, py(zh), text_ipa(es)]

def new_srow(es, zh, src):
    global es_next, zh_next
    ep = "es/%05d.mp3" % es_next; zp = "zh/%05d.mp3" % zh_next
    es_next += 1; zh_next += 1
    audio_jobs.append((es, ep, zh, zp))
    return [es, zh, src, ep, zp, py(zh), text_ipa(es)]

# helper to find existing audio by (zh,es)
def audio_map(sec, arr):
    m = {}
    for row in sec.get(arr, []):
        if len(row) >= 7:
            m[(row[0], row[1])] = (row[3], row[4], row[5], row[6])
    return m

def row_with_audio(zh, es, pos, amap):
    if (zh, es) in amap:
        ep, zp, old_py, old_ipa = amap[(zh, es)]
        return [zh, es, pos, ep, zp, old_py, old_ipa]   # keep original audio + py/ipa
    return new_row(zh, es, pos)

secs = {s["no"]: s for s in obj["secs"]}

# ================= SEC 1 =================
secs[1]["e"].append(new_row("忙的", "ocupado", "p.p."))

# ================= SEC 2 =================
# fix corrupted [14]: "及时地 a" -> Spanish "a tiempo" (book: 及时地 a tiempo)
w2 = secs[2]["w"]
assert w2[14][0].startswith("及时地"), w2[14]
w2[14][0] = "及时地"
w2[14][1] = "a tiempo"
w2[14][5] = py("及时地")
w2[14][6] = text_ipa("a tiempo")
# regenerate es/00045 -> "a tiempo"; zh/00044 ("及时地") already correct
audio_jobs.append(("a tiempo", "es/00045.mp3", "及时地", "zh/00044.mp3"))
# append 4 missing phrases
for item in [["周末","fin de semana",""], ["两周","dos semanas",""],
             ["永远","para siempre",""], ["一段时间","un período de tiempo",""]]:
    w2.append(new_row(item[0], item[1], item[2]))
# append missing E: dar un paseo
secs[2]["e"].append(new_row("溜达，闲逛", "dar un paseo", "v."))

# ================= SEC 3 =================
w3 = secs[3]["w"]
for item in [["睡觉时间","tiempos de dormir",""], ["在……之前","antes","adv."],
             ["在……之后","después","adv."], ["在……期间","durante","adv."],
             ["每次","cada vez",""]]:
    w3.append(new_row(item[0], item[1], item[2]))
secs[3]["e"].append(new_row("每个，各个", "cada", ""))

# ================= SEC 8 =================
w8 = secs[8]["w"]
for item in [["元旦","Día del Año Nuevo",""], ["春节","Año Nuevo Chino",""],
             ["除夕","la víspera del Año Nuevo Chino",""], ["元宵节","el Festival de los Faroles",""],
             ["植树节","el Día del Arbol",""], ["清明节","el Festival de los Muertos",""],
             ["端午节","el Festival del Bote del Dragón",""], ["中秋节","Festival del Medio Otoño",""],
             ["教师节","Día del Maestro",""], ["国庆节","Día Nacional",""]]:
    w8.append(new_row(item[0], item[1], item[2]))

# ================= SEC 9 (rebuild W in book order) =================
amap9 = audio_map(secs[9], "w")
canon9 = [["守岁","mantenerse en la víspera del Año Nuevo",""],
          ["鞭炮","petardo","n.m."],
          ["放（烟花）","lanzar (fuegos artificiales)",""],
          ["庆祝","celebración","n.f."],
          ["舞龙","danza del dragón",""],
          ["舞狮","danza del león",""],
          ["贴","pegar","v.t."],
          ["谜语","enigma","n.m."],
          ["猜测","adivinar","v.t."],
          ["元宵","refresco del festival de los faroles",""],
          ["红包","bolsa roja",""]]
secs[9]["w"] = [row_with_audio(zh, es, pos, amap9) for (zh, es, pos) in canon9]

# ================= SEC 10 =================
w10 = secs[10]["w"]
for item in [["音乐节","festival de música",""], ["情人节","Día de San Valentín",""],
             ["母亲节","Día de la Madre",""], ["父亲节","Día del Padre",""],
             ["电影节","festival de cine",""],
             ["第一次世界大战结束纪念日","el aniversario de la Primera Guerra Mundial",""],
             ["劳动节","Día Laboral",""]]:
    w10.append(new_row(item[0], item[1], item[2]))
# S4: Pascua y Navidad  (S rows order: [es, zh, src, ep, zp, py(zh), ipa(es)])
secs[10]["s"].append(new_srow(
    "La Pascua y la Navidad son festivales internacionales.",
    "复活节和圣诞节都是国际型节日。", ""))
# Fix stale pinyin/ipa on S0, S1, S3 (S rows: row[0]=es, row[1]=zh)
def fix_s(sec, idx, recompute_ipa):
    row = secs[sec]["s"][idx]
    while len(row) < 7:
        row.append("")
    row[5] = py(row[1])                 # pinyin from Chinese (row[1])
    if recompute_ipa:
        row[6] = text_ipa(row[0])       # ipa from Spanish (row[0])
fix_s(10, 0, False)   # S0: pinyin fix only (ipa already correct)
fix_s(10, 1, True)    # S1: both missing -> recompute
fix_s(10, 3, True)    # S3: pinyin + ipa fix

# ---- write sec/0.js ----
new_sec = 'window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[0]=' + \
          json.dumps(obj, ensure_ascii=False) + trailing
open(path, "w", encoding="utf-8").write(new_sec)
print("sec/0.js written, bytes:", len(new_sec))

# ---- update meta.js ----
mpath = os.path.join(BASE, "data", "meta.js")
mt = open(mpath, encoding="utf-8").read()
mstart = mt.index("={") + 1
depth = 0; i = mstart; instr = False; esc = False
while i < len(mt):
    c = mt[i]
    if instr:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': instr = False
    else:
        if c == '"': instr = True
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
    i += 1
meta = json.loads(mt[mstart:i+1])
mtrail = mt[i+1:]

g0 = meta["grupos"][0]
for s in g0["partes"][0]["secs"]:
    no = s["no"]
    if no in secs:
        sec = secs[no]
        s["w"] = len(sec.get("w", []))
        s["s"] = len(sec.get("s", []))
        s["e"] = len(sec.get("e", []))
# recompute totals
tw = ts = te = 0
for gr in meta["grupos"]:
    for pt in gr["partes"]:
        for sc in pt["secs"]:
            tw += sc.get("w", 0); ts += sc.get("s", 0); te += sc.get("e", 0)
meta["total"] = {"w": tw, "s": ts, "e": te}
meta["totalAll"] = tw + ts + te

new_meta = 'window.BOOK_META=' + json.dumps(meta, ensure_ascii=False) + mtrail
open(mpath, "w", encoding="utf-8").write(new_meta)
print("meta written. total:", meta["total"], "totalAll:", meta["totalAll"])

# ---- write audio manifest ----
manifest = {"jobs": [{"es": a, "esPath": b, "zh": c, "zhPath": d} for (a, b, c, d) in audio_jobs]}
json.dump(manifest, open(os.path.join(BASE, "_tools", "audio_manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("audio jobs:", len(audio_jobs))
