#!/usr/bin/env python3
"""probe3: 发'介绍猫'，定位回复容器（含'猫'的最具体元素），区分用户/AI 消息。"""
import time
from playwright.sync_api import sync_playwright

TEST = "请用大约40个字介绍一下猫的习性"
KW = "猫"
INPUT_SEL = {"deepseek": 'textarea[placeholder*="发送消息"]',
             "doubao":   'textarea[placeholder*="发消息"]'}

DUMP_JS = r"""
(kw)=>{
 const out=[];
 document.querySelectorAll('div,article,section,p').forEach(e=>{
   const t=(e.innerText||'').trim();
   if(t.includes(kw)&&t.length>8){
     let el=e,path=[];
     while(el&&el.nodeType===1&&path.length<6){let s=el.tagName.toLowerCase();let c=el.className;if(c&&c.toString){let f=c.toString().split(/\s+/)[0];if(f)s+='.'+f;}path.unshift(s);el=el.parentElement;}
     let childSum=0;for(const ch of e.children)childSum+=(ch.innerText||'').length;
     out.push({len:t.length,childSum,path:path.join('>'),head:t.replace(/\n/g,' ').slice(0,28)});
   }
 });
 out.sort((a,b)=>a.len-b.len);
 return out.slice(0,10);
}
"""

with sync_playwright() as p:
    br = p.chromium.connect_over_cdp("http://localhost:9222")
    pages = {}
    for pg in br.contexts[0].pages:
        for k in INPUT_SEL:
            if k in pg.url: pages[k] = pg
    for SITE in ["deepseek", "doubao"]:
        page = pages.get(SITE)
        if not page: print(f"[{SITE}] no page"); continue
        print("=" * 70)
        print(f"[{SITE}] {page.url}")
        inp = page.locator(INPUT_SEL[SITE]).first
        inp.wait_for(state="visible", timeout=5000)
        inp.fill(TEST); time.sleep(0.4); page.keyboard.press("Enter")
        print(f"[{SITE}] sent, waiting stream...")
        t0 = time.time(); last = ""; stable = 0
        while time.time() - t0 < 25:
            time.sleep(1); cur = page.inner_text("body")
            if cur != last: stable = 0; last = cur
            else: stable += 1
            if stable >= 3: break
        print(f"[{SITE}] stream done {round(time.time()-t0,1)}s")
        cands = page.evaluate(DUMP_JS, KW)
        print(f"[{SITE}] 含'{KW}'最具体容器 (len升序; childSum<<len=叶子文本):")
        for c in cands:
            print(f"    len={c['len']:4d} childSum={c['childSum']:4d}  head={c['head']!r}")
            print(f"        {c['path']}")
