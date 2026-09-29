# -*- coding: utf-8 -*-
"""Build data/sec/13.js (Parte 13 人的情绪 / book gid=13) from _tools/parte13_raw.txt.
ES_FIX: 令人信服的 convencivo->convincente (clear OCR/typo).  S_SUBS cosmetic.
Left as-is (flagged): 喜爱 preferencia, 亲近的 afecto, 同等地 también, 缩放 condensación."""
from build_parte_lib import Builder

b = Builder(
    gid=13, bp_name="人的情绪", raw_file="_tools/parte13_raw.txt",
    ES_FIX={"令人信服的":"convincente"},
    S_SUBS={"comlicado":"complicado", "nostros":"nosotros"},
)
b.run()
