#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2 零样本 vs 少样本：k 曲线 + 随机标签消融（指南 techniques/zeroshot+fewshot 的实证）
================================================================================
问题1：加示例到底涨多少？涨到几个够了？（k=0/1/2/4/8）
问题2：Min et al. 2022 (arXiv:2202.12837) 声称"随机标签的示例也有效，格式比正确性重要"——真的吗？
设计：
  任务：中文情感二分类（正面/负面），20 条测试句（10正10负，含3条难例）
  条件：k ∈ {0,1,2,4,8} 正确标签示例；k=4 随机标签（打乱后2正2负标签对调）
  模型：本地 Qwen2.5-0.5B + glm-4-flash（对照：小模型是否更需要 few-shot）
产出：results/e2_fewshot.json + e2_fewshot.png
"""
from common import local_qwen, glm, save
import re, time

# 示例池（不与测试集重叠）
EXEMPLARS = [
    ("这家餐厅的菜品让人惊喜，服务也周到。", "正面"),
    ("快递太慢了，包装还破损。", "负面"),
    ("电影节奏紧凑，看完意犹未尽。", "正面"),
    ("界面难用，广告还多。", "负面"),
    ("客服很耐心，问题一次解决。", "正面"),
    ("质量差，一周就坏了。", "负面"),
    ("性价比很高，回购第三次。", "正面"),
    ("内容空洞，浪费时间。", "负面"),
]
# 测试集：10正10负（末尾3条为难例：否定前缀/反讽/中性偏移）
TEST = [
    ("孩子看完笑个不停，强烈推荐。", "正面"), ("物流破损，客服踢皮球。", "负面"),
    ("音质超出预期，做工精细。", "正面"), ("用了两天就闪屏，失望。", "负面"),
    ("剧情扎实，演员演技在线。", "正面"), ("全是套话，毫无新意。", "负面"),
    ("安装简单，静音效果好。", "正面"), ("尺寸不符，退货还扣运费。", "负面"),
    ("这次体验不难受，反而挺舒心。", "正面"), ("没有想象中难用，但也没惊喜。", "正面"),
    ("我不是说它好，是说它非常好。", "正面"), ("信号谈不上稳定，偶尔断连。", "负面"),
    ("说明书缺失，组装凭感觉。", "负面"), ("包装用心，还送了小礼物。", "正面"),
    ("降价太快，早买的成了冤种。", "负面"), ("细节到位，看得出用了心。", "正面"),
    ("噪音大得像拖拉机。", "负面"), ("朋友聚会首选，气氛拉满。", "正面"),
    ("续航虚标，实测打七折。", "负面"), ("响应迅速，功能恰到好处。", "正面"),
]

def build_prompt(k, random_labels=False):
    exs = EXEMPLARS[:k] if k > 0 else []
    if random_labels:
        exs = [(s, ("负面" if l == "正面" else "正面")) for s, l in exs]
    parts = ["请判断下面句子的情感倾向。"] if k == 0 else []
    for s, l in exs:
        parts.append(f"句子：{s}\n情感：{l}")
    parts.append("句子：{Q}\n情感：")
    return "\n\n".join(parts)

def parse(out):
    m = re.search(r"(正面|负面)", out)
    return m.group(1) if m else ("正面" if "正" in out[:6] else "负面" if "负" in out[:6] else None)

def eval_local(k, random_labels=False):
    correct = 0; details = []
    for q, gold in TEST:
        out = local_qwen(build_prompt(k, random_labels).replace("{Q}", q),
                         max_new_tokens=4, temperature=0.0)
        pred = parse(out)
        correct += (pred == gold)
        details.append((q[:10], gold, pred))
    return correct / len(TEST), details

def eval_glm(k, random_labels=False):
    correct = 0; details = []
    for q, gold in TEST:
        r = glm("glm-4-flash", build_prompt(k, random_labels).replace("{Q}", q),
                max_tokens=8, temperature=0.1)
        pred = parse(r["content"])
        correct += (pred == gold)
        details.append((q[:10], gold, pred))
        time.sleep(0.2)
    return correct / len(TEST), details

res = {"meta": {"test_n": len(TEST), "models": ["Qwen2.5-0.5B", "glm-4-flash"]},
       "k_curve": {}, "random_label": {}}

print("== k 曲线 ==")
for k in [0, 1, 2, 4, 8]:
    a, da = eval_local(k); time0 = time.time()
    b, db = eval_glm(k)
    res["k_curve"][str(k)] = {"qwen": a, "glm4flash": b}
    print(f"  k={k}: Qwen-0.5B {a:.0%} | glm-4-flash {b:.0%} ({time.time()-time0:.0f}s)")

print("== k=4 随机标签消融（Min et al. 2022 复现） ==")
a, da = eval_local(4, True); b, db = eval_glm(4, True)
res["random_label"]["k4_random"] = {"qwen": a, "glm4flash": b}
res["random_label"]["qwen_details"] = da; res["random_label"]["glm_details"] = db
print(f"  随机标签: Qwen-0.5B {a:.0%} (正确标签 {res['k_curve']['4']['qwen']:.0%}) | "
      f"glm-4-flash {b:.0%} (正确标签 {res['k_curve']['4']['glm4flash']:.0%})")

save("e2_fewshot", res)

# ---- 可视化 ----
import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
ks = ["0", "1", "2", "4", "8"]
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(ks, [res["k_curve"][k]["qwen"] for k in ks], "o-", label="Qwen2.5-0.5B(本地)")
ax.plot(ks, [res["k_curve"][k]["glm4flash"] for k in ks], "s-", label="glm-4-flash(API)")
ax.axhline(0.5, ls="--", c="gray", lw=0.8, label="随机基线 50%")
ax.scatter(["4"], [res["random_label"]["k4_random"]["qwen"]], marker="x", s=90,
           c="C0", label="Qwen k=4随机标签")
ax.scatter(["4"], [res["random_label"]["k4_random"]["glm4flash"]], marker="x", s=90,
           c="C1", label="glm k=4随机标签")
ax.set_xlabel("few-shot 示例数 k"); ax.set_ylabel("测试集准确率")
ax.set_title("E2 少样本 k 曲线 + 随机标签消融"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("results/e2_fewshot.png", dpi=130)
print("[saved] results/e2_fewshot.png")
