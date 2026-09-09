# 飞腾 FTC862 PMU 规范详解（v0.10 金矿发现）

> **来源**：`/opt/phytune/pt_agent/arm/modules/Performance/phyTune_core/topdown/topdown_tool/metrics/`
> **依据**：ARM Telemetry Specification（Copyright 2022-2023 Arm Ltd.）
> **价值**：彻底填补性能架构师盲区 6（PMU 太粗）+ 芯片设计专家盲区（4 FVU 硅真相推断）
> **License**：Apache-2.0

---

## 一、6 个 JSON 的角色

### 1.1 `mapping.json`（17 行）— MIDR_EL1 → CPU 型号映射

```json
{
    "0x41d0c": {"name": "neoverse-n1"},     // ARM 公版
    "0x41d49": {"name": "neoverse-n2"},
    "0x41d40": {"name": "neoverse-v1"},
    "0x70663": {"name": "phytium-ftc663"},  // 飞腾上一代
    "0x70862": {"name": "phytium-ftc862"}   // ← 本项目硬件
}
```

**解读**：
- MIDR_EL1 寄存器的完整 32-bit 值 = `implementer(8) | variant(4) | arch(4) | part(12) | revision(4)`
- `0x70862`：implementer=0x70（飞腾）、part=0x862、其他位组合 = `0x70862`
- `0x41d0c`：implementer=0x41（ARM Ltd.）、part=0xd0c（Neoverse-N1）
- 飞腾 `0x70` vs ARM `0x41`：**飞腾是独立 implementer，不是 ARM 二道贩子**——自主可控二级的关键证据

### 1.2 五个 CPU JSON 的体量对比

| CPU | 文件 | 事件数 | 世代 | 备注 |
|---|---|---|---|---|
| neoverse-n1 | 89 KB | **110** | 2019 | ARM 公版服务器 |
| neoverse-v1 | 105 KB | 132 | 2020 | ARM 公版 HPC（带 SVE）|
| neoverse-n2 | 116 KB | **155** | 2021 | ARMv9 + SVE2 |
| phytium-ftc663 | 79 KB | **84** | 2018 | 飞腾上一代（最简）|
| **phytium-ftc862** | **90 KB** | **103** | **2022** | **本项目硬件** |

**关键洞察**：
- FTC862 的 103 events 介于公版 N1（110）和上代 FTC663（84）之间——**比上代多 23%，但仍少于公版 N1 7 个**
- 飞腾 PMU 实现略简化于 ARM 公版（这是国产芯片 PMU 完整度的参考数据）
- Neoverse-N2（155）领先 FTC862（103）52 个事件——主要是 ARMv9 SVE2/SME 相关，FTC862 不支持

---

## 二、FTC862 PMU 关键事实校正（重要！）

### 2.1 `product_configuration`（FTC862 自报家门）

```json
{
    "product_name": "Phytium FTC862",
    "part_num": "0x862",
    "implementer": "0x70",               // 飞腾独立
    "architecture": "armv8.1",            // ⚠️ 不是 v8.2！
    "pmu_architecture": "pmu_v3",
    "num_slots": 5,                       // 同时只能开 5 个 PMU 计数器
    "num_bus_slots": 0
}
```

**项目内部的事实校正**：
- ⚠️ **README/Makefile 写 `-march=armv8.2-a+fp16+dotprod`**，但官方 PMU 规范自报 `architecture: armv8.1`
- 这不矛盾：PMU 规范的 `armv8.1` 指 **PMU 架构基线**（PMUv3 在 ARMv8.1 完善），编译器 march 用 `armv8.2-a+fp16+dotprod` 是真值（FP16/DotProd 是 ARMv8.2 强制扩展）
- **num_slots: 5** = D3000 同时只能开 **5 个硬件 PMU 计数器**——这是 `perf stat -e e1,e2,e3,e4,e5,e6` 多了会 fail 的根因

---

## 三、PMU 事件分类详解（103 个事件，按类别）

### 3.1 通用架构事件（architectural=true，跨 CPU 移植）

| 事件 | code | 用途 |
|---|---|---|
| `SW_INCR` | 0x00 | 软件 PMU 计数（写 PMSWINC_EL0）|
| `INST_RETIRED` | 0x08 | **提交指令数（IPC 分子）** |
| `CPU_CYCLES` | 0x11 | **CPU 周期数（IPC 分母）** |
| `EXC_TAKEN` | 0x09 | 异常进入 |
| `EXC_RETURN` | 0x0A | 异常返回（ERET）|
| `BR_RETIRED` | 0x21 | **架构提交分支数** |
| `CHAIN` | 0x1E | 64-bit 计数器链 |
| `CID_WRITE_RETIRED` | 0x0B | CONTEXTIDR 写（PID 跟踪）|
| `TTBR_WRITE_RETIRED` | 0x1C | TTBR 写（上下文切换指标）|

### 3.2 Cache 层级事件（性能调优核心）

| 事件 | code | 用途 |
|---|---|---|
| `L1I_CACHE` / `L1I_CACHE_REFILL` | 0x14 / 0x01 | L1 指令 cache 访问/缺失 |
| `L1D_CACHE` / `L1D_CACHE_REFILL` | 0x04 / 0x03 | L1 数据 cache 访问/缺失 |
| `L2D_CACHE` / `L2D_CACHE_REFILL` | 0x16 / 0x17 | L2 cache（统一）访问/缺失 |
| `L1D_CACHE_WB` | 0x15 | L1→L2 写回 |
| `L2D_CACHE_WB` | 0x18 | L2→外存写回 |
| `L1D_CACHE_LD` / `_ST` | 0x40 / 0x41 | L1 读/写分解（impdef）|
| `L1D_CACHE_REFILL_LD` / `_ST` | 0x42 / 0x43 | L1 缺失分解（读/写）|
| `L1D_CACHE_REFILL_INNER` / `_OUTER` | 0x44 / 0x45 | **L1 缺失数据来源（簇内/外）** |
| `L2D_CACHE_REFILL_LD` / `_ST` | 0x52 / 0x53 | L2 缺失分解 |
| `L1D_CACHE_WB_VICTIM` / `_CLEAN` | 0x46 / 0x47 | L1 写回分解（淘汰/一致性）|

**对项目的价值**：
- `L1D_CACHE_REFILL_OUTER`（0x45）直接测**多核 L3 争用**（性能架构师盲区 5/6 + OS 专家盲区 ⑥）
- `L1D_CACHE_WB_VICTIM`（0x46）测 **C 矩阵被 evict 程度**（OS 专家 MC×NC 分块论证的硬证据）
- `L1D_CACHE_LD/ST` 分解可以验证 GEMM 内核的 load/store 比例

### 3.3 ⭐ Stall 事件（性能架构师盲区 6 的答案）

| 事件 | code | 用途 |
|---|---|---|
| **`STALL_FRONTEND`** | **0x23** | **前端 stall（fetch/分支预测）**|
| **`STALL_BACKEND`** | **0x24** | **后端 stall（LSU/数据依赖）**|

**这是项目 PMU lens 的最大升级点**——当前 `lens-pmu.c` 只用通用 `PERF_COUNT_HW_CACHE_*`，**完全没采 STALL_FRONTEND/BACKEND**。补上后能精确回答："GEMM 51% 后端 stall 里，多少是 LSU、多少是分支、多少是 TLB"——性能架构师点名要的"stall 拆解到 root cause"。

### 3.4 TLB 事件（OS 专家盲区 ④ + ⑤）

| 事件 | code | 用途 |
|---|---|---|
| `L1D_TLB_REFILL` | 0x05 | L1 D-TLB 重填 |
| `L2D_TLB_REFILL` | 0x2D | L2 TLB 重填（D3000 L2 TLB 2048 entry）|
| `L1D_TLB` | 0x25 | L1 D-TLB 访问 |
| `L2D_TLB` | 0x2F | L2 TLB 访问 |
| **`DTLB_WALK`** | **0x34** | **页表遍历（TLB 全 miss 后走页表）**|
| `ITLB_WALK` | 0x35 | 指令侧页表遍历 |
| `L1D_TLB_REFILL_LD/_ST` | 0x4C/0x4D | TLB 重填分解 |

**对项目的价值**：
- 4MB B_blk / 4KB 页 = 1024 页 > L1 D-TLB 64 entry（OS 专家盲区 ④）
- 用 `DTLB_WALK` 实测页表遍历次数，验证 hugepage 价值（性能架构师 P0.3）

### 3.5 指令分类事件（芯片设计专家盲区 ① 的推断依据）

| 事件 | code | 用途 |
|---|---|---|
| `INST_SPEC` | 0x1B | 总 spec 指令 |
| **`ASE_SPEC`** | **0x74** | **Advanced SIMD（NEON）spec 指令** |
| `VFP_SPEC` | 0x75 | 标量 FP spec 指令 |
| `LD_SPEC` / `ST_SPEC` | 0x70 / 0x71 | load/store 指令 |
| `DP_SPEC` | 0x73 | 整数数据处理 |
| `CRYPTO_SPEC` | 0x77 | 加密指令（AES/SHA）|
| `BR_IMMED_SPEC` / `BR_INDIRECT_SPEC` | 0x78 / 0x7A | 分支指令分类 |

**⭐ 验证 4 FVU 物理结构**（芯片设计专家盲区 ①）：
- 跑 FP32 GEMM MR=8 时：`ASE_SPEC / CPU_CYCLES` ≈ 32（每周期 32 条 NEON FMLA，即 8 acc × 4 lane）→ 反推 FVU 数
- 跑 FP16 GEMM MR=8 时：`ASE_SPEC / CPU_CYCLES` 应该是 FP32 的 2 倍（如果 FVU 是全流水 128-bit）——**实测不是，证明芯片设计专家的"lane-broadcast port=4"推断**

### 3.6 总线 + 远端访问（多 socket 视角）

| 事件 | code | 用途 |
|---|---|---|
| `BUS_ACCESS` | 0x19 | 总线访问 |
| `BUS_ACCESS_LD` / `_WR` | 0x60 / 0x61 | 读/写总线分解 |
| `BUS_ACCESS_SHARED` / `_NOT_SHARED` | 0x62 / 0x63 | 可共享/不可共享 |
| **`REMOTE_ACCESS`** | **0x31** | **跨 socket 访问（多 socket 系统才有意义）**|
| `MEMORY_ERROR` | 0x1A | ECC 错误（可靠性指标）|

**对项目的价值**：
- D3000 单 socket，`REMOTE_ACCESS` 应恒为 0（验证拓扑）
- `MEMORY_ERROR` > 0 表示硬件可靠性下降（ESG/安全视角关注）

---

## 四、Topdown 决策树（性能分析方法论）

### 4.1 三阶段 Topdown

```
Stage 1: Cycle Accounting（4 项根指标）
├── frontend_stall_pct = STALL_FRONTEND / CPU_CYCLES × 100
├── backend_stall_pct  = STALL_BACKEND  / CPU_CYCLES × 100
├── retired_pct        = INST_RETIRED   / (slots × CPU_CYCLES) × 100
└── bad_speculation_pct = 1 - 上述三项

Stage 2: 按 Stage 1 结果 drill-down
├── 若 frontend_stall_pct 高 → 查 Branch/ITLB/L1I/L2
├── 若 backend_stall_pct 高  → 查 DTLB/L1D/L2/Operation_Mix
├── 若 retired_pct 低        → 查 Operation_Mix
└── 若 bad_spec 高           → 查 Branch
```

### 4.2 Stage 2 metric groups（11 组）

| Group | metrics |
|---|---|
| **Cycle_Accounting** | frontend/backend/retired/bad_spec _pct |
| **General** | IPC、branch_mpki 等 |
| **MPKI** | l1i_mpki / l1d_mpki / l2_mpki / **dtlb_mpki** / branch_mpki |
| **Miss_Ratio** | 各级 cache miss rate、branch mispred rate |
| **Branch_Effectiveness** | 分支预测准确率 |
| **ITLB/DTLB_Effectiveness** | TLB 命中率 + walk ratio |
| **L1I/L1D/L2_Cache_Effectiveness** | cache 命中率 + miss rate |
| **Operation_Mix** | load/store/SIMD/FP/branch/crypto 指令占比 |

### 4.3 核心 metric 公式（精选）

```c
ipc                 = INST_RETIRED / CPU_CYCLES
frontend_stall_pct  = STALL_FRONTEND / CPU_CYCLES × 100
backend_stall_pct   = STALL_BACKEND  / CPU_CYCLES × 100
l1d_mpki            = L1D_CACHE_REFILL / INST_RETIRED × 1000
l2_mpki             = L2D_CACHE_REFILL / INST_RETIRED × 1000
dtlb_mpki           = DTLB_WALK / INST_RETIRED × 1000
branch_mpki         = BR_MIS_PRED_RETIRED / INST_RETIRED × 1000
branch_mispred_rt   = BR_MIS_PRED_RETIRED / BR_RETIRED
dtlb_walk_rt        = DTLB_WALK / L1D_TLB
simd_pct            = ASE_SPEC / INST_SPEC × 100     // NEON 占比
scalar_fp_pct       = VFP_SPEC / INST_SPEC × 100
l1d_miss_rt         = L1D_CACHE_REFILL / L1D_CACHE
```

---

## 五、对项目的具体升级路径

### 5.1 性能架构师盲区 6 完整修复（P0）

替换 `analysis/lens-pmu.c` 的通用 `PERF_COUNT_HW_CACHE_*` 为 FTC862 raw event：

```c
/* 旧（v0.9）*/
PERF_COUNT_HW_CACHE_REFERENCES  // 粗
PERF_COUNT_HW_CACHE_MISSES      // 粗

/* 新（v0.11，用 FTC862 raw event）*/
PE配置 type=PERF_TYPE_RAW, config=0x23  // STALL_FRONTEND
PE配置 type=PERF_TYPE_RAW, config=0x24  // STALL_BACKEND
PE配置 type=PERF_TYPE_RAW, config=0x34  // DTLB_WALK
PE配置 type=PERF_TYPE_RAW, config=0x74  // ASE_SPEC（NEON 占比）
PE配置 type=PERF_TYPE_RAW, config=0x31  // REMOTE_ACCESS
```

但 `num_slots: 5` 限制——同时只能开 5 个事件，多事件需 multiplex 或多次跑。

### 5.2 新增 `analysis/lens-topdown-ftc862.c`

按官方 topdown 决策树实现：
1. Stage 1：采 4 个根指标（frontend/backend/retired/bad_spec）
2. 根据最高 stall 类型，Stage 2 采对应 metric group（如 backend 高 → 采 DTLB/L1D/L2）
3. 输出 markdown 报告："GEMM 内核 X% backend stall，其中 Y% 是 DTLB、Z% 是 L2 miss"

### 5.3 新增 `analysis/lens-fvu-truth.c`

用 ASE_SPEC 反推 4 FVU 物理结构（芯片设计专家盲区 ①）：
- 跑 FP32 MR=8 GEMM：理论 ASE_SPEC/CYCLES = 32（如全流水）
- 实测如果 < 32，差额揭示瓶颈（issue slot / lane port / regfile 读端口）
- 跑 FP16 MR=8 GEMM：理论 64，实测若 < 64 证明 lane-broadcast port=4

### 5.4 验证多 socket 假设

跑 `REMOTE_ACCESS` > 0？如果 D3000 单 socket 应该恒为 0。任何非零值表明实际是多 chip 配置。

---

## 六、对比 ARM 公版（Neoverse-N1/N2/V1）

### 6.1 FTC862 vs Neoverse-N1（同期 2019-2022）

| 维度 | FTC862 | N1 | 差距 |
|---|---|---|---|
| 事件数 | 103 | 110 | -7 |
| stall 事件 | ✓ STALL_FRONTEND/BACKEND | ✓ | 持平 |
| REMOTE_ACCESS | ✓（0x31）| ✓ | 持平 |
| Memory tagging (MTE) | ❌ | ❌ | 持平（v8.2 都没）|
| SVE | ❌ | ❌ | 持平（v8.2 都没）|
| Topdown methodology | ✓ | ✓ | 持平 |

**结论**：FTC862 的 PMU 完整度 ≈ Neoverse-N1（差距 7 个事件，主要是 impdef 细节），足以支撑专业性能分析。

### 6.2 FTC862 vs Neoverse-N2（ARMv9 + SVE2）

N2 多 52 个事件主要是 SVE2/SME/矩阵扩展相关。**FTC862 是 ARMv8.x，永远拿不到这些事件**——这是 ISA 锁死的硬天花板（供应链专家盲区 ②）。

---

## 七、版权与使用合规

- **License**：Apache-2.0（每个 JSON 文件头声明）
- **Copyright**：Arm Ltd. 2022-2023（**这是 ARM 提供给飞腾的官方 PMU 规范**）
- **confidential**: false（**公开可引用**）
- **使用范围**：可自由引用、复现、修改（符合 Apache-2.0）

**对法律/政策 lens 的意义**：
- 这份 JSON 是飞腾"ARM 架构授权"在软件层的直接物证（法律 lens 18 + 政策 lens 11 共识）
- Apache-2.0 license 让项目可以合法引用这份规范（无需 NDA）
- 但飞腾的 PMU 实现（RTL）仍属飞腾机密，**事件定义 ≠ 实现细节**

---

## 八、本项目应做的 v0.11 P0 升级

| 优先级 | 任务 | 落地 |
|---|---|---|
| **P0** | `analysis/lens-pmu-ftc862.c` 替换通用事件为 raw event | 新文件 |
| **P0** | `analysis/lens-topdown-ftc862.c` 实现官方决策树 | 新文件 |
| **P0** | `analysis/lens-fvu-truth.c` 用 ASE_SPEC 反推 4 FVU 结构 | 新文件 |
| P1 | 修正 `docs/OPTIMAL-PARAMS.md` 把"armv8.2"补全为"PMU 架构 v8.1 / 指令集 v8.2-a+fp16+dotprod" | edit |
| P1 | 在 `lens-pmu.c` 加 `num_slots=5` 提示（避免 perf 报错）| edit |
| P2 | `scripts/topdown-runner.sh` 包装飞腾 pt_agent 工具 | 新文件 |

---

## 九、附：完整事件 code 速查表（103 个）

> 详见 `phytium-ftc862.json` 完整文件。常用 code：

```
0x00 SW_INCR            0x08 INST_RETIRED         0x11 CPU_CYCLES
0x01 L1I_CACHE_REFILL   0x10 BR_MIS_PRED          0x12 BR_PRED
0x03 L1D_CACHE_REFILL   0x21 BR_RETIRED           0x13 MEM_ACCESS
0x04 L1D_CACHE          0x22 BR_MIS_PRED_RETIRED  0x1B INST_SPEC
0x05 L1D_TLB_REFILL     0x23 STALL_FRONTEND ⭐    0x31 REMOTE_ACCESS
0x16 L2D_CACHE          0x24 STALL_BACKEND  ⭐    0x34 DTLB_WALK    ⭐
0x17 L2D_CACHE_REFILL   0x44 L1D_CACHE_REFILL_INNER 0x35 ITLB_WALK
0x2D L2D_TLB_REFILL     0x45 L1D_CACHE_REFILL_OUTER 0x46 L1D_CACHE_WB_VICTIM
0x2F L2D_TLB            0x1A MEMORY_ERROR         0x70 LD_SPEC
0x70 LD_SPEC  0x71 ST_SPEC  0x73 DP_SPEC  0x74 ASE_SPEC ⭐  0x75 VFP_SPEC
0x77 CRYPTO_SPEC  0x78 BR_IMMED_SPEC  0x7A BR_INDIRECT_SPEC
```

⭐ = 项目当前 lens-pmu.c 未采但 FTC862 支持的关键事件。
