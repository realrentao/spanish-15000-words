# -*- coding: utf-8 -*-
"""./probe_one.py <es|zh> <path> ... : md5-verify stored audio against a fresh
synthesis of every text that references the path (and, optionally, print them)."""
import os, sys, asyncio, glob, json, hashlib, tempfile
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "_tools"))
from regen_es2 import synth, ES_VOICE  # 音色常量


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def rows_for(path):
    out = []
    for sp in glob.glob(os.path.join(BASE, "data/sec/*.js")):
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
        o = json.loads(t[i:j + 1])
        for s in o["secs"]:
            for k in ("w", "e"):
                for r in s.get(k, []):
                    if r[3] == path:
                        out.append((s["no"], k, r[1]))
            for r in s.get("s", []):
                if r[3] == path:
                    out.append((s["no"], "s", r[0]))
    return out


async def main():
    lang = sys.argv[1]
    paths = sys.argv[2:]
    td = tempfile.mkdtemp(dir=os.path.join(BASE, "_tools", "_regen_tmp"))
    for p in paths:
        fp = os.path.join(BASE, "audio", p)
        if not os.path.exists(fp):
            print("MISSING FILE", p)
            continue
        cur = md5(fp)
        rs = rows_for(p)
        for (no, k, tx) in rs:
            h = await synth(tx, td, ES_VOICE if lang == "es" else "zh-CN-XiaoxiaoNeural")
            print("%-14s sec%-4s %-2s %-28s cur=%s fresh=%s match=%s"
                  % (p, no, k, tx[:28], cur[:10], (h or "ERR")[:10], h == cur), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
