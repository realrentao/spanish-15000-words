# -*- coding: utf-8 -*-
""".Force-regenerate every Spanish mp3 whose number >= BAD_FROM (the slots that
were synthesized with the wrong, Chinese voice because of the
`relpath.startswith("audio/es")` bug).

Robust version: throttled, 429-aware, resumable, and it verifies the md5 of a
sample at the end.

Usage:
    python _tools/regen_es2.py            # regenerate
    python _tools/regen_es2.py --probe    # only verify a sample, do not write
"""
import os, re, sys, asyncio, json, glob, time, hashlib, tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "_tools"))
ES_VOICE = "es-ES-ElviraNeural"
BAD_FROM = 6827
PROGRESS = os.path.join(BASE, "_tools/_regen_es_progress.json")

from generate_parte10_audio import collect, BASE as B  # noqa: E402

CONC = 3


def num(p):
    return int(re.search(r"(\d+)", os.path.basename(p)).group(1))


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load_done():
    if os.path.exists(PROGRESS):
        try:
            return set(json.load(open(PROGRESS, encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_done(s):
    json.dump(sorted(s), open(PROGRESS, "w", encoding="utf-8"), ensure_ascii=False)


async def synth(text, tmpdir, voice):
    from edge_tts import Communicate
    out = os.path.join(tmpdir, "p.mp3")
    try:
        await asyncio.wait_for(Communicate(text, voice).save(out), timeout=35)
        return md5(out)
    except Exception as e:
        return "ERR:%s" % (type(e).__name__,)


async def gen_one(text, relpath, td, sem):
    from edge_tts import Communicate
    out = os.path.join(BASE, "audio", relpath)
    async with sem:
        for attempt in range(6):
            try:
                comm = Communicate(text, ES_VOICE)
                await asyncio.wait_for(comm.save(out), timeout=40)
                if os.path.exists(out) and os.path.getsize(out) > 200:
                    return True
            except Exception as e:
                msg = str(e)
                if "429" in msg or "Too Many" in msg:
                    await asyncio.sleep(6 + 5 * attempt)
                    continue
                if attempt == 5:
                    print("FAIL %s %s %s" % (relpath, type(e).__name__, msg[:80]), flush=True)
                    return False
                await asyncio.sleep(1.5 * (attempt + 1))
    return False


async def main():
    probe = "--probe" in sys.argv
    jobs = collect()
    targets = []
    for (t, p, lang) in jobs:
        if lang != "es":
            continue
        fp = os.path.join(BASE, "audio", p)
        if not os.path.exists(fp):
            continue
        if num(p) >= BAD_FROM:
            targets.append((t, p))
    if probe:
        # 抽样校验：只比对 md5，不写回文件
        targets.sort()
        samp = targets[:8] + targets[len(targets) // 2:len(targets) // 2 + 8] + targets[-8:]
        td = tempfile.mkdtemp(dir=os.path.join(BASE, "_tools", "_regen_tmp"))
        os.makedirs(td, exist_ok=True)
        sem = asyncio.Semaphore(CONC)
        tasks = []
        for (t, p) in samp:
            async def chk(t=t, p=p):
                async with sem:
                    h = await synth(t, td, ES_VOICE)
                    sp = os.path.join(BASE, "audio", p)
                    cur = md5(sp) if os.path.exists(sp) else None
                    return (p, t, h == cur)
            tasks.append(chk())
        res = await asyncio.gather(*tasks)
        ok = sum(1 for r in res if r[2])
        for p, t, good in res[:10]:
            print("  %s %s %s" % ("OK " if good else "BAD", p, t[:24]))
        print("probe sample=%d match=%d" % (len(res), ok), flush=True)
        return

    done = load_done()
    todo = [(t, p) for (t, p) in targets if p not in done]
    print("targets=%d done=%d todo=%d" % (len(targets), len(done), len(todo)), flush=True)
    sem = asyncio.Semaphore(CONC)
    td = tempfile.mkdtemp(dir=os.path.join(BASE, "_tools", "_regen_tmp"))
    os.makedirs(td, exist_ok=True)
    t0 = time.time()
    for i, (t, p) in enumerate(todo):
        if await gen_one(t, p, td, sem):
            done.add(p)
        if (i + 1) % 50 == 0:
            save_done(done)
            el = time.time() - t0
            print("[%d/%d] %.0fs left~%.0fs" %
                  (i + 1, len(todo), el, el / (i + 1) * (len(todo) - i - 1)), flush=True)
    save_done(done)
    print("regenerated=%d targets=%d elapsed=%.0fs" % (len(done), len(targets), time.time() - t0), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
