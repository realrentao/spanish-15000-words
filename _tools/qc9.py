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
issues = 0
for s in o["secs"]:
    for kind, arr in (("w", s["w"]), ("e", s["e"]), ("s", s["s"])):
        for r in arr:
            es = r[1] if kind == "s" else r[1]
            zh = r[0] if kind == "s" else r[0]
            # Spanish field for w/e is r[1]; for s it's r[0]
            sp = r[0] if kind == "s" else r[1]
            zhf = r[1] if kind == "s" else r[0]
            # checks on Spanish
            if re.search(r'[一-鿿]', sp):
                print("CJK in Spanish!", kind, r); issues += 1
            if re.search(r'(?<=[A-Za-z])-(?=[A-Za-z])', sp):
                print("midword hyphen!", kind, r); issues += 1
            if re.search(r'[aeiouáéíóúAEIOUÁÉÍÓÚ]\.[aeiouáéíóúAEIOUÁÉÍÓÚ]', sp):
                print("vowel. vowel leftover!", kind, r); issues += 1
            if re.search(r'(?<=[A-Za-z])\.(?=[A-Za-z])', sp):
                print("stray dot in latin!", kind, r); issues += 1
            # check key fixes present
print("issues =", issues)
# print specific fixed entries
def show(cn_sub):
    for s in o["secs"]:
        for kind, arr in (("w", s["w"]), ("e", s["e"])):
            for r in arr:
                if cn_sub in r[0]:
                    print(kind, r[0], "=>", r[1], r[3])
show("蓬乱的"); show("梳理"); show("卷发的"); show("染色"); show("一缕毛发"); show("理发"); show("稀疏的头发")
