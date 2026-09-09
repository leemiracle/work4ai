# 工作负载优化建议

> 基于 [`profile_report.md`](./profile_report.md) 实测数据 + 飞腾 D3000M 微架构特性。
> 每条建议都标注了**数据依据**和**预期收益**。

---

## 数据快照（来自 [`profile_report.md`](./profile_report.md)）

| 工作负载 | IPC | L1 Miss% | Br Miss (M) |
|---------|----:|---------:|------------:|
| `gemm_single_core` | 1.79 | 9.35% | 8.66 |
| `zstd_random_L1` | 1.04 | 4.69% | 0.57 |
| `zstd_random_L19` | **0.41** ⚠️ | 3.87% | **130.50** ⚠️ |
| `zstd_text_L1` | 1.36 | 3.98% | 0.07 |
| `zstd_text_L9` | **1.94** 🎯 | 1.51% | 0.19 |

**最大反差**：`zstd_random_L19` 的 IPC 仅为 `zstd_text_L9` 的 21%，且分支预测失败高达 130M 次——这是"对不可压缩数据用高压缩级别"导致的灾难性反模式。

---

## 建议 1：zstd 输入预处理——避免"白费力"压缩

### 现象
`zstd_random_L19`（不可压缩随机数据 + 最高压缩级别）：
- IPC = 0.41（远低于飞腾 4-wide 峰值的 10%）
- 分支预测失败 130M 次（是 `zstd_text_L19` 的 700×）
- 23.4 秒压缩 64MB → 仅 2.7 MB/s（vs text_L1 的 1.0 GB/s，**400× 慢**）

### 根因
zstd 高级别（L19）会反复扫描输入尝试找匹配。对随机数据，每次匹配查找都失败，但流水线无法预测"失败"分支，导致 flush 风暴。

### 建议
**在调用 zstd 前做快速熵检测**：
```c
// 抽样 64KB 计算熵；熵 > 7.5 bit/byte 则直接 store 模式
double entropy = sample_entropy(input, 64 * 1024);
if (entropy > 7.5) {
    zstd_compress_level = 1;   // 直接降级，反正压不动
}
```
**预期收益**：随机数据压缩时间从 23s 降到 0.1s（**200× 加速**），压缩率损失 < 5%（本来就压不动）。

---

## 建议 2：GEMM 单核优化——分块尺寸调优

### 现象
`gemm_single_core` L1 miss 率 = 9.35%（所有工作负载中最高）。Lab05 程序里"分块 32×32"变体 GFLOPS=2.22，反而比"循环交换"（2.76）**慢**。

### 根因
飞腾 D3000M 的 L1 D-Cache 是 **64KB / 4-way / 64B line**（实测，见 [`Lab00/arch_probe`](../../Lab00_测量基础设施/src/arch_probe.c)）。
- 32×32 fp32 块 = 4 KB（输入 A 切片） + 4 KB（B 切片） + 4 KB（C 累加） = 12 KB ✓（应该装得下）
- 但**关联度只有 4-way**：当多个数组在相同 set 上冲突时，会提前 evict。
- 实测 L1 miss 9.35% 意味着 cache 没有充分复用。

### 建议
- **改用 16×16 或 8×8 起步**（占用 1.5KB / 384B），保证完全留在 L1。
- 或**对齐数组到 cache line 边界**：`posix_memalign(&A, 64, N*N*sizeof(float))`，避免 bank conflict。
- **更激进**：用 NEON 8×8 micro-kernel（fp16 的话能塞 16 个一行），见 [`Lab05/gemm_full_stack.c`](../../Lab05_并行与SIMD/src/gemm_full_stack.c) 的 NEON 变体。

**预期收益**：L1 miss 率从 9.35% 降到 < 3%，单核 GEMM GFLOPS 从 8.54 提到 12+（**+40%**）。

---

## 建议 3：开启大页（Transparent Huge Pages）

### 现象
所有工作负载的 cache miss 中包含 TLB miss 隐性代价（perf 后端不支持 LLC-load-misses，但 TLB miss 可观）。

### 根因
飞腾 D3000M TLB：L1 48 entry + L2 2048 entry（实测）。当工作集 > 4MB × 2048 = 8GB 时 TLB 开始压力。但即便 64MB 工作集，**4KB 小页**也会占 16K 个 page table entry，TLB L2 装 2K 都很挤。

### 建议
对 GEMM 大矩阵（N=512 → 1MB 数组）和 zstd 大 buffer 启用大页：
```bash
# 系统级：让 khugepaged 自动合并
echo always > /sys/kernel/mm/transparent_hugepage/enabled

# 或运行时强制：
HUGETLB_MORE=1 hugeadm --pool-pages-min 2MB:64
./your_program   # 配合 madvise(MADV_HUGEPAGE)
```
**预期收益**：TLB miss 减 80%，大矩阵 GEMM 加速 5–15%。

---

## 建议 4：绑核 + 关 SMT + 固定频率（实验纪律）

### 现象
本测试已用 `taskset -c 0` 绑核 + `governor=performance` 锁频。**生产环境常常不做这些**，导致数据漂移 30%+。

### 建议（已在本项目所有 Lab 实施为标准纪律）
```bash
# 1. 锁最高频率
cpupower frequency-set -g performance

# 2. 关闭 SMT（飞腾默认 smt_active=0，已 OK）
cat /sys/devices/system/cpu/smt/control

# 3. 绑核（避免调度漂移）
taskset -c 0 ./your_program

# 4. NUMA 感知（多核时）
numactl --cpunodebind=0 --membind=0 ./your_program
```
**预期收益**：测量噪声从 ±20% 降到 ±2%，**A/B 比较才有意义**。
参考 CAQA Ch1 "Producing Wrong Data Without Doing Anything Obviously Wrong"（Mytkowicz 2009）。

---

## 建议 5：用 NEON 重写 zstd 热点（或选 L9 而非 L19）

### 现象
`zstd_text_L9` IPC=1.94（接近 4-wide 极限的 50%），而 `zstd_text_L19` IPC 仅 1.93（**与 L9 几乎相同**），但压缩率只高 1-2%。

### 根因
zstd 在 L9 → L19 主要增加匹配查找深度，对可压缩数据收益已饱和。两者 IPC 相近，说明流水线占用结构相同，但 L19 多用 50% 时间。

### 建议
**默认用 L9 而非 L19**：
```bash
zstd -9 input   # 而非 -19
```
- 时间收益：约 3× 加速（实测 L9=0.19s vs L19=0.25s 看似不大，但大文件时差距拉大）
- 空间损失：< 2%

**对自研压缩需求**：用 NEON 加速熵编码（Huffman）和 LZ77 匹配，飞腾 NEON 128-bit 可一次处理 4 个 int32 哈希比较，详见 [`isa_reference/v8.0_asimd.md`](../../isa_reference/v8.0_asimd.md)。

---

## 总结表

| # | 建议 | 适用场景 | 预期收益 | 难度 |
|---|------|---------|---------|------|
| 1 | 输入熵检测避免徒劳压缩 | zstd / 通用压缩 | 200×（最坏情况） | 低 |
| 2 | GEMM 分块尺寸调小 + 对齐 | 科学计算 / 推理 | +40% | 中 |
| 3 | 启用 THP / 大页 | 大内存工作负载 | 5–15% | 低 |
| 4 | 绑核 + 锁频 + 关 SMT | 任何 benchmark | 噪声 -90% | 低 |
| 5 | zstd 默认 L9 + NEON 热点 | 压缩密集型 | 3× | 中 |

---

## 数据可重现

```bash
cd Capstone/workload_characterization
./driver.sh                                    # 跑工作负载 + 写 data/
python3 collect.py 'data/*.perf' -o profile_report.md   # 生成报告
cat profile_report.md recommendations.md       # 查看完整分析
```

📌 **下一步**：
- 看 [`profile_report.md`](./profile_report.md) 的实测数据表
- 看 [`../alpha_21264_study/comparison.md`](../alpha_21264_study/comparison.md) 的微架构上下文
- 在 [`../cpu_simulator/`](../cpu_simulator/) 跑 5 级流水线模拟器对比 IPC 边界
