import json
t=open("data/sec/0.js",encoding="utf-8").read()
i=t.index("={")+1; d=0; j=i; s=False; e=False
while j<len(t):
    c=t[j]
    if s:
        if e: e=False
        elif c=='\\': e=True
        elif c=='"': s=False
    else:
        if c=='"': s=True
        elif c=='{': d+=1
        elif c=='}':
            d-=1
            if d==0: break
    j+=1
o=json.loads(t[i:j+1])
s2=[x for x in o["secs"] if x["no"]==2][0]
w14=s2["w"][14]
print("W14:", w14)
print("sec2 w count:", len(s2["w"]), "e count:", len(s2["e"]))
s10=[x for x in o["secs"] if x["no"]==10][0]
print("sec10 w count:", len(s10["w"]), "s count:", len(s10["s"]))
# verify prefix
print("prefix OK:", t.startswith('window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[0]='))
