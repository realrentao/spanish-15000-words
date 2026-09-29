# -*- coding: utf-8 -*-
"""Build data/sec/12.js (Parte 12 人身体的行为 / book gid=12) from _tools/parte12_raw.txt.
No ES_FIX/ES_TYPO/S_SUBS needed: OCR handled by generic clean (per-sonas, men-tira,
cla-sificación, espa.oles, noso-tros hyphens; espa.oles vowel-dot-vowel -> españoles).
Left as-is (flagged to user): 弯腰 curva, 摇晃 escalonar, 拖着脚步走 colgando de la pierna,
叫喊 proclamar, 表扬 exaltar."""
from build_parte_lib import Builder

b = Builder(
    gid=12, bp_name="人身体的行为", raw_file="_tools/parte12_raw.txt",
)
b.run()
