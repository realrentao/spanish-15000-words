# -*- coding: utf-8 -*-
"""Fill any missing NEW audio for Parte 6 (gid=5) directly from data/sec/5.js.
Scans all es/zh paths in the new range (es>=es/06693, zh>=zh/07466); for any that
are missing on disk, generate via edge-tts. Authoritative source = sec/5.js (not the
manifest, which may be polluted by earlier build runs)."""
import asyncio, edge_tts, os, re, json
BASE = "D:/西班牙语材料/15000词西语随身背"
ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"

def num(p):
    m = re.match(r'(?:es|zh)/(\d{5})\.mp3$', p or "")
    return int(m.group(1)) if m else 0

def load_sec(gid):
    t = open(os.path.join(BASE, "data/sec/%d.js" % gid), encoding="utf-8").read()
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

obj = load_sec(5)
todo = []
for s in obj["secs"]:
    for kind,key in (("w","w"),("s","s"),("e","e")):
        for r in s[key]:
            ep, zp = r[3], r[4]
            if num(ep) >= 6693 and not os.path.exists(os.path.join(BASE,"audio",ep)):
                txt = r[1] if kind!="s" else r[0]
                todo.append((txt, ES_VOICE, ep))
            if num(zp) >= 7466 and not os.path.exists(os.path.join(BASE,"audio",zp)):
                txt = r[0] if kind!="s" else r[1]
                todo.append((txt, ZH_VOICE, zp))

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
    total=len(todo); done=ok=err=skip=0
    for i in range(0, total, 50):
        rs = await asyncio.gather(*[gen_one(t,v,p) for (t,v,p) in todo[i:i+50]])
        for res in rs:
            done+=1
            if res=="OK": ok+=1
            elif res=="skip": skip+=1
            else: err+=1; print("ERR", res)
    print("DONE: %d/%d ok=%d err=%d skip=%d" % (ok,total,ok,err,skip))

if __name__ == "__main__":
    asyncio.run(main())
