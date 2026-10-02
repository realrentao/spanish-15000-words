# -*- coding: utf-8 -*-
"""重建 gid18「学习成长」10 小节：以 _tools/parte18_raw.txt（用户粘贴文案）为内容权威，
   并把其中不符合西语表述习惯 / 词义不符 / OCR 拼写错 / 词性配错的地方修正掉。

铁律：
  - 词性只按文案标；文案没标的保持不标。
  - 只改西语文本 + 对应 es 音频 + IPA；中文 / zh 音频 / 拼音不动。
  - 文案的值在西语里不成立时才回退（下方 RETAIN 里列出来）。

修正分类（见 ES_FIX / ES_TYPO / S_SUBS / POS_FIX / POST_FIX / RETAIN）。
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_parte_lib import Builder, clean_es

GID, BP_NAME, RAW = 18, "学习成长", "_tools/parte18_raw.txt"

# ---------------------------------------------------------------- 1) 西语替换（中文头词 -> 正确西语）
# 只改西语；词性仍按文案（文案标错的一律进 POS_FIX）。
ES_FIX = {
    ("有事业心的", "emprenderdor"): "emprendedor",  # OCR 断词 emprender-dor 被拼成错误词形
    ("选课", "elegir la clase"): "elegir asignaturas",   # elegir la clase 不成立（la clase=这节课）
    ("选择的", "selectivo"): "electivo",            # selectivo=挑剔的/精心挑选的；「选修的」是 electivo
    ("点名", "hacer la lista"): "pasar lista",      # 点名西语固定说法 pasar lista（hacer la lista 不成立）
    ("社团", "comunidad"): "asociación",            # comunidad=社区/共同体；「社团」= asociación
    ("赞助", "apoyo"): "patrocinio",                # apoyo=支持/扶持；「赞助」= patrocinio
    ("奖金", "bono"): "bonus",                      # bono=债券/代金券；「奖金」= bonus（bonus n.m.）
    ("加入", "añadir"): "unirse a",                 # añadir=添加；「加入(社团)」= unirse a
    ("留级", "repetición del estudio"): "repetir curso",       # 留级西语固定说法 repetir curso
    ("名列前茅", "tener un buen ranking"): "llenar los primeros puestos",  # ranking 是英语借词，原说法不成立
    ("文学士", "bachiller de literatura"): "bachillerato de letras",       # bachiller≠bachillerato；「文学士」= bachillerato de letras
    ("理学士", "bachiller de tecnología"): "bachillerato de ciencias",     # tecnología 不对，「理科学士」= bachillerato de ciencias
    ("硕士", "licenciatura"): "máster",             # licenciatura=本科/学士（西班牙），「硕士」= máster / maestría
    ("通晓多种语言的", "sabe muchas leguas"): "políglota",     # 「sabe muchas leguas」是英/法语直译，不成立
    ("提纲，方案", "programa"): "esquema",          # programa=程序/计划/大纲；「提纲」= esquema
    ("结论", "conclusion"): "conclusión",           # conclusion 缺重音且为英语化，西语 conclusión
    ("坚定的", "asegurado"): "firme",               # asegurado=受保险的/稳妥的；「坚定的」= firme/decidido
}

# ---------------------------------------------------------------- 2) OCR 拼写
ES_TYPO = {"activiad": "actividad"}

# ---------------------------------------------------------------- 3) 经典实用句（西语）子串替换
S_SUBS = [
    # 句首字母标点：. -> ¿ / ¡（clean 后前的句点已被剥掉，这里补问号/叹号）
    ("reclamar exenciones?", "solicitar exenciones?"),   # reclamar=索求/抗议；申请豁免用 solicitar
    ("Tiene usted algún contacto en la especialidad doméstica y la de España",
     "Tiene usted algún contacto entre la especialidad de su país y la de España"),
    # OCR 断词 in-gles -> ingles（少了重音）
    ("diaria de ingles", "diaria de inglés"),
    # 讲座提前结束：con media hora de anticipación 不地道
    ("terminó con media hora de anticipación", "terminó media hora antes"),
    # 享有声誉：缺主语一致性 + tiene una reputación 不自然
    ("Entre los clientes tiene una reputación excelente",
     "Entre sus clientes goza de una reputación excelente"),
    # 证书「有效」用 es válido，es efectivo 用于人/效力；Dele -> DELE（官方写法）
    ("El certificado de Dele es efectivo en todo el mundo",
     "El certificado DELE es válido en todo el mundo"),
    # 她是社长：presidente 作阴性名词用 presidenta
    ("Es la presidente del club literario", "Es la presidenta del club literario"),
    # 真遗憾…输了：对既成事实的惋惜用虚拟式 hayan perdido
    ("Lástima que ellos han perdido el partido", "Lástima que hayan perdido el partido"),
    # 成于勤而荒于嬉：原句把 «llevar a» 的两个宾语拆散，语法不成立
    ("la diligencia nos lleva al éxito y la diversión, al fracaso, y los estudios de lenguas extranjeras también",
     "la diligencia nos lleva al éxito y la diversión nos lleva al fracaso, y los estudios de lenguas extranjeras también"),
    # 我从…毕业已经两年：Llevo dos anos + 形容词缺系词
    ("Llevo ya dos años licenciada en filología hispánica",
     "Llevo ya dos años como licenciada en filología hispánica"),
    # graduarse 用 en 不用 de
    ("Cuándo se graduó de Oxford", "Cuándo se graduó en Oxford"),
    # ésto 缺重音（西语 esto 无重音音符号；原 OCR 残留）+ 学位证书应为 licenciatura
    ("ésto es el certificado del licenciado", "Esto es el certificado de licenciatura"),
    # dudar 后接 en + infinitivo
    ("Nunca dudo a declarar, que el diploma", "Nunca dudo en declarar que el diploma"),
    # postular 在西班牙本土义为「推荐/竞选」，申请签证用 solicitar
    ("Ella postuló a una visa", "Ella solicitó una visa"),
    ("¡Perdí mi pasaporte", "¡Perdí mi pasaporte"),          # 仅保证句首叹号排版
    # 答辩 = defender la tesis，leer su tesis 只是「宣读」
    ("Anna leerá su tesis el lunes", "Anna defenderá su tesis el lunes"),
    ("Quién quiere hacer un resumen sencillo", "¿Quién quiere hacer un resumen sencillo"),
    # 要么缺乏动力，要么想享受阳光：or 两边结构不对齐
    ("Debido a la falta de motivación o disfruta del sol",
     "Debido a la falta de motivación o al deseo de disfrutar del sol"),
]

# ---------------------------------------------------------------- 4) 词性（文案标错的按西语事实纠正）
POS_FIX = {
    "奖学金": "n.f.",      # beca 是阴性
    "签证": "n.f.",        # visa 是阴性
    "学士": "n.m.",        # bachiller 是阳性
    "导师": "n.m.",        # maestro 是阳性
    "提名，推荐": "adj.",   # propuesto 是过去分词/形容词，不是名词
    "环境的": "adj.",      # ambiental 是形容词
}

# ---------------------------------------------------------------- 5) 跑构建
b = Builder(GID, BP_NAME, RAW, ES_FIX=ES_FIX, ES_TYPO=ES_TYPO, S_SUBS=S_SUBS, POS_FIX=POS_FIX)
b.run()

# ---------------------------------------------------------------- 6) 后处理：逐条精确修正 + 去重
SEC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/sec/%d.js" % GID)
t = open(SEC_PATH, encoding="utf-8").read()
p = t.index("={")
prefix = t[:p + 1]
obj = json.loads(t[p + 1:-1])

POST_FIX = {
    ("奖学金", "beca"): ("n.f.",),          # 只在「奖学金 beca」这一行生效（budget 里同中文还有别条）
    ("máster",): ("n.m.",),                 # 毕业节「硕士 máster」用阳性（POST_FIX 按 es 精确命中）
    ("签证", "visa"): ("n.f.",),
    ("学士", "bachiller"): ("n.m.",),
    ("导师", "maestro"): ("n.m.",),
    ("propuesto",): ("adj.",),              # E 行：propuesto 提名，推荐
    ("ambiental",): ("adj.",),              # E 行：ambiental 环境的
}

applied = []
for s in obj["secs"]:
    seen = set()
    for arr in ("w", "e"):
        out = []
        for r in s.get(arr, []):
            cn, es, pos = r[0], r[1], r[2]
            key = cn if arr == "w" else es
            if arr == "w" and cn == "目的" and es in seen:
                applied.append(("DEDUP", s["name"], cn, es))
                continue          # 讲座里「目的 objetivo」出现两次，删掉第二条
            if arr == "w":
                seen.add(es)
            for pk, pv in POST_FIX.items():
                if es == pk[0] and pos != pv[0]:
                    applied.append(("POS", arr, s["name"], r))
                    r[2] = pv[0]
            out.append(r)
        s[arr] = out
    # S 行：标点规范化（句首 ¿/¡ 与句末 ?/! 配对；S_SUBS 已在 Builder 里应用过，避免重复替换）
    from es_ipa import text_ipa
    for r in s.get("s", []):
        old = r[0]
        new = old
        if new.rstrip().endswith("?") and not new.startswith("¿"):
            new = new if "¿" in new[1:] else "¿" + new   # 句中已有 ¿（冒号后跟问句）就不再补句首
        elif new.rstrip().endswith("!"):
            new = ("¡" + new.lstrip("¿¡ ")) if not new.startswith("¡") else "¡" + new[1:].lstrip("¿¡ ")
        elif new.rstrip().endswith("¿"):          # 句末倒问号却无句首开问号
            new = "¿" + new.rstrip()[:-1].rstrip() + "?"
        if new != old:
            r[0] = new
            r[6] = text_ipa(new)
            applied.append(("PUNT", s["name"], old, "->", new, r[3]))

obj["gid"] = GID
obj["no"] = 3
obj["name"] = BP_NAME
obj["gname"] = "校园"
open(SEC_PATH, "w", encoding="utf-8").write(
    prefix + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";")
print("\n=== 后处理 %d 处 ===" % len(applied))
for a in applied:
    print("  ", a)

print("\n=== 最终统计 ===")
tw = ts = te = 0
for s in obj["secs"]:
    print("  sec%-2d %-10s W=%-3d S=%-3d E=%-3d" % (s["no"], s["name"], len(s["w"]), len(s["s"]), len(s["e"])))
    tw += len(s["w"]); ts += len(s["s"]); te += len(s["e"])
print("  TOTAL W=%d S=%d E=%d all=%d" % (tw, ts, te, tw + ts + te))
