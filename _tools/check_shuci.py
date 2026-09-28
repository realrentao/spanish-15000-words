# -*- coding: utf-8 -*-
import sys
from playwright.sync import sync_playwright

URL = "http://127.0.0.1:8822/"
errs = []

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1100, "height": 1000})
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERR " + str(e)))
    pg.goto(URL, wait_until="networkidle")
    pg.wait_for_timeout(800)

    res = pg.evaluate("""() => {
        // 进入「数词（1）」 (grupo0 / parte0 / sec3)
        const items=[...document.querySelectorAll('.sec-item')];
        const t=items.find(e=>e.textContent.includes('数词（1）'));
        if(!t) return {err:'no sec-item'};
        // 确保所属 grupo 展开
        try { t.closest('.grupo').querySelector('.grupo-hd').click(); } catch(e){}
        t.click();
        return {ok:true};
    }""")
    pg.wait_for_timeout(1000)

    info = pg.evaluate("""() => {
        const rows=document.querySelectorAll('.row').length;
        const sents=document.querySelectorAll('.sent').length;
        const tags=[...document.querySelectorAll('.block-hd .tag')].map(e=>e.textContent);
        const firstEs=document.querySelector('.row .es');
        const firstIpa=document.querySelector('.row .ipa');
        const firstZh=document.querySelector('.row .zh');
        // audio src reachability
        const spk=document.querySelector('.spk');
        const a=spk && spk.getAttribute('data-a');
        return {rows, sents, tags,
                firstEs:firstEs&&firstEs.textContent,
                firstIpa:firstIpa&&firstIpa.textContent,
                firstZh:firstZh&&firstZh.textContent,
                spkAudio:a};
    }""")
    print("nav:", res)
    print("info:", info)

    # 尝试播放第一个音频，捕获错误
    play_err=[]
    def on_err(m):
        if m.type=="error": play_err.append(m.text)
    pg.on("console", on_err)
    pg.evaluate("""() => { const s=document.querySelector('.spk'); if(s) s.click(); }""")
    pg.wait_for_timeout(1500)

    print("console errors:", errs)
    pg.screenshot(path="/tmp/shuci.png", full_page=False)
    b.close()
