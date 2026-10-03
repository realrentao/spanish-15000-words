# -*- coding: utf-8 -*-
"""List every audio path referenced in data/sec/*.js that does not exist."""
import os, glob, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def main():
    miss = []
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js"))):
        o = load(sp)
        for s in o["secs"]:
            for k in ("w", "e", "s"):
                for r in s.get(k, []):
                    for idx in (3, 4):
                        p = r[idx]
                        if p and not os.path.exists(os.path.join(BASE, "audio", p)):
                            miss.append((os.path.basename(sp), s["no"], k, idx, p))
    print("missing:", len(miss))
    for m in miss[:20]:
        print("  ", m)
    # 同时列出「孤儿」音频：存在但无人引用
    used = set()
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js"))):
        o = load(sp)
        for s in o["secs"]:
            for k in ("w", "e", "s"):
                for r in s.get(k, []):
                    for idx in (3, 4):
                        if r[idx]:
                            used.add(r[idx])
    orph = []
    for sub in ("es", "zh"):
        d = os.path.join(BASE, "audio", sub)
        for f in os.listdir(d):
            p = "%s/%s" % (sub, f)
            if p not in used:
                orph.append(p)
    print("orphan audio files:", len(orph))
    for p in orph[:10]:
        print("  ", p)


if __name__ == "__main__":
    main()
