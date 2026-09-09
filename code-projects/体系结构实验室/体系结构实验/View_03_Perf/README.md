# View_03_Perf — 性能工程师视角（工具集）

> **切入问题**：给定一段慢代码，**怎么定位瓶颈、量化优化空间、逐级提升**？
>
> **主导思维**：先测量（不要瞎优化）→ 找瓶颈（Iron Law / Roofline）→ 改代码 → 验证。
> 这 3 个可运行 demo 演示性能工程师的 3 大常见场景。

---

## 1. matmul_evolution — 矩阵乘 8 步优化阶梯

源码 [`src/matmul_evolution.c`](./src/matmul_evolution.c)，跑 `make run`。

### 飞腾 D3000M 实测（N=512）

| Step | 方法 | T(ms) | GFLOPS | %peak |
|------|------|------:|-------:|------:|
| 0 | 朴素 i-j-k | 443.2 | 0.61 | 6.4% |
| 1 | 循环交换 i-k-j | 96.1 | 2.79 | 29.5% |
| 2 | 分块 32×32 | 118.7 | 2.26 | 23.9% |
| 3 | 循环展开 4× | 74.6 | 3.60 | 38.1% |
| 4 | NEON fmla | 32.3 | 8.32 | 88.1% |
| 5 | NEON + B 转置 | 30.6 | 8.77 | 92.8% |
| **6** | **tile 4×4 NEON** | **29.1** | **9.22** | **97.6%** |

**总加速**：**15×**（step 0 → step 6），达到理论峰值 9.45 GFLOPS 的 97.6%。

### 优化决策树
```
你写的循环慢 → 看 cache miss 高吗?
├─ 是 → 改循环顺序 (ijk → ikj) → +5×
│       └─ 还慢 → 看工作集 > L2? → 分块
└─ 否 → 看 IPC 低吗?
        ├─ 是 → 寄存器端口满? → 循环展开
        └─ 否 → 用 SIMD (NEON/SVE) → +2-4×
                └─ 已用 SIMD 但还慢 → tile 阻塞 → 接近 peak
```

### 关键洞察
- **缓存友好（step 1）比 SIMD（step 4）先做**：5× vs 1.5×
- **分块（step 2）反而比 step 1 慢**：因为 N=512 时 L2=512KB 工作集已 fit，分块开销 > 收益
- **NEON 不是终点**：step 4 → step 6 还有 11% 提升空间，靠 tile 4×4 复用

---

## 2. false_sharing — 多核 false sharing 警示

源码 [`src/false_sharing.c`](./src/false_sharing.c)。

### 实测（2 线程，每线程 1 亿次自增）
```
struct 大小: bad=8B, good=64B (cache line=64B)
false sharing (bad): 0.520 s
padding (good)      : 0.264 s
加速比              : 2.0×
```

**根因**：两个线程写各自 `value`，但 value 在同一 cache line（64B）。
任何线程写都会 invalidate 另一线程的本地 cache 副本，导致 cache line 在核间反复 ping-pong。

**修法**：
```c
// 错误
struct { long value; } shared[N_THREADS];

// 正确：补齐到 cache line
struct { long value; char pad[56]; } padded[N_THREADS];

// 或用 C11 alignas
struct { alignas(64) long value; } aligned[N_THREADS];
```

### 在飞腾上的实际影响
- 2 核 false sharing：~2× 慢
- 4 核：~4× 慢（cache line 在 4 核间轮转）
- 8 核：~6-8× 慢（线性恶化）

---

## 3. branch_patterns — 分支模式对性能的影响

源码 [`src/branch_patterns.c`](./src/branch_patterns.c)。

### 飞腾实测（10M 次分支判断）
```
pattern                T(ms)    ns/op
-------                ------   -----
never taken             12.0    1.20
always taken            12.0    1.20
periodic (1/4)          11.0    1.10
staircase (1/2)          8.2    0.82
random (50%)            12.0    1.20
```

**注意**：时间差异不显著——这是**现代分支预测器的强大副作用**！
飞腾的预测器把"never/always/random"都处理得很好，时间几乎一样。

**真实差异要看 branch-miss 计数**：
```bash
perf stat -e branches,branch-misses ./branch_patterns
```
预期：
- `never/always/periodic` → branch-misses < 0.1%
- `random` → branch-misses ~50%（每个分支都猜错一半）

### 教学结论
1. **不要用"循环里加 if"测分支开销**——编译器和预测器都很聪明
2. **真实分支开销**出现在：hash 表查询、二分搜索、链表遍历、间接调用
3. **缓解方法**：
   - 把 hot branch 放函数外（避免每次调用）
   - 用 `__builtin_expect` 提示编译器
   - 用 branchless 代码（如 `(cond << 31) >> 31` mask）

---

## 4. 跑这个视角

```bash
cd View_03_Perf
make run          # 跑全部 3 个 demo
# 或单独
./matmul_evolution
./false_sharing
./branch_patterns
```

📌 **下一步**：去 [Expert_09_Performance_Model](../Expert_09_Performance_Model/) 看 Roofline 模型如何预测这些性能数字的上限。
