# 09 Prompt 自动优化（APO）：从"手搓"到"搜索"

> 讲透 Prompt 工程扩展篇 · 素材：[Prompt综述精华-四篇地图](./Prompt综述精华-四篇地图.md) §三（四篇综述核实的 APO 双篇）
> arXiv 一手核实：2502.11560（优化理论）/ 2502.16923（AWS，EMNLP 2025 main）/ ProTeGi 等

---

## 1. 灵魂：一句话钉死

> **APO = 把 prompt 工程变成一个优化问题**：$\max_{P} \mathbb{E}[\text{acc}(f(P(x)), y)]$——你不再写 prompt，你写**评估函数**，让机器搜 prompt。

00 章说"prompt 是条件概率里的条件"；本章说：**找最好的条件，是一个搜索问题，搜索应该交给机器**。

---

## 2. 直觉：为什么手搓会输给搜索

三个理由（对应 The Prompt Report 对 prompt engineering 的定义——"**迭代地**组合/测试/选择"，迭代二字就是优化的种子）：

1. **组合爆炸**：指令词 × few-shot 示例选择 × 排序 × 格式——语义相近的 prompt 性能差异巨大（Sclar et al.: 格式敏感；Liu et al.: 排序敏感）。人只能试几个点，机器能扫上千。
2. **敏感性即脆弱性**：换个模型版本，你精心手搓的 prompt 可能失效——手搓结果不可迁移，搜索流程可迁移。
3. **人是坏评估器**：你觉得自己写的 prompt 好，往往是在自己脑补的 5 个例子上测试。机器优化被迫面对一个诚实的验证集。

**文本梯度（ProTeGi 核心比喻）**：数值优化里梯度告诉我们"往哪个方向调参数"；ProTeGi 让 LLM 看错误样本后输出一句自然语言反馈——"这些错误都是否定句，应该提示模型注意否定词"——这句反馈就是**文本空间的梯度方向**，再用它改写 prompt 就是"沿着梯度走一步"。

---

## 3. 数学：优化理论框架（2502.11560）

### 3.1 统一形式化

$$\max_{P \in \mathcal{P}} \; \mathbb{E}_{(x,y) \sim \mathcal{D}_{val}} \left[ g\big(f(P(x)), y\big) \right]$$

prompt 空间三分为：

| 空间 | 优化变量 | 可微性 | 代表方法 | 你能读懂吗 |
|---|---|---|---|---|
| 离散 $\mathcal{P}_d$ | 硬指令 I / few-shot 示例 $\{e_i\}$ | ❌ 组合爆炸 | APE / ProTeGi / DSPy | ✅ |
| 连续 $\mathcal{P}_c$ | 可学习嵌入 $\theta_i \in \mathbb{R}^d$ | ✅ 梯度直接可用 | Prefix/Prompt/P-Tuning | ❌（soft prompt 是向量）|
| 混合 $\mathcal{P}_h$ | 离散 × 连续 | 部分 | soft→hard 回译投影 | 半 |

**黑盒约束**（2502.16923 的三特征）：API 模型拿不到参数 → 只能走 $\mathcal{P}_d$；不要求参数访问 + 系统化搜索 + **保持人类可读**——可读性是 APO 相对微调的核心卖点（微调把知识埋进权重，prompt 优化后你还能看懂它说了什么）。

### 3.2 四计算范式

| 范式 | 机制 | 代表 |
|---|---|---|
| **FM as optimizer** | LLM 自己当优化器：解法+分数写进 meta-prompt，下一轮生成更好候选 | OPRO / PE2 / DSPy |
| **进化计算** | 遗传算子（变异+交叉）作用于 prompt 文本 | EvoPrompt（FM 生成 × GA 算子）/ SPRIG |
| **梯度** | soft prompt 直接 SGD；离散空间需"文本梯度"近似 | Prefix-Tuning / **ProTeGi** |
| **强化学习** | 策略梯度估计离散选择 | BDPL / Prompt-OIRL（测试时按查询选 prompt）|

### 3.3 AWS 5-part 工程框架（2502.16923，方法谱系的路标）

一个 APO 系统要回答五个问题：**在哪优化**（离散指令/示例选择排序/soft）→**种子哪来**（人写 / APE 从几百样本诱导 / README 诱导 SCULPT / 模板填充 UniPrompt）→**优化什么准则**（任务指标 / 多目标：SOS 把安全分纳入；Jafari：体积法优于加权平均）→**候选生成算子**（见 §4 速查表）→**什么迭代算法**（贪心 / 束搜索 / MCTS / 遗传 / 测试时动态 best-of-N）。

### 3.4 理论天花板：AlignPro 上界

AlignPro (2025) 证明：给定优化器，离散 prompt 优化的收益存在**上界**，且相对 RLHF 最优策略 $\pi^*$ 有不可消除的次优差距。直觉：prompt 只能激活模型已有的能力，不能创造新能力——**prompt 优化救不了模型缺陷**（实验 Part 4 验证）。

---

## 4. 方法谱系速查表（可操作）

| 方法 | 机制一句话 | 何时用 | 成本 |
|---|---|---|---|
| **APE** (2022) | 从几百个输入输出对"反向诱导"指令 | 完全没思路时生成种子 | 低（几十次调用）|
| **ProTeGi** (2023) | 文本梯度：错误样本→LLM 反馈→定向改写 | 有种子有验证集，通用默认 | 中 |
| **OPRO** (2024) | meta-prompt 里放"解法+分数"历史，LLM 自我改进 | 无代码集成，纯对话式 | 中 |
| **PromptAgent** (2024) | MCTS 四步（选择-扩展-模拟-回溯）搜索 prompt 空间 | 预算充足求最优 | 高 |
| **SPRIG** (2024) | 300 组件语料（CoT/角色/风格/情感…）上做遗传变异 | 优化**系统 prompt**（跨任务复用）| 中 |
| **EvoPrompt** (2024) | 遗传算法：变异+交叉两条谱系（GA/DE）| 有种群多样性需求 | 中 |
| **TextGrad** (2024) | 把"梯度"泛化成任意文本反馈，自动微分整个管线 | 多组件管线整体优化 | 中高 |
| **BPO** (2024) | 微调 7B 小模型当专用 prompt 优化器 | 大批量/要隐私（FIPO 本地化）| 一次性训练 |
| **DSPy** (框架) | 声明式编程：签名+模块+编译器（内置多种优化器）| 工程落地首选 | 视优化器 |

**决策树**（什么时候上 APO）：

```
任务能自动评估吗？（有明确指标/可程序化判分 or 可靠 LLM-as-Judge）
├─ 否 → 先解决评估（04 章），APO 无从谈起——评估函数是 APO 的引擎
└─ 是 → 手写 prompt 达到基线了吗？
    ├─ 否 → 先手写 baseline（APO 需要种子，好种子省预算）
    └─ 是 → 调用量级？
        ├─ 小（<1k 次/月）→ ProTeGi 式手动循环 + promptfoo 记录
        ├─ 中 → DSPy 编译（MIPROv2 优化器）
        └─ 大/产品级 → BPO 微调优化器 / PromptAgent MCTS + CI 集成
```

---

## 5. 代码：文本梯度 vs 随机搜索（实验 09）

**玩具世界**：情感分类；prompt = 激活的特征集合；模拟模型"prompt 提到什么才会用什么"；搜索空间 9 个候选指令（3 有用 + 6 干扰，干扰激活无益且 10% 概率带偏）；两个算子对同一差种子（只会"统计正面词"，acc 49%）。

```bash
python3 -u 讲透Prompt/experiments/09_apo.py
```

四部分结果（2026-08-17 实跑）：

| 实验 | 结果 | 说明 |
|---|---|---|
| P1 演化现场 | 49.0% → **96.5%**（1 轮补齐 2 缺陷）| 文本梯度一轮从错误里同时看到"否定句错"和"负面词句错" |
| P2 梯度 vs 随机 ×50 | **93.4% vs 70.5%**，胜 44/50 | 干扰项存在时，方向信息值钱——随机 6 轮预算大概率撞不满 3 个有用特征 |
| P3 种子×算子交叉 | 差种子+梯度 **93.6%** > 好种子+随机 84.6%（反超 40/50）| **反直觉：算子质量 > 种子质量**——好算子修 ALL 缺陷，随机算子在剩余空间瞎撞 |
| P4 上界 | 全有用特征 = **96.5% ≠ 100%** | 模拟模型否定处理只有 80% 生效——prompt 再好也修不了模型缺陷（AlignPro 直觉）|

实验骨架即 5-part 框架的化身：`apo_loop`（评估→收集错误→算子改写→贪心接受）里 `op_textual_gradient` 是候选生成算子，`evaluate` 是优化准则，验证集是 $\mathcal{D}_{val}$。

---

## 6. 不足：APO 的四个坑

1. **评估函数是真正的瓶颈**：优化器只会朝你给的指标走。指标设计错（比如只用 accuracy 忽略安全），APO 高效地优化出错误目标——垃圾进垃圾出的加速版。
2. **过拟合验证集**：AWS 综述明确警告。验证集要有代表性 + 留 held-out 测试集（04 章练习 2 的场景：测试集 90% 上线 70%）。
3. **算子设计仍是黑科技**：文本梯度为什么有效？没有理论保证，ProTeGi/PromptAgent/SPRIG 各有各的启发式。"recipe book"（2502.18746 的比喻）：算子是食材，迭代算法是烹饪法——组合有效但无菜单保证。
4. **上界存在**（AlignPro）：能力缺口只能靠微调/换模型补。APO 是"榨干现有模型"，不是"升级模型"。

---

## 7. 应用：三步落地

**① 最小可行（今天就能做）**：拿一个你已手写的 prompt + 20 个失败案例 → 让 LLM 分析错误模式并给一句改进反馈 → 按反馈改写 → 在 100 例验证集上对比。这就是一轮 ProTeGi，零框架成本。

**② DSPy 工程化**（声明式，编译器管优化）：

```python
import dspy
lm = dspy.LM("openai/gpt-4o-mini")  # 或本地模型
dspy.configure(lm=lm)

class Sentiment(dspy.Signature):
    """判断句子情感倾向"""
    sentence: str = dspy.InputField()
    positive: bool = dspy.OutputField()

# 声明模块（不写 prompt），交给优化器
trainset = [dspy.Example(sentence=s, positive=p).with_inputs("sentence") for s, p in data]
optimize = dspy.MIPROv2(metric=my_metric)   # metric = 你写的评估函数 = 优化引擎
optimized = optimize.compile(dspy.Predict(Sentiment), trainset=trainset)
```

关键转移：**你的工作从"写 prompt"变成"写 metric + 攒数据"**。

**③ 工具链衔接**：本仓 [`../Agent框架案例/prompt工程工具链/`](../Agent框架案例/prompt工程工具链/README.md) 的六仓蓝图（optimizer/promptfoo/ragas）→ opencode `/optimize` `/ptest` 命令；CI 里挂 prompt 回归（换模型版本自动重跑评估，防敏感性失效）。

---

## ✍️ 练习

**A**（文本梯度）：把实验的 `op_textual_gradient` 噪声从 20% 调到 50%，P2 优势还剩多少？找到梯度失效的临界噪声。
**B**（上界直觉）：给模拟模型加一个"修复模式"（否定 100% 生效），验证 prompt 优化后能到 100%——体会"上界由模型决定"。
**C**（实战）：用方法①对自己的一个真实 prompt 做三轮 ProTeGi 循环，记录每轮 acc 与反馈文本。
**D**（Deep Thinking）：如果评估函数本身是个 LLM-as-Judge，它的偏差会不会被 APO 放大？如何检测（提示：对比 judge 与人工标注的一致率随优化轮数的变化）？

---

## 📌 下一步

Prompt 系列至此覆盖"手工技术（00-08）+ 综述地图 + 自动优化（09）"。横向：DSPy 的签名思想与 [03-结构化输出](./03-结构化输出与函数调用.md) 同源；TextGrad 的"文本反馈当梯度"会在讲透Agent 的 Self-Improvement 里再次出现（2502.16923 frontier：agent-oriented prompt design 是未开垦地）。
