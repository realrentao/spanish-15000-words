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

CFG = {16: G16, 17: G17, 19: G19, 20: G20}

if __name__ == "__main__":
    gid = int(sys.argv[1])
    cfg = CFG[gid]
    b = Builder(gid, cfg["name"], cfg["raw"],
                ES_FIX=cfg.get("fix"), ES_TYPO=cfg.get("typo"),
                S_SUBS=cfg.get("subs"), POS_FIX=cfg.get("pos"),
                S_ZH_SUBS=cfg.get("zh_subs"))
    b.run()
