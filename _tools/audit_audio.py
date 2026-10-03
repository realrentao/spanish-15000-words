# -*- coding: utf-8 -*-
"""全站音频「错音」校验器（可断点续跑）。

原理：edge-tts 对同一 (文本, 音色) 的输出是**确定性**的（已实测验证：
es/04629.mp3 parrilla 与三个月前生成的字节完全一致）。
所以把每条引用按当前文本 + 正确音色重新合成一次，与磁盘 mp3 比对 md5：
- 一致 -> 该音频确实由这条文本生成
- 不一致 -> 磁盘上的是别的文本（串号/陈旧），或音色用错
  （历史 bug 典型：西语路径里灌进了中文音色）

输出 _tools/audit_result.json：
  ok    : {path: [text,...]}
  bad   : {path: [text,...]}  该路径上所有引用文本都**不匹配**（音像确定性地不对）
  mixed : {path: {"text":owner_text, "other":[text,...]}} 只有部分文本匹配
          -> 匹配的那条是「主人」，其余引用该路径的行都要换新路径
"""
import os, re, sys, glob, json, asyncio, hashlib, tempfile, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ES_VOICE = "es-ES-ElviraNeural"
ZH_VOICE = "zh-CN-XiaoxiaoNeural"
RES = os.path.join(BASE, "_tools", "audit_result.json")

def load_sec(path):
    t = open(path, encoding="utf-8").read()
    i = t.index("={") + 1
    d = 0; j = i; ins = False; esc = False
    while j < len(t):
        c = t[j]
        if ins:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == "{": d += 1
            elif c == "}':
                d -= 1
                if d == 0: break
        j += 1
    return json.loads(t[i:j+1])

def collect_rows():
    """[(gid, secno, kind, es_text, zh_text, es_path, zh_path)]"""
    rows = []
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js")),
                     key=lambda p: int(re.search(r"(\d+)", os.path.basename(p)).group(1))):
        gid = int(re.search(r"(\d+)", os.path.basename(sp)).group(1))
        o = load_sec(sp)
        for s in o["secs"]:
            for k in ("w", "e"):
                for r in s.get(k, []):
                    rows.append((gid, s["no"], k, r[0], r[1], r[3], r[4]))
            for r in s.get("s", []):
                rows.append((gid, s["no"], "s", r[0], r[1], r[3], r[4]))
    return rows

def refs_of(rows):
    """{path: sorted(set(text))} 按 lang 分组"""
    es, zh = {}, {}
    for (_g, _n, _k, a, b, ep, zp) in rows:
        if ep: es.setdefault(ep, set()).add(a)
        if zp: zh.setdefault(zp, set()).add(b)
    return es, zh

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

async def synth(text, voice, out, tries=3):
    from edge_tts import Communicate
    for _ in range(tries):
        try:
            await asyncio.wait_for(Communicate(text, voice).save(out), timeout=40)
            if os.path.getsize(out) > 200:
                return True
        except Exception:
            pass
    return False

async def verify_one(sem, tmpdir, path, texts, tq):
    async with sem:
        store = os.path.join(BASE, "audio", path)
        if not os.path.exists(store):
            return path, None, list(texts)      # 文件根本不存在
        sm = md5(store)
        voice = ES_VOICE if path.startswith("es/") else ZH_VOICE
        for t in texts:
            if tq.get(t):
                cand = tq[t]
            else:
                out = os.path.join(tmpdir, "p%d.mp3" % (hash(t) & 0xffffff))
                tq[t] = out
                ok = await synth(t, voice, out)
                if not ok:
                    continue
            if md5(tq[t]) == sm:
                return path, t, None
        return path, None, list(texts)

async def run(langs=("es", "zh")):
    sys.stdout.reconfigure(encoding="utf-8")
    rows = collect_rows()
    es_r, zh_r = refs_of(rows)
    targets = {}
    if "es" in langs: targets.update(es_r)
    if "zh" in langs: targets.update(zh_r)
    print("待校验路径 %d（西语 %d / 中文 %d），引用行 %d" % (len(targets), len(es_r), len(zh_r), len(rows)), flush=True)

    prev = {}
    if os.path.exists(RES):
        try: prev = json.load(open(RES, encoding="utf-8"))
        except Exception: prev = {}
    done = set(prev.get("_done", []))
    todo = [p for p in sorted(targets) if p not in done]
    print("断点续跑：已完成 %d，剩余 %d" % (len(done), len(todo)), flush=True)

    tmpdir = tempfile.mkdtemp(prefix="auditchk_")
    tq = {}
    sem = asyncio.Semaphore(10)
    results = {}
    t0 = time.time()
    for i in range(0, len(todo), 120):
        batch = todo[i:i+120]
        out = await asyncio.gather(*[verify_one(sem, tmpdir, p, sorted(targets[p]), tq) for p in batch])
        for path, owner, wrong in out:
            results[path] = {"owner": owner, "wrong": wrong}
        print("  %d/%d  用时 %.0fs" % (min(i+120, len(todo)), len(todo), time.time()-t0), flush=True)
    res = {"_done": sorted(set(done) | set(targets)), **results}
    for p, v in prev.items():
        if p not in res: res[p] = v
    json.dump(res, open(RES, "w", encoding="utf-8"), ensure_ascii=False)
    ok = sum(1 for v in res.values() if not isinstance(v, dict) or v["owner"])
    mixed = [p for p, v in res.items() if isinstance(v, dict) and v["owner"] and v["wrong"]]
    bad = [p for p, v in res.items() if isinstance(v, dict) and not v["owner"]]
    print("完成：ok=%d  mixed(部分文本不匹配)=%d  bad(全不匹配)=%d  用时%.0fs" % (ok, len(mixed), len(bad), time.time()-t0))
    return res

if __name__ == "__main__":
    langs = tuple(a for a in sys.argv[1:] if a in ("es", "zh")) or ("es", "zh")
    asyncio.run(run(langs))
