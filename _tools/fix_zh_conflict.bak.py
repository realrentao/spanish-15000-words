# -*- coding: utf-8 -*-
"""Fix Chinese-audio cross-references (the 'parrilla->烤架 plays 烧烤' bug).

A `zh/*.mp3` that is referenced by several *different* Chinese texts can only
hold one of them.  For every such path we re-synthesize all candidate texts
with zh-CN-XiaoxiaoNeural, md5-compare against the stored file and identify the
legitimate owner.  Every other row is then

  * repointed to the path that already contains *its own* audio, or
  * given a brand-new slot (fresh synthesis).

Dry run by default; pass --apply to rewrite data/sec/*.js.
"""
import os, re, sys, json, glob, asyncio, time, hashlib, tempfile
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "_tools"))
ZH_VOICE = "zh-CN-XiaoxiaoNeural"
CONC = 2
APPLY = "--apply" in sys.argv
PROGRESS = os.path.join(BASE, "_tools/_zhfix_progress.json")


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load_sec(sp):
    t = open(sp, encoding="utf-8").read()
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
            elif c == "}":
                d -= 1
                if d == 0: break
        j += 1
    return t[:i], json.loads(t[i:j+1]), t[j+1:]


def dump_sec(obj):
    # 与既有约定一致：紧凑 JSON
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def all_rows():
    """-> (gid, sec_no, kind, row, secfile) ; zh text = row[0], zh path = row[4]"""
    out = []
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js")),
                     key=lambda p: int(re.search(r"(\d+)", os.path.basename(p)).group(1))):
        gid = int(re.search(r"(\d+)", os.path.basename(sp)).group(1))
        pre, o, suf = load_sec(sp)
        for s in o["secs"]:
            for kind in ("w", "e", "s"):
                for idx, r in enumerate(s.get(kind, [])):
                    out.append(dict(gid=gid, no=s["no"], kind=kind, idx=idx, row=r,
                                    sec=s, sp=sp, pre=pre, suf=suf))
    return out


async def synth(text, td, voice=ZH_VOICE):
    from edge_tts import Communicate
    out = os.path.join(td, "p.mp3")
    for attempt in range(5):
        try:
            await asyncio.wait_for(Communicate(text, voice).save(out), timeout=40)
            if os.path.exists(out) and os.path.getsize(out) > 100:
                return md5(out)
        except Exception as e:
            msg = str(e)
            if "429" in msg or "Too Many" in msg:
                await asyncio.sleep(5 + 4 * attempt)
                continue
        await asyncio.sleep(1.2)
    return None


async def synth_many(texts, td, sem):
    hcache = {}
    async def one(t):
        if t in hcache:
            return t, hcache[t]
        async with sem:
            h = await synth(t, td)
        hcache[t] = h
        return t, h
    res = await asyncio.gather(*[one(t) for t in texts])
    return hcache


def next_zh_slot():
    d = os.path.join(BASE, "audio", "zh")
    mx = -1
    for f in os.listdir(d):
        m = re.match(r"^(\d+)\.mp3$", f)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


async def gen_file(text, relpath, sem):
    from edge_tts import Communicate
    out = os.path.join(BASE, "audio", relpath)
    async with sem:
        for attempt in range(5):
            try:
                await asyncio.wait_for(Communicate(text, ZH_VOICE).save(out), timeout=40)
                if os.path.exists(out) and os.path.getsize(out) > 100:
                    return True
            except Exception as e:
                msg = str(e)
                if "429" in msg or "Too Many" in msg:
                    await asyncio.sleep(5 + 4 * attempt)
                    continue
            await asyncio.sleep(1.2)
    return False


async def main():
    rows = all_rows()
    rows = [r for r in rows if r["row"][4]]           # 有中音频路径
    print("rows with zh audio: %d" % len(rows), flush=True)

    bypath = defaultdict(list)
    for r in rows:
        bypath[r["row"][4]].append(r)

    conflict = {p: rs for p, rs in bypath.items() if len({x["row"][0] for x in rs}) > 1}
    print("conflict paths: %d" % len(conflict), flush=True)

    td = tempfile.mkdtemp(dir=os.path.join(BASE, "_tools", "_probe_tmp"))
    os.makedirs(td, exist_ok=True)
    sem = asyncio.Semaphore(CONC)

    # 1) 判定每条冲突路径的归属文本（md5）
    store_md5 = {p: (md5(os.path.join(BASE, "audio", p)) if os.path.exists(os.path.join(BASE, "audio", p)) else None)
                 for p in conflict}
    texts_needed = sorted({t for p in conflict for t in {x["row"][0] for x in bypath[p]}})
    print("candidate texts to synthesize: %d" % len(texts_needed), flush=True)
    hcache = await synth_many(texts_needed, td, sem)
    owner = {}
    for p in conflict:
        texts = sorted({x["row"][0] for x in bypath[p]})
        hits = [t for t in texts if hcache.get(t) and hcache[t] == store_md5.get(p)]
        owner[p] = hits[0] if len(hits) == 1 else None

    none_owner = [p for p, o in owner.items() if o is None]
    print("paths with NO unique owner: %d" % len(none_owner), flush=True)
    for p in none_owner[:10]:
        print("    ", p, sorted({x["row"][0] for x in bypath[p]}),
              "stored=", store_md5[p],
              "cache=", [hcache.get(t) for t in sorted({x["row"][0] for x in bypath[p]})], flush=True)

    # 2) 为每条「非归属行」找自己的音频
    fixes = []          # (row, new_path)
    new_audio = []      # (text, path)
    todo = []
    for p, rs in conflict.items():
        own = owner[p]
        for r in rs:
            if r["row"][0] == own:
                continue
            todo.append((r, p))

    used = set()
    for r, bad_path in todo:
        t = r["row"][0]
        cand = [q for q in {x["row"][4] for x in bypath.get(t, [])} if q != bad_path]
        target = None
        for q in cand:
            if q in used:
                continue
            fp = os.path.join(BASE, "audio", q)
            if os.path.exists(fp) and hcache.get(t) and md5(fp) == hcache[t]:
                target = q
                break
        if target is None:
            target = None
            # 需要新分配
            fixes.append((r, "__NEW__", t))
            used.add(bad_path)
        else:
            fixes.append((r, target, t))
            used.add(target)

    print("rows to repoint: %d" % sum(1 for f in fixes if f[1] != "__NEW__"), flush=True)
    print("rows needing new audio: %d" % sum(1 for f in fixes if f[1] == "__NEW__"), flush=True)

    if not APPLY:
        for r, p, t in fixes[:15]:
            print("   ", r["gid"], r["no"], r["kind"], r["idx"], t[:18], "->", p, flush=True)
        return

    # 3) 生成缺失音频（先占位分配路径）
    slot = next_zh_slot()
    for (r, p, t) in fixes:
        if p == "__NEW__":
            r["new_path"] = "zh/%05d.mp3" % slot
            slot += 1
        else:
            r["new_path"] = p
    todo_gen = [(r["row"][0], r["new_path"]) for (r, p, t) in fixes if p == "__NEW__"]
    print("next zh slot: %d ; generating %d files" % (slot, len(todo_gen)), flush=True)
    okc = 0
    for i, (t, p) in enumerate(todo_gen):
        if await gen_file(t, p, asyncio.Semaphore(CONC)):
            okc += 1
            slot += 1
        if (i + 1) % 25 == 0:
            print("   generated %d/%d" % (i + 1, len(todo_gen)), flush=True)
    print("new audio generated: %d/%d" % (okc, len(todo_gen)), flush=True)

    # 4) 回写 sec/*.js
    per_file = defaultdict(list)
    for (r, p, t) in fixes:
        per_file[r["sp"]].append(r["row"])
    for sp, rs in per_file.items():
        t = open(sp, encoding="utf-8").read()
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
                elif c == "}":
                    d -= 1
                    if d == 0: break
            j += 1
        pre, obj, suf = t[:i], json.loads(t[i:j+1]), t[j+1:]
        n = 0
        for r in rs:
            for s in obj["secs"]:
                if s["no"] != r["no"]:
                    continue
                s.setdefault(r["kind"], [])[r["idx"]][4] = r["new_path"]
                n += 1
                break
        open(sp, "w", encoding="utf-8").write(pre + dump_sec(obj) + suf)
        print("   wrote %s (%d rows updated)" % (os.path.basename(sp), n), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
