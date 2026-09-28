# -*- coding: utf-8 -*-
"""精修 sec/0.js 的「数词（1）」: 填充 25 个数字词(w) + 同步 4 句经典例句(s) + 6 个词汇大拓展(e)，并重新生成对应西/中音频。"""
import os, sys, json, asyncio, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pypinyin import pinyin, Style
import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"

# ---------- 拼音 ----------
def py(text):
    parts = pinyin(text, style=Style.TONE, errors="ignore")
    return " ".join(p[0] for p in parts if p[0])

# ---------- 句子 IPA（用站内转换器）----------
try:
    from es_ipa import text_ipa
except Exception:
    text_ipa = None

# =======================================================================
# 内容定义
# =======================================================================
# 数字词 w: (中文, 西语, 词类, IPA)
WORDS = [
    ("一", "uno, una", "m.", "ˈuno, ˈuna"),
    ("二", "dos", "m.", "dos"),
    ("三", "tres", "m.", "tɾes"),
    ("四", "cuatro", "m.", "ˈkwatɾo"),
    ("五", "cinco", "m.", "ˈsiŋko"),
    ("六", "seis", "m.", "sejs"),
    ("七", "siete", "m.", "ˈsjete"),
    ("八", "ocho", "m.", "ˈotʃo"),
    ("九", "nueve", "m.", "ˈnweβe"),
    ("十", "diez", "m.", "djeθ/djes"),
    ("十一", "once", "m.", "ˈonθe/ˈonse"),
    ("十二", "doce", "m.", "ˈdoθe/ˈdose"),
    ("十三", "trece", "m.", "ˈtɾeθe/ˈtɾese"),
    ("十四", "catorce", "m.", "kaˈtoɾθe/kaˈtoɾse"),
    ("十五", "quince", "m.", "ˈkiŋθe/ˈkinse"),
    ("十六", "dieciséis", "m.", "djeθiˈsejs/djesiˈsejs"),
    ("十七", "diecisiete", "m.", "djeθiˈsjete/djesiˈsjete"),
    ("十八", "dieciocho", "m.", "djeθiˈotʃo/djesiˈotʃo"),
    ("十九", "diecinueve", "m.", "djeθiˈnweβe/djesiˈnweβe"),
    ("二十", "veinte", "m.", "ˈbejnte"),
    ("二十一", "veintiuno", "m. inv.", "bejnˈtjuno"),
    ("二十二", "veintidós", "m. inv.", "bejntiˈðos"),
    ("二十三", "veintitrés", "m. inv.", "bejntiˈtɾes"),
    ("二十四", "veinticuatro", "m. inv.", "bejntiˈkwatɾo"),
    ("二十五", "veinticinco", "m. inv.", "bejntiˈsiŋko"),
]

# 经典例句 s: (西语, 中文, 出处)
SENTENCES = [
    ("La valentía y la alegría son dos factores vitales.",
     "勇气和快乐是生活必不可少的两个要素。", ""),
    ("¿Qué hora es? Son las cinco menos cuarto.",
     "现在几点了？差一刻五点。", ""),
    ("Créame, son los quince minutos más aterradores del día.",
     "相信我，这是每天最恐怖的15分钟。", "《绝望的主妇》"),
    ("Quien a los veinte años tiene la misma visión del mundo que a los cincuenta, ha perdido treinta años de su vida.",
     "人若二十岁就有五十岁的心，便错失了三十年的美好年华。", ""),
]

# 词汇大拓展 e: (中文, 西语, 词类, IPA)
EXPANSIONS = [
    ("勇气", "valentía", "f.", "balenˈtja"),
    ("因素", "factor", "m.", "fakˈtoɾ"),
    ("生命的", "vital", "adj.", "biˈtal"),
    ("较少，更少", "menos", "adv.", "ˈmenos"),
    ("可怕的，恐怖的", "aterrador, a", "adj.", "ateɾaˈðoɾ, a"),
    ("失去，丧失", "perder", "v.t.", "peɾˈðeɾ"),
]

# =======================================================================
# 音频生成
# =======================================================================
es_counter = [None]
zh_counter = [None]

def next_es():
    es_counter[0] += 1
    return f"es/{es_counter[0]:05d}.mp3"

def next_zh():
    zh_counter[0] += 1
    return f"zh/{zh_counter[0]:05d}.mp3"

async def tts_one(text, voice, out_path, sem):
    async with sem:
        for attempt in range(4):
            try:
                comm = edge_tts.Communicate(text, voice, rate="+0%")
                with open(out_path, "wb") as f:
                    async for chunk in comm.stream():
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])
                if os.path.getsize(out_path) > 44:
                    return True
                os.remove(out_path)
            except Exception as e:
                if attempt == 3:
                    print("  FAIL", out_path, e)
                await asyncio.sleep(0.6 * (attempt + 1))
    return False

async def gen_all(tasks):
    sem = asyncio.Semaphore(8)
    # tasks: list of (text, voice, out_path)
    # skip existing
    todo = [(t, v, o) for (t, v, o) in tasks if not (os.path.exists(o) and os.path.getsize(o) > 44)]
    print(f"  需生成 {len(todo)} / {len(tasks)} 个音频")
    await asyncio.gather(*[tts_one(t, v, o, sem) for (t, v, o) in todo])

# =======================================================================
# 主流程
# =======================================================================
def main():
    # 起始编号（当前最大 +1）
    es_files = [int(f[:-4]) for f in os.listdir(os.path.join(ROOT, "audio/es")) if f.endswith(".mp3")]
    zh_files = [int(f[:-4]) for f in os.listdir(os.path.join(ROOT, "audio/zh")) if f.endswith(".mp3")]
    es_counter[0] = max(es_files)
    zh_counter[0] = max(zh_files)
    print(f"  当前 es 最大={es_counter[0]} zh 最大={zh_counter[0]}")

    tasks = []
    w_arr, s_arr, e_arr = [], [], []

    # --- w ---
    print("构建 w (25 数字词)...")
    for zh, es, pos, ipa in WORDS:
        es_path = next_es()
        zh_path = next_zh()
        tasks.append((es, ES_VOICE, os.path.join(ROOT, "audio", es_path)))
        tasks.append((zh, ZH_VOICE, os.path.join(ROOT, "audio", zh_path)))
        w_arr.append([zh, es, pos, es_path, zh_path, py(zh), ipa])

    # --- s ---
    print("构建 s (4 经典例句)...")
    for es, zh, src in SENTENCES:
        es_path = next_es()
        zh_path = next_zh()
        tasks.append((es, ES_VOICE, os.path.join(ROOT, "audio", es_path)))
        tasks.append((zh, ZH_VOICE, os.path.join(ROOT, "audio", zh_path)))
        ipa = text_ipa(es) if text_ipa else ""
        s_arr.append([es, zh, src, es_path, zh_path, py(zh), ipa])

    # --- e ---
    print("构建 e (6 词汇大拓展)...")
    for zh, es, pos, ipa in EXPANSIONS:
        es_path = next_es()
        zh_path = next_zh()
        tasks.append((es, ES_VOICE, os.path.join(ROOT, "audio", es_path)))
        tasks.append((zh, ZH_VOICE, os.path.join(ROOT, "audio", zh_path)))
        e_arr.append([zh, es, pos, es_path, zh_path, py(zh), ipa])

    print(f"总音频任务: {len(tasks)}")
    asyncio.run(gen_all(tasks))

    # --- 写回 sec/0.js ---
    print("写入 sec/0.js ...")
    sp = os.path.join(ROOT, "data/sec/0.js")
    s = open(sp, encoding="utf-8").read()
    marker = "window.BOOK_DATA[0]="
    idx = s.index(marker) + len(marker)
    prefix = s[:idx]
    json_str = s[idx:]
    jstart = json_str.index("{")
    jend = json_str.rindex("}") + 1
    obj = json.loads(json_str[jstart:jend])
    sec = obj["secs"][3]
    assert sec["name"] == "数词（1）", sec["name"]
    sec["w"] = w_arr
    sec["s"] = s_arr
    sec["e"] = e_arr
    new_json = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    with open(sp, "w", encoding="utf-8") as f:
        f.write(prefix + new_json + ";")

    # --- 更新 meta.js ---
    print("更新 meta.js ...")
    mp = os.path.join(ROOT, "data/meta.js")
    ms = open(mp, encoding="utf-8").read()
    midx = ms.index("window.BOOK_META=") + len("window.BOOK_META=")
    mobj = json.loads(ms[midx:ms.rindex("}") + 1])
    # 更新本小节计数
    for gr in mobj["grupos"]:
        for parte in gr["partes"]:
            for ssec in parte["secs"]:
                if ssec.get("name") == "数词（1）":
                    ssec["w"], ssec["s"], ssec["e"] = 25, 4, 6
    # 从所有 sec 文件重算全局 total
    tw = ts = te = 0
    for fp in sorted(glob.glob(os.path.join(ROOT, "data/sec/*.js"))):
        t = open(fp, encoding="utf-8").read()
        i = t.index("window.BOOK_DATA[")
        j = t.index("{", i)
        k = t.rindex("}")
        d = json.loads(t[j:k + 1])
        for ss in d["secs"]:
            tw += len(ss.get("w", []))
            ts += len(ss.get("s", []))
            te += len(ss.get("e", []))
    mobj["total"] = {"w": tw, "s": ts, "e": te}
    mobj["totalAll"] = tw + ts + te
    with open(mp, "w", encoding="utf-8") as f:
        f.write("window.BOOK_META=" + json.dumps(mobj, ensure_ascii=False, separators=(",", ":")) + ";")
    print(f"  meta total: w={tw} s={ts} e={te} totalAll={mobj['totalAll']}")

    print("完成。")

if __name__ == "__main__":
    main()
