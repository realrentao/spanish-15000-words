import json
t=open("data/sec/0.js",encoding="utf-8").read()
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
for sec in obj["secs"]:
    if sec["no"] in (1,2,3,8,9,10):
        print("="*72)
        print(f"SEC {sec['no']}  {sec['name']}  (w{len(sec.get('w',[]))} s{len(sec.get('s',[]))} e{len(sec.get('e',[]))})")
        for arr,lab in (("w","W"),("s","S"),("e","E")):
            if arr in sec:
                for idx,row in enumerate(sec[arr]):
                    print(f"  [{lab}{idx}] " + " | ".join(str(x) for x in row))
