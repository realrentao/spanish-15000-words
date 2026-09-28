# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8821/"

with sync_playwright() as p:
    try:
        b = p.chromium.launch(channel="msedge", headless=True)
    except Exception:
        b = p.chromium.launch(headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERR: " + str(e)))
    pg.goto(URL, wait_until="networkidle")
    pg.wait_for_timeout(800)
    # 找到第九篇并点击进入小节
    toc = pg.inner_text("#toc")
    has9 = "时尚热词" in toc
    print("目录含第九篇:", has9)
    # 点击第九篇的 sec-item
    # 展开第九篇 grupo
    for hd in pg.query_selector_all(".grupo-hd"):
        if "时尚热词" in (hd.inner_text() or ""):
            hd.click()
            break
    pg.wait_for_timeout(500)
    clicked = False
    for s in pg.query_selector_all(".sec-item"):
        if "时尚热词" in (s.inner_text() or ""):
            s.scroll_into_view_if_needed()
            s.click()
            clicked = True
            break
    pg.wait_for_timeout(800)
    h1 = pg.inner_text(".sec-title") if pg.query_selector(".sec-title") else "(无)"
    wcount = len(pg.query_selector_all(".w-card")) if pg.query_selector(".w-card") else 0
    print("点击第九篇成功:", clicked)
    print("小节标题:", h1)
    print("控制台错误数:", len(errs))
    for e in errs[:10]:
        print("  ERR:", e)
    b.close()
