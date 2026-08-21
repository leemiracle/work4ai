# 附录 K — 基于框架的对话系统：槽位填充与状态追踪

> 对应 SLP3 附录 K。前面讲了句子级的语义（FOL、词义），但在实际应用中，用户说的话需要被映射成**结构化的任务表示**。任务型对话系统（task-oriented dialogue）用**框架-槽位**（frame-slot）范式组织交互——这是从 1977 年 GUS 到 2010 年代 Siri 统治了产业界 30 年的架构。

---

## 1. 直觉：对话 = 填一张表

订机票需要知道：出发城市、目的城市、日期、时间。把这些必填项做成一张“表”（frame），系统不断提问直到所有**槽位**（slot）填满，然后执行操作。

```
FRAME: AIR-TRAVEL
  ORIGIN_CITY:  Boston       ✓
  DEST_CITY:    San Francisco ✓
  DATE:         Tuesday       ✓
  TIME:         morning       ✓
  → 查询数据库 → 返回航班列表
```

用户说 *"Show me morning flights from Boston to San Francisco on Tuesday"*，系统提取：

```
DOMAIN: AIR-TRAVEL   INTENT: SHOW-FLIGHTS
ORIGIN-CITY: Boston   DEST-CITY: San Francisco
ORIGIN-DATE: Tuesday   ORIGIN-TIME: morning
```

**三件事**一起做：(1) **领域分类**（AIR-TRAVEL vs ALARM-CLOCK）→ (2) **意图识别**（SHOW-FLIGHTS vs SET-ALARM）→ (3) **槽位填充**（BIO 序列标注）。

---

## 2. 核心组件

### 2.1 槽位填充（Slot Filling）

用 BIO 序列标注从用户话语中提取槽-值对：

```
I want to fly to San Francisco on Monday afternoon
O  O    O O  O  B  I         I  B       I
                        ↑DEST      ↑DATE ↑TIME
```

现代方法：预训练语言模型 encoder + feedforward + softmax，每个 token 输出一个 BIO 标签；EOS 位置额外输出 domain+intent。

### 2.2 对话状态追踪（Dialogue State Tracking, DST）

DST 维护**累积**的框架状态——不只是当前句子的槽位，而是整个对话到目前为止所有约束的汇总：

| 轮次 | 用户输入 | DST 状态 |
|------|---------|---------|
| 1 | *"cheaper restaurant"* | `price=cheap` |
| 2 | *"Thai food, downtown"* | `price=cheap, food=Thai, area=centre` |
| 3 | *"where is it?"* | `price=cheap, food=Thai, area=centre; request=address` |

> 注意第 3 轮用户没重复说 Thai/cheap，但 DST **保留**了前面轮的信息。DST 还要检测**纠错**（用户改主意：*"No, I said Italian"* → 覆盖 food 槽）。

### 2.3 对话策略（Dialogue Policy）

策略决定系统**说什么**（生成哪个对话行为）：

- **确认策略**：显式确认（*"Is that correct?"*）vs 隐式确认（重复确认+追问）vs 不确认——由 ASR 置信度阈值 $a < b < \gamma$ 决定。
- **拒绝**：低置信度时 *"I'm sorry, I didn't understand."*

### 2.4 句子实现（Sentence Realization）

从对话_act + 槽位值生成自然语言。现代方法用 encoder-decoder，先**去词汇化**（delexicalize：把具体值替换为 slot 占位符），训练后再**重新词汇化**（relexicalize：填回真实值）。

---

## 3. 历史脉络

| 系统/时期 | 特点 |
|-----------|------|
| **ELIZA** (1966) | 模式匹配聊天机器人，无任务理解 |
| **GUS** (Bobrow et al. 1977) | 首个框架驱动系统，订机票——奠定 30 年范式 |
| **MERCURY** (1999) | AT&T/Bell Labs，引入统计方法做槽填充 |
| **HIS** (Young et al. 2010) | POMDP 对话管理 + 对话_act tagset |
| **Siri/Alexa** (2010s) | GUS 架构商业化，大规模部署 |
| **DSTC 系列** (2013-至今) | 对话状态追踪挑战赛年度评测 |

### 对话行为（Dialogue Acts）

```
HELLO, INFORM, REQUEST, CONFIRM, AFFIRM, NEGATE,
DENY, SELECT, BYE, REQALTS, CONFREQ ...
```

每个 act 携带内容参数：`inform(food=Italian, near=museum)`。

---

## 4. LLM 时代的范式变迁

| 维度 | 经典框架系统 (GUS→Siri) | LLM 任务型对话 |
|------|------------------------|----------------|
| **槽位提取** | BIO 序列标注 + 分类器 | LLM 直接 JSON/function call |
| **DST** | 独立模块，累积规则 | LLM 隐式维护（context window） |
| **策略** | 规则 / RL | LLM 推理（chain-of-thought） |
| **生成** | 模板 / encoder-decoder | 端到端自然语言生成 |
| **领域扩展** | 每个新领域需标注+训练 | 换 prompt 即可 |
| **可控性** | 高（规则透明） | 低（黑盒，需 guardrail） |

> **LLM 并没有抛弃框架思想**——function calling / tool use 的 JSON schema 就是“数字化的 frame”。区别是：经典系统手工定义 frame + 训练分类器；LLM 用 prompt 描述 frame + 推理填充。**框架作为知识结构**依然有效，变的只是实现方式。

---

## 5. 批判性视角

- **框架范式的局限**：只适合**槽位明确**的任务（订票、设闹钟）。开放域对话、咨询、情感支持无法用 frame 建模——这恰恰是 GUS 架构做不到而 LLM 擅长的领域。
- **DST 至今未“解决”**：即使在 LLM 时代，多轮对话中的槽位继承、纠错、跨领域槽位传递仍是难点。MultiWOZ 上的 state tracking accuracy 仍有很大提升空间。
- **可解释性的权衡**：经典系统的每个决策可审计（哪条规则触发、哪个槽位被填）；LLM 的决策不可解释。在医疗、金融等高风险领域，这种可审计性可能比“更自然”更重要。

---

## ✍️ 练习

1. ⭐ 给出 *"Book me a table at Roma for 2 tomorrow at 7pm"* 的 frame 表示。有几个槽位？哪些需要后续追问？
2. 用户先说 *"I want Italian food"*，后说 *"Actually make it Chinese"*。DST 应如何更新？纠错检测为什么难？
3. ★ LLM 的 function calling 和经典 frame 系统在概念上有什么相同和不同？为什么说 “frame 思想没有过时”？

→ 回到 [README.md](../README.md)：至此 SLP3 附录 G-K 补完了语义（G/H）、词义（I）、词向量（J）、对话（K）五大板块。
