# -*- coding: utf-8 -*-
"""Fix Spanish-audio cross-references (same es/*.mp3 serving several *different*
Spanish texts).  Only handled when the md5 test finds exactly one owner, so
trivial pairs (case / trailing dot that synthesize identically) are left alone.

Dry run by default; pass --apply to rewrite data/sec/*.js.
"""
import os, re, sys, json, glob, asyncio, tempfile
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "_tools"))
ES_VOICE = "es-ES-ElviraNeural"
CONC = 3
APPLY = "--apply" in sys.argv


def md5(p):
    import hashlib
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
    return json.loads(t[i:j+1])


def all_rows():
    out = []
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js")),
                     key=lambda p: int(re.search(r"(\d+)", os.path.basename(p)).group(1))):
        gid = int(re.search(r"(\d+)", os.path.basename(sp)).group(1))
        o = load_sec(sp)
        for s in o["secs"]:
            for kind in ("w", "e"):
                for idx, r in enumerate(s.get(kind, [])):
                    out.append([s, kind, idx, r[1], r[3], sp])     # es text, es path
            for idx, r in enumerate(s.get("s", [])):
                out.append([s, "s", idx, r[0], r[3], sp])
    return out


async def synth(text, td, voice=ES_VOICE):
    from edge_tts import Communicate
    out = os.path.join(td, "p.mp3")
    for attempt in range(4):
        try:
            await asyncio.wait_for(Communicate(text, voice).save(out), timeout=40)
            if os.path.exists(out) and os.path.getsize(out) > 100:
                return md5(out)
        except Exception as e:
            msg = str(e)
            if "429" in msg:
                await asyncio.sleep(5 + 4 * attempt)
                continue
        await asyncio.sleep(1.0)
    return None


async def gen_file(text, relpath, sem):
    from edge_tts import Communicate
    out = os.path.join(BASE, "audio", relpath)
    async with sem:
        for attempt in range(4):
            try:
                await asyncio.wait_for(Communicate(text, ES_VOICE).save(out), timeout=40)
                if os.path.exists(out) and os.path.getsize(out) > 100:
                    return True
            except Exception as e:
                msg = str(e)
                if "429" in msg:
                    await asyncio.sleep(5 + 4 * attempt)
                    continue
            await asyncio.sleep(1.0)
    return False


def next_es_slot():
    d = os.path.join(BASE, "audio", "es")
    mx = -1
    for f in os.listdir(d):
        m = re.match(r"^(\d+)\.mp3$", f)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


async def main():
    rows = all_rows()
    bypath = defaultdict(list)
    for r in rows:
        if r[4]:
            bypath[r[4]].append(r)
    conflict = {p: rs for p, rs in bypath.items() if len({x[3] for x in rs}) > 1}
    print("es conflict paths:", len(conflict), flush=True)

    td = tempfile.mkdtemp(dir=os.path.join(BASE, "_tools", "_probe_tmp"))
    os.makedirs(td, exist_ok=True)
    sem = asyncio.Semaphore(CONC)

    texts = sorted({t for p in conflict for t in {x[3] for x in bypath[p]}})
    hcache = {}
    async def one(t):
        if t in hcache: return
        async with sem:
            hcache[t] = await synth(t, td)
    await asyncio.gather(*[one(t) for t in texts])
    print("synthesized:", len(texts), "non-empty:", sum(1 for v in hcache.values() if v), flush=True)

    fixes = []
    unresolved = []
    for p, rs in conflict.items():
        sm = md5(os.path.join(BASE, "audio", p)) if os.path.exists(os.path.join(BASE, "audio", p)) else None
        hits = [t for t in {x[3] for x in rs} if hcache.get(t) and hcache[t] == sm]
        if len(hits) != 1:
            unresolved.append((p, sorted({x[3] for x in rs}), hits))
            continue
        own = hits[0]
        def norm(x):
            return x.rstrip(".!?；; ").casefold()
        for r in rs:
            if r[3] != own and norm(r[3]) != norm(own):
                fixes.append((r, p, own))

    print("unresolved:", len(unresolved))
    for p, ts, hits in unresolved[:6]:
        print("   ", p, ts, hits, flush=True)
    print("rows to fix:", len(fixes), flush=True)
    for r, p, own in fixes[:12]:
        print("   ", r[3][:30], "->", p, "(owner:%s)" % own[:30], flush=True)

    if not APPLY or not fixes:
        return

    slot = next_es_slot()
    # 分配新路径
    for r, p, own in fixes:
        t = r[3]
        target = None
        for q in {x[4] for x in bypath.get(t, [])} - {p}:
            fp = os.path.join(BASE, "audio", q)
            if os.path.exists(fp) and hcache.get(t) and md5(fp) == hcache[t]:
                target = q
                break
        if target is None:
            target = "es/%05d.mp3" % slot
            slot += 1
        r.append(target)   # r = [sec, kind, idx, text, oldpath, newpath]
    todo = [(r[3], r[4]) for (r, p, own) in fixes if r[4].startswith("es/")]
    print("new es audio:", len(todo), flush=True)
    ok = 0
    for i, (t, pth) in enumerate(todo):
        if await gen_file(t, pth, asyncio.Semaphore(CONC)):
            ok += 1
        if (i + 1) % 25 == 0:
            print("   gen %d/%d" % (i + 1, len(todo)), flush=True)
    print("generated:", ok, "/", len(todo), flush=True)

    per_file = defaultdict(list)
    for (r, p, own) in fixes:
        per_file[r[5]].append(list(r))
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
                if s["no"] != r[0]["no"]:
                    continue
                s.setdefault(r[1], [])[r[2]][3] = r[5]
                n += 1
                break
        open(sp, "w", encoding="utf-8").write(
            pre + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + suf)
        print("   wrote %s (%d rows)" % (os.path.basename(sp), n), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
