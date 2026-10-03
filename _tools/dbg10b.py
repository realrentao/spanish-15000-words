import sys; sys.path.insert(0,"_tools")
import build_parte10 as B
secs=B.parse_raw()
rs=secs[4]
print("sec4 name:", rs["name"])
print("sec4 s count:", len(rs["s"]))
for x in rs["s"]:
    print("  S:", x[:80])
print("----- raw sec4 block (lines) -----")
txt=open("_tools/parte10_raw.txt",encoding="utf-8").read()
import re
idx=txt.find("### Sección 4")
blk=txt[idx:txt.find("### Sección", idx+10)]
for ln in blk.split("\n"):
    if "例" in ln or "经典实用句" in ln:
        print("LINE:", repr(ln))
