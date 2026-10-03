# -*- coding: utf-8 -*-
"""按给定的 (文本, 文件路径) 重新合成一次音频，与磁盘上的 mp3 比对 md5。
一致 => 磁盘音频确实由该文本生成（未串号）；
不一致 => 磁盘音频是旧文本/别处文本的产物（串号）。"""
import os, sys, asyncio, hashlib, shutil, tempfile
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"

async def synth(text, voice, out):
    from edge_tts import Communicate
    for _ in range(3):
        try:
            await asyncio.wait_for(Communicate(text, voice).save(out), timeout=35)
            if os.path.getsize(out) > 200:
                return True
        except Exception as e:
            print("  err", type(e).__name__, str(e)[:80])
    return False

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

async def check(pairs):
    sys.stdout.reconfigure(encoding="utf-8")
    tmpdir = tempfile.mkdtemp(prefix="audprobe_")
    for text, rel in pairs:
        voice = ES_VOICE if rel.startswith("es/") else ZH_VOICE
        store = os.path.join(BASE, "audio", rel)
        tmp = os.path.join(tmpdir, os.path.basename(rel))
        ok = await synth(text, voice, tmp)
        if not ok:
            print("SYNTH-FAIL %-14s %r" % (rel, text)); continue
        same = md5(tmp) == md5(store)
        print("%-16s 文本=%-28r  %s  (存储%d字节/重合成%d字节)" % (
            rel, text, "MATCH" if same else "DIFF ", os.path.getsize(store), os.path.getsize(tmp)))
    shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == "__main__":
    items = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []
    asyncio.run(check([tuple(x) for x in items]))
