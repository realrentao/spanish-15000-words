# -*- coding: utf-8 -*-
"""Generate missing edge-tts audio for the whole site (authoritative = all data/sec/*.js),
then rebuild _tools/audio_manifest.json from every referenced path.
Spanish voice: es-ES-ElviraNeural ; Chinese voice: zh-CN-XiaoxiaoNeural.
"""
import os, re, json, asyncio, glob
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"

def load_sec(path):
    t = open(path, encoding="utf-8").read()
    i = t.index("={") + 1
    depth=0; j=i; ins=False; esc=False
    while j < len(t):
        c=t[j]
        if ins:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c=='"': ins=False
        else:
            if c=='"': ins=True
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0: break
        j+=1
    return json.loads(t[i:j+1])

def collect():
    jobs=[]
    for sp in sorted(glob.glob(os.path.join(BASE,"data/sec/*.js"))):
        o=load_sec(sp)
        for s in o.get("secs",[]):
            for kind,arr in (("w",s.get("w",[])),("e",s.get("e",[])),("s",s.get("s",[]))):
                for r in arr:
                    es_text = r[0] if kind=="s" else r[1]
                    zh_text = r[1] if kind=="s" else r[0]
                    es_path = r[3]; zh_path = r[4]
                    if es_path: jobs.append((es_text, es_path, "es"))
                    if zh_path: jobs.append((zh_text, zh_path, "zh"))
    return jobs

def exists(p):
    return os.path.exists(os.path.join(BASE, "audio", p))

async def gen_one(text, relpath):
    from edge_tts import Communicate
    out = os.path.join(BASE, "audio", relpath)
    if exists(relpath):
        return "skip"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # 路径形如 "es/00012.mp3" / "zh/00012.mp3"（前缀不含 audio/）。
    # 历史 bug：这里写成 relpath.startswith("audio/es") 恒为 False，
    # 导致所有新建的西语音频被 zh-CN-XiaoxiaoNeural 配音再存进 audio/es/ —— 西语全军覆没。
    voice = ES_VOICE if relpath.startswith("es/") else ZH_VOICE
    for attempt in range(4):
        try:
            comm = Communicate(text, voice)
            await asyncio.wait_for(comm.save(out), timeout=35)
            if os.path.getsize(out) > 200:
                return "ok"
            os.remove(out)
        except Exception as e:
            if attempt == 3:
                print("FAIL", relpath, type(e).__name__, str(e)[:120], flush=True)
                return "fail"
    return "fail"

async def main():
    jobs = collect()
    missing = [j for j in jobs if not exists(j[1])]
    print("total refs:", len(jobs), "missing:", len(missing), flush=True)
    sem = asyncio.Semaphore(4)
    async def wrap(j):
        async with sem:
            return await gen_one(j[0], j[1])
    results = await asyncio.gather(*[wrap(j) for j in missing])
    ok = sum(1 for r in results if r=="ok")
    skip = sum(1 for r in results if r=="skip")
    fail = sum(1 for r in results if r=="fail")
    print("generated:", ok, "skip:", skip, "fail:", fail, flush=True)
    # rebuild manifest authoritatively
    seen=set(); man=[]
    for text,relpath,lang in jobs:
        if relpath in seen: continue
        seen.add(relpath)
        man.append({"text":text,"path":relpath,"lang":lang})
    json.dump({"jobs":man}, open(os.path.join(BASE,"_tools/audio_manifest.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=0)
    print("manifest rebuilt: total jobs =", len(man))

if __name__=="__main__":
    asyncio.run(main())
