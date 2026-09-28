# -*- coding: utf-8 -*-
"""从已生成的分册数据中提取 西语文本 -> IPA 对照，用于校验规则转换器。"""
import json, glob, os, sys, pickle

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_sec(path):
    s = open(path, encoding="utf-8").read()
    # window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[46]={...};
    i = s.index("window.BOOK_DATA[")
    j = s.index("{", i)
    k = s.rindex("}")
    return json.loads(s[j:k + 1])


def main():
    pairs = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "sec", "*.js")),
                    key=lambda p: int(os.path.basename(p)[:-3])):
        d = load_sec(f)
        for sec in d["secs"]:
            for it in sec.get("w", []) + sec.get("e", []):
                pairs.setdefault(it[1], it[6])
            for it in sec.get("s", []):
                pairs.setdefault(it[0], it[6])
    print("unique es texts:", len(pairs))
    pickle.dump(pairs, open(os.path.join(ROOT, "_tools", "_ipa_pairs.pkl"), "wb"))


if __name__ == "__main__":
    main()
