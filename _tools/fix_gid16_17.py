# -*- coding: utf-8 -*-
"""gid16「不同学校」/ gid17「学校设置」：西语习惯修正（不走 parse_raw，直接改现有行）。
- 只改西语文本 + 词性 + IPA + es 音频；中文 / zh 音频 / 拼音一律沿用旧值。
- 西语改过之后：先在全站复用同文本音频，再不行才新录（中文未变，zh 音频沿用旧的）。
"""
import json, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from es_ipa import text_ipa
from build_parte_lib import norm, py
from pypinyin import Style

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------- 修正表 ----------------
# W/E: (sec, old_cn, old_es, new_cn, new_es, new_pos)   cn 基本不动，只修 es/pos
W = {
16: {
 1: [("幼儿园","guardería","幼儿园","escuela infantil","n.f."),          # guardería=托儿所(0-3岁)，幼儿园=escuela infantil
     ("寄宿学校","pensionado","寄宿学校","internado","n.m."),              # pensionado=寄宿生/寄宿处，寄宿学校=internado
    ],
 2: [("延长","extender","延长","prolongar","v.t."),                       # extender=展开/扩展，「延长学制」用 prolongar
    ],
 3: [("笔试 examen por","escrito","笔试","examen escrito","n.m."),         # OCR 断行 + 词性错(短语非动词)
      ("试卷","hoja","试卷","hoja de examen","n.f."),                      # hoja 只是「纸」，试卷=hoja de examen
      ("复习","revisar","复习","repasar","v.t."),                          # revisar=检查，复习=repasar
    ],
},
17: {
 1: [("注册","registrar","注册","matricular","v.t."),                     # 大学注册=matricular(se)
    ],
 2: [("讲台","plataforma","讲台","tarima","n.f."),                        # plataforma=平台，讲台=tarima/estrado
     ("讲台","tribuna","讲台","podium","n.m."),                            # tribuna=观众席/看台，讲台=podium
     ("教鞭","varita","教鞭","bastón","n.m."),                             # varita=魔杖/小棍，教鞭=bastón
     ("投影仪","proyector","投影仪","proyector","n.m."),                    # proyector 阳性
     ("教科书","manual","教科书","libro de texto","n.m."),                  # manual=手册，教科书=libro de texto
    ],
 3: [("地面","tierra","地面","suelo","n.m."),                              # tierra=泥土/土地，地面=suelo
     ("秋千","oscilación","秋千","columpio","n.m."),                       # oscilación=摆动，秋千=columpio
     ("跳绳","saltar","跳绳","saltar a la cuerda","v.i."),                  # 跳绳整体=saltar a la cuerda
    ],
 4: [("单人床","cama","单人床","cama individual","n.f."),                  # 补出「单人」
     ("广播","emisión","广播","radio","n.f."),                             # emisión=播出，宿舍广播=radio
     ("被子","cobertura","被子","manta","n.f."),                            # cobertura=覆盖/保险，被子=manta/colcha
     ("睡觉","dormir","睡觉","dormir","v.i."),                              # dormir 不及物
    ],
 5: [("人物","carácter","人物","personaje","n.m."),                        # carácter=性格，人物=personaje
     ("水粉画 pintura de","gouache","水粉画","pintura al gouache","n.f."),
     ("画夹","bordo","画夹","carpeta","n.f."),                              # bordo=船舷，画夹=carpeta/portafolio
     ("画笔","cepillo","画笔","pincel","n.m."),                             # cepillo=刷子(鞋刷)，画笔=pincel
     ("素描","esbozar","素描","esbozo","n.m."),                             # esbozar=打草稿(动)，素描=esbozo(名)
     ("艺术家","artista","艺术家","artista","n.m."),
     ("画油画","pintar","画油画","pintar al óleo","v.t."),
     ("橡皮","goma","橡皮","goma de borrar","n.f."),
    ],
 6: [],
 7: [("导师","instructor","导师","tutor","n.m."),                          # instructor=教官/教练，导师=tutor
     ("代理的","interino","代理的","interino","adj."),                      # 中文带「的」→ 形容词
     ("转校生 estudiante de","transferencia","转校生","estudiante transferido","n.m."),
    ],
 8: [("财务","finanza","财务","finanzas","n.f."),                          # finanza 单数不常用
     ("人力资源 recurso","humano","人力资源","recursos humanos","n.f."),
    ],
 9: [("期刊","periódico","期刊","publicación periódica","n.f."),           # periódico=报纸
     ("借","prestar","借","tomar prestado","v.t."),                        # prestar=借出，借(入)=tomar prestado
     ("订阅 补录","suscribirse","订阅","suscribir","v.t."),
     ("到期的","vencimiento","到期的","vencido","adj."),                    # 中文带「的」→ 形容词
     ("扫描机","escáner","扫描机","escáner","n.m."),
     ("电子版 versión","electrónica","电子版","versión electrónica","n.f."),
     ("章","sello","章","capítulo","n.m."),                                # sello=印章/邮票，书的章=capítulo
    ],
},
}

# E（词汇大拓展）同 W（r[0]=中, r[1]=西, r[2]=词性）
E = {
16: {2: [("值得","merecer","值得","merecer","v.t.")]},                    # merecer 及物
17: {2: [("椅子","silla","椅子","silla","n.f."),                           # silla 阴性
          ("学生","alumno","学生","alumno","n.m.")],
     3: [("走动","excursion","走动","paseo","n.m.")]},                     # excursion 少重音，且「走动」=paseo
}

# S: (sec, old_es, new_es)  —— 中文不动
S = {
16: {
 1: [("Poco después del final de estudio en la escuela secundaria en 1870, Maupassant se alistó como voluntario en la guerra francoprusiana y luchó con valentía.",
      "Poco después de terminar la secundaria en 1870, Maupassant se alistó como voluntario en la guerra francoprusiana y luchó con valentía.")],
 2: [("Sobre el futuro de la educación, tenemos diferentes opinións.",
      "Sobre el futuro de la educación, tenemos opiniones diferentes."),   # opinións 拼写错
      ("El niño merece la educación.", "El niño merece una buena educación.")],
 3: [("Estó preparando un examen toda la noche.",                          # Estó → Está
      "Está preparando un examen toda la noche."),
      ("Ana aprobó un examen a base de codos.",                            # a base de codos 不是地道西语
       "Ana aprobó el examen estudiando mucho."),
      ("Entiendo inglés, pasé examen de inglés de nivel seis, y puedo hacer la conversación cotidiana en inglés.",
       "Entiendo inglés; aprobé el examen de inglés de nivel seis y puedo mantener una conversación cotidiana en inglés."),
      ("Si quieres una buena preparación, es mejor que no deje que el sudor bloquee los poros.",
       "Si quieres prepararte bien, es mejor que no dejes que el sudor te bloquee los poros.")],
},
17: {
 1: [("Hay una taquilla bonita en mi oficina.", "Hay una taquilla en mi oficina."),
     # 西语段尾部被 OCR 粘进一个 "51%"、中文段丢了开头的 "51% "，这里整条重排
     ("51% de los padres envían a sus hijos a los Estados Unidos para la educación superior. 51%",
      "51% de los padres envían a sus hijos a los Estados Unidos para la educación superior.",
      "51% 的家长想要送孩子去美国，以便能接受到最高等的教育。")],
 2: [("Veo los alumnos desde la tribuna.", "Veo los alumnos desde el podium.")],
 3: [("No mate dos pájaros de un tiro.", "No puedes matar dos pájaros de un tiro."),
     ("Ves lo todo como un espectador.", "Lo ves todo como un espectador.")],
 4: [("Recientemente, debido al frío, no he podido despertarme, aún con sueño.",
      "Recientemente, debido al frío, no he podido despertarme, aunque tengo sueño."),
     ("Yo abré las ventanas temprano esta mañana para ventilar.",
      "Abriré las ventanas temprano esta mañana para ventilar.")],
 6: [("No elegimos olvidar, elija recopilar y recoger en abismo del corazón.",
      "No elegimos olvidar, sino guardar en el abismo del corazón.")],
 7: [("Rápido que el profesor hable, los estudiantes son capaces de notar.",
      "Por muy rápido que hable el profesor, los estudiantes pueden anotarlo todo."),
     ("El director dio una locución a los estudiabtes.",                   # estudiabtes 拼写错
      "El director dio una locución a los estudiantes."),
     ("La tarjeta de estudiante te da derecho a un descuento para el viaje.",
      "La tarjeta de estudiante te da derecho a un descuento para viajar.")],
 8: [("¡Nosotros en los próximos años podremos lograr la automatización de la producción, orientando a las personas, fortaleciendo la gestión, y con los clientes estableceremos la cooperación sincera cogiendo la mano!",
      "En los próximos años lograremos la automatización de la producción, poniendo a las personas en el centro, fortaleciendo la gestión y estableciendo con los clientes una cooperación sincera de mano a mano."),
     ("La muerte de una lengua no es grave como lo que es, sino por lo que podría traer.",
      "La muerte de una lengua no es grave en sí misma, sino por lo que podría traer.")],
 9: [("Tengo el inconveniente en prestarte este libro.", "No puedo prestarte este libro."),
     ("¿Por qué faltan dos libros de < en > este estante?", "¿Por qué faltan dos libros en este estante?")],
},
}

# ---------------- 基础设施 ----------------
def _extract_json(t):
    i3 = t.index("={") + 1
    d = 0; j = i3; ins = False; esc = False
    while j < len(t):
        c = t[j]
        if ins:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == "{": d += 1
            elif c == "}":
                d -= 1
                if d == 0: break
        j += 1
    return json.loads(t[i3:j+1])

def load_ges():
    m = {}
    for i in range(48):
        fp = os.path.join(BASE, "data/sec/%d.js" % i)
        if not os.path.exists(fp): continue
        for s in _extract_json(open(fp, encoding="utf-8").read()).get("secs", []):
            for r in s.get("w", []) + s.get("e", []):
                if len(r) >= 7 and r[3] and r[4]: m.setdefault(norm(r[1]), (r[3], r[4]))
            for r in s.get("s", []):
                if len(r) >= 7 and r[3] and r[4]: m.setdefault(norm(r[0]), (r[3], r[4]))
    return m

class Alloc:
    def __init__(self, ges):
        self.ges = ges
        self.EXIST_ES = set(); self.EXIST_ZH = set()
        for fld, st in (("audio/es", self.EXIST_ES), ("audio/zh", self.EXIST_ZH)):
            for f in os.listdir(os.path.join(BASE, fld)):
                mm = re.match(r'(\d{5})\.mp3$', f)
                if mm: st.add(int(mm.group(1)))
        for i in range(48):
            fp = os.path.join(BASE, "data/sec/%d.js" % i)
            if not os.path.exists(fp): continue
            t = open(fp, encoding="utf-8").read()
            for mm in re.finditer(r'es/(\d{5})\.mp3', t): self.EXIST_ES.add(int(mm.group(1)))
            for mm in re.finditer(r'zh/(\d{5})\.mp3', t): self.EXIST_ZH.add(int(mm.group(1)))
        self.n_es = max(self.EXIST_ES) + 1; self.n_zh = max(self.EXIST_ZH) + 1
        self.jobs = []
    def next_es(self):
        n = self.n_es
        while n in self.EXIST_ES: n += 1
        self.n_es = n + 1; self.EXIST_ES.add(n)
        return "es/%05d.mp3" % n
    def es_zh(self, es, old_zh_path, zh_text):
        """返回 (es_path, zh_path, how)；中文没变就沿用旧 zh 音频。"""
        gp = self.ges.get(norm(es))
        if gp and os.path.exists(os.path.join(BASE, "audio", gp[0])):
            return gp[0], gp[1], "reuse"
        ep = self.next_es()
        if old_zh_path and os.path.exists(os.path.join(BASE, "audio", old_zh_path)):
            zp = old_zh_path
        else:
            zp = None
        self.jobs.append((es, ep, zh_text, zp))
        return ep, zp, "new"

def process(gid, wtab, etab, stab):
    fp = os.path.join(BASE, "data/sec/%d.js" % gid)
    t = open(fp, encoding="utf-8").read()
    o = _extract_json(t)
    ges = load_ges()
    al = Alloc(ges)
    applied = []
    for s in o["secs"]:
        no = s["no"]
        # W
        for r in s["w"]:
            for (ocn, oes, ncn, nes, npos) in wtab.get(no, []) + etab.get(no, []):
                if r[0] == ocn and r[1] == oes:
                    old_zh = r[4]
                    r[0], r[1], r[2] = ncn, nes, npos
                    r[3], r[4], how = al.es_zh(nes, old_zh, ncn)
                    if how == "new": r[5] = py(ncn)
                    r[6] = text_ipa(nes)
                    applied.append(("W", s["name"], ocn, oes, "->", nes, npos, how))
                    break
        # S
        for r in s["s"]:
            for tup in stab.get(no, []):
                if len(tup) == 3:
                    (oes, nes, nzh) = tup
                else:
                    (oes, nes) = tup; nzh = None
                if r[0] == oes:
                    old_zh = r[4]
                    r[0] = nes
                    if nzh: r[1] = nzh
                    r[3], r[4], how = al.es_zh(nes, old_zh, r[1])
                    if how == "new": r[5] = py(r[1])
                    r[6] = text_ipa(nes)
                    applied.append(("S", s["name"], oes[:40], nes[:40], "", "", how))
                    break
    for a in applied:
        print("  ", " | ".join(map(str, a)))
    out = 'window.BOOK_DATA=window.BOOK_DATA||{};window.BOOK_DATA[%d]=' % gid + \
          json.dumps(o, ensure_ascii=False, separators=(",", ":")) + ";"
    open(fp, "w", encoding="utf-8").write(out)
    print("sec/%d.js written | fixes=%d | new audio jobs=%d (next es=%d)" % (gid, len(applied), len(al.jobs), al.n_es))
    with open(os.path.join(BASE, "_tools/_jobs%d.json" % gid), "w", encoding="utf-8") as f:
        json.dump(al.jobs, f, ensure_ascii=False)
    return al.jobs

if __name__ == "__main__":
    which = sys.argv[1:] or ["16", "17"]
    for g in which:
        g = int(g)
        wtab = W.get(g, {}); etab = E.get(g, {}); stab = S.get(g, {})
        print("=== gid%d ===" % g)
        process(g, wtab, etab, stab)
