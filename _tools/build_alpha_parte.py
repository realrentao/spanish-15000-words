# -*- coding: utf-8 -*-
"""为「字母分区词表」型 Part（gid47 时尚热词）构建 sec 文件。

与 rebuild_gid.py 的三段式 Builder 不同，本脚本：
- 用 parse_alpha_table.parse_alpha_table 解析（字母分区 + 「中文 西语」词条）
- 全部词条作为终极分类词（W），无词性（这套词表原文没标）
- 无例句（S）、无词汇大拓展（E）
- 复用 build_parte_lib.Builder 的音频分配 / 拼音 / IPA 逻辑

用法: python build_alpha_parte.py 47
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_parte_lib import Builder, clean_es, clean_cn, norm
from parse_alpha_table import parse_alpha_table

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- 修正表
TYPO = {
    # OCR：ñ 被识别成 .
    "rasgu.o": "rasguño",                # 白手起家
    "a.o": "año",                        # 拜年 / 本命年 / 年夜饭
    "pa.uelo": "pañuelo",                # 红领巾
    "dise.o": "diseño",                  # 构想
    "ca.ón": "cañón",                    # 炮灰
    "desempe.ar": "desempeñar",          # 跑龙套
    "ni.os": "niños",                    # 望子成龙
    "co.o": "coño",                      # 傻帽
    # 断词/空格残留
    "los laurel": "los laureles",        # 吃老本（缺词尾 s）
    "exámen": "examen",                  # 枪手（西语无重音符号）
    "beneficio mutuo": "beneficios mutuos",   # 互惠贸易（复数）
    "vía láctea": "vía del Vega Cuadra",     # 鹊桥会（银河，非母乳）
    "ofrenda": "ofrenda",
}

# (中文, clean_es+typo 后的西语) -> 正确西语
FIX = {
    # ---- 义项错配：西语与中文完全不对应
    ("扒窃", "chorizar"): "robo",         # chorizar=偷（小动作），非「扒窃」
    ("吃香", "peregrino"): "popular",# peregrino=朝圣者/流浪者（已 WebSearch 核实）
    ("电脑迷", "ventiladores de ordenadores"): "aficionado a la informática",  # ventiladores=通风扇
    ("单眼皮", "sepet"): "párpado",        # sepet 拼写错误
    ("看跌者", "carto"): "bajista",         # carto 残缺（应为<IP>酩bajista</IP>）
    ("碰钉子", "desairado;"): "desairado",  # 行尾多余分号
    ("非婚生子女", "adulterio"): "hijo ilegítimo",  # adulterio=通奸
    ("挂职", "apego"): "destacado",        # apego=黏合/执着
    ("挂靠公司", "empresa allied"): "empresa afiliada",  # allied=英文借词
    ("独家代理", "representación exclusivo"): "representación exclusiva",  # 性数不一致
    ("倾国倾城", "la viuda de emperatriz"): "mujer fatale",  # 「皇后寡妇」与中文无关
    ("还俗", "ser reducido al estado laical"): "ser secularizado",  # 搭配错误
    ("严惩", "castigar severamente"): "castigar severamente",
    # ---- 冠词/体例
    ("八宝饭", "arroz glutinoso con ochos cereales"): "arroz glutinoso con ocho cereales",
}

# 中文词头修正（CN_FIX 只按中文单键匹配）
CN_FIX = {}


def build(gid, bp_name, raw_file, split_every=1):
    secs = parse_alpha_table(raw_file, split_every)

    # 套一层「Builder 兼容」的壳：Builder.run 内部会调 parse_raw，
    # 这里改为直接注入 secs，手动复用其行构建逻辑。
    b = Builder.__new__(Builder)
    # book.json 里没有 gid47（这套词表是新加的），所以不能走 Builder.__init__。
    # 只初始化「与内容无关」的部分：音频号分配 + 全站已有音频复用索引。
    b.gid = gid
    b.bp_name = bp_name
    b.raw_file = raw_file
    b.ES_FIX = FIX
    b.ES_TYPO = TYPO
    b.S_SUBS = []
    b.POS_FIX = {}
    b.CN_FIX = CN_FIX
    b.S_ZH_SUBS = []

    import re as _re
    def cur_max(folder):
        m = 0
        for f in os.listdir(os.path.join(BASE, folder)):
            mm = _re.match(r'(\d{5})\.mp3$', f)
            if mm:
                m = max(m, int(mm.group(1)))
        return m

    b.EXIST_ES = set(); b.EXIST_ZH = set()
    for folder, s in (("audio/es", b.EXIST_ES), ("audio/zh", b.EXIST_ZH)):
        for f in os.listdir(os.path.join(BASE, folder)):
            mm = _re.match(r'(\d{5})\.mp3$', f)
            if mm:
                s.add(int(mm.group(1)))
    # 全站 sec 文件已占用的号也视为已用
    for i2 in range(48):
        fp = os.path.join(BASE, "data/sec/%d.js" % i2)
        if not os.path.exists(fp):
            continue
        t2 = open(fp, encoding="utf-8").read()
        for mm in _re.finditer(r'es/(\d{5})\.mp3', t2):
            b.EXIST_ES.add(int(mm.group(1)))
        for mm in _re.finditer(r'zh/(\d{5})\.mp3', t2):
            b.EXIST_ZH.add(int(mm.group(1)))
    b._es_n = cur_max("audio/es") + 1
    b._zh_n = cur_max("audio/zh") + 1
    while b._es_n in b.EXIST_ES:
        b._es_n += 1
    while b._zh_n in b.EXIST_ZH:
        b._zh_n += 1
    b.audio_jobs = []
    b.built = {}
    b.bp = {"gid": gid, "secs": []}
    b.bj_secs = {}
    b.sent_by_norm = {}
    b.GES = b._load_global_audio()   # 全站「西语文本 -> 已有音频」索引

    out_secs = []
    tw = ts = te = 0
    stat = {"book": 0, "new": 0, "reuse": 0, "dedup": 0}
    for no in sorted(secs):
        rs = secs[no]
        w_out = []
        for (raw_cn, raw_es, raw_pos) in rs["w"]:
            cn = clean_cn(raw_cn)
            if cn in CN_FIX:
                cn = CN_FIX[cn]
            ces = clean_es(raw_es)
            for k, v in TYPO.items():
                ces = ces.replace(k, v)
            if (cn, ces) in FIX:
                ces = FIX[(cn, ces)]
            row, how = b._row_for(cn, ces, "", [])
            w_out.append(row)
            stat[how] += 1
        out_secs.append({"no": no, "name": rs["name"], "w": w_out, "s": [], "e": []})
        tw += len(w_out)
        print("sec %-2d %-4s W=%d" % (no, rs["name"], len(w_out)))

    obj = {"secs": out_secs}
    out = ("window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=" % gid) + \
        json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";"
    open(os.path.join(BASE, "data/sec/%d.js" % gid), "w", encoding="utf-8").write(out)
    print("sec/%d.js written. W=%d S=0 E=0 totalAll=%d" % (gid, tw, tw))
    print("rows: book=%d reuse=%d new=%d dedup=%d | new audio jobs=%d"
          % (stat["book"], stat["reuse"], stat["new"], stat["dedup"], len(b.audio_jobs)))
    print("next es=%d zh=%d" % (b._es_n, b._zh_n))


if __name__ == "__main__":
    gid = int(sys.argv[1])
    bp = sys.argv[2]
    raw = sys.argv[3]
    every = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    build(gid, bp, raw, every)
