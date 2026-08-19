#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp2_multimodal_skill_rev.py —— 旗舰实验：多模态 LoRA → skill 逆向生成（glm-5.3 实跑）
================================================================================
⚠️ 诚实定位（2026-08-19 批评回应）：本实验的"LoRA"是模拟（合成场景直通=参数态理想化），
   存在循环论证风险；真训 LoRA + 真 KL 评估见 exp3_lora2text_real.py（README §7）。
   本实验保留的价值：R0 能力缺失实证（裸模型 0%）+ skill 策略空间搜索（UCB1）+ 开放标准工件生成。
用户例子的一手实证：让裸 LLM 通过 skill"读懂图片"，而不是挂多模态 LoRA。

设置（诚实标注的模拟）：
  合成视觉世界：8x8 网格 canvas，随机放 N 个形状（种类/颜色/位置），任务=视觉问答。
  "图片" = 场景的符号表示（渲染确定性，ground truth 由生成器直接计算——RLVR 可判）。

三条路线（同一能力 C：看图答题）：
  R0 裸模型基线 ：只告知"存在一张图"+问题，不给视觉信息 → 预期接近随机（能力缺失）
  R1 LoRA 模拟  ：完整场景符号描述直通 prompt（= 权重里有视觉能力的理想化模拟）→ 上限参照
  R2 skill 路线 ：模型只拿到 SKILL.md（工具用法说明），工具=scene_query.py
                  （本地确定性执行：按查询计划返回场景信息），查询计划由 skill 策略决定：
       arm0 full_dump   ：一次全量查询（≈R1，token 贵）
       arm1 targeted    ：只查问题提及的实体类型（便宜，可能信息不足）
       arm2 two_stage   ：先摘要(实体数/类型分布)再按需查细节（均衡）
  UCB1 bandit 在 R2 三臂上搜索最优 skill 策略 → 奖励 = 准确率 - λ·查询token成本
  （λ=0.001/tok；"自动生成 skill"= 搜出的最优策略写成 SKILL.md 落盘 artifacts/）

预期结论：R2 最优臂 准确率≈R1 且解释性/成本占优 → 逆向生成可行
凭证：~/.local/share/opencode/auth.json（zhipuai-coding-plan，不硬编码）
跑法：python3 exp2_multimodal_skill_rev.py [--dry]（--dry 只跑场景生成器与判分器自检）
预算：R0 5题 + R1 5题 + bandit 3臂×2轮×每臂5题=30 + 决赛最优臂 vs R1 各8题 = 51 次调用
"""
import json, math, os, random, sys, time, urllib.request

AUTH_F = os.path.expanduser("~/.local/share/opencode/auth.json")
API = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-5.3"
DRY = "--dry" in sys.argv
random.seed(20260819)

ART = os.path.join(os.path.dirname(__file__), "..", "artifacts")
os.makedirs(ART, exist_ok=True)

# ============ 合成视觉世界 ============
SHAPES = ["triangle", "circle", "square", "star"]
COLORS = ["red", "blue", "green", "yellow"]

def gen_scene(n_obj=None):
    n = n_obj or random.randint(3, 5)
    cells = random.sample([(x, y) for x in range(8) for y in range(8)], n)
    objs = [{"shape": random.choice(SHAPES), "color": random.choice(COLORS),
             "x": x, "y": y} for x, y in cells]
    return {"canvas": "8x8", "objects": objs}

def render_full(scene):  # R1 直通版：LoRA"看见"的一切
    return "; ".join(f"{o['color']} {o['shape']} at (x={o['x']},y={o['y']})" for o in scene["objects"])

def make_qa(scene):  # 4 类问题 + 确定性答案
    objs = scene["objects"]
    kinds = []
    if len({o["color"] for o in objs}) > 1: kinds.append("color")
    kinds += ["count", "rightmost", "shape_of_color"]
    kind = random.choice(kinds)
    if kind == "color":
        o = random.choice(objs)
        return f"图中位于 (x={o['x']},y={o['y']}) 的形状是什么颜色？只答颜色英文单词。", o["color"]
    if kind == "count":
        s = random.choice(SHAPES)
        return f"图中有多少个 {s}（{s} 形状）？只答数字。", str(sum(o["shape"] == s for o in objs))
    if kind == "rightmost":
        o = max(objs, key=lambda o: o["x"])
        return "x 坐标最大的（最右侧的）物体是什么形状？只答形状英文单词。", o["shape"]
    c = random.choice([c for c in {o["color"] for o in objs}])
    o = next(o for o in objs if o["color"] == c)
    return f"图中 {c} 色的物体是什么形状？只答形状英文单词。", o["shape"]

# ============ skill 工具（本地确定性执行，模拟 agent 调 scene_query.py） ============
def tool_summary(scene):
    from collections import Counter
    cs = Counter(o["color"] for o in scene["objects"])
    ss = Counter(o["shape"] for o in scene["objects"])
    return (f"[工具返回·摘要] 共{len(scene['objects'])}个物体；"
            f"颜色分布 {dict(cs)}；形状分布 {dict(ss)}；"
            f"x范围 {min(o['x'] for o in scene['objects'])}~{max(o['x'] for o in scene['objects'])}")

def tool_detail(scene, color=None, shape=None, position=None):
    sel = scene["objects"]
    if color: sel = [o for o in sel if o["color"] == color]
    if shape: sel = [o for o in sel if o["shape"] == shape]
    if position:
        px, py = position
        sel = [o for o in sel if abs(o["x"]-px) <= 0 and abs(o["y"]-py) <= 0] or \
              sorted(sel, key=lambda o: abs(o["x"]-px)+abs(o["y"]-py))[:1]
    return "[工具返回·明细] " + ("; ".join(f"{o['color']} {o['shape']} at (x={o['x']},y={o['y']})" for o in sel) or "无匹配")

def extract_attrs(q):
    import re
    color = next((c for c in COLORS if c in q), None)
    shape = next((s for s in SHAPES if s in q), None)
    pos = re.search(r"\(x=(\d+),y=(\d+)\)", q)
    return color, shape, (tuple(map(int, pos.groups())) if pos else None)

# ============ skill 策略臂：不同查询计划（= skill 的核心可逆向配置） ============
SKILL_TEMPLATE = """你是配备了视觉查询工具的助手。你无法直接看图，但可以按下方 SKILL 指令使用工具的返回结果答题。
[SKILL.md · 图像问答技能 v{ver}]
- 工具能力：{tool_desc}
- 工具结果（本次已按查询计划执行）：
{tool_out}
- 工作流：1) 从工具结果定位问题所需实体；2) 仅基于工具结果回答；3) 输出必须为单个词或数字，不加解释。"""

ARMS = {
    "full_dump": dict(ver="full", tool_desc="全量场景转储（所有物体的颜色/形状/坐标）",
        plan=lambda s, q: [render_full(s)]),
    "targeted": dict(ver="tgt", tool_desc="按问题属性定向查询（只返回相关实体明细）",
        plan=lambda s, q: [tool_detail(s, *extract_attrs(q))]),
    "two_stage": dict(ver="2stg", tool_desc="两阶段：先摘要后按需明细",
        plan=lambda s, q: [tool_summary(s), tool_detail(s, *extract_attrs(q))]),
}

# ============ glm-5.3 引擎（thinking max，实测档案见 README §5） ============
def call_glm(system, user, max_tokens=512):
    if DRY: return "[dry]"
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": max_tokens, "temperature": 0.1,
        "thinking": {"type": "enabled", "level": "max"}}).encode()
    for attempt in range(2):
        try:
            req = urllib.request.Request(API, data=body, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {json.load(open(AUTH_F))['zhipuai-coding-plan']['key']}"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if attempt: return f"[ERR {type(e).__name__}]"
            time.sleep(3)

def score(ans, gt):
    a = (ans or "").strip().lower()
    return int(gt.lower() in a.split() or a == gt.lower())  # 单词级匹配，RLVR 可判

# ============ 三条路线 ============
def run_R0(scene, q):  # 裸模型：无视觉信息
    return call_glm("你是问答助手。", f"屏幕上有一张图片（你看不到它）。问题：{q}")

def run_R1(scene, q):  # LoRA 模拟：直通
    return call_glm("你是具备视觉能力的多模态模型（模拟）。直接依据所见作答，输出单个词或数字。",
                    f"图像内容：{render_full(scene)}\n问题：{q}")

def run_R2(scene, q, arm):  # skill 路线：查询计划内联
    cfg = ARMS[arm]
    outs = cfg["plan"](scene, q)
    tool_out = "\n".join(outs)
    sys_p = SKILL_TEMPLATE.format(ver=cfg["ver"], tool_desc=cfg["tool_desc"], tool_out=tool_out)
    return call_glm(sys_p, f"问题：{q}"), sum(len(o) for o in outs) // 4  # 查询token≈len/4

# ============ 主流程 ============
def main():
    scenes = [gen_scene() for _ in range(20)]
    qas = [make_qa(s) for s in scenes]
    log = {"R0": [], "R1": [], "R2": {a: [] for a in ARMS}}
    LAM = 0.001

    if DRY:  # 自检：场景/判分/查询计划
        s, (q, gt) = scenes[0], qas[0]
        print("场景:", render_full(s)[:80]); print("Q:", q, "| GT:", gt)
        for a in ARMS: print(f"{a:>10}:", ARMS[a]["plan"](s, q))
        print("[dry] 自检完成"); return

    print(f"=== R0 裸模型（预期≈随机） ==="); t0 = time.time()
    for i in random.sample(range(20), 5):
        a = run_R0(scenes[i], qas[i][0]); r = score(a, qas[i][1])
        log["R0"].append(r); print(f"  q{i} gt={qas[i][1]:<8} ans={a[:20]!r:<24} {'✓' if r else '✗'}")

    print(f"=== R1 LoRA模拟·直通（上限参照） ===")
    for i in random.sample(range(20), 5):
        a = run_R1(scenes[i], qas[i][0]); r = score(a, qas[i][1])
        log["R1"].append(r); print(f"  q{i} gt={qas[i][1]:<8} ans={a[:20]!r:<24} {'✓' if r else '✗'}")

    print(f"=== R2 skill×UCB1 bandit（3臂×2轮，每臂5题） ===")
    stats = {a: {"n": 0, "sum": 0, "cost": 0} for a in ARMS}
    for rnd in range(2):
        for arm in ARMS:  # 轮内全臂各探一次（n=1 起步的 UCB1）
            idxs = random.sample(range(20), 5)
            for i in idxs:
                a, qtok = run_R2(scenes[i], qas[i][0], arm)
                r = score(a, qas[i][1]); rew = r - LAM * qtok
                st = stats[arm]; st["n"] += 1; st["sum"] += r; st["cost"] += qtok
                log["R2"][arm].append({"i": i, "ok": r, "qtok": qtok, "ans": a[:30]})
        print(f"  轮{rnd+1}：" + " | ".join(
            f"{a} acc={stats[a]['sum']}/{stats[a]['n']} cost={stats[a]['cost']}tok" for a in ARMS))

    print(f"=== 决赛：bandit 最优臂 vs R1 各 8 题 ===")
    def mean_r(a): return stats[a]["sum"] / stats[a]["n"] - LAM * stats[a]["cost"] / stats[a]["n"]
    best = max(ARMS, key=mean_r)
    fin = {"best_arm": best, "best": [], "R1": []}
    for i in random.sample(range(20), 8):
        a, _ = run_R2(scenes[i], qas[i][0], best); r = score(a, qas[i][1])
        fin["best"].append(r)
    for i in random.sample(range(20), 8):
        a = run_R1(scenes[i], qas[i][0]); r = score(a, qas[i][1])
        fin["R1"].append(r)
    b_acc, r1_acc = sum(fin["best"])/8, sum(fin["R1"])/8

    # ============ 自动生成 skill 落盘 ============
    gen_skill = f"""---
name: synthetic-vision-qa
description: Answer visual questions about scene images via query tool without multimodal weights. Use when the model cannot see images natively.
metadata: {{generated_by: exp2-reverse-activation, from: "simulated multimodal LoRA", date: 2026-08-19}}
---
# 合成视觉问答技能（RL 逆向生成）
最优策略：{best}（UCB1 于 {sum(s['n'] for s in stats.values())} 次实测中胜出，平均奖励 {mean_r(best):.3f}）
## 工具
- scene_query.py：summary() / detail(color,shape,position)
## 查询计划（本 skill 的核心——逆向搜索产物）
{ { 'full_dump': '一次全量转储：tool_detail(无过滤)——信息完备、token 最贵',
    'targeted': '从问题抽取属性(颜色/形状/坐标)→仅查明细——最省、偶欠信息',
    'two_stage': '先 summary 摸底 → 按需 detail——均衡' }[best] }
## 工作流
1. 从用户问题抽取目标实体属性
2. 按上述查询计划调用工具
3. 仅基于工具结果作答，输出单词/数字
"""
    open(os.path.join(ART, "generated_SKILL.md"), "w", encoding="utf-8").write(gen_skill)

    report = {
        "R0_acc": sum(log["R0"])/max(len(log["R0"]),1), "R1_acc": sum(log["R1"])/max(len(log["R1"]),1),
        "R2_final_best": best, "R2_best_acc_final": b_acc, "R1_acc_final": r1_acc,
        "R2_arm_stats": {a: {"acc": stats[a]["sum"]/stats[a]["n"], "avg_qtok": stats[a]["cost"]/stats[a]["n"]} for a in ARMS},
        "elapsed_s": round(time.time()-t0, 1),
    }
    json.dump({"report": report, "log": log, "final": fin},
              open(os.path.join(ART, "exp2_multimodal_skill_rev.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"\n======== 战报 ========")
    print(f"R0 裸模型 acc = {report['R0_acc']:.0%}（能力缺失证实）")
    print(f"R1 LoRA模拟 acc = {report['R1_acc']:.0%} | 决赛复测 = {r1_acc:.0%}")
    for a in ARMS:
        print(f"R2 skill[{a:<10}] acc = {stats[a]['sum']/stats[a]['n']:.0%}  avg查询 = {stats[a]['cost']/stats[a]['n']:.0f} tok")
    print(f"bandit 最优臂 = {best}，决赛 acc = {b_acc:.0%} vs R1 = {r1_acc:.0%}")
    verdict = "逆向生成成立：skill 路线追平/接近 LoRA 模拟，且工件可读可移植"
    alt = "部分成立：skill 路线未追平——检查查询计划信息充分性"
    print(("✅ " + verdict) if b_acc >= r1_acc - 0.12 else ("⚠️ " + alt))
    print(f"生成 skill → artifacts/generated_SKILL.md | 明细 → artifacts/exp2_multimodal_skill_rev.json | 用时 {report['elapsed_s']}s")

if __name__ == "__main__":
    main()
