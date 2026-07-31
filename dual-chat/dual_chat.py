#!/usr/bin/env python3
"""dual_chat.py — DeepSeek(初学者提问) ↔ 豆包(专家回答) 自动多轮对话。
通过 CDP 连接已登录的 chromium，操作两个聊天页面。
用法: python3 dual_chat.py [--rounds N] [--seed "..."]
前提: chromium 已用 --remote-debugging-port=9222 启动，两个站点已登录。
关键设计:
  - 输入用 keyboard.type（逐字触发原生 input，React state 可靠更新；fill 会失效）
  - 所有 prompt 单行无 \\n（避免 type 把 \\n 当 Enter 提前发送）
  - DeepSeek 流式结束: count 增加 + .ds-assistant-message-main-content 稳定
  - 豆包流式结束: data-observe-row uuid 记录法 + 新增 AI 项 .md-box-root 稳定"""
import argparse, random, re, sys, time, datetime, pathlib

from playwright.sync_api import sync_playwright

CDP = "http://localhost:9222"
DS_INPUT = 'textarea[placeholder*="发送消息"]'        # DeepSeek 输入框
DS_REPLY = ".ds-assistant-message-main-content"       # DeepSeek AI 回复容器(语义化,稳)
DB_INPUT = 'textarea[placeholder*="发消息"]'          # 豆包输入框
DB_ROW   = "[data-observe-row]"                       # 豆包每条消息项(唯一uuid)
DB_MD    = ".md-box-root"                             # 豆包 markdown 渲染根

# 角色设定 —— 全部单行无 \n
DS_FIRST = ("【角色设定】你是一个正从零开始、想成为 AI、AI Agent 专家的初学者。"
            "请直接提出你现在最该问的第一个、最具体的问题。"
            "要求：只输出问题本身，不要任何寒暄或前缀，30 字以内。")
DS_NEXT  = ("【角色设定】你是初学者。专家刚才的回答：「{ans}」。"
            "请消化后，提出你下一个最想弄懂、最具体的疑问。"
            "要求：只输出问题本身，不要寒暄，30 字以内。")
DB_ASK   = ("请作为 AI、AI Agent 领域的资深专家，简明回答下面这个初学者的具体问题"
            "（150 字内，抓重点，必要时举例，直接给答案不要客套）。问题：{q} 你的回答：")

OUTDIR = pathlib.Path(__file__).parent


def human_type(page, text):
    """人类化输入：逐字 + 随机抖动；强制把换行变空格，避免 type 把 \\n 当 Enter 提前发送。"""
    text = re.sub(r'[\r\n]+', ' ', text)
    page.keyboard.type(text, delay=random.randint(35, 95))
    time.sleep(random.uniform(0.4, 0.9))


def set_input(page, selector, text):
    """用原生 setter 设 textarea value + input 事件，绕过 keyboard 字符陷阱
    （豆包 type '/' 会触发斜杠命令菜单；type '\\n' 会触发 Enter 发送）。"""
    text = re.sub(r'[\r\n]+', ' ', text)
    page.eval_on_selector(selector, """(el, val) => {
        const s = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        s.call(el, val); el.focus();
        el.dispatchEvent(new Event('input', {bubbles:true}));
    }""", text)
    time.sleep(random.uniform(0.5, 1.0))


def wait_stable(get_text, stable_secs=3, max_wait=70, min_len=2):
    """轮询 get_text()，连续 stable_secs 秒不变且够长 => 流式结束。"""
    t0 = time.time(); prev = ""; stable = 0
    while time.time() - t0 < max_wait:
        time.sleep(1)
        try: cur = (get_text() or "").strip()
        except Exception: cur = ""
        if cur and cur == prev: stable += 1
        else: stable = 0; prev = cur
        if cur and len(cur) >= min_len and stable >= stable_secs: return cur
    return prev


def send_deepseek(page, prompt):
    """向 DeepSeek 发送 prompt，等流式结束，返回 AI 回复。"""
    loc = page.locator(DS_INPUT).first
    loc.wait_for(state="visible", timeout=10000)
    cnt = page.locator(DS_REPLY).count()                 # 发送前已有回复数
    loc.click()
    human_type(page, prompt)
    time.sleep(random.uniform(0.3, 0.7))
    page.keyboard.press("Enter")
    # 先等新回复元素出现(count 增加)，避免把旧回复误判为稳定
    t0 = time.time()
    while time.time() - t0 < 30 and page.locator(DS_REPLY).count() <= cnt:
        time.sleep(0.5)
    return wait_stable(lambda: page.locator(DS_REPLY).last.inner_text())


def send_doubao(page, prompt):
    """向豆包发送 prompt，uuid 记录法定位新增 AI 回复，等流式结束。带重试应对偶发发送失败。"""
    loc = page.locator(DB_INPUT).first
    loc.wait_for(state="visible", timeout=10000)
    ai_uuid = None
    for attempt in range(3):
        before = set(page.eval_on_selector_all(DB_ROW, "els=>els.map(e=>e.getAttribute('data-observe-row'))"))
        loc.click()
        human_type(page, prompt)
        time.sleep(random.uniform(0.4, 0.8))
        page.keyboard.press("Enter")
        # 等新增项出现
        t0 = time.time()
        while time.time() - t0 < 20:
            rows = page.eval_on_selector_all(DB_ROW, "els=>els.map(e=>({u:e.getAttribute('data-observe-row'),t:(e.innerText||'').trim()}))")
            if len([r for r in rows if r['u'] not in before]) >= 2:
                break
            time.sleep(1)
        time.sleep(3)                       # 让流式进行, AI 文本变长
        # 选文本最长的新项 = AI 回复(排除空 padding 和较短的用户消息)
        rows = page.eval_on_selector_all(DB_ROW, "els=>els.map(e=>({u:e.getAttribute('data-observe-row'),t:(e.innerText||'').trim()}))")
        new = sorted((r for r in rows if r['u'] not in before), key=lambda r: len(r['t']), reverse=True)
        ai_uuid = new[0]['u'] if new else None
        longest = len(new[0]['t']) if new else 0
        if ai_uuid and longest > 5:
            break
        time.sleep(3)
    if not ai_uuid:
        return "[豆包: 3次未获取到回复，可能风控，请稍后重试]"
    # 动态取"最长新项"文本(不锁 uuid，避免流式时项重挂载/uuid 失效)
    def get_longest_new():
        try:
            rows = page.eval_on_selector_all(DB_ROW, "els=>els.map(e=>{const m=e.querySelector('%s');return{u:e.getAttribute('data-observe-row'),t:m?(m.innerText||'').trim():''}})" % DB_MD)
            new = sorted((r for r in rows if r['u'] not in before and r['t']), key=lambda r: len(r['t']), reverse=True)
            return new[0]['t'] if new else ""
        except Exception:
            return ""
    return wait_stable(get_longest_new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--seed", default=None, help="跳过 DeepSeek 首问，直接用此问题问豆包")
    args = ap.parse_args()

    log = []
    def rec(role, txt):
        log.append((role, txt))
        print(f"\n{'='*64}\n[{role}]\n{txt}\n", flush=True)

    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp(CDP)
        ds = next((pg for pg in br.contexts[0].pages if "deepseek" in pg.url), None)
        db = next((pg for pg in br.contexts[0].pages if "doubao" in pg.url), None)
        if not ds or not db:
            print("找不到 DeepSeek/豆包 页面，确认两个标签都在且已登录。"); sys.exit(1)
        print(f"DeepSeek: {ds.url}\n豆包    : {db.url}\n轮数: {args.rounds}", flush=True)
        print("→ 开启新对话...", flush=True)
        ds.goto("https://chat.deepseek.com/", wait_until="domcontentloaded")
        db.goto("https://www.doubao.com/chat", wait_until="domcontentloaded")
        ds.locator(DS_INPUT).first.wait_for(state="visible", timeout=15000)
        db.locator(DB_INPUT).first.wait_for(state="visible", timeout=15000)
        time.sleep(2)

        prev_ans = None
        for i in range(args.rounds):
            print(f"\n{'#'*64}\n# 第 {i+1}/{args.rounds} 轮\n{'#'*64}", flush=True)
            if args.seed and i == 0:
                question = args.seed
                rec("🎓 DeepSeek(初学者·种子问题)", question)
            else:
                prompt = DS_FIRST if prev_ans is None else DS_NEXT.format(ans=prev_ans)
                question = send_deepseek(ds, prompt)
                question = re.sub(r'^好的[！!，,]?\s*', '', question.strip())
                rec("🎓 DeepSeek(初学者提问)", question)
            time.sleep(random.uniform(2, 4))
            answer = send_doubao(db, DB_ASK.format(q=question))
            rec("👨‍🏫 豆包(专家回答)", answer)
            prev_ans = answer
            time.sleep(random.uniform(2, 4))

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = OUTDIR / f"dialogue_{ts}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# DeepSeek(初学者) ↔ 豆包(专家) 对话  {ts}\n\n")
        for role, txt in log:
            f.write(f"## {role}\n\n{txt}\n\n---\n\n")
    print(f"\n✅ 对话已保存: {out}", flush=True)


if __name__ == "__main__":
    main()
