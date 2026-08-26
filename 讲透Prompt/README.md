# 讲透 Prompt：一门实验科学（Prompt Engineering）

> 知识卡宇宙：`讲透X` 系列 | 三层宪法：**直觉 → 公式 → 代码（bash 跑通）** | 五幕：直觉→数学→代码→不足→应用
> 源站：[Prompt Engineering Guide 中文版](https://www.promptingguide.ai/zh)（44 页源文存档 `_source/`）+ [Google Cloud: What is prompt engineering](https://cloud.google.com/discover/what-is-prompt-engineering)
> 本章证据标准：**每个知识点配一个真实可跑的实验**（`experiments/` 下 py + 结果 json/png），绝不停留在"指南说"。

## 为什么要有这个单元

Prompt 工程是零基础上手 AI 的第一课，但市面教程止步于"技巧清单"。本单元的三个增量：
1. **实验化**：指南里每个技巧（zero-shot→CoT→ToT→ReAct→对抗）都用本地 Qwen2.5-0.5B + 智谱 GLM API 真跑一遍，给出数字，而不是复述论文数字；
2. **模型适配**：同一个 prompt 在不同模型（小模型/大模型/思考型模型）上表现截然不同——这是 2025-2026 最重要的实践知识，指南 reasoning-llms 篇 + ACL 2026 敏感性研究给你讲透；
3. **自动优化 + 数学落地**：OPRO/APE/DSPy 自动找 prompt，最后全部应用到数学（GSM8K 矩阵 + Lean/Prover 实战模板）。

## 篇目表（目录宪法）

| # | 章节 | 核心实验 | 状态 |
|---|------|---------|------|
| 00 | 开场白：Prompt 是一门实验科学 | — | ⬜ 明日写 |
| 01 | 基础：模型设置与提示词要素 | E1 temperature/top_p 实测 ✅ | ⬜ 明日写 |
| 02 | 零样本与少样本 | E2 k 曲线+随机标签消融 ✅ | ⬜ 明日写 |
| 03 | CoT 与自我一致性 | E3 待跑 / E4 待跑 | ⬜ 明日写 |
| 04 | 知识增强与程序辅助 | E5 PAL 待跑 | ⬜ 明日写 |
| 05 | 搜索与行动：ToT 与 ReAct | E6/E7 待跑 | ⬜ 明日写 |
| 06 | 链式与组合 | E-mini 待跑 | ⬜ 明日写 |
| 07 | 对抗与安全 | E8 待跑 | ⬜ 明日写 |
| 08 | ★ 模型适配：不同模型怎么吃 prompt | E9 五模型配置×同 prompt 矩阵 | ⬜ 明日写 |
| 09 | ★ 自动优化 Prompt | E10 OPRO 自实现 + DSPy | ⬜ 明日写 |
| 10 | ★ 前沿 2025-2026 | 文献综述（素材已备） | ⬜ 明日写 |
| 11 | ★ 数学领域应用 | E11 GSM8K 矩阵 + Lean 模板 | ⬜ 明日写 |
| 12 | 不足与展望：批判收尾 | — | ⬜ 明日写 |

> **诚实状态（2026-08-25 下班）**：素材全部就绪（44 页源文存档+25 篇论文核实+前沿检索完成），实验基座 3 通道验证通过，E1/E2 跑通落盘，E3 脚本就绪未跑。章节全部未写。断点详情见 `RESUME-0825.md`。

★ = 用户重点关注的四大主题（模型适配 / 自动优化 / 前沿研究 / 数学应用）。

## 实验环境（真实可复现）

- **本地**：Qwen2.5-0.5B-Instruct（transformers, CPU, `~/ai/models/`）
- **API**：智谱 GLM（glm-4-flash 便宜档 / glm-4.7 / glm-5 思考模型），密钥走 opencode auth.json，绝不硬编码
- **铁律**：①小模型 thread=1 ②实验脚本独立可跑 ③结果存 json+png ④arXiv ID 全部核实（见各章引用）

## 挂网（本单元的桥）

- 上游：`讲透Agent/`（harness 把 prompt 当代码管理）、`讲透NLP/`（Ch22 词典分类 = prompt 的对照面）、`prompt工程手册（工程化手册库）`（本单元的理论深化版）
- 下游：`讲透Agent/实战案例-Prover数学Agent/`（Ch11 Lean prompt 直接复用其 harness）
- 横向：`top-math-courses/MATH_LOOP_ENGINE.md`（数学实验循环）、`讲透模型/`（模型宇宙）
- **姊妹篇（2026-08-26 新建）：`../讲透Context/`**——升维到整个窗口的信息设计学（compaction/memory/sub-agent/Context Rot/Bloom filter 对决），其 Ch02 位置效应以本单元 E1/E2 为实验基座

## 来源与核实

- 44 页指南源文（zh 35 + en 9）存档于 `_source/`，2026-08-25 抓取自 dair-ai/Prompt-Engineering-Guide GitHub 仓库（MIT 许可）
- 25 篇关键论文 arXiv ID 于 2026-08-25 逐一直接核实（arxiv.org abs 页）；6 篇次要引用标注"据指南"
- Google Cloud 页面内容经 websearch 全文获取（含 Gemini Enterprise Agent Platform 的 prompt 组件表）
