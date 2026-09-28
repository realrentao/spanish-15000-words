# -*- coding: utf-8 -*-
import os, sys, re, json, glob, asyncio
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
from es_ipa import text_ipa
import pypinyin
from pypinyin import pinyin, Style

ZH_RE = re.compile(r"[^\w\u4e00-\u9fff]+")
ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"


def zh_pinyin(text):
    clean = ZH_RE.sub(" ", text).strip()
    parts = pinyin(clean, style=Style.TONE, heteronym=False, errors="default")
    return " ".join(p[0] for p in parts if p and p[0])


def load_sec47():
    s = open(os.path.join(ROOT, "data", "sec", "47.js"), encoding="utf-8").read()
    i = s.index("window.BOOK_DATA[47]=")
    j = s.index("{", i)
    k = s.rindex("}")
    return json.loads(s[j:k + 1])


def main():
    d = load_sec47()
    need = []  # (path, text, voice)
    for sec in d["secs"]:
        for it in sec["w"] + sec["e"]:
            need.append((it[3], it[1], ES_VOICE))
            need.append((it[4], it[0], ZH_VOICE))
        for it in sec["s"]:
            need.append((it[3], it[0], ES_VOICE))
            need.append((it[4], it[1], ZH_VOICE))

    tasks = []
    for rel, text, voice in need:
        p = os.path.join(ROOT, "audio", rel)
        if not os.path.exists(p) or os.path.getsize(p) < 44:
            if os.path.exists(p):
                os.remove(p)
            tasks.append((p, text, voice))

    print("待重生成：", len(tasks))

    async def gen_all(ts):
        import edge_tts
        sem = asyncio.Semaphore(3)

        async def one(tp):
            path, text, voice = tp
            for attempt in range(4):
                try:
                    comm = edge_tts.Communicate(text, voice, rate="+0%")
                    with open(path, "wb") as f:
                        async for chunk in comm.stream():
                            if chunk["type"] == "audio":
                                f.write(chunk["data"])
                    if os.path.getsize(path) >= 44:
                        return
                except Exception as e:
                    print("  retry", os.path.basename(path), e)
            print("  !! 失败", os.path.basename(path), repr(text))

        await asyncio.gather(*[one(t) for t in ts])

    if tasks:
        asyncio.run(gen_all(tasks))
    # 校验
    remain = [t for t in tasks if not os.path.exists(t[0]) or os.path.getsize(t[0]) < 44]
    print("仍缺失：", len(remain))
    for t in remain:
        print("   ", t[1], t[2])


if __name__ == "__main__":
    main()
