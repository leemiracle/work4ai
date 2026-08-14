# 讲透 Prompt 工程 · 完整版

> 用「直觉 → 数学 → 代码 → 不足 → 应用」讲透 Prompt 工程。从"prompt 是条件概率里的条件"到 CoT/结构化输出/上下文工程。姊妹项目：`../讲透激活函数/`、`../讲透基础模型/`、`../讲透微调/`、`../讲透RAG/`。

**5 篇全部完成**。

## 阅读顺序
```
00-为什么Prompt是控制信号 (条件概率本质)
   │
01-Few-shot与ICL (不更新权重学新任务的奇迹)
   │
02-CoT思维链 (分步推理=分治)  →  03-结构化输出与函数调用 (Agent基础)
   │
04-上下文工程与评估
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
| §15.3 Stanford CS329T/CS324（Percy Liang）| [`pluralistic_safety.py`](../stanford-cs-projects/topic3-safety/pluralistic_safety.py) | preference data 聚合数学（Borda/Approval/Condorcet）+ Arrow 不可能性——Prompt 对齐背后的社会选择理论 |

---


---

## 🎭 欺骗动力学视角：模型表面顺从

> 承接 [`欺骗动力学-社会进步的隐秘引擎.md`](欺骗动力学-社会进步的隐秘引擎.md) §5。

### 三问

1. **讲透Prompt 防的是什么欺骗？** → Sycophancy（模型假装顺从而实际出错）的最小单位。
2. **被什么攻破？** → prompt 注入 / 越狱 / 上下文污染。
3. **沉淀进哪条主链？** → AI 安全主链——prompt 安全是 LLM 时代反欺骗的第一道门。

### 一句话

> Prompt 工程的反面是 prompt 安全：前者让模型听话，后者防模型被骗、骗人。
