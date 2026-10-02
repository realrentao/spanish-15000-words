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

CFG = {16: G16, 17: G17}

if __name__ == "__main__":
    gid = int(sys.argv[1])
    cfg = CFG[gid]
    b = Builder(gid, cfg["name"], cfg["raw"],
                ES_FIX=cfg.get("fix"), ES_TYPO=cfg.get("typo"),
                S_SUBS=cfg.get("subs"), POS_FIX=cfg.get("pos"))
    b.run()
