# AI-Scientist 深读卡 —— SakanaAI 全自主科研 Agent（idea→实验→论文→自评审 全闭环）

> **定位**：SakanaAI 的 "The AI Scientist"（论文 arXiv:2408.06292）官方实现——给定研究模板（代码+数据+latex 骨架），Agent 自主完成**想法生成 → 实验迭代（Aider 改代码+跑实验）→ 论文撰写（LaTeX）→ LLM 评审（模拟 ICLR reviewer）**，每篇成本 ~$15/篇。本仓库为 v1；v2（tree search 版，arXiv:2504.08066）与 workshop 化另见 ai-scientist-v2 仓库。
> **本地**：`repos/ai-scientist`（SakanaAI/AI-Scientist）｜**深读**：deepwiki 28 子页归档 `deepwiki/ai-scientist/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 阶段 | 脚本 | 职责 |
|---|---|---|
| Idea 生成 | `generate_ideas.py` | 从模板 seed 出发，LLM 头脑风暴+去重+打分，产出 ideas.json |
| 实验执行 | `perform_experiments.py` | **内部调 Aider**（aider coders）迭代改代码跑实验，记 notes/max_perf 行 Plotting |
| 论文写作 | `generate_paper.py` | LaTeX 模板填充（ latexmk 编译，引用 bibtex 自动检索配对）|
| 评审 | `perform_review.py` | few-shot ICLR 风格评审（Soundness/Presentation/Contribution/Overall/Rating/Confidence 6 维）|
| 编排 | `ai_scientist/__init__.py`（launch_scientist） | 全流程串联 + 并行实验 + 超时控制 |

## 二、核心机制

1. **Aider 嵌入式代码 Agent**（Experiment Execution 页）：实验阶段不是自研循环，而是直接 `aider.coders.Coder` 创建编码会话——"科研 Agent 内嵌编码 Agent"的组件复用范式；每轮实验 Aider 修改 `experiment.py`/`prompt.json`，跑后解析结果写入 notes。
2. **LLM 评审器 = few-shot 检索**（Review System Training 页 15-17）：评审 prompt 由 ICLR 评审样本库（`data/` 9 篇）做相似度检索动态拼装；`perform_review` 含 reflection 机制（对已有 review 再评一轮可提升质量）；还产出 self-review 分析（22 页：模型偏好好评的统计）。
3. **模板即研究域**（Template System 页）：每个模板（nanoGPT/2d_diffusion 等 4 个）= 完整可跑实验代码 + latex 骨架 + 数据准备脚本；换研究方向=换模板目录——领域知识全部外置于模板，Agent 核心零领域假设。
4. **成本控制工程**：阶段化 LLM 配置（idea 用强模型、写作可换便宜模型）、并行多实验（`parallel_experiments`）、每阶段超时+轮次上限。

## 三、与讲透系列的对位

| AI-Scientist 概念 | 讲透系列对应 |
|---|---|
| idea→实验→论文→评审闭环 | 讲透学习型Agent/05 §自主科学发现 |
| 嵌入 Aider 做编码 | 讲透Agent/01 §组件复用（Agent 调 Agent）|
| LLM-as-Reviewer few-shot | 讲透Agent/00 §LLM 评判（对照 reward model）|
| 模板化领域封装 | ml-experiment §实验模板与复现 |

## 四、关键入口

```
ai_scientist/generate_ideas.py       # 想法生成（头脑风暴+novelty 查重）
ai_scientist/perform_experiments.py  # Aider 迭代实验（核心页 8，11KB）
ai_scientist/generate_paper.py       # LaTeX 写作+编译
ai_scientist/perform_review.py       # LLM 评审（含 reflection）
ai_scientist/templates/              # 4 个研究模板（nanoGPT 等）
ai_scientist/launch_scientist.py     # 主管道（init 暴露）
```

## 五、深读子页地图（28 页精选 6）

2 System Architecture（5 图管道全景）｜8 Experiment Execution（Aider 集成）｜9-10 Paper Writing/Review（写作+评审双页）｜15-17 Review Training 三连页（few-shot 检索式评审）｜22 Self-Review Analysis（诚实的偏差统计）｜12-14 Template System。

## 六、与"我们"的关系（一句话）

"AI 做科研"叙事的最可跑注脚：28 页 wiki 全归档后，讲透学习型Agent 的终章可以从"愿景"落到"每阶段一个 python 脚本"的工程现实；其评审器 few-shot 设计可直接搬进任何 LLM-as-judge 教程。

---
生成：2026-08-21 · deepwiki 28 页全归档 · v1 快照（v2 tree-search 版在 SakanaAI/AI-Scientist-v2）
