# -*- coding: utf-8 -*-
"""gid13 人的情绪 更新后校验：前缀 / 每行字段数 / 西语里不能混中文 / 音频文件必须存在。"""
import json, os, re, sys

GIDS = [int(x) for x in (sys.argv[1:] or ["13"])]
bad, refs, missing, nrows = [], 0, [], 0
for gid in GIDS:
    p = "data/sec/%d.js" % gid
    t = open(p, encoding="utf-8").read()
    if not t.startswith("window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=" % gid):
        bad.append(("PREFIX", p))
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
    obj = json.loads(t[i:j + 1])
    for s in obj["secs"]:
        for kind in ("w", "e", "s"):
            for r in s.get(kind, []):
                nrows += 1
                if len(r) != 7:
                    bad.append(("FIELDS", p, kind, r[:2]))
                # 西语段：S 行在 r[0]，W/E 行在 r[1]
                f = r[0] if kind == "s" else r[1]
                if re.search(r"[\u4e00-\u9fff]", f):
                    bad.append(("CJK", p, kind, f))
                for f in (r[3], r[4]):
                    if f:
                        refs += 1
                        if not os.path.exists(os.path.join("audio", f)):
                            missing.append(f)
                    else:
                        bad.append(("NOAUDIO", p, kind, r[:2]))

print("rows:", nrows, "| audio refs checked:", refs)
if bad:
    print("BAD:", bad[:8], "count", len(bad))
if missing:
    print("MISSING AUDIO:", missing[:8], "count", len(missing))
print("VERIFY:", "OK" if not bad and not missing else "FAIL")
