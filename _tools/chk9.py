import json, re
t = open(r"D:/西班牙语材料/15000词西语随身背/data/sec/8.js", encoding="utf-8").read()
i = t.index("={") + 1
depth = 0; j = i; ins = False; esc = False
while j < len(t):
    c = t[j]
    if ins:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': ins = False
    else:
        if c == '"': ins = True
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
    j += 1
o = json.loads(t[i:j+1])
print("secs:", [(s["no"], s["name"], len(s["w"]), len(s["s"]), len(s["e"])) for s in o["secs"]])
print("---- NEW audio (es>=06816 or zh>=07589) ----")
new = []
for s in o["secs"]:
    for kind, arr in (("w", s["w"]), ("e", s["e"]), ("s", s["s"])):
        for r in arr:
            ep = r[3]; zp = r[4]
            m = re.match(r'es/(\d{5})\.mp3', ep); z = re.match(r'zh/(\d{5})\.mp3', zp)
            ne = int(m.group(1)) >= 6816 if m else False
            nz = int(z.group(1)) >= 7589 if z else False
            if ne or nz:
                new.append((kind, r[0], r[1], ep, zp))
for x in new:
    print(x)
print("NEW count =", len(new))
