# -*- coding: utf-8 -*-
"""Fix Chinese-audio cross-references (the 'parrilla->烤架 plays 烧烤' bug).

A `zh/*.mp3` referenced by several *different* Chinese texts can hold only one
of them.  For every such path we

  1. identify the owner text:  re-synthesize every candidate text with
     zh-CN-XiaoxiaoNeural and md5-compare with the stored file (unique hit wins);
     if no unique hit -> fall back to the most frequently used text and
     re-synthesize that path from scratch;
  2. give every other row either the path that already contains *its own*
     audio, or a brand new slot (fresh synthesis).

Dry run by default; pass --apply to write audio + data/sec/*.js.
"""
import os, re, sys, json, glob, asyncio, hashlib, tempfile
from collections import defaultdict, Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "_tools"))
ZH_VOICE = "zh-CN-XiaoxiaoNeural"
CONC = int(os.environ.get("CONC", "3"))
APPLY = "--apply" in sys.argv


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def split_json(t):
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
    return t[:i], t[i:j + 1], t[j + 1:]


def load_sec(sp):
    pre, body, suf = split_json(open(sp, encoding="utf-8").read())
    return pre, json.loads(body), suf


def all_rows():
    """-> list of dict(gid,no,kind,idx,row,text,path,sp)"""
    out = []
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js")),
                     key=lambda p: int(re.search(r"(\d+)", os.path.basename(p)).group(1))):
        gid = int(re.search(r"(\d+)", os.path.basename(sp)).group(1))
        _, o, _ = load_sec(sp)
        for s in o["secs"]:
            for kind in ("w", "e"):
                for idx, r in enumerate(s.get(kind, [])):
                    out.append(dict(gid=gid, no=s["no"], kind=kind, idx=idx, row=r,
                                    text=r[0], path=r[4], sp=sp))
            for idx, r in enumerate(s.get("s", [])):
                out.append(dict(gid=gid, no=s["no"], kind="s", idx=idx, row=r,
                                text=r[1], path=r[4], sp=sp))
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
        await asyncio.sleep(1.0)
    return None


async def gen_file(text, relpath, sem):
    from edge_tts import Communicate
    out = os.path.join(BASE, "audio", relpath)
    os.makedirs(os.path.dirname(out), exist_ok=True)
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


def next_slot(sub):
    d = os.path.join(BASE, "audio", sub)
    mx = -1
    for f in os.listdir(d):
        m = re.match(r"^(\d+)\.mp3$", f)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


def main_sync():
    rows = [r for r in all_rows() if r["path"]]
    print("rows with zh audio: %d" % len(rows), flush=True)
    bypath = defaultdict(list)
    for r in rows:
        bypath[r["path"]].append(r)
    conflict = {p: rs for p, rs in bypath.items() if len({x["text"] for x in rs}) > 1}
    print("conflict paths: %d" % len(conflict), flush=True)
    return rows, bypath, conflict


async def main():
    rows, bypath, conflict = main_sync()
    td = tempfile.mkdtemp(dir=os.path.join(BASE, "_tools", "_probe_tmp"))
    os.makedirs(td, exist_ok=True)
    sem = asyncio.Semaphore(CONC)

    texts = sorted({t for p in conflict for t in {x["text"] for x in bypath[p]}})
    print("candidate texts: %d" % len(texts), flush=True)
    hcache = {}

    async def one(t):
        if t in hcache:
            return
        async with sem:
            hcache[t] = await synth(t, td)
    await asyncio.gather(*[one(t) for t in texts])
    print("synth done, usable=%d" % sum(1 for v in hcache.values() if v), flush=True)

    owners = {}
    for p, rs in conflict.items():
        fp = os.path.join(BASE, "audio", p)
        sm = md5(fp) if os.path.exists(fp) else None
        hits = [t for t in {x["text"] for x in rs} if hcache.get(t) and hcache[t] == sm]
        cnt = Counter(x["text"] for x in rs)
        if len(hits) == 1:
            owners[p] = (hits[0], False)
        else:
            own = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            owners[p] = (own, True)

    need_regen = [p for p, (t, rg) in owners.items() if rg]
    print("paths needing re-synthesis: %d" % len(need_regen), flush=True)

    for p, rs in conflict.items():
        own, rg = owners[p]
        for r in rs:
            if r["text"] == own:
                r["new_path"] = p if not rg else "__REGEN__"
                continue
            cand = [q for q in {x["path"] for x in bypath.get(r["text"], [])} if q != p]
            tgt = None
            for q in cand:
                fp = os.path.join(BASE, "audio", q)
                if os.path.exists(fp) and hcache.get(r["text"]) and md5(fp) == hcache[r["text"]]:
                    tgt = q
                    break
            r["new_path"] = tgt if tgt else "__NEW__"

    n_re = sum(1 for r in rows if r.get("new_path") == "__REGEN__")
    n_nw = sum(1 for r in rows if r.get("new_path") == "__NEW__")
    n_rp = sum(1 for r in rows if r.get("new_path") and r["new_path"] not in ("__NEW__", "__REGEN__")
               and r["new_path"] != r["path"])
    n_keep = sum(1 for r in rows if r.get("new_path") == r["path"])
    print("rows: keep=%d repoint=%d new=%d regen=%d" % (n_keep, n_rp, n_nw, n_re), flush=True)
    for r in [x for x in rows if x.get("new_path") in ("__NEW__", "__REGEN__")][:10]:
        print("   ", r["gid"], r["no"], r["kind"], r["idx"], r["text"][:20], r["new_path"], flush=True)

    if not APPLY:
        return

    fresh = next_slot("zh")
    jobs = []
    for r in rows:
        if r.get("new_path") == "__NEW__":
            r["new_path"] = "zh/%05d.mp3" % fresh
            fresh += 1
            jobs.append((r["text"], r["new_path"]))
    for p, (t, rg) in owners.items():
        if rg:
            jobs.append((t, p))
    print("to synthesize: %d (new=%d, regen=%d)" % (len(jobs), len(jobs) - len(need_regen), len(need_regen)), flush=True)
    gsem = asyncio.Semaphore(CONC)
    ok = 0
    for i, (t, pth) in enumerate(jobs):
        if await gen_file(t, pth, gsem):
            ok += 1
        if (i + 1) % 25 == 0:
            print("   gen %d/%d (%d ok)" % (i + 1, len(jobs), ok), flush=True)
    print("generated ok=%d/%d" % (ok, len(jobs)), flush=True)

    per_file = defaultdict(list)
    for r in rows:
        if r.get("new_path") and r["new_path"] not in ("__NEW__", "__REGEN__") and r["new_path"] != r["path"]:
            per_file[r["sp"]].append(r)
    for sp, rs in per_file.items():
        t = open(sp, encoding="utf-8").read()
        pre, body, suf = split_json(t)
        obj = json.loads(body)
        n = 0
        for r in rs:
            for s in obj["secs"]:
                if s["no"] != r["no"]:
                    continue
                s.setdefault(r["kind"], [])[r["idx"]][4] = r["new_path"]
                n += 1
                break
        open(sp, "w", encoding="utf-8").write(
            pre + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + suf)
        print("   wrote %s (%d rows)" % (os.path.basename(sp), n), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
