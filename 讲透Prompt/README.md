# 讲透 Prompt 工程 · 完整版

> 用「直觉 → 数学 → 代码 → 不足 → 应用」讲透 Prompt 工程。从"prompt 是条件概率里的条件"到 CoT/结构化输出/上下文工程。姊妹项目：`../讲透激活函数/`、`../讲透基础模型/`、`../讲透微调/`、`../讲透RAG/`、`../讲透LLM/`（整合枢纽）。

**主线 5 篇 + 扩展 4 篇 + 激活总纲，全部完成**（05-08 与 5W3H 总纲为扩展篇）。

## 阅读顺序
```
00-为什么Prompt是控制信号 (条件概率本质)
   │
01-Few-shot与ICL (不更新权重学新任务的奇迹)
   │
02-CoT思维链 (分步推理=分治)  →  03-结构化输出与函数调用 (Agent基础)
   │
04-上下文工程与评估
   │
扩展: 05-SelfConsistency → 06-ToT (推理深化) | 07-ReAct (推理+行动) | 08-Prompt安全 (反面)
   │
总纲: 激活LLM能力-5W3H分析 (22手段全景 → ../激活大语言模型能力-总结.md 四层谱系)
```

## 章节
| # | 文件 | 核心 | 实验 |
|---|---|---|---|
| 00 | `00-为什么Prompt是控制信号.md` | prompt=P(输出\|输入)的条件 | trigram: 不同prompt不同输出 |
| | `experiments/00_why_prompt.py` ✅ | | |
| 01 | `01-Few-shot与ICL.md` | ICL不更新权重学新任务; 涌现; induction head | 最近邻类比模拟ICL |
| | `experiments/01_few_shot.py` ✅ | | |
| 02 | `02-CoT思维链.md` | 分治; token预测角度; 涌现; Zero-shot CoT | 17×24分治+GSM8K文献 |
| | `experiments/02_cot.py` ✅ | | |
| 03 | `03-结构化输出与函数调用.md` | JSON/Schema约束解码; Function Calling; Agent基础 | (概念) |
| 04 | `04-上下文工程与评估.md` | lost in middle; 信息密度; LLM-as-Judge | (概念) |
| 05 | `05-SelfConsistency.md` | 采样 N 次取多数票；用多样性对冲单点随机错误 | (文献) |
| 06 | `06-TreeofThoughts.md` | 思维成树：生成-评估-剪枝-回溯，CoT 的搜索版 | (文献) |
| 07 | `07-ReAct.md` | 推理+行动交替；工具调用补外部事实 | (文献) |
| 08 | `08-Prompt安全.md` | 注入/越狱/上下文污染——激活的反面：防模型被骗 | (概念) |
| **⭐ 总纲** | [`激活LLM能力-5W3H分析.md`](激活LLM能力-5W3H分析.md) | **22 个激活手段 5W3H 全解**（What/Why/How/效果/成本 + 决策树 + 9 陷阱 + 黄金组合）；四层谱系横向总结见 [`../激活大语言模型能力-总结.md`](../激活大语言模型能力-总结.md) | (文献) |
| 枢纽 | `00-讲透笔记-算法经验枢纽.md` | 跨单元算法经验索引 | — |
| **地图** | [`Prompt综述精华-四篇地图.md`](Prompt综述精华-四篇地图.md) | **四篇高影响力综述核实蒸馏**（The Prompt Report 2406.06608：33 术语/58 技术六族分类；APO 双综述：优化理论形式化 + AWS 5-part 工程框架）+ 全系列章节映射 | — |
| **实战** | [`../Agent框架案例/prompt工程工具链/`](../Agent框架案例/prompt工程工具链/README.md) | 六仓蓝图（optimizer/promptfoo/ragas/opik/promptflow/leaks）→ opencode `/optimize` `/ptest` `/evalrag` 工具链 | ✅ |

## 五大核心洞见
1. **Prompt 是条件**：改 prompt = 改 P(输出|输入) 的输出分布，模型权重不变。
2. **ICL 是奇迹**：prompt 放例子就学新任务且不改权重，是大模型涌现能力（induction head）。
3. **CoT 是分治**：把一次难推理拆成多次易推理，涌现能力，Zero-shot 一句"一步步思考"就能激发。
4. **结构化输出靠约束解码**：Schema + 有限状态机物理保证合法，比 prompt 要求 JSON 可靠。
5. **上下文工程**：警惕中间丢失、保持高密度、关键信息放首尾。

## 与其他系列的关系
- **Prompt 是 RAG/微调/Agent 的统一接口**：RAG 把检索结果塞 prompt；微调后的模型仍靠 prompt 驱动；Agent 靠 prompt(系统提示+工具描述) 规划。
- 横向打通见 `../横向打通-能力获取决策框架.md`。

## 环境备忘
本机无本地 LLM。实验用小模型(trigram/最近邻)演示**原理**(prompt作为条件/ICL类比/CoT分治)，真实 Prompt 工程的指令遵循/ICL/CoT 依赖大模型涌现，在豆包/DeepSeek 等上才完全显现（可在它们上验证练习）。

---

## 🔗 理论锚点（§12-15 横向打通）

> 本系列讲"条件概率/ICL/CoT/结构化输出"的 Prompt 工程；这门课把**偏好数据聚合**公理化：
> 枢纽：[`§12-15 整合`](../§12-15%20理论·形式化·安全·可信AI%20整合.md) §21

| 课程 | 产物 | 公理化的内容 |
|---|---|---|
| §15.3 Stanford CS329T/CS324（Percy Liang）| [`pluralistic_safety.py`](../top-cs-projects/stanford-cs-projects/topic3-safety/pluralistic_safety.py) | preference data 聚合数学（Borda/Approval/Condorcet）+ Arrow 不可能性——Prompt 对齐背后的社会选择理论 |

---


---

## 🎭 欺骗动力学视角：模型表面顺从

> 承接 [`欺骗动力学-社会进步的隐秘引擎.md`](../欺骗动力学-社会进步的隐秘引擎.md) §5。

### 三问

1. **讲透Prompt 防的是什么欺骗？** → Sycophancy（模型假装顺从而实际出错）的最小单位。
2. **被什么攻破？** → prompt 注入 / 越狱 / 上下文污染。
3. **沉淀进哪条主链？** → AI 安全主链——prompt 安全是 LLM 时代反欺骗的第一道门。

### 一句话

> Prompt 工程的反面是 prompt 安全：前者让模型听话，后者防模型被骗、骗人。
