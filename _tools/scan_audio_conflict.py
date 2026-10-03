# -*- coding: utf-8 -*-
"""扫描全站「同一音频路径被多个不同文本引用」的串号冲突。

- es 路径冲突 = 同一个 mp3 被多个不同**西语文本**引用 -> 至少一条西语配音串号
- zh 路径冲突 = 同一个 mp3 被多个不同**中文文本**引用 -> 至少一条中文配音串号
（同一西语词对应多个中文义项是正常的，所以 ES 侧必须按西语文本判定；
  同一中文词对应多个西语词也正常，所以 ZH 侧必须按中文文本判定。）
"""
import json, sys, glob, re, os
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
    return json.loads(t[i:j+1])

def scan():
    es = defaultdict(set); zh = defaultdict(set); pairs = {}   # path -> (es_text, zh_text)
    for sp in sorted(glob.glob(os.path.join(BASE, "data/sec/*.js")),
                     key=lambda p: int(re.search(r"(\d+)", os.path.basename(p)).group(1))):
        gid = int(re.search(r"(\d+)", os.path.basename(sp)).group(1))
        o = load(sp)
        for s in o["secs"]:
            for k in ("w", "e"):
                for r in s[k]:
                    pairs.setdefault(r[3], r[1]); pairs.setdefault(r[4], r[0])
                    es[r[3]].add(r[1]); zh[r[4]].add(r[0])
            for r in s["s"]:
                pairs.setdefault(r[3], r[0]); pairs.setdefault(r[4], r[1])
                es[r[3]].add(r[0]); zh[r[4]].add(r[1])
    return es, zh, pairs

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    es, zh, pairs = scan()
    ec = [(p, v) for p, v in es.items() if len(v) > 1]
    zc = [(p, v) for p, v in zh.items() if len(v) > 1]
    print("=== ES 路径冲突（同一 mp3 对应多个西语文本）: %d ===" % len(ec))
    for p, v in sorted(ec)[:20]:
        print("  ", p, sorted(v)[:4])
    print("=== ZH 路径冲突（同一 mp3 对应多个中文文本）: %d ===" % len(zc))
    for p, v in sorted(zc)[:20]:
        print("  ", p, sorted(v)[:4])
    print("=== 受影响行数 ===")
    for p, v in ec: pass
