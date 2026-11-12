# 01 · Lean4 作为 RL 奖励验证器：速度可行性与工程考量

> 本章回答一个关键工程问题：**Lean4 编译速度够快吗，能塞进 RL 训练循环当 reward verifier 吗？** 这连接 [00 篇](./00-为什么形式化+Lean4SOTA.md)（Lean4 形式化）和 [`讲透RL/04`](../讲透RL/04-RL与形式证明.md)（RL 证定理）——如果 Lean4 太慢，整个"RL + 形式化"赛道在工程上不成立。本章用实测数据回答：**够快，sub-second，但有三个必须避开的陷阱**。
>
> 配套：[`讲透RL/04`](../讲透RL/04-RL与形式证明.md)（RL + 形式证明）+ [`讲透RL/05`](../讲透RL/05-RLVR的极限.md)（RL 能力边界）

---

## 一、直觉：RL reward 要多快？Lean4 有多慢？

### 1.1 RL 训练循环对 reward 的速度预算

RL 训练（尤其是 GRPO，[讲透RL/03](../讲透RL/03-RLHF-DPO-GRPO.md)）的每步要算一组（group_size=4~64）候选的 reward。整个训练循环的单步时间通常是 **30 秒到几分钟**（LLM 推理是大头）。

所以 reward 计算的**速度预算**大约是 **1-10 秒/样本**。只要 reward verifier 在这个预算内，就不会成为瓶颈。

### 1.2 Lean4 的"慢"名声从哪来

Lean4 在大众印象里"慢"，是因为：
- **Mathlib cold-start 要几十分钟**（百万定理全量编译）
- 复杂数学证明（Scholze 的 Liquid Tensor Experiment）编译要几小时

但这**不是 Lean4 作为 RL reward 的真实场景**。RL reward 验证的是**结构化小定理**（候选规则/不变式），不是 Mathlib 级别的大证明。

> 🎯 **核心问题**：对**结构化小定理（< 200 行，无 Mathlib 依赖）**，Lean4 cold-compile 到底多快？这决定了"Lean4-as-reward"路线是否工程可行。

---

## 二、实测数据：sub-second，14.9× 余量

对一组真实的形式化种子（5 个 OS 因果不变式 + 主定理 + spinlock×preempt 非平凡规则）做 cold-compile benchmark：

### 2.1 分层耗时（x86_64 + Lean 4.21.0）

| 测试项 | wall-clock（均值）| 含义 |
|--------|------------------|------|
| Python `subprocess.run` 开销 | ~1 ms | fork+exec（可忽略）|
| Lean 进程启动 | ~30 ms | `lean --version` |
| Cold compile 5 个 toy 不变式 | **223 ms** | omega-solvable 的简单不变式 |
| Cold compile 非平凡规则（spinlock×preempt）| **335 ms** | induction on trace，sorry=0，3 反例定理零公理 |
| **Batch 10 cold（GRPO group 模拟）** | **336 ms/样本** | 模拟 GRPO 一次算 10 个候选 |

### 2.2 判词

```
GRPO reward 预算  :  5.0 s/样本（保守上限）
实测（x86_64）   :  0.336 s/样本（batch 10 cold 平均）
余量             :  14.9× headroom
```

> 🎯 **结论**：**Lean4 作为 RL reward verifier 完全可行**。结构化小定理的 cold-compile 是 sub-second，远低于 GRPO 每步 reward 预算。Lean4 的"慢"名声是 Mathlib 场景的，不适用于 RL reward。

### 2.3 ARM vs x86_64

同样 Lean 4.21.0 + 同样 formal-seed：

| 测试 | aarch64 | x86_64 | 加速比 |
|------|---------|--------|--------|
| Cold compile 非平凡规则 | 706 ms | 335 ms | **2.1×** |
| Batch 10 cold | 774 ms | 336 ms | **2.3×** |

x86_64 比 ARM 快 ~2.3×。所以 **ARM 上的余量是 6.5×，x86_64 上是 14.9×**——两边都够用。

---

## 三、关键工程考量：三个必须避开的陷阱

光看速度够不够，会忽略三个真正的工程难点。

### 3.1 陷阱一：Mathlib 依赖（最致命）

**现象**：如果候选定理 `import Mathlib.XXX`，cold-compile 从 sub-second 跳到**分钟级**（Mathlib 全量编译）。

**为什么**：Lean4 的 `import` 会触发被导入模块的重新检查。Mathlib 百万定理，cold-start 几十分钟。

**对策**：
- ✅ RL reward 验证的候选定理**自包含**（只 `import Lean4 stdlib` + 项目本地模块）
- ✅ 把需要的 Mathlib 定理**拷贝**到本地（避免 import 链）
- ❌ 绝不在 reward verifier 路径上 `import Mathlib`

> 🟥 **铁律**：reward verifier 的候选定理**必须不依赖 Mathlib**。这是 sub-second 的前提。

### 3.2 陷阱二：复杂证明的编译时间会涨

当前 baseline（spinlock×preempt，induction 6 分支）是 335 ms。更复杂的并发证明（RCU、lock-free queue、内存序）可能涨到 **2-5 秒**。

**对策**：
- 限制候选定理粒度（**< 100 行 Lean4 + < 5 个 case 分支**）
- 把大证明拆成小引理，分别验证
- 对超时（> 预算）的候选直接返回 reward=0（GRPO 容忍部分样本失败）

### 3.3 陷阱三：reward signal 太稀疏

二元 reward（Lean 接受=1/拒绝=0）是**全有或全无**（[讲透RL/04 §5.1](../讲透RL/04-RL与形式证明.md)）。这导致：
- 大多数候选是错的（reward=0），梯度信号弱
- 模型学不到"接近正确"的梯度（只知道"全错"）

**对策**（研究方向）：
- **过程奖励**（[讲透RL/04](../讲透RL/04-RL与形式证明.md) 提到的 Process-Verified RL，arXiv:2606.20068）：用 Lean 做 symbolic oracle，给 first-error propagation
- **部分 credit**：解析 Lean 错误信息，给"证明了一半"的中间 reward
- **猜想池模式**（Seed-Prover heavy）：批量生成 + 逐一 prove/disprove，证成的进 lemma 库

---

## 四、公理依赖验证（soundness 的工程保证）

速度够还不够，还要保证**健全性**（soundness）——证明不能偷偷用 `sorry` 或不一致的 axiom。Lean4 提供 `#print axioms` 检查：

| 定理类型 | 依赖公理 | 健全性 |
|---------|---------|--------|
| 主定理（trace 不变式保持）| `propext, Quot.sound` | ✅ Lean 标准公理（不可避免）|
| 反例定理（必要性展示）| **无** | ✅ **零公理**（最强保证）|

**健全性 checklist**（每个 reward=1 的候选必须过）：
- [ ] `#print axioms` 仅含 `propext, Quot.sound`（Lean core）或更少
- [ ] 无 `sorry`（CI gate grep）
- [ ] 无 `admit`
- [ ] 无自定义 `axiom` 声明
- [ ] 无 `lax` 属性（防 [讲透形式化验证/00 §六](./00-为什么形式化+Lean4SOTA.md) 的 Verification Theatre）

> 📌 这与 [讲透形式化验证/00 §六](./00-为什么形式化+Lean4SOTA.md) 的"验证剧场"陷阱直接相关——reward verifier 必须**强制健全性 gate**，否则 RL 会找到钻漏洞的"假证明"（[讲透RL/04 §5.2](../讲透RL/04-RL与形式证明.md) 的 atp-checkers 398 缺陷）。

---

## 五、与 Alive2（SMT-based）的对比

"形式化验证 as RL reward"赛道有两条技术路线：

| 维度 | Lean4（type theory）| Alive2（C++，SMT-based，LLVM-VeriOpt 用）|
|------|---------------------|------------------------------------------|
| 验证目标 | 任意 Lean4 可表达的性质 | LLVM IR 等价性（同语言）|
| 表达力 | **极强**（调度/并发/协议/因果）| 受限（内存安全 + 等价性）|
| 验证速度 | sub-second（结构化小定理）| 秒级到分钟级（取决于 SMT）|
| 适合领域 | **调度/并发/协议/因果不变式** | 编译器优化（LLVM pass）|

> 🎯 **选型建议**：
> - 做 **LLVM pass 优化**（编译器域）→ Alive2（LLM-VeriOpt 路线，已占位）
> - 做 **调度/并发/协议/因果规则**（系统域）→ **Lean4 是唯一可行选项**（Alive2 表达不了）

系统域（OS / 分布式 / 协议）正是 Alive2 帮不上忙的地方——这是 Lean4-as-reward 的护城河。

---

## 六、最小可运行示例

模拟 GRPO reward 计算的真实路径：policy 生成候选定理 → Python wrapper → fork lean 子进程 → 解析 returncode → 返回 reward。

```python
import subprocess
import time
from pathlib import Path

def lean_reward(candidate_lean: str, lean_bin: str = "lean") -> float:
    """
    把候选 Lean4 代码写成临时文件，fork lean 编译，
    returncode=0 → reward=1.0（证明成立）
    returncode≠0 → reward=0.0（证明失败）
    """
    tmp = Path("/tmp/candidate.py.lean")
    tmp.write_text(candidate_lean)
    t0 = time.time()
    result = subprocess.run(
        [lean_bin, str(tmp), "-o", "/tmp/candidate.olean"],
        capture_output=True, timeout=10.0  # 硬 timeout，防 Mathlib 类 cold-start
    )
    elapsed = time.time() - t0
    return 1.0 if result.returncode == 0 else 0.0

# 测试
candidate = """
inductive Ev where | lockAcquire | lockRelease
inductive Trace : Type where | nil | cons : Ev → Trace → Trace
theorem trace_nil_is_nil : Trace.nil = Trace.nil := by rfl
"""
print(f"reward = {lean_reward(candidate)}")  # 预期 1.0，耗时 ~0.3s
```

**关键点**：
- `timeout=10.0`：硬超时，防 Mathlib 依赖的候选卡死训练循环（[§3.1](#31-陷阱一mathlib-依赖最致命)）
- `lean file.lean -o out.olean`：直接编译单文件（比 `lake build` 快，适合 reward 路径）
- 自包含（无 `import Mathlib`）

---

## 七、一句话总结

> 🎯 **三句话**：
> 1. **Lean4 作为 RL reward verifier 工程可行**：结构化小定理（< 200 行，无 Mathlib）cold-compile 是 **0.336 s/样本**（x86_64），GRPO reward 预算 5s 的 **14.9× 余量**——Lean4 的"慢"名声是 Mathlib 场景，不适用于 RL reward。
> 2. **三个陷阱**：① Mathlib 依赖（cold-start 跳到分钟级，候选必须自包含）；② 复杂证明会涨（限制 < 100 行 + < 5 case）；③ reward 太稀疏（需过程奖励/部分 credit/猜想池）。
> 3. **护城河**：Alive2（LLM-VeriOpt 路线）只做 LLVM 等价性；**调度/并发/协议/因果不变式只能用 Lean4**——这是系统域 AlphaProof 的形式化基座。

📌 **下一步**：回到 [00 篇](./00-为什么形式化+Lean4SOTA.md) 看 Lean4 基础，或去 [`讲透RL/04`](../讲透RL/04-RL与形式证明.md) 看这个 reward verifier 怎么塞进 AlphaProof 式闭环（以及为什么 RL 只能当辅助不能当引擎）。

---

## 附：关键数据来源

| 数据 | 来源 | 核实 |
|------|------|------|
| cold-compile 0.336 s/样本（x86_64）| Lean 4.21.0 toolchain 实测 | ✅ 可独立复现 |
| cold-compile 0.774 s/样本（aarch64）| Lean 4.21.0 ARM 实测 | ✅ |
| 公理依赖 `propext, Quot.sound` | `#print axioms` 输出 | ✅ Lean core |
| LLM-VeriOpt（Alive2 路线）| CGO 2026 | ⚠️ 二手（neo-os 调研引用）|
| Process-Verified RL | arXiv:2606.20068 | ✅ |
| atp-checkers（398 基准缺陷）| arXiv:2606.29493 | ✅（[讲透RL/04](../讲透RL/04-RL与形式证明.md)）|
