# common/ — 共享实验基础设施

> **来源**：本目录借用自姊妹项目「体系结构实验」（飞腾 D3000M 体系结构教学实验），
> 该项目定位是"自下而上理解硬件"，本目录的计时/PMU 工具恰好补齐了 kernel-opt-lab
> 原本分散在各 `src/*.c` 里的计时代码。两套工具互补，详见下表。

## 与 `include/kernel_lab.h` 的分工

| 头文件 | 定位 | 提供什么 | 给谁用 |
|--------|------|---------|--------|
| `include/kernel_lab.h` | **库 ABI**（对外发布）| `kl_gemm` / `kl_conv2d` / `kl_attention` 等 C 接口 + `kl_xmalloc` 安全分配 | 外部链接者（C++/pybind11/ctypes）|
| `common/bench.h` | **实验计时**（对内测量）| `now_ns` / `now_cycles` / `median` / `escape` / `pin_to_cpu` | 写 benchmark 的人 |
| `common/pmu.h` | **PMU 计数器**（对内观测）| `perf_event_open` 包装 + 飞腾 FTC862 事件常量 | 想看微架构行为的人 |

一句话：`kernel_lab.h` 回答"怎么调用算子"，`common/` 回答"怎么测量算子跑得多快、为什么快/慢"。

## 文件清单

| 文件 | 作用 |
|------|------|
| `bench.h` | 高精度计时（`now_ns`/`now_cycles`）+ 统计（median/stdev）+ 防优化（escape/sink）+ 绑核（pin_to_cpu）|
| `pmu.h` | `perf_event_open` 简易包装 + 飞腾常用 PMU 事件常量（`FTC_L1D_CACHE_REFILL` 等）|
| `Makefile.inc` | 各 Lab 复用的编译规则（`-mcpu=ftc86x` 自适应、PhyGCC 探测）|
| `perf_stat_run.sh` | 飞腾/麒麟受限内核下 `perf stat` 的标准化包装（多次取中位数 + 派生 IPC/MPKI）|
| `run_template.sh` | 完整实验模板：锁频 + 绑核 + warmup + measured + perf 采集 |

## 用法示例

### 1. 写一个新的算子 benchmark

```c
#include "bench.h"
#include "pmu.h"

int main(void) {
    pin_to_cpu(0);                       // 绑核，避免调度漂移
    float *A = aligned_alloc(64, N*N*4); // 64B 对齐
    /* ... 准备数据 ... */

    pmu_group_t g = {0};
    pmu_add_hw(&g, PERF_COUNT_HW_CPU_CYCLES, "cycles");
    pmu_add_hw(&g, PERF_COUNT_HW_INSTRUCTIONS, "inst");
    pmu_add_raw(&g, FTC_L1D_CACHE_REFILL, "l1d_refill");

    uint64_t t[20];
    for (int rep = 0; rep < 5; rep++) my_gemm(A,B,C,N);   // warmup
    pmu_start(&g);
    for (int rep = 0; rep < 20; rep++) {
        t[rep] = now_ns();
        my_gemm(A,B,C,N);
        t[rep] = now_ns() - t[rep];
        escape(C);                      // 防 DCE
    }
    pmu_stop(&g);

    printf("median = %.1f ns\n", (double)median_u64(t, 20));
    uint64_t v[8]; pmu_read(&g, v); pmu_print(&g, v);
}
```

编译：`gcc -O3 -I common my_bench.c -o my_bench -lm`

### 2. 用 perf 包装现有算子（不改源码）

```bash
sudo ./common/perf_stat_run.sh ./bin/gemm_f32
./common/run_template.sh ./bin/conv_winograd_f44
```

## 实验纪律（来自体系结构实验项目宪法）

用 `common/` 跑实验时务必遵守（否则数据不可信）：

1. **固定频率**：`cpupower frequency-set -g performance`
2. **绑单核**：`taskset -c 0` 或 `pin_to_cpu(0)`
3. **warmup + measured**：先跑 5 次预热 Cache，再计时 20 次
4. **取中位数**：单次结果几乎一定有偏差
5. **防 DCE**：`escape()` 或 memory clobber，否则编译器删掉"无副作用"循环
6. **数据对齐**：`posix_memalign` / `aligned_alloc`，64 字节
7. **检查 hot loop**：`objdump -d` 确认编译器没"作弊"

详见 [`项目宪法.md`](../项目宪法.md) 第 7 节"实验纪律"。
