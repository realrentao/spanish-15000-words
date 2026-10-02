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

CFG = {16: G16, 17: G17, 19: G19, 20: G20, 21: G21, 22: G22, 23: G23, 24: G24, 25: G25, 26: G26, 27: G27, 28: G28, 29: G29}

if __name__ == "__main__":
    gid = int(sys.argv[1])
    cfg = CFG[gid]
    b = Builder(gid, cfg["name"], cfg["raw"],
                ES_FIX=cfg.get("fix"), ES_TYPO=cfg.get("typo"),
                S_SUBS=cfg.get("subs"), POS_FIX=cfg.get("pos"),
                S_ZH_SUBS=cfg.get("zh_subs"), CN_FIX=cfg.get("CN_FIX"))
    b.run()
