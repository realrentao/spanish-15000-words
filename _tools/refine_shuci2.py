# -*- coding: utf-8 -*-
"""精修 数词（2）/ 数词（3）两节：用规范 IPA 重写 w/s/e，删除旧的多余内容。
数词（1）已是正确数据，保持不变。"""
import re, json, os
from pypinyin import pinyin, Style

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC0 = os.path.join(BASE, "data", "sec", "0.js")
AUD  = os.path.join(BASE, "audio")

# ---------- 1. 全局 text -> audio 映射（去重） ----------
es_map, zh_map = {}, {}
for fn in sorted(os.listdir(os.path.join(BASE, "data", "sec"))):
    if not fn.endswith(".js"):
        continue
    with open(os.path.join(BASE, "data", "sec", fn), encoding="utf-8") as f:
        raw = f.read()
    k = raw.index("=", raw.index("window.BOOK_DATA[")) + 1
    i = raw.index("{", k)
    obj = json.loads(raw[i:].rstrip().rstrip(";"))
    for sec in obj.get("secs", []):
        for row in sec.get("w", []):
            es_map.setdefault(row[1], row[3]); zh_map.setdefault(row[0], row[4])
        for row in sec.get("s", []):
            es_map.setdefault(row[0], row[3]); zh_map.setdefault(row[1], row[4])
        for row in sec.get("e", []):
            es_map.setdefault(row[1], row[3]); zh_map.setdefault(row[0], row[4])

# ---------- 2. 下一个可用 audio 序号 ----------
def _max(d, sub):
    mx = 0
    for f in os.listdir(os.path.join(AUD, sub)):
        if f.endswith(".mp3"):
            try: mx = max(mx, int(f[:-4]))
            except: pass
    return mx
next_es = [_max("es", "es") + 1]
next_zh = [_max("zh", "zh") + 1]
missing_es, missing_zh = [], []

def alloc_es(text):
    if text in es_map:
        return es_map[text]
    while True:
        f = "es/%05d.mp3" % next_es[0]
        if not os.path.exists(os.path.join(AUD, f)):
            break
        next_es[0] += 1
    es_map[text] = f; next_es[0] += 1
    missing_es.append((text, f))
    return f

def alloc_zh(text):
    if text in zh_map:
        return zh_map[text]
    while True:
        f = "zh/%05d.mp3" % next_zh[0]
        if not os.path.exists(os.path.join(AUD, f)):
            break
        next_zh[0] += 1
    zh_map[text] = f; next_zh[0] += 1
    missing_zh.append((text, f))
    return f

PY_RE = re.compile(r"^[a-zāáǎàēéěèīíǐìōóǒòūúǔùüǖǘǚǜ]+$")
def zh_pinyin(zh):
    toks = [t[0] for t in pinyin(zh, style=Style.TONE)]
    return " ".join(t for t in toks if PY_RE.match(t))

def mk_w(zh, es, pos, ipa):
    return [zh, es, pos, alloc_es(es), alloc_zh(zh), zh_pinyin(zh), ipa]
def mk_e(zh, es, pos, ipa):
    return [zh, es, pos, alloc_es(es), alloc_zh(zh), zh_pinyin(zh), ipa]
def mk_s(es, zh, src, ipa):
    return [es, zh, src, alloc_es(es), alloc_zh(zh), zh_pinyin(zh), ipa]

# ---------- 3. 数词（2） 规范数据（IPA 手校，西/拉美双拼仅对 ce/ci/z） ----------
shuci2_w = [
    ("二十六","veintiséis","f.","bejntiˈsejs"),
    ("二十七","veintisiete","f.","bejntiˈsjete"),
    ("二十八","veintiocho","f.","bejntiˈotʃo"),
    ("二十九","veintinueve","f. inv.","bejntiˈnweβe"),
    ("三十","treinta","m.","ˈtɾeinta"),
    ("四十","cuarenta","m.","kwaˈɾenta"),
    ("五十","cincuenta","m.","siŋˈkwenta"),
    ("六十","sesenta","m.","seˈsenta"),
    ("七十","setenta","m.","seˈtenta"),
    ("八十","ochenta","m.","oˈtʃenta"),
    ("九十","noventa","m.","noˈβenta"),
    ("一百","cien","m.","θjen/sjen"),
    ("一千","mil","m.","mil"),
    ("百万","millón","m.","miˈʎon"),
    ("十亿","mil millones","m.","mil miˈʎones"),
    ("第一","primero","m.","pɾiˈmeɾo"),
    ("第二","segundo","m.","seˈɣundo"),
    ("第三","tercero","m.","teɾˈseɾo"),
    ("第四","cuarto","m.","ˈkwaɾto"),
    ("第五","quinto","m.","ˈkinto"),
    ("第六","sexto","m.","ˈseksto"),
    ("第七","séptimo","m.","ˈseptimo"),
    ("第八","octavo","m.","okˈtaβo"),
]
shuci2_s = [
    ("Paul va a organizar treinta y tres conciertos en el mundo.","保罗今年将开三十三场演唱会。","",
     "ˈpaul ba a oɾɣaniˈθaɾ ˈtɾeinta i tɾes koŋˈθjeɾtos en el ˈmundo"),
    ("El ADN humano tiene 3 mil millones de combinaciones de genes.","人类的 DNA 有 30 亿种基因组合。","《英雄》",
     "el a ðe ˈene ˈumano ˈtjene tɾes mil miˈʎones ðe komβinaˈθjones ðe ˈxenes"),
    ("Primera calidad, la credibilidad de la supremacía, es el objetivo de nuestra empresa.","质量第一，信誉至上，是我们的经营宗旨。","",
     "ˈpɾimeɾa kaliˈðað la kɾeðiβiliˈðað ðe la supɾemaˈkia es el oβxetˈiβo ðe ˈnwestɾa emˈpɾesa"),
    ("Hay cien maneras de llegar allí.","有很多办法可以达到目的。","",
     "ai θjen/sjen maˈneɾas ðe ʎeˈɣaɾ aˈʎi"),
]
shuci2_e = [
    ("品种，种类","tipo","n.m.","ˈtipo"),
    ("组合","combinación","n.f.","kombinaˈθjon/kombinaˈsjon"),
    ("质量","calidad","n.f.","kaliˈðað"),
    ("可信性","credibilidad","n.f.","kɾeðiβiliˈðað"),
    ("最高权力","supremacía","n.f.","supɾemaˈkia"),
    ("企业","empresa","n.f.","emˈpɾesa"),
    ("到达","llegar","v.i.","ʎeˈɣaɾ"),
]

# ---------- 4. 数词（3） 规范数据 ----------
shuci3_w = [
    ("第九","noveno","m.","noˈβeno"),
    ("第十","décimo","m.","ˈdeθimo/ˈdesimo"),
    ("第十一","undécimo","m.","unˈðeθimo/unˈðesimo"),
    ("第十二","duodécimo","m.","dwoˈðeθimo/dwoˈðesimo"),
    ("第十三","decimotercero","m.","ðeθimoteɾˈseɾo/desimoteɾˈseɾo"),
    ("第十四","decimocuarto","m.","ðeθimokoˈaɾto/desimokoˈaɾto"),
    ("第十五","decimoquinto","m.","ðeθimokoˈinto/desimokoˈinto"),
    ("第十六","decimosexto","m.","ðeθimoˈseksto/desimoˈseksto"),
    ("第十七","decimoséptimo","m. inv.","ðeθimoˈseptimo/desimoˈseptimo"),
    ("第十八","decimoctavo","m. inv.","ðeθimoˈktaβo/desimoˈktaβo"),
    ("第十九","decimonoveno","m. inv.","ðeθimonoˈβeno/desimonoˈβeno"),
    ("第二十","vigésimo","m.","biˈxesimo"),
    ("第三十","trigésimo","m.","tɾiˈxesimo"),
    ("第四十","cuadragésimo","m.","kwaðɾaˈxesimo"),
    ("第五十","quincuagésimo","m.","kiŋkwaˈxesimo"),
    ("第六十","sexagésimo","m.","seksaˈxesimo"),
    ("第七十","septuagésimo","m. inv.","septwaˈxesimo"),
    ("第八十","octogésimo","m. inv.","oktoˈxesimo"),
    ("第九十","nonagésimo","m. inv.","nonaˈxesimo"),
]
shuci3_s = [
    ("Con tal de que me des una décima parte de la posibilidad, te daremos plena satisfacción.","只要你给我十分之一的机会，我们会给你百分之百的满意。","",
     "kon tal ðe ke me ðes ˈuna ˈðeθima ˈpaɾte ðe la posiβiliˈðað te daˈɾemos ˈplena satisfakˈθjon"),
    ("Es el noveno día, no nos comunicamos.","这是我们不联系的第九天。","",
     "es el noˈβeno ˈdia no nos komunikaˈmos"),
    ("Te lo repito por centésima vez.","我重复多遍了，再向你重复一遍。","",
     "te lo reˈpito poɾ senˈteθima βes"),
    ("El señor Muyl es superrico, este es su undécimo castillo.","弥勒先生超级富有，这是他买的第十一座庄园。","",
     "el seˈɲoɾ muil es supeˈriko ˈeste es su unˈðeθimo kasˈtiʎo"),
    ("Este libro nos explicará el futuro anterior en la vigésima lección.","这本书的第二十课将为我们详细讲解先将来时的用法。","",
     "ˈeste ˈliβɾo nos eksplikaˈɾa el fuˈtuɾo anˈteɾioɾ en la biˈxesima lekˈθjon"),
]
shuci3_e = [
    ("可能性","posibilidad","n.f.","posiβiliˈðað"),
    ("满足，满意","satisfacción","n.f.","satisfakˈθjon/satisfakˈsjon"),
    ("联系","relacionar","v.t.","relaθjoˈnaɾ/relasjoˈnaɾ"),
    ("重复，重述","repetir","v.t.","repetˈiɾ"),
    ("庄园","castillo","n.m.","kasˈtiʎo"),
    ("先前的","anterior","adj.","anˈteɾioɾ"),
]

# ---------- 5. 写回 sec/0.js ----------
with open(SEC0, encoding="utf-8") as f:
    raw = f.read()
k = raw.index("=", raw.index("window.BOOK_DATA[")) + 1
i = raw.index("{", k)
obj = json.loads(raw[i:].rstrip().rstrip(";"))

def build_sec(secs, name, wdata, sdata, edata):
    for sec in secs:
        if sec.get("name") == name:
            sec["w"] = [mk_w(*r) for r in wdata]
            sec["s"] = [mk_s(*r) for r in sdata]
            sec["e"] = [mk_e(*r) for r in edata]
            print("rewrote %s: w=%d s=%d e=%d" % (name, len(sec["w"]), len(sec["s"]), len(sec["e"])))
            return
    raise SystemExit("section not found: " + name)

build_sec(obj["secs"], "数词（2）", shuci2_w, shuci2_s, shuci2_e)
build_sec(obj["secs"], "数词（3）", shuci3_w, shuci3_s, shuci3_e)

with open(SEC0, "w", encoding="utf-8") as f:
    f.write("window.BOOK_DATA[0]=" + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";")

# ---------- 6. 输出待生成音频清单 ----------
plan = {"es": [{"text": t, "file": f} for t, f in missing_es],
        "zh": [{"text": t, "file": f} for t, f in missing_zh]}
with open(os.path.join(BASE, "_tools", "missing_audio.json"), "w", encoding="utf-8") as f:
    json.dump(plan, f, ensure_ascii=False, indent=2)

print("\n新分配 es 音频: %d 个, zh 音频: %d 个" % (len(missing_es), len(missing_zh)))
print("next_es=%d next_zh=%d" % (next_es[0], next_zh[0]))
