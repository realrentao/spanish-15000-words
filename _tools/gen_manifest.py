# -*- coding: utf-8 -*-
"""根据 _tools/audio_manifest.json 生成音频。
manifest 为 jobs 列表，每个 job 是元组 (es_text, es_path, zh_text, zh_path)，
缺项用 None。直接用 edge_tts.Communicate().save()，不调 ffmpeg/os.remove。
可断点续跑：已存在且 >500 字节的文件跳过。
"""
import asyncio, json, os, sys
import edge_tts

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(BASE, "audio")
PLAN = os.path.join(BASE, "_tools", "audio_manifest.json")
VOICE_ES = "es-ES-ElviraNeural"
VOICE_ZH = "zh-CN-XiaoxiaoNeural"
sem = asyncio.Semaphore(4)

async def gen_one(text, voice, out):
    for _ in range(4):
        try:
            await edge_tts.Communicate(text, voice).save(out)
            if os.path.getsize(out) > 500:
                return True
        except Exception:
            pass
    return False

async def worker(text, rel, voice, label):
    if not text:
        return True
    async with sem:
        out = os.path.join(AUD, rel)
        if os.path.exists(out) and os.path.getsize(out) > 500:
            return True
        ok = await gen_one(text, voice, out)
        print(f"{'OK ' if ok else 'FAIL'} [{label}] {rel}  {text[:40]}", flush=True)
        return ok

async def main():
    plan = json.load(open(PLAN, encoding="utf-8"))
    tasks = []
    for j in plan["jobs"]:
        if isinstance(j, dict):
            es_text, es_path, zh_text, zh_path = j.get("es"), j.get("esPath"), j.get("zh"), j.get("zhPath")
        else:
            es_text, es_path, zh_text, zh_path = j[0], j[1], j[2], j[3]
        if es_path:
            tasks.append(worker(es_text or "", es_path, VOICE_ES, "es"))
        if zh_path:
            tasks.append(worker(zh_text or "", zh_path, VOICE_ZH, "zh"))
    results = await asyncio.gather(*tasks)
    ok = sum(1 for r in results if r)
    print(f"\nDONE: {ok}/{len(results)} generated", flush=True)
    if ok != len(results):
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())
