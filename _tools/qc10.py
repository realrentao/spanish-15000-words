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
issues=[]
for s in o["secs"]:
    for kind,arr in (("w",s["w"]),("e",s["e"]),("s",s["s"])):
        for r in arr:
            es=r[1 if kind!="s" else 0]
            zh=r[0 if kind!="s" else 1]
            if re.search(r'[一-鿿]', es): issues.append(("CJK in es",kind,es))
            if re.search(r'[A-Za-z]', zh) and kind!="s": pass
            # OCR residual markers
            for bad in ["ba.o","se.al","ca.a","u.a","construción","vidria","da.o","esplio","carmino","izquerida","contigente","ferrocaril","alma-cenes","empe.o","mas-cotas","jo-yer","vebde","tra-baja","se.ora","es-pecial","desmesu-","clara-","trans-porte","incre-mento","co-mestibles","su-bida","mer-canc","es-trella","importante.Tú"]:
                if bad in es.lower(): issues.append(("OCR residual "+bad,kind,es))
            # mid-word hyphen
            if re.search(r'[A-Za-zÁÉÍÓÚÑÜáéíóúñü]-[A-Za-zÁÉÍÓÚÑÜáéíóúñü]', es): issues.append(("mid hyphen",kind,es))
            # stray isolated dot between letters (not abbreviation)
            if re.search(r'[A-Za-zÁÉÍÓÚÑÜáéíóúñü]\.[A-Za-zÁÉÍÓÚÑÜáéíóúñü]', es): issues.append(("mid dot",kind,es))
print("issues:", len(issues))
for x in issues: print("  ",x)
print("---- all es fields ----")
for s in o["secs"]:
    print("SEC",s["no"],s["name"])
    for kind,arr in (("w",s["w"]),("e",s["e"])):
        for r in arr: print("  ",kind,repr(r[1]),"|",r[0])
    for r in s["s"]: print("  S",repr(r[0]))
