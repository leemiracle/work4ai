# Neo-OS · 立场文件（POSITION）

> **版本**：v2.0（升级版——从"OS 解释器"到"通用复杂软件可解释性基础设施"）
>
> **一句话立场**：
> *"Neo-OS treats **events as first-class citizens**, maintains a **distilled system world model** as a resident component, and **formally verifies causal rules** to guarantee the soundness of every explanation — so that **any complex software** (OS, browser, compiler, game engine, GPU, database, distributed system, network stack) can be **explained in human language**, eliminating the cognitive stack between humans and the machine."*

---

## 一、问题：信息差是软件领域的根本痛点

**核心洞察**：所有有点重要的程序，最终都会成长成巨型工程，造成**领域内信息差**。

- 操作系统内核（Linux ~30M 行）
- 浏览器引擎（Blink ~800-1000 万行 + V8 ~200 万行）
- 编译器（LLVM ~1000 万行，GCC ~1500 万行）
- 游戏引擎（Unreal 数百万行，Unity 闭源）
- GPU driver（Vulkan spec 486 扩展，driver 数百万行）
- 数据库（PostgreSQL ~1.3M 行，MySQL 体量 10×）
- 分布式系统（K8s ~百万行 + etcd/TiKV/CockroachDB）
- 网络协议栈（Linux net/ 含数十子系统，TCP sysctl 80+ 参数）

**每个领域都只有少数内部人真懂，外部人被术语墙和复杂性挡住。** 这是软件工程的结构性痛点，也是创新的瓶颈——降低基础软件门槛 = 加速整个领域的创新。

---

## 二、洞察：软件栈的本质是人脑认知的 IR

软件栈的复杂度（编译器/链接器/signal handler/ext4 journaling...）本质是**人脑认知的中间表示（IR）**——因为人脑无法直接理解 CPU 事件，所以发明了层层"认知缓冲层"。

**LLM + world model 让我们可以抛弃这些 IR**，重新让事件直达人脑——这是 60 年来第一次。

**Neo-OS 的使命**：把"理解系统"的认知成本（**Cognitive Token Cost, CTC**）从"10 年专家经验 + 几天定位"降到"一句英文提问 + 几秒回答"。

---

## 三、定位：通用复杂软件可解释性基础设施

Neo-OS **不是**：
- ❌ 又一个 LLM OS（AIOS 已经在做 Agent 调度）
- ❌ 又一个 AIOps（Datadog/Dynatrace 已经在做云端事后分析）
- ❌ 又一个 observability 工具（eBPF/DTrace/OpenTelemetry 已经在做采集）

Neo-OS **是**：
- ✅ **机器执行流的实时、可证明、本机常驻的符号解释层**
- ✅ 一个**领域无关的解释内核** + 一套**可复用的接入方法论**
- ✅ 把"采集器告诉你的 *what*"升级为"**Neo 告诉你 *why*，且每句话引 spec 为证**"

**不可替代三角**（护城河）：
1. **commit-distilled 语义**（从软件历史蒸馏领域世界模型）——无人系统做过
2. **形式化可证明**（Lean4 验证的因果规则）——唯一能压过 Dynatrace 因果图
3. **系统调用级实时**（告警前行动，而非事后）——唯一在事件发生时解释

---

## 四、架构：四层 + 五原子 + 薄 adapter

### 四层技术栈

```
┌─────────────────────────────────────────────────────────┐
│ L3  English Interface（英文输出口）                       │
│     三层讲解 × 17 视角护栏 × 费曼质量门                   │
├─────────────────────────────────────────────────────────┤
│ L2.5 Formal Rule Layer（形式化规则层）★ 声音来自 seL4    │
│     Lean4 形式化的因果规则，保证 soundness                │
│     LLM 输出经规则过滤，证明不了的标"低置信度"            │
├─────────────────────────────────────────────────────────┤
│ L2  System World Model（系统世界模型层）★ 核心创新        │
│     从软件历史（commits/spec/docs）蒸馏的领域世界模型     │
│     7B 级蒸馏小模型，本机常驻，<100ms                     │
├─────────────────────────────────────────────────────────┤
│ L1  Event Ontology Layer（事件本体层）★ 声音来自 DTrace  │
│     一切都是 (event, cause) 对，LLM-friendly JSON 格式    │
│     eBPF 常态采集 + 硬件 PT/ETM snapshot 异常放大         │
├─────────────────────────────────────────────────────────┤
│ L0  Hardware（ISA / Intel PT / Arm CoreSight / NPU）     │
└─────────────────────────────────────────────────────────┘
```

### 五原子（领域无关的解释原语）

| 原子 | 回答 | 定义 |
|------|------|------|
| **Event 事件** | 发生了什么？ | 时空点上的可观测发生 + 溯源 |
| **State 状态** | 此刻在哪？ | 显式配置 + 位置 |
| **Causality 因果** | 为什么导致它？ | cause→effect 有向边 + 机制 |
| **Invariant 不变式** | 本该/本不该怎样？ | 断言 + 形式锚点 |
| **Decision Point 决策点** | 本可走另一条路？ | 分叉 + 备选项 |

**判据**：五原子定义里**不含任何 OS 概念**。引擎只针对五原子编程。

### 领域插拔 adapter（薄，~20%）

每个领域提供五件契约：`trace_source` / `ontology` / `world_corpus` / `formal_anchors` / `canonical_QA`。**adapter 只翻译，不负责任何解释逻辑**。

---

## 五、方法论内核：讲透 × trace 接地

Neo-OS 的解释引擎继承 work4ai 的"讲透"方法论：

- **三层讲解**（直觉→数学→trace 证据）——trace-native 让"代码实证层"自动化
- **17 视角护栏**——自动启发式扫描（第一性原理/布鲁姆层级/图尔敏论证/红队/系统论/...）
- **费曼质量门**（F1 外行复述 / F2 卡壳自曝 / F3 术语黑名单 / F4 回炉记录）

**关键升华**：trace 是终极 ground truth。每条解释都能被 trace 复核 → 具备**可证伪性**，区别于 LLM 的 plausible hallucination。

---

## 六、靶子领域与渐进路径

**核心纪律（刻在墙上）**：
> **"深度上专精，方法上通用。"** "通用"是挣来的结论，不是起点的口号。

**渐进路径**：
1. **Phase 0**（立项）：1000 commit 抽取率实验（命门）+ 形式化粒度种子
2. **Phase 1**（OS prototype）：Linux + eBPF，验证 trace→英文解释
3. **Phase 2**（第二靶子）：**浏览器**（验证内核领域不变性）——备选数据库查询规划器
4. **Phase 3**（扩展）：编译器 / 数据库 / 分布式 / 游戏 / GPU / 网络
5. **Phase 4**（提取）：**从两实例提取"通用框架"**（框架是提取出来的，不是设计出来的）

---

## 七、最大的风险与防线

**Top 3 死因**（来自红队）：
1. **概念核心不可证伪——"行为规则粒度"不存在**（~40%）
2. **孤儿综合征——无生态无用户**（~30%，历史上 8/8 野心项目死于此）
3. **蒸馏噪声——stochastic parrot 撞上 commit 垃圾堆**（~25%）

**Phase 0 第 4 周生死指标（必须全绿）**：
1. 1000 commit 抽取率 ≥10%，LLM precision ≥0.7
2. 产出 ≥1 条合格规则（非平凡 + 蒸馏 + 可形式化 + 有用）
3. ≥3 位真实工程师确认具体价值
4. 解释开销 <15%

**降级方案**（设计优雅降级，非孤注一掷）：形式化失败→LLM 代码考古；OS 集成失败→可观测插件；world model 失败→commit 智能产品；全失败→负面结果论文。

---

## 八、学术与生态定位

**三个 paper-grade 研究点**：
1. **Linux commit history as training corpus for system world models**（SOSP/OSDI/ACL）
2. **Neuro-symbolic trace explanation with formal soundness**（NeurIPS/NeSy/POPL）
3. **Cognitive Token Cost: democratizing complex software**（CHI/CSCW/ASPLOS）

**生态影响**：降低 kernel 贡献门槛（10× 扩大贡献者池）/ 重写 OS 教育 / 替代部分 AIOps SaaS / 给形式化方法一个杀手级应用。

**开源策略**：Apache 2.0 + 模型 CC-BY。影响力优先，非商业。

---

## 九、一句话总结

> **Neo-OS 把"可观测性"从 OS 的附加层提升为本体论根，把 work4ai 的"讲透任意领域"方法论运行时化，用 commit 蒸馏的 world model + Lean4 形式化规则 + trace-native 事件本体，把任意复杂软件的行为翻译成可证明的英文解释——目标是消灭软件领域的信息差，让基础软件创新门槛降低一个数量级。**

---

*立场版本：v2.0。下一步阅读：[DESIGN.md](./DESIGN.md)（详细架构）· [EXPANDED_KNOWLEDGE.md](../02-research/EXPANDED_KNOWLEDGE.md)（22 路探索整合）· [ROADMAP.md](./ROADMAP.md)（执行路线）· [LOCAL_ASSETS.md](../02-research/LOCAL_ASSETS.md)（本地资产索引）*
