import json, re
t=open("data/sec/9.js",encoding="utf-8").read()
i=t.index("={")+1
depth=0; j=i; ins=False; esc=False
while j<len(t):
    c=t[j]
    if ins:
        if esc: esc=False
        elif c=='\\': esc=True
        elif c=='"': ins=False
    else:
        if c=='"': ins=True
        elif c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: break
    j+=1
o=json.loads(t[i:j+1])
new_es=set(); new_zh=set()
for s in o["secs"]:
    for kind,arr in (("w",s["w"]),("e",s["e"]),("s",s["s"])):
        for r in arr:
            # new audio = path not matching the book ranges already present; just print path numbers
            ep=r[3]; zp=r[4]
            def num(p):
                m=re.match(r'(es|zh)/(\d{5})\.mp3',p)
                return int(m.group(2)) if m else None
            en=num(ep); zn=num(zp)
            # mark as "new" if es>=6827 or zh>=7600 (disk max before build was es=6826 zh=7599)
            if en is not None and en>=6827:
                new_es.add(en)
            if zn is not None and zn>=7600:
                new_zh.add(zn)
            if (en is not None and en>=6827) or (zn is not None and zn>=7600):
                print(kind, r[0], "| es=",ep,"zh=",zp)
print("count new es rows:", len(new_es), "new zh rows:", len(new_zh), "union entries:", len(new_es|new_zh))
