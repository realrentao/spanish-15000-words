# -*- coding: utf-8 -*-
"""Probe gid + sec structure for the three upcoming partes."""
import json, re, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bj=json.load(open(os.path.join(BASE,"data/book.json"),encoding="utf-8"))
for name in ("人的情绪","人类交流的方式","人与人之间的关系"):
    for idx,p in enumerate(bj["partes"]):
        if p.get("name")==name:
            print("FOUND book name=%r index=%d secs=%s"%(name,idx,
                [(s["no"],s.get("name",""),len(s.get("words",[])),len(s.get("sents",[])),len(s.get("extra",[]))) for s in p["secs"]]))
            break
    else:
        print("MISSING in book:", name)

import json as J
mt=open(os.path.join(BASE,"data/meta.js"),encoding="utf-8").read()
mi=mt.index("=")+1
m=J.loads(mt[mi:mt.index(";",mi)])
for g in m["grupos"]:
    for p in g["partes"]:
        if p.get("name") in ("人的情绪","人类交流的方式","人与人之间的关系"):
            print("meta gid=%d name=%r secs=%s"%(p["gid"],p.get("name"),
                [(s["no"],s.get("name",""),s.get("w"),s.get("s"),s.get("e")) for s in p["secs"]]))
