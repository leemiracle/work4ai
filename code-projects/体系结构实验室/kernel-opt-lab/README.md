# Kernel-Lab — Phytium D3000 (FTC862) 国产边缘/信创算力 SoC 算子优化实验室

> **🆕 v1.0（2026-07-01）：系统化改造** —— 借鉴姊妹项目「体系结构实验」，引入：
> 三层视角体系（技术 lens / 专家 lens / 异质透镜）+ A64 指令参考（[`isa_reference/`](isa_reference/)，755 条指令）+
> 共享实验基础设施（[`common/`](common/)）+ 项目宪法 + 学习路径。**不动 src/ 算子代码**。
>
> 📚 **导航**：[学习路径](学习路径.md) ｜ [代码索引](CODE_INDEX.md) ｜ [视角矩阵](Views.md) ｜ [项目宪法](项目宪法.md) ｜ [ISA 扩展](扩展专题.md)
>
> **v0.15（2026-06-30）**：csdiy.wiki 全 117+ 门课程深度展开 + FTC862 PMU 规范详解 + 20 视角全方位审视 + MC×NC 分块 4 核 143 GFLOPS 新纪录。详见 [`docs/CSDIY-DEEP-DIVE/`](docs/CSDIY-DEEP-DIVE/)。
>
> D3000 单核 / 多核 GEMM / 卷积 / 量化算子 / Attention 的性能分析、瓶颈定位、优化实验工作目录。
> 配套工具：Perfetto v56.1 + PhyGCC 12.3.2 + Linux perf 5.4 + OpenMP
>
> **当前版本：v0.15（2026-06-30）** — csdiy.wiki 全课程深度展开完成（117+ 门 / 10 文件 / 20 lens 映射）

---

## 🎯 项目目标

把 D3000 算子推到理论峰值，沉淀**可复用的多视角分析方法论** + 参数表。
**双重定位**：(a) 飞腾"自主可控等级二级"的**软件层实证**（4 FVU 自研差异化）；(b) **国产边缘/信创算力**场景的算子优化实战。

## 📊 当前基线（v0.15）

**重大突破**：4 核 MC×NC 分块 GEMM 达 **143 GFLOPS（92% 效率）**，比 v0.8 的 71 GFLOPS 提升 **+101%**！

| 配置 | 实现 | GFLOPS | 效率 |
|---|---|---|---|
| 单核 FP32 | v5 MR=8 | 39.45 | 98.6% of 40 |
| **4 核 tiled** ⭐ v0.9 | MC=NC=256 + MR=8 | **142.86** | **92.4%** |
| 8 核 flat（旧） | flat MR=8 | ~170 | ~57% |
| INT8 单核 | v5 MR=8 | 77.74 | 97.2% of 80 |
| FP16 单核 | v4_dual MR=2 | 39.01 | 78% of 50 |
| Winograd F(4,4) 单核 | 6×6 tile | 26.19 等效 | 21.5× vs Direct |
| NEON Flash Attention N=1024 | 8 核 | 24.0 ms | 16.0× Naive |

### GEMM 性能（1024³，单核）

| 数据类型 | 最优实现 | 实测 | 利用率 |
|---|---|---|---|
| **FP32** | v5 MR=8（4 FVU 全开）| **39.45 GFLOPS** | **98.6% of 40** |
| **INT8** | v5 MR=8 | **77.74 GOPS** | **97.2% of 80** |
| **FP16** | v4_dual MR=2 ⚠️ | **39.01 GFLOPS** | 78% of 50 |

> 🔥 **v0.8 反直觉发现**：FP16 用 MR=8 反而比 MR=2 **慢**（35 vs 39 GFLOPS）。
> 原因：D3000 单条 `vfmaq_laneq_f16` 指令吞吐 < 4/cyc（4 FVU×8 lane 是理论，实际单 instr 只有 1-2/cyc）。
> → **结论：FP32/INT8 用 MR=8，FP16 用 MR=2**。

### 多核 GEMM（FP32 MR=8）

| 线程数 | GFLOPS | 加速比 | 效率 |
|---|---|---|---|
| 1 | 39.45 | 1.0× | 100% |
| 4 | ~150 | 3.8× | 93% |
| 8 | ~170 | 4.3× | 57%（L3 双段限制）|

### 卷积性能（3×3 stride=1 pad=1，56×56×64）

| 实现 | 时间 | 等效 GFLOPS | 加速比 |
|---|---|---|---|
| Direct (标量) | 189.6 ms | 1.22 | 1× |
| im2col + GEMM | 30.3 ms | 7.63 | 6.3× |
| **Winograd F(2,3)** | 12.8 ms | 18.13 | 14.8× |
| **Winograd F(4,4)** ⭐ v0.8 | **8.83 ms** | **26.19** | **21.5×** |

> F(4,4) 比 F(2,3) **再快 31%**，理论 4× 加速完美达成。

### Attention（head_dim=64）

| 实现 | N=1024 时间 | 加速比 | 备注 |
|---|---|---|---|
| Naive scalar | 154.2 ms | 1.0× | 基线 |
| **NEON Flash** ⭐ v0.7 | **23.4 ms** | **6.58×** | 单核 |
| NEON Flash 8 核 | **9.6 ms** | **16.0×** | 多核 |

→ 详见 [`results/baseline.md`](results/baseline.md)

## 📁 目录结构

```
kernel-opt-lab/
├── src/                            # C 算子源码（18 个 Makefile 目标 + 2 未挂载，详见 CODE_INDEX.md）
│   ├── gemm_f32.c                  # FP32 GEMM v5 (MR=8, 4 FVU) → 39.45 GFLOPS
│   ├── gemm_s8.c                   # INT8 GEMM v5 (vdotq) → 77.74 GOPS
│   ├── gemm_f16.c                  # FP16 GEMM (v4_dual MR=2，⚠️反直觉陷阱)
│   ├── gemm_tune/autotune/mr8_verify.c   # 自动调优 + 验证
│   ├── conv_*.c                    # 卷积家族（benchmark/winograd/f44/sizes/dispatcher）
│   ├── attention.c / attention_neon.c    # Naive vs NEON Flash（16×）
│   ├── multicore*.c                # flat / MC×NC tiled(92%) / winograd 多核
│   └── asm_kernel.c / bench_gemm.c
├── analysis/                       # ⭐ 技术维度 lens（可执行，5 个）
│   └── lens-{roofline,pmu,thermal,precision,latency}.c
├── include/kernel_lab.h            # 统一 C ABI（kl_gemm 等，库化接口）
├── common/                         # 🆕 v1.0 共享实验基础设施（借用姊妹项目）
│   ├── bench.h / pmu.h             # 高精度计时 + PMU 包装（与 kernel_lab.h 互补）
│   └── perf_stat_run.sh / run_template.sh  # 标准化 perf 测量
├── isa_reference/                  # 🆕 v1.0 A64 指令深度参考（18 md，755 条指令）
├── Lenses/                         # 🆕 v1.0 异质思维透镜（9 个：历史/Christensen/VC/...）
├── docs/
│   ├── lenses/                     # 专家角色 lens（10 份审查报告）
│   ├── CSDIY-DEEP-DIVE/            # csdiy.wiki 117+ 课程深度展开
│   └── INSTALL/ANALYSIS/OPTIMAL-PARAMS/PERFETTO-TUTORIAL/FTC862-PMU-SPEC.md
├── scripts/                        # build/test/bench/perfetto/pmu 工具脚本
├── perfetto/                       # trace 配置 + helper
├── results/                        # baseline + bench 报告 + lenses 分析
├── Makefile                        # 现代构建系统（make / make lens / make analyze / test / bench）
│
├── 项目宪法.md                     # 🆕 v1.0 最高决策文档（质量门槛 + 实验纪律 + 特异性测试）
├── CODE_INDEX.md                   # 🆕 v1.0 可运行程序总索引
├── Views.md                        # 🆕 v1.0 三层视角矩阵（技术/专家/异质）
├── 扩展专题.md                     # 🆕 v1.0 算子优化相关 ARMv8.x 扩展（NEON/FP16/UDOT）
├── 学习路径.md                     # 🆕 v1.0 八阶段教学化导览（假设→实验→解释→陷阱）
└── README.md
```

## 🚀 三分钟上手（现代方式：Make）

```bash
cd /data/usershare/ai/飞腾/kernel-opt-lab

make                                        # 编译全部 18 个算子目标
make lens                                   # ⭐ 编译 5 个 lens 视角分析
make analyze                                # ⭐ 跑全套 lens，生成 results/lenses/ 报告
make test                                   # 正确性回归（CI ready）
make bench                                  # 全套 bench + 自动报告
make clean                                  # 清理 bin/
make list                                   # 列出所有目标
make gemm_f32                               # 单目标编译

# 或继续用 build.sh（向后兼容）
./scripts/build.sh
./bin/gemm_f32                              # FP32 GEMM v5 MR=8 验证
./bin/conv_winograd_f44                     # ⭐ F(4,4) Winograd
./bin/attention_neon                        # NEON Flash + 多核 Flash

# trace + 可视化
./scripts/run-perfetto.sh ./bin/multicore   # Perfetto UI: https://ui.perfetto.dev
```

## 📌 关键发现（v0.1 → v0.9 沉淀）

1. **D3000 是 4 FVU**（v0.6 重大校准），不是早期以为的 2 FVU——FP32 真实峰值 40 GFLOPS
2. **FP32/INT8 用 MR=8**（4 FVU 全开，98% 利用率），FP16 反而用 MR=2（v0.8 反直觉发现）
3. **Winograd 全胜 im2col**，F(4,4) 比 F(2,3) 再快 31%（21.5× vs Direct）
4. **NEON Flash Attention** 单核 6.58× / 多核 16× vs Naive（v0.7）
5. **多核 MC×NC 分块是关键**（v0.9）：4 核 tiled 143 GFLOPS（92% 效率），flat 只有 94 GFLOPS（61%）
6. **OMP_PROC_BIND=close 在 D3000 上反而慢**（v0.9 实测）：拓扑特殊，通用 OS 调优建议必须本机验证

## 🔬 多视角分析框架（v0.9 引入）

项目从"单一优化工程师视角"扩展为**多专家多维度审视**。详见 [`docs/lenses/LENS-INDEX.md`](docs/lenses/LENS-INDEX.md)。

### 技术维度 lens（`analysis/`，可执行）

| Lens | 视角 | 命令 |
|---|---|---|
| Roofline | compute/memory bound | `./bin/lens-roofline` |
| PMU | 微架构 IPC/cache/branch | `./bin/lens-pmu` |
| Thermal | 热设计 + DVFS | `./bin/lens-thermal` |
| Precision | FP16/INT8 误差分布 | `./bin/lens-precision` |
| Latency | p50/p90/p99 长尾 | `./bin/lens-latency` |

### 专家角色 lens（`docs/lenses/`，10 份审查报告）

| 角色 | 报告 | 关键发现 |
|---|---|---|
| 性能架构师 | [`01`](docs/lenses/01-performance-architect.md) | 零 prefetch / 宏参数未探索 / 多核 57% 误诊 |
| 算法科学家 | [`02`](docs/lenses/02-algorithm-scientist.md) | BF16 缺席 / FP16 累加 bug / 距离 Llama-7B 还差 90% |
| OS/Runtime | [`03`](docs/lenses/03-os-runtime-expert.md) | MC×NC 分块缺失（4 核 tiled +52%）/ hugepage / 绑核 |
| 编译器专家 | [`04`](docs/lenses/04-compiler-expert.md) | PhyGCC/clang/gcc 零横评 / fast-math 未测 |
| 硬件专家 | [`05`](docs/lenses/05-hardware-engineer.md) | 4 FVU 结构 / L3 双段 DynamIQ / Spec store bypass Vulnerable |
| 教育者 | [`06`](docs/lenses/06-developer-advocate.md) | 缺 TUTORIAL+VISUAL+COMMON-PITFALLS 三件套 |
| DevOps/SRE | [`07`](docs/lenses/07-sre.md) | CI 跑 Graviton 不是 D3000 / 零 perf-gate |
| QA | [`08`](docs/lenses/08-qa.md) | 覆盖率 0.006% / 零 property testing / attention ⚠️ CI 漏洞（已修）|
| 安全 | [`09`](docs/lenses/09-security.md) | malloc 零 NULL check / tail 静默错误（已修）/ NaN 链路 |
| 应用集成 | [`10`](docs/lenses/10-integration.md) | 全仓 0 个 .h、38 static kernel（已加 include/kernel_lab.h）|

跑法：`make lens` 编译 / `make analyze` 一键跑全套 + 生成报告到 `results/lenses/`。

### 🆕 v1.0 异质思维透镜（`Lenses/`，9 个战略视角）

> 借用自姊妹项目「体系结构实验」，用**非从业者**的眼睛看"国产算子优化"这件事。
> 这些透镜不直接产出代码，但回答"为什么做、做给谁、能不能成"。详见 [`Views.md`](Views.md) §3。

| 透镜 | 范式 | 在算子优化里的追问 |
|---|---|---|
| 历史学家 | 历史模式 | 国产算子库能否复刻 cuBLAS/MKL 的生态崛起？ |
| Christensen | 破坏式创新 | 边缘算力是 GPU 性能过度供给留下的颠覆窗口？ |
| VC 投资人 | 下注判断 | 投不投"基于 D3000 的国产推理引擎"？ |
| 未来学家 | 技术赌注 | D3000 无 SVE/BF16，2026+ AI 算力图景撑多久？ |
| （其余 5 个）| 供应链/经济/人类学/反垄断/伦理 | 详见 [`Lenses/LENS-INDEX.md`](Lenses/LENS-INDEX.md) |

**三层对偶**：技术 lens（测量）→ 专家 lens（判断）→ 异质透镜（跳出框架的战略审视）。冲突记录在 [`Views.md`](Views.md) §4 对偶矩阵。

## 🎯 下一步优化方向（v0.9 多视角共识 P0）

1. **posix_memalign 全仓替换**（架构师+OS 共识）— 一行改动消除 alignment 慢路径
2. **FP16 改 FP32 累加**（算法科学家）— 修算法 bug，重测精度
3. **governor=performance + hugepage**（OS）— bench 前必跑
4. **BF16 GEMM 实现**（算法科学家）— LLM 落地前置
5. **causal + KV-cache Flash Attention**（算法科学家）— LLM 最小可运行单元
6. **software prefetch**（架构师）— GEMM 内核 +5-8%

## 📝 变更历史

- **2026-07-01 v1.0**：🏗️ 系统化改造（借鉴姊妹项目「体系结构实验」）— 引入三层视角体系（技术 lens / 专家 lens / 异质透镜 [`Lenses/`](Lenses/)）+ A64 指令参考 [`isa_reference/`](isa_reference/)（755 条指令）+ 共享实验基础设施 [`common/`](common/)（bench.h/pmu.h/perf 脚本）+ [`项目宪法.md`](项目宪法.md) + [`CODE_INDEX.md`](CODE_INDEX.md) + [`Views.md`](Views.md) + [`扩展专题.md`](扩展专题.md) + [`学习路径.md`](学习路径.md)（8 阶段教学化）。**不动 src/ 算子代码**，纯文档层 + 基础设施引入。
- **2026-06-30 v0.9**：🔬 多视角分析框架 — 5 技术 lens（Roofline/PMU/Thermal/Precision/Latency）+ 5 专家 lens（架构师/算法/OS/编译器/硬件）+ MC×NC 分块 4 核 143 GFLOPS 新纪录 + 实测验证 OS 专家盲区⑥
- **2026-06-30 v0.8**：FP16 反直觉发现 + F(4,4) Winograd（21.5× vs Direct）+ Makefile 现代构建 + bench-all.sh/test.sh 工程化
- **2026-06-29 v0.7**：GEMM MR=8 + NEON Flash Attention（6.58×）+ 多核 Flash
- **2026-06-29 v0.6**：🚨 重大校准——D3000 真实峰值是 40 GFLOPS（4 FVU 不是 2）
- **2026-06-29 v0.5**：多核 Winograd + Flash Attention + 混合 dispatcher
- **2026-06-29 v0.4**：多核 + Winograd F(2,3) + 尺寸扫描 + 手写汇编
- **2026-06-29 v0.3**：发现并修复 3 类 NEON 算法 bug；新增 INT8/FP16 v4 + 卷积
- **2026-06-29 v0.2**：修正 bench_gemm.c 4 处分母 bug；FP32 dual FVU 初版
- **2026-06-29 v0.1**：项目初始化；Perfetto 工具链搭建

## 📚 相关资源

- **Perfetto 文档**：https://perfetto.dev/docs/
- **ARM NEON intrinsics**：https://developer.arm.com/architectures/instruction-sets/intrinsics/
- **GEMM 优化经典论文**：*Anatomy of High-Performance Matrix Multiplication* (Goto & Van de Geijn, 2008)
- **Winograd 论文**：*Fast Algorithms for Convolutional Neural Networks* (Lavin & Gray, 2016)
- **Flash Attention 论文**：Dao et al., 2022
