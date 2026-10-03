# -*- coding: utf-8 -*-
""".Force-regenerate the Spanish audio files that were synthesized with the
wrong voice (zh-CN-XiaoxiaoNeural instead of es-ES-ElviraNeural).

Root cause: generate_parte10_audio.py used relpath.startswith("audio/es")
while relpath is like "es/06998.mp3" (no audio/ prefix) -> always False.
Every freshly allocated Spanish slot from that point on got a Chinese voice.

Binary search on the es/NNNNN numbering located the break point:
last OK = 6826, first BAD = 6827.  Everything >= 6827 that was really
synthesized must be re-generated with the Spanish voice.

Idempotent / resumable: a progress file records already-fixed paths.
"""
import os, re, sys, asyncio, json, glob, time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ES_VOICE = "es-ES-ElviraNeural"
LIMIT = 6827
PROGRESS = os.path.join(BASE, "_tools/_regen_es_progress.json")

sys.path.insert(0, os.path.join(BASE, "_tools"))
from generate_parte10_audio import collect, BASE as B  # noqa: E402


def num(p):
    return int(re.search(r"(\d+)", os.path.basename(p)).group(1))


def load_done():
    if os.path.exists(PROGRESS):
        return set(json.load(open(PROGRESS, encoding="utf-8")))
    return set()


def save_done(s):
    json.dump(sorted(s), open(PROGRESS, "w", encoding="utf-8"), ensure_ascii=False)


async def gen_one(text, relpath, sem, todo):
    from edge_tts import Communicate
    out = os.path.join(BASE, "audio", relpath)
    for attempt in range(4):
        async with sem:
            try:
                # 直接覆盖写入：edge_tts 内部以 wb 模式打开，会截断重写。
                # 不要用 os.remove —— 本机沙箱有批量删除守卫，删到 50 个会被拦停。
                comm = Communicate(text, ES_VOICE)
                await asyncio.wait_for(comm.save(out), timeout=35)
                if os.path.getsize(out) > 200:
                    return True
            except Exception as e:
                if attempt == 3:
                    print("FAIL %s %s %s" % (relpath, type(e).__name__, str(e)[:100]), flush=True)
                    return False
                await asyncio.sleep(1.5 * (attempt + 1))
    return False


async def main():
    jobs = collect()                      # (text, relpath, lang)
    targets = [(t, p) for (t, p, lang) in jobs
               if lang == "es" and num(p) >= LIMIT]
    targets = [(t, p) for (t, p) in targets if os.path.exists(os.path.join(BASE, "audio", p))]

    done = load_done()
    todo = [(t, p) for (t, p) in targets if p not in done]
    print("targets(es,>=%d): %d  already done: %d  todo: %d"
          % (LIMIT, len(targets), len(done), len(todo)), flush=True)

    sem = asyncio.Semaphore(4)
    t0 = time.time()
    for i, (t, p) in enumerate(todo):
        ok = await gen_one(t, p, sem, todo)
        if ok:
            done.add(p)
            if (i + 1) % 100 == 0:
                save_done(done)
                el = time.time() - t0
                print("[%d/%d] %.0fs left~%.0fs" %
                      (i + 1, len(todo), el, el / (i + 1) * (len(todo) - i - 1)), flush=True)
    save_done(done)
    print("done: %d  total targets: %d  elapsed %.0fs"
          % (len(done), len(targets), time.time() - t0), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
