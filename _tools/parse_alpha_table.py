# -*- coding: utf-8 -*-
"""字母分区词表解析器（用于 gid47「时尚热词」这类文案）。

与 build_parte_lib.parse_raw 的三段式（终极分类词/经典实用句/词汇大拓展）不同，
本文案的结构是：

    时尚热词
    A
    安慰奖 premio de consolación
    暗箱操作 operaciones encubiertas
    B
    八宝饭 arroz glutinoso con ochos cereales
    ...

即：单字母行 = 分区标题；「中文 西语」行 = 词条。
**没有小节标题、没有词性、没有例句、没有词汇大拓展。**

输出与 parse_raw 相同的结构：{no: {"name","w","s","e"}}，
其中 w = [(cn, es, pos)]，s = []，e = []，这样可以直接复用 Builder。
"""
import re, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 只有一个字母（不区分大小写）的行 = 分区标题
_SECT_RE = re.compile(r'^[A-Z]$')
# 词条行：必须同时含汉字与拉丁字母
_ENTRY_RE = re.compile(r'[一-鿿]')

# OCR 常见垃圾：出现在词条里的孤立标点/页码残片
_JUNK_RE = re.compile(r'^[<\[].*|^.*?[<>]\d{4,}.*$')


def _norm_line(s):
    """压掉多余空白（含全角空格），便于分词。"""
    return re.sub(r'[\s\u3000]+', ' ', s).strip()


def _is_junk(s):
    """判断是否是 OCR 残片行（页码标记、空行等）。"""
    if not s:
        return True
    # 形如 <1HITC1"> 的页码残片
    if re.search(r'<\d+[A-Z]*\d*"', s):
        return True
    return False


def parse_alpha_table(raw_file, split_every=1):
    """解析字母分区词表。

    split_every: 每 N 个字母合成一个小节。1 = 每个字母一节。
    返回 {no: {"name","w","s","e"}}，no 从 1 开始。
    """
    txt = open(os.path.join(BASE, raw_file), encoding="utf-8").read()
    txt = re.sub(r'<[^>]*>', '', txt)          # 去 HTML/页码残片
    txt = txt.replace('\\', '')

    # 首行若是 Part 标题（无西语的纯中文行），单独剔除
    lines = txt.split("\n")
    for i, l in enumerate(lines):
        s = _norm_line(l)
        if s and re.fullmatch(r'[一-鿿]+', s) and i == 0:
            continue          # 标题行，忽略
        break
    txt = "\n".join(lines[i:]) if i else txt

    # 先扫一遍，收集 (字母, 中文, 西语)
    entries = []          # [(letter, cn, es)]
    letter = None
    for raw in txt.split("\n"):
        line = _norm_line(raw)
        if _is_junk(line):
            continue
        if _SECT_RE.match(line):
            letter = line
            continue
        if not _ENTRY_RE.search(line):        # 无汉字 -> 不是词条行
            continue
        # 切分点 = **第一个拉丁字母**（词条格式为「中文 西语」，
        # 中文段可能含空格/全角标点，用「首个拉丁字母」定位最稳；
        # 若用「首个汉字」当切点，行首即汉字时会得到空 cn + 整行进 es）。
        m = re.search(r'[A-Za-zÁÉÍÓÚÑáéíóúñ]', line)
        if not m:
            continue
        cn = line[:m.start()].strip()
        es = line[m.start():].strip()
        if not cn or not es:
            continue
        # 极少数行是「西语 中文」写法（es 段含汉字），交换回来
        if re.search(r'[一-鿿]', es):
            cn, es = es, cn
        entries.append((letter, cn, es))

    # 按字母分组 -> 每 split_every 个字母合成一个小节
    letters = []
    for lt, _, _ in entries:
        if lt is not None and (not letters or letters[-1] != lt):
            letters.append(lt)

    secs = {}
    for no in range(1, len(letters) + 1, split_every):
        chunk = letters[no - 1: no - 1 + split_every]
        name = "".join(chunk) if len(chunk) > 1 else chunk[0]
        secs[no] = {"name": name, "w": [], "s": [], "e": []}

    for idx, (lt, cn, es) in enumerate(entries, start=1):
        # 找到该字母属于第几个小节
        sec_no = (letters.index(lt) // split_every) + 1
        secs[sec_no]["w"].append((cn, es, ""))   # 无词性 -> 空

    return secs


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    import glob
    raw = sys.argv[1] if len(sys.argv) > 1 else "_tools/parte47_raw.txt"
    every = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    secs = parse_alpha_table(raw, every)
    total = 0
    for no in sorted(secs):
        s = secs[no]
        total += len(s["w"])
        print("Sec%-2d %-4s W=%d" % (no, s["name"], len(s["w"])))
    print("总词条:", total)
    # 打印前 10 条与后 5 条做抽样检查
    allw = [(no, cn, es) for no in sorted(secs) for (cn, es, _) in secs[no]["w"]]
    print("\n--- 前 8 条 ---")
    for no, cn, es in allw[:8]:
        print("  %-2d %-10s | %s" % (no, cn, es))
    print("--- 后 5 条 ---")
    for no, cn, es in allw[-5:]:
        print("  %-2d %-10s | %s" % (no, cn, es))
