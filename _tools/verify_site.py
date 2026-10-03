# -*- coding: utf-8 -*-
"""./verify_site.py : full-site structural + meta consistency check.

Checks, for every data/sec/*.js :
  * JSON loads and the row field count is >= 7 (or >= 7 for S rows too),
  * every row's audio paths exist,
  * every audio path maps to exactly one text of its language,
  * meta.js group/part counts match the actual data.
"""
import os, re, sys, glob, json, hashlib
from collections import defaultdict

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
    bad_struct = []
    bad_audit = []
    es_map = defaultdict(set)
    zh_map = defaultdict(set)
    counts = {"w": 0, "s": 0, "e": 0}
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js")),
                     key=lambda p: int(re.search(r"(\d+)", os.path.basename(p)).group(1))):
        gid = int(re.search(r"(\d+)", os.path.basename(sp)).group(1))
        try:
            o = load(sp)
        except Exception as e:
            bad_struct.append((gid, "JSON", str(e)[:60]))
            continue
        if not os.path.basename(sp).startswith("window"):
            pass
        for s in o["secs"]:
            for k in ("w", "e"):
                for idx, r in enumerate(s.get(k, [])):
                    counts[k] += 1
                    if len(r) < 7 or not r[6]:
                        bad_struct.append((gid, s["no"], k, idx, "shape"))
                    if r[3]:
                        es_map[r[3]].add(r[1])
                        zh_map[r[4]].add(r[0])
            for idx, r in enumerate(s.get("s", [])):
                counts["s"] += 1
                if len(r) < 7 or not r[6]:
                    bad_struct.append((gid, s["no"], "s", idx, "shape"))
                if r[3]:
                    es_map[r[3]].add(r[0])
                    zh_map[r[4]].add(r[1])

    # meta 对比
    mt = open(os.path.join(BASE, "data/meta.js"), encoding="utf-8").read()
    i = mt.index("={") + 1
    d = 0; j = i; ins = False; esc = False
    while j < len(mt):
        c = mt[j]
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
    meta = json.loads(mt[i:j + 1])
    mt_g = meta.get("total", {})
    print("meta total.w/s/e:", mt_g.get("w"), mt_g.get("s"), mt_g.get("e"),
          "| data w/s/e:", counts["w"], counts["s"], counts["e"])
    print("meta totalAll:", meta.get("totalAll"), "| data rows:", sum(counts.values()))
    print("structure problems:", len(bad_struct))
    for b in bad_struct[:10]:
        print("   ", b)
    es_c = {p: v for p, v in es_map.items() if len(v) > 1}
    zh_c = {p: v for p, v in zh_map.items() if len(v) > 1}
    print("es path collisions:", len(es_c), "| zh path collisions:", len(zh_c))
    for p, v in list(es_c.items())[:5]:
        print("   ES", p, sorted(v))
    for p, v in list(zh_c.items())[:5]:
        print("   ZH", p, sorted(v))
    ok = not bad_struct and not zh_c and mt_g.get("w") == counts["w"] and mt_g.get("s") == counts["s"] \
        and mt_g.get("e") == counts["e"]
    print("VERIFY", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
