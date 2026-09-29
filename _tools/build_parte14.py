# -*- coding: utf-8 -*-
"""Build data/sec/14.js (Parte 14 人类交流的方式 / book gid=14) from _tools/parte14_raw.txt.
No ES_FIX. S_SUBS cosmetic only. Left as-is (flagged): 缩放 condensación."""
from build_parte_lib import Builder

b = Builder(
    gid=14, bp_name="人类交流的方式", raw_file="_tools/parte14_raw.txt",
    S_SUBS={"comlicado":"complicado", "nostros":"nosotros"},
)
b.run()
