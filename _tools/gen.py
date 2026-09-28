# -*- coding: utf-8 -*-
"""生成第九篇《时尚热词》分册，复用已有音频，生成缺失音频，并更新 meta.js。"""
import os, sys, re, json, glob, asyncio
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
from content import WORDS, SENTENCES, EXT
from es_ipa import text_ipa
import pypinyin
from pypinyin import pinyin, Style

SEC_GID = 47
GNAME = "时尚热词"
PNAME = "时尚热词"
SNAME = "时尚热词"

ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"
AUDIO_FMT = "audio-24khz-48kbitrate-mono-mp3"

ZH_RE = re.compile(r"[^\w\u4e00-\u9fff]+")


def zh_pinyin(text):
    clean = ZH_RE.sub(" ", text).strip()
    parts = pinyin(clean, style=Style.TONE, heteronym=False, errors="default")
    return " ".join(p[0] for p in parts if p and p[0])


def load_sec(path):
    s = open(path, encoding="utf-8").read()
    i = s.index("window.BOOK_DATA[")
    j = s.index("{", i)
    k = s.rindex("}")
    return json.loads(s[j:k + 1])


def build_existing_maps():
    es_map, zh_map = {}, {}
    for f in glob.glob(os.path.join(ROOT, "data", "sec", "*.js")):
        try:
            d = load_sec(f)
        except Exception:
            continue
        for sec in d["secs"]:
            for it in sec.get("w", []) + sec.get("e", []):
                es_map.setdefault(it[1], int(it[3].split("/")[1].split(".")[0]))
                zh_map.setdefault(it[0], int(it[4].split("/")[1].split(".")[0]))
            for it in sec.get("s", []):
                es_map.setdefault(it[0], int(it[3].split("/")[1].split(".")[0]))
                zh_map.setdefault(it[1], int(it[4].split("/")[1].split(".")[0]))
    return es_map, zh_map


def alloc(m, idx, maxref):
    if idx[0] is None:
        for v in m.values():
            maxref[0] = max(maxref[0], v)
        idx[0] = maxref[0]
    return idx[0]


def main():
    es_map, zh_map = build_existing_maps()
    maxe = [None]; maxz = [None]

    async def gen_all(tasks):
        import edge_tts
        sem = asyncio.Semaphore(8)

        async def one(tp):
            path, text, voice = tp
            async with sem:
                try:
                    comm = edge_tts.Communicate(text, voice, rate="+0%")
                    with open(path, "wb") as f:
                        async for chunk in comm.stream():
                            if chunk["type"] == "audio":
                                f.write(chunk["data"])
                except Exception as e:
                    print("  ! fail", path, e)

        await asyncio.gather(*[one(t) for t in tasks])

    new_tasks = []

    def es_index(text):
        if text in es_map:
            return es_map[text]
        if maxe[0] is None:
            maxe[0] = max(es_map.values()) if es_map else 6062
        maxe[0] += 1
        es_map[text] = maxe[0]
        ap = os.path.join(ROOT, "audio", "es", "%05d.mp3" % maxe[0])
        new_tasks.append((ap, text, ES_VOICE))
        return maxe[0]

    def zh_index(text):
        if text in zh_map:
            return zh_map[text]
        if maxz[0] is None:
            maxz[0] = max(zh_map.values()) if zh_map else 6814
        maxz[0] += 1
        zh_map[text] = maxz[0]
        ap = os.path.join(ROOT, "audio", "zh", "%05d.mp3" % maxz[0])
        new_tasks.append((ap, text, ZH_VOICE))
        return maxz[0]

    # ---- 终极分类词 ----
    w = []
    for zh, es, pos in WORDS:
        ei = es_index(es)
        zi = zh_index(zh)
        w.append([zh, es, pos, "es/%05d.mp3" % ei, "zh/%05d.mp3" % zi,
                  zh_pinyin(zh), text_ipa(es)])
    # ---- 经典实用句 ----
    s = []
    for es, zh in SENTENCES:
        ei = es_index(es)
        zi = zh_index(zh)
        s.append([es, zh, "", "es/%05d.mp3" % ei, "zh/%05d.mp3" % zi,
                  zh_pinyin(zh), text_ipa(es)])
    # ---- 词汇大拓展 ----
    e = []
    for zh, es, pos in EXT:
        ei = es_index(es)
        zi = zh_index(zh)
        e.append([zh, es, pos, "es/%05d.mp3" % ei, "zh/%05d.mp3" % zi,
                  zh_pinyin(zh), text_ipa(es)])

    print("需生成音频文件：", len(new_tasks))

    if new_tasks:
        asyncio.run(gen_all(new_tasks))
        print("音频生成完成")

    sec = {"no": 1, "name": SNAME, "w": w, "s": s, "e": e}
    blob = {
        "gid": SEC_GID, "no": 1, "name": PNAME, "gname": GNAME,
        "secs": [sec],
    }
    out = os.path.join(ROOT, "data", "sec", "%d.js" % SEC_GID)
    with open(out, "w", encoding="utf-8") as f:
        f.write("window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=" % SEC_GID)
        json.dump(blob, f, ensure_ascii=False)
        f.write(";")
    print("写入", out)

    # ---- 更新 meta.js ----
    meta = open(os.path.join(ROOT, "data", "meta.js"), encoding="utf-8").read()
    j = meta[meta.index("{"):meta.rindex("}") + 1]
    m = json.loads(j)
    new_grupo = {
        "name": GNAME,
        "partes": [{
            "gid": SEC_GID, "no": 1, "name": PNAME,
            "secs": [{"no": 1, "name": SNAME, "w": len(w), "s": len(s), "e": len(e)}],
        }],
    }
    m["grupos"].append(new_grupo)
    # 重新统计
    tot = {"w": 0, "s": 0, "e": 0}
    nv = 0
    for gr in m["grupos"]:
        for pt in gr["partes"]:
            nv += 1
            for sc in pt["secs"]:
                tot["w"] += sc["w"]; tot["s"] += sc["s"]; tot["e"] += sc["e"]
    m["total"] = tot
    m["totalAll"] = sum(tot.values())
    new_meta = "window.BOOK_META=" + json.dumps(m, ensure_ascii=False) + ";"
    open(os.path.join(ROOT, "data", "meta.js"), "w", encoding="utf-8").write(new_meta)
    print("meta.js 已更新：grupos=%d partes=%d totalAll=%d" % (len(m["grupos"]), nv, m["totalAll"]))
    print("本篇：终极分类词 %d / 经典实用句 %d / 词汇大拓展 %d" % (len(w), len(s), len(e)))


if __name__ == "__main__":
    main()
