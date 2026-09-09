# Great Ideas in Computer Architecture：体系结构的十大思想母题

> **一句话定位**：这不是讲"CPU 是什么"，而是讲**"计算机为什么会设计成今天这样"**——
> 抽象、局部性、并行、流水线、预测、存储层次、可靠性、接口、能效、可扩展性。
> CPU 可以换、ISA 可以换、工艺可以换，但这些**思想**不会消失，因为它们是**设计哲学**，不是技术细节。
>
> **本文在项目中的位置**（思想母题层）：
>
> | 层次 | 文档 | 回答的问题 |
> |------|------|-----------|
> | **思想母题（本文）** | `Great_Ideas_体系结构思想.md` | **为什么**会有这些设计？ |
> | 实验观测层 | [`Lab00`–`Lab07`](../) | 在飞腾 D3000M 上**怎么观测**？ |
> | 专家视角层 | [`Expert_01`–`Expert_23`](../) | 不同角色**怎么看**？ |
> | 异质透镜层 | [`Lenses/Lens_01`–`Lens_09`](../Lenses/) | **换个角度**怎么看？ |
> | 事实锚点层 | [`战略锚点.md`](../战略锚点.md) | 飞腾的**核心事实**权威定义 |
>
> 本文**不重复**Lab/Expert 的细节，只做**入口索引**——每个 Great Idea 都标注"在飞腾 D3000M 上的观测入口"。
>
> **横向 × 纵向十字骨架**：本文是**横向**（十大思想贯穿所有层）；姊妹篇 [`处理器分层模型.md`](./处理器分层模型.md) 是**纵向**（从 App 一路下到硅片的 5 层抽象栈）。两文不重复——本文回答"为什么需要 Cache、流水线、预测"，姊妹篇回答"Cache 在哪一层、流水线又属于哪一层"。建议两文搭配阅读。
>
> **数字分级**（项目宪法 §4.3）：`[实测]` / `[官方]` / `[报告]` / `[推测-依据]` / `[经典理论]`

---

## 0. 为什么需要这份文档？

本项目有 8 个实验、23 个专家视角、9 个异质透镜——但这些都是**切面**，
缺少一份**母题层**回答："这些切面所指向的体系结构思想，**从哪里来、为什么存在、为什么不会消失**？"

本文用 **5H3W 分析法**（What/Why/Who/When/Where/How/Which/Whom）梳理十大 Great Ideas，
并以 Patterson & Hennessy《Computer Architecture: A Quantitative Approach》
与《计算机组成与设计》的经典八大思想为骨架，扩展为**十大**（加入 Interface、Energy First、Scalability）。

---

## 1. 5H3W 全局分析

### ① What（是什么）

研究对象 = Computer Architecture 的**核心思想**：

```
Computer Architecture
├── 指令集（ISA）           ── Abstraction + Interface
├── CPU 设计                ── Pipelining + Prediction + Parallelism
├── Memory                  ── Memory Hierarchy
├── Cache                   ── Locality
├── Pipeline                ── Pipelining
├── Parallelism             ── Parallelism
├── IO                      ── Dependability + Interface
├── Virtual Memory          ─── Locality + Abstraction
├── GPU / DSA               ── Parallelism + Energy First
└── Distributed / Cloud     ── Scalability + Dependability
```

**作者真正想讲的不是"它们怎么实现"，而是"它们为什么会出现"。**

#### 核心 Great Ideas（十大）

| # | Great Idea | 一句话本质 |
|---|-----------|-----------|
| 1 | **Abstraction（抽象）** | 分层隐藏复杂度，让上层不用懂下层 |
| 2 | **Locality（局部性）** | 程序访问有规律，使 Cache 成为可能 |
| 3 | **Parallelism（并行）** | 频率上不去，就用多核/SIMD/GPU |
| 4 | **Pipelining（流水线）** | 不让任何一拍空闲，提高吞吐量 |
| 5 | **Prediction（预测）** | 不等条件算完，先猜先做 |
| 6 | **Memory Hierarchy（存储层次）** | 速度与容量不可兼得，就分层 |
| 7 | **Dependability（可靠性）** | 硬件会出错，要能检测、纠正、恢复 |
| 8 | **Interface（接口）** | ISA 不变，让软硬解耦演进 |
| 9 | **Energy First（能效优先）** | 功耗墙之后，每瓦性能比峰值性能重要 |
| 10 | **Scalability（可扩展性）** | 单核到多核到 Chiplet 到集群的演进逻辑 |

> **来源**：前 8 条源自 Patterson & Hennessy《计算机组成与设计》经典八大思想；
> 第 9–10 条是 2010 年后（功耗墙、多核时代、Chiplet、WSC）的扩展，本项目补入。

---

### ② Why（为什么需要这些思想）

因为计算机一直面临**三个永恒矛盾**：

#### 矛盾 1：CPU 与内存的速度鸿沟（→ Locality + Memory Hierarchy）

```
CPU 寄存器访问    ~ 0.3 ns
L1 Cache          ~ 1   ns
L2 Cache          ~ 4   ns
L3 Cache          ~ 12  ns
DRAM              ~ 60  ns        ← 比 CPU 慢 200×
SSD               ~ 100,000 ns
```

**飞腾 D3000M 实测拓扑**（`[实测 Lab03]`）：

- 每核：L1-I 64KB + L1-D 64KB + L2 512KB（私有）
- 每簇（4 核）：L3 4MB（共享）
- 全片（8 核）：L4 8MB 系统缓存（最后一级）

**→ 这个矛盾催生了 Locality 与 Memory Hierarchy 两大思想。**

#### 矛盾 2：频率墙（→ Parallelism + Energy First）

```
更多晶体管 → 更高频率 → 更大功耗 → 散热失败
（Dennard Scaling 在 2005 年前后失效）
```

**于是**：单核频率停在 4–5 GHz 已十多年，性能提升靠**多核 / SIMD / GPU / DSA**。

**→ Parallelism 与 Energy First 成为后频率时代的主旋律。**

#### 矛盾 3：复杂度爆炸（→ Abstraction + Interface + Prediction）

CPU 已有数百亿晶体管，没有任何一个工程师能全局理解。
**于是**：分层抽象、稳定 ISA、靠预测应对未知分支。

**→ Abstraction / Interface / Prediction 三大思想应对复杂度。**

> **核心论断**：Great Ideas 本质 = **解决计算机发展过程中不断涌现的瓶颈**。`[经典理论]`

---

### ③ Who（谁提出的）

不是一个人，而是**几十年集体智慧的结晶**：

| 人物 | 贡献 | 影响 |
|------|------|------|
| **Moore** | Moore's Law | 整个半导体工业的节奏律 |
| **John Hennessy** | RISC、MIPS、Quantitative Methodology | 现代 CPU 方法论奠基者 |
| **David Patterson** | RISC、Cache、RAID、RISC-V | 同上，并与 Hennessy 共获 2017 图灵奖 |
| **Robert Tomasulo** | 动态调度算法 | 乱序执行的鼻祖（IBM 360/91，1967） |
| **Michael Flynn** | Flynn 分类（SISD/SIMD/MISD/MIMD） | 并行体系结构的术语体系 |
| **Gene Amdahl** | Amdahl 定律 | 并行加速比上限 |
| **Robert Dennard** | Dennard Scaling | 解释了频率墙为何出现 |
| **Jack Kilby / Robert Noyce** | 集成电路发明 | 所有体系结构思想的物理载体 |
| **Tse-Yu Feng** | 并行处理分类 | 早期并行理论 |

> 详见 [`View_04_History`](../View_04_History/) 与 [`Lenses/Lens_01_Historian`](../Lenses/Lens_01_Historian.md)。

---

### ④ When（时间线）

```
1940s  真空管              ENIAC、EDVAC
1950s  晶体管             晶体管取代真空管
1960s  IC                  Kilby/Noyce；Tomasulo 算法（1967）
1970s  Cache/Pipeline/VM   IBM 360/91；Intel 4004、8086
1980s  RISC                Hennessy MIPS / Patterson RISC I/II / Berkeley
1990s  Superscalar/OoO     Pentium Pro、Alpha 21164/21264
2000s  Multicore           Dennard Scaling 失效；Core 2 Duo（2006）
2010s  GPU/AI              CUDA、TPU（2017）、Apple Neural Engine
2020s  Chiplet/RISC-V/AI   Apple M1（2020）、UCIe、域专用加速器
```

**飞腾 D3000M 在时间线上的位置**（`[报告]`）：ARMv8.4-A 基座、14nm 工艺、4-wide 乱序超标量——
相当于 2014–2016 年的国际主流水平（对标 Cortex-A76/A77）。

---

### ⑤ Where（在哪里使用）

**几乎所有计算设备**：

```
通用 CPU：Intel / AMD / ARM / Apple M / 飞腾 / 鲲鹏 / 龙芯 / RISC-V
GPU    ：NVIDIA / AMD / Intel / 华为昇腾 / 寒武纪 / 壁仞 / 海光 DCU
AI DSA ：Google TPU / Apple Neural Engine / 各种 NPU
嵌入式 ：SSD 控制器 / 路由器 / NIC / DSP / 智能手机基带
```

> **核心论断**：Great Ideas 是**跨厂商、跨 ISA、跨时代**的通用设计哲学。`[经典理论]`

---

## 2. How：十大 Great Ideas 详解

> 每条结构：**本质 → 为什么需要 → 费曼比喻 → 🔗 在飞腾 D3000M 上哪里观测 → 项目资源索引**

### Great Idea 1：Abstraction（抽象）

**本质**：分层隐藏复杂度。

**为什么需要**：如果程序员面对的是晶体管，几乎没人能写程序。

**层次**：
```
Application
   ↓
Library / Runtime
   ↓
Operating System
   ↓
ISA（指令集架构）          ← 软硬件的"合同"
   ↓
Microarchitecture（微架构）  ← CPU 设计师的地盘
   ↓
Logic / Circuit
   ↓
Transistor / Device
```
每层只关心自己的接口。

**费曼比喻**：开车——司机用方向盘，不必懂活塞、燃烧、气缸。
程序员用 `printf`，不必懂晶体管。

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Lab01_ISA`](../Lab01_ISA与汇编/)：直接面对 ISA 这一层——汇编就是"抽象的接口"
- [`Expert_02_Architect`](../Expert_02_Architect/)：从微架构往下看，理解 ISA 与 Microarchitecture 的分离
- [`战略锚点.md §锚点1`](../战略锚点.md)：BF16/I8MM/SVE 缺失 = ISA 这层"合同"决定了上层能做什么

---

### Great Idea 2：Locality（局部性）

**本质**：程序对存储的访问**不是随机的**。

**两种局部性**：
- **空间局部性**（Spatial）：访问 `A[0]` 后，大概率很快访问 `A[1]`、`A[2]`
- **时间局部性**（Temporal）：访问 `A[0]` 后，大概率很快**再次**访问 `A[0]`

```c
// 空间局部性
for (int i = 0; i < 100; i++) sum += A[i];   // 顺序访问

// 时间局部性
sum += A[0]; sum += A[0]; sum += A[0];        // 重复访问
```

**为什么有用**：使 Cache 命中率极高（典型 > 95%），从而让 Memory Hierarchy 成立。

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Lab03_存储层次`](../Lab03_存储层次/)：用 `L1D_CACHE_REFILL (0x03)` 等 PMU 事件实测 Cache 命中率
- [`背景知识/概念.md`](./概念.md)：缓存组相联（Set-Associative）、Way、Set 的定义

---

### Great Idea 3：Parallelism（并行）

**本质**：用"同时做多个"代替"做得更快"。

**Flynn 四分类**：
```
SISD  单指令单数据   ── 传统标量 CPU
SIMD  单指令多数据   ── 向量指令、GPU、NEON
MISD  多指令单数据   ── 罕见（容错系统）
MIMD  多指令多数据   ── 多核、多机
```

**演进逻辑**：
```
频率++（2005 年前）
   ↓ Dennard Scaling 失效
多核（2006 至今）
   ↓
SIMD 宽度++（AVX-512、SVE、NEON）
   ↓
GPU（数千核心）
   ↓
DSA（TPU、NPU、昇腾）
```

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Lab05_并行与SIMD`](../Lab05_并行与SIMD/)：用 `ASE_SPEC / NEON (0x74)` 实测 SIMD 指令执行数
- [`Expert_10_Distributed`](../Expert_10_Distributed/)：从单机并行扩展到分布式并行
- [`Expert_21_AI_Positioning`](../Expert_21_AI_Positioning/)：D3000M 在并行算力上的定位（无 SVE/BF16）

---

### Great Idea 4：Pipelining（流水线）

**本质**：把一条指令的执行切成多段，**让多段同时进行**，提高吞吐量。

**经典五级流水线**：
```
IF → ID → EX → MEM → WB
取指   译码   执行   访存   写回
```

不是"做得更快"，而是"**一次做好几条**"。

**费曼比喻**（洗衣店）：
```
不做流水线：
  衣服1: 洗→烘→脱水
  衣服2:                          洗→烘→脱水

做流水线：
  衣服1: 洗  烘  脱水
  衣服2:     洗  烘  脱水
  衣服3:         洗  烘  脱水
                                  ↑ 吞吐量 ×3
```

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Lab02_流水线与ILP`](../Lab02_流水线与ILP/)：实测流水线停顿（`STALL_FRONTEND (0x23)` / `STALL_BACKEND (0x24)`）
- [`背景知识/概念.md`](./概念.md)："指令流水线"定义
- [`Capstone/alpha_21264_study`](../Capstone/alpha_21264_study/)：经典 7 级流水线深度案例

---

### Great Idea 5：Prediction（预测）

**本质**：分支结果未知时，**先猜先做**，猜对就赚时间，猜错就回滚。

**为什么需要**：
```c
if (cond) { /* CPU 不知道 cond，但要等就浪费时间 */ }
```

**现代 CPU 分支预测准确率**：**95%+** `[经典理论]`

**衍伸**：
- Branch Prediction（分支预测）
- Value Prediction（值预测）
- Memory Disambiguation（访存歧义预测）
- Speculation（投机执行，**Spectre/Meltdown 的根源**）

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Lab02_流水线与ILP`](../Lab02_流水线与ILP/)：用 `BR_MIS_PRED (0x10)` / `BR_PRED (0x12)` 实测准确率
- [`Expert_12_Security_CISO`](../Expert_12_Security_CISO/)：投机执行的安全副作用（Spectre v1/v2）
- [`背景知识/概念.md`](./概念.md)：分支预测器与寄存器重命名如何让 RAW 链变成 1 cycle

---

### Great Idea 6：Memory Hierarchy（存储层次）

**本质**：速度与容量不可兼得，**只能分层**。

```
容量↑                              延迟↑
─────────────────────────────────────────────
Register  < L1 < L2 < L3 < DRAM < SSD < Disk/HDD
~1B         ~64K  ~512K  ~数M   ~数G   ~数百G ~数T
<1ns        ~1ns  ~4ns   ~12ns  ~60ns  ~100μs ~10ms
─────────────────────────────────────────────
速度↑                              容量↑
```

**金子塔结构**：越上越快越小，越下越慢越大。

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Lab03_存储层次`](../Lab03_存储层次/)：完整的多级缓存实测
- [`Lab06_内存模型与并发`](../Lab06_内存模型与并发/)：存储层次与内存一致性模型的相互作用
- [`战略锚点.md`](../战略锚点.md)：D3000M 的 L1/L2/L3/L4 拓扑权威定义

---

### Great Idea 7：Dependability（可靠性）

**本质**：硬件会出错（宇宙射线、工艺缺陷、老化），系统要能**检测、纠正、恢复**。

**关键技术**：
- **Parity / ECC**：内存单 bit 错误纠正
- **RAID**：磁盘冗余阵列
- **Checkpoint / Recovery**：周期性保存状态
- **RAS**（Reliability/Availability/Serviceability）：服务器级容错

**为什么对 AI 集群尤其重要**：一个 bit 翻转可能让**几个月的训练白费** `[推测-依据]`。

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Expert_23_Server_RAS`](../Expert_23_Server_RAS/)：服务器级 RAS 视角
- [`Lab07_密码学专题`](../Lab07_密码学专题/)：完整性、防篡改（可靠性的安全侧面）
- [`战略锚点.md §锚点2`](../战略锚点.md)：国密 SM3/SM4 入 ARMv8.4 的合规链

---

### Great Idea 8：Interface（接口 / ISA 稳定性）

**本质**：**ISA 是软硬件之间的"合同"**——一旦定义，硬件可以随便改，软件不用改。

**为什么 ISA 能几十年不变**：
- ARMv8（2011 发布）→ 同一份 ISA 由 Apple、Qualcomm、Samsung、飞腾**各自实现完全不同**的 CPU
- 软件二进制兼容 → 生态可累积

**费曼比喻**：标准插座——不同品牌电器都能用同一种供电标准。

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Lab01_ISA与汇编`](../Lab01_ISA与汇编/)：直接面对 ARMv8-A 这份"合同"
- [`Expert_06_Standards_Policy`](../Expert_06_Standards_Policy/)：ISA 标准的博弈过程
- [`战略锚点.md §锚点5`](../战略锚点.md)：ARM v9 不授中国厂商 → ISA 这份"合同"的地缘约束

---

### Great Idea 9：Energy First（能效优先）

**本质**：后频率墙时代，**Performance/Watt（每瓦性能）** 比峰值性能更重要。

**驱动因素**：
- 数据中心电费 = OPEX 大头
- 移动设备电池续航 = 用户体验底线
- 摩尔定律变慢，每晶体管能效不再免费提升

**代表**：Apple M 系列、GPU、TPU、各种 DSA——都在 Performance/Watt 上做文章。

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Expert_20_Green_Compute`](../Expert_20_Green_Compute/)：绿色计算视角
- [`Expert_21_AI_Positioning`](../Expert_21_AI_Positioning/)：D3000M 在 Performance/Watt 上的定位
- [`Lab00_测量基础设施`](../Lab00_测量基础设施/)：功耗测量基础设施

---

### Great Idea 10：Scalability（可扩展性）

**本质**：单点算力有上限，性能提升靠**横向扩展**。

**演进**：
```
单核 → 多核 → 多 socket → NUMA → Chiplet → 机柜 → WSC（仓库级计算机）
                                                    ↑
                                          Hennessy & Patterson CAQA Ch6/Ch10
```

**Amdahl 定律的约束**：加速比受**串行部分**限制。
**Gustafson 定律的反驳**：问题规模随并行度增加时，可突破 Amdahl 上限。

**🔗 在飞腾 D3000M 上哪里观测**：
- [`Expert_15_Package_Chiplet`](../Expert_15_Package_Chiplet/)：Chiplet 视角
- [`Expert_10_Distributed`](../Expert_10_Distributed/)：分布式扩展
- [`Capstone/workload_characterization`](../Capstone/workload_characterization/)：WSC 视角的工作负载分析

---

## 3. Which：十大 Great Ideas × 项目资源映射表

| # | Great Idea | 解决的矛盾 | 代表技术 | Lab 观测入口 | Expert 视角 | Lens 透镜 |
|---|-----------|-----------|---------|-------------|------------|----------|
| 1 | **Abstraction** | 复杂度 | ISA、OS、API | Lab01 | E02 架构 / E04 OS | — |
| 2 | **Locality** | CPU–内存鸿沟 | Cache | Lab03 | — | — |
| 3 | **Parallelism** | 频率墙 | 多核、SIMD、GPU | Lab05 | E10 分布式 | — |
| 4 | **Pipelining** | 吞吐量 | 五级流水、超流水 | Lab02 | — | — |
| 5 | **Prediction** | 分支停顿 | Branch Predictor、Speculation | Lab02 | E12 安全 | — |
| 6 | **Memory Hierarchy** | 容量–速度矛盾 | Register/L1/L2/L3/DRAM | Lab03 + Lab06 | — | — |
| 7 | **Dependability** | 错误恢复 | ECC、RAID、Checkpoint | Lab07 | E23 RAS | — |
| 8 | **Interface** | 兼容性 | ISA、ABI、PCIe | Lab01 | E06 标准 | — |
| 9 | **Energy First** | 功耗墙 | DVFS、DSA | Lab00 | E20 绿色 | — |
| 10 | **Scalability** | 系统增长 | Chiplet、NUMA、WSC | Capstone | E15 Chiplet / E10 分布式 | Lens_05 Futurist |

---

## 4. Whom：不同角色关注哪些 Great Ideas

| 角色 | 最重要的 Great Ideas | 项目入口 |
|------|---------------------|---------|
| **应用开发** | Abstraction、Interface、Locality | [Expert_01](../Expert_01_Scientist/) |
| **编译器工程师** | Interface（ISA）、Pipelining、Prediction | [Expert_11](../Expert_11_Compiler_Research/) / [View_01](../View_01_Compiler/) |
| **OS 工程师** | Memory Hierarchy、虚拟内存、缓存一致性 | [Expert_04](../Expert_04_OS_Kernel/) |
| **CPU 架构师** | Pipelining、OoO、Branch Pred、Cache | [Expert_02](../Expert_02_Architect/) / [Lab02](../Lab02_流水线与ILP/) / [Lab04](../Lab04_超标量乱序/) |
| **GPU/NPU 架构师** | Parallelism、Memory Hierarchy、Energy | [Expert_21](../Expert_21_AI_Positioning/) |
| **AI 系统工程师** | Parallelism、带宽、能耗、DSA | [Expert_05](../Expert_05_AI_Inference/) / [Expert_21](../Expert_21_AI_Positioning/) |
| **HPC 工程师** | NUMA、缓存一致性、互连 | [Expert_10](../Expert_10_Distributed/) |
| **安全工程师** | Prediction（Speculation）、Dependability | [Expert_12](../Expert_12_Security_CISO/) / [View_02](../View_02_Security/) |

---

## 5. 费曼学习法总结：把计算机想象成一家大型工厂

| Great Idea | 工厂比喻 |
|-----------|---------|
| **Abstraction** | 公司分部门，每人只完成自己的职责，不必了解整个公司 |
| **Pipelining** | 汽车装配线，不是一辆装完再装下一辆，而是多工位同时作业 |
| **Parallelism** | 增加多条生产线，让多件产品同时制造 |
| **Locality** | 把常用工具放在工位旁，而不是每次跑仓库拿 |
| **Prediction** | 根据订单趋势提前备料，大多数时候省时间，偶尔备错也值得 |
| **Memory Hierarchy** | 办公桌、文件柜、仓库三级存储，越近越快但越小 |
| **Dependability** | 质量检测和备份系统，故障时能发现、纠正、恢复 |
| **Interface** | 标准插座，不同品牌电器都能用同一种供电标准 |
| **Energy First** | 不仅追求产量，还追求单位电费能产更多 |
| **Scalability** | 从单厂到连锁到跨国集团，靠标准化流程横向扩张 |

**最终**，这十大思想共同服务于计算机体系结构的**四个永恒目标**：

```
1. 更快（Performance）    ── Pipelining + Parallelism + Prediction
2. 更省（Energy Eff.）    ── Energy First + DSA
3. 更可靠（Dependability）── ECC + 容错 + 恢复
4. 更易扩展（Scalability）── Abstraction + Interface + Memory Hierarchy + Multicore
```

理解了这些思想，再学习 MIPS / RISC-V / ARM / x86 / 超标量 / 乱序 / GPU / TPU 时，
就能看清它们**本质上都是这些核心思想在不同时代、不同约束下的具体实现**。

---

## 6. 学习路径建议（按角色）

### 🎓 学生入门路线（无体系结构背景）

```
Step 1  读本文 §5（费曼比喻）建立直觉
   ↓
Step 2  [Lab00]  学会"度量衡"（Iron Law / Amdahl）
   ↓
Step 3  [Lab01]  面对 ISA 这份"合同"（Abstraction + Interface）
   ↓
Step 4  [Lab02]  观测流水线与分支预测（Pipelining + Prediction）
   ↓
Step 5  [Lab03]  观测 Cache（Locality + Memory Hierarchy）
   ↓
Step 6  [Lab05]  观测 SIMD（Parallelism）
   ↓
Step 7  按兴趣选 Expert 深入某一视角
```

### 👨‍💻 工程师路线（有系统/编译经验）

```
Step 1  读本文 §2（十大思想）建立全局观
   ↓
Step 2  [Expert_11 编译] → [Expert_04 OS]（编译+OS 视角）
   ↓
Step 3  [Lab04 超标量乱序]（最硬核的微架构）
   ↓
Step 4  [Expert_02 架构师]（融会贯通）
```

### 🔬 研究者路线（想做体系结构研究）

```
Step 1  读本文 §1.④（时间线）+ §1.③（Who）
   ↓
Step 2  [Lens_01 Historian] + [Lens_05 Futurist]（历史与未来）
   ↓
Step 3  [Capstone/alpha_21264_study]（经典论文精读）
   ↓
Step 4  [Lens_02 Christensen]（颠覆性创新视角）
   ↓
Step 5  锁定研究方向（DSA / Chiplet / RISC-V / 安全 / 可靠性）
```

### 🤔 想破思维定式

直接进 [`Lenses/`](../Lenses/)——9 个异质思维透镜会让你**重新看体系结构**。

---

## 附录 A：5H3W 分析法本身

本文用 **5H3W**（What/Why/Who/When/Where/How/Which/Whom）梳理一个主题。
它比传统的 5W1H（What/Why/Who/When/Where/How）多了两个维度：

- **Which**：有哪些具体技术/分类（用于系统化枚举）
- **Whom**：对不同角色意味着什么（用于多视角分析）

这恰好**与本项目的方法论同构**：
- `Which` ↔ Lab/Expert 的系统化枚举
- `Whom` ↔ Expert_01–23 的多角色分工

> **元启示**：体系结构的思想可以用 5H3W 拆解，**学习体系结构的过程**也可以用 5H3W 拆解。

---

## 附录 B：参考来源

| 来源 | 角色 | 备注 |
|------|------|------|
| Patterson & Hennessy《计算机组成与设计：硬件/软件接口 RISC-V 版》第 2 版 | 经典八大思想的来源 | `[经典理论]` |
| Hennessy & Patterson《Computer Architecture: A Quantitative Approach》第 5 版 | 量化方法论 + WSC + 多核 | `[经典理论]` |
| 姚永斌《超标量处理器设计》 | 中文 CPU 设计圣经 | `[经典理论]` |
| [View_04_History](../View_04_History/) | 历史脉络细节 | 本项目 |
| [Lenses/Lens_01_Historian](../Lenses/Lens_01_Historian.md) | 历史学家视角 | 本项目 |
| 飞腾 D3000M 实测数据 | 全文 `[实测]` 标记的来源 | Lab00–Lab07 |

---

**最后**：本文是**思想母题层**，回答"为什么"。
"**在飞腾 D3000M 上怎么观测**" → 进 [Lab00–Lab07](../)。
"**不同角色怎么看**" → 进 [Expert_01–23](../)。
"**换个角度怎么看**" → 进 [Lenses/](../Lenses/)。
