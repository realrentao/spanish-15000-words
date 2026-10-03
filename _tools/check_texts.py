# -*- coding: utf-8 -*-
"""./check_texts.py <text> [<text> ...] : find every row whose Chinese text (or
Spanish text with prefix es:) equals the argument and md5-verify the audio."""
import os, sys, glob, json, hashlib, tempfile, asyncio

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "_tools"))
from regen_es2 import synth, ES_VOICE   # synth() 支持两种音色
ZH = "zh-CN-XiaoxiaoNeural"


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load(sp):
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
    return json.loads(t[i:j + 1])


async def main():
    want = sys.argv[1:]
    hits = []
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js"))):
        o = load(sp)
        for s in o["secs"]:
            for k in ("w", "e"):
                for r in s.get(k, []):
                    if r[0] in want:
                        hits.append((os.path.basename(sp), s["no"], k, r[0], r[4]))
            for r in s.get("s", []):
                if r[1] in want:
                    hits.append((os.path.basename(sp), s["no"], "s", r[1], r[4]))
    print("rows found:", len(hits))
    td = tempfile.mkdtemp(dir=os.path.join(BASE, "_tools", "_regen_tmp"))
    for (sp, no, k, tx, p) in hits:
        h = await synth(tx, td, ZH)
        fp = os.path.join(BASE, "audio", p)
        cur = md5(fp) if os.path.exists(fp) else None
        print("  %s sec%-4s %-2s %-10s %-16s match=%s" %
              (sp, no, k, tx[:10], p, h == cur), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
