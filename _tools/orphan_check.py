# -*- coding: utf-8 -*-
import os, json, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(BASE, "data", "sec")
AUD = os.path.join(BASE, "audio")

# 1. 收集所有被引用的音频文件
ref = set()
for fn in sorted(os.listdir(SEC)):
    if not fn.endswith(".js"):
        continue
    with open(os.path.join(SEC, fn), encoding="utf-8") as f:
        raw = f.read()
    k = raw.index("=", raw.index("window.BOOK_DATA[")) + 1
    i = raw.index("{", k)
    obj = json.loads(raw[i:].rstrip().rstrip(";"))
    for sec in obj.get("secs", []):
        for row in sec.get("w", []):
            ref.add(row[3]); ref.add(row[4])
        for row in sec.get("s", []):
            ref.add(row[3]); ref.add(row[4])
        for row in sec.get("e", []):
            ref.add(row[3]); ref.add(row[4])

print("referenced audio files:", len(ref))

# 2. 候选孤儿范围（旧 数词（2）/（3） 使用过）
def check_range(sub, lo, hi):
    orphans = []
    for n in range(lo, hi + 1):
        f = "%s/%05d.mp3" % (sub, n)
        if os.path.exists(os.path.join(AUD, f)) and f not in ref:
            orphans.append(f)
    return orphans

es_orph = check_range("es", 83, 102)
zh_orph = check_range("zh", 82, 102)
print("\nES orphans (%d):" % len(es_orph))
print(" ", " ".join(es_orph))
print("\nZH orphans (%d):" % len(zh_orph))
print(" ", " ".join(zh_orph))

with open(os.path.join(BASE, "_tools", "orphans.json"), "w", encoding="utf-8") as f:
    json.dump({"es": es_orph, "zh": zh_orph}, f, ensure_ascii=False, indent=2)
