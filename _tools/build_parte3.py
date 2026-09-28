# -*- coding: utf-8 -*-
"""Build data/sec/2.js (Parte 3 食) from the user's pasted 文案 (parte3_raw.txt).
- Content source of truth = 文案 (word/sentence/extra lists + 词性).
- Clean Spanish + existing audio reused from book.json where cn matches.
- 文案-only entries (111 W + 8 E) get hand-corrected clean Spanish + NEW audio.
- 词性 kept only where the 文案 explicitly marked it (blank otherwise).
- Sentences: clean es + audio from book.json (hyphen artifacts fixed), src from 文案.
"""
import json, re, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from es_ipa import text_ipa
from pypinyin import pinyin, Style

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = 2

POS = set(["n.m.","n.f.","v.t.","v.i.","adj.","adv.","prnl.","n.","v.","s.m.","s.f.","m.","f."])
def is_pos(t):
    if t in POS:
        return True
    if t in ("vi.","vt."):
        return True
    return re.match(r'^[a-z]+\.[mf]\.?$', t) is not None
def norm_pos(t):
    return {"vi.":"v.i.","vt.":"v.t."}.get(t, t)

# ---------- parse 文案 ----------
def parse_raw():
    txt = open(os.path.join(BASE, "_tools/parte3_raw.txt"), encoding="utf-8").read()
    secs = {}
    cur=None; mode=None
    for ln in txt.split("\n"):
        s = ln.strip()
        if not s: continue
        m = re.match(r'^Secci[oó]n\s+(\d+)\s+(.*)$', s)
        if m:
            cur=int(m.group(1)); secs[cur]={"name":m.group(2).strip(),"w":[],"s":[],"e":[]}
            mode=None; continue
        if s.startswith("终极分类词"): mode="w"; continue
        if s.startswith("经典实用句"): mode="s"; continue
        if s.startswith("词汇大拓展"): mode="e"; continue
        if s.startswith("Parte"): continue
        if cur is None: continue
        if mode=="w":
            toks=s.split()
            if not toks: continue
            cn=toks[0]; rest=toks[1:]
            pos=""
            if rest and is_pos(rest[-1]):
                pos=norm_pos(rest[-1]); es=" ".join(rest[:-1])
            else:
                es=" ".join(rest)
            secs[cur]["w"].append((cn,es,pos))
        elif mode=="e":
            toks=s.split()
            if len(toks)<2: continue
            cn=toks[-1]; pre=toks[-2]
            if is_pos(pre):
                pos=norm_pos(pre); es=" ".join(toks[:-2])
            else:
                pos=""; es=" ".join(toks[:-1])
            secs[cur]["e"].append((es,cn,pos))
        elif mode=="s":
            if s.startswith("例"):
                secs[cur]["s"].append(s[1:].strip())
    return secs

# ---------- pinyin ----------
def py(text):
    return " ".join(ch[0] for ch in pinyin(text, style=Style.TONE, heteronym=False, errors="ignore"))

# ---------- hand-corrected Spanish for 文案-only / wrong-es entries ----------
ES_FIX = {
 # W missing
 "消化":"digestión","清淡饮食":"comida ligera",
 "炒米饭":"arroz frito","火烧煎蛋卷":"tortilla flambeada","皮蛋":"huevos conservados en cal",
 "稀饭":"gachas de arroz","豆浆":"leche de soja","烤鸭":"pato laqueado","咸鸡蛋":"huevo salado",
 "火锅":"fondue mongola","煮鸡蛋":"huevo duro",
 "烤鹅肝":"foie gras asado",
 "套餐":"menú del día","中餐厨师长":"cocinero chino","吃饱喝足":"atiparse",
 "方便面":"fideos instantáneos","擀平":"extender","麻酱面":"fideos de sésamo",
 "米粉":"fideos de arroz","扁面条":"fideos planos",
 "面包片":"la rebanada de pan","圆面包":"pan de pita","圆形面包":"pan redondo",
 "黑麦面包":"pan de centeno","牛角面包":"croissant","奶油面包":"pan de crema",
 "慕斯":"mousse","水果罐头":"frutas en conserva","奶油蛋糕":"tarta de crema",
 "炒":"frito","在烤箱烘烤":"hornear en el horno",
 "食用油":"aceite de cocina","大豆油":"aceite de soja","菜籽油":"aceite de colza","玉米油":"aceite de maíz",
 "花生油":"aceite de maní","棕榈油":"aceite de palma","橄榄油":"aceite de oliva","香油":"aceite de sésamo",
 "核桃油":"aceite de nuez","调和油":"aceite mezclado","地沟油":"aceite desechado",
 "辣椒粉":"polvo de chile","酱油":"salsa de soja","料酒":"vino de cocinar",
 "肉豆蔻":"nuez moscada","黑椒":"pimienta negra",
 "香草冰激凌":"helado de vainilla","冰水":"agua helada","橙汁":"zumo de naranja","可乐":"coca cola",
 "充气饮料":"bebida carbonatada",
 "矿泉水":"agua mineral","绿茶":"té verde","红茶":"té rojo","茉莉花茶":"té de jazmín","乌龙茶":"té oolong",
 "香味":"olor agradable","饮用水":"agua potable","白开水":"agua hervida","热水":"agua caliente","冷水":"agua fría",
 "碳酸饮料":"bebida carbonatada","二氧化碳":"dióxido de carbono","瓶装啤酒":"cerveza en lata",
 "咖啡豆":"grano de café","咖啡器具":"juego de café","咖啡匙":"cuchara de café","咖啡磨":"amoladora de café",
 "冰咖啡":"café helado","拿铁":"latté","脱脂咖啡":"café descafeinado","黑咖啡":"café negro",
 "牛奶咖啡":"café con leche","速溶咖啡":"café instantáneo",
 "餐具架":"vasar","不锈钢":"acero inoxidable",
 "玻璃马克杯":"taza de cristal","咖啡杯":"taza de café","啤酒杯":"jarra de cerveza","玻璃杯":"jarra de cristal",
 "小垫子":"estera pequeña","运动水壶":"botella de deporte",
 "坚果":"fruto seco","少量":"una pequeña cantidad","含果仁的":"contener nueces","葡萄干":"pasas de uva",
 "葵花籽":"semilla de girasol","爆米花":"palomitas de maíz","夹心糖":"caramelo relleno",
 "压缩饼干":"galleta comprimida","消化饼干":"galleta digestiva","曲奇饼干":"cookies","饼干盒":"caja de galletas",
 "华夫饼":"gofres","薄饼干":"cracker","椒盐脆饼干":"bretzel",
 "风干":"secar al aire","食品添加剂":"aditivo alimentario",
 "香草酸":"ácido vanílico",
 # E missing
 "除了……":"además de","牛肉":"carne de vaca","既然":"ya que","污油":"aceite sucio",
 "走过，驶过；经过":"pasar","行为，举止":"comportamiento","糕点，糕点制作法":"pastelería",
 "渗透的，渗透作用的":"osmótico",
 # Sec13 wine sub-entries (missing from book.json): correct OCR/book typos
 "红葡萄酒":"vino tinto","白葡萄酒":"vino blanco","鸡尾酒":"cóctel","玫瑰红葡萄酒":"vino rosado",
 "干葡萄酒":"vino seco","半干葡萄酒":"vino medio seco","甜葡萄酒":"vino dulce",
 "天然葡萄酒":"vino natural","加香葡萄酒":"vino con especias","起泡葡萄酒":"vino espumoso",
}
# special multi-synonym (cn in 文案 is '酒；'); book.json has clean es 'vino'
WINE_CN = "酒； 葡萄酒； 果酒"

# ---------- new audio allocator ----------
def next_es():
    global es_n
    while os.path.exists(os.path.join(BASE,"audio/es/%05d.mp3"%es_n)): es_n+=1
    p="es/%05d.mp3"%es_n; es_n+=1; return p
def next_zh():
    global zh_n
    while os.path.exists(os.path.join(BASE,"audio/zh/%05d.mp3"%zh_n)): zh_n+=1
    p="zh/%05d.mp3"%zh_n; zh_n+=1; return p

es_n=6326; zh_n=7099
audio_jobs=[]

def mkrow_missing(cn, es, pos):
    ep=next_es(); zp=next_zh()
    audio_jobs.append((es, ep, cn, zp))
    return [cn, es, pos, ep, zp, py(cn), text_ipa(es)]

# ---------- load book.json parte 3 ----------
bj=json.load(open(os.path.join(BASE,"data/book.json"),encoding="utf-8"))
bp=[x for x in bj["partes"] if x["no"]==3][0]
bj_secs={s["no"]:s for s in bp["secs"]}

def find_book(cn, words):
    for w in words:
        if w["cn"]==cn: return w
    for w in words:
        if w["cn"].startswith(cn+" "): return w
    return None

def fix_s_es(es):
    return (es.replace("moles-tarte","molestarte")
             .replace("en-canta","encanta")
             .replace("mu-.eca","muñeca"))

def extract_src(text):
    i=text.find("——")
    return text[i:] if i>=0 else ""

# ---------- build ----------
secs=parse_raw()
out_secs=[]
total_w=total_s=total_e=0
for no in sorted(secs.keys()):
    rs=secs[no]
    bjw=bj_secs[no]["words"]; bje=bj_secs[no].get("extra",[]); bjs=bj_secs[no].get("sents",[])
    w_out=[]; e_out=[]; s_out=[]
    for (cn,raw_es,pos) in rs["w"]:
        if cn == "酒；":
            b=find_book(WINE_CN, bjw)
            es="vino"; cn=WINE_CN; pos="n.m."
            if b:
                w_out.append([cn,es,pos,b["ae"],b["az"],b["py"],b["ipa"]])
            else:
                w_out.append(mkrow_missing(cn,es,pos))
            continue
        if cn in ES_FIX and not find_book(cn, bjw):
            w_out.append(mkrow_missing(cn, ES_FIX[cn], pos)); continue
        b=find_book(cn, bjw)
        if b:
            es=b["es"]
            if cn in ES_FIX and ES_FIX[cn]!=es:
                w_out.append(mkrow_missing(cn, ES_FIX[cn], pos)); continue
            w_out.append([cn,es,pos,b["ae"],b["az"],b["py"],b["ipa"]])
        else:
            w_out.append(mkrow_missing(cn, ES_FIX.get(cn, raw_es), pos))
    for (es,cn,pos) in rs["e"]:
        if cn in ES_FIX and not find_book(cn, bje):
            e_out.append(mkrow_missing(cn, ES_FIX[cn], pos)); continue
        b=find_book(cn, bje)
        if b:
            bes=b["es"]
            if cn in ES_FIX and ES_FIX[cn]!=bes:
                e_out.append(mkrow_missing(cn, ES_FIX[cn], pos)); continue
            e_out.append([cn,bes,pos,b["ae"],b["az"],b["py"],b["ipa"]])
        else:
            e_out.append(mkrow_missing(cn, ES_FIX.get(cn, es), pos))
    # S: index-aligned with book.json sents; clean es + audio from book, src from 文案
    for i, raw in enumerate(rs["s"]):
        b = bjs[i] if i < len(bjs) else None
        if b:
            es=fix_s_es(b["es"]); zh=b["zh"]
            s_out.append([es, zh, extract_src(raw), b["ae"], b["az"], b["py"], b["ipa"]])
        else:
            ep=next_es(); zp=next_zh()
            audio_jobs.append((raw, ep, raw, zp))
            s_out.append([raw, raw, extract_src(raw), ep, zp, "", ""])
    out_secs.append({"no":no,"name":rs["name"],"w":w_out,"s":s_out,"e":e_out})
    total_w+=len(w_out); total_s+=len(s_out); total_e+=len(e_out)

obj={"secs":out_secs}
out='window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]='%GID + json.dumps(obj, ensure_ascii=False, separators=(",",":")) + ";"
open(os.path.join(BASE,"data/sec/%d.js"%GID),"w",encoding="utf-8").write(out)
print("sec/%d.js written. W=%d S=%d E=%d  new audio jobs=%d"%(GID,total_w,total_s,total_e,len(audio_jobs)))
print("totalAll this parte:", total_w+total_s+total_e)

# ---------- manifest ----------
mj=os.path.join(BASE,"_tools/audio_manifest.json")
existing=[]
if os.path.exists(mj):
    try: existing=json.load(open(mj,encoding="utf-8")).get("jobs",[])
    except Exception: existing=[]
def add_job(es,esp,zh,zhp):
    key=esp or zhp
    if not key or key in seen: return
    seen.add(key); merged.append({"es":es,"esPath":esp,"zh":zh,"zhPath":zhp})
seen=set(); merged=[]
for j in existing:
    if isinstance(j,dict): add_job(j.get("es"),j.get("esPath"),j.get("zh"),j.get("zhPath"))
    else: add_job(j[0],j[1],j[2],j[3])
for j in audio_jobs:
    add_job(j[0],j[1],j[2],j[3])
json.dump({"jobs":merged}, open(mj,"w",encoding="utf-8"), ensure_ascii=False, indent=0)
print("manifest jobs now:", len(merged))
