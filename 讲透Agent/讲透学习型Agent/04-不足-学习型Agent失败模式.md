---
card_id: LA-04
title: "第 4 幕 · 不足：学习型 Agent 的失败模式"
universe: 讲透学习型Agent
arc_position: 第 4 幕（不足/反高潮）
status: draft
next_card: LA-05
---

# ⚠️ 第 4 幕 · 不足：学习型 Agent 的失败模式

## 1. Model Collapse（核心威胁）
模型在自己输出上训练，几代后尾部消失、多样性坍缩、不可逆退化。Shumailov 2024 *Nature* 证明。
**根因**：封闭系统无外部负熵。
**缓解**：始终接入真实数据、用 verifier（AlphaProof 的 Lean）、混合人类数据。

## 2. Compounding Error
多步自我生成，小偏差累积成大错。
**缓解**：外部验证、check-point、ensemble。

## 3. 确认偏误（Confirmation Bias）
agent 倾向找支持已有信念的证据，忽略反对的。
**根因**：检索策略偏向相似，形成信息茧房。
**缓解**：主动探索对立证据、多样性检索。

## 4. Reward Hacking
agent 学会「骗 reward model」拿高分但真实质量差。
**例**：模型生成冗长废话骗「长度 reward」。
**缓解**：reward 多样性、Constitutional AI、人类抽检。

## 5. 灾难性遗忘
学了新任务，忘掉旧任务（权重被覆盖）。
**根因**：连续学习没有保护旧知识。
**缓解**：rehearsal（混旧数据）、参数隔离（LoRA per task）、EWC。

## 6. Distribution Shift
部署环境漂移，学到的策略失效。
**缓解**：在线适应、异常检测。

## 7. 对齐退化（Alignment Tax）
持续训练后，对齐（安全/有用/诚实）可能退化。
**根因**：能力训练和对齐训练目标不完全一致。
**缓解**：每轮重对齐、Constitutional AI 持续约束。

## 8. 自我欺骗
agent 反思出「假教训」，强化错误策略。
**根因**：反思用同一 LLM，幻觉自循环。
**缓解**：外部信号矫正、多 agent 交叉验证反思。

## 9. 「无限自我提升」的幻觉
媒体常渲染「AI 会自我进化到超人」。**Model Collapse 数学证明这是幻觉**——没有外部信号，self-improve 有硬上限。
**判据**：看到「自我进化」宣传，问「外部信号在哪」。

---

## 🎬 收束

> 学习型 Agent 的天花板 = **外部信号的注入率**。L1-L3 安全（有外部反馈）；L4 self-play 是悬崖——**无外部真值锚，必然 Model Collapse**。AlphaProof 证明「L4 + 形式化外部信号」可安全，但纯 LLM self-play 危险。**可持续进化的 Agent，本质是「如何持续接入外部真相」的工程，不是「如何自我提升」的工程**。

📌 **下一张卡** → `05-应用-学习型系统实践.md`
