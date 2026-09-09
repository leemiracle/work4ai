# Neo-OS · L3 English Interface（三层讲解 prototype）

> **四层架构的 L3（英文输出口）**：把 L2.5 形式化规则翻译成人类可理解的英文解释，**降低 CTC（Cognitive Token Cost）**。
>
> 继承 [work4ai 三层讲透宪法](https://gitee.com/leemiracle/work4ai)：直觉 → 数学 → 代码。Neo-OS L3 = 该方法论的**运行时化**（自动生成三层讲解）。

## 文件

| 文件 | 作用 |
|------|------|
| `l3_explain.py` | L3 prototype：规则 → GLM → 三层英文讲解 |
| `explanations.md` | 4 个 L2.5 规则的三层讲解输出（ElectionSafety/committedMono/spinlock/logMatching）|

## 三层结构（work4ai 继承）

| 层 | 内容 | ElectionSafety 示例 |
|----|------|---------------------|
| **Intuition** | 1-2 句比喻 + 为什么规则必须成立 | "两 candidate 各赢过半票必同人，否则票数超 voter 总数" |
| **Formal statement** | Lean4 不变式 + 数学含义 | `2*votesFor > length → c1=c2`（pigeonhole, 2*(n/2+1)>n）|
| **Trace evidence** | 具体 trace 示例 / 违规现象 | 3 voter 例子 + split-brain 联系 |

## 用法

```bash
# 生成所有内置规则的三层讲解
python3 .l3_explain.py

# 单个规则
python3 .l3_explain.py ElectionSafety
```

输出：`.explanations.md`（GLM-4-plus 生成）。

## 内置规则（从 L2.5 形式化层来）

| 规则 | 锚点 | Lean4 状态 |
|------|------|-----------|
| ElectionSafety | Raft §5.2 / dsyme RE5 | ✅ sorry=0（完整）|
| committedMono | Raft §5.4.2 / dsyme hcommitted_mono | ✅ sorry=0 |
| spinlockPreempt | Linux spinlocks.rst | ✅ sorry=0（C2）|
| logMatchingSingle | Raft §5.4.1 / dsyme LogMatching | ✅ 零公理 |

## Neo-OS L3 的价值（降低 CTC）

CTC（Cognitive Token Cost）= 人理解系统所需的认知资源。L3 把：
- **形式化规则**（Lean4，专家才能读）→ **三层英文讲解**（任何工程师能懂）

从"10 年 kernel 专家 + 几天定位"降到"一句英文提问 + 几秒回答"。

## 当前局限（Phase 1 prototype）

1. **GLM 生成，未接真实 trace**：Trace evidence 是 GLM 构造的示例，非 eBPF 真实 trace
2. **未做费曼质量门**：work4ai 的 F1-F4（外行复述/卡壳自曝/术语黑名单/回炉）未自动化
3. **未做 17 视角护栏**：第一性原理/布鲁姆/图尔敏等启发式扫描未实现
4. **规则集小**（4 条）：Phase 1 完整版接 DistilledRules（48 条 L2 蒸馏规则）

## Phase 1 L3 完整路线

1. 接 DistilledRules（48 条 L2 蒸馏规则）→ 批量生成三层讲解
2. 接 eBPF trace（L1）→ Trace evidence 用真实 trace 而非构造示例
3. 费曼质量门（F1-F4）+ 17 视角护栏自动化
4. CTC 度量实证（对标 Bloom 2-sigma，≥3 工程师用户研究）

---

*L3 是 Neo-OS 的用户可见层（价值层）。当前 prototype 验证 GLM 能从形式化规则生成高质量三层讲解——work4ai 方法论运行时化可行。*
