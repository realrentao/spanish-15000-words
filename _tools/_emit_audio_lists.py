# -*- coding: utf-8 -*-
"""Emit per-gid NEW (untracked) audio path lists referenced by data/sec/<gid>.js.
Orphan files from rebuilds are not referenced by any sec file -> excluded.
Already-tracked reused book audio -> excluded (no need to re-add)."""
import os, re, json, subprocess
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_sec(path):
    t = open(path, encoding="utf-8").read()
    i = t.index("={") + 1
    depth=0; j=i; ins=False; esc=False
    while j < len(t):
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
    return json.loads(t[i:j+1])

# untracked paths from git status --porcelain
out=subprocess.run(["git","-C",BASE,"status","--porcelain"],capture_output=True,text=True).stdout
untracked=set()
for line in out.splitlines():
    if line.startswith("?? "):
        untracked.add(line[3:].strip().replace("\\","/"))

for gid in (13,14,15):
    o=load_sec(os.path.join(BASE,"data/sec/%d.js"%gid))
    new=set()
    for s in o.get("secs",[]):
        for kind,arr in (("w",s.get("w",[])),("e",s.get("e",[])),("s",s.get("s",[]))):
            for r in arr:
                for p in (r[3], r[4]):
                    if p and os.path.exists(os.path.join(BASE,"audio",p)) and p in untracked:
                        new.add(p)
    fpath=os.path.join(BASE,"_tools","audio%d.txt"%gid)
    with open(fpath,"w",encoding="utf-8") as f:
        for p in sorted(new):
            f.write(p+"\n")
    print("gid=%d NEW audio files to commit: %d"%(gid,len(new)))
