# -*- coding: utf-8 -*-
"""Plan the fix for Chinese-audio cross-references (same zh/*.mp3 serving
several different Chinese texts).

For every conflicting path we determine the authoritative owner by
re-synthesizing each candidate text with the Chinese voice and comparing md5.
Then every wrongly-pointing row is either
  * repointed to the path that already holds *its own* audio (no new file), or
  * given a brand new slot (needs one fresh synthesis).
Dry-run by default: pass --apply to actually edit data/sec/*.js.
"""
import os, re, sys, json, glob, hashlib, asyncio

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH_VOICE = "zh-CN-XiaoxiaoNeural"

sys.path.insert(0, os.path.join(BASE, "_tools"))


def load_sec(path):
    t = open(path, encoding="utf-8").read()
    i = t.index("={") + 1
    depth = 0; j = i; ins = False; esc = False
    while j < len(t):
        c = t[j]
        if ins:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0: break
        j += 1
    return json.loads(t[i:j+1])


def all_rows():
    """-> list of (gid, sec_no, kind, row) ; zh text = row[0], zh path = row[4]"""
    out = []
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js")),
                     key=lambda p: int(re.search(r"(\d+)", os.path.basename(p)).group(1))):
        gid = int(re.search(r"(\d+)", os.path.basename(sp)).group(1))
        o = load_sec(sp)
        for s in o["secs"]:
            for r in s.get("w", []): out.append((gid, s["no"], "w", r))      # [zh,es,pos,esA,zhA,py,ipa]
            for r in s.get("e", []): out.append((gid, s["no"], "e", r))
            for r in s.get("s", []): out.append((gid, s["no"], "s", r))      # [es,zh,...,esA,zhA,...]
    return out


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


async def synth_md5(text, tmpdir):
    from edge_tts import Communicate
    out = os.path.join(tmpdir, "probe.mp3")
    if os.path.exists(out):
        os.remove(out)
    try:
        await asyncio.wait_for(Communicate(text, ZH_VOICE).save(out), timeout=35)
        return hashlib.md5(open(out, "rb").read()).hexdigest()
    except Exception:
        return None


async def main(apply=False):
    rows = all_rows()
    rows = [(g, n, k, r) for (g, n, k, r) in rows if r[4]]      # has zh path
    from collections import defaultdict
    bypath = defaultdict(set)          # zh path -> {zh text}
    texts_paths = defaultdict(set)     # zh text -> {zh path}
    for g, n, k, r in rows:
        bypath[r[4]].add(r[0])
        texts_paths[r[0]].add(r[4])

    conflicts = {p: t for p, t in bypath.items() if len(t) > 1}
    print("涉及冲突路径: %d，涉及中文文本: %d" % (len(conflicts), sum(len(v) for v in conflicts.values())))

    need_repoint = 0     # 文本在别处已有自己的音频 -> 改引用
    need_new = 0         # 文本没有自己音频 -> 需新生成
    already_ok = 0
    owner_conflict = []  # 无法用 md5 判定归属

    tmp = os.path.join(BASE, "_tools", "_probe_tmp")
    os.makedirs(tmp, exist_ok=True)
    import tempfile
    td = tempfile.mkdtemp(dir=tmp)

    for p, texts in sorted(conflicts.items()):
        store = os.path.join(BASE, "audio", p)
        if not os.path.exists(store):
            continue
        sm = md5(store)
        owners = []
        for t in texts:
            h = await synth_md5(t, td)
            if h == sm:
                owners.append(t)
        if len(owners) == 1:
            owner = owners[0]
        else:
            # 唯一匹配不上：取首个（同时给出提示）
            owner = sorted(texts)[0]
            owner_conflict.append((p, sorted(texts), owners))
        for t in sorted(texts):
            if t == owner:
                continue
            own = [q for q in texts_paths[t] if q != p]
            if own:
                need_repoint += 1
            else:
                need_new += 1

    print("需要改引用(repoint): %d" % need_repoint)
    print("需要新生成音频:     %d" % need_new)
    print("判定存疑: %d" % len(owner_conflict))
    for c in owner_conflict[:8]:
        print("   ", c[0], c[1], "matches=", c[2])

    if apply:
        print("--apply 尚未实现，先跑 dry-run")
    return need_repoint, need_new


if __name__ == "__main__":
    asyncio.run(main(apply="--apply" in sys.argv))
