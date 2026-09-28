# -*- coding: utf-8 -*-
import json, os, asyncio, edge_tts

BASE = r"D:\西班牙语材料\15000词西语随身背"
path = os.path.join(BASE, "data", "sec", "4.js")

txt = open(path, encoding="utf-8").read()
PREFIX = "window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[4]="
idx = txt.index(PREFIX) + len(PREFIX)
dec = json.JSONDecoder()
obj, end = dec.raw_decode(txt, idx)
trailing = txt[end:]

target = None
for sec in obj["secs"]:
    if sec.get("name") == "搭火车":
        target = sec
        break
assert target, "sec 搭火车 not found"

w = target["w"]

# locate entries by current (broken) Chinese text
def find(startswith):
    for i, row in enumerate(w):
        if row[0].startswith(startswith):
            return i, row
    raise SystemExit("not found: " + startswith)

# ---- 货运站 ----
i4, e4 = find("货运站")
print("BEFORE W%d: %s" % (i4, e4))
e4[0] = "货运站"
e4[1] = "estación de mercancías"
e4[5] = "huò yùn zhàn"
e4[6] = "estaˈθjon de meɾkanˈθias"
e4[3] = "es/06218.mp3"
e4[4] = "zh/06995.mp3"
print("AFTER  W%d: %s" % (i4, e4))

# ---- 铁路员工 ----
i6, e6 = find("铁路员工")
print("BEFORE W%d: %s" % (i6, e6))
e6[0] = "铁路员工"
e6[1] = "trabajador del ferrocarril"
e6[5] = "tiě lù yuán gōng"
e6[6] = "tɾaβaxaˈðoɾ ðel feɾokarˈil"
e6[3] = "es/06217.mp3"
e6[4] = "zh/06994.mp3"
print("AFTER  W%d: %s" % (i6, e6))

# write back, preserving prefix + trailing exactly
open(path, "w", encoding="utf-8").write(PREFIX + json.dumps(obj, ensure_ascii=False) + trailing)
print("sec/4.js written")

# ---- audio generation ----
VOICE_ES = "es-ES-ElviraNeural"
VOICE_ZH = "zh-CN-XiaoxiaoNeural"
sem = asyncio.Semaphore(4)

async def gen(text, voice, out):
    if os.path.exists(out) and os.path.getsize(out) > 500:
        return True
    for _ in range(4):
        try:
            await edge_tts.Communicate(text, voice).save(out)
            if os.path.getsize(out) > 500:
                return True
        except Exception:
            pass
    return False

async def main():
    plan = [
        ("es/06217.mp3", "trabajador del ferrocarril", VOICE_ES),
        ("zh/06994.mp3", "铁路员工", VOICE_ZH),
        ("es/06218.mp3", "estación de mercancías", VOICE_ES),
        ("zh/06995.mp3", "货运站", VOICE_ZH),
    ]
    tasks = [gen(t, v, os.path.join(BASE, "audio", f)) for f, t, v in plan]
    res = await asyncio.gather(*tasks)
    for (f, t, v), ok in zip(plan, res):
        print(("OK  " if ok else "FAIL") + " %s  %s" % (f, t))

asyncio.run(main())
print("DONE")
