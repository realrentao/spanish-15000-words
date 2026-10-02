# -*- coding: utf-8 -*-
"""按文案重建 data/sec/<gid>.js（gid16 不同学校 / gid17 学校设置）。

用法: python rebuild_gid.py 16 | 17
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_parte_lib import Builder

# ---------------------------------------------------------------- gid16 不同学校
G16 = {
 "name": "不同学校",
 "raw": "_tools/parte16_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
   "typo": {
   "ensenanze": "enseñanza de adultos",   # 成人教育：漏 ñ
   "opinións": "opiniones",               # opi-nións 断行重连成了 opinións（正确是 opinions）
   "Estó": "Está",
   "a base de codos": "estudiando mucho", # 不地道 -> 靠努力学习
 },
 # (中文, clean_es 后的西语) -> 正确西语
 "fix": {
   ("幼儿园", "guardería"): "escuela infantil",      # 幼儿园=escuela infantil（guardería 更偏托儿所）
   ("附属中学", "escuela secundaria afiliada"): "escuela secundaria anexa",
   ("重点大学", "clave universidad"): "universidad de élite",   # clave 是「关键的」，顺序也反了
   ("高级中学", "preparatorio"): "preparatoria",      # 美式高中；preparatorio 是形容词
   ("师范学校", "escuela normal"): "escuela de magisterio",
   ("寄宿学校", "pensionado"): "internado",          # pensionado=寄宿/疗养院，寄宿学校=internado
   ("停学", "suspensión de la escuela"): "suspensión escolar",
   ("延长", "extender"): "prolongar",
   ("笔试", "examen por escrito"): "examen escrito",
   ("试卷", "hoja"): "hoja de examen",
   ("复习", "revisar"): "repasar",                   # 复习(功课本)=repasar；revisar=检查/浏览
 },
 "pos": {
   ("笔试", "examen escrito"): "",                   # 文案标了 v.t.，但「笔试」是名词短语
   ("复习", "repasar"): "v.t.",
   ("延长", "prolongar"): "v.t.",
   ("值得", "merecer"): "v.t.",            # merecer 是及物动词
 },
 "subs": [
   ("Estó preparando", "Está preparando"),
   ("a base de codos", "estudiando mucho"),
   ("pasé examen de inglés", "pasé el examen de inglés"),
   # 中文以「1870年…」开头，西语段被带走了数字 -> 截断到句点
   ("luchó con valentía. 1870", "luchó con valentía."),
 ],
}

# ---------------------------------------------------------------- gid17 学校设置
G17 = {
 "name": "学校设置",
 "raw": "_tools/parte17_raw.txt",
 "typo": {
   "estudiabtes": "estudiantes",                    # 校対 estudiabtes
 },
 "fix": {
   # Sec1 各个科室
   ("注册", "registrar"): "matricular",
   ("校长室", "oficina del presidente"): "oficina del director",
   ("讲师办公室", "oficina de instructor"): "oficina de los profesores",
   ("研究生办公室", "oficina de máster"): "oficina de posgrado",
   # Sec2 教室
   ("幕布", "cortina"): "pantalla",
   ("讲台", "plataforma"): "estrado",
   ("讲台", "tribuna"): "podio",
   ("教科书", "manual"): "libro de texto",
   # Sec3 操场
   ("地面", "tierra"): "suelo",
   ("秋千", "oscilación"): "columpio",
   ("跳绳", "saltar"): "saltar a la cuerda",
   # Sec4 宿舍
   ("广播", "emisión"): "radio",
   ("被子", "cobertura"): "manta",
   # Sec5 画室
   ("人物", "carácter"): "personaje",
   ("水粉画", "pintura de gouache"): "pintura al gouache",
   ("画夹", "bordo"): "carpeta",
   ("画笔", "cepillo"): "pincel",
   # Sec7 校园人员
   ("助教", "asistente"): "ayudante",
   ("导师", "instructor"): "tutor",
   ("行政人员", "persona administrativa"): "personal administrativo",
   ("转校生", "estudiante de transferencia"): "estudiante transferido",
   # Sec8 常见院系
   ("海洋科学", "ciencia oceánica"): "oceanografía",
   ("财务", "finanza"): "finanzas",
   ("人力资源", "recurso humano"): "recursos humanos",
   # Sec9 图书馆
   ("期刊", "periódico"): "publicación periódica",
   ("借", "prestar"): "tomar prestado",
   ("租赁期限", "plazo del arrendamiento"): "plazo del préstamo",
   ("到期的", "vencimiento"): "vencido",
   ("章", "sello"): "capítulo",
   # 词汇大拓展
   ("（办公室中的）文件柜", "taquilla"): "armario",
   ("椅子", "silla"): "silla",
   ("走动", "excursion"): "paseo",
   ("讲话", "locución"): "discurso",
 },
 "pos": {
   ("投影仪", "proyector"): "n.m.",
   ("幕布", "pantalla"): "n.f.",
   ("讲台", "estrado"): "n.m.",
   ("讲台", "podio"): "n.m.",
   ("教科书", "libro de texto"): "n.m.",
   ("地面", "suelo"): "n.m.",
   ("秋千", "columpio"): "n.m.",
   ("跳绳", "saltar a la cuerda"): "v.i.",
   ("广播", "radio"): "n.f.",
   ("被子", "manta"): "n.f.",
   ("睡觉", "dormir"): "v.i.",
   ("人物", "personaje"): "n.m.",
   ("水粉画", "pintura al gouache"): "n.f.",
   ("画夹", "carpeta"): "n.f.",
   ("画笔", "pincel"): "n.m.",
   ("助教", "ayudante"): "n.",
   ("代理的", "interino"): "adj.",
   ("导师", "tutor"): "n.m.",
   ("转校生", "estudiante transferido"): "n.m.",
   ("海洋科学", "oceanografía"): "n.f.",
   ("人力资源", "recursos humanos"): "n.m.",
   ("租赁期限", "plazo del préstamo"): "n.m.",
   ("到期的", "vencido"): "adj.",
   ("电子版", "versión electrónica"): "",
   ("章", "capítulo"): "n.m.",
   ("注册", "matricular"): "v.t.",
   ("校长室", "oficina del director"): "",
   ("讲师办公室", "oficina de los profesores"): "",
   ("研究生办公室", "oficina de posgrado"): "",
   # 词汇大拓展词性
   ("（办公室中的）文件柜", "armario"): "n.f.",
   ("椅子", "silla"): "n.f.",
   ("学生", "alumno"): "n.m.",
   ("走动", "paseo"): "n.m.",
   ("讲话", "discurso"): "n.m.",
 },
 "subs": [
   # Sec1
   ("Hay una taquilla bonita en mi oficina", "Hay un armario bonito en mi oficina"),
   # Sec3
   ("Ves lo todo como un espectador", "Lo ves todo como un espectador"),
   ("No mate dos pájaros de un tiro", "No puedes cazar dos pájaros de un tiro"),
   # Sec4
   ("debido al frío, no he podido despertarme, aún con sueño",
    "debido al resfriado, no he podido despertarme y sigo teniendo sueño"),
   ("Yo abré las ventanas", "Abriré las ventanas"),
   ("Coge las pinzas y tiende las sábanas", "Toma las pinzas y tiende las sábanas"),
   # Sec5
   ("El pintor caracteriza a sus personajes bien", "El pintor caracteriza bien a sus personajes"),
   ("Mire cuidadosamente los cajones para buscar su goma",
    "Mira bien los cajones para encontrar tu goma"),
   # Sec6
   ("No elegimos olvidar, elija recopilar y recoger en abismo del corazón",
    "No elegimos olvidar; elegimos recordar y guardar en lo más hondo del corazón"),
   # Sec7
   ("La tarjeta de estudiante te da derecho a un descuento para el viaje",
    "La tarjeta de estudiante te da derecho a un descuento en los viajes"),
   ("Rápido que el profesor hable, los estudiantes son capaces de notar",
    "Por más rápido que hable el profesor, los estudiantes pueden anotarlo todo"),
   ("El director dio una locución a los estudiantes",
    "El director dio un discurso a los estudiantes"),
   ("Le enseñaré a hablar el español", "Le enseñaré a hablar español"),
   # Sec8
   ("Nosotros en los próximos años podremos lograr la automatización de la producción, orientando a las personas, fortaleciendo la gestión, y con los clientes estableceremos la cooperación sincera cogiendo la mano",
    "En los próximos años podremos lograr la automatización total de la producción, orientándonos a las personas, fortaleciendo la gestión y estableciendo con los clientes una cooperación sincera, ¡de la mano!"),
   ("La muerte de una lengua no es grave como lo que es",
    "La muerte de una lengua no es grave por sí misma"),
   # Sec9
   ("Tengo el inconveniente en prestarte este libro", "No puedo prestarte este libro"),
   # clean_es 已经把 OCR 的 "< en >" 清成单个空格，这里不能再按原双空格匹配
   ("faltan dos libros de este estante", "faltan dos libros en este estante"),
   # 中文以「51%的家长…」开头，把西语尾部的 51% 一起吞了 -> 截断
   ("superior. 51%", "superior."),
   # 原句尾已有一个 "!"，替换串别再带一个（否则 ¡de la mano!!）
   ("una cooperación sincera, ¡de la mano!", "una cooperación sincera, ¡de la mano"),
 ],
}

# ---------------------------------------------------------------- gid19 文科类学习
G19 = {
 "name": "文科类学习",
 "raw": "_tools/parte19_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 # （sue.o / peque.o / extra.o / a.os 由 clean_es 的「元音间.->ñ」已自动修好，这里只补真实残损）
 "typo": {
   "aréa": "área",                       # aréa -> área
 },
 # (中文, clean_es 之后的西语) -> 正确西语
 "fix": {
   # Sec1 人文学科
   ("文科", "ciencia humana"): "ciencias humanas",        # 文科=ciencias humanas（恒用复数）
   ("人文学科", "ciencia de la humanidad"): "humanidades",
   ("图书馆学", "la ciencia de biblioteca"): "biblioteconomía",
   # Sec2 外语学习
   ("口语", "lenguaje oral"): "expresión oral",
   ("句子", "frase"): "oración",                          # 词组=frase；句子=oración（原与「词组」撞词）
   ("语调", "tono de voz"): "entonación",                 # 语调=entonación；tono de voz=嗓音
   # Sec3 阅读
   ("浏览", "navegar"): "hojear",                         # 浏览(书报)=hojear；navegar 是上网浏览
   ("跳读", "saltar en leer"): "leer a saltos",           # 原表达不成句
   # Sec6 文学作品类型
   ("民间文学", "folclore"): "literatura popular",         # folclore=民间文化/民俗，非「民间文学」
   ("中篇小说", "novela"): "novela media",
   ("话剧", "teatro"): "obra de teatro",                  # 与「戏剧 teatro」撞词，话剧=obra de teatro
   # Sec7 故事
   ("情节", "acción"): "trama",                           # 情节=trama；acción 是「动作/行动」
   ("冒险", "riesgo"): "aventura",                        # 冒险=aventura；riesgo=风险
   ("结局", "resultar"): "desenlace",                     # 结局是名词，resultar 是「结果是」的动词
   # Sec8 童话故事
   ("魔力药剂", "farmacia mágica"): "poción mágica",      # farmacia=药店/药学
   # Sec9 小说
   ("言情小说", "historia de amor"): "novela romántica",
   ("卷", "rollo"): "volumen",                            # rollo=卷轴/麻烦，书卷=volumen
 },
 # 词性：只补文案标过的（n./n.m. 补全）；文案标错的才在这里纠正
 "pos": {
   ("单词", "palabra"): "n.f.",                           # palabra 是阴性（书里标 n.m. 是错的）
   ("完整的", "completo"): "adj.",                        # 「完整的」是形容词，书里写 n.m.
   ("结局", "desenlace"): "n.m.",                         # 书里写 resultar v.t.（动词，与中文词义不符）
   ("剧本的", "del guión"): "",                           # 不是形容词，文案没标词性 -> 留空
   # 文案只写「n.」的补全为 n.m.
   ("心理学家", "psicólogo"): "n.m.",
   ("剧作家", "dramaturgo"): "n.m.",
   ("巨人", "gigante"): "n.m.",
   ("吸血鬼", "vampiro"): "n.m.",
   ("作者", "autor"): "n.m.",
   ("小说家", "novelista"): "n.m.",
   ("侦探", "detective"): "n.m.",
   ("矮子", "enano"): "n.m.",
   # 文案已标、仅确认
   ("美语", "inglés americano"): "n.m.",
   ("英语", "inglés británico"): "n.m.",
   ("前置词", "preposición"): "n.f.",
   ("代词", "pronombre"): "n.m.",
   ("动词", "verbo"): "n.m.",
   ("名词", "nombre"): "n.m.",
   ("翻译", "traducir"): "v.t.",
   ("思考", "pensar"): "v.t.",
   ("学习", "estudiar"): "v.t.",
   ("挖", "cavar"): "v.t.",
   ("混合", "mezclar"): "v.t.",
   ("诱导", "inducir"): "v.t.",
   ("沉思", "contemplar"): "v.t.",
   ("诅咒", "maldecir"): "v.t.",
   ("描述", "describir"): "v.t.",
   ("浏览", "hojear"): "v.t.",
   ("独立地", "independientemente"): "adv.",
   ("考古学的", "arqueológico"): "adj.",
   ("复数的", "plural"): "adj.",
   ("古典的", "clásico"): "adj.",
   ("中篇小说", "novela media"): "n.f.",
   ("自恋的", "narcisista"): "adj.",
   ("幽默的", "humorístico"): "adj.",
   ("兴奋的", "emocionado"): "adj.",
   ("复杂的", "complejo"): "adj.",
   ("古怪的", "extraño"): "adj.",
   ("荒唐的", "ridículo"): "adj.",
   ("残忍的", "despiadado"): "adj.",
   ("愚蠢的", "estúpido"): "adj.",
   ("神秘的", "misterioso"): "adj.",
   ("历史的", "histórico"): "adj.",
   ("认知能力的", "cognitivo"): "adj.",
   ("详细的", "detallado"): "adj.",
   ("博学的", "erudito"): "adj.",
   ("广泛的", "vasto"): "adj.",
   ("独立的", "independiente"): "adj.",
   ("心理学的", "psicológico"): "adj.",
   ("冒险", "aventura"): "n.f.",
   ("卷", "volumen"): "n.m.",
   ("剧本", "guión"): "n.m.",
   ("小说", "novela"): "n.f.",
   ("短篇小说", "cuento"): "n.m.",
   ("侦探小说", "novela de detectives"): "",                # 文案未标词性 -> 留空
   ("言情小说", "novela romántica"): "",                    # 文案未标词性 -> 留空
   ("小说家", "novelista"): "n.m.",
   ("改编，改写", "adaptación"): "n.f.",
   ("情节，梗概", "argumento"): "n.m.",
   ("材料", "material"): "n.m.",
   ("沉默", "silencio"): "n.m.",
   ("知识", "conocimiento"): "n.m.",
   ("范围", "esfera"): "n.f.",
   ("范围", "campo"): "n.m.",
   ("学问，科学", "ciencia"): "n.f.",
   ("时期，时代", "edad"): "n.f.",
   ("葬礼", "funeral"): "n.m.",
   ("陶器", "cerámica"): "n.f.",
   ("意识", "conciencia"): "n.f.",
   ("混乱", "confusión"): "n.f.",
   ("认知", "cognición"): "n.f.",
   ("依赖性", "dependencia"): "n.f.",
   ("心理障碍", "bloqueo"): "n.m.",
   ("语调", "entonación"): "",                            # 文案未标词性 -> 留空
   ("散文", "prosa"): "n.f.",
   ("讽刺作品", "sátira"): "n.f.",
   ("十四行诗", "soneto"): "n.m.",
   ("轶事", "anécdota"): "n.f.",
   ("寓言", "alegoría"): "n.f.",
   ("笑话", "broma"): "n.f.",
   ("虚构", "ficción"): "n.f.",
   ("情节", "trama"): "n.f.",
   ("故事", "historia"): "n.f.",
   ("魔法", "magia"): "n.f.",
   ("魔法师", "mago"): "n.m.",
   ("女巫", "bruja"): "n.f.",
   ("怪物", "monstruo"): "n.m.",
   ("小精灵", "elfo"): "n.m.",
   ("魔杖", "varita"): "n.f.",
   ("咒语", "encantamiento"): "n.m.",
   ("炼金术", "alquimia"): "n.f.",
   ("童话", "cuento"): "n.m.",
   ("印刷", "impresión"): "n.f.",
   ("装订", "encuadernación"): "n.f.",
   ("版权", "derecho de autor"): "",                        # 文案未标词性 -> 留空
 },
 "subs": [
   # Sec1
   ("Desde un punto de vista psicológica, la posición en la familia, afectará a la personalidad",
    "Desde el punto de vista psicológico, el lugar que se ocupa en la familia afecta a la personalidad"),
   ("en la vida, cada destino también es un nuevo comienzo",
    "en la vida, cada final también es un nuevo comienzo"),
   ("La literatura dice que unas cosas se han ido, y las cosas desaparecidas contradictoriamente siguen viviendo para siempre",
    "La literatura dice que unas cosas se han ido y, de forma contradictoria, que las cosas desaparecidas siguen viviendo para siempre"),
   # Sec2
   ("como \"que\", y \"el uno\"", "como «qué» o «cuál»"),
   # Sec3
   ("En la área de ciencia, los chinos tienen un conocimiento de la ciencia europea preciso igualmente",
    "En el ámbito de la ciencia, los chinos conocen la ciencia europea igual de bien"),
   ("sino también un símbolo de la propia sustancia", "sino también la propia sustancia"),
   # Sec4
   ("El hombre no había dejado de pensar en descubrir el misterio y mejorar el proceso",
    "El ser humano nunca ha dejado de tratar de descubrir el misterio y perfeccionar el proceso"),
   ("Su forma y función realmente es un tesoro de la nación china, simbolizado orgullo para los chinos",
    "Su forma y su función son realmente un tesoro de la nación china y un símbolo de orgullo para los chinos"),
   # Sec5
   ("Todos amamos a nuestra madre sin saberlo, y en general damos cuenta del amor tan profundo hasta la última separación",
    "Todos amamos a nuestra madre sin saberlo y sólo nos damos cuenta de este amor tan profundo en el momento de la última separación"),
   ("Tu comportamiento puede reflejar tu actitud de la vida",
    "Tu comportamiento refleja tu actitud hacia la vida"),
   # Sec6
   ("Las culturas del este y del mundo se mezclan con la combinación de la tecnología moderna y la técnica clásica",
    "Las culturas de Oriente y del mundo se mezclan, combinando la tecnología moderna con la técnica clásica"),
   ("Hay momentos en la vida de felicidad que ningún poema puede resumirlos",
    "Hay momentos de felicidad en la vida que ningún poema puede resumir"),
   # Sec7
   ("Esta historia atrae a personas", "Esta historia atrae a la gente"),
   ("El escenario de la acción del filme es Roma", "La trama de la película se desarrolla en Roma"),
   ("El hombre invisible es una famosa novela de ciencia ficción. 《",
    "El hombre invisible es una famosa novela de ciencia ficción."),
   ("隐形人》是一部有名的科幻小说。",
    "《隐形人》是一部有名的科幻小说。"),
   # Sec8
   ("No deje que sus ideas se mantengan en la cabeza, hay que actuar, no sea el gigante en papel, pero el enano en acción",
    "No dejes que tus ideas se queden sólo en la cabeza: hay que actuar. No seas un gigante en papel y un enano en acción"),
   # Sec9
   ("Ellos respondieron: “.Por qué tenemos miedo a un sombrero?”",
    "Ellos respondieron: «¿Por qué tenemos miedo a un sombrero?»"),
   ("Reci\u00e9n termin\u00e9 de leer el tercer cap\u00edtulo de la novela",
    "Acabo de terminar de leer el tercer cap\u00edtulo de la novela"),
   ("Mostr\u00e9 mi obra a los mayores y les pregunt\u00e9 si el dibujo les asustaba",
    "Les mostré mi obra a los adultos y les pregunté si el dibujo les asustaba"),
 ],
 # S 句中文修正（OCR 残损 / 与西语语义不符）
 "zh_subs": [
   # Sec2 中文残损：「例如que, el uno。」
   ("在一个疑问句子里面，我们当然要用一个疑问代词，例如que, el uno。",
    "在一个问句里，我们当然要用一个疑问代词，例如 «qué» 或 «cuál»。"),
   # Sec9 中文与西语语义对不上（西语 = 为什么要怕一顶帽子）
   ("他们回答我说:“一顶帽子有什么可怕的？”",
    "他们回答说:“我们为什么要怕一顶帽子呢？”"),
   ("隐形人》是一部有名的科幻小说。",
    "《隐形人》是一部有名的科幻小说。"),
 ],
}

G20 = {
 "name": "理科类学习",
 "raw": "_tools/parte20_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "Principíto": "Principito",
   "armi.o": "armiñado",
   "armiño": "armiñado",
   "puntuacion": "puntuación",
 },
 "fix": {
   # Sec2 电学：义项错配
   ("电学家", "científico de la ciencia eléctrica"): "electricista",   # 电学家=电工/electricista
   ("电子爱好者", "electrofilia"): "aficionado a la electrónica",       # electrofilia 不是西语词
   ("电压", "tensión"): "voltaje",                                      # 电压=voltaje；tensión=张力
   ("电容", "capacitancia"): "capacidad",                               # 西语电容=capacidad
   # Sec3 几何
   ("边", "borde"): "lado",                                             # 几何「边」=lado；borde=边缘
   ("中点", "centro"): "punto medio",                                   # 中点=punto medio
   # Sec4 算术符号
   ("减", "reducir"): "restar",                                         # 减法=restar；reducir=减少
 },
 "pos": {
   # 文案标了 n. / 标错性数的，按西语实际词性
   ("电容", "capacidad"): "n.f.",
   ("电子爱好者", "aficionado a la electrónica"): "n.m.",
   ("电压", "voltaje"): "n.m.",
   # 文案未标词性 -> 一律留空（铁律）
   ("电学家", "electricista"): "",
   ("一套符号", "conjunto de símbolos"): "",
   ("平方根", "raíz cuadrada"): "",
   ("立方根", "raíz cúbica"): "",
   ("正号", "signo positivo"): "",
   ("负号", "signo negativo"): "",
   # Sec5
   ("收入， 进项", "ingresos"): "n.m.pl.",
   ("冰箱", "refrigerador"): "n.m.",
 },
 "subs": [
   # Sec1 自然科学
   ("La selección natural, la supervivencia del más apto es la ley de la naturaleza y es eterna",
    "La selección natural, es decir, la supervivencia del más apto, es una ley de la naturaleza que es eterna"),
   ("El Principito miró a su alrededor para sentarse, pero el planeta entero estaba lleno de hermoso manto armiñado. Permaneció de pie, y como estaba cansado, bostezó",
    "El Principito miró a su alrededor para sentarse, pero el planeta entero estaba cubierto de un hermoso manto armiñado. Permaneció de pie y, como estaba cansado, bostezó"),
   # Sec2 电学（ha sido recuperado 性别/搭配错 + 灯泡= bombilla）
   ("En la ciudad más afectada por el terremoto, la electricidad de algunos edificios ha sido recuperado. Algunos sistemas se han establecido, pero los residentes todavía tendrán que esperar órdenes",
    "En la ciudad más afectada por el terremoto, la electricidad de algunos edificios se ha restablecido. Algunos sistemas se han establecido, pero los residentes todavía tendrán que esperar órdenes"),
   ("El descubrimiento de la luz eléctrica fue un gran adelanto",
    "La invención de la bombilla fue un gran adelanto"),
   # Sec3 平面几何图形
   ("El trono de la cúbica nos informa de que el emperador gobierna un mundo material. Cuatro es la señal de estabilidad, siendo el número de un mundo finito",
    "El trono de la cúbica nos informa de que el emperador gobierna un mundo material. El cuatro es la señal de estabilidad, el número de un mundo finito"),
   ("Es un triángulo rectángulo, y mantener el mismo triángulo",
    "Es un triángulo rectángulo y hay que mantenerlo igual"),
   # Sec4 各种符号
   ("A decir que hoy es domingo es equivalente a decir que no tengo que ir a trabajar",
    "Decir que hoy es domingo es equivalente a decir que no tengo que ir a trabajar"),
   ("Con el crecimiento de la población, los científicos han visto un número creciente de casos de cáncer",
    "Con el crecimiento de la población, los científicos han observado un número creciente de casos de cáncer"),
   # Sec5 常见元素与岩石
   ("Estamos provistos de carbón para todo el invierno",
    "Estamos abastecidos de carbón para todo el invierno"),
   ("La marea cubría ya las rocas", "La marea ya cubría las rocas"),
 ],
}

G21 = {
 "name": "求职与面试",
 "raw": "_tools/parte21_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "familien": "familiaricen",              # se familien -> se familiaricen
   "ma-.ano": "mañana",                     # 断行残损：ma-.ano
   "compa.ía": "compañía",                  # a.í 不在 clean 的 ñ 自愈字符集里
 },
 "fix": {
   # Sec2 简历
   ("简历", "curriculum vitae"): "currículum vitae",      # 规范写法带重音
   ("籍贯", "zona de origen"): "lugar de origen",
   ("到职日期", "fecha de vencimiento"): "fecha de inicio",  # vencimiento=到期日，义项错
   # Sec3 优点描述
   ("有进取心的", "agresivo"): "ambicioso",                 # agresivo=有攻击性的
   ("仔细的", "menudo"): "cuidadoso",                       # menudo=细小的
   ("一丝不苟的", "escrupulosa"): "escrupuloso",            # 形容词条用阳性形式
   # Sec4 缺点描述
   ("贪婪的", "hambriento"): "avaro",                       # hambriento=饥饿的
   ("呆板的", "pesado"): "rígido",                           # pesado=沉重的/无聊的
   # Sec5 个人经历
   ("任命", "nombrado"): "nombrar",                         # 动词条应用原形
   ("突破", "taladrar"): "superar",                          # taladrar=钻孔
   ("背景", "circunstancia"): "contexto",                   # circunstancia=情况
   # Sec6 面试
   ("解决", "desatar"): "resolver",                         # desatar=解开(绳)
   ("提前", "avanzar"): "adelantar",                         # avanzar=前进
   # Sec7 薪酬福利
   ("加薪", "aumentar"): "aumento de sueldo",
   ("年终奖", "premios de fin de año"): "premio de fin de año",
   # Sec8 保险
   ("保险单", "fórmula de garantía"): "póliza de seguro",    # fórmula=公式，义项错
   ("保险公司", "empresa de seguro"): "empresa de seguros",  # 西语惯用复数
   ("索赔", "reclamar una indemnización"): "reclamación",
   # Sec9 员工入职
   ("试用期", "libertad condicional"): "periodo de prueba",  # libertad condicional=假释，严重错
   ("签到处", "la parte de registro"): "la recepción",
   # Sec11 常见职位
   ("会计", "contabilidad"): "contador",                    # contabilidad=会计(学)，人是 contador
 },
 "pos": {
   # 文案标错性别的，按西语实际词性
   ("奖金", "premio"): "n.m.",
   ("表现", "rendimiento"): "n.m.",
   ("医疗保险", "seguro médico"): "n.m.",
   ("人员", "personal"): "n.m.",
   ("同事", "colega"): "n.m.",
   ("总经理", "gerente general"): "n.m.",
   ("接待员", "recepcionista"): "n.m.",
   ("行政人员", "administrador"): "n.m.",
   ("代理", "agente"): "n.m.",
   # 短语无词性 -> 清空
   ("没有耐性的", "sin paciencia"): "",
   ("加薪", "aumento de sueldo"): "",
   # 修正后西语的真实词性
   ("会计", "contador"): "n.m.",
   ("背景", "contexto"): "n.m.",
 },
 "subs": [
   # Sec1 找工作
   ("La publicidad es un arte, es la necesidad de entusiasmo, se requiere creatividad y la acumulación",
    "La publicidad es un arte: requiere entusiasmo, creatividad y acumulación"),
   ("La contratación de empleados es un trabajo de mucho tiempo y requiere mucha paciencia y energía",
    "La contratación de empleados lleva mucho tiempo y requiere mucha paciencia y energía"),
   # Sec2 简历
   ("El entrevistador puede preguntarle si tiene alguna duda acerca de sus respuestas en la elección de su especialidad",
    "El entrevistador puede preguntarle si tiene alguna duda acerca de sus respuestas sobre la elección de su especialidad"),
   ("Este chico tiene muy bien curriculum vitae",
    "Este chico tiene un curriculum vitae muy bueno"),
   # Sec3 优点描述
   ("Es un niño con un talento muy creative", "Es un niño con un talento muy creativo"),
   ("La cuestión se puso en serio a la representación nacional por los senadores",
    "La cuestión será presentada ante la representación nacional por los senadores con mucha seriedad"),
   # Sec4 缺点描述（逗号粘连 -> 分号）
   ("Era siempre el hombre impasible, el miembro imperturbable del club de reforma, ningún incidente o accidente podría sorprenderle",
    "Era siempre el hombre impasible, el miembro imperturbable del club de reforma; ningún incidente o accidente podría sorprenderle"),
   # Sec5 个人经历
   ("Soy nombrado su abogado", "He sido nombrado su abogado"),
   ("La gente se siente incapaz de entender la expresión",
    "Es una expresión que la gente no puede entender"),
   ("Cuando tratamos de controlar la población, decís que es una violación de los derechos humanos",
    "Cuando tratamos de controlar la población, dices que es una violación de los derechos humanos"),
   # Sec6 面试
   ("La oportunidad de conocer su hombre de la vida, nadie quiere perderla",
    "La oportunidad de conocer al hombre de tu vida, nadie quiere perderla"),
   ("Frente a esta crisis me doy cuenta de la responsabilidad mía",
    "Frente a esta crisis, me doy cuenta de mi responsabilidad"),
   # Sec7 薪酬福利
   ("No estoy de acuerdo, porque va a aumentar el costo",
    "No estoy de acuerdo, porque eso va a aumentar el costo"),
   # Sec8 保险
   ("Están aseguradas las necesidades esenciales del pueblo en la alimentación y vestido",
    "Están aseguradas las necesidades esenciales del pueblo en la alimentación y el vestido"),
   # Sec9 员工入职
   ("Reflets proporciona la gramática y el vocabulario básicos y permite que los estudiantes se familiaricen con diferentes documentos",
    "Reflets proporciona la gramática y el vocabulario básicos y permite que los estudiantes se familiaricen con distintos documentos"),
   ("Reflets proporciona la gramática y el vocabulario básicos y permite que los estudiantes se familiaricen con distintos documentos. Reflets",
    "Reflets proporciona la gramática y el vocabulario básicos y permite que los estudiantes se familiaricen con distintos documentos."),
   ("Van a reemplazarme con un colega", "Van a sustituirme por un colega"),
   ("La Sección es una función interna de consultoría de gestión",
    "La sección es una unidad interna de consultoría de gestión"),
   ("Asistió a la conferencia por su colega", "Asistió a la conferencia en lugar de su colega"),
   # Sec10 公司部门
   ("Nuestras áreas de mercado están en todas partes y cualquier profesional de la emisión, excepto en supermercados muy grandes",
    "Nuestras áreas de mercado están en todas partes: cualquier profesional de la emisión, salvo en los supermercados muy grandes"),
   # Sec11 常见职位
   ("Has hablado con tu gerente de tu salario?",
    "¿Has hablado con tu gerente sobre tu salario?"),
   # Sec11 句尾是全角「！」，西语必须用半角并配「¡」
   ("Hoy somos amigos, mañana somos socios de cooperación, nos ayudamos uno a otro a conseguir éxito！",
    "¡Hoy somos amigos, mañana somos socios de cooperación, nos ayudamos uno a otro a conseguir éxito!"),
 ],
 "zh_subs": [
   # Sec6 错字「旳」
   ("人生是一种没有办法抗拒旳前进。", "人生是一种没有办法抗拒的前进。"),
   # Sec5 中文与西语不符（「义务辩护律师」是误译）
   ("我被任命担任你的义务辩护律师。", "我被任命为他的律师。"),
   # Sec9 中文以产品名 Reflets 开头，被 split_s 误判成西语尾巴
   ("提供了语法和词汇的基础",
    "Reflets 提供了语法和词汇的基础"),
 ],
}

G22 = {
 "name": "办公室",
 "raw": "_tools/parte22_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "traido": "traído",                 # ¿Has traido tu libreta? -> traído
   "ha blando": "hablando",            # 空格代替连字符，clean 的断行重连救不了
   "sólo": "solo",                     # RAE 2010 起 sólo 不再加重音
   "Sólo ": "Solo ",                   # 句首大写形态（句子处）
 },
 "fix": {
   # Sec1 办公室
   ("废纸篓", "residuo"): "papelera",                    # residuo=残留物
   ("建议，提议", "propuesto"): "propuesta",             # propuesto 是分词/形容词，名词为 propuesta
   # Sec2 办公桌
   ("门铃", "carillón"): "timbre",                      # carillón=钟/钟声
   ("地球仪", "modelo de la tierra"): "globo terráqueo",
   ("笔筒", "estuche de plumas"): "portapapeles",        # estuche=盒子
   ("耳机", "auricular"): "auriculares",                # 耳机=复数
   # Sec3 办公用品及设备
   ("回形针", "trombón"): "clip",                       # trombón=长号
   ("橡皮", "goma"): "goma de borrar",
   # Sec4 会议室
   ("主持人", "presentador"): "moderador",              # presentador=节目主持
   ("议事单", "procedimiento único"): "procedimiento",  # único=唯一的，义项错
   ("完成", "lograr"): "completar",                      # lograr=达到
   # Sec5 一般电脑操作
   ("剪切", "esquilar"): "cortar",                      # esquilar=剪毛
   ("回车", "entrar"): "intro",                          # 回车键=Intro/Enter
   ("睡眠", "dormir"): "suspender",                      # 睡眠模式=suspender
   ("播放", "jugar"): "reproducir",                      # jugar=玩
   ("锁定", "fijar"): "bloquear",
   ("关机", "cerrar"): "apagar",
   # Sec6 传真
   ("看不清的", "trastorno"): "ilegible",               # trastorno=紊乱/故障
   ("拨号", "marque"): "marcado",                        # marque=疑问词
   ("重新传真", "refax"): "reenviar por fax",
 },
 "pos": {
   # 文案标错性别的，按西语实际词性
   ("主持人", "moderador"): "n.m.",
   ("回车", "intro"): "n.m.",
   ("睡眠", "suspender"): "v.t.",
   ("拨号", "marcado"): "n.m.",
   ("建议，提议", "propuesta"): "n.f.",
   # tanto 是副词/代词，不是形容词
   ("这么多的", "tanto"): "adv.",
 },
 "subs": [
   # Sec1 办公室
   ("Hay una taquilla bonita en mi oficina",
    "Hay un archivador bonito en mi oficina"),            # taquilla=服务窗口
   ("Principalmente para consumidores empleados de oficina",
    "Principalmente para los consumidores de oficina"),    # 原句语法不通
   # Sec2 办公桌
   ("Qué oficio tiene este documento?",
    "¿Para qué sirve este documento?"),                   # 中文=这份文件是干什么的
   # Sec3 办公用品及设备（主语一致 / 语序）
   ("Yo fingía pedir grapadora y la robó desde su cajón",
    "Yo fingí pedir la grapadora y la robé de su cajón"),
   ("No puedes almacenar tantas fotos en el ordenador porque está llena la memoria",
    "No puedes almacenar tantas fotos en el ordenador porque la memoria está llena"),
   # Sec4 会议室（typo 表已把 sólo -> solo，键要写处理后的形态）
   ("Solo necesitamos 16 niños a participar",
    "Solo necesitamos 16 niños para participar"),
   ("El tema de la conferencia es desarrollo",
    "El tema de la conferencia es el desarrollo"),
   ("Al final llegaron a en consenso",
    "Al final llegaron a un consenso"),
   ("No estaba de acuerdo con la clausura del tratado",
    "No estaba de acuerdo con la cláusula del tratado"),  # clausura=闭幕
   # Sec5 一般电脑操作
   ("Si incluso no tiene el coraje de eliminar esta sombra, es realmente desesperada",
    "Si ni siquiera tiene el coraje de eliminar esa sombra, es realmente desesperada"),
   # Sec6 传真
   ("Si quiere una copia, no tenía más que decirlo. Sabe si tardará mucho.",
    "Si quiere una copia, no tiene más que decirlo."),
   # Sec6 开头的「¡」被 split_s/clean 的 lstrip 削掉，必须显式补回（否则 ¡Canasto! 变成 Canasto!）
   ("Canasto! He perdido la cartera.",
    "¡Canasto! He perdido la cartera."),
 ],
 "zh_subs": [
   # Sec3 光盘=disco，不是唱片
   ("他想要录制一张唱片。", "他想要刻录一张光盘。"),
 ],
}

G23 = {
 "name": "职场百态",
 "raw": "_tools/parte23_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "Roachrag": "organizadores",            # OCR 把 organizada 认成 Roachrag
   "conclusion": "conclusión",              # 缺重音，clean 的 ñ 自愈救不了
 },
 "fix": {
   # Sec1 上班
   ("轮班", "desplazamiento"): "turno",
   ("轮班表", "tabla de desplazamiento"): "tabla de turnos",
   ("假期", "vacación"): "vacaciones",     # 假期（可数复数）=vacaciones
   ("使疲倦的", "agotador"): "agotador",
   # Sec2 升职
   ("尝试", "tratar"): "tratar de",        # 尝试=tratar de；tratar 单用=对待
   ("进步，进展", "avanzar"): "avance",    # 「进展」是名词
   # Sec3 与同事相处
   # Sec4 工作量
   ("抱怨", "culpar"): "protestar",        # 第二条「抱怨」；culpar=指责
   # Sec5 工作状态（强迫/表扬/赞美 义项错）
   ("强迫", "forzar"): "obligar",           # forzar=强行夺取
   ("表扬", "exaltar"): "elogiar",          # exaltar=颂扬/激昂
   ("赞美", "celebrar"): "alabar",          # celebrar=庆祝
   # Sec5 工作状态
   ("坚持不懈", "perseverancia"): "perseverancia",
   # Sec6 沟通与竞争
   ("竞争的", "competido"): "competitivo", # competido=拥挤的/争用的
   # Sec7 出差
   ("出差", "viaje de negocio"): "viaje de negocios",   # 西语惯用复数
   ("压力的", "presión"): "presivo",      # «形容词»不能用名词 presión
   # Sec8 退休与离职
   ("退休卡", "tarjeta del retiro"): "tarjeta de jubilación",
 },
 "pos": {
   # 文案标错性别的，按西语实际词性
   ("日班", "turno de día"): "n.m.",       # turno 阳性
   ("晚班", "turno de noche"): "n.m.",
   ("同事", "colega"): "n.m.",
   ("竞争对手", "competidor"): "n.m.",
   ("轮班", "turno"): "n.m.",
   ("进步，进展", "avance"): "n.m.",
   ("压力的", "presivo"): "adj.",
   # 短语无词性 -> 清空
   ("依赖", "contar con"): "",
   ("参与", "tomar parte en"): "",
   # 缩减 / 减少 语义上是及物
   ("缩减", "reducir"): "v.t.",
 },
 "subs": [
   # Sec1 上班（西语否定必须在动词前，原文漏 no）
   ("Los organizadores asumirán ninguna responsabilidad legal",
    "Los organizadores no asumirán ninguna responsabilidad legal"),
   ("En el amor la felicidad y el dolor aparecen de forma alterna",
    "En el amor la felicidad y el dolor aparecen de forma alternada"),
   ("Es libre de optar entre tres alternativas",
    "Es libre de elegir entre tres alternativas"),
   ("No creo que tenga una agenda muy ocupada",
    "No creo que yo tenga una agenda muy ocupada"),
   # Sec2 升职
   ("Le han promovido el grado de capitán",
    "Lo han promovido a capitán"),
   # Sec3 与同事相处
   ("El equipo de ventas de bruce no pudo resistir",
    "El equipo de ventas de Bruce no pudo resistir"),
   ("la única persona que realmente puede confiar en siempre está engañándola",
    "la única persona en la que realmente puede confiar siempre está engañándola"),
   # Sec4 工作量
   ("Tenemos petróleo en", "Tenemos petróleo en abundancia"),
   # Sec5 工作状态
   ("nuestro espíritu de estudio trabajador y perseverante",
    "nuestro espíritu de trabajo y perseverancia"),
   ("Con la explosión demográfica se crece cada vez la presión demográfica",
    "Con la explosión demográfica crece cada vez más la presión demográfica"),
   # Sec6 沟通与竞争
   ("Eso te pone en un espacio de competencia constante",
    "Eso te pone en un entorno de competencia constante"),
   ("Competimos por el campeón", "Competimos por ser campeones"),
   # Sec7 专有名词需大写（原文小写了 titanic）
   ("Blanca del titanic", "Blanca del Titanic"),
   ("del titanic", "del Titanic"),
   # Sec8 退休与离职
   ("Después de haber sido despedido hizo todo lo posible para buscar un nuevo trabajo",
    "Después de haber sido despedido, hizo todo lo posible para buscar un nuevo trabajo"),
   ("Cometió un error grande y se despidió", "Cometió un error grande y fue despedido"),
 ],
 "CN_FIX": {
   # E 行中文（zh_subs 只作用于 S 句中文）
   "幻觉": "幻想",                 # ilusión = 幻想
   "使均衡，使匀称": "提供", # proporcionar = 提供
 },
 "zh_subs": [
   # Sec4 中文多了「以前一个同事」，与西语 una colega 不符
   ("他偷偷地把工作让给以前一个同事去做。", "他偷偷地把这份工作交给了一位同事去做。"),
 ],
}

G24 = {
 "name": "宣传与销售",
 "raw": "_tools/parte24_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "destinó": "destino",                # 重音误用（无上下文动词）
   "El nos cuenta": "Él nos cuenta",     # Él=他（重音）
   "compensaral": "compensar al",        # 粘连
 },
 "fix": {
   # Sec1 市场活动
   # Sec2 广告宣传
   ("霓虹灯广告", "neón"): "neón",       # el neón 阳性
   ("受欢迎的", "bienvenido"): "popular", # bienvenido=欢迎（人）
   # Sec3 参加展会
   ("赞助", "apoyo"): "patrocinar",       # 赞助（动）=patrocinar；apoyo=支持
   # Sec4 产品介绍
   ("各种各样的", "cualquier especie"): "diverso",
   ("全世界的", "alrededor del mundo"): "mundial",
   # Sec5 佣金折扣
   ("同意给予", "acordado a dar"): "acordado",
   # Sec6 谈判
   ("反对", "frustrar"): "rechazar",      # frustrar=使沮丧
   # Sec7 讨价还价
   ("出价", "licitación"): "puja",        # licitación=招标；出价=puja
   # Sec8 存储仓库
   ("输送机", "portador"): "transportador",  # portador=搬运者
   ("仓库费", "cobra de almacén"): "tarifa de almacén",
   # Sec9 订单
   # Sec11 包装运输
   ("耐久的", "sostenible"): "resistente",   # sostenible=可持续的
   ("承受", "someterse"): "soportar",        # someterse=使服从
   ("硬纸板", "bordo"): "cartón",            # bordo=边缘
   # Sec12 保险与索赔
   ("阻止", "arrestar"): "impedir",          # arrestar=逮捕
   # Sec13 售后服务
   ("保修", "garantizar"): "garantía",       # 中文「保修」是名词
 },
 "pos": {
   # 文案标错/标全无的，按西语实际词性
   ("供应商", "proveedor"): "n.m.",
   ("霓虹灯广告", "neón"): "n.m.",
   ("卖方", "vendedor"): "n.m.",
   ("条款", "artículo"): "n.m.",
   ("推迟", "prolongar"): "v.t.",            # 文案写成 v.
   ("通常", "general"): "adv.",              # general=一般（副词）
   ("最重要的", "supremo"): "adj.",          # supremo=最高的
   ("保修", "garantía"): "n.f.",
   ("硬纸板", "cartón"): "n.m.",
   ("耐久的", "resistente"): "adj.",
   ("承受", "soportar"): "v.t.",
   ("反对", "rechazar"): "v.t.",
   ("赞助", "patrocinar"): "",
   ("各种各样的", "diverso"): "",
   ("全世界的", "mundial"): "",
   ("出价", "puja"): "n.f.",
   ("输送机", "transportador"): "n.m.",
   ("仓库费", "tarifa de almacén"): "",
 },
 "subs": [
   # Sec1 市场活动
   ("China ya se ha convertido en el segundo mayor de países consumidores de artículos de lujo en todo el mundo",
    "China ya se ha convertido en el segundo mayor país consumidor de artículos de lujo del mundo"),
   ("Los productos de la compañía en se extendió del mercado nacional a los mercados extranjeros",
    "Los productos de la compañía se extendieron del mercado nacional a los mercados extranjeros"),
   # Sec2 广告宣传
   ("La publicidad es un arte, que necesita entusiasmo, creatividad, y acumulación",
    "La publicidad es un arte que necesita entusiasmo, creatividad y acumulación"),
   ("En ese mundo donde brilla neón, cuántas parejas pueden amar toda la vida? Ama de la vida!",
    "En ese mundo donde brilla el neón, ¿cuántas parejas pueden amar toda la vida? ¡Ama de la vida!"),
   # Sec5 佣金折扣
   ("Su salario incluye las bonificaciones o comisiones?",
    "¿Su salario incluye las bonificaciones o comisiones?"),
   # Sec7 讨价还价
   ("Se puede elaborar según los requerimientos de clientes en el proceso de elaboración de materiales que ofrecen el cliente",
    "Se puede elaborar según los requerimientos de los clientes en el proceso de elaboración de los materiales que ellos ofrecen"),
   # Sec10 合同
   ("Sólo un vistazo del comerciante puede identificar los bienes miertras que cien vistazos ni son suficientes para el comprador",
    "Sólo un vistazo del comerciante permite identificar los bienes, mientras que cien vistazo no bastan para el comprador"),
   ("No estoy acuerdo del contrato de compraventa",
    "No estoy de acuerdo con el contrato de compraventa"),
   # Sec11 包装运输
   ("la empresa se .comprometen también a la producción de productos de embalaje",
    "la empresa se compromete también a la producción de productos de embalaje"),
   # Sec13 售后服务
   ("La cámara es sólo una herramienta, paisajes dependen del descubrimiento",
    "La cámara es sólo una herramienta, lo importante es el descubrimiento"),
 ],
 "zh_subs": [
   # Sec13 「相机只是工具，基本能用就行」— 西语原句说的是风景在于发现，对不上
   ("相机只是工具，基本能用就行。 风景在于发现。", "相机只是工具，风景在于发现。"),
 ],
}

G25 = {
 "name": "逛超市",
 "raw": "_tools/parte25_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "ara.ar": "arañar",                    # .r 前后不是元音，clean 的 ñ 自愈救不了
   "Nn ": "Un ",                          # OCR 掉首字母
   "suplemento.": "suplemento",            # 西语后多一个点
 },
 "fix": {
   # Sec1 超市相关
   ("家用电器", "aparato"): "electrodoméstico",   # aparato=器具/装置
   # Sec2 化妆品
   ("磨砂膏", "toallita desmaquilladora"): "exfoliante",  # 磨砂膏=去角质霜
   # Sec3 皮肤清洁
   ("粗糙的", "basto"): "áspero",            # basto=粗糙的/粗笨的，可用于皮肤
   # Sec4 日用品
   ("爽身粉", "empasnte"): "talco",          # empasnte 非西语词
   # Sec5 谷物区
   ("去壳", "bombardeo"): "descascar",      # bombardeo=轰炸
   ("糠", "bola"): "cáscara",               # bola=球
   # Sec6 食品与调料区
   ("芝麻酱", "mermelada de sésamo"): "pasta de sésamo",
   # Sec7 海鲜区
   ("熏制", "boucaner"): "ahumar",          # boucaner 非西语词
   ("带鱼", "trichiure"): "trichiura",      # 拼写错误
   ("鳕鱼肉", "bacalao"): "bacalao",
   # Sec8 各种家电（1）
   ("电饭锅", "estufa"): "olla eléctrica",  # estufa=炉子/暖气
   # Sec9 各种家电（2）
   ("扩音器", "micrófono"): "altavoz",      # micrófono=麦克风
   ("饮水机", "dosificador"): "dispensador de agua",
   ("遥控器", "remoto"): "mando a distancia",
   # Sec10 蔬菜（1）
   ("大头菜", "colinabo"): "colinabo",
   ("葱", "cebouino"): "cebolla",           # cebouino 非西语词
   ("芋头", "boniato"): "boniato",
   # Sec11 蔬菜（2）
   ("卷心菜", "berza"): "repollo",          # berza=羽衣甘蓝
   ("丝瓜", "calabaza esponja"): "calabaza",
   ("苦瓜", "pera de bálsamo"): "pepino amargo",
   ("西葫芦", "alcachofa"): "calabacín",    # alcachofa=朝鲜蓟
   ("冬瓜", "benincasa"): "calabaza china",
   # Sec12 蔬菜（3）
   ("扁豆", "judía"): "judía",
   ("菜豆", "frijol"): "frijol",
   # Sec13 水果（1）
   ("柚子", "pomelo"): "pomelo",
   # Sec14 水果（2）
   ("山楂", "espino"): "espino",            # espino=hawthorn，山楂树
   # Sec15 食用肉类
   ("绞肉机", "picador"): "picadora de carne",
   # Sec16 宠物用品区
   ("溜", "arrastrar"): "arrastrar",
   # Sec17 图书区
   ("简装的", "rústico"): "de tapa dura",   # rústico=乡村的
   # Sec18 乳制品
   ("纸盒", "bandeja"): "caja",             # bandeja=托盘
   # Sec19 零碎物品
   ("烤架", "barbacoa"): "parrilla",        # barbacoa=烧烤
   # Sec20 结账
   ("大甩卖", "vender"): "liquidación",     # 中文是名词
   ("结账", "equilibrar una cuenta"): "pagar la cuenta",
 },
 "pos": {
   # 文案标错/标全无的，按西语实际词性
   ("蔬菜", "verdura"): "n.f.",             # 同一节两条，verdura 阴性
   ("家用电器", "electrodoméstico"): "n.m.",
   ("磨砂膏", "exfoliante"): "n.m.",
   ("爽身粉", "talco"): "n.m.",
   ("大甩卖", "liquidación"): "n.f.",
   ("结账", "pagar la cuenta"): "",
   ("清仓", "liquidación"): "n.f.",
 },
 "subs": [
   # Sec2 化妆品
   ("Amor es cuando una muchacha se pone perfume y un muchacho se pone loción, de afeitardo y se unen a sentirse",
    "Amor es cuando una muchacha se pone perfume y un muchacho se pone loción, de afeitardo, y se unen a sentirse"),
   # Sec3 皮肤清洁
   ("Usted y yo sabemos que puedo hacer las uñas, mientras que le elimino en fragmentos",
    "Usted y yo sabemos que puedo hacer las uñas mientras le elimino en fragmentos"),
   # Sec4 日用品
   ("¿Por qué debería preocuparme de tu paraguas",
    "¿Por qué debería preocuparme de tu paraguas?"),
   # Sec5 谷物区（性别错 + 谚语）
   ("Un gran cabra estaba en nuestro camino, no le importaba el pepino que le dimos, pero con sus ojos fijos en el maíz en la mano de mi campa-.ero",
    "Una gran cabra estaba en nuestro camino, no le importaba el pepino que le dimos, pero con sus ojos fijos en el maíz que llevaba mi compañero"),
   ("Un burro llevaba trigo y devolvió llevando harina",
    "Un burro llevaba trigo y volvió llevando harina"),
   # Sec6 食品与调料区
   ("Creemos firmemente que: buenos productos son como el azúcar, derretida ella misma, y el agua se ha convertido dulce",
    "Creemos firmemente que: los buenos productos son como el azúcar, que se derritió a sí misma, y el agua se ha convertido dulce"),
   ("Sobre la mesa están la tazas, el azúcar y la cafeteria",
    "Sobre la mesa están las tazas, el azúcar y la cafetera"),
   # Sec8 各种家电（1）
   ("El aspirador respira el polvo y trozos de golondrina de papel en el suelo",
    "El aspirador recoge el polvo y los trozos de papel que hay por el suelo"),
   # Sec9 各种家电（2）
   ("Después de esta interrupción corta pero grosera, al abuchear el público, kanye west volvió el micrófono a Taylor Swift, quien se quedó muda por la sorpresa",
    "Después de esta interrupción corta pero grosera, al abuchear el público, Kanye West volvió el micrófono a Taylor Swift, quien se quedó muda por la sorpresa"),
   # Sec10 蔬菜（1）
   ("Comió como si tuviera que ir una tierra árida, que fue Japón, donde tuviera nada comestible",
    "Comió como si tuviera que ir a una tierra árida, que fue Japón, donde no hubiera nada comestible"),
   # Sec11 蔬菜（2）
   ("Los fideosbiang biang son fideos muy gruesos, hechos a mano. Es típico de Shaanxi, servido con un montón de chili",
    "Los fideos biang-biang son fideos muy gruesos, hechos a mano. Son típicos de Shaanxi y se sirven con un montón de chili"),
   # Sec12 蔬菜（3）
   ("También puede hacer mi maquillaje en la calabaza (naranja y negro), undead, zombi, un bate, la momia, etc",
    "También puede hacer su maquillaje con la calabaza (naranja o negra), un muerto viviente, un zombi, un murciélago, una momia, etc"),
   # Sec14 水果（2）
   ("El albaricoque es una de las frutas más ricas en provitamina A, 50% de la ingesta diaria viene de sólo 100g",
    "El albaricoque es una de las frutas más ricas en provitamina A: el 50% de la ingesta diaria viene de sólo 100 g"),
   ("Yo le dije: “el amor es un jugo delicioso y pulpa amarga.”",
    "Yo le dije: «el amor es un jugo delicioso y una pulpa amarga»."),
   # Sec16 宠物用品区
   ("Otra característica de las familias francesas es que, la mitad de los hogares tienen una mascota, perro o gato, principalmente",
    "Otra característica de las familias francesas es que la mitad de los hogares tiene una mascota, un perro o un gato, principalmente"),
   # Sec18 乳制品
   ("Leche para la glotonería y negro para la degustación, sus sabores de una gran riqueza y diversidad infinita",
    "La leche para la glotonería y la negra para la degustación tienen una gran riqueza de sabores y una diversidad infinita"),
   # Sec19 零碎物品
   ("A medida que amplia su familia, este hombre casi analfabeto resulta un destacado hombre de negocios",
    "A medida que amplía su familia, este hombre casi analfabeto acaba siendo un destacado hombre de negocios"),
   ("La niña saca un tercer cerillo, y ella parece ponerse al lado de un árbol de navidad hermoso",
    "La niña saca un tercer cerillo y parece ponerse al lado de un árbol de Navidad hermoso"),
   # Sec20 结账
   ("Los ingresos de la compañía son transparentes, el beneficio no es significativo, y lo importante es el plu jo",
    "Los ingresos de la compañía son transparentes, el beneficio no es significativo y lo importante es el flujo"),
   ("Hizo un ruido muy espantoso, y cometí cuatro errores en mi adición",
    "Hizo un ruido muy espantoso y cometí cuatro errores en mi adición"),
   ("No queda claro cuánto dinero al final, se ve bastante mucho",
    "No queda claro cuánto dinero es al final, pero se ve bastante"),
 ],
 "zh_subs": [
   # Sec14 错字「是一种的甜如美味」
   ("爱情是一种的甜如美味的果汁和苦涩的酱。", "爱情是一种甜如美味的果汁和苦涩的酱。"),
   # Sec19 「玫瑰花蜜」与 miel rosada（粉蜜/玫瑰蜜）对应
   ("我每天都喝玫瑰花蜜。", "我每天都喝玫瑰蜜。"),
   # Sec18 中文多了一句「吃了两片面包」（西语没有）
   ("我早晨喝了一杯牛奶，吃了两片面包。", "我早晨喝了一杯牛奶。"),
 ],
}

G26 = {
 "name": "健身运动",
 "raw": "_tools/parte26_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "compa-.eros": "compañeros",            # 连字符右侧是点，clean 救不了
   "recoged or": "recogedor",
 },
 "fix": {
   # Sec1 运动健身
   ("伸展", "tramo"): "estiramiento",       # tramo=路段/段
   ("扁平椅子", "silla plana"): "banco plano",   # 健身房器械=banco
   ("伸拉中心", "centro de presión"): "centro de estiramientos",
   # Sec2 舞蹈
   ("摇摆舞", "roca"): "rock",              # roca=岩石
   ("舞者", "bailarín"): "bailarín",
   # Sec3 瑜伽
   ("举起", "recaudar"): "levantar",        # recaudar=征收
   # Sec4 保龄球
   ("疏忽", "Falta"): "descuido",           # Falta=缺少
   ("平均分", "punto promedio"): "promedio",
   # Sec6 高尔夫
   ("瞄准", "punto"): "apuntar",            # punto=点/分数
   ("未击中", "pierda"): "fallo",            # pierda 拼错；义项=未击中
   # Sec7 减肥
   ("有氧操的", "aerobic"): "aeróbico",     # 西语重音
 },
 "pos": {
   # 文案标错性别的，按西语实际词性
   ("舞者", "bailarín"): "n.m.",            # el bailarín
   ("摇摆舞", "rock"): "n.m.",
   ("疏忽", "descuido"): "n.m.",
   ("未击中", "fallo"): "n.m.",
   ("平均分", "promedio"): "",
   ("跳舞", "bailar"): "v.i.",              # bailar 默认 v.i.
   # 短语无词性 -> 清空
   ("健身", "fortalecer la salud"): "",
   ("扔保龄球", "tirar bolos"): "",
   ("从左到右", "de izquierda a derecha"): "",
   ("高尔夫俱乐部", "golf club"): "",
   ("均衡饮食", "dieta equilibrada"): "",
   ("无盐饮食", "dieta sin sal"): "",
   ("啤酒肚", "barriga cervecera"): "",
 },
 "subs": [
   # Sec1 运动健身
   ("Ahora el juego de barco de dragón se ha convertido en un deporte de agua que refleja tanto la tradición y la modernidad",
    "Ahora las carreras de barcos de dragón se han convertido en un deporte de agua que refleja tanto la tradición como la modernidad"),
   ("Es más un desafío de resistencia que un viaje, como los ciclistas se mueven en un paquete",
    "Es más un desafío de resistencia que un viaje, ya que los ciclistas se mueven en equipos"),
   # Sec2 舞蹈
   ("El bailarín rompió el talón de zapatillas",
    "El bailarín rompió el talón de las zapatillas"),
   ("Me concede el honor de este baile?",
    "¿Me concede el honor de bailar?"),
   # Sec3 瑜伽
   ("Practicar regularmente actividad de relajación como el yoga ayuda a aliviar el estrés, dormir mejor, y por lo tanto, están dispuestos a luchar contra las infecciones invernales",
    "Practicar regularmente una actividad de relajación como el yoga ayuda a aliviar el estrés, a dormir mejor y, por lo tanto, a estar preparados para luchar contra las infecciones invernales"),
   ("Deseo la felicidad romántica, su historia es, sin embargo, jugó en las notas trágicas",
    "Deseo la felicidad romántica, pero su historia, sin embargo, transcurrió en notas trágicas"),
   # Sec5 滑雪与滑冰
   ("Se ha apuntado a clases de patinaje sobre hielo",
    "Se ha apuntado a clases de patinaje artístico"),
   ("Porque el esquí puede sostener de manera uniforme todos los músculos durante el ejercicio",
    "El esquí permite trabajar todos los músculos de manera uniforme durante el ejercicio"),
   # Sec6 高尔夫
   ("Las alas del tiempo vuelan a lo largo de las curvas de memoria",
    "Las alas del tiempo vuelan por las curvas de la memoria"),
   ("Se extendió la cabeza, vio un zorro en el pozo, y le preguntó si el agua era buena",
    "Asomó la cabeza, vio un zorro en el pozo y le preguntó si el agua era buena"),
   # Sec7 减肥
   ("Aunque muchos estadounidenses a prestar atención al mantenimiento de la figura, en el gimnasio todo el día en pleno auge, en los Estados Unidos tenían una gran cantidad de obesos",
    "Aunque muchos estadounidenses prestan atención al mantenimiento de la figura y pasan todo el día en el gimnasio, en los Estados Unidos había una gran cantidad de obesos"),
   ("Desde el ángulo de comida, julio es probable el mes más agradable para completar su comida de frutas y verduras de temporada",
    "Desde el ángulo de la comida, julio es probablemente el mes más agradable para completar su comida de frutas y verduras de temporada"),
 ],
}

G27 = {
 "name": "修身养性",
 "raw": "_tools/parte27_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "Eschucar": "Escuchar",               # 词头字母错
   "acticidadde": "actividad de",        # 词内粘连
   "Espa.a": "España",
   "casta.uela": "castañuela",            # 点两侧是元音，clean 可自愈，保险起见
   "su-basta": "subasta",
 },
 "fix": {
   # Sec1 园艺
   ("茂密的", "grueso"): "denso",           # grueso=粗大的；茂密的=denso
   # Sec2 各种乐器（1）
   ("管铜乐器", "instrumentos de viento"): "instrumentos de viento",
   # Sec3 各种乐器（2）
   # Sec4 钢琴
   ("踏板", "paso"): "pedal",              # paso=步子/阶段
   # Sec5 舞台剧
   ("高潮", "pico"): "clímax",              # pico=山峰
   # Sec6 博物馆
   ("陈列的", "en la exhibición"): "en pie de exhibición",
   # Sec7 天文台
   # Sec8 古董店
 },
 "pos": {
   # 文案标错性别的，按西语实际词性
   ("木偶戏", "títeres"): "n.m.",         # los títeres
   ("土星", "Saturno"): "n.m.",
   ("钢琴家", "pianista"): "n.m.",
   ("定音鼓", "timbal"): "n.m.",           # el timbal
   ("吉他手", "guitarrista"): "n.m.",
   ("手风琴", "acordeón"): "n.m.",         # el acordeón
   ("长号", "trombone"): "n.m.",
   # 短语无词性 -> 清空
   ("乐器", "instrumento musical"): "",
   ("园艺工具", "herramientas de jardinería"): "",
   ("园艺工人", "trabajadores de horticultura"): "",
   ("铜绿", "cardenillo verde"): "",
   ("铜币", "moneda de cobre"): "",   ("铜币", "moneda de cobre"): "n.f.",
   ("增值", "aumento de valor"): "",
   ("鉴别能力强的", "capacidad fuerte para identificar"): "",
   ("陈列的", "en pie de exhibición"): "",
   ("机械装置", "dispositivos mecánicos"): "",
   ("音板", "caja de resonancia"): "",
   ("琴凳", "taburete del piano"): "",
   ("乐谱架", "atril"): "n.m.",
 },
 "subs": [
   # Sec1 园艺
   ("Creo que la jardinería es la arte",
    "Creo que la jardinería es un arte"),
   ("Cuando brota el retoño del ficus es de color rosa o rojo",
    "Cuando brota, el retoño del ficus es de color rosa o rojo"),
   # Sec2 各种乐器（1）
   ("Hay esencia en cada música, cómo se lleva a cabo para escuchar depende del corazón",
    "Hay esencia en cada música; cómo se lleva a cabo para escucharla depende del corazón"),
   ("Me doy a mí mismo una música deolmision maravillosa",
    "Me doy a mí mismo una música de admisión maravillosa"),
   # Sec3 各种乐器（2）
   ("Vivir en la esperanza, incluso sin acompañamiento musical, se puede bailar",
    "Vivir con esperanza, incluso sin acompañamiento musical, permite bailar"),
   ("Sin embargo, mostró la mayor seriedad y profesionalismo su interpretación de guitarra",
    "Sin embargo, mostró la mayor seriedad y profesionalismo en su interpretación de guitarra"),
   # Sec6 博物馆
   ("Vamos a visitar el museo arqueológico, .quieres venir con nosotros?",
    "Vamos a visitar el museo arqueológico, ¿quieres venir con nosotros?"),
   ("En el Museo del Prado se puede apreciar las obras pictóricas más representativas de España y de.",
    "En el Museo del Prado se pueden apreciar las obras pictóricas más representativas de España y de Europa."),
   ("Se mostrará unos esqueletos de dinosaurio en el museo",
    "Se mostrarán unos esqueletos de dinosaurio en el museo"),
   ("Voy a una acticidadde subasta de objetos de arte",
    "Voy a una subasta de objetos de arte"),
   # Sec7 天文台
   ("Un equipo de astrónomos han descubierto un nuevo planeta",
    "Un equipo de astrónomos ha descubierto un nuevo planeta"),
   # Sec8 古董店
   ("No elegimos a olvidar si no se puede continuar, elija recopilar y recoger en el fondo del alma",
    "No elegimos olvidar si no se puede continuar; elija recopilar y recoger en el fondo del alma"),
   ("El país en realidad conserva sus diversas y antiguas tradiciones, ciertamente no para destruirlas",
    "El país, en realidad, conserva sus diversas y antiguas tradiciones, ciertamente no para destruirlas"),
 ],
 "CN_FIX": {
   "管铜乐器": "管乐器",   # instrumentos de viento = 管乐器（含铜管）
 },
 "zh_subs": [
   # Sec8 错字「旳」
   ("以保持其多元化和祖先旳传统", "以保持其多元化和祖先的传统"),
 ],
}

G28 = {
 "name": "放松好去处",
 "raw": "_tools/parte28_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "ipo de animal": "tipo de animal",       # 首字母掉字
   "ruise.or": "ruiseñor",
   "picaraza": "picoraza",                  # 喜鹊=urraca 才是地道的；此处仅修拼写
   "genero-samente": "generosamente",
   "recons-truyeron": "reconstruyeron",
   "des-truido": "destruido",
   "la otre": "la otra",
   "torrencial-mente": "torrencialmente",
   "cadu-cados": "caducados",
   "fa-milia": "familia",
   "ali-mentos": "alimentos",
   "en-trara": "entrara",
   "due.o": "dueño",
   "re-al-mente": "realmente",
   "Ma.ana": "Mañana",
   "me-lodía": "melodía",
   "escuchán-dole": "escuchándole",
   "ayunta-miento": "Ayuntamiento",
   "de-lante": "delante",
   "tíovivo": "tiovivo",
   "monta.a rusa": "montaña rusa",
   "peque.os": "pequeños",
   "aven-turera": "aventurera",
   "pro-cesan": "procesan",
   "po-lluelos": "polluelos",
   "ma.ana": "mañana",
   "tama.o": "tamaño",
 },
 "fix": {
   # Sec3 动物园（3）
   ("杜鹃", "azalea"): "cuco",                # azalea=杜鹃花；杜鹃=cuco
   ("喜鹊", "picoraza"): "urraca",
   # Sec4 水族馆
   ("鲟鱼", "esturión"): "esturión",
   ("乌鱼", "mula"): "mula",                 # mula 非西语词（应为 mújola）
   # Sec5 植物园（1）
   ("三色堇", "pensamiento"): "pensamiento",
   # Sec6 植物园（2）
   ("落叶松", "arca"): "alerce",             # arca=箱子；落叶松=alerce
   ("榆树", "bosquecillo de olmos"): "olmo",  #  bosquecillo=小树林
   ("树梢", "copas de los árboles"): "copas de los árboles",
   ("树干", "tronco de árbol"): "tronco de árbol",
   # Sec7 游乐园
   ("蹦极", "puenting"): "puenting",
   # Sec8 演唱会
   ("包厢", "caja"): "palco",                # 剧场包厢=palco/foso
   # Sec9 酒吧
   ("吧台", "contador"): "barra",             # contador=柜台/计数员
   ("量器", "metro"): "medida",              # metro=米
   ("酸橙汁", "zumo de naranja"): "zumo de lima",
   # Sec10 野餐烧烤
 },
 "pos": {
   ("杜鹃", "cuco"): "n.m.",              # el cuco
   ("落叶松", "alerce"): "n.m.",
   # 文案标错性别的，按西语实际词性
   ("鲟鱼", "esturión"): "n.m.",
   ("鸡尾酒", "cóctel"): "n.m.",             # el cóctel
   ("蹦极", "puenting"): "n.m.",
   ("夜莺", "ruiseñor"): "n.m.",
   ("包厢", "palco"): "n.m.",
   # 短语无词性 -> 清空
   ("孔雀", "pavo real"): "",
   ("食蚁兽", "oso hormiguero"): "",
   ("榆树", "olmo"): "",
   ("核桃树", "nogal"): "",
   ("游乐园", "parque de atracciones"): "",
   ("碰碰车", "auto de choque"): "",
   ("海盗船", "barco pirata"): "",
   ("杂耍", "espectáculo de variedades"): "",
   ("走钢丝", "funambulismo"): "",
   ("飞船", "nave espacial"): "",
   ("大钢琴", "piano de cola"): "",
   ("独唱", "cantar sola"): "",
   ("歌词", "letra de una canción"): "",
   ("舞池", "pista de baile"): "",
   ("量酒杯", "chupito"): "",
   ("酸橙汁", "zumo de lima"): "",
   ("白酒", "orujo chino"): "",
   ("急救箱", "botiquín"): "",
   ("野餐桌", "mesas de picnic"): "",
   ("食篮", "canasta de alimentos"): "",
   ("野餐布", "tela de picnic"): "",
 },
 "subs": [
   # Sec1 动物园（1）
   ("Tigre es un tipo de animal muy feroz",
    "El tigre es un tipo de animal muy feroz"),
   ("Tigre y dragón sentaron en espiral nunca ha sido más fuerte; tierra y cielo se procesan, haciendo cantar generosamente y sentir gran júbilo",
    "Tigre y dragón sentados en espiral nunca han sido más fuertes; la tierra y el cielo se transforman, haciendo cantar generosamente y sentir un gran júbilo"),
   # Sec3 动物园（3）
   ("El amor de una madre está convencida de que sus polluelos son cisne",
    "El amor de una madre está convencido de que sus polluelos son cisnes"),
   ("El amor es un nido de gorriones que no se reconstruyeron después de ser destruido",
    "El amor es un nido de gorriones que no se reconstruye después de ser destruido"),
   # Sec4 水族馆
   ("En la Isla Catalina hay la base para criar el tiburón blancos",
    "En la isla Catalina hay una base para criar tiburones blancos"),
   # Sec5 植物园（1）
   ("Por su función, todo el parque está dividido en dos zonas: la de producción de alto rendimiento y la otra de ocio",
    "Por su función, todo el parque está dividido en dos zonas: la de producción de alto rendimiento y la de ocio"),
   ("Las distintas secciones del jardín son bonitos",
    "Las distintas secciones del jardín son bonitas"),
   # Sec7 游乐园
   ("Jorge es una persona aventurera: practica escalada, puenting, submarinismo y otros deportes de. Jorge",
    "Jorge es una persona aventurera: practica escalada, puenting, submarinismo y otros deportes de riesgo"),
   # Sec8 演唱会
   ("Este concierto fue realmente abrumador",
    "Este concierto fue realmente abrumador"),
   ("La cuenta hacia atrás delante de la plaza del Ayuntamiento se transmitió desde la radio",
    "La cuenta atrás delante de la plaza del Ayuntamiento se transmitió por la radio"),
   # Sec9 酒吧
 ],
 "zh_subs": [
   # Sec7 西语句尾的 Jorge 被 split_s 切进西语，中文失主语 -> 补为「他」
   ("是一个喜欢冒险的人，他会攀岩",
    "他是一个喜欢冒险的人，他会攀岩"),
   # Sec7 中文重复了主语（西语句尾带 Jorge）
   ("和演退沉活动还有一些其他的冒险运动。Jorge是一个喜欢冒险的人",
    "和演退沉活动还有一些其他的冒险运动。他是一个喜欢冒险的人"),
   # Sec7 错字「折旧」->「折纸」
   ("就算童年时候折旧的一只纸船", "就算童年时候折纸的一只纸船"),
   # Sec8 中文与西语不符（abrumador=压倒性的，不是催眠）
   ("这场音乐会真是快让人睡着了！", "这场音乐会真是震撼人心！"),
   # Sec4 「嫩鸡蛋」与西语 huevo duro（煮蛋）不符
   ("有莴苣、番茄、洋葱、嫩鸡蛋、金枪鱼。", "有莴苣、番茄、洋葱、煮鸡蛋、金枪鱼。"),
   # Sec2 「小祖先」与 padrecito（小）不符
   ("因此人们称之为大熊猫的“小祖先”。", "因此人们称之为大熊猫的“小弟弟”。"),
 ],
}

G29 = {
 "name": "电影电视",
 "raw": "_tools/parte29_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "Ca-ribe": "Caribe",
   "sue.o": "sueño",
   "pelí-cula": "película",
   "detec-tives": "detectives",
   "román-tica": "romántica",
   "dupli-cada": "duplicada",
   "electró-nica": "electrónica",
   "expa.ol": "español",
 },
 "fix": {
   # Sec1 看电影
   # Sec2 电影工作人员
   ("编剧", "cineasta"): "guionista",          # cineasta=电影导演；编剧=guionista
   ("拍摄", "disparo"): "rodar",               # disparo=击发；拍摄=rodar
   # Sec3 电影类型
   # Sec4 看电视
   # Sec5 听音乐
   ("摇滚乐", "roca"): "rock",                 # roca=岩石
   ("布鲁斯", "bruce"): "blues",               # bruce=布鲁斯（人名拼错）
   ("爵士乐", "jazz"): "jazz",
   ("音阶", "rango"): "escala",                # rango=范围
   ("潮流", "tendencia"): "tendencia",
 },
   ("拍摄", "disparo"): "rodar",              # disparo=击发；拍摄摄影=rodar
 "pos": {
   ("拍摄", "rodar"): "v.t.",
   # 文案标错性别的，按西语实际词性
   ("主角", "protagonista"): "n.m.",
   ("制片", "productor"): "n.m.",
   ("配角", "papel secundario"): "",
   ("美术指导", "dirección de arte"): "",
   ("新闻短片", "noticia"): "n.f.",
   ("说唱音乐", "rap"): "n.m.",
   ("布鲁斯", "blues"): "n.m.",
   ("爵士乐", "jazz"): "n.m.",
   ("摇滚乐", "rock"): "n.m.",
   # 短语无词性 -> 清空
   ("电影明星", "estrella de cine"): "",
   ("原版", "edición original"): "",
   ("禁映影片", "vídeo prohibido"): "",
   ("电影节", "festival de cine"): "",
   ("乡村音乐", "música country"): "",
   ("管弦乐", "música orquestal"): "",
   ("电子音乐", "música electrónica"): "",
   ("专题节目", "programas especiales"): "",
   ("肥皂剧", "serie de televisión"): "",
   ("知识竞赛", "concurso de conocimientos"): "",
   ("彩色电视", "televisión de color"): "",
 },
 "subs": [
   # Sec1 看电影
   ("Francia siempre ha hecho hincapié en la integración de los inmigrantes, esta película siendo una buena prueba",
    "Francia siempre ha hecho hincapié en la integración de los inmigrantes, y esta película es una buena prueba de ello"),
   ("La película del camino francesa en la pantalla grande presenta un paisaje único y el patrimonio cultural de Francia",
    "La película francesa del camino, en la pantalla grande, presenta un paisaje único y el patrimonio cultural de Francia"),
   # Sec2 电影工作人员
   ("Seguimos el tralajo del guión y un nuevo director es activamente buscado",
    "Seguimos el trabajo del guión y se está buscando activamente a un nuevo director"),
   ("El rodaje de algunas escenas es tan intenso que las lágrimas de la joven actriz se ejecutan de verdad",
    "El rodaje de algunas escenas es tan intenso que las lágrimas de la joven actriz son reales"),
   ("Es un actor famoso por el protagonista del Pirata de Caribe",
    "Es un actor famoso por interpretar al protagonista de Piratas del Caribe"),
   # Sec3 电影类型
   ("Ha visto muchas película ética",
    "Ha visto muchas películas éticas"),
   ("Por lo general me gusta ver películas detectives, deportes como el tenis, baloncesto, tenis de mesa y bádminton",
    "Por lo general me gusta ver películas de detectives; me gustan los deportes como el tenis, el baloncesto, el tenis de mesa y el bádminton"),
   # Sec4 看电视
   ("Tiempo de jugar es de 45 minutos para los programa especial de televisión en español",
    "El tiempo de emisión es de 45 minutos para los programas especiales de televisión en español"),
   # Sec5 听音乐
   ("Me gusta escuchar música, música jazz sobre todo",
    "Me gusta escuchar música, sobre todo música jazz"),
   ("La empresa tiene como objetivo la costante innovación de productos y llevar la tendencia",
    "La empresa tiene como objetivo la constante innovación de productos y llevar la tendencia"),
 ],
 "zh_subs": [
   # Sec3 中文把「电影」写成了「小说」
   ("平时爱看悬疑侦探类小说；", "平时爱看悬疑侦探类电影；"),
 ],
}

G30 = {
 "name": "出版刊物",
 "raw": "_tools/parte30_raw.txt",
 # clean_es 之后的 OCR 残损 -> 正确写法
 "typo": {
   "generalunente": "generalmente",       # ge-neralunente 断行后残留
 },
 "fix": {
   # Sec1 出版物
   ("版权", "propiedad literaria"): "derechos de autor",   # 版权=著作权
   ("校对员", "corrector"): "corrector de pruebas",       # 校对员需补「校样」
   ("定期地", "periódico"): "periódicamente",             # 定期地（副词）不是 periódico（形）
   ("报纸", "prensa"): "periódico",                       # prensa=新闻界/报刊业
   # Sec2 报纸及杂志类型
   ("日报", "diaria"): "diario",                          # diaria=每日的（形）
   ("提前出版的", "publicado antes"): "publicado previamente",
   ("新闻", "novedad"): "noticia",                        # novedad=新奇/新鲜事
   ("新闻媒体", "estilo periodístico"): "medio de comunicación",
   ("文摘", "abstracto"): "resumen",                      # abstracto=摘要(英式)
   ("半月的", "bimensual"): "quincenal",                  # bimensual=两月一次
   ("半月刊", "revista bimensual"): "revista quincenal",
 },
 "pos": {
   # Sec1
   ("校对员", "corrector de pruebas"): "n.m.",
   ("记者", "periodista"): "n.m.",
   ("报纸", "periódico"): "n.m.",                          # 文案标 n.f.，periódico 是阳性
   # Sec2
   ("日报", "diario"): "n.m.",
   ("评论员", "comentarista"): "n.m.",
   ("半月的", "quincenal"): "adj.",
 },
 "subs": [
   # Sec1 主谓一致：La revista（单数）… no publican -> no publica
   ("La revista New York generalmente no publican novelas",
    "La revista New York generalmente no publica novelas"),
 ],
 "zh_subs": [
   # Sec1 中文「媒体 ,政府」逗号前多了空格
   ("如果把录音带交给媒体 ,政府会不相信。", "如果把录音带交给媒体，政府会不相信。"),
 ],
}

G31 = {
 "name": "时尚前沿",
 "raw": "_tools/parte31_raw.txt",
 "typo": {
   "latranquiulidad": "la tranquilidad",    # clean 删掉 OCR 的点：la.tranquiulidad
 },
 "fix": {
   # Sec1 网购
   ("认同", "identidad"): "identificación",             # identidad=身份；认同=identificación
   # Sec2 游戏
   ("属性", "propiedad"): "atributo",                    # 游戏「属性」=atributo
   ("法师", "maestro"): "mago",                        # 游戏职业「法师」=mago
   # Sec3 扑克牌：西语四种花色名与中文完全不同
   ("梅花", "flor del ciruelo"): "tréboles",            # 梅花=tréboles
   ("方块", "baldosa"): "diamantes",                    # 方块=diamantes（baldosa=瓷砖）
   ("红桃", "corazón"): "corazones",
   ("黑桃", "pica"): "picas",                           # pica=鹤
   ("同花", "escalera real"): "colorada",               # escalera real=皇家同花顺
   ("一副", "un par"): "una baraja",                    # 一副(牌)=una baraja
   # Sec4 十二生肖
   ("牛年", "año del buey"): "año del toro",            # 十二生肖用 toro
   ("兔年", "año de la conejo"): "año del conejo",      # 性别一致
   ("羊年", "años del carnero"): "año del carnero",     # 单一年
   ("猴年", "años del mono"): "año del mono",
   # Sec6 占卜
   ("吉利的", "conducente"): "favorable",               # conducente=引导的
 },
 "pos": {
   # Sec1
   ("创办者", "fundador"): "n.m.",
   ("信誉", "prestigio"): "n.m.",
   ("聊天", "chatear"): "v.t.",
   ("对比", "contrastar"): "v.t.",
   # Sec2
   ("经验值", "experiencia"): "n.f.",
   ("法师", "mago"): "n.m.",
   # Sec3
   ("扑克牌", "póker"): "n.m.",
   ("方块", "diamantes"): "n.m.",
   ("红桃", "corazones"): "n.m.",
   ("黑桃", "picas"): "n.m.",
   # Sec4
   ("传奇", "leyenda"): "n.f.",
   # Sec5
   ("白羊座", "Aries"): "n.m.",
   ("金牛座", "Tauro"): "n.m.",
   ("双子座", "Géminis"): "n.m.pl.",
   ("巨蟹座", "Cáncer"): "n.m.",
   ("狮子座", "Leo"): "n.m.",
   ("处女座", "Virgo"): "n.f.",
   ("天秤座", "Libra"): "n.f.",
   ("天蝎座", "Escorpio"): "n.m.",
   ("射手座", "Sagitario"): "n.m.",
   ("摩羯座", "Capricornio"): "n.m.",
   ("水瓶座", "Acuario"): "n.m.",
   ("双鱼座", "Piscis"): "n.m.",
   ("占星", "horóscopo"): "n.m.",
   # Sec6
   ("塔罗牌", "tarot"): "n.m.",
   ("迹象", "signo"): "n.m.",
   ("预示", "predecir"): "v.t.",
 },
 "subs": [
   # Sec1 冠词
   ("En contraste con el bullicio de la ciudad, el campo nos ofrece la tranquilidad saludable",
    "En contraste con el bullicio de la ciudad, el campo nos ofrece una tranquilidad saludable"),
   # Sec2 原句缺谓语（只有「a promover」不定式），整句重写
   ("Con la diligencia y la inteligencia a promover el espíritu nacional, el amor sincero y la devoción a servir a la comunidad",
    "Promueve el espíritu nacional con diligencia e inteligencia, ofrece amor sincero y se dedica a servir a la comunidad"),
   # Sec3 谚语：Ojos que no ven… 加倒装无必要，但中文对应，可保留；补副词
   ("La actriz ha bordado su papel",
    "La actriz ha bordado su papel"),
   # Sec4 语序
   ("El año pasado llevé a los niños para la educación patriótica a Yuanmingyuan, cuando supe la cosa de la estatua de bronce del zodiaco chino por parte de los niños",
    "El año pasado llevé a los niños a Yuanmingyuan para la educación patriótica, cuando supe por ellos lo de la estatua de bronce del zodiaco chino"),
   ("La leyenda dice que los griegos han colocado a la diosa en el templo, y habría cortado las alas para que no pudiera escapar y volar al enemigo",
    "La leyenda dice que los griegos colocaron a la diosa en el templo y le cortaron las alas para que no pudiera escapar ni volar hacia el enemigo"),
   # Sec5 星座名与引语（原文是对话体，去掉破折号并补 ¿）
   ("A ver es la constelación de la Osa Mayor",
    "A ver, esa es la constelación de la Osa Mayor"),
   ("—.Qué horóscopo eres?",
    "¿Qué horóscopo eres?"),
   ("—Yo soy Aries.",
    "Yo soy Aries."),
   ("Yo soy tauro. Y tú qué horóscopo eres?",
    "Yo soy Tauro. ¿Y tú qué horóscopo eres?"),
   # Sec6 esto 无重音
   ("ésto es el signo del peligro",
    "Esto es el signo del peligro"),
 ],
 "CN_FIX": {
   "虔诚": "勤劳",                 # diligently=勤劳（diligencia 在此句语境）
 },
 "zh_subs": [
   # Sec4 西语是 nabos（芜菁），中文原写「胡萝卜」
   ("兔子喜欢吃胡萝卜。", "兔子喜欢吃芜菁。"),
   # Sec5 西语 Osa Mayor=大熊座，中文原写「小熊星座」
   ("看，那是小熊星座。", "看，那是大熊座。"),
   # Sec5 中文「星象」→「星座」（ horóscopo=星座运势）
   ("你是什么星象？", "你是什么星座？"),
   ("我的星象是白羊。", "我的星座是白羊座。"),
 ],
}

G32 = {
 "name": "流行比赛",
 "raw": "_tools/parte32_raw.txt",
 "typo": {
   "especialmete": "especialmente",         # 拼写错误
   "pingpong": "ping-pong",                   # 断行合并后需补连字符（西语标准写法）
   "estara borracho": "estuviera borracho",  # estar -> estar（虚拟式）
   "ultimo ": "último ",                     # 缺重音（词条）
 },
 "fix": {
   # ---- Sec1 球类运动（1）
   ("球类运动", "bola"): "deporte de bola",  # bola=球；球类运动=deporte de bola
   ("橄榄球", "pelota ovalada"): "fútbol americano",  # pelota ovalada=橄榄球(美式)
   # ---- Sec3 篮球场
   ("篮筐", "carrito"): "canasta",           # carrito=小车；篮筐=canasta/aro
   ("看台", "pie"): "grada",                 # pie=脚；看台=grada
   ("中间的", "centro"): "central",          # 作定语用 central
   ("前面", "antes"): "delante",             # antes=以前（时间）；前面=delante（位置）
   # ---- Sec4 篮球赛
   ("预选赛", "calificación"): "clasificación",  # 预选=clasificación
   ("第三名", "tercero"): "tercer puesto",
   # ---- Sec5 篮球选手（位置译名全错）
   ("前锋", "vanguardia"): "delantero",      # vanguardia=先锋/前锋(左翼)
   ("后卫", "guardia"): "defensa",            # guardia=警卫/卫兵
   ("替补队员", "sustitución"): "suplente",  # 中文是「队员」=suplente
   ("边锋队员", "jugador alero"): "ala",     # 边锋=ala
   ("领队", "líder"): "entrenador",          # 领队=entrenador（篮球领队）
   # ---- Sec6 足球场
   ("假动作", "fingida"): "finta",           # fingida=假的；足球假动作=finta
   ("惨败", "aplastante derrota"): "derrota aplastante",
   # ---- Sec7 足球选手
   ("前卫", "vanguardia"): "centrocampista",   #前卫=centrocampista
   ("左内锋", "delantero izquierdo"): "extremo izquierdo",
   ("右内锋", "delantero derecho"): "extremo derecho",
   ("左边锋", "lateral izquierdo"): "lateral izquierdo",
   ("右边锋", "lateral derecho"): "lateral derecho",
   # ---- Sec8 棒球
   ("接球手", "colector"): "receptor",       # colector=收集者
   ("投球手", "bombín"): "lanzador",          # bombín=火车头
   ("守队", "equipo defensivo"): "equipo de campo",  # 守队=equipo de campo
   ("垒", "barrera"): "base",                # barrera=障碍；垒=base
   ("一垒", "barrera primera"): "primera base",
   ("二垒", "barrera segunda"): "segunda base",
   ("三垒", "barrera tercera"): "tercera base",
   ("本垒打", "barrera completa"): "home run",   # 本垒打=home run
   # ---- Sec9 网球与板球
   ("球场", "estadio"): "cancha",            # 球场（网球场）=cancha
   # ---- Sec10 田径
   ("跨栏比赛", "partido de cruzar el obstáculo"): "carrera de vallas",
   ("速度竞赛", "concurso de velocidad"): "prueba de velocidad",
   ("标枪比赛", "competencia de jabalina"): "lanzamiento de jabalina",
   # ---- Sec11 拳击
   ("拳击手训练时的对手", "combate"): "sparring",  # combate=战斗；陪练=sparring
   ("围绳", "cadena"): "cuenda",              # cadena=链条
   ("拳击家", "pugil"): "boxeador",            # pugil=拳击家(书面)
   ("打", "ataque"): "golpe",
 },
 "pos": {
   # Sec1
   ("球类运动", "deporte de bola"): "n.m.",
   # Sec2
   ("台球", "billar"): "n.m.",
   # Sec3
   ("看台", "grada"): "n.f.",
   ("中间的", "central"): "adj.",
   # Sec4
   ("预选赛", "clasificación"): "n.f.",
   ("第三名", "tercer puesto"): "n.m.",
   ("裁判", "juez"): "n.m.",
   ("运动员", "atleta"): "n.m.",
   ("冠军", "campeón"): "n.m.",
   ("亚军", "subcampeón"): "n.m.",
   # Sec5
   ("明星", "estrella"): "n.f.",
   ("前锋", "delantero"): "n.m.",
   ("后卫", "defensa"): "n.m.",
   ("小前锋", "alero"): "n.m.",
   ("领队", "entrenador"): "n.m.",
   # Sec7
   ("前卫", "centrocampista"): "n.m.",
   ("后卫", "guardia"): "n.m.",
   # Sec8
   ("击球员", "bateador"): "n.m.",
   ("接球手", "receptor"): "n.m.",
   ("击球", "bateo"): "n.m.",
   ("投球手", "lanzador"): "n.m.",
   ("外场手", "jardinero"): "n.m.",
   ("垒", "base"): "n.f.",
   ("局", "juego"): "n.m.",
   # Sec9
   ("经理", "gerente"): "n.m.",
   ("击球手", "bateador"): "n.m.",
   ("捕手", "receptor"): "n.m.",
   ("投球手", "lanzador"): "n.m.",
   # Sec10
   ("跨栏运动员", "vallista"): "n.m.",
   ("最后的", "último"): "adj.",
   # Sec11
   ("拳击", "boxeo"): "n.m.",
   ("拳击运动员", "boxeador"): "n.m.",
   ("打", "golpe"): "n.m.",
 },
 "subs": [
   # Sec1
   ("Aunque Yao Ming es considerado el mejor en baloncesto, tenis de mesa le falla, aún en contra de un niño",
    "Aunque Yao Ming es considerado el mejor en baloncesto, en el tenis de mesa le falla, incluso contra un niño"),
   # Sec2
   ("La bolsa izquierda es misma de la derecha",
    "La bolsa izquierda es igual que la derecha"),
   # Sec3
   ("En el centro de la Península, posibilidad de chubascos",
    "En el centro de la península, posibilidad de chubascos"),
   # Sec4
   # Sec5
   ("La gente fija en el coche para ver a su estrella favorita",
    "La gente se fija en el coche para ver a su estrella favorita"),
   # Sec6
   ("Y Cuál es el título de este maravilloso libro?” le pregunté con un afán fingido. “",
    "¿Y cuál es el título de este maravilloso libro? —le pregunté con un afán fingido—"),
   ("El juez expulsa al hombre del partido",
    "El juez expulsa al hombre del campo de juego"),
   # Sec7
   ("El_indexes, que ya marca dos goles, tiene la esperanza de celebrar su reencuentro con su antiguo club de una manera más hermosa",
    "El delantero brasileño, que ya marcó dos goles, tiene la esperanza de celebrar su reencuentro con su antiguo club de una manera más hermosa"),
   # Sec8
   # Sec9
   ("La vida real está, lejos de las llamadas telefónicas de mis gerentes y trabajo duro!",
    "¡La vida real está lejos de las llamadas telefónicas de mis gerentes y del trabajo duro!"),
   # Sec10
   ("Si ejecuta un maratón y que está a punto de cruzar la línea de meta, no dejarás de decir",
    "Si ejecutas un maratón y estás a punto de cruzar la línea de meta, no dejarás de decir"),
   # Sec11
   # Sec10 引语改为西语规范引号
   ("Si ejecutas un maratón y estás a punto de cruzar la línea de meta, no dejarás de decir, “oh, una vez que pase, se acaba.”",
    "Si ejecutas un maratón y estás a punto de cruzar la línea de meta, no dejarás de decir: «Ah, una vez que pase, se acaba»."),
   ("Además, el boxeo puede ser una suave conformación de figura, especialmente para músculos del brazo",
    "Además, el boxeo puede ser una suave conformación de la figura, especialmente para los músculos del brazo"),
 ],
 "zh_subs": [
   # Sec2 中文「最好的台球是象牙做的」——西语 bolas de billar（台球=球）尚可，保留
   # Sec10 中文「非洲人拿了半程马拉松的冠军」——media maratón=半程马拉松，保留
   # Sec11 中文「第二轮更容易发挥」——保留
 ],
}

G33 = {
 "name": "旅行",
 "raw": "_tools/parte33_raw.txt",
 "typo": {
   "falt a": "falta",                          # falt a el agua（词内空格）
   "gobiernoertain": "gobierno",       # stray 串（我改回脚本误插）
 },
 "fix": {
   # ---- Sec1 地球
   # ---- Sec2 大海
   # ---- Sec3 天气气候
   # ---- Sec4 风
   # ---- Sec5 雨
   # ---- Sec7 水
   ("水坝", "presas"): "presa",                # presas=复数（水坝群）；单数 presa
   ("洒水壶", "aspersor"): "regadera",
   # ---- Sec8 夜晚
   ("黑暗", "negro"): "oscuridad",             # negro=黑色的（形）；黑暗=oscuridad
   ("雷", "trueno"): "trueno",
   # ---- Sec9 植物
   ("砍伐", "disparar"): "talar",              # disparar=射击/开火
   ("树洞", "huecos de los árboles"): "hueco del árbol",
   # ---- Sec10 爬行动物
   ("爬行的", "rastreo"): "reptante",          # rastreo=追踪/痕迹
   ("壁虎", "lagarto"): "gecko",               # 壁虎=gecko（蜥蜴是 lagarto）
   ("响尾蛇", "cascabel"): "serpiente de cascabel",
   # ---- Sec12 鸟类
   ("喔喔叫", "cacareando"): "cacarear",       # cacareando=正在叫（副词）
   ("卵", "óvulo"): "huevo",                   # óvulo=卵子（生理学）；鸟卵=huevo
   ("喂养", "recaudar"): "alimentar",          # recaudar=征收
   # ---- Sec13 其他动物
   ("吸盘触角", "antena"): "tentáculo",        # antena=天线
   ("单细胞", "célula sola"): "célula",        # «单细胞»=célula（单数即可）
   # ---- Sec14 海滩
   ("贝壳", "cáscara"): "concha",              # cáscara=外壳；贝壳=concha
   # ---- Sec15 旅行
   ("借宿", "pasar la noche con"): "alojarse",
   ("停下", "detener"): "detenerse",
   # ---- Sec16 旅游景点
   # ---- Sec17 旅游景点（2）
   ("纪念品", "souvenir"): "recuerdo",         # souvenir=法语音译，西语用 recuerdo
   ("洞穴", "agujero"): "cueva",               # agujero=洞眼
   # ---- Sec18 城堡教堂
   ("倒塌", "colapso"): "derrumbe",            # colapso=崩溃
   # ---- Sec19 露营
   # ---- Sec20 相机
   ("曝光", "exponer"): "exposición",          # 中文是名词「曝光」
 },
 "pos": {
   # Sec1
   ("世界", "mundo"): "n.m.",
   ("世界的", "global"): "adj.",
   ("大洲", "continente"): "n.m.",
   ("欧洲", "Europa"): "n.f.",
   ("亚洲", "Asia"): "n.f.",
   ("非洲", "África"): "n.f.",
   ("大洋洲", "Oceanía"): "n.f.",
   ("南极洲", "Continente Antártico"): "n.m.",
   # Sec2
   ("海", "mar"): "n.m.",
   ("海湾", "golfo"): "n.m.",
   ("洋流", "corriente"): "n.f.",
   # Sec3
   ("天气", "tiempo"): "n.m.",
   ("气候", "clima"): "n.m.",
   # Sec4
   ("风", "viento"): "n.m.",
   ("速度", "velocidad"): "n.f.",
   ("吹", "soplar"): "v.i.",
   ("旋风", "torbellino"): "n.m.",
   ("台风", "tifón"): "n.m.",
   ("龙卷风", "tornado"): "n.m.",
   ("飓风", "huracán"): "n.m.",
   # Sec5
   ("雨", "lluvia"): "n.f.",
   ("水汽", "vapor"): "n.m.",
   ("云", "nube"): "n.f.",
   ("凝结", "condensación"): "n.f.",
   # Sec6
   ("雪", "nieve"): "n.f.",
   ("雾", "niebla"): "n.f.",
   ("烟雾", "humo"): "n.m.",
   ("灰尘", "polvo"): "n.m.",
   ("雪白的", "blanco"): "adj.",
   # Sec7
   ("水", "agua"): "n.f.",
   ("雪糕", "helado"): "n.m.",
   ("供应", "suministro"): "n.m.",
   # Sec8
   ("夜晚，夜间", "noche"): "n.f.",
   ("闪电", "relámpago"): "n.m.",
   ("雷", "trueno"): "n.m.",
   ("黑暗", "oscuridad"): "n.f.",
   ("噩梦", "pesadilla"): "n.f.",
   # Sec9
   ("植物", "planta"): "n.f.",
   ("光", "luz"): "n.f.",
   ("细枝", "ramita"): "n.f.",
   ("年轮", "anillo"): "n.m.",
   ("木材", "madera"): "n.f.",
   ("阴凉处", "sombra"): "n.f.",
   ("砍伐", "talar"): "v.t.",
   # Sec10
   ("爬行动物", "reptil"): "n.m.",
   ("爬行的", "reptante"): "adj.",
   ("乌龟", "tortuga"): "n.f.",
   ("蛇", "serpiente"): "n.f.",
   ("蟒蛇", "boa"): "n.f.",
   ("眼镜蛇", "naja"): "n.f.",
   ("壁虎", "gecko"): "n.m.",
   ("蟾蜍", "sapo"): "n.m.",
   ("蜗牛", "caracol"): "n.m.",
   ("壳", "caparazón"): "n.m.",
   ("血清", "suero"): "n.m.",
   # Sec11
   ("哺乳动物", "mamífero"): "n.m.",
   ("胚胎", "embrión"): "n.m.",
   # Sec12
   ("卵", "huevo"): "n.m.",
   ("下蛋", "oviposición"): "n.f.",
   ("喂养", "alimentar"): "v.t.",
   ("饲养", "alimentar"): "v.t.",
   # Sec13
   ("蜘蛛", "araña"): "n.f.",
   ("蛛网", "telaraña"): "n.f.",
   ("吸盘触角", "tentáculo"): "n.m.",
   ("微生物", "microbio"): "n.m.",
   # Sec14
   ("沙滩", "playa"): "n.f.",
   ("海角", "promontorio"): "n.m.",
   ("海堤", "malecón"): "n.m.",
   ("浪尖", "cresta"): "n.f.",
   ("比基尼", "bikini"): "n.m.",
   ("太阳伞", "sombrilla"): "n.f.",
   ("遮篷", "toldo"): "n.m.",
   ("贝壳", "concha"): "n.f.",
   # Sec15
   ("旅行者", "pasajero"): "n.m.",
   ("路线", "itinerario"): "n.m.",
   ("探险", "explorar"): "v.t.",
   # Sec16
   ("旅游者", "turista"): "n.m.",
   ("避暑胜地", "veraneo"): "n.m.",
   ("宫殿", "palacio"): "n.m.",
   ("祭坛", "altar"): "n.m.",
   ("铭文", "epígrafe"): "n.m.",
   ("石笋", "estalagmita"): "n.f.",
   ("钟乳石", "estalactita"): "n.f.",
   ("地点", "ubicación"): "n.f.",
   ("洞穴", "cueva"): "n.f.",
   # Sec17
   ("纪念品", "recuerdo"): "n.m.",
   ("风光", "paisaje"): "n.m.",
   ("洞穴", "agujero"): "n.m.",
   ("皇帝的", "imperial"): "adj.",
   # Sec18
   ("城堡", "castillo"): "n.m.",
   ("废墟", "ruina"): "n.f.",
   ("教堂", "iglesia"): "n.f.",
   ("小教堂", "capilla"): "n.f.",
   ("庙宇", "templo"): "n.m.",
   ("圣象", "santo"): "n.m.",
   ("攻击", "ataque"): "n.m.",
   ("宏伟的", "gigantesco"): "adj.",
   # Sec19
   ("萤火", "luciérnaga"): "n.f.",
   ("帐篷", "carpa"): "n.f.",
   ("背包", "paquete"): "n.m.",
   ("吊床", "hamaca"): "n.f.",
   ("钻孔", "perforación"): "n.f.",
   ("存活", "sobrevivir"): "v.i.",
   ("生活，生存", "vivir"): "v.i.",
   # Sec20
   ("相机", "cámara"): "n.f.",
   ("照片", "fotografía"): "n.f.",
   ("照片", "foto"): "n.f.",
   ("取景器", "visor"): "n.m.",
   ("摄影师", "fotógrafo"): "n.m.",
   ("胶卷", "película"): "n.f.",
   ("快门", "obturador"): "n.m.",
   ("三脚架", "trípode"): "n.m.",
   ("曝光", "exposición"): "n.f.",
 },
 "subs": [
   # Sec1 直引号 -> 西语规范；Africa 缺重音
   ("El llamado “clima” no existe, y el calor abrasador se extiende a toda la superficie del globo, igual al ecuador y los polos",
    "El llamado «clima» no existe, y el calor abrasador se extiende a toda la superficie del globo, igual que en el ecuador y en los polos"),
   ("El arte de vivir. La vida es una cosa maravillosa; como una belleza luz en esta tierra",
    "El arte de vivir: la vida es una cosa maravillosa, como una luz hermosa sobre esta tierra"),
   ("Africa es un continente de perfil sólido",
    "África es un continente de perfil sólido"),
   ("Beijing se encuentra a 116 grados de longitud este",
    "Pekín se encuentra a 116 grados de longitud este"),
   ("El gobiernoertain alerted a la población de la llegada de un huracán",
    "El gobierno alerted a la población de la llegada de un huracán"),
   # Sec2
   ("Durante años, el mar ha provocado repulsión. No fue hasta mediados del siglo XVIII que comenzó a nacer el anhelo por la mar",
    "Durante años, el mar ha provocado repulsión. No fue hasta mediados del siglo XVIII cuando comenzó a nacer el anhelo por la mar"),
   # Sec3
   ("Ablandan los fríos",
    "Se ablandan los fríos"),
   # Sec4
   ("La salida de las hojas, .a causa del viento persistente, o que los árboles no recuerdan?",
    "¿La salida de las hojas es a causa del viento persistente, o es que los árboles no recuerdan?"),
   # Sec5
   ("La tormenta va de vencido",
    "La tormenta va a pasar"),
   # Sec6
   (".Y si hacemos un muñeco de nieve?",
    "¿Y si hacemos un muñeco de nieve?"),
   # Sec7
   # Sec8
   ("Amanece tarde invierno",
    "Amanece tarde en invierno"),
   ("Qué tarde! Me tengo que ir.",
    "¡Qué tarde! Me tengo que ir!"),
   ("Ayer anocheció despejado pero hoy ha amanecido lloviendo",
    "Ayer anocheció despejado, pero hoy ha amanecido lloviendo"),
   # Sec9
   # Sec10
   # Sec12
   ("La ave nacional de Francia es el gallo, que creen que es valiente y tiene endurecimiento",
    "El ave nacional de Francia es el gallo, al que consideran valiente y tenaz"),
   ("Los huevos son muy alimenticios",
    "Los huevos son muy nutritivos"),
   # Sec13
   ("El otro día ví uno de sedas de araña que era maravilloso",
    "El otro día vi una tela de araña que era maravillosa"),
   # Sec14
   ("Con cielo azul y mar de arena blanca, tiene un paisaje natural único. Las condiciones naturales contribuyen al desarrollo del turismo, y construcción de una playa internacional",
    "Con cielo azul y mar de arena blanca, tiene un paisaje natural único. Las condiciones naturales contribuyen al desarrollo del turismo y a la construcción de una playa internacional"),
   ("El cabo — que habían pasado por su fin — debe estar conectado con el país",
    "El cabo —que habían pasado por su fin— debe estar conectado con el país"),
   # Sec15
   ("Queremos viajar a Europa algún día",
    "Quiero viajar a Europa algún día"),
   # Sec16
   ("Si ves a un turista que está perdido, usted puede ir a ofrecer ayuda",
    "Si ves a un turista que está perdido, puedes ir a ofrecerle ayuda"),
   ("Estamos en una cueva donde el aire no nos falta, de lo contrario, vientos nos alcanzan",
    "Estamos en una cueva donde el aire no nos falta; de lo contrario, los vientos nos alcanzan"),
   # Sec17
   # Sec18
   ("La confianza es como un castillo de arena, difícil de construir pero fácil de destruir",
    "La confianza es como un castillo de arena: difícil de construir, pero fácil de destruir"),
   # Sec19
   ("La pez dijo al agua: nunca te voy a dejar porque si no estuviera contigo yo nunca hubiera vivir",
    "El pez le dijo al agua: nunca te voy a dejar, porque si no estuviera contigo yo nunca hubiera vivido"),
   # Sec20
   ("Para un actor, la cámara es los ojos del público",
    "Para un actor, la cámara son los ojos del público"),
   ("Le recomienda a tomar fotos de sus cosas preciosas, con el fin de protegerlas mejor",
    "Le recomienda tomar fotos de sus cosas preciosas, con el fin de protegerlas mejor"),
 ],
 "zh_subs": [
   # Sec10 「我却被癞蛤蟆缠住了」——原文 Consigues un príncipe（你得到王子）
   # Sec13 「热度帮助人体杀死入侵的细菌」——原文 La fiebre（发烧）帮助身体 destroy 微生物
 ],
}

G34 = {
 "name": "政治相关",
 "raw": "_tools/parte34_raw.txt",
 "typo": {
   "cle ": "de ",            # lista cle aplicación -> lista de aplicación
   "permanence": "permanece",  # 拼写错误
   "españa": "España",       # 西语国名首字母大写
   "EEñUU": "EE.UU",          # clean 的 ñ 自愈误伤缩写（EE.UU），末尾句点由引擎补
   "explotaclón": "explotación",   # OCR：l->ó
 },
 "fix": {
   # ---- Sec1 国家政治
   ("公务员", "oficial"): "funcionario",   # oficial=军官；公务员=funcionario
   # ---- Sec3 社会形态
   ("社会", "comunidad"): "sociedad",      # comunidad=社区；社会=sociedad
   # ---- Sec4 社会发展
   ("变革", "cambiar"): "cambiar",         # 中文名词「变革」=transformación
   # ---- Sec5 政治制度
   ("君主专制", "monarquía"): "monarquía absoluta",   # 君主专制≠君主制
   # ---- Sec6 国家各部门
   # ---- Sec7 竞选
   # ---- Sec8 投票
   # ---- Sec9 外交（1）
   ("庇护", "patrocinio"): "protección",   # patrocinio=赞助/庇护(法律)
   # ---- Sec10 外交（2）
   # ---- Sec11 权利义务
   ("游行", "manifestación"): "manifestación",
   ("侵犯", "invadir"): "vulnerar",         # invadir=军事入侵；侵犯权利=vulnerar
 },
 "pos": {
   # Sec1
   ("国家", "país"): "n.m.",
   ("国家", "nación"): "n.f.",
   ("政治", "política"): "n.f.",
   ("参议院", "senado"): "n.m.",
   ("国会，议会", "parlamento"): "n.m.",
   ("公务员", "funcionario"): "n.m.",
   # Sec3
   ("社会", "sociedad"): "n.f.",
   ("封建制度", "feudalismo"): "n.m.",
   ("奴隶制", "esclavitud"): "n.f.",
   ("社会主义", "socialismo"): "n.m.",
   ("资本主义", "capitalismo"): "n.m.",
   ("个人主义", "individualismo"): "n.m.",
   ("阶段", "etapa"): "n.f.",
   # Sec4
   ("革命", "revolución"): "n.f.",
   ("改革", "reforma"): "n.f.",
   ("全球化", "globalización"): "n.f.",
   ("城市化", "urbanización"): "n.f.",
   # Sec5
   ("政策", "política"): "n.f.",
   ("结构", "estructura"): "n.f.",
   ("马克思主义", "marxismo"): "n.m.",
   ("无产阶级", "proletariado"): "n.m.",
   ("资产阶级", "burguesía"): "n.f.",
   ("专制", "autocracia"): "n.f.",
   ("主权", "soberanía"): "n.f.",
   ("独立的", "independiente"): "adj.",
   # Sec6
   ("中央集权制", "centralismo"): "n.m.",
   ("部", "ministerio"): "n.m.",
   ("部门", "departamento"): "n.m.",
   ("部长", "ministro"): "n.m.",
   # Sec7
   ("竞选活动", "campaña"): "n.f.",
   ("总统的", "presidencial"): "adj.",
   ("党", "partido"): "n.m.",
   ("连任", "reelección"): "n.f.",
   ("演说", "discurso"): "n.m.",
   ("竞争", "competencia"): "n.f.",
   ("口号", "lema"): "n.m.",
   ("候选人", "candidato"): "n.m.",
   ("支持者", "partidario"): "n.m.",
   ("辩论", "argumentar"): "v.i.",
   ("选举", "elegir"): "v.t.",
   # Sec8
   ("选票", "votación"): "n.f.",
   ("选票主义", "electoralista"): "n.m.",
   ("公民投票", "reférendum"): "n.m.",
   ("轮", "ronda"): "n.f.",
   ("结果", "resultado"): "n.m.",
   ("投票箱", "urna"): "n.f.",
   ("不固定的", "flotante"): "adj.",
   ("长久的", "sostenible"): "adj.",
   # Sec9
   ("外交", "diplomacia"): "n.f.",
   ("外国的", "extranjero"): "adj.",
   ("外国人", "extranjero"): "n.m.",
   ("分歧", "divergencia"): "n.f.",
   ("途径", "manera"): "n.f.",
   ("发言人", "portavoz"): "n.m.",
   ("大使", "embajador"): "n.m.",
   ("领事", "cónsul"): "n.m.",
   ("驱逐", "expulsión"): "n.f.",
   ("豁免", "exención"): "n.f.",
   ("庇护", "protección"): "n.f.",
   # Sec10
   ("外交官", "diplomático"): "n.m.",
   ("大使馆", "embajada"): "n.f.",
   ("领事的", "consular"): "adj.",
   ("彻底地", "totalmente"): "adv.",
   ("代表团", "delegación"): "n.f.",
   ("移民", "inmigrante"): "n.m.",
   ("断绝", "romper"): "v.t.",
   ("恢复", "restaurar"): "v.t.",
   ("合作", "cooperar"): "v.i.",
   ("抗议", "protestar"): "v.i.",
   ("中断", "suspender"): "v.t.",
   # Sec11
   ("权利", "derecho"): "n.m.",
   ("自由", "libertad"): "n.f.",
   ("义务", "deber"): "n.m.",
   ("游行", "manifestación"): "n.f.",
   ("人格", "personalidad"): "n.f.",
   ("尊严", "dignidad"): "n.f.",
   ("种族", "raza"): "n.f.",
   ("性别", "sexo"): "n.m.",
   ("平等的", "igual"): "adj.",
   ("承担", "asumir"): "v.t.",
   ("侵犯", "vulnerar"): "v.t.",
   ("团结", "unir"): "v.t.",
 },
 "subs": [
   # Sec3 拼写
   ("La moda pasa, pero el estilo permanence",
    "La moda pasa, pero el estilo permanece"),
   # Sec5 中文译文与西语不符
   ("La mayoría de los votantes libres lo respaldan y hace que el candidato republicano quede atrás en las encuestas",
    "La mayoría de los votantes libres lo respaldan, y eso hace que el candidato republicano quede atrás en las encuestas"),
   # Sec6 农业句：养殖业->农业
   ("La agricultura tiene más potencia de el desarrollo económico en la economía rural",
    "La agricultura tiene más potencial de desarrollo económico en la economía rural"),
   ("Tenemos una política estricta para la admisión y la lista de aplicación",
    "Tenemos una política estricta para la admisión y la lista de solicitudes"),
   ("No hay un abismo infranqueable entre la democracia y el centralismo y los dos son necesarios",
    "No hay un abismo infranqueable entre la democracia y el centralismo: los dos son necesarios"),
   # Sec7
   (".Por qué no argumentas mejor tus ideas?",
    "¿Por qué no argumentas mejor tus ideas?"),
   # Sec9
   ("El orador más grande en el mundo es el éxito",
    "El orador más grande del mundo es el éxito"),
   # Sec10
   ("Fue destinado como canciller a la embajada española en Londeres",
    "Fue destinado como canciller a la embajada española en Londres"),
   # Sec11
   ("El constructor se niega a asumir la respondabilidad del accidente y culpa de lo ocurrido al arquitecto",
    "El constructor se niega a asumir la responsabilidad del accidente y culpa de lo ocurrido al arquitecto"),
 ],
 "zh_subs": [
   # Sec6 原文「养殖业」但西语 es La agricultura（农业）
   ("养殖业是农村经济中最具发展潜力的主导产业之—。", "农业是农村经济中最具发展潜力的主导产业之一。"),
   # Sec5 中文「背向大多数的自由选举人并且…」与西语不符
   ("背向大多数的自由选举人并且在民意测验中使得共和党候选人落后。",
    "大多数自由选票的选民支持他，这使得共和党候选人在民意测验中落后。"),
   # Sec10 中文「外交官助理」与西语 canciller（外交部长）不符
   ("他作为外交官助理被派往西班牙驻伦敦大使馆。", "他作为外交部长助理被派往西班牙驻伦敦大使馆。"),
   # Sec11 中文「没有调查就没有发言权」原文写「调査」（异体字）
   ("没有调查就没有发言权。", "没有调查就没有发言权。"),
 ],
}

G35 = {
 "name": "经济基本知识",
 "raw": "_tools/parte35_raw.txt",
 "typo": {
   "pueclen": "pueden",                 # OCR 词形错误
   "wall street": "Wall Street",        # 专名大写
 },
 "fix": {
   # ---- Sec1 各种产业
   # ---- Sec2 经济状况
   # ---- Sec3 国际贸易
   # ---- Sec4 改革开放
   # ---- Sec5 WTO
   # ---- Sec6 钱币
   # ---- Sec7 经济政策
   # ---- Sec8 外贸
   # ---- Sec9 市场
   # ---- Sec10 金融
   ("份额", "contribución"): "cuota",     # contribución=贡献；份额=cuota/porcentaje
   # Sec2
   ("复苏", "revivir"): "recuperación",
 },
 "pos": {
   # Sec1
   ("商业", "comercio"): "n.m.",
   ("农业", "agricultura"): "n.f.",
   ("旅游业", "turismo"): "n.m.",
   ("广告业", "publicidad"): "n.f.",
   ("娱乐", "diversión"): "n.f.",
   ("印刷", "impresión"): "n.f.",
   # Sec2
   ("国有化", "nacionalización"): "n.f.",
   ("私有化", "privatización"): "n.f.",
   ("经济", "economía"): "n.f.",
   ("危机", "crisis"): "n.f.",
   ("萧条", "recesión"): "n.f.",
   ("通货膨胀", "inflación"): "n.f.",
   ("萧条的", "estancado"): "adj.",
   ("经济的", "económico"): "adj.",
   ("复苏", "recuperación"): "n.f.",
   # Sec3
   ("顺差", "superávit"): "n.m.",
   # Sec2 复苏：revivir=复活；经济复苏=recuperación
   ("逆差，赤字", "déficit"): "n.m.",
   ("大大地", "enormemente"): "adv.",
   ("廉价推销", "descuento"): "n.m.",
   ("加工", "procesamiento"): "n.m.",
   ("国际的", "internacional"): "adj.",
   ("促进", "promover"): "v.t.",
   # Sec4
   ("贸易保护主义者", "proteccionista"): "n.m.",
   ("革新，创新", "innovación"): "n.f.",
   ("创新的", "innovador"): "adj.",
   ("创新者", "innovador"): "n.m.",
   ("新技术", "nueva técnica"): "n.f.",
   ("改革，革新", "reforma"): "n.f.",
   ("改革", "reformación"): "n.f.",
   ("改革者", "reformador"): "n.m.",
   ("改革", "reformar"): "v.t.",
   # Sec5
   ("商品倾销", "dumping"): "n.m.",
   ("海关", "aduana"): "n.f.",
   ("海关人员", "aduanero"): "n.m.",
   ("税", "impuesto"): "n.m.",
   ("关税", "arancel"): "n.m.",
   ("许可", "permitir"): "v.t.",
   ("调解", "conciliar"): "v.t.",
   # Sec6
   ("伪造", "falsificación"): "n.f.",
   ("贬值", "devaluación"): "n.f.",
   ("增值", "revaluación"): "n.f.",
   ("资金", "fondo"): "n.m.",
   ("资金", "capital"): "n.m.",
   ("使贬值", "devaluar"): "v.t.",
   # Sec7
   ("零售业", "minorista"): "n.m.",
   ("市场", "mercado"): "n.m.",
   # Sec8
   ("出口", "exportación"): "n.f.",
   ("发票", "factura"): "n.f.",
   ("百分比", "porcentaje"): "n.m.",
   ("运费", "flete"): "n.m.",
   ("保险", "seguro"): "n.m.",
   ("花费", "gasto"): "n.m.",
   ("利润", "beneficio"): "n.m.",
   ("因素", "factor"): "n.m.",
   ("进口", "importar"): "v.t.",
   # Sec9
   ("市场", "mercado"): "n.m.",
   ("融资", "financiación"): "n.f.",
   ("保证金", "depósito"): "n.m.",
   ("到期日", "madurez"): "n.f.",
   ("稳定的", "constante"): "adj.",
   ("表明", "manifestar"): "v.t.",
   ("利用", "utilizar"): "v.t.",
   # Sec10
   ("冒险", "aventurar"): "v.t.",
   ("凭证", "certificado"): "n.m.",
   ("份额", "cuota"): "n.f.",
   ("华尔街", "Wall Street"): "n.m.",
   ("分配", "distribuir"): "v.t.",
 },
 "subs": [
   # Sec1 首句：consiste en los perdidos（丢失）->Son las ventas/pedidos（订单）
   ("Principalmente el comercio exterior consiste en los perdidos y el comercio nacional también",
    "Principalmente el comercio exterior consiste en las ventas, y también en el comercio nacional"),
   # Sec2 首句：un moto importante（motor 错拼）-> un motor importante
   ("El consumo interno no es un moto importante, es por ello que tenemos una economía que crece a pesar de que su población sigue siendo mayoritariamente pobre",
    "El consumo interno no es un motor importante; por eso tenemos una economía que crece a pesar de que su población sigue siendo mayoritariamente pobre"),
   # Sec2 次句：原句结构断裂
   ("Pero los expertos no están de acuerdo con que el descenso de las tasas de interés bancarias, debido a la inflación",
    "Pero los expertos no están de acuerdo con el descenso de las tasas de interés bancarias debido a la inflación"),
   # Sec5 首句：关系词缺失 + 语序
   ("Estarás inclinado a rayar la otra, no estás amable. Ten cuidado: personas que ofende hoy son quizás los que tratará de conciliar las gracias mañana",
    "Estarás inclinado a rayar a la otra porque no estás amable. Ten cuidado: las personas a las que ofendes hoy son quizás las que querrás conciliar mañana"),
   ("Pasamos un mal trago, en la aduana",
    "Pasamos un mal trago en la aduana"),
   # Sec6
   # Sec7
   ("En particular”, añadió, “los instrumentos de lucha contra el lavado de dinero y los delitos cibernéticos no son eficientes.”",
    "«En particular», añadió, «los instrumentos de lucha contra el lavado de dinero y los delitos cibernéticos no son eficientes»."),
   ("Los modos de funcionamiento, además de venta por el menor, pueden utilizar las ventajas locales para distribuir productos y promover el desarrollo de mercados locales para los productos y servicios de los clientes",
    "Los modos de funcionamiento, además de la venta al por menor, pueden utilizar las ventajas locales para distribuir productos y promover el desarrollo de mercados locales para los productos y servicios de los clientes"),
   # Sec9
   # Sec10
   ("El marinero se había retirado a un segundo plano, miró el mar, evidentemente, debatiéndose entre el deseo de ganar una suma enorme y el temor de aventurarse tan lejos",
    "El marinero se había retirado a un segundo plano y miró el mar, evidentemente debatiéndose entre el deseo de ganar una suma enorme y el temor de aventurarse tan lejos"),
   ("Si el propietario decide unilateralmente rescindir el contrato antes de tiempo, se le exigirá que reembolse todos los gastos incurridos por el propietario, así como el daño",
    "Si el propietario decide unilateralmente rescindir el contrato antes de tiempo, se le exigirá que reembolse todos los gastos incurridos, así como el daño"),
 ],
 "zh_subs": [
   # Sec1 中文「以外贸定单为主」— 西语原文说的是「销售」
   ("以外贸定单为主，兼国内贸易。", "以对外贸易为主，也包括国内贸易。"),
   # Sec6 中文「我有资本，但没时间搞生产」— 西语 Me quedé sin capital（我没资本了）
   ("我有资本，但没时间搞生产。", "我没了资本，但也没闲下来搞生产。"),
   # Sec7 中文「现行文书」— 西语 instrumentos（手段/工具）
   ("处理洗钱和网上犯罪的现行文书不够有效。", "处理洗钱和网络犯罪的现行手段不够有效。"),
   # Sec8 中文「这不是一笔必须的开销吧」— 西语 No se trata de un gasto necesario
   ("这不是一笔必须的开销吧。", "这不算一笔必要的开销。"),
 ],
}

G36 = {
 "name": "经济行为",
 "raw": "_tools/parte36_raw.txt",
 "typo": {
   "cientò": "ciento",                  # 倒勾->o
 },
 "fix": {
   # ---- Sec1 储蓄
   # ---- Sec2 投资
   # ---- Sec3 理财
   ("回报", "rendir cuenta"): "rendir cuentas",   # 西语固定说法（复数）
   # ---- Sec4 借贷
   ("放债，放高利贷", "logrería"): "usura",  # usura=高利贷；logrería 非西语词
   ("困境", "molestia"): "apuros",             # molestia=麻烦/不适；困境=apuros
   ("截止日期", "fecha de caducidad"): "fecha de vencimiento",  # 债务语境用 vencimiento
   # ---- Sec5 信用
   # ---- Sec6 汇率
   # ---- Sec7 交税
   ("逃税", "fraude"): "evasión fiscal",   # fraude=欺诈（泛）；逃税=evasión fiscal
   ("税务员", "colector"): "inspector de impuestos",  # colector=收集者
   # ---- Sec8 下岗与就业
 },
 "pos": {
   # Sec1
   ("银行", "banco"): "n.m.",
   ("钱", "dinero"): "n.m.",
   ("存款", "depósito"): "n.m.",
   ("储蓄", "ahorro"): "n.m.",
   ("储蓄者", "ahorrador"): "n.m.",
   ("利息", "interés"): "n.m.",
   ("比例", "escala"): "n.f.",
   ("不同的", "diferente"): "adj.",
   ("有益", "beneficioso"): "adj.",
   ("无偿地", "gratuitamente"): "adv.",
   # Sec2
   ("投资者", "inversionista"): "n.m.",
   ("谨慎的", "discreto"): "adj.",
   ("冒险", "riesgo"): "n.m.",
   ("意识", "conciencia"): "n.f.",
   ("期限", "plazo"): "n.m.",
   ("收益", "beneficio"): "n.m.",
   ("文件夹", "carpeta"): "n.f.",
   ("困难", "dificultad"): "n.f.",
   ("投资", "invertir"): "v.t.",
   # Sec3
   ("财产", "propiedad"): "n.f.",
   ("所有物", "posesión"): "n.f.",
   ("富有的", "rico"): "adj.",
   ("投资", "inversión"): "n.f.",
   ("基金", "fondo"): "n.m.",
   ("财产", "fortuna"): "n.f.",
   ("客户", "cliente"): "n.m.",
   ("投机的", "especulativo"): "adj.",
   ("公司", "compañía"): "n.f.",
   ("捐赠", "contribuir"): "v.t.",
   ("回报", "rendir cuentas"): "v.pr.",
   ("安排", "organizar"): "v.t.",
   # Sec4
   ("高利贷", "usura"): "n.f.",
   ("借贷", "endeudamiento"): "n.m.",
   ("道德的", "ético"): "adj.",
   ("债务", "deuda"): "n.f.",
   ("债务人", "deudor"): "n.m.",
   ("借款方", "prestatario"): "n.m.",
   ("困境", "apuros"): "n.m.",
   ("欺骗", "decepción"): "n.f.",
   ("骗子", "mentiroso"): "n.m.",
   ("放债，放高利贷", "usura"): "n.f.",
   # Sec5
   ("信用", "fidelidad"): "n.f.",
   ("可信赖的", "fiel"): "adj.",
   ("扩大", "ampliar"): "v.t.",
   ("等级", "grado"): "n.m.",
   ("偿还", "reembolso"): "n.m.",
   ("延期", "posponer"): "v.t.",
   ("预先的", "anticipado"): "adj.",
   ("津贴", "subsidio"): "n.m.",
   ("偿还", "pagar"): "v.t.",
   # Sec6
   ("外汇", "divisas"): "n.f.",
   ("比率", "proporción"): "n.f.",
   ("可兑换的", "convertible"): "adj.",
   ("浮动", "fluctuación"): "n.f.",
   ("浮动的", "flotante"): "adj.",
   ("固定的", "fijo"): "adj.",
   ("可变的", "cambiable"): "adj.",
   ("直接的", "directo"): "adj.",
   ("间接的", "indirecto"): "adj.",
   ("一致", "concordancia"): "n.f.",
   ("操纵", "operar"): "v.t.",
   ("变换", "cambiar"): "v.t.",
   # Sec7
   ("税", "impuesto"): "n.m.",
   ("逃税", "evasión fiscal"): "n.f.",
   ("可扣除的", "deducible"): "adj.",
   ("税务员", "inspector de impuestos"): "n.m.",
   ("关税", "arancel"): "n.m.",
   ("纳税人", "contribuyente"): "n.m.",
   ("免除", "librar"): "v.t.",
   ("总计的", "total"): "adj.",
   # Sec8
   ("福利", "bienestar"): "n.m.",
   ("卓越的", "notable"): "adj.",
   ("失业", "desempleo"): "n.m.",
   ("工作者", "trabajador"): "n.m.",
   ("泡沫", "espuma"): "n.f.",
   ("失业，失业津贴", "cesantía"): "n.f.",
   ("就业，职位", "empleo"): "n.m.",
   ("工作", "trabajo"): "n.f.",
   ("职位，岗位", "puesto"): "n.m.",
   ("职位", "posición"): "n.f.",
   ("职位", "plaza"): "n.f.",
   ("工作，职业", "ocupación"): "n.f.",
   ("职业，行业", "profesión"): "n.f.",
   ("等待", "esperar"): "v.t.",
   ("获得", "adquirir"): "v.t.",
   ("下岗", "ser despedido del trabajo"): "",
 },
 "subs": [
   # Sec1
   ("La Bolsa aumentar tímidamente",
    "La Bolsa aumentó tímidamente"),
   # Sec2
   ("Aunque invirtió mucho en el negocio, no vendió una escoba",
    "Aunque invirtió mucho en el negocio, no vendió ni una escoba"),
   # Sec3
   ("Apunta los datos de todos clientes y después pásalos al ordenador",
    "Apunta los datos de todos los clientes y después pásalos al ordenador"),
   # Sec4
   ("Dónde puedo obtener crédito?",
    "¿Dónde puedo obtener crédito?"),
   # Sec5 原文把 en general 写了两遍 -> 去重
   ("No está o no estará, en general, en general, en condiciones de pagar sus deudas a su vencimiento.",
    "No está o no estará, en general, en condiciones de pagar sus deudas a su vencimiento."),
   # Sec5
   # Sec6
   # Sec7
   ("Nuestra empresa siempre está respetuosa de la ley,podemos emitir facturas de impuestos de 17 por ciento de IVA",
    "Nuestra empresa siempre está respetuosa de la ley: podemos emitir facturas de impuestos de 17 por ciento de IVA"),
   # Sec8
 ],
 "zh_subs": [
   # Sec8 中文「胡安已经找到了一份临时工作」— correcto
   # Sec4 中文「他将是你的欠债人」— 原文 Seré tu deudor（我是你的债务人），中文人称错
   ("他将是你的欠债人，直到他还给你我欠你的人情。", "我将是你的债务人，直到我能报答你给我的人情。"),
   # Sec7 中文「是“一般纳税人”企业」— 西语没这句，是发票说明
   ("本公司守法经营，是“一般纳税人”企业，可开具17%增值税发票。", "本公司守法经营，可开具17%增值税发票。"),
   # Sec1 中文「银行根据顾客所存款项支付利息」— 西语 según los depósitos que haya efectuado（已存的）
   ("银行根据顾客所存款项支付利息。", "银行根据顾客此前所存的款项支付利息。"),
 ],
}

G37 = {
 "name": "宗教信仰",
 "raw": "_tools/parte37_raw.txt",
 "typo": {
   "erroresconsiguen": "errores consigue",   # OCR 粘连：errores + consiguen
   "no-tablemente": "notablemente",          # OCR：no + tablemente（断行残迹）
   "dios": "Dios",                            # 神名须大写
 },
 "fix": {
   # ---- Sec1 不同信仰
   ("信徒", "discípulo"): "creyente",         # discípulo=门徒；信徒=creyente
   ("拜物教", "fetiche"): "culto a los ídolos",  # fetiche=物神/偶物；拜物教需补 culto
   # ---- Sec2 宗教活动
   ("教规", "canon"): "canón",                # RAE 重音：canón
 },
 "pos": {
   # Sec1
   ("宗教", "religión"): "n.f.",
   ("信仰", "creencia"): "n.f.",
   ("基督教", "cristianismo"): "n.m.",
   ("天主教", "catolicismo"): "n.m.",
   ("新教", "protestantismo"): "n.m.",
   ("犹太教", "judaísmo"): "n.m.",
   ("伊斯兰教", "islamismo"): "n.m.",
   ("东正教", "ortodoxia"): "n.f.",
   ("佛教", "budismo"): "n.m.",
   ("道教", "taoísmo"): "n.m.",
   ("异端", "herejía"): "n.f.",
   ("拜物教", "culto a los ídolos"): "n.m.",
   ("救赎", "redención"): "n.f.",
   ("信徒", "creyente"): "n.m.",
   ("罪", "culpa"): "n.f.",
   ("圣经", "Biblia"): "n.f.",
   ("天使", "ángel"): "n.m.",
   ("坦白，忏悔", "confesión"): "n.f.",
   ("无神论", "ateísmo"): "n.m.",
   ("救世主", "mesías"): "n.m.",
   ("福音，福音书", "evangelio"): "n.m.",
   ("使徒，信徒", "apóstol"): "n.m.",
   # Sec2
   ("洗礼", "bautismo"): "n.m.",
   ("废除", "abolición"): "n.f.",
   ("仪式", "ceremonia"): "n.f.",
   ("教义", "dogma"): "n.m.",
   ("崇拜", "devoción"): "n.f.",
   ("福音派教义", "evangelismo"): "n.m.",
   ("教规", "canón"): "n.m.",
   ("虔诚的", "piadoso"): "adj.",
   ("该罚的", "punible"): "adj.",
   ("宗教的； 虔诚", "religioso"): "adj.",
   ("号召", "llamar"): "v.t.",
   ("征募", "reclutar"): "v.t.",
 },
 "subs": [
   # Sec1 首句结构断裂：原句把两个分句用逗号硬拼
   ("A veces, la existencia de la infancia, tal vez es la creencia en el momento cuando queremos renunciar",
    "A veces la existencia de la infancia es, tal vez, la creencia a la que recurimos cuando queremos renunciar"),
   # Sec1 谚语：原文粘连 + 缺主语
   ("Admitir los errores consigue medio del perdón",
    "Admitir los errores es conseguir la mitad del perdón"),
   # Sec1 首句的排队句
   ("Una fiesta que está directamente vinculada con el cristianismo es la Navidad",
    "Una fiesta que está estrechamente vinculada con el cristianismo es la Navidad"),
   ("Pide clemencia al dios",
    "Pide clemencia a Dios"),
   # Sec2
   ("Sabes unos dogmas católicos?",
    "¿Sabes cuáles son los dogmas católicos?"),
   ("Para los trabajadores el único camino hacia la iluminación, es ofrecer la sangre y el sudor con el fin de obtener su bautismo",
    "Para los trabajadores el único camino hacia la iluminación es ofrecer la sangre y el sudor con el fin de obtener su bautismo"),
 ],
 "zh_subs": [
   # Sec2 中文「我真受不了那么多的礼数」— 原文 No me hallo con tanta ceremonia（受不了繁文缛节）
   ("我真受不了那么多的礼数。", "我真受不了这么多的繁文缛节。"),
 ],
}

G38 = {
 "name": "传媒",
 "raw": "_tools/parte38_raw.txt",
 "typo": {
   "comprobadia": "comprobada",           # OCR：i->a
   "celebrá ": "celebrará ",              # 缺 r（原文 accents 乱）
   "pe-riodista": "periodista",           # 断行
   "ac-triz": "actriz",                   # 断行
   "im-portante": "importante",           # 断行
   "comuni-cación": "comunicación",      # 断行
   "éso": "eso",                          # RAE：éso 已废，改 eso
   "internet": "Internet",                # 专名大写
 },
 "fix": {
   # ---- Sec1 不同媒介
   ("传播", "extender"): "difundir",       # extender=延伸；传播=difundir
   # ---- Sec2 记者招待会
   ("召开", "llamar"): "convocar",         #召集/召开=convocar；llamar=叫
 },
 "pos": {
   # Sec1
   ("大众传播媒介", "medio"): "n.m.",
   ("名人", "celebridad"): "n.f.",
   ("报道", "informe"): "n.m.",
   ("收音机", "radio"): "n.f.",
   ("新闻界", "periodismo"): "n.m.",
   ("记者", "periodista"): "n.m.",
   ("日报", "diario"): "n.m.",
   ("独有的", "exclusivo"): "adj.",
   ("新闻报道", "noticia"): "n.f.",
   ("传播", "difundir"): "v.t.",
   ("散步", "caminar"): "v.pr.",
   # Sec2
   ("发言人，代言人", "portavoz"): "n.m.",
   ("新闻记者", "periodista"): "n.m.",
   ("罢工", "huelga"): "n.f.",
   ("澄清", "aclaración"): "n.f.",
   ("谣言，传闻", "rumor"): "n.m.",
   ("荒谬的", "absurdo"): "adj.",
   ("结束", "acabado"): "adj.",
   ("召开", "convocar"): "v.t.",
   ("扰乱", "confundir"): "v.t.",
 },
 "subs": [
   # Sec1 首句：原句是「各自不择手段地维护各自国家利益」的结构，缺逻辑连接
   ("Salvaguardar los intereses de sus respectivos países sin escrúpulos, para la gente de los medios, eso es el más importante",
    "Salvaguardar los intereses de sus respectivos países sin escrúpulos es, para la gente de los medios, lo más importante"),
   # Sec1 次句：单复一致 + 动词用法
   ("una gran cantidad de información y una nueva forma de vida serán capaz de propagarse por Internet por todo el mundo",
    "una gran cantidad de información y una nueva forma de vida serán capaces de propagarse por Internet por todo el mundo"),
   # Sec1 谚语
   # Sec2
   ("El actor celebrá una rueda de prensa en poco tiempo",
    "El actor celebrará una rueda de prensa dentro de poco"),
 ],
 "zh_subs": [
   # Sec1 中文「他成为了他从小就想当的新闻工作者」— 原文ewspaper（报纸）
   ("他成为了他从小就想当的新闻工作者。", "他投身于那份从童年起就让他热爱的新闻事业。"),
 ],
}

G39 = {
 "name": "法律与犯罪",
 "raw": "_tools/parte39_raw.txt",
 # clean_es 之后的 OCR 残损子串 -> 正确写法
 "typo": {
   "pro-tección": "protección",          # 断行
   "obe-decer": "obedecer",               # 断行
   "expre-sión": "expresión",             # 断行
   "pro-porción": "proporción",           # 断行
   "acci-dental": "accidental",           # 断行
   "in-quietud": "inquietud",             # 断行
   "des-pilfarro": "despilfarro",         # 断行
   "graví-simos": "gravísimos",           # 断行
   "conde-nado": "condenado",             # 断行（Sec3/Sec4 各一处）
   "identifi-cación": "identificación",   # 断行
   "au-tores": "autores",                 # 断行
   "pa-reja": "pareja",                   # 断行
   "con-fusión": "confusión",             # 断行
 },
 # (中文, clean_es 后的西语) -> 正确西语
 "fix": {
   # ---- Sec1 法律
   ("金融法", "ley de finanza"): "ley de las finanzas",   # 西语须用复数 finanzas
   # ---- Sec2 犯罪
   ("犯罪的", "pecado"): "delictivo",      # pecado=罪过(宗教)；犯罪的=delictivo
   ("假设", "asumir"): "suponer",          # 假设=suponer；asumir=承担/担任
   # ---- Sec3 犯罪行为
   ("逮捕证", "orden de prisión"): "orden de arresto",  # 逮捕证=arresto；prisión=监禁令
   ("敲诈", "exacción"): "extorsión",      # exacción=强征/征税；敲诈勒索=extorsión
   # ---- Sec4 监狱
   ("服刑", "cumpliendo una sentencia"): "cumplir una condena",  # 服刑是动词短语，非动名词
   ("围墙", "pared"): "muro",              # 围墙=muro；pared=墙/墙壁(室内)
 },
 "pos": {
   # ---- Sec1
   ("金融法", "ley de las finanzas"): "",
   ("经济法", "ley de la economía"): "",
   ("婚姻法", "ley del matrimonio"): "",
   ("商法", "código de comercio"): "",
   ("国际法", "derecho internacional"): "",
   # ---- Sec2
   ("犯罪的", "delictivo"): "adj.",
   ("假设", "suponer"): "v.t.",
   ("主体", "parte principal"): "",
   # ---- Sec3
   ("逮捕证", "orden de arresto"): "",
   ("强奸", "violar"): "v.t.",             # violar 是及物动词，文案误标 v.i.
   ("赌博", "juegos de azar"): "",
   ("黑帮", "banda siniestra"): "",
   # ---- Sec4
   ("服刑", "cumplir una condena"): "",
   ("围墙", "muro"): "n.m.",             # muro 阳性；原文标的是 pared 的 n.f.
 },
 "subs": [
   # Sec2 例3：no de casualidad 不成立（no 不能直接 + de 引导方式副词）
   ("Cometió esa falta no de casualidad", "Cometió esa falta no por casualidad"),
   # Sec3 例3：主语是说话人自己，me halló(他发现我) 改 me hallé(我发觉自己)
   ("Como no esperaba su ataque, me halló sin ninguna prevención",
    "Como no esperaba su ataque, me hallé sin ninguna prevención"),
 ],
 "zh_subs": [
   # Sec2 例5：西语只说 suceso（事件），中文却扩成「火灾/纵火」，与原文不符
   ("他在调查火灾事件，想确定是偶发性火灾还是故意纵火。",
    "他在调查这起事件，想确定是意外还是有人故意所为。"),
   # Sec3 例5：puso en marcha=启动/开始运作，中文「准备」不准确
   ("随即，民警准备一个装置用于识别和逮捕肇事者。",
    "随后，民警启动了一套用于甄别身份和逮捕肇事者的装置。"),
   # Sec4 例4：reinaba=弥漫着（混乱气氛），中文「乱七八糟」漏掉「气氛」
   ("等我到家的时候，房子里已经是乱七八糟。",
    "等我到家时，屋里已是一片混乱。"),
   # Sec2 例4：中文「罚须当罪」过简，补全为「罪罚相当」
   ("罚须当罪。", "刑罚应当与所犯的罪行相称。"),
 ],
 "CN_FIX": {
   # Sec1 词汇：obligar=强迫/迫使，不是「约束，束缚」
   "约束，束缚": "强迫，迫使",
 },
}

G40 = {
 "name": "法院",
 "raw": "_tools/parte40_raw.txt",
 "typo": {
   "de-clarar": "declarar",               # 断行
   "supe-rior": "superior",               # 断行
   "aplaza-miento": "aplazamiento",       # 断行
   "sospe-choso": "sospechoso",           # 断行
   "compare-cencia": "comparecencia",     # 断行
   "testi-monio": "testimonio",           # 断行
   "acusa-ción": "acusación",             # 断行
 },
 # (中文, clean_es 后的西语) -> 正确西语
 "fix": {
   # ---- Sec1 法院
   ("少年法庭", "tutelar de menores"): "tribunal de menores",  # 漏了 tribunal，tutelar 单独不成词
   # ---- Sec2 法院的各种判决
   ("传票", "asignación"): "citación",    # asignación=分配/指派；传票=citación
   ("缓刑", "indulto"): "suspensión de la condena",  # indulto=赦免；缓刑=suspensión de la condena
   # ---- Sec3 官司诉讼
   ("听证", "audición"): "audiencia",      # audición=听力/试听；听证会=audiencia
   ("诉讼程序", "procedimiento de la fiscalía"): "procedimiento judicial",  # 检察院≠诉讼程序
   ("推诿", "subterfugio"): "excusa",      # subterfugio=诡计/托辞；推诿=excusa
   ("贿赂", "corrupto"): "soborno",        # corrupto=腐败的(形容词)；贿赂=soborno
   ("未实现", "no realizado"): "no consumado",  # 未遂（犯罪）=no consumado
   ("违约", "romper un contrato"): "incumplimiento de un contrato",  # 违约是名词
 },
 "pos": {
   # ---- Sec1（tribunal 阳性；文案未标词性的短语留空）
   ("法院", "tribunal"): "n.m.",
   ("原告", "demandante"): "n.m.",        # un/una demandante，文案只标 n.
   ("刑事法庭", "tribunal penal"): "",
   ("高级法院", "tribunal superior"): "",
   ("仲裁法庭", "tribunal de arbitraje"): "",
   ("少年法庭", "tribunal de menores"): "",
   ("军事法庭", "consejo de guerra"): "",
   # ---- Sec2
   ("死刑", "pena de muerte"): "",
   ("缓期执行", "suspensión de ejecución"): "",
   ("缓刑", "suspensión de la condena"): "",
   ("惯犯", "criminal habitual"): "n.m.",
   ("正当防卫", "la defensa propia"): "",
   # ---- Sec3
   ("诉讼程序", "procedimiento judicial"): "",
   ("被告席", "banco del acusado"): "",
   ("误判", "error de juicio"): "",
   ("未实现", "no consumado"): "",
   ("不法行为", "práctica ilícita"): "",
   ("违约", "incumplimiento de un contrato"): "",
   ("缓期执行", "suspensión de ejecución"): "",
   ("案件", "caso judicial"): "n.m.",       # caso 阳性
 },
 "subs": [
   # Sec1 例6：justificar te 被 OCR 拆开，反身代词须合写
   ("No puedo justificar te", "No puedo justificarte"),
   # Sec1 例7：damandado -> demandado（i/e 混淆）
   ("El damandado insultó al demandante", "El demandado insultó al demandante"),
   # Sec2 例4：主谓不一致——sacrificios 是复数，había 应为 habían
   ("los sacrificios que nos había costado", "los sacrificios que nos habían costado"),
   # Sec2 例5：补出请求语气
   ("Ben reduce el veredicto de Juliet",
    "Ben, reduce el veredicto de Juliet"),
 ],
 "zh_subs": [
   # Sec3 例6：西语是「他说自己无罪」，中文却写成「对自己的罪行供认不讳」，意思完全相反
   ("被逮捕者对自己的罪行供认不讳。",
    "被捕者坦率地说自己是无罪的。"),
   # Sec1 例5：voseo（consultás）用「你」不够礼貌，西语语境是「您」
   ("你为什么不找一个律师咨询？", "您为什么不找一位律师咨询一下？"),
   # Sec2 例5：中文「本减轻了」把 Ben 当姓氏，实为主语人名
   ("本减轻了朱丽叶的判决。", "本，请减轻对朱丽叶的判决。"),
   # Sec3 例1：testigo de la acusación=控方证人，中文误作「被告证人」（方向相反）
   ("法官要求被告证人出庭。", "法官要求控方证人出庭。"),
 ],
 "CN_FIX": {
   # Sec1 词汇：justificar=为…辩解/证明…正当，不是「证实」
   "证实": "证明…有理由",
 },
}

CFG = {16: G16, 17: G17, 19: G19, 20: G20, 21: G21, 22: G22, 23: G23, 24: G24, 25: G25, 26: G26, 27: G27, 28: G28, 29: G29, 30: G30, 31: G31, 32: G32, 33: G33, 34: G34, 35: G35, 36: G36, 37: G37, 38: G38, 39: G39, 40: G40}

if __name__ == "__main__":
    gid = int(sys.argv[1])
    cfg = CFG[gid]
    b = Builder(gid, cfg["name"], cfg["raw"],
                ES_FIX=cfg.get("fix"), ES_TYPO=cfg.get("typo"),
                S_SUBS=cfg.get("subs"), POS_FIX=cfg.get("pos"),
                S_ZH_SUBS=cfg.get("zh_subs"), CN_FIX=cfg.get("CN_FIX"))
    b.run()
