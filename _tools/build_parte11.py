# -*- coding: utf-8 -*-
"""Build data/sec/11.js (Parte 11 人的特征 / book gid=11) from _tools/parte11_raw.txt.
ES_FIX (cn-level, clearly wrong Spanish fixed): 军人 militante->militar, 使发怒 irritir->irritar,
招呼，问候 saludó->saludo.  ES_TYPO: rosadoa->rosada.
S_SUBS: Sevillia->Sevilla, el europe.->el europeo., rosadoa->rosada, burlar aotros->burlar a otros.
Left as-is (flagged to user, replacement uncertain): 鼓起来的 saldado, 深陷的 atascado,
卑鄙的 astroso, 斜视 bizcar, 消瘦的 seco, 微弱的 pálido, 比例 escala, 迷人的 atractivo,a."""
from build_parte_lib import Builder

b = Builder(
    gid=11, bp_name="人的特征", raw_file="_tools/parte11_raw.txt",
    ES_FIX={"军人":"militar", "使发怒":"irritar", "招呼，问候":"saludo"},
    ES_TYPO={"rosadoa":"rosada"},
    S_SUBS={"Sevillia":"Sevilla", "el europe.":"el europeo.", "rosadoa":"rosada",
            "burlar aotros":"burlar a otros"},
)
b.run()
