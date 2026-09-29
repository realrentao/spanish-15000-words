# -*- coding: utf-8 -*-
"""Generate edge-tts audio for Parte 8 (gid=7).
Source of truth = data/sec/7.js. For every es/zh audio path referenced in sec/7.js
that is missing on disk, generate it. Then rebuild _tools/audio_manifest.json
authoritatively from ALL existing sec files (0..47) so old + new jobs are present.
"""
import asyncio, edge_tts, os, re, json, glob
BASE = "D:/西班牙语材料/15000词西语随身背"
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

obj = load_sec(os.path.join(BASE, "data/sec/7.js"))
todo = []
seen = set()
for s in obj["secs"]:
    for kind, etxt, ztxt in (
        ("w",1,0), ("e",1,0), ("s",0,1)):
        for r in s[kind]:
            ep, zp = r[3], r[4]
            if ep and not os.path.exists(os.path.join(BASE,"audio",ep)) and ep not in seen:
                seen.add(ep); todo.append((r[etxt], ES_VOICE, ep))
            if zp and not os.path.exists(os.path.join(BASE,"audio",zp)) and zp not in seen:
                seen.add(zp); todo.append((r[ztxt], ZH_VOICE, zp))

sem = asyncio.Semaphore(8)
async def gen_one(text, voice, rel):
    path = os.path.join(BASE, "audio", rel)
    if os.path.exists(path):
        return "skip"
    async with sem:
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text, voice).save(path)
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
    total=len(todo); ok=err=skip=0
    for i in range(0, total, 50):
        rs = await asyncio.gather(*[gen_one(t,v,p) for (t,v,p) in todo[i:i+50]])
        for res in rs:
            if res=="OK": ok+=1
            elif res=="skip": skip+=1
            else: err+=1; print("ERR", res)
    print("GEN: %d/%d ok=%d err=%d skip=%d" % (ok,total,ok,err,skip))

asyncio.run(main())

# ---- rebuild manifest authoritatively from ALL sec files ----
jobs=[]
jseen=set()
for sp in sorted(glob.glob(os.path.join(BASE,"data/sec/*.js"))):
    o=load_sec(sp)
    for s in o.get("secs",[]):
        for kind, etxt, ztxt in (
            ("w",1,0), ("e",1,0), ("s",0,1)):
            for r in s[kind]:
                ep, zp = r[3], r[4]
                if ep and ep not in jseen:
                    jseen.add(ep); jobs.append({"es":r[etxt],"esPath":ep,"zh":r[ztxt],"zhPath":zp})
                if zp and zp not in jseen:
                    jseen.add(zp); jobs.append({"es":r[ztxt],"esPath":zp,"zh":r[etxt],"zhPath":ep})
json.dump({"jobs":jobs}, open(os.path.join(BASE,"_tools/audio_manifest.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=0)
print("manifest rebuilt: jobs=%d" % len(jobs))
