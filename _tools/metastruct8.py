# -*- coding: utf-8 -*-
import json
t = open("data/meta.js", encoding="utf-8").read()
i = t.index("=") + 1
j = t.rindex(";")
m = json.loads(t[i:j])
print("top keys:", list(m.keys()))
ps = m["partes"]
print("num partes:", len(ps))
print("parte0 keys:", list(ps[0].keys()))
print("parte0 sample sec:", ps[0]["secs"][0] if ps[0]["secs"] else None)
for p in ps:
    if p.get("gid") == 7 or p.get("name") == "在银行":
        print("FOUND parte gid=", p.get("gid"), "name=", p.get("name"), "secs=", len(p.get("secs", [])))
        for s in p.get("secs", []):
            print("  sec", s.get("no"), s.get("name"), "w/s/e=", s.get("w"), s.get("s"), s.get("e"))
print("totals:", m.get("total.w"), m.get("total.s"), m.get("total.e"), m.get("totalAll"))
