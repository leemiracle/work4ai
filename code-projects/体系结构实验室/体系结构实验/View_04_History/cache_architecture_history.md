# Cache 架构代际演进史（1980s → 2025）

> **首席科学家视角**配套。Cache 是 50 年来研究最多的硬件结构之一。
> 每个现代 CPU 的多级 cache 都是这些 idea 的堆叠。

---

## 0. 一图概览

```
1968 ── Atlas 使用虚拟存储（最初概念）
  │
1980s ── 单级 D-cache（4KB direct-mapped）
  │
1990 ── 2 级：L1 内嵌 + L2 外挂 (i486)
  │
1995 ── L1 split：I-cache + D-cache 分离
  │
1998 ── L1 set-associative (2-way → 4-way → 8-way)
  │
2000 ── L2 on-die (Pentium III Coppermine)
  │
2003 ── L3 on-die (Intel Itanium 2)
  │
2005 ── Non-inclusive L3 (AMD K10)
  │
2010 ── Victim cache / 受害者 cache 普及
  │
2015 ── 3D-stacked cache (Hybrid Memory Cube)
  │
2017 ── Intel Mesh Interconnect（多 socket）
  │
2020 ── HBM 集成 cache (Intel Xeon Max)
  │
2022 ── AMD 3D V-Cache (SRAM 堆叠 in L3)
  │
2024 ── CXL memory expansion (cache-coherent 远程内存)
```

---

## 1. 关键设计维度

每个现代 cache 都是这 5 个维度的特定组合：

| 维度 | 选项 |
|------|------|
| **关联度** | direct-mapped / set-assoc (N-way) / fully-assoc |
| **替换策略** | LRU / pseudo-LRU / RRIP / SRRIP / DIP |
| **预取** | none / next-line / stride / stream / region |
| **包含策略** | inclusive / non-inclusive / exclusive |
| **写策略** | write-through / write-back / write-allocate |

---

## 2. 各代经典设计

### 2.1 direct-mapped（1980s 主流）
- **优点**：硬件最简单、低延迟
- **缺点**：conflict miss 高（多个地址映射同一 set）
- **代表**：早期 MIPS R2000 L1 (4KB direct-mapped)

### 2.2 set-associative（1990s 至今主流）
- 2-way → 4-way → 8-way → 12-way → 16-way
- **飞腾 D3000M**：L1 4-way / L2 8-way / L3 16-way（实测，[Lab00/arch_probe](../Lab00_测量基础设施/)）
- **trade-off**：way 数 ↑ → 命中率 ↑ + 延迟 ↑ + 功耗 ↑

### 2.3 Victim Cache（Jouppi 1990）
- **思想**：direct-mapped 主 cache + 小的 fully-assoc 辅 cache
- 主 cache evict 的数据进 victim cache，下次访问命中
- **效果**：直接映射 + victim 8 entry ≈ 4-way assoc 性能

### 2.4 Non-inclusive L3（AMD K10 / Intel Skylake-SP）
- **思想**：L2 数据不在 L3（独立存储）
- **优点**：省容量（不重复存）
- **缺点**：coherence 复杂
- **飞腾 D3000M 推测**：L3 是 inclusive（共享）或 non-inclusive

### 2.5 3D-stacked Cache（2020s 新趋势）
- **代表 1**：**AMD 3D V-Cache**（Zen 3+）
  - 在 CPU die 上堆 64MB SRAM
  - 通过 TSV (Through-Silicon Via) 连接
  - 游戏 +15-30% 性能
- **代表 2**：**Intel Xeon Max**（Sapphire Rapids HBM）
  - 集成 HBM2e 当 L4 cache
  - HPC 工作负载 +3-5×
- **飞腾现状**：无 3D cache，下一代 D4000 可能加

### 2.6 CXL Memory Expansion（2022+）
- **思想**：用 CXL 协议把远端内存当本地 cache
- 解决单 socket 内存容量上限
- 飞腾下一代推测会加 CXL 2.0

---

## 3. 预取策略代际

| 年代 | 策略 | 描述 |
|------|------|------|
| 1990s | next-line | 访问 line N 时预取 N+1 |
| 2000s | stride | 检测 stride 访问（A[0], A[8], A[16]）预取下一个 |
| 2010s | stream / region | 大块连续预取 |
| 2020s | ML-based | 用神经网络预测（研究阶段）|

---

## 4. Cache Coherence 代际

| 代 | 协议 | 代表 |
|---|------|------|
| 1980s | **MSI** (Modified/Shared/Invalid) | 早期单总线 |
| 1990s | **MESI** (加 Exclusive) | x86 / ARM 普遍使用 |
| 2000s | **MOESI** (加 Owned) | AMD / ARM big.LITTLE |
| 2010s | **MESIF** (加 Forward) | Intel 至强系列 |
| 2020s | **directory-based** | 大型 NUMA / DC |

**飞腾 D3000M**：推测 MESI 或 MOESI 变种（ARM 标配）。

---

## 5. 飞腾 D3000M 的 cache 在历史中的位置

| 层级 | 飞腾 | 历史对比 |
|------|------|---------|
| L1 D | 64KB / 4-way / 1.6 ns | 与 ARM Cortex-X3 同代 |
| L2 | 512KB / 8-way / 4.8 ns | 比 Intel/AMD 1MB+ 略小 |
| L3 | 8MB shared / 16-way / 14 ns | 比 Intel 105MB LLC 小得多 |

**评级**：飞腾 D3000M 的 cache 是**主流跟随**（90% 同代水平），不是**领先**。

---

## 6. 参考文献

1. Smith, "Cache Memories" (ACM Computing Surveys 1982)
2. Hennessy & Patterson, *CAQA* Ch2 + Appendix B
3. Jouppi, "Improving Direct-Mapped Cache Performance" (ISCA 1990) — Victim Cache
4. Qureshi et al., "Adaptive Insertion Policies" (ISCA 2007) — DIP
5. Qureshi et al., "A Case for MLP-Aware Cache Replacement" (ISCA 2006)
6. AMD 3D V-Cache whitepaper (2022)
7. CXL 3.0 Specification (2022)

📌 **下一步**：[isa_history.md](./isa_history.md) 看 ISA 的兴衰史。
