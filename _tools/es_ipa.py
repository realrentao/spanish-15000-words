# -*- coding: utf-8 -*-
"""西语文本 -> 规则化 IPA（与站内既有 6063 条音标风格一致）。

规则要点（由站内已有数据反推）：
- 每个 a/e/i/o/u 都是一个音节核（naive 切分，不合并二重元音）；y 变来的 i 不算核
- 重音：有重音符 -> 该元音；单词仅一个音节 -> 不标；词尾为 n/s/元音 -> 倒数第二音节；否则末音节
- ˈ 插在重读元音之前
- Castilian：c(e/i)/z -> θ，g(e/i)/j -> x，ll -> ʎ，ñ -> ɲ，ch -> tʃ，rr -> r，h 不发音
- b/v、d、g 在非词首/非鼻音后弱化；n 在硬 g 前 -> ŋ
- 硬 g 连字：gu + e/i 永远发硬 ɡ（跳过 u）；gü + e/i -> ɡ/w + 词中 e/i 为核
- 词尾 que/gue 的 e/i 不另起音节（并入前一音节，无重音）
"""
import re

ACC = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u"}
VOWELS = "aeiou"
NASAL = ("m", "n", "ŋ")


def _base(c):
    return ACC.get(c, c)


def word_ipa(w):
    w = w.strip().lower()
    if not w:
        return ""
    ls = [c for c in w if c.isalpha() or c in ACC]
    if not ls:
        return ""

    ph = []  # [(phoneme, is_nucleus)]
    stress_idx = None

    def prev():
        return ph[-1][0] if ph else None

    def emit(p, isv=False):
        ph.append((p, isv))

    i = 0
    n = len(ls)
    while i < n:
        c = ls[i]
        b = _base(c)
        nxtraw = ls[i + 1] if i + 1 < n else ""
        nxt = _base(nxtraw)
        nxt2 = _base(ls[i + 2]) if i + 2 < n else ""

        # 二合字母 / 连字
        if b == "c" and nxt == "h":
            emit("tʃ"); i += 2; continue
        if b == "l" and nxt == "l":
            emit("ʎ"); i += 2; continue
        if b == "r" and nxt == "r":
            emit("r"); i += 2; continue
        if b == "q" and nxt == "u":
            emit("k"); i += 2                       # 跳过 q,u，落在 e/i 上
            if i < n and ls[i] in "ei":
                last = (i == n - 1)                 # 词尾 que -> e 不另起音节
                emit(_base(ls[i]), isv=not last); i += 1
            continue
        if b == "g" and nxt == "u" and nxt2 in "ei":
            emit("ɡ")                               # 硬 g 连字，永远硬 ɡ
            i += 2
            if i < n and ls[i] in "ei":
                last = (i == n - 1)
                emit(_base(ls[i]), isv=not last); i += 1
            continue
        if b == "g" and nxtraw == "ü" and nxt2 in "ei":
            g = "ɡ" if (prev() is None or prev() in NASAL) else "ɣ"
            emit(g); emit("w"); i += 2
            emit(_base(ls[i]), isv=True); i += 1; continue
        if b == "h":
            i += 1; continue

        # 单字母
        if c in "áéíóú":
            stress_idx = len(ph)
            emit(ACC[c], isv=True); i += 1; continue
        if b in VOWELS:
            emit(b, isv=True); i += 1; continue
        if b == "ü":
            emit("w"); i += 1; continue
        if b == "y":
            emit("ʝ" if i == 0 else "i", isv=False); i += 1; continue
        if b in ("b", "v"):
            emit("b" if (prev() is None or prev() in NASAL) else "β"); i += 1; continue
        if b == "d":
            emit("d" if (prev() is None or prev() in ("n", "l", "ŋ")) else "ð"); i += 1; continue
        if b == "g":
            if nxt in "ei":
                emit("x")
            else:
                emit("ɡ" if (prev() is None or prev() in NASAL) else "ɣ")
            i += 1; continue
        if b == "j":
            emit("x"); i += 1; continue
        if b == "c":
            emit("θ" if nxt in "ei" else "k"); i += 1; continue
        if b == "z":
            emit("θ"); i += 1; continue
        if b == "ñ":
            emit("ɲ"); i += 1; continue
        if b == "r":
            emit("r" if (prev() is None or prev() in ("l", "n", "s", "ŋ")) else "ɾ"); i += 1; continue
        if b == "n":
            hard = (nxt == "g" and nxt2 not in "ei") or (nxt == "g" and nxt2 == "u") \
                or (nxt == "g" and nxt2 == "ü")
            emit("ŋ" if hard else "n"); i += 1; continue
        if b == "x":
            emit("k"); emit("s"); i += 1; continue
        # 其余（k, w, l, m, p, s, f, t 等）
        emit(b); i += 1

    if not ph:
        return ""

    nuclei = [k for k, (p, isv) in enumerate(ph) if isv]
    if len(nuclei) <= 1:
        return "".join(p for p, _ in ph)

    # 重音定位
    if stress_idx is not None:
        target = stress_idx
    else:
        last_char = ls[-1]
        if last_char in "ns" or last_char in VOWELS or last_char == "y":
            target = nuclei[-2]
        else:
            target = nuclei[-1]

    out = []
    for k, (p, _) in enumerate(ph):
        if k == target:
            out.append("ˈ")
        out.append(p)
    return "".join(out)


WORD_RE = re.compile(r"[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]+")


def text_ipa(text):
    parts = []
    for w in WORD_RE.findall(text.lower()):
        s = word_ipa(w)
        if s:
            parts.append(s)
    return " ".join(parts)


if __name__ == "__main__":
    for t in ["semana", "Estás muy ocupado esta semana.", "jersey", "ley", "agua",
              "residencia", "guerra", "seguir", "guisar", "toque", "bosque", "parque",
              "hamburguesa", "antigüedad", "tuxedo", "outfit", "vintage", "blazer",
              "leggings", "jeans", "cool", "shopping", "look", "show", "baguette",
              "burguesía", "arqueología", "despegue", "hoguera", "guante"]:
        print(t.ljust(14), "->", text_ipa(t))
