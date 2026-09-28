# -*- coding: utf-8 -*-
import json, os, glob, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# full missing-audio check across all sec files
refs = set()
for f in glob.glob(os.path.join(BASE, "data/sec/*.js")):
    t = open(f, encoding="utf-8").read()
    for m in re.findall(r'"(?:es|zh)/\d{5}\.mp3"', t):
        refs.add(m.strip('"'))
missing = [r for r in refs if not os.path.exists(os.path.join(BASE, "audio", r))]
print("total audio refs (all secs):", len(refs))
print("MISSING:", len(missing))
for m in missing[:40]:
    print("  ", m)

# prefix check sec/1.js
t1 = open(os.path.join(BASE, "data/sec/1.js"), encoding="utf-8").read()
print("sec/1.js prefix OK:", t1.startswith(
    "window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[1]="))

# global count of audio files
es = len(glob.glob(os.path.join(BASE, "audio/es/*.mp3")))
zh = len(glob.glob(os.path.join(BASE, "audio/zh/*.mp3")))
print("audio files on disk: es=%d zh=%d" % (es, zh))
