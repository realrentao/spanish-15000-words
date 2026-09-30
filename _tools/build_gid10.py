# -*- coding: utf-8 -*-
"""Build data/sec/10.js (Parte 6 其他常见设施 / book gid=10) from _tools/parte_gid10_raw.txt.
NOTE: 文案 自编号 "Parte 6" != book gid (=10). Filename uses gid to avoid clashing with
parte10_raw.txt / build_parte10.py (常见商店, gid=9).
S_SUBS: búsquada->búsqueda (OCR 'e'->'a' inside bús-quada), basureres->basureros.
Left as-is (flagged): 花坛 terraza, 堆 meter, 处理 organizar, 清除 barrer, 分解 disociar,
阉割 emasculación, 使畅通 descongestionar, 成衣 vestimenta, 垃圾场 botadero de vertedero;
pos kept as 文案 marked (paloma/base marked n.m. though grammatically feminine)."""
from build_parte_lib import Builder

b = Builder(
    gid=10, bp_name="其他常见设施", raw_file="_tools/parte_gid10_raw.txt",
    S_SUBS={"búsquada":"búsqueda", "basureres":"basureros"},
)
b.run()
