# 可运行代码索引（CODE_INDEX）

> Kernel-Lab 所有**可运行程序、脚本、工具**的统一入口。
> 每个程序都附"做什么 / 跑法 / 预期输出"。
> 配套 [`Views.md`](./Views.md)（视角矩阵）+ [`项目宪法.md`](./项目宪法.md)（写作与实验纪律）。

---

## A. 算子核心（`src/`，18 个 Makefile 目标 + 2 个未挂载）

### A.1 GEMM 家族（矩阵乘，算子优化之王）

| 程序 | 源文件 | 做什么 | 跑法 | 关键结果 |
|------|--------|--------|------|---------|
| `gemm_f32` | [`src/gemm_f32.c`](./src/gemm_f32.c) | FP32 GEMM v5（MR=8，4 FVU 全开）| `make gemm_f32 && ./bin/gemm_f32` | **39.45 GFLOPS（98.6% of 40）** |
| `gemm_s8` | [`src/gemm_s8.c`](./src/gemm_s8.c) | INT8 GEMM v5（vdotq，4 FVU）| `make gemm_s8 && ./bin/gemm_s8` | **77.74 GOPS（97.2% of 80）** |
| `gemm_f16` | [`src/gemm_f16.c`](./src/gemm_f16.c) | FP16 GEMM（v4_dual MR=2 最优）| `make gemm_f16 && ./bin/gemm_f16` | 39.01 GFLOPS（78% of 50）⚠️ 反直觉 |
| `gemm_tune` | [`src/gemm_tune.c`](./src/gemm_tune.c) | MR × NR × KC 自动调参 | `make gemm_tune && ./bin/gemm_tune` | 输出最优参数表 |
| `gemm_autotune` | [`src/gemm_autotune.c`](./src/gemm_autotune.c) | 进阶自动调优（**未挂 Makefile**）| `gcc -O3 src/gemm_autotune.c -o bin/gemm_autotune -lm` | — |
| `gemm_mr8_verify` | [`src/gemm_mr8_verify.c`](./src/gemm_mr8_verify.c) | 三种数据类型 MR=8 正确性验证 | `make gemm_mr8_verify && ./bin/gemm_mr8_verify` | 全 PASS |
| `bench_gemm` | [`src/bench_gemm.c`](./src/bench_gemm.c) | 原版主基准（含 raw throughput）| `make bench_gemm && ./bin/bench_gemm` | 基线对照 |

### A.2 卷积家族

| 程序 | 源文件 | 做什么 | 跑法 | 关键结果 |
|------|--------|--------|------|---------|
| `conv_benchmark` | [`src/conv_benchmark.c`](./src/conv_benchmark.c) | 3×3/1×1/depthwise 卷积对比 | `make conv_benchmark && ./bin/conv_benchmark` | im2col 6.3× vs Direct |
| `conv_winograd` | [`src/conv_winograd.c`](./src/conv_winograd.c) | Winograd F(2×2, 3×3) | `make conv_winograd && ./bin/conv_winograd` | 14.8× vs Direct |
| `conv_winograd_f44` | [`src/conv_winograd_f44.c`](./src/conv_winograd_f44.c) | ⭐ Winograd F(4×4, 3×3) | `make conv_winograd_f44 && ./bin/conv_winograd_f44` | **21.5× vs Direct** |
| `conv_winograd_int8` | [`src/conv_winograd_int8.c`](./src/conv_winograd_int8.c) | INT8 Winograd（**未挂 Makefile**）| `gcc -O3 src/conv_winograd_int8.c -o bin/conv_winograd_int8 -lm` | — |
| `conv_sizes` | [`src/conv_sizes.c`](./src/conv_sizes.c) | 尺寸扫描 32→224 | `make conv_sizes && ./bin/conv_sizes` | roofline 拟合 |
| `conv_dispatcher` | [`src/conv_dispatcher.c`](./src/conv_dispatcher.c) | 自动策略选择（+OpenMP）| `make conv_dispatcher && ./bin/conv_dispatcher` | 自适应分发 |

### A.3 Attention 家族

| 程序 | 源文件 | 做什么 | 跑法 | 关键结果 |
|------|--------|--------|------|---------|
| `attention` | [`src/attention.c`](./src/attention.c) | Naive vs scalar Flash | `make attention && ./bin/attention` | 基线 |
| `attention_neon` | [`src/attention_neon.c`](./src/attention_neon.c) | ⭐ NEON Flash + 多核 Flash（+OpenMP）| `make attention_neon && ./bin/attention_neon` | **单核 6.58× / 多核 16×** |

### A.4 多核与汇编

| 程序 | 源文件 | 做什么 | 跑法 | 关键结果 |
|------|--------|--------|------|---------|
| `multicore` | [`src/multicore.c`](./src/multicore.c) | OpenMP flat 多核扩展性（+OpenMP）| `make multicore && ./bin/multicore` | 8 核 ~170 GFLOPS（57%）|
| `multicore_tiled` | [`src/multicore_tiled.c`](./src/multicore_tiled.c) | ⭐ MC×NC 分块多核（+OpenMP）| `make multicore_tiled && ./bin/multicore_tiled` | **4 核 143 GFLOPS（92%）** |
| `multicore_winograd` | [`src/multicore_winograd.c`](./src/multicore_winograd.c) | 多核 Winograd（+OpenMP）| `make multicore_winograd && ./bin/multicore_winograd` | — |
| `multicore_winograd_f44` | [`src/multicore_winograd_f44.c`](./src/multicore_winograd_f44.c) | 多核 F(4,4) Winograd（+OpenMP）| `make multicore_winograd_f44 && ./bin/multicore_winograd_f44` | — |
| `asm_kernel` | [`src/asm_kernel.c`](./src/asm_kernel.c) | 手写 inline asm 微内核 | `make asm_kernel && ./bin/asm_kernel` | 对照编译器 |

---

## B. 视角分析（`analysis/`，5 个可执行 lens）

> 技术维度 lens，可执行，输出结构化报告。跑法：`make lens && make analyze`。

| Lens | 源文件 | 视角 | 命令 | 输出 |
|------|--------|------|------|------|
| `lens-roofline` | [`analysis/lens-roofline.c`](./analysis/lens-roofline.c) | compute/memory bound 分类 | `./bin/lens-roofline` | Roofline 定位 |
| `lens-pmu` | [`analysis/lens-pmu.c`](./analysis/lens-pmu.c) | 微架构 IPC/cache/branch | `./bin/lens-pmu` | PMU 计数 |
| `lens-thermal` | [`analysis/lens-thermal.c`](./analysis/lens-thermal.c) | 热设计 + DVFS 降频 | `./bin/lens-thermal` | 热节流证据 |
| `lens-precision` | [`analysis/lens-precision.c`](./analysis/lens-precision.c) | FP16/INT8 误差分布 | `./bin/lens-precision` | 精度损失量化 |
| `lens-latency` | [`analysis/lens-latency.c`](./analysis/lens-latency.c) | p50/p90/p99 长尾 | `./bin/lens-latency` | 尾延迟分布 |

报告归档：[`results/lenses/`](./results/lenses/)（`make analyze` 自动生成）。

---

## C. 角色审查 lens（`docs/lenses/`，10 份专家报告）

> 不可执行，是各领域专家对项目的书面审查。详见 [`Views.md`](./Views.md)。

| 角色 | 报告 | 关键发现 |
|------|------|---------|
| 性能架构师 | [`docs/lenses/01-performance-architect.md`](./docs/lenses/01-performance-architect.md) | 零 prefetch / 宏参数未探索 |
| 算法科学家 | [`docs/lenses/02-algorithm-scientist.md`](./docs/lenses/02-algorithm-scientist.md) | BF16 缺席 / FP16 累加 bug |
| OS/Runtime | [`docs/lenses/03-os-runtime-expert.md`](./docs/lenses/03-os-runtime-expert.md) | MC×NC 分块缺失（已修）/ hugepage |
| 编译器专家 | [`docs/lenses/04-compiler-expert.md`](./docs/lenses/04-compiler-expert.md) | PhyGCC/clang/gcc 零横评 |
| 硬件专家 | [`docs/lenses/05-hardware-engineer.md`](./docs/lenses/05-hardware-engineer.md) | 4 FVU 结构 / L3 双段 DynamIQ |
| 教育者 | [`docs/lenses/06-developer-advocate.md`](./docs/lenses/06-developer-advocate.md) | 缺 TUTORIAL+VISUAL+PITFALLS |
| DevOps/SRE | [`docs/lenses/07-sre.md`](./docs/lenses/07-sre.md) | CI 跑 Graviton 不是 D3000 |
| QA | [`docs/lenses/08-qa.md`](./docs/lenses/08-qa.md) | 覆盖率 0.006% / attention ⚠️ 已修 |
| 安全 | [`docs/lenses/09-security.md`](./docs/lenses/09-security.md) | malloc 零 NULL check（已修）|
| 应用集成 | [`docs/lenses/10-integration.md`](./docs/lenses/10-integration.md) | 全仓 0 个 .h（已加 kernel_lab.h）|

---

## D. 基础设施与工具脚本

### D.1 构建与测试（`scripts/`）

| 脚本 | 做什么 | 命令 |
|------|--------|------|
| [`scripts/build.sh`](./scripts/build.sh) | 编译全部算子（兼容旧脚本）| `./scripts/build.sh` |
| [`scripts/test.sh`](./scripts/test.sh) | 正确性回归（CI ready）| `make test` |
| [`scripts/bench-all.sh`](./scripts/bench-all.sh) | 全套 bench + 自动 markdown 报告 | `make bench` |
| [`scripts/analyze-all.sh`](./scripts/analyze-all.sh) | 跑全套 lens 生成报告 | `make analyze` |
| [`scripts/run-perfetto.sh`](./scripts/run-perfetto.sh) | perf record + trace_processor 一条龙 | `./scripts/run-perfetto.sh ./bin/multicore` |
| [`scripts/pmu-stat.sh`](./scripts/pmu-stat.sh) | 完整 18 项 PMU 统计 | `./scripts/pmu-stat.sh ./bin/gemm_f32` |
| [`scripts/detect-topology.sh`](./scripts/detect-topology.sh) | 探测 CPU/Cache/NUMA 拓扑 | `./scripts/detect-topology.sh` |
| [`scripts/runtime-tune.sh`](./scripts/runtime-tune.sh) | governor/hugepage/绑核环境调优 | `sudo ./scripts/runtime-tune.sh` |

### D.2 实验计时与 PMU（`common/`，借用自体系结构实验项目）

| 文件 | 作用 | 用法 |
|------|------|------|
| [`common/bench.h`](./common/bench.h) | 高精度计时 + 统计 + 防优化 + 绑核 | `#include "bench.h"`（见 [`common/README.md`](./common/README.md)）|
| [`common/pmu.h`](./common/pmu.h) | perf_event_open 包装 + FTC862 事件常量 | `#include "pmu.h"` |
| [`common/perf_stat_run.sh`](./common/perf_stat_run.sh) | 受限内核下 perf stat 标准包装 | `sudo ./common/perf_stat_run.sh ./bin/gemm_f32` |
| [`common/run_template.sh`](./common/run_template.sh) | 完整实验模板（锁频+绑核+warmup+measured）| `./common/run_template.sh ./bin/gemm_f32` |

### D.3 Perfetto trace 工具（`perfetto/`）

| 文件 | 作用 |
|------|------|
| [`perfetto/tp-serve.sh`](./perfetto/tp-serve.sh) | 启动 trace_processor 服务 |
| [`perfetto/trace_config_minimal.pbtxt`](./perfetto/trace_config_minimal.pbtxt) | 最小 trace 配置 |
| [`perfetto/trace_config_pmu.pbtxt`](./perfetto/trace_config_pmu.pbtxt) | 含 PMU 的 trace 配置 |

### D.4 库 ABI（`include/`）

| 文件 | 作用 |
|------|------|
| [`include/kernel_lab.h`](./include/kernel_lab.h) | 统一 C ABI（`kl_gemm`/`kl_conv2d`/`kl_attention` + `kl_xmalloc` 安全分配），extern "C" 兼容 C++/ctypes |

---

## E. 文档与结果

| 路径 | 内容 |
|------|------|
| [`results/baseline.md`](./results/baseline.md) | 性能基线 + 完整历史 |
| [`results/bench-*.md`](./results/) | 自动生成的 bench 报告 |
| [`results/lenses/SUMMARY.md`](./results/lenses/SUMMARY.md) | lens 分析汇总 |
| [`docs/INSTALL.md`](./docs/INSTALL.md) | Perfetto + 系统配置安装 |
| [`docs/ANALYSIS.md`](./docs/ANALYSIS.md) | 瓶颈分析 + bug 发现过程 |
| [`docs/OPTIMAL-PARAMS.md`](./docs/OPTIMAL-PARAMS.md) | 完整最优参数表（含推导）|
| [`docs/PERFETTO-TUTORIAL.md`](./docs/PERFETTO-TUTORIAL.md) | Perfetto UI 5 分钟入门 |
| [`docs/FTC862-PMU-SPEC.md`](./docs/FTC862-PMU-SPEC.md) | FTC862 PMU 事件规范 |
| [`docs/SHARE.md`](./docs/SHARE.md) | 对外分享文档 |
| [`docs/CSDIY-DEEP-DIVE/`](./docs/CSDIY-DEEP-DIVE/) | csdiy.wiki 117+ 课程深度展开 |
| [`isa_reference/`](./isa_reference/) | A64 指令级深度参考（18 个 md，755 条指令）|
| [`扩展专题.md`](./扩展专题.md) | ARMv8.x 扩展在算子优化中的应用 |

---

## F. 一键命令速查

```bash
make                # 编译全部 18 个算子
make lens           # 编译 5 个 lens
make analyze        # 跑全套 lens 生成报告
make test           # 正确性回归
make bench          # 全套 benchmark + 自动报告
make list           # 列出所有目标
make clean          # 清理 bin/

# 标准化 perf 测量（来自 common/）
sudo ./common/perf_stat_run.sh ./bin/gemm_f32      # IPC/MPKI 派生
./common/run_template.sh ./bin/conv_winograd_f44   # 锁频+绑核+中位数

# trace 可视化
./scripts/run-perfetto.sh ./bin/multicore          # → https://ui.perfetto.dev
```
