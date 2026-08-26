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
| 00 | [开场白：Prompt 是一门实验科学](00-开场白.md) | 五大反直觉数字总览 | ✅ |
| 01 | [基础：模型设置与提示词要素](01-模型设置与提示词要素.md) | E1 temperature/top_p（互异 1/12/12，top_p 压过温度） | ✅ |
| 02 | [零样本与少样本](02-零样本与少样本.md) | E2 k 曲线 + 随机标签消融（glm 100% 纯格式学习） | ✅ |
| 03 | [CoT 与自我一致性](03-CoT与自我一致性.md) | E3 矩阵（few-direct 毒药 10%）+ E4 SC 反例（5:4 投错） | ✅ |
| 04 | [知识增强与程序辅助](04-知识增强与程序辅助.md) | E5 PAL 平手 + 失败分类学（错误搬家：算术层→建模层） | ✅ |
| 05 | [搜索与行动：ToT 与 ReAct](05-搜索与行动ToT与ReAct.md) | E6 ToT 0% 三臂 + E7 ReAct 33%→67%（协议开销反例） | ✅ |
| 06 | [提示链与组合](06-提示链与组合.md) | E-mini 链式 60%→73%（规范化分段击破） | ✅ |
| 07 | [对抗与安全](07-对抗与安全.md) | E8 无防御 5/8 攻破、防御全 1/4 安慰剂、模型规模真防御 | ✅ |
| 08 | [★ 模型适配](08-模型适配.md) | E9 四配置矩阵（thinking 开关切换最优策略） | ✅ |
| 09 | [★ 自动优化 Prompt](09-自动优化Prompt.md) | E10 OPRO（天花板效应+解析器教训）+ DSPy/Bootstrap | ✅ |
| 10 | [★ 前沿 2025-2026](10-前沿2025-2026.md) | 敏感性 scaling law / SAIR 单 prompt 天花板 / reasoning 接口化 | ✅ |
| 11 | [★ 数学领域应用](11-数学领域应用.md) | E11 矩阵（zero-cot +87.5pp）+ Persona 过程≠对错 + Prover 三模板 | ✅ |
| 12 | [不足与展望](12-不足与展望.md) | 十条定律（每条带实验编号）+ 期权清单 | ✅ |

> **完成状态（2026-08-26）**：13 章 + 11 个实验（E1-E11 + E-mini，12 组 json/png）全部完成。断点档案见 `RESUME-0826.md`（完成档案 + 期权清单）。

★ = 用户重点关注的四大主题（模型适配 / 自动优化 / 前沿研究 / 数学应用）。

## 实验环境（真实可复现）

- **本地**：Qwen2.5-0.5B-Instruct（transformers, CPU, `~/ai/models/`）
- **API**：智谱 GLM（glm-4-flash 便宜档 / glm-4.7 / glm-5 思考模型），密钥走 opencode auth.json，绝不硬编码
- **铁律**：①小模型 thread=1 ②实验脚本独立可跑 ③结果存 json+png ④arXiv ID 全部核实（见各章引用）
- **长实验规约（0826 新增）**：本地 CPU 跑 CoT 单次 ~120s——双通道拆分（api 前台 / local lite 后台 setsid），前台单脚本 ≤10min

## 挂网（本单元的桥）

- 上游：`讲透Agent/`（harness 把 prompt 当代码管理）、`讲透NLP/`（Ch22 词典分类 = prompt 的对照面）、`prompt工程手册/`（工程化视角，本单元=其实验视角，已互链 工程化手册总览）
- 下游：`讲透Agent/实战案例-Prover数学Agent/`（Ch11 Lean prompt 直接复用其三模板）、`讲透Agent/讲透Prompt/`（注入深潜版 57 case，Ch07 互链）
- 横向：`top-math-courses/MATH_LOOP_ENGINE.md`（数学实验循环）、`讲透模型/`（模型宇宙）、`讲透Context/`（输入侧姊妹篇）、`讲透Loop/`（多次采样的循环化）

## 来源与核实

- 44 页指南源文（zh 35 + en 9）存档于 `_source/`，2026-08-25 抓取自 dair-ai/Prompt-Engineering-Guide GitHub 仓库（MIT 许可）
- 25 篇关键论文 arXiv ID 于 2026-08-25 逐一直接核实（arxiv.org abs 页）；6 篇次要引用标注"据指南"
- 前沿素材（10 章）2026-08-25 检索核实：ACL 2026 Findings 2084 / arXiv 2608.18539 / 2608.03401 / 2604.18897 / ACL 2026 order 敏感性 / Springer 2026 persona 研究
- Google Cloud 页面内容经 websearch 全文获取（含 Gemini 平台 prompt 组件表与 "Thinking vs Reasoning" 建议）
