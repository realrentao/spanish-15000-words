import json, re
bj=json.load(open("data/book.json",encoding="utf-8"))
p=bj["partes"][9]
def norm(s):
    return re.sub(r'[^a-záéíóúñü]', '', (s or "").lower())
# book sec2 sent2
s2=[s for s in p["secs"] if s["no"]==2][0]
b_sent=s2["sents"][1]["es"]
print("BOOK S2 es repr:", repr(b_sent))
print("BOOK norm:", norm(b_sent))
print("BOOK norm bytes:", [hex(ord(c)) for c in norm(b_sent) if ord(c)>127])
# 文案 cleaned
ces="Es el tiempo que tú has gastado en tu rosa que hace tu rosa tan importante. Tú serás responsable para siempre de lo que has domesticado."
print("CES  norm:", norm(ces))
print("CES  norm bytes:", [hex(ord(c)) for c in norm(ces) if ord(c)>127])
print("MATCH:", norm(b_sent)==norm(ces))
# show the region around importante in both
print("BOOK around:", repr(b_sent[b_sent.find('importan'):b_sent.find('importan')+20]))
