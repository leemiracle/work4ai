#!/usr/bin/env python3
"""动态探测：发一条测试消息，验证 Enter 发送 + 抓回复容器 + 流式结束信号 + completion URL。
用法: python3 probe2.py deepseek | doubao"""
import sys, time, json, re
from playwright.sync_api import sync_playwright

SITE = sys.argv[1] if len(sys.argv) > 1 else "deepseek"
TEST = "请只回复两个字：收到"
INPUT_SEL = {
    "deepseek": 'textarea[placeholder*="发送消息"]',
    "doubao":   'textarea[placeholder*="发消息"]',
}[SITE]

RES_JS = r"""()=>performance.getEntriesByType('resource').map(r=>r.name)"""
# 抓候选回复容器（含 markdown/message/answer 等特征的元素）
DUMP_JS = r"""
()=>{const out=[];
 for(const e of document.querySelectorAll('[class*="markdown"],[class*="message"],[class*="answer"],[class*="receive"],[class*="content"],[class*="bubble"],[class*="flow"],[class*="rich"]')){
   const t=(e.innerText||'').trim();
   if(t.length>15){
     // 生成简易 css 路径
     let el=e,path=[];
     while(el&&el.nodeType===1&&path.length<5){let s=el.tagName.toLowerCase();let c=el.className;if(c&&c.toString){let first=c.toString().split(/\s+/)[0];if(first)s+='.'+first;}path.unshift(s);el=el.parentElement;}
     out.push({cls:(e.className&&e.className.toString)?e.className.toString().slice(0,70):'',len:t.length,head:t.slice(0,40),path:path.join('>')});
   }
 }
 return out.slice(-12);
}"""

def main():
    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp("http://localhost:9222")
        page = next((pg for pg in br.contexts[0].pages if SITE in pg.url), None)
        if not page:
            print(f"[{SITE}] 找不到页面"); sys.exit(1)
        print(f"[{SITE}] URL: {page.url}")
        inp = page.locator(INPUT_SEL).first
        inp.wait_for(state="visible", timeout=5000)
        print(f"[{SITE}] 输入框定位 OK")
        res_before = set(page.evaluate(RES_JS))
        body_before = len(page.inner_text("body"))
        inp.fill(TEST)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        print(f"[{SITE}] 已 Enter 发送: {TEST!r}")
        t0 = time.time(); last_len = body_before; stable = 0; grew = False
        while time.time() - t0 < 28:
            time.sleep(1)
            cur = len(page.inner_text("body"))
            if cur > last_len + 3:
                stable = 0; last_len = cur; grew = True
            else:
                stable += 1
            if grew and stable >= 3:
                break
        elapsed = round(time.time() - t0, 1)
        print(f"[{SITE}] 流式结束 耗时={elapsed}s body增长={grew} (before={body_before} after={last_len})")
        if not grew:
            print(f"[{SITE}] ⚠ Enter 似乎没触发发送！需要改用发送按钮。")
        # completion 网络请求
        res_after = set(page.evaluate(RES_JS))
        PAT = re.compile(r'completion|/chat/|message|stream|sse|talk|generat|conversation', re.I)
        new_res = sorted(r for r in (res_after - res_before) if PAT.search(r))
        print(f"[{SITE}] 候选 completion 请求 ({len(new_res)}):")
        for r in new_res[:6]:
            print(f"    {r[:130]}")
        # 候选回复容器
        cands = page.evaluate(DUMP_JS)
        print(f"[{SITE}] 候选回复容器 (最后{len(cands)}个):")
        for c in cands:
            print(f"    len={c['len']:4d} head={c['head']!r}")
            print(f"        cls={c['cls']}")
            print(f"        path={c['path']}")

if __name__ == "__main__":
    main()
