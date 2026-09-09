# Lab00 — 测量基础设施

> "你必须先有度量衡，才能做实验。"
>
> —— 这是 CAQA 第 1 章的核心哲学：**Quantitative Approach**

---

## 0. 学习目标（一句话）

**用一手测量回答：我的飞腾 D3000 到底有多快？每个细节长什么样？** 学完你将拥有：
- 一份**实测的飞腾硬件参数表**（不抄手册）
- 一个**可信的微基准测试框架**（后续每个 Lab 都用）
- 对 **Iron Law**（CPU 时间 = IC × CPI × T）和 **Amdahl/Gustafson** 的实证理解

---

## 🎯 已实测的关键发现（2026-06-29，飞腾 D3000M / FTC862 @ 2.5 GHz）

### 硬件实测参数
| 项目 | 实测值 | 与手册/旧报告对比 |
|------|--------|-------------------|
| Implementer / Part | 0x70 / 0x862 (Phytium FTC862) | ✓ |
| 核数 / 频率 | 8 核 / 2500 MHz（performance governor）| ✓ |
| L1 D-Cache | 64 KB, 4-way, 64B line, 256 sets | ✓ |
| **L2 Cache** | **512 KB, 8-way, 1024 sets** | ⚠️ **与 MIT6_172 报告里"1MB"不一致** |
| L3-1 | 4 MB, 16-way（核 0-3 共享） | 新发现 |
| L3-2 | 8 MB, 16-way（核 0-7 共享） | 新发现 |

### 微架构性能实测（null_loop）
| 工作负载 | ns/iter | cyc/iter | IPC | 含义 |
|---------|---------|---------|------|------|
| loop_empty (-O2 DCE) | 0.00 | 0.00 | 0.60 | 编译器部分消除循环 |
| **loop_volatile** | **0.40** | **1.00** | **4.00** | **飞腾是 4-wide 超标量！** |
| loop_nop | 0.47 | 1.17 | 3.42 | 接近 4，受分支指令拖累 |
| loop_add (ALU) | 0.80 | 2.00 | 2.00 | **ALU 端口限制**：每周期最多 2 条 |

### 工作负载 IPC 谱（iron_law）
| 工作负载 | IPC | CPI | 解读 |
|---------|-----|-----|------|
| array_sum | **2.00** | 0.50 | NEON 自动向量化（每周期 1 load + 1 fadd）|
| linked_list | **0.01** | 107.5 | **依赖链 + L1 miss**：每次访存拖 100+ cycles |
| branchy_random | 3.04 | 0.33 | 飞腾推测执行即使分支随机也能保持高 IPC |
| branchy_predict | **3.99** | 0.25 | 接近 4-wide 完美（理论极限）|

### Iron Law 验证（理论 cycles × τ vs 实测时间）
| 工作负载 | T_pred (us) | T_med (us) | 误差 |
|---------|-------------|-----------|------|
| array_sum | 801.2 | 802.1 | **0.1%** ✓ |
| linked_list | 79184.6 | 80573.2 | 1.7% ✓ |
| branchy_random | 1052.8 | 1055.9 | **0.3%** ✓ |
| branchy_predict | 802.0 | 805.3 | 0.4% ✓ |

**Iron Law 误差 < 2%，证明我们的 PMU 测量是可信的。**

---

## ⚠️ 飞腾/麒麟内核 PMU 适配坑（实测得到的，必读）

飞腾/麒麟内核（5.4.18-125-generic）有几个非标准行为，否则 `perf_event_open` 直接返回 `ENOTSUP`：

### 1. `CONFIG_SECURITY_PERF_EVENTS_RESTRICT=y`
- 编译时硬限制，普通 `perf_event_open()` 在某些 attr 配置下被拒
- 但 `perf stat` 命令行能工作（perf 工具内部用更宽松的 attr）
- **不影响实验**：调整 attr 后用户态可正常调用

### 2. **`exclude_idle=1` 在 attach-to-task 模式下被拒绝**
- 标准 man page 说这个字段合法
- 但飞腾 5.4 内核在 `pid>=0, cpu=-1` 模式下接受 `exclude_idle=1` 会返回 ENOTSUP
- **解决方案**：见 [`common/pmu.h`](../common/pmu.h)，不设 `exclude_idle`

### 3. PERF_COUNT_HW_BRANCH_INSTRUCTIONS 在飞腾 PMU 里没映射
- 但 `BR_PRED`(0x12) raw 事件工作正常
- 用 `pmu_add_raw(&g, FTC_BR_PRED, "br_pred")` 替代

### 4. GENERIC 事件可用性（实测）
| 事件 | 是否可用 | 备注 |
|------|---------|------|
| `PERF_COUNT_HW_CPU_CYCLES` | ✓ | |
| `PERF_COUNT_HW_INSTRUCTIONS` | ✓ | |
| `PERF_COUNT_HW_CACHE_REFERENCES` | ✓ | |
| `PERF_COUNT_HW_CACHE_MISSES` | ✓ | |
| `PERF_COUNT_HW_BRANCH_INSTRUCTIONS` | ✗ | 用 raw `BR_PRED` |
| `PERF_COUNT_HW_BRANCH_MISSES` | ✓ | |
| raw `L1D_CACHE_REFILL` (0x03) | ✓ | |
| raw `L2D_CACHE_REFILL` (0x17) | ✓ | |
| raw `BR_MIS_PRED` (0x10) | ✓ | |
| raw `STALL_FRONTEND` (0x23) | ✓ | |
| raw `STALL_BACKEND` (0x24) | ✓ | |
| raw `ASE_SPEC` (0x74, NEON) | ✓ | |


---

## 1. 对应教材与课程

| 来源 | 章节 | 重点 |
|------|------|------|
| 📘 Patterson RISC-V | **Ch1 (Performance)** | CPI 公式、Amdahl、Iron Law、bench 陷阱 |
| 📗 CAQA 5th | **Ch1 (Fundamentals of Quantitative Design)** | 量化方法论的奠基章，必读 |
| 📗 CAQA 5th | **App B / Fallacies & Pitfalls** | "Wrong Data" 经典陷阱 |
| 🎓 CSAPP | **Ch8.1 之外** | 计时 API |
| 经典论文 | **Mytkowicz 2009, "Producing Wrong Data..."** | ASPLOS 经典，强烈推荐 |

---

## 2. 核心概念速览

### 2.1 直觉：为什么先要 Lab00？

> 我第一次给一个工作做"性能优化"，跑了 5 次取均值，结果优化后比优化前还慢 30%。
> 后来才发现：CPU 频率在 1.2-2.6 GHz 之间漂移，我的"测量"测的是 DVFS 状态而非代码。
> ——CAQA 引用的真实故事

**没有测准就没有结论**。这是 Lab00 的全部存在意义。

### 2.2 数学：三大铁律

#### **Iron Law of Performance**（性能铁律）

$$
\text{CPU Time} = \frac{\text{Instructions}}{\text{Program}} \times \frac{\text{Cycles}}{\text{Instruction}} \times \frac{\text{Seconds}}{\text{Cycle}}
$$

简写：$\text{Time} = \text{IC} \times \text{CPI} \times \tau$

- $\text{IC}$ = Instruction Count（指令数）
- $\text{CPI}$ = Cycles Per Instruction（每条指令平均周期）
- $\tau$ = 时钟周期长度（秒）= 1 / 频率

**任何性能优化本质上只能影响这三个量之一**：
- 减少 IC：算法选择、消除冗余指令
- 降低 CPI：提高 ILP、改善访存、降低分支预测失败
- 减小 $\tau$：提频率（硬件）

#### **Amdahl 定律**（串行部分的瓶颈）

$$
S_{\text{total}}(N) = \frac{1}{(1-p) + \frac{p}{N}}
$$

- $p$ = 可并行部分占比
- $N$ = 处理器数

**即使 $N \to \infty$，加速比上限也只有 $1/(1-p)$**。这是 4 实验 4 的"心脏杀手"。

#### **Gustafson-Barlasis 定律**（修正）

$$
S_{\text{total}}(N) = N - \alpha(N-1)
$$

Amdahl 假设**问题规模固定**，Gustafson 假设**问题规模随 N 扩大**。两者都对，但适用场景不同。

### 2.3 一张图：测量流程

```
┌──────────────────────────────────────────────────────┐
│  实验:                                                │
│   warmup (3-5 次, 预热 Cache/分支预测器/TLB)         │
│        ↓                                              │
│   for i in 0..N:                                      │
│     ┌── pmu_start() ────────────────────────────┐    │
│     │   t0 = now_ns()                            │    │
│     │   /* 被测代码 hot loop */                  │    │
│     │   t1 = now_ns()                            │    │
│     └── pmu_stop() ─────────────────────────────┘    │
│        ↓                                              │
│   中位数 + 标准差                                      │
└──────────────────────────────────────────────────────┘
```

---

## 3. 实验列表

### 3.1 实验 0.1：架构探测（`arch_probe.c`）

**现象**：手册上写的 L2 = 1MB，但 `lscpu` / `cacheinfo` 怎么说？PMU 支持哪些事件？

**假设**（先写）：
- L1 D-cache 是 64 KB，4-way，64B 行 → 我预计访问 64KB 数组刚好不溢出
- L2 是 1MB 私有，比典型 Intel 的 256 KB 大
- L3 是 8 MB 共享
- 飞腾 PMU 支持 ~80 个 raw 事件（参考 PhyTune 模板）

**运行**：
```bash
make arch_probe
./arch_probe
```

**预期输出**（你的飞腾实测，可能略有差异）：
```
== CPU ==
model: FTC862 (Phytium D3000M)
cores: 8 physical
freq_cur: 2500 MHz
freq_max: 2500 MHz

== Caches ==
L1d: size=64K  ways=4  line=64  sets=256   (private, per-core)
L1i: size=64K  ways=4  line=64  sets=256   (private, per-core)
L2:  size=512K ways=8  line=64  sets=1024  (private, per-core)
L3:  size=4M(核0-3)+8M(核0-7) 分级        (shared, partitioned)

== NUMA ==
nodes: 1
node0 cpus: 0-7
node0 memory: 64 GB

== PMU sanity ==
PERF_COUNT_HW_CPU_CYCLES:     OK
PERF_COUNT_HW_INSTRUCTIONS:   OK
PERF_COUNT_HW_CACHE_MISSES:   OK
PERF_COUNT_HW_BRANCH_MISSES:  OK
RAW(0x03 L1D_REFILL):         OK
RAW(0x10 BR_MIS_PRED):        OK
```

**解释**：
- L2 = 512KB（实测，非手册标的 1MB），分块矩阵乘法的"内层块"需相应缩小（128×128 双精度 ≈ 128 KB 更稳妥）
- L3 共享，多核实验时要注意 cache contention

**缺陷与陷阱**：
- `sysfs` 显示的 L3 大小可能是"所有核聚合后"的（32M = 4 个 8M slice 拼接）
- "private" 不代表"物理独占"——共享 L3 的核可能互相驱逐 L3 数据

**扩展思考**：
- 不同核的 cache info 可能不同（异构）。写循环扫 0..N-1 验证。

---

### 3.2 实验 0.2：空循环的代价（`null_loop.c`）

**现象**：一段"什么都不做"的循环，每条指令究竟消耗多少 cycles？

**假设**（先写）：
- `for (i=0; i<N; i++) {}` 在 `-O0` 下应该是 N 条 `add`+`cmp`+`b` ≈ 3N 条指令
- 在 `-O2` 下，编译器可能直接消除循环（因为无副作用）
- 加 `volatile` 后，每次循环应该消耗 1-3 cycles

**关键代码**：
```c
volatile uint64_t sink_var;
#define ESCAPE() (sink_var = sink_var + 1)

for (uint64_t i = 0; i < N; i++) {
    ESCAPE();   // 防止 DCE
}
```

**运行**：
```bash
make null_loop
./null_loop              # 默认 1e8 次循环，10 reps
# 或者：
PERF_EVENTS=cycles,instructions ./run_template.sh ./null_loop
```

**预期结果**：
| 优化级别 | 每循环 cycles | 备注 |
|---------|---------------|------|
| -O0     | ~3-5 cycles   | add+cmp+branch，分支预测器救场 |
| -O2     | ~1 cycles     | 编译器看到 `i++` 后循环不变量 |
| -O2 + volatile | ~1-2 cycles | 强制 store/load，但分支预测器命中 |
| -O3 (优化掉) | 0 cycles | ❌ 你测到了"空气"，结果无效 |

**解释**：这个实验最重要的不是数字，而是让你看到**"无副作用的循环会被消除"**——这就是 Mytkowicz 论文里最重要的陷阱。

**缺陷与陷阱**：
- 即使加了 `volatile`，编译器仍可能把整个循环替换成单次赋值。永远用 `objdump -d` 检查 hot loop 真的存在。

**扩展思考**：
- 写一个 `for (i=0; i<N; i++) asm("nop");` 测纯 NOP 吞吐
- 飞腾 D3000 一个 cycle 能发射几条 NOP？（探测发射宽度）

---

### 3.3 实验 0.3：Amdahl 定律验证（`amdahl_law.c`）

**现象**：写一个工作负载，其中 $p$ 比例可以并行，$(1-p)$ 串行。用 OpenMP 跑 1-8 核，看加速比。

**假设**（先写）：
- $p=0.95$ 时，8 核应该接近 $1/(0.05 + 0.95/8) = 6.4\times$
- $p=1.0$ 时，应该接近 8×
- $p=0.5$ 时，8 核只有 $1/(0.5 + 0.5/8) = 1.78\times$

**关键代码**：
```c
// p_parallel 比例的并行工作
#pragma omp parallel for
for (uint64_t i = 0; i < N_parallel; i++) {
    volatile double x = i * 1.001;
    (void)x;
}

// (1 - p_parallel) 比例的串行工作
for (uint64_t i = 0; i < N_serial; i++) {
    volatile double x = i * 1.001;
    (void)x;
}
```

**运行**：
```bash
make amdahl_law
for nthreads in 1 2 4 8; do
    OMP_NUM_THREADS=$nthreads ./amdahl_law 0.95
done
```

**预期输出**（理论 vs 实测，飞腾 8 核）：
| p \ N | 1 | 2 | 4 | 8 |
|-------|---|---|---|---|
| 0.50 | 1.00 | 1.33 (1.78) | 1.60 (2.50) | 1.78 (4.00) |
| 0.90 | 1.00 | 1.82 (1.95) | 3.05 (3.48) | 4.71 (5.93) |
| 0.99 | 1.00 | 1.98 (1.99) | 3.88 (3.96) | 7.18 (7.47) |

（括号外是实测，括号内是理论 Amdahl 预测）

**解释**：实测总是**低于**理论，因为：
- OpenMP 同步开销（fork-join）
- Cache contention（多核访问共享 L3）
- 内存带宽（多核竞争 DDR4 通道）

**缺陷与陷阱**：
- 我用了 `volatile double x = i * 1.001` 制造"工作量"，但编译器仍可能识别出这是死代码
- 真正严谨的做法是算 sum 减少到 reduce（见 6.172 L07）

**扩展思考**：
- 测一下 Gustafson 路线（问题规模随 N 扩大），对比是否更"乐观"
- 如果改用 pthread 手动控制线程数，OpenMP 同步开销占多少？

---

### 3.4 实验 0.4：Iron Law 分解（`iron_law.c`）

**现象**：同一段代码，分别测出 $\text{IC}$、$\text{CPI}$、$\tau$，验证 $\text{Time} = \text{IC} \times \text{CPI} \times \tau$ 成立。

**假设**（先写）：
- 一个 `for` 加和数组：IC ≈ N 条 add + N 条 load + ...
- 若每条指令 1 cycle，CPI ≈ 1，总时间 ≈ N / freq
- 实际 CPI 通常 0.5-2.0（超标量 + 乱序让 CPI 可小于 1，飞腾 D3000 大概 0.6-0.8 IPC）

**关键代码**：
```c
// 被测函数：N 个 double 数组求和
double sum_array(const double *a, size_t n) {
    double s = 0;
    for (size_t i = 0; i < n; i++) s += a[i];
    return s;
}

// 主测量：用 PMU 读 cycles + instructions + 时间
pmu_group_t g = {0};
pmu_add_hw(&g, PERF_COUNT_HW_CPU_CYCLES, "cycles");
pmu_add_hw(&g, PERF_COUNT_HW_INSTRUCTIONS, "insts");
// ...
pmu_start(&g);
double s = sum_array(arr, N);
pmu_stop(&g);
```

**运行**：
```bash
make iron_law
./iron_law
```

**预期输出**：
```
N = 100000
  wall_time = 50.3 us
  cycles    = 130780
  insts     = 200012
  freq      = 2.5 GHz
  IPC       = 1.53
  CPI       = 0.65   ← 超标量让 CPI < 1！
  
Iron Law check:
  Time_pred = IC × CPI × τ = 200012 × 0.65 × (1/2.5e9) = 52.0 us  ✓
  Time_meas = 50.3 us   ✓ match
```

**解释**：现代处理器是**超标量**的，每个 cycle 可以**退休**多条指令，所以 IPC > 1 是常态。
这是后续 Lab04（超标量乱序）的预告。

**缺陷与陷阱**：
- PERF_COUNT_HW_INSTRUCTIONS 计的是 **retired** 指令（成功完成的），不包含被分支预测失败浪费的
- 如果代码里有大量分支预测失败，"真实"执行的指令数比 retired 多
- 高精度计数器 (`PERF_SAMPLE_READ`) 更准但开销大

**扩展思考**：
- 用同样的方法测**矩阵乘法**，看 IC、CPI、Time 如何随 N 增长
- 测一段**串行链表遍历**，对比 IPC——你会看到 IPC 跌到 0.2-0.3

---

## 4. 学完应该掌握的检查清单（自测）

- [ ] 我能用 `arch_probe` 独立给出任意一台 ARM/x86 机器的 cache 层级
- [ ] 我能解释 `volatile` 为什么"防 DCE"，也知道它什么时候**防不住**
- [ ] 我能解释 IPC > 1 意味着什么，并说出**至少两个**让 IPC 上不去的硬件原因
- [ ] 我能写出 Amdahl 公式，并指出 $p$ 怎么测出来
- [ ] 我能解释为什么"测了 100 次取平均"**仍可能错**（系统偏差 vs 随机偏差）
- [ ] 我会用 `objdump -d` 检查编译器有没有"作弊"
- [ ] 我能说出至少 3 种**测量偏差源**：DVFS、调度器漂移、cache 污染、SMM 中断、…

---

## 5. 参考文献

| 编号 | 文献 | 章节/页码 |
|------|------|----------|
| 📘 | Patterson & Hennessy RISC-V 第2版 | Ch1 §1.5-1.10, "Performance" |
| 📗 | Hennessy & Patterson CAQA 5th | Ch1 全章, "Fundamentals of Quantitative Design" |
| 📗 | CAQA 5th | Ch1 §1.11 "Fallacies and Pitfalls"（必读！） |
| 🎓 | Mytkowicz et al., ASPLOS 2009 | "Producing Wrong Data Without Doing Anything Obviously Wrong" |
| 🎓 | Bryan Cantrill, USENIX | "Not your parents' microbenchmark" |
| 🛠 | Linux `perf_event_open(2)` man page | 必读 |
| 🛠 | ARM ARM (ARM DDI 0487) | "Performance Monitors Extension" 章节 |

---

## 6. 编译与运行

```bash
cd Lab00_测量基础设施
make              # 编译所有实验
./arch_probe      # 先跑架构探测，确认环境
./null_loop       # 然后跑空循环
./amdahl_law 0.95 # Amdahl 验证，p=0.95
./iron_law        # Iron Law 分解
```

如果想用 PhyTune topdown-tool 做更精细的测量：
```bash
sudo python3 /opt/phytune/.../topdown-tool --cpu phytium-ftc862 ./iron_law
```

---

📌 **下一步**：完成 Lab00 后，进入 [`Lab01_ISA与汇编/`](../Lab01_ISA与汇编/)。在那里你将第一次**亲自写汇编**，看到 C 代码是如何变成飞腾能理解的 ARM64 指令的。
