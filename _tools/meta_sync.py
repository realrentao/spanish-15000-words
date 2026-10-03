# -*- coding: utf-8 -*-
"""./meta_sync.py [--apply]

Compare data/meta.js counts with the actual data/sec/*.js content and, with
--apply, rewrite every numeric field (per-section w/s/e, per-part total,
global total / total.w / total.s / total.e) while preserving all text fields.
"""
import os, re, sys, glob, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLY = "--apply" in sys.argv


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


def data_counts():
    """-> {(gid, sec_no): (w, s, e)}"""
    out = {}
    for sp in glob.glob(os.path.join(BASE, "data/sec/*.js")):
        gid = int(re.search(r"(\d+)", os.path.basename(sp)).group(1))
        o = load(sp)
        for s in o["secs"]:
            out[(gid, s["no"])] = (len(s.get("w", [])), len(s.get("s", [])), len(s.get("e", [])))
    return out


def main():
    dc = data_counts()
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
    pre, meta, suf = mt[:i], json.loads(mt[i:j + 1]), mt[j + 1:]
    mtsec = {}     # (gid,no) -> [w,s,e]
    mtpart = {}    # gid -> [w,s,e]
    bad = 0
    data_secs = {k for k in dc}
    meta_secs = {(p["gid"], s["no"]) for g in meta["grupos"] for p in g["partes"] for s in p["secs"]}
    print("data secs:", len(data_secs), "meta secs:", len(meta_secs))
    if data_secs - meta_secs:
        print("data-not-meta:", sorted(data_secs - meta_secs)[:20])
    if meta_secs - data_secs:
        print("meta-not-data:", sorted(meta_secs - data_secs)[:20])
    # 把数据里有、meta 里没有的小节补进去
    sec_names = {(gid, s["no"]): s.get("name", "") for sp_ in
                 glob.glob(os.path.join(BASE, "data/sec/*.js")) if False}
    for sp_ in glob.glob(os.path.join(BASE, "data/sec/*.js")):
        gid_ = int(re.search(r"(\d+)", os.path.basename(sp_)).group(1))
        for s in load(sp_)["secs"]:
            sec_names[(gid_, s["no"])] = s.get("name", "")
    added = 0
    for g in meta["grupos"]:
        for p in g["partes"]:
            have = {s["no"] for s in p["secs"]}
            for (gid_, no_), (w, s_, e_) in sorted(dc.items()):
                if gid_ != p["gid"] or no_ in have:
                    continue
                p["secs"].append({"no": no_, "name": sec_names.get((gid_, no_), ""),
                                  "w": w, "s": s_, "e": e_})
                p["secs"].sort(key=lambda x: x["no"])
                have.add(no_)
                added += 1
                print("  + added sec", p["gid"], no_, sec_names.get((gid_, no_)))
    print("secs added to meta:", added)
    for g in meta["grupos"]:
        for p in g["partes"]:
            gid = p["gid"]
            agg = [0, 0, 0]
            for s in p["secs"]:
                key = (gid, s["no"])
                s["w"] = dc.get(key, (0, 0, 0))[0]
                s["s"] = dc.get(key, (0, 0, 0))[1]
                s["e"] = dc.get(key, (0, 0, 0))[2]
                mtsec[key] = [s["w"], s["s"], s["e"]]
                if (gid, s["no"]) not in dc:
                    print("  !! sec not in data:", key)
                agg[0] += s["w"]; agg[1] += s["s"]; agg[2] += s["e"]
            if p.get("total") != sum(agg):
                bad += 1
                print("  !! parte %d total %s != %s" % (gid, p.get("total"), sum(agg)))
            mtpart[gid] = agg
            p["total"] = sum(agg)
    tw = sum(v[0] for v in mtpart.values())
    ts = sum(v[1] for v in mtpart.values())
    te = sum(v[2] for v in mtpart.values())
    print("computed totals: w=%d s=%d e=%d all=%d" % (tw, ts, te, tw + ts + te))
    print("current  totals: w=%s s=%s e=%s all=%s" % (
        meta["total"]["w"], meta["total"]["s"], meta["total"]["e"], meta["totalAll"]))
    print("partes with wrong total:", bad)
    if not APPLY:
        print("(dry run; use --apply to write)")
        return
    meta["total"] = {"w": tw, "s": ts, "e": te}
    meta["totalAll"] = tw + ts + te
    open(os.path.join(BASE, "data/meta.js"), "w", encoding="utf-8").write(
        pre + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + suf)
    print("meta.js rewritten")


if __name__ == "__main__":
    main()
