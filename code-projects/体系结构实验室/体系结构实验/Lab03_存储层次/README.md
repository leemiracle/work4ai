# Lab03 — 存储层次：Cache / TLB / NUMA

> "内存是新的磁盘。" —— 说这话的人意识到：CPU 比 DRAM 快 1000 倍。
>
> 存储层次的设计目标：**让 95% 的访问感觉就像在 L1 里。**

---

## 0. 学习目标（一句话）

**实证地理解每一级存储（L1/L2/L3/DRAM/NUMA）的容量、延迟、带宽**，并掌握 cache 行、关联度、TLB、false sharing、prefetching 等机制——这些是性能优化的核心战场。

---

## 1. 对应教材与课程

| 来源 | 章节 | 重点 |
|------|------|------|
| 📘 Patterson RISC-V | **Ch5 (Memory Hierarchy)** | Cache 基础、写策略、虚存 |
| 📗 CAQA 5th | **Ch2 (Memory Hierarchy Design)** | 高级 Cache、Prefetch、Consistency |
| 📗 CAQA 5th | **App B** | 存储层次复习（必读） |
| 📕 姚永斌超标量 | **Ch2 (Cache)** | 多端口 Cache、Victim Cache |
| 📕 姚永斌超标量 | **Ch3 (虚拟存储)** | TLB、Page Walk、Page Fault |
| 🎓 CSAPP | Ch6 (The Memory Hierarchy) | 程序员视角的存储层次 |
| 🎓 CS61C | Lecture 17-19 | Cache 深度 |

---

## 2. 核心概念速览

### 2.1 直觉：为什么有"层次"？

```
速度 ↑                容量 ↓
L1     1-4 cycles    64 KB   (离核最近)
L2     10-15 cycles  512 KB  (飞腾 D3000M 实测)
L3     30-50 cycles  8 MB    (核间共享)
DRAM   130-265 ns (实测)  64 GB   (DDR4-3200)
NUMA   +50% DRAM     数百 GB (跨 socket)
SSD    10-100 μs     TB      (PCIe NVMe)
HDD    1-10 ms       多 TB
```

**金句**：每一级是下一级的 ~10x 容量、~10x 慢。

### 2.2 数学：AMAT（Average Memory Access Time）

$$
\text{AMAT} = T_{\text{hit}} + \text{MissRate} \times T_{\text{penalty}}
$$

例如飞腾：
- L1 hit: 4 cycles, miss rate 5%, penalty (to L2) = 12 cycles
- L2 hit: 12 cycles, miss rate 20%, penalty (to L3) = 40 cycles
- L3 hit: 40 cycles, miss rate 30%, penalty (to DRAM) = 200 cycles

$\text{AMAT} = 4 + 0.05 \times (12 + 0.20 \times (40 + 0.30 \times 200)) \approx 6.16 \text{ cycles}$

**注意**：飞腾 D3000M 的 L2 = 512 KB（实测，比手册上说的 1MB 小），影响分块参数选择。

### 2.3 Cache 行 vs 字

```
Cache line = 64 字节 = 8 个 double / 16 个 int / 64 个 char
对齐访问 a[0] 和 a[1]（同一 line）几乎免费
对齐访问 a[0] 和 a[64]（不同 line）需要 2 次 cache access
```

### 2.4 一张图：4-way set-associative cache

```
  Set index (例如 8 位 → 256 sets)
   ↓
┌─────────────────────────────┐
│ Set 0: [Way0][Way1][Way2][Way3] │   ← 4 个 way（飞腾 L1D 是 4-way）
│ Set 1: [Way0][Way1][Way2][Way3] │
│ ...                              │
│ Set 255: [...]                   │
└─────────────────────────────┘
每个 Way 存：Tag | Data(64B) | Valid | Dirty | LRU

地址解析：
[Tag | Set index | Block offset]
 高位  中间位     低 6 位（64 字节）
```

---

## 3. 实验列表

### 3.1 实验 3.1：实测 Cache 容量（`cache_sizes.c`）

**现象**：跑一段 stride-1 顺序访问，看不同数组大小下延迟的"台阶"。

**假设**：
- 数组 ≤ 64 KB：~1 cycle/元素（L1 命中）
- 64 KB < 数组 ≤ 512 KB：~10 cycles（L2 命中）
- 512 KB < 数组 ≤ 8 MB：~40 cycles（L3 命中）
- 数组 > 8 MB：~200 cycles（DRAM）

**关键代码**（经典 pointer chasing）：
```c
// 构造一个链表，每个节点 sizeof(node) 字节
// 然后 chase 这个链表 N 次，每次访问必须等数据回来
typedef struct node { struct node *next; } node_t;

double measure_latency(node_t *head, size_t n_iter) {
    uint64_t t0 = now_ns();
    volatile node_t *p = head;
    for (size_t i = 0; i < n_iter; i++) {
        p = p->next;
    }
    uint64_t t1 = now_ns();
    return (double)(t1 - t0) / (double)n_iter;
}
```

**运行**：
```bash
make cache_sizes
./cache_sizes
```

**预期输出**（飞腾 D3000M 实测，横轴是数组大小，纵轴是延迟）：
```
size=      4 KB  latency=  1.6 ns  (L1)
size=     16 KB  latency=  1.6 ns  (L1)
size=     64 KB  latency=  2.3 ns  (L1 边界)
size=    128 KB  latency=  4.8 ns  (L2)
size=    512 KB  latency=  8.0 ns  (L2 边界)
size=      1 MB  latency= 14.0 ns  (L3)
size=      8 MB  latency= 14.0 ns  (L3 边界，核0-7 分级共享)
size=     32 MB  latency=130.0 ns  (DRAM)
size=    128 MB  latency=138.0 ns  (DRAM)
```

> 📌 实测范围（诊断报告 §5，2026-07-02）：L1 1.6-2.3 / L2 4.6-8.8 / L3 13-109 / DRAM 127-138 ns。
> L3 跨度大是因为 4M(核0-3)+8M(核0-7) 分级 + 末端受 DRAM 邻接污染。

**解释**：latency 跳跃点直接告诉你 cache 边界。

**缺陷与陷阱**：
- prefetcher 会把"看似随机"的访问识别成顺序，破坏实验
- 用随机排列的指针链抑制 prefetcher
- TLB miss 会污染结果（>几 MB 时改用 huge page）

---

### 3.2 实验 3.2：Cache 行（`cache_line.c`）

**现象**：访问 a[0] 和 a[1]（同 line）几乎免费；访问 a[0] 和 a[8]（不同 line）贵。

**假设**：cache line = 64 字节，double = 8 字节，所以 a[0..7] 在同一 line。

**关键代码**（stride 测试）：
```c
double measure_stride(const double *a, size_t n, size_t stride) {
    uint64_t t0 = now_cycles();
    volatile double s = 0;
    for (size_t i = 0; i < n; i += stride) {
        s += a[i];
    }
    uint64_t t1 = now_cycles();
    return (double)(t1 - t0) / (double)(n / stride);
}

// 调用：
for (size_t stride = 1; stride <= 128; stride *= 2) {
    printf("stride=%zu: %.2f cyc/access\n", stride, measure_stride(arr, 1<<20, stride));
}
```

**预期结果**：
| Stride | Cyc/access | 解读 |
|--------|-----------|------|
| 1 (8B) | 0.25 | 同 line，向量化 |
| 2 (16B) | 0.25 | 仍在同 line |
| 8 (64B) | 0.5 | 正好一行 |
| 16 (128B) | 4.0 | 跨 line，每次新 line |
| 32 | 5.0 | 跨 line + 一半浪费 |
| 64+ | 5.0 | saturate |

**解释**：stride=8 时（一个 cache line），每次 access 拉一个新的 64 字节进来。stride=1 时同 line 8 个元素被一次拉进来，所以 amortized 0.25 cyc。

---

### 3.3 实验 3.3：关联度（`associativity.c`）

**现象**：访问 power-of-2 个互相冲突的地址，IPC 突然暴跌——这是 associativity 限制。

**前提**：飞腾 L1D 实测 64KB / **4-way / 256 sets** / line 64B（Lab00 arch_probe）。
- set index = addr[6:13]（line offset 6 位后 8 位）→ **同 set 地址间隔 = 256×64 = 16KB**
- 构造 N 个间隔 16KB 的地址（全映射同一 set），N≤4 全在 4-way 内命中，N≥5 eviction

**实测（飞腾 D3000M，2026-07-02，pointer chasing 随机环，N 同 set 地址）**：
| N | cyc/step | miss/step | 解读 |
|---|----------|-----------|------|
| 1-4 | **4.00** | **0.00** | ≤4-way，全 L1 命中 |
| **5** | **12.00** | **1.00** | **← 超 way 数，eviction thrashing** |
| 6-9 | 12.00 | 1.00 | 每步 miss L2 |

**拐点 N\*=4，完美反推飞腾 L1D 是 4-way**（miss/step 从 0 突变到 1.00，证据无可辩驳）。

**对偶解读**：CPU 设计处处是"冲突→硬件机制"——
- cache 结构冒险（set 冲突）→ **set-associative + replacement**（本实验）
- 数据冒险 RAW → **forwarding 单元**（[Expert_03](../Expert_03_HW_Designer/) 的 `forward_a/forward_b` RTL）
- 控制冒险 → **分支预测器**（Lab02 branch_predict）

**实战陷阱**：power-of-2 stride 是性能杀手（大量地址撞同 set）——矩阵列遍历、hash 表桶数选 2^k 都可能触发本实验观测的 thrashing。

---

### 3.4 实验 3.4：TLB 与大页（`tlb_hugepage.c`）

**现象**：访问 100 MB 数组，4 KB 页 → TLB miss 拖累；2 MB 大页 → 快 5 倍。

**关键代码**：
```c
// 用 mmap + MAP_HUGETLB 直接分配 2MB 大页
double *arr = mmap(NULL, 256*1024*1024, PROT_READ|PROT_WRITE,
                   MAP_PRIVATE|MAP_ANONYMOUS|MAP_HUGETLB, -1, 0);
```

**方法 vs 实测（飞腾 D3000M，2026-07-02，pointer chasing 跨页随机环，256MB）**：

方法：每步 `p = *(void**)p` 跨一页，随机环防 prefetcher，cyc/step 差异纯来自 TLB。

| 页大小 | 页数 vs TLB | ns/step | 解读 |
|--------|------------|---------|------|
| 4KB | 65536 >> TLB(48+2048) | **140.5** | 频繁 page walk（查 4 级页表）|
| 2MB | 128 < TLB | **41.3** | 全命中，零 walk |

**3.40× 加速，page walk 代价 ~99 ns**（与 Expert_04 实测 2M vs 4K 页 4.81× 同向，差异来自负载/方法）。

> 开启大页：`sudo bash -c 'echo 128 > /proc/sys/vm/nr_hugepages'`，否则 2MB 分支 fallback。
> ⚠ 顺序 stride 法会被 prefetcher+cache miss 淹没（测出大页反慢），必须用 pointer chasing。

---

### 3.5 实验 3.5：False Sharing（`false_sharing.c`）

**现象**：两个线程各自更新自己的计数器，但变量在同一 cache line → 性能暴跌 10 倍。

**关键代码**：
```c
// Bad: 两个变量在同一 line
struct { int x; int y; } shared;  // 同一 cache line

// Good: 用 alignas 隔开
struct alignas(64) {
    alignas(64) int x;
    alignas(64) int y;
} isolated;
```

**预期 vs 实测（飞腾 D3000M，2026-07-02，2核 200M inc/线程）**：
| 模式 | ns/inc | 慢x倍 |
|------|--------|-------|
| 单线程（纯 L1 基线）| 2.25 | 1.0× |
| 2线程 false sharing（同 line）| **4.29** | **1.9×** |
| 2线程 隔离（alignas64）| 2.28 | 1.0× |

- false sharing 实测慢 ~1.9×（每次 inc 触发跨核 MESI line 迁移；比教科书说的"10-50×"低，因 volatile+asm 开销占大头，但趋势明确）
- alignas(64) 隔离后与单线程基线持平 → 证明 false sharing 是唯一原因
- 验证：`perf stat -e cache-misses ./false_sharing` 看 bad 版 miss 暴涨

---

### 3.6 实验 3.6：NUMA 效应（`numa_effects.c`）

**现象**：单 NUMA 节点时不会感知；多 socket 时跨节点访问慢 50-100%。

**关键代码**：
```c
// 用 numa_alloc_onnode 强制在指定节点分配
// 用 numactl --membind 限制内存节点
// 用 taskset 限制 CPU
```

---

## 4. 学完应该掌握的检查清单

- [ ] 能用 pointer chasing 测出 L1/L2/L3/DRAM 的边界
- [ ] 能解释 power-of-2 stride 为什么是性能杀手
- [ ] 能用 `posix_memalign` / `alignas` 避免 false sharing
- [ ] 能用 MAP_HUGETLB 分配大页，并测量 TLB miss 收益
- [ ] 能解释 AMAT 公式，并粗略估算某段代码的 AMAT
- [ ] 能用 perf stat 看 cache miss rate（L1D/L2/L3）

---

## 5. 参考文献

| 编号 | 文献 | 章节 |
|------|------|------|
| 📘 | Patterson RISC-V 第2版 | Ch5 全章 |
| 📗 | CAQA 5th | **Ch2 全章** |
| 📕 | 姚永斌超标量 | Ch2 Cache, Ch3 虚拟存储 |
| 🎓 | CSAPP Ch6 | 程序员视角 |
| 📖 | Smith, "Cache Memories" (1982) | 经典 |
| 📖 | Baer, "Microprocessor Architecture" | Cache 章节 |

---

## 6. 编译与运行

```bash
cd Lab03_存储层次
make
./cache_sizes
./cache_line
./associativity
./tlb_hugepage
./false_sharing
./numa_effects
```

---

📌 **下一步**：完成 Lab03 后，进入 [`Lab04_超标量乱序/`](../Lab04_超标量乱序/)。在那里你将反推飞腾的微架构参数——寄存器重命名容量、ROB 大小、Issue Queue 深度。
