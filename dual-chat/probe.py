#!/usr/bin/env python3
"""探测 DeepSeek + 豆包 的 DOM 选择器（静态，不发消息）。
连 CDP，对两个站点的页面 dump 输入框/contenteditable/可见按钮，
据此选出稳定的发送选择器。"""
import json
from playwright.sync_api import sync_playwright

PROBE_JS = r"""
() => {
  const vis = e => !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length);
  const pick = e => ({
    tag: e.tagName,
    type: e.getAttribute('type'),
    role: e.getAttribute('role'),
    aria: e.getAttribute('aria-label'),
    ph: e.placeholder || null,
    txt: (e.innerText || '').trim().slice(0, 24),
    cls: (e.className && e.className.toString) ? e.className.toString().slice(0, 70) : null,
    testid: e.getAttribute('data-testid') || e.getAttribute('data-test-id'),
    ced: e.getAttribute('contenteditable'),
    vis: vis(e),
    dis: !!e.disabled
  });
  return {
    url: location.href,
    title: document.title,
    textareas: [...document.querySelectorAll('textarea')].map(pick),
    contenteditable: [...document.querySelectorAll('[contenteditable]')].map(pick),
    buttons: [...document.querySelectorAll('button')].filter(b => vis(b)).map(pick)
  };
}
"""

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        for page in ctx.pages:
            if not any(k in page.url for k in ("deepseek", "doubao")):
                continue
            try:
                page.wait_for_load_state("domcontentloaded", timeout=5000)
            except Exception:
                pass
            data = page.evaluate(PROBE_JS)
            print("=" * 72)
            print(f"SITE : {data['url']}")
            print(f"TITLE: {data['title']}")
            print(f"\n[TEXTAREAS] ({len(data['textareas'])})")
            for t in data['textareas']:
                print("  ", json.dumps(t, ensure_ascii=False))
            print(f"\n[CONTENTEDITABLE] ({len(data['contenteditable'])})")
            for t in data['contenteditable']:
                print("  ", json.dumps(t, ensure_ascii=False))
            print(f"\n[BUTTONS visible] ({len(data['buttons'])})")
            for b in data['buttons']:
                print("  ", json.dumps(b, ensure_ascii=False))
            print()

if __name__ == "__main__":
    main()
