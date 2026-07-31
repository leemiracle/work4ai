#!/usr/bin/env python3
"""diag_doubao: 精确诊断豆包 type→Enter→回复 链路。"""
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    br = p.chromium.connect_over_cdp("http://localhost:9222")
    db = next(pg for pg in br.contexts[0].pages if "doubao" in pg.url)
    print("→ 新对话", flush=True)
    db.goto("https://www.doubao.com/chat", wait_until="domcontentloaded")
    loc = db.locator('textarea[placeholder*="发消息"]').first
    loc.wait_for(state="visible", timeout=15000)
    time.sleep(2)
    loc.click()
    msg = "你好，这是一个测试问题，请只回复两个字：收到"
    print(f"→ type: {msg}", flush=True)
    db.keyboard.type(msg, delay=55)
    time.sleep(0.6)
    val = loc.input_value()
    print(f"→ 输入框 value 长度={len(val)} 内容={val[:30]!r}", flush=True)
    n_before = db.eval_on_selector_all("[data-observe-row]", "els=>els.length")
    print(f"→ 发送前 rows={n_before}", flush=True)
    db.keyboard.press("Enter")
    print("→ 已 Enter，轮询 18s：", flush=True)
    for k in range(18):
        time.sleep(1)
        n = db.eval_on_selector_all("[data-observe-row]", "els=>els.length")
        info = db.evaluate(
            "()=>{const e=document.querySelectorAll('[data-observe-row]');"
            "if(!e.length)return 'none';"
            "const last=e[e.length-1];"
            "return 'rows='+e.length+' last='+JSON.stringify((last.innerText||'').trim().slice(0,40));}")
        print(f"  t={k+1:2d}s  {info}", flush=True)
