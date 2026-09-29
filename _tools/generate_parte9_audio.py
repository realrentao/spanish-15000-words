# -*- coding: utf-8 -*-
"""Generate any MISSING edge-tts audio referenced by data/sec/*.js, then rebuild
_tools/audio_manifest.json authoritatively from all sec files (this clears any
pollution from earlier partial runs). Reuses existing files (disk is source of truth).
"""
import json, re, os, asyncio, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"

def load_sec(path):
    t = open(path, encoding="utf-8").read()
    i = t.index("={") + 1
    depth = 0; j = i; ins = False; esc = False
    while j < len(t):
        c = t[j]
        if ins:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
        j += 1
    return json.loads(t[i:j+1])

# collect all (es_text, es_path, zh_text, zh_path) from every sec file
jobs = []  # (text, path, voice)
seen = set()
for sp in sorted(__import__("glob").glob(os.path.join(BASE, "data/sec/*.js"))):
    o = load_sec(sp)
    for s in o.get("secs", []):
        for kind, arr in (("w", s.get("w", [])), ("e", s.get("e", [])), ("s", s.get("s", []))):
            for r in arr:
                if kind == "s":
                    es_text, zh_text, es_path, zh_path = r[0], r[1], r[3], r[4]
                else:
                    es_text, zh_text, es_path, zh_path = r[1], r[0], r[3], r[4]
                for text, path, voice in ((es_text, es_path, ES_VOICE), (zh_text, zh_path, ZH_VOICE)):
                    if not text or not path:
                        continue
                    if path in seen:
                        continue
                    seen.add(path)
                    jobs.append((text, path, voice))

# only generate missing
missing = []
for text, path, voice in jobs:
    fp = os.path.join(BASE, "audio", path)
    if not os.path.exists(fp):
        missing.append((text, path, voice))
print("total refs: %d, missing: %d" % (len(jobs), len(missing)))

async def gen_one(text, path, voice):
    fp = os.path.join(BASE, "audio", path)
    for attempt in range(4):
        try:
            comm = __import__("edge_tts").Communicate(text, voice)
            await comm.save(fp)
            if os.path.getsize(fp) > 0:
                return True
        except Exception as e:
            if attempt == 3:
                print("FAIL", path, text, e)
            await asyncio.sleep(0.5)
    return False

async def main():
    sem = asyncio.Semaphore(8)
    async def wrap(t, p, v):
        async with sem:
            ok = await gen_one(t, p, v)
            return p, ok
    results = await asyncio.gather(*[wrap(t, p, v) for t, p, v in missing])
    fails = [p for p, ok in results if not ok]
    print("generated: %d, failures: %d" % (len(results), len(fails)))
    if fails:
        print("FAILURES:", fails)

asyncio.run(main())

# rebuild manifest authoritatively
manifest = {"jobs": [{"es": t, "esPath": p} if v == ES_VOICE else {"zh": t, "zhPath": p}
                     for t, p, v in jobs]}
# merge into a single job list keyed by path to avoid duplication
merged = {}
for t, p, v in jobs:
    if p not in merged:
        merged[p] = {"path": p, "voice": v, "text": t}
mp = {"jobs": list(merged.values())}
with open(os.path.join(BASE, "_tools/audio_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(mp, f, ensure_ascii=False, separators=(",", ":"))
print("manifest rebuilt: %d jobs (authoritative, from all sec files)" % len(mp["jobs"]))
