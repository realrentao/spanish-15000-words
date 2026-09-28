# -*- coding: utf-8 -*-
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from es_ipa import text_ipa
from pypinyin import pinyin, Style

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 1

# ---- pinyin helper: only Chinese syllables, space-separated ----
def py(zh):
    sylls = []
    for ch in pinyin(zh, style=Style.NORMAL, errors="ignore", strict=False):
        s = ch[0]
        if s:
            sylls.append(s)
    return " ".join(sylls)

# ---- read sec/1.js ----
def read_obj(path):
    t = open(path, encoding="utf-8").read()
    p = t.index("={")            # position of '='
    start = p + 1                # position of '{'
    depth = 0; i = start; instr = False; esc = False
    while i < len(t):
        c = t[i]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': instr = False
        else:
            if c == '"': instr = True
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0: break
        i += 1
    return t[:p+1], json.loads(t[start:i+1]), t[i+1:]

prefix, obj, suffix = read_obj(os.path.join(BASE, f"data/sec/{GID}.js"))

# ---- global audio reuse maps (es_text -> path, zh_text -> path) ----
es_map = {}
zh_map = {}
for f in os.listdir(os.path.join(BASE, "data/sec")):
    if not f.endswith(".js"):
        continue
    _, o, _ = read_obj(os.path.join(BASE, "data/sec", f))
    for sec in o["secs"]:
        for arr in ("w", "s", "e"):
            if arr not in sec:
                continue
            for row in sec[arr]:
                if len(row) >= 5:
                    e = (row[1] or "").strip().lower()
                    z = (row[0] or "").strip()
                    if e and e not in es_map:
                        es_map[e] = row[3]
                    if z and z not in zh_map:
                        zh_map[z] = row[4]

# ---- new number counters ----
def next_es():
    global es_next
    p = "es/%05d.mp3" % es_next; es_next += 1; return p
def next_zh():
    global zh_next
    p = "zh/%05d.mp3" % zh_next; zh_next += 1; return p

es_next = 6255
zh_next = 7032

audio_jobs = []  # (es_text, es_path, zh_text, zh_path)

def get_es(es):
    e = es.strip().lower()
    if e in es_map:
        return es_map[e]
    p = next_es()
    audio_jobs.append((es, p, None, None))
    return p

def get_zh(zh):
    z = zh.strip()
    if z in zh_map:
        return zh_map[z]
    p = next_zh()
    audio_jobs.append((None, None, zh, p))
    return p

# ---- canonical W lists (zh, es, pos) in book order ----
CW = {
 1: [("衣服","ropa","n.f."),("穿衣服","vestir","v.t."),("制服","uniforme","n.m."),
     ("内衣","ropa interior",""),("礼服","ropaje","n.m."),("浴衣","albornoz","n.m."),
     ("燕尾服","tuxedo","n.m."),("睡袍","camisón","n.m."),("运动服","ropa deportiva",""),
     ("领带","corbata","n.f."),("正式的","formal","adj."),("非正式的","informal","adj."),
     ("时尚的","de moda","adj."),("游泳衣","trajes de baño","")],
 2: [("服装材料","materiales de la ropa",""),("布料","tela","n.f."),("质地","jaez","n.m."),
     ("棉花","algodón","n.m."),("蚕丝","seda","n.f."),("羊毛","lana","n.m."),
     ("涤纶","poliéster","n.m."),("帆布","lienzo","n.m."),("皮革","cuero","n.m."),
     ("质量好的","buena calidad",""),("触摸","toque","n.m."),("柔软","suavidad","n.f."),
     ("合成纤维","fibra sintética",""),("可渗透的","permeable","adj.")],
 3: [("绿色的","verde","adj."),("翡翠绿","verde esmeralda",""),("浅绿色","verde claro",""),
     ("苹果绿","verde de manzana",""),("暗绿色","verde oscuro",""),("黄色的","amarillo","adj."),
     ("芥末黄","amarillo de mostaza",""),("柠檬黄","amarillo limón",""),("微黄色的","amarillo claro",""),
     ("金色","oro","n.m."),("褐色","marrón","n.m."),("米色","beige","n.m."),
     ("黄绿色","amarillo-verde",""),("黄褐色","amarillo-marrón",""),("金黄色","amarillo dorado","")],
 4: [("蓝色的","azul","adj."),("天蓝色","azul cielo",""),("深蓝色","azul oscuro",""),
     ("海蓝色","azul marino",""),("普蓝色","azul de Berlín",""),("瓷蓝色","azul de cobalto",""),
     ("宝蓝色","azul zafiro",""),("碧蓝色","azul oscuro",""),("藏蓝色","azul purpúreo",""),
     ("深蓝的，靛青的","turquí","adj."),("紫色","violeta","n.m."),("浅紫色","violeta claro",""),
     ("紫红色","fucsia","n.f."),("紫罗兰","violeta","n.f."),("深紫色","violeta oscuro",""),
     ("紫色的","cárdeno","adj."),("深紫色的","morado","adj."),("紫红色","púrpura","n.f."),
     ("青紫色的","amoratado","adj."),("洋红色","magenta","n.f."),("洋红的","carmíneo","adj.")],
 5: [("红色","rojo","n.m."),("粉红的","rosado","adj."),("紫红色","fucsia","n.f."),
     ("深红色","rojo oscuro",""),("朱红色","bermellón","n.m."),("深红色","rojo oscuro",""),
     ("猩红色","escarlata","n.f."),("银色","plata","n.f."),("黑色","negro","n.m."),
     ("青铜色","bronce","n.m."),("白色","blanco","n.m."),("象牙白","marfil","n.m."),
     ("灰色","gris","n.m."),("棕色","marrón","n.m."),("浅棕色","marrón claro","adj."),
     ("多彩的","coloroso","adj.")],
 6: [("得体的","decente","adj."),("与……相配","hacer juego",""),("朴素的","simple","adj."),
     ("漂亮雅致的","elegante","adj."),("对比","contraste","n.m."),("运动的","deportivo","adj."),
     ("衣服的风格","estilo","n.m."),("肤色","color","n.m."),("最近的","reciente","adj."),
     ("适当的","apropiado","adj."),("完美的","perfecto","adj."),("流行的","popular","adj."),
     ("多种色彩的","multicolor","adj."),("印象","impresión","n.f."),("细节","detalle","n.m.")],
 7: [("最新款式","últimos estilos",""),("流行","moda","n.f."),("过时的","anticuado","adj."),
     ("领子","collar","n.m."),("领口","escote","n.m."),("U型领","escote en-u",""),
     ("V型领","escote en-v",""),("尺寸","tamaño","n.m."),("小号的","pequeño","adj."),
     ("中号的","medio","adj."),("大号的","grande","adj."),("剪裁","recorte","n.m."),
     ("特大号的","XL","adj."),("胸围","busto","n.m."),("孕妇装","ropa de maternidad","")],
 8: [("帽子","sombrero","n.m."),("帽子","chapeo","n.m."),("礼帽","galera","n.f."),
     ("草帽","chapeo de hierba",""),("兜帽","capucha","n.f."),("贝雷帽","boina","n.f."),
     ("戴着","vistiendo",""),("头饰","tocado","n.m."),("头巾","pañuelo de cabeza",""),
     ("头盔","casco","n.m."),("带，箍","copo","n.m.")],
 9: [("大衣","abrigo","n.m."),("短外套","chaqueta","n.f."),("短大衣","abrigo corto",""),
     ("女衬衫","blusa","n.f."),("衬衫","camisa","n.f."),("T-恤衫","camiseta","n.f."),
     ("汗衫","camiseta interior",""),("毛衣","suéter","n.m."),("开襟短上衣","chaqueta cárdigan",""),
     ("无袖毛衣","suéter sin mangas",""),("坎肩背心","chaleco","n.m."),("外衣","capa","n.f."),
     ("内衣","ropa interior",""),("乳罩","sujetador","n.m."),("无袖的","sin mangas",""),
     ("纽扣","botón","n.m."),("宽松的","suelto","adj."),("紧的","estrecho","adj.")],
 10: [("裤子","pantalón","n.m."),("牛仔裤","jean","n.m."),("喇叭裤","pantalones acampanados",""),
      ("内裤","braga","n.f."),("短裤","pantalones cortos",""),("灯笼裤","pantalones anchos",""),
      ("裤","overol","n.m."),("短衬裤","calzoncillos","n.m."),("马裤","alforja","n.f."),
      ("背带","correa","n.f."),("裤腿","pierna del pantalón",""),("口袋","bolsillo","n.m."),
      ("拉链","zip",""),("扣子","botón","n.m."),("宽松的","suelto","adj."),
      ("松弛","relajación","n.f."),("下垂的","colgante","adj."),("舒适的","cómodo","adj.")],
 11: [("裙子","falda","n.f."),("连衣裙","traje","n.m."),("迷你短裙","mini falda",""),
      ("芭蕾舞裙","falda de ballet",""),("短褶裙","falda corta",""),("喇叭裙","falda con pata de elefante",""),
      ("衬裙","enagua","n.f."),("无袖连衣裙","traje sin mangas",""),("宽松连衣裙","traje suelto",""),
      ("和服","kimono","n.m."),("褶裙","kilt","n.m."),("透明的","transparente","adj."),
      ("透明的","claro","adj.")],
 12: [("鞋","zapato","n.m."),("木屐","zueco","n.m."),("靴子","bota","n.f."),
      ("拖鞋","chancla","n.f."),("凉鞋","sandalia","n.f."),("运动鞋","calzado deportivo",""),
      ("高跟鞋","zapatos de tacón alto",""),("矮跟鞋","zapatos de tacón bajo",""),("鞋底","suela","n.f."),
      ("短袜","calcetines","n.f."),("长袜","medias","n.f."),("系紧","fijar","v.t."),
      ("一双，一对","un par",""),("旧鞋","zapatos viejos",""),("厚实坚固的","sólido","adj."),
      ("大的，巨大的","grande","adj.")],
 13: [("背包","paquete","n.m."),("背包","mochila","n.f."),("手提包","bolso","n.m."),
      ("公文包","maletín","n.f."),("旅行袋","bolsa de viaje",""),("塑料的","plástico","adj."),
      ("手提箱","valise","n.f."),("旅行箱","maleta","n.f."),("钱包","billetera","n.f."),
      ("书包","bolsa para la escuela",""),("挎包","alforja","n.f."),("薄的","delgado","adj."),
      ("厚的","grueso","adj."),("松紧带","elasticidad","n.f."),("内衬","forro","n.m.")],
}

# ---- rebuild W arrays ----
for sec in obj["secs"]:
    no = sec["no"]
    if no not in CW:
        continue
    # per-section lookup of existing rows
    lookup = {}
    for row in sec.get("w", []):
        if len(row) >= 5:
            lookup[(row[0].strip(), row[1].strip().lower())] = row
    new_w = []
    for (zh, es, pos) in CW[no]:
        key = (zh.strip(), es.strip().lower())
        if key in lookup:
            new_w.append(lookup[key])  # preserve existing (audio + pinyin + ipa)
        else:
            ep = get_es(es)
            zp = get_zh(zh)
            new_w.append([zh, es, pos, ep, zp, py(zh), text_ipa(es)])
    sec["w"] = new_w

# ---- S fixes / additions ----
for sec in obj["secs"]:
    no = sec["no"]
    if no == 1:
        # insert missing sentence at index 1
        es_t = "¿Te gusta el uniforme de azul cielo o de azul oscuro?"
        zh_t = "你喜欢天蓝的还是深蓝的制服？"
        ep = get_es(es_t); zp = get_zh(zh_t)
        row = [es_t, zh_t, "", ep, zp, py(zh_t), text_ipa(es_t)]
        sec["s"].insert(1, row)
    elif no == 4:
        # fix EI -> El (index 2)
        row = sec["s"][2]
        row[0] = "El violado es para usted."
        row[3] = get_es(row[0])
        row[5] = py(row[1])
        row[6] = text_ipa(row[0])

# ---- write sec/1.js ----
out = prefix + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + suffix
open(os.path.join(BASE, f"data/sec/{GID}.js"), "w", encoding="utf-8").write(out)
print("sec/1.js written; new audio jobs:", len(audio_jobs))

# ---- write manifest (merge with existing so re-runs don't drop jobs) ----
mj = os.path.join(BASE, "_tools/audio_manifest.json")
existing = []
if os.path.exists(mj):
    try:
        existing = json.load(open(mj, encoding="utf-8")).get("jobs", [])
    except Exception:
        existing = []
seen = set()
merged = []
for j in existing + audio_jobs:
    if j[1] is None and j[3] is None:
        continue
    key = j[1] or j[3]
    if key in seen:
        continue
    seen.add(key); merged.append(j)
json.dump({"jobs": merged}, open(mj, "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)

# ---- update meta.js counts ----
mt = open(os.path.join(BASE, "data/meta.js"), encoding="utf-8").read()
mi = mt.index("=") + 1
# brace-match the JSON object even if extra trailing chars exist
mt2 = mt[mi:]
depth = 0; j = 0; instr = False; esc = False
while j < len(mt2):
    c = mt2[j]
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
    j += 1
meta = json.loads(mt2[:j+1])
for g in meta["grupos"]:
    if g["name"] != "基本生活":
        continue
    for p in g["partes"]:
        if p["gid"] != GID:
            continue
        for s in p["secs"]:
            # find rebuilt sec
            rb = next(x for x in obj["secs"] if x["no"] == s["no"])
            s["w"] = len(rb.get("w", []))
            s["s"] = len(rb.get("s", []))
            s["e"] = len(rb.get("e", []))
# recompute global totals
tw = ts = te = 0
for g in meta["grupos"]:
    for p in g["partes"]:
        for s in p["secs"]:
            tw += s.get("w", 0); ts += s.get("s", 0); te += s.get("e", 0)
meta["total.w"] = tw; meta["total.s"] = ts; meta["total.e"] = te
meta["totalAll"] = tw + ts + te
open(os.path.join(BASE, "data/meta.js"), "w", encoding="utf-8").write(
    "window.BOOK_META=" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";")
print("meta totals: w=%d s=%d e=%d all=%d" % (tw, ts, te, meta["totalAll"]))
