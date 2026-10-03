# -*- coding: utf-8 -*-
"""Cross-parte corrections on data/sec/<gid>.js for the 11 updated partes (gids 5-15, gid 10 done).
Catches the SAME class of problems the user fixed in gid 10:
- Spanish word whose meaning does not match the Chinese headword (false friend / OCR / wrong sense)
- wrong part-of-speech pairing (verb headword given a noun, etc.)
- broken/Portuguese-contaminated/garbled S sentences
Only the Spanish text + its es audio path + IPA change; cn / zh audio / pinyin stay.
Audio reuse: reuse an existing on-disk audio when some sec file already references the SAME
normalized Spanish text; otherwise allocate a new number (collision-safe across all sec files).
"""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from es_ipa import text_ipa

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (gid, cn, old_es, new_es)
W_FIX = [
    # gid 5 在医院
    (5, "塌鼻", "nariz colapso", "nariz chata"),
    (5, "腰部", "lomos", "cintura"),
    (5, "屁股", "culo", "trasero"),
    (5, "表皮", "cutícula", "epidermis"),
    (5, "住院部", "hospitalización", "sala de hospitalización"),
    (5, "刺痛", "dolor palpitante", "dolor punzante"),
    (5, "耳鸣； 焦躁", "hormigueo", "tinnitus"),
    (5, "移植", "de trasplantes", "trasplante"),
    (5, "视力表", "tablet de variedad visual", "cartilla de la vista"),
    (5, "看不清的", "trastornador", "borroso"),
    (5, "看护", "monitorear", "atender"),
    # gid 6 在邮局
    (6, "邮包", "parcela", "paquete postal"),
    (6, "邮袋", "portacartas", "saco de correo"),
    (6, "乡下", "campaña", "campo"),
    (6, "粘上", "pegamento", "pegar"),
    # gid 7 在银行
    (7, "储户", "cuenta de ahorros", "ahorrador"),
    (7, "取款", "depósito quitado", "retiro"),
    (7, "转账", "trasladar", "transferir"),
    # gid 8 在理发店
    (8, "平头", "cabeza plana", "corte de cepillo"),
    (8, "卷起", "agrupamiento", "enrollar"),
    (8, "梳理", "desentrañar", "peinar"),
    (8, "发蜡", "ungüento", "cera para el pelo"),
    (8, "边", "dobladillo", "lado"),
    # gid 9 常见商店
    (9, "肉店", "carnicero", "carnicería"),
    (9, "磅秤", "mecedora", "báscula"),
    (9, "保质期", "período de garantía de la calidad", "fecha de caducidad"),
    # gid 11 人的特征
    (11, "消瘦的", "seco", "demacrado"),
    (11, "比例", "escala", "proporción"),
    (11, "鼓起来的", "saldado", "abultado"),
    (11, "深陷的", "atascado", "hundido"),
    (11, "卑鄙的", "astroso", "vil"),
    (11, "微弱的", "pálido", "tenue"),
    (11, "捧腹大笑", "reír a torcer", "reír a carcajadas"),
    (11, "嘲笑", "tomar a risa algo", "burlarse de"),
    (11, "幽默地", "tiene el humor", "humorístico"),
    (11, "早产儿", "prematura", "prematuro"),
    (11, "中年", "edad mediana", "edad media"),
    # gid 12 人身体的行为
    (12, "弯腰", "curva", "agacharse"),
    (12, "摇晃", "escalonar", "balancear"),
    (12, "拖着脚步走", "colgando de la pierna", "arrastrar los pies"),
    (12, "叫喊", "proclamar", "vociferar"),
    (12, "表扬", "exaltar", "elogiar"),
    (12, "鼓掌", "animar", "aplaudir"),
    # gid 13 人的情绪
    (13, "喜爱", "preferencia", "afición"),
    (13, "偏袒", "ponerse al lado", "favorecer"),
    (13, "漠不关心的", "desinteresado", "indiferente"),
    # gid 14 人类交流的方式
    (14, "缩放", "condensación", "zoom"),
    (14, "关机", "cerrar", "apagar"),
    (14, "直板手机", "teléfono de la barra", "teléfono de barra"),
    (14, "刷新", "renovar", "actualizar"),
    # gid 15 人与人之间的关系
    (15, "亲近的", "afecto", "cercano"),
    (15, "亲属", "relación", "pariente"),
    (15, "同等地", "también", "igualmente"),
    (15, "竞争的", "competido", "competitivo"),
]

# (gid, old_substring, new_substring) -> replaced inside the S sentence Spanish text
S_FIX = [
    (5, "Sarah se cayó la barbilla", "rompieron la barbilla a Sarah"),
    (5, "se puso las orejas en el suelo", "acercó la oreja al suelo"),
    (5, "célula ácida", "célula glandular"),
    (6, "comigo", "conmigo"),
    (8, "La cabeza suya es pelada", "Él está calvo"),
    (11, "el europe", "el europeo"),
    (13, "preciar ", "apreciar "),
    (13, "despreciará", "despreciar"),
    (14, "español blog", "blog español"),
    (15, "del soltería", "de la soltería"),
]

def norm(s):
    return re.sub(r'[^a-záéíóúñü]', '', (s or "").lower())

# ---- global es-text -> audio path map (for reuse) + taken numbers -------------------
es_by_text = {}
taken = set()
for i2 in range(48):
    fp = os.path.join(BASE, "data/sec/%d.js" % i2)
    if not os.path.exists(fp): continue
    t2 = open(fp, encoding="utf-8").read()
    for mm in re.finditer(r'es/(\d{5})\.mp3', t2): taken.add(int(mm.group(1)))
    i = t2.index("={") + 1
    d = 0; j = i; ins = False; esc = False
    while j < len(t2):
        c = t2[j]
        if ins:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == '{': d += 1
            elif c == '}':
                d -= 1
                if d == 0: break
        j += 1
    try:
        o2 = json.loads(t2[i:j+1])
    except Exception:
        continue
    for s in o2.get("secs", []):
        for r in s.get("w", []) + s.get("e", []):
            if len(r) == 7 and r[3]:
                es_by_text.setdefault(norm(r[1]), r[3])
        for r in s.get("s", []):
            if len(r) == 7 and r[3]:
                es_by_text.setdefault(norm(r[0]), r[3])

def cur_max(folder):
    m = 0
    for f in os.listdir(os.path.join(BASE, folder)):
        mm = re.match(r'(\d{5})\.mp3$', f)
        if mm: m = max(m, int(mm.group(1)))
    return m

es_n = cur_max("audio/es") + 1
def next_es():
    global es_n
    while es_n in taken: es_n += 1
    n = es_n; es_n = n + 1; taken.add(n)
    return "es/%05d.mp3" % n

def assign(new_es):
    cand = es_by_text.get(norm(new_es))
    if cand and os.path.exists(os.path.join(BASE, "audio", cand)):
        return cand, "reuse"
    p = next_es()
    es_by_text[norm(new_es)] = p   # so identical new text reuses instead of dup mp3
    return p, "new"

def load(gid):
    path = os.path.join(BASE, "data/sec/%d.js" % gid)
    t = open(path, encoding="utf-8").read()
    p = t.index("={")
    prefix = t[:p+1]
    i = p + 1
    d = 0; j = i; ins = False; esc = False
    while j < len(t):
        c = t[j]
        if ins:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == '{': d += 1
            elif c == '}':
                d -= 1
                if d == 0: break
        j += 1
    return path, prefix, json.loads(t[i:j+1])

def save(path, prefix, obj):
    open(path, "w", encoding="utf-8").write(
        prefix + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";")

# group fixes by gid
from collections import defaultdict
W_BY = defaultdict(list); S_BY = defaultdict(list)
for t in W_FIX: W_BY[t[0]].append(t)
for t in S_FIX: S_BY[t[0]].append(t)

all_changed = []
for gid in sorted(set(list(W_BY) + list(S_BY))):
    path, prefix, obj = load(gid)
    for s in obj["secs"]:
        for r in s["w"]:
            for g, cn, old_es, new_es in W_BY[gid]:
                if r[0] == cn and norm(r[1]) == norm(old_es):
                    if r[1] == new_es:
                        continue
                    old_path = r[3]
                    r[1] = new_es
                    r[6] = text_ipa(new_es)
                    r[3], how = assign(new_es)
                    all_changed.append(("W", gid, cn, old_es, old_path, new_es, r[3], how))
                    break
        for r in s["s"]:
            for g, old_sub, new_sub in S_BY[gid]:
                if old_sub in r[0] and new_sub not in r[0]:
                    new_es = r[0].replace(old_sub, new_sub)
                    old_path = r[3]
                    r[0] = new_es
                    r[6] = text_ipa(new_es)
                    r[3], how = assign(new_es)
                    all_changed.append(("S", gid, r[1][:10], old_sub, old_path, new_es, r[3], how))
                    break
    save(path, prefix, obj)

# verify every fix matched at least once
applied_W = defaultdict(int); applied_S = defaultdict(int)
for c in all_changed:
    if c[0] == "W": applied_W[(c[1], c[2], c[3])] += 1
    else: applied_S[(c[1], c[3])] += 1
for t in W_FIX:
    key = (t[0], t[2], t[3])
    assert applied_W.get(key, 0) >= 1, "W fix not applied: %r" % (t,)
for t in S_FIX:
    key = (t[0], t[3])
    assert applied_S.get(key, 0) >= 1, "S fix not applied: %r" % (t,)

for c in all_changed:
    print("FIXED %s gid%d %-10s %r (%s) -> %r (%s) [%s]" % c)
print("total changed:", len(all_changed), "next es=", es_n)
