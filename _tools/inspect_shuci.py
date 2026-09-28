# -*- coding: utf-8 -*-
import re, json, sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fpath = os.path.join(BASE, "data", "sec", "0.js")

with open(fpath, encoding="utf-8") as f:
    raw = f.read()

# extract JSON after 'window.BOOK_DATA[0]='
marker = "window.BOOK_DATA[0]="
j = raw.index(marker) + len(marker)
i = raw.index("{", j)
obj = json.loads(raw[i:].rstrip().rstrip(";"))

secs = obj["secs"]
print("gid=%s nombre=%s  total secs=%d" % (obj.get("gid"), obj.get("name"), len(secs)))
for idx, s in enumerate(secs):
    nm = s.get("name", "")
    if "数词" in nm:
        w = s.get("w", [])
        ss = s.get("s", [])
        e = s.get("e", [])
        print("\n=== SEC idx=%d  no=%s  name=%s  w=%d s=%d e=%d ===" % (idx, s.get("no"), nm, len(w), len(ss), len(e)))
        print("  -- w (终极分类词) --")
        for row in w:
            print("   ", row)
        print("  -- s (经典实用句) --")
        for row in ss:
            print("   ", row)
        print("  -- e (词汇大拓展) --")
        for row in e:
            print("   ", row)
