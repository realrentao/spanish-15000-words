# -*- coding: utf-8 -*-
"""生成 missing_audio.json 中的缺失音频。
直接用 edge_tts.Communicate(...).save()（输出即 24k mono mp3），不调用 ffmpeg / os.remove，
避免 Windows 并发 Popen 的 OSError 与沙箱批量删除守卫。可断点续跑。"""
import asyncio, json, os, sys
import edge_tts

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(BASE, "audio")
PLAN = os.path.join(BASE, "_tools", "missing_audio.json")
VOICE_ES = "es-ES-ElviraNeural"
VOICE_ZH = "zh-CN-XiaoxiaoNeural"
sem = asyncio.Semaphore(4)

async def gen_one(text, voice, out):
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

async def worker(item, voice, label):
    async with sem:
        out = os.path.join(AUD, item["file"])
        if os.path.exists(out) and os.path.getsize(out) > 500:
            print(f"SKIP [{label}] {item['file']}", flush=True)
            return True
        ok = await gen_one(item["text"], voice, out)
        print(f"{'OK ' if ok else 'FAIL'} [{label}] {item['file']}  {item['text'][:36]}", flush=True)
        return ok

async def main():
    plan = json.load(open(PLAN, encoding="utf-8"))
    tasks = [worker(it, VOICE_ES, "es") for it in plan["es"]]
    tasks += [worker(it, VOICE_ZH, "zh") for it in plan["zh"]]
    results = await asyncio.gather(*tasks)
    ok = sum(1 for r in results if r)
    print(f"\nDONE: {ok}/{len(results)} generated", flush=True)
    if ok != len(results):
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())
