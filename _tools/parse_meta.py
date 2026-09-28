import json
t=open("data/meta.js",encoding="utf-8").read()
start=t.index("={")+1
depth=0;i=start;instr=False;esc=False
while i<len(t):
    c=t[i]
    if instr:
        if esc: esc=False
        elif c=='"': instr=False
    else:
        if c=='"': instr=True
        elif c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: break
    i+=1
obj=json.loads(t[start:i+1])
print("top keys:", list(obj.keys()))
for k in obj:
    if k!="grupos":
        print(k, "=", obj[k])
g0=obj["grupos"][0]
tot=0
for s in g0["partes"][0]["secs"]:
    tot += s.get("w",0)+s.get("s",0)+s.get("e",0)
print("gid0 current sum(w+s+e):", tot)
print("totalAll (if present):", obj.get("totalAll","NONE"))
print("trailing chars after JSON:", repr(t[i+1:i+30]))
