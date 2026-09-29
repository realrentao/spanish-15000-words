# -*- coding: utf-8 -*-
"""Build data/sec/15.js (Parte 15 人与人之间的关系 / book gid=15) from _tools/parte15_raw.txt.
No ES_FIX. S_SUBS: comlicado->complicado, nostros->nosotros."""
from build_parte_lib import Builder

b = Builder(
    gid=15, bp_name="人与人之间的关系", raw_file="_tools/parte15_raw.txt",
    S_SUBS={"comlicado":"complicado", "nostros":"nosotros"},
)
b.run()
