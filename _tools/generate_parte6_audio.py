# -*- coding: utf-8 -*-
"""Generate edge-tts audio for Parte 6 (gid=5) NEW entries only.
Reads _tools/audio_manifest.json; for jobs whose es/zh path is in the new range
(es >= es/06693.mp3, zh >= zh/07466.mp3), generate if not already on disk.
es-ES-ElviraNeural / zh-CN-XiaoxiaoNeural, 8 concurrent, 4 retries, byte-check.
"""
import asyncio, edge_tts, os, json, time, re
BASE = "D:/西班牙语材料/15000词西语随身背"
ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"
mj = os.path.join(BASE, "_tools/audio_manifest.json")
jobs = json.load(open(mj, encoding="utf-8")).get("jobs", [])

def num(p):
    m = re.match(r'(?:es|zh)/(\d{5})\.mp3$', p or "")
    return int(m.group(1)) if m else 0

NEW_ES = 6693
NEW_ZH = 7466

def is_new(rel):
    if not rel: return False
    if rel.startswith("es/") and num(rel) >= NEW_ES: return True
    if rel.startswith("zh/") and num(rel) >= NEW_ZH: return True
    return False

def exists(rel):
    return os.path.exists(os.path.join(BASE, "audio", rel))

sem = asyncio.Semaphore(8)

async def gen_one(text, voice, rel):
    path = os.path.join(BASE, "audio", rel)
    if os.path.exists(path):
        return "skip"
    async with sem:
        for attempt in range(4):
            try:
                comm = edge_tts.Communicate(text, voice)
                await comm.save(path)
                if os.path.getsize(path) > 0:
                    return "OK"
                if os.path.exists(path):
                    try: os.remove(path)
                    except Exception: pass
            except Exception as e:
                if attempt == 3:
                    return "ERR:%s" % e
                await asyncio.sleep(1.5)
    return "skip"

async def main():
    todo = []
    for j in jobs:
        es, esp, zh, zhp = j.get("es"), j.get("esPath"), j.get("zh"), j.get("zhPath")
        if is_new(esp) and not exists(esp):
            todo.append((es, ES_VOICE, esp))
        if is_new(zhp) and not exists(zhp):
            todo.append((zh, ZH_VOICE, zhp))
    log = open(os.path.join(BASE, "_tools/gen_parte6_audio.log"), "w", encoding="utf-8")
    total = len(todo)
    done = 0; ok = 0; err = 0; skip = 0
    t0 = time.time()
    log.write("TODO: %d files\n" % total); log.flush()
    async def worker(item):
        text, voice, rel = item
        res = await gen_one(text, voice, rel)
        return rel, res
    # chunked gather to keep concurrency bounded by semaphore
    results = []
    for i in range(0, total, 50):
        chunk = todo[i:i+50]
        rs = await asyncio.gather(*[worker(x) for x in chunk])
        results.extend(rs)
    for rel, res in results:
        done += 1
        if res == "OK": ok += 1
        elif res == "skip": skip += 1
        else:
            err += 1
            log.write("ERR %s %s\n" % (rel, res))
        if done % 20 == 0 or done == total:
            log.write("PROGRESS %d/%d ok=%d err=%d skip=%d  %.1fs\n" % (done, total, ok, err, skip, time.time()-t0))
            log.flush()
    log.write("DONE: %d/%d generated (ok=%d err=%d skip=%d)\n" % (ok, total, ok, err, skip))
    log.flush(); log.close()
    print("DONE: %d/%d  ok=%d err=%d skip=%d" % (ok, total, ok, err, skip))

if __name__ == "__main__":
    asyncio.run(main())
