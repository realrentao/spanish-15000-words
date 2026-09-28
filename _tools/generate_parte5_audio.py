# -*- coding: utf-8 -*-
"""Generate edge-tts audio for Parte 5 new entries.
Reads _tools/audio_manifest.json; for each job, if the es/zh mp3 does not yet
exist on disk, generate it (skip existing). Logs progress to gen_parte5_audio.log.
"""
import asyncio, edge_tts, os, json, time
BASE = "D:/西班牙语材料/15000词西语随身背"
ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"
mj = os.path.join(BASE, "_tools/audio_manifest.json")
jobs = json.load(open(mj, encoding="utf-8")).get("jobs", [])

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
                if os.path.exists(path): os.remove(path)
            except Exception as e:
                if attempt == 3:
                    return "ERR:%s" % e
                await asyncio.sleep(1.5)
    return "skip"

async def main():
    todo = []
    for j in jobs:
        es, esp, zh, zhp = j.get("es"), j.get("esPath"), j.get("zh"), j.get("zhPath")
        if esp and not exists(esp):
            todo.append((es, ES_VOICE, esp, "es"))
        if zhp and not exists(zhp):
            todo.append((zh, ZH_VOICE, zhp, "zh"))
    log = open(os.path.join(BASE, "_tools/gen_parte5_audio.log"), "w", encoding="utf-8")
    total = len(todo)
    done = 0; ok = 0; err = 0; skip = 0
    t0 = time.time()
    for i, (text, voice, rel, kind) in enumerate(todo):
        res = await gen_one(text, voice, rel)
        done += 1
        if res == "OK": ok += 1
        elif res == "skip": skip += 1
        else: err += 1; log.write("ERR %s %s %s\n" % (rel, text[:40], res))
        if done % 10 == 0 or done == total:
            log.write("PROGRESS %d/%d ok=%d err=%d skip=%d  %.1fs\n" % (done, total, ok, err, skip, time.time()-t0))
            log.flush()
    log.write("DONE: %d/%d generated (ok=%d err=%d skip=%d)\n" % (ok, total, ok, err, skip))
    log.flush(); log.close()
    print("DONE: %d/%d  ok=%d err=%d skip=%d" % (ok, total, ok, err, skip))

if __name__ == "__main__":
    asyncio.run(main())
