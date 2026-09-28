import glob, os, re, json, importlib.util

# audio maxes
nums_es=set(); nums_zh=set()
for f in glob.glob("audio/es/*.mp3")+glob.glob("audio/zh/*.mp3"):
    base=os.path.basename(f)
    m=re.match(r"(\d{5})\.mp3$", base)
    if m:
        parent=os.path.basename(os.path.dirname(f))
        if parent=="es": nums_es.add(int(m.group(1)))
        elif parent=="zh": nums_zh.add(int(m.group(1)))
print("max es:", max(nums_es) if nums_es else 0, "count:", len(nums_es))
print("max zh:", max(nums_zh) if nums_zh else 0, "count:", len(nums_zh))
print("edge_tts:", "OK" if importlib.util.find_spec("edge_tts") else "MISSING")
print("pypinyin:", "OK" if importlib.util.find_spec("pypinyin") else "MISSING")
