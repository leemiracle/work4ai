# A64 System Instructions — Cache/TLB/Barrier/Address Translation


> **生成日期**：2026-06-29  
> **PDF 源版本**：ARM DDI 0487G.b (2021-07)  
> **数据来源**：[`isa_instructions_v7.json`](https://example.com) — 755 条指令 / 36 FEAT，PyMuPDF 全自动提取  
> **飞腾实测平台**：D3000M (FTC862) @ 2.5 GHz, ARMv8.4-A

> 本文件是 [`isa_reference/`](./README.md) 系列之一。所有指令基于 ARM ARM DDI 0487G.b (2021-07)。

---

## 目录

- [0. 一句话](#0-一句话)

- [1. 现象：为什么需要它？](#1-现象为什么需要它)

- [2. 引入版本 & 飞腾状态](#2-引入版本--飞腾状态)

- [3. 指令清单总表（16 条）](#3-指令清单总表)

- [4. 每条指令详解](#4-每条指令详解按章节顺序)

  - 4.1 `AT`
  - 4.2 `MRS`
  - 4.3 `MSR`
  - 4.4 `MSR`
  - 4.5 `SEV`
  - 4.6 `SEVL`
  - 4.7 `TLBI`
  - 4.8 `WFE`
  - ...（共 16 条）
- [5. 实测代码](#5-实测代码)

- [6. 性能预期](#6-性能预期飞腾-d3000m--25-ghz)

- [7. 缺陷与陷阱](#7-缺陷与陷阱)

- [8. 进一步阅读](#8-进一步阅读)


---

## 0. 一句话

DMB/DSB/ISB/DC/IC/AT/TLBI —— 内存模型、cache 维护、地址翻译的硬件控制指令。


---
## 1. 现象：为什么需要它？

**内存序屏障**（Lab06 核心）：
```asm
DMB ST     ; Data Memory Barrier, 所有 store 完成后才能继续
DMB SY     ; 全屏障（最强）
DSB ST     ; Data Synchronization Barrier, store 真正可见后才继续（比 DMB 强）
ISB        ; Instruction Synchronization Barrier, flush 流水线 / 序列化
```

**Cache 维护**（Lab03）：
```asm
DC CIVAC, [x0]   ; Clean+Invalidate by VA to PoC
DC CVAC, [x0]    ; Clean by VA to PoC
DC ZVA, [x0]     ; Zero by VA (DC ZVA, 一段 cache line 清零)
IC IVAU, [x0]    ; Invalidate I-cache by VA (JIT 用)
IC IALLU         ; Invalidate entire I-cache (flush all)
```

**地址翻译**（虚拟 → 物理）：
```asm
AT S1E1R, [x0]   ; Translate VA (EL1 read) → 看 PAR_EL1 结果
```

**TLB 维护**：
```asm
TLBI ASIDE1IS, x0  ; Invalidate by ASID at EL1
TLBI VAE1, x0      ; Invalidate by VA at EL1
TLBI ALLE1IS       ; Invalidate all (EL1)
```


---
## 2. 引入版本 & 飞腾状态

**版本**：ARMv8.0-A mandatory（基线）。


**飞腾 D3000M 状态**：

飞腾 D3000M 全部支持。注意：用户态（EL0）只能用 DMB/DSB/ISB，DC/IC/AT/TLBI 需要 EL1。


**杀手级应用**：内存序控制 / JIT cache flush / OS 内存管理 / 虚拟化


---
## 3. 指令清单总表（16 条）

| 助记符 | 变体 | 章节号 | ARM 页 | PDF 页 | 别名 / 被别名 |

|--------|------|--------|--------|--------|---------------|

| `AT` | - | C6.2.19 | C6-911 | p911 | alias→SYS |

| `MRS` | - | C6.2.194 | C6-1236 | p1236 |  |

| `MSR (immediate)` | immediate | C6.2.195 | C6-1237 | p1237 |  |

| `MSR (register)` | register | C6.2.196 | C6-1240 | p1240 |  |

| `SEV` | - | C6.2.238 | C6-1312 | p1312 |  |

| `SEVL` | - | C6.2.239 | C6-1313 | p1313 |  |

| `TLBI` | - | C6.2.332 | C6-1487 | p1487 | alias→SYS |

| `WFE` | - | C6.2.348 | C6-1512 | p1512 |  |

| `WFI` | - | C6.2.350 | C6-1514 | p1514 |  |

| `YIELD` | - | C6.2.354 | C6-1519 | p1519 |  |

| `DC` | - | C6.2.75 | C6-1007 | p1007 | alias→SYS |

| `DMB` | - | C6.2.80 | C6-1013 | p1013 |  |

| `DSB` | - | C6.2.82 | C6-1016 | p1016 |  |

| `HINT` | - | C6.2.92 | C6-1032 | p1032 |  |

| `IC` | - | C6.2.95 | C6-1036 | p1036 | alias→SYS |

| `ISB` | - | C6.2.97 | C6-1039 | p1039 |  |


---

## 3.5 系统指令的 Option 详表（飞腾 D3000M 实测可用）

> 这些指令本身只是助记符，**真正的语义在 `<option>` 里**。例如 `DMB ISHST` 和 `DMB SY` 是同一条指令的两种不同 CRm 编码，但语义截然不同。

### 3.5.1 DMB（Data Memory Barrier）— 12 种 option

内存屏障：保证 barrier **之前**和**之后**的内存访问在系统其他观察者眼中的可见顺序。

| Option | CRm | 共享域 | 访问类型 | 何时使用 |
|--------|-----|-------|---------|---------|
| `DMB SY` | `0b1111` | Full system | All (R+W) | **最强屏障**，C++ seq_cst，TLS handshake |
| `DMB ST` | `0b1110` | Full system | Stores only | "之前的 store 都可见"（最常用） |
| `DMB LD` | `0b1101` | Full system | Loads (pre) / All (post) | 较少用 |
| `DMB ISH` | `0b1011` | Inner Shareable | All | 多核同 OS 场景（默认） |
| `DMB ISHST` | `0b1010` | Inner Shareable | Stores only | **pthread mutex 解锁路径** |
| `DMB ISHLD` | `0b1001` | Inner Shareable | Loads / All | 较少用 |
| `DMB NSH` | `0b0111` | Non-shareable | All | 单核场景 |
| `DMB NSHST` | `0b0110` | Non-shareable | Stores only | 单核 store-store |
| `DMB NSHLD` | `0b0101` | Non-shareable | Loads / All | 较少用 |
| `DMB OSH` | `0b0011` | Outer Shareable | All | 跨 OS / cluster |
| `DMB OSHST` | `0b0010` | Outer Shareable | Stores only | device DMA 同步 |
| `DMB OSHLD` | `0b0001` | Outer Shareable | Loads / All | 较少用 |

**速记**：
- 后缀 `ST` = Store-Store / `LD` = Load-Load / 无 = All
- 前缀 `ISH` = Inner Shareable（同 OS 多核）/ `OSH` = Outer Shareable（跨 cluster）/ `NSH` = Non-shareable（单核）/ `SY` = Full system

**C++ memory_order 映射**：
- `memory_order_relaxed` → 无屏障（普通 LDR/STR）
- `memory_order_consume/acquire` → 不需要 DMB（LDAR/LDAPR 自带 acquire）
- `memory_order_release` → 不需要 DMB（STLR 自带 release）
- `memory_order_acq_rel` → LDAR+STLR
- **`memory_order_seq_cst` → DMB ISH（最常见）或 DMB SY**

### 3.5.2 DSB（Data Synchronization Barrier）— 同 DMB 12 种 option

DSB 比 DMB **更强**：DMB 只保证"顺序"，DSB **等待所有访问完成**才执行后续指令。

| Option | 何时使用 |
|--------|---------|
| `DSB SY` | 切换 EE/上下文 / 启动 DMA 前 |
| `DSB ST` | 较少用（一般直接 DSB SY） |
| `DSB ISH` | 多核 spin lock 退出 |
| `DSB ISHST` | write-combine buffer flush |
| `DSB OSH` | PCIe MMIO 完成确认 |
| `DSB NSH` | 单核场景 |

**`DSB nXS` (v8.7 FEAT_XS)**：弱化版 DSB，不等待设备侧。

### 3.5.3 ISB（Instruction Synchronization Barrier）— 1 种 option

| Option | 何时使用 |
|--------|---------|
| `ISB` (= `ISB SY`, CRm=`0b1111`) | flush 流水线 + 序列化 |

ISB **没有真的 ISH/OSH 变体**——CRm 其他值 reserved。ISB 等价于：清空流水线 + 强制后续指令重新取指。

**核心使用场景**：
1. 修改 CPACR/TCR/SCTLR 等系统寄存器后（让修改生效）
2. JIT 代码生成后（清 I-cache 影响）
3. 异常返回（ERET 前）
4. CPU hotplug / 频率切换
5. speculation barrier（防止分支预测器污染）

### 3.5.4 DC（Data Cache operation）— 7 类用户态可用 + 14 类 set/way

| Option | 操作 | 用途 | 飞腾可用 |
|--------|------|------|---------|
| `DC IVAC, <Xt>` | Invalidate by VA to PoC | 丢弃 cache line（让下次读从内存） | EL1+ |
| `DC CIVAC, <Xt>` | Clean+Invalidate by VA to PoC | 写回脏数据 + 丢弃 cache line | EL1+ |
| `DC CVAC, <Xt>` | Clean by VA to PoC | 仅写回脏数据 | EL1+（v8.1 起用户态可访问 with SCTLR.Elite） |
| `DC CVAU, <Xt>` | Clean by VA to PoU | 写回脏数据到统一 cache 点（JIT 共享 I/D cache） | EL0/EL1 |
| `DC ZVA, <Xt>` | Zero by VA | **整个 cache line 清零（不读内存）** | EL0/EL1（**用户态可用，性能优化神器**） |
| `DC CVAP, <Xt>` | Clean by VA to Point of Persistence | 持久化内存 flush (v8.2+) | EL1+ |
| `DC CVADP, <Xt>` | Clean by VA to Point of Deep Persistence | 更深持久化点 (v8.6+) | EL1+ |

**Set/Way 操作（OS 内存管理用）**：
- `DC ISW` / `DC CSW` / `DC CISW` (set/way invalidate/clean)
- `DC IGVAC` / `DC CGVAC` / `DC CIGVAC` (v8.4 新增)
- `DC IGDVAC` / `DC CGDVAC` / `DC CIGDVAC` (v8.4)
- `DC IGVADP` / `DC CGVADP` (v8.6)
- `DC IGDSW` / `DC CGDSW` / `DC CIGDSW` (v8.4)
- `DC IGDPSW` / `DC CGDPSW` / `DC CIGDPSW` (v8.6)

**用户态关键指令：`DC ZVA`**（飞腾 D3000M 实测可用）
```c
// 把 [x0, x0+64) 整个 cache line 清零，不读 DDR
// 比手动 memset 1.5-3× 快（大块时）
#include <arm_acle.h>
__dc_zva(p);   // 需要 SCTLR.Elite = 1，飞腾默认开
// 内联汇编版
asm volatile("dc zva, %[p]" :: [p] "r"(p) : "memory");
```

### 3.5.5 IC（Instruction Cache operation）— 3 种 option

| Option | 操作 | 何时使用 |
|--------|------|---------|
| `IC IVAU, <Xt>` | Invalidate I-cache by VA to PoU | **JIT 写完代码后必须调用**（让新代码对 I-cache 可见） |
| `IC IALLU` | Invalidate All (local) | 进程切换（清掉旧进程的 I-cache） |
| `IC IALLUIS` | Invalidate All Inner Shareable | 跨核 invalidate（IPI 场景） |

**JIT 完整序列**（飞腾上 v8 / SpiderMonkey / Libffi 用）：
```asm
STR  x0, [code_addr]      ; 1. 写机器码到内存
DC   CVAU, [code_addr]    ; 2. Clean D-cache 让其他观察者可见
DSB  ISH                   ; 3. 等待 clean 完成
IC   IVAU, [code_addr]    ; 4. Invalidate I-cache 对应行
DSB  ISH                   ; 5. 等待 IC 完成
ISB                        ; 6. 强制重新取指
```

少一步 → I-cache 看到旧代码 → 神秘崩溃。

### 3.5.6 TLBI（TLB Invalidate）— 70+ 种 option

TLB 维护指令**非常多**（不同 EL、不同范围、不同 shareability）。飞腾 D3000M 用户态基本用不到，OS 内核用。

**主要类别**（按 EL 划分）：

| 类别 | 代表 option | 用途 |
|------|------------|------|
| **EL1 (Linux kernel)** | `TLBI VAE1` / `TLBI ASIDE1` / `TLBI ALLE1` | 进程切换 / munmap / fork |
| **EL2 (Hypervisor)** | `TLBI IPAS2E1` / `TLBI ALLE2` / `TLBI VMALLS12E1` | KVM guest 切换 / Stage-2 page table |
| **EL3 (Secure monitor)** | `TLBI ALLE3` / `TLBI VAE3` | TrustZone 切换 |
| **Common** | `TLBI VMALLE1IS` | 全局 / 跨核 |

**后缀含义**：
- `IS` = Inner Shareable（IPI 广播到所有核）
- `OS` = Outer Shareable（v8.4 FEAT_TLBIOS，更高效）
- 无后缀 = local（仅当前核）
- `R` (range, v8.7 FEAT_TLRANGE) = 范围批量 invalidation

**典型内核代码**：
```c
// 进程切换时刷 EL1 TLB
asm volatile("tlbi vmalle1is" ::: "memory");  // 全核广播
dsb nsh;
isb;
```

### 3.5.7 AT（Address Translation）— 8 种 option

把虚拟地址翻译成物理地址，结果放在 `PAR_EL1`。

| Option | EL | 用途 |
|--------|-----|------|
| `AT S1E1R, <Xt>` | EL1 read | 翻译 EL1 stage-1 read VA |
| `AT S1E1W, <Xt>` | EL1 write | 翻译 EL1 stage-1 write VA（含 write 权限检查） |
| `AT S1E2R` / `AT S1E2W` | EL2 | Hypervisor 翻译 |
| `AT S12E1R` / `AT S12E1W` | EL1 | 走 stage-1+stage-2（虚拟化） |
| `AT S1E3R` / `AT S1E3W` | EL3 | Secure monitor 翻译 |

**典型用法**（内核 page fault handler）：
```asm
AT   S1E1R, [x0]     ; 翻译 x0 处的 VA
MRS  x1, PAR_EL1     ; 读结果
; PAR_EL1.PA = 物理地址
; PAR_EL1.F = 失败位
```

### 3.5.8 PRFB/PRFM/PRFW/PRFD（Prefetch Memory, v8.0+）— 5 种 option

虽然不是 DMB/DC 类，但属于"内存系统指令"。 prefetch 给 MMU 提示。

| Option | 含义 |
|--------|------|
| `PLDL1KEEP` | Prefetch Load to L1, keep (temporal) |
| `PLDL1STRM` | Prefetch Load to L1, stream (non-temporal) |
| `PLDL3KEEP` | Prefetch Load to L3, keep |
| `PLDL3STRM` | Prefetch Load to L3, stream |
| `PSTL1KEEP/STRM/PSTL3KEEP/STRM` | Prefetch Store 系列 |

**用法**：
```c
// 软件预取（飞腾 D3000M 实测有效，~1 cycle latency 隐藏）
asm volatile("prfm pldl1keep, [%[addr]]" :: [addr] "r"(addr));
```

---

## 4. 每条指令详解（按章节顺序）


### 4.1 `AT` (C6.2.19)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：Address Translate. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399.


**汇编模板**：
```
AT <at_op>, <Xt>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<at_op>` | Is an AT instruction name, as listed for the AT system instruction group, encoded in the "op1:CRm<0>:op2" field. It can  |

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rt" field. 1 1 0 1 0 1 0 1 0 0 0 0 1 op1 0 1  |


</details>


*PDF 跨页*：p911-p913（共 3 页）


### 4.2 `MRS` (C6.2.194)

**语义**：Move System Register allows the PE to read an AArch64 System register into a general-purpose register.


**汇编模板**：
```
MRS <Xt>, (<systemreg>|S<op0>_<op1>_<Cn>_<Cm>_<op2>)
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
AArch64.CheckSystemAccess('1':o0, op1, CRn, CRm, op2, Rt, L); 
  
 integer t = UInt(Rt); 
  
 integer sys_op0 = 2 + UInt(o0); 
 integer sys_op1 = UInt(op1); 
 integer sys_op2 = UInt(op2); 
 integer sys_crn = UInt(CRn); 
 integer sys_crm = UInt(CRm);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
X[t] = AArch64.SysRegRead(sys_op0, sys_op1, sys_crn, sys_crm, sys_op2);
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<Xt>` | Is the 64-bit name of the general-purpose destination register, encoded in the "Rt" field. |

| `<systemreg>` | Is a System register name, encoded in the "o0:op1:CRn:CRm:op2". The System register names are defined in Chapter D13 AAr |

| `<op0>` | Is an unsigned immediate, encoded in the "o0" field. It can have the following values: 2 when o0 = 0 3 when o0 = 1 |

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cn>` | Is a name 'Cn', with 'n' in the range 0 to 15, encoded in the "CRn" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |


</details>


*PDF 跨页*：p1236-p1237（共 2 页）


### 4.3 `MSR (immediate)` (C6.2.195)

**语义**：Move immediate value to Special Register moves an immediate value to selected bits of the PSTATE. For more information, see PSTATE.


**汇编模板**：
```
MSR <pstatefield>, #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
if op1 == '000' && op2 == '000' then SEE "CFINV"; 
 if op1 == '000' && op2 == '001' then SEE "XAFLAG"; 
 if op1 == '000' && op2 == '010' then SEE "AXFLAG"; 
  
 AArch64.CheckSystemAccess('00', op1, '0100', CRm, op2, '11111', '0'); 
 bits(2) min_EL; 
 boolean need_secure = FALSE; 
  
 case op1 of 
     when '00x' 
         min_EL = EL1; 
     when '010' 
         min_EL = EL1; 
     when '011' 
         min_EL = EL0; 
     when '100' 
         min_EL = EL2; 
     when '101' 
         if !HaveVirtHostExt() then 
             UNDEFINED; 
         min_EL = EL2; 
     when '110' 
         min_EL = EL3; 
     when '111' 
         min_EL = EL1; 
         need_secure = TRUE; 
  
 if UInt(PSTATE.EL) < UInt(min_EL) || (need_secure && !IsSecure()) then 
     UNDEFINED; 
  
 PSTATEField field; 
 case op1:op2 of 
     when '000 011' 
         if !HaveUAOExt() then 
1
1
0
1
0
1
0
1
0
0
0
0
0
op1
0
1
0
0
CRm
op2
1
1
1
1
1
31 30 29 28 27 26 25 24 23 22 21 20 19 18
16 15 14 13 12 11
8
7
5
4
3
2
1
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
C6-1238
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
ARM DDI 0487G.b
Non-Confidential
ID072021
             UNDEFINED; 
         field = PSTATEField_UAO; 
     when '000 100' 
         if !HavePANExt() then 
             UNDEFINED; 
         field = PSTATEField_PAN; 
     when '000 101' field = PSTATEField_SP; 
     when '011 010' 
         if !HaveDITExt() then 
             UNDEFINED; 
         field = PSTATEField_DIT; 
     when '011 100' 
         if !HaveMTEExt() then 
             UNDEFINED; 
         field = PSTATEField_TCO; 
     when '011 110' field = PSTATEField_DAIFSet; 
     when '011 111' field = PSTATEField_DAIFClr; 
     when '011 001' 
         if !HaveSSBSExt() then 
             UNDEFINED; 
         field = PSTATEField_SSBS; 
     otherwise UNDEFINED; 
  
 // Check that an AArch64 MSR/MRS access to the DAIF flags is permitted 
 if PSTATE.EL == EL0 && field IN {PSTATEField_DAIFSet, PSTATEField_DAIFClr} then 
     if !ELUsingAArch32(EL1) && ((EL2Enabled() && HCR_EL2.<E2H,TGE> == '11') || SCTLR_EL1.UMA == '0') 
then 
         if EL2Enabled() && !ELUsingAArch32(EL2) && HCR_EL2.TGE == '1' then 
             AArch64.SystemAccessTrap(EL2, 0x18); 
         else 
             AArch64.SystemAccessTrap(EL1, 0x18);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
case field of
```

</details>


*PDF 跨页*：p1237-p1240（共 4 页）


### 4.4 `MSR (register)` (C6.2.196)

**语义**：Move general-purpose register to System Register allows the PE to write an AArch64 System register from a general-purpose register.


**汇编模板**：
```
MSR (<systemreg>|S<op0>_<op1>_<Cn>_<Cm>_<op2>), <Xt>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
AArch64.CheckSystemAccess('1':o0, op1, CRn, CRm, op2, Rt, L); 
  
 integer t = UInt(Rt); 
  
 integer sys_op0 = 2 + UInt(o0); 
 integer sys_op1 = UInt(op1); 
 integer sys_op2 = UInt(op2); 
 integer sys_crn = UInt(CRn); 
 integer sys_crm = UInt(CRm);
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
AArch64.SysRegWrite(sys_op0, sys_op1, sys_crn, sys_crm, sys_op2, X[t]);
```

</details>


<details><summary>Assembler symbols / 操作数含义（7 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<systemreg>` | Is a System register name, encoded in the "o0:op1:CRn:CRm:op2". The System register names are defined in Chapter D13 AAr |

| `<op0>` | Is an unsigned immediate, encoded in the "o0" field. It can have the following values: 2 when o0 = 0 3 when o0 = 1 |

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cn>` | Is a name 'Cn', with 'n' in the range 0 to 15, encoded in the "CRn" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |

| `<Xt>` | Is the 64-bit name of the general-purpose source register, encoded in the "Rt" field. |


</details>


*PDF 跨页*：p1240-p1241（共 2 页）


### 4.5 `SEV` (C6.2.238)

**语义**：Send Event is a hint instruction. It causes an event to be signaled to all PEs in the multiprocessor system. For more information, see Wait for Event mechanism and Send event on page D1-2536.


**汇编模板**：
```
SEV
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
SendEvent();
```

</details>


*PDF 跨页*：p1312-p1313（共 2 页）


### 4.6 `SEVL` (C6.2.239)

**语义**：Send Event Local is a hint instruction that causes an event to be signaled locally without requiring the event to be signaled to other PEs in the multiprocessor system. It can prime a wait-loop which starts with a WFE instruction.


**汇编模板**：
```
SEVL
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
SendEventLocal();
```

</details>


*PDF 跨页*：p1313-p1314（共 2 页）


### 4.7 `TLBI` (C6.2.332)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：TLB Invalidate operation. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399.


**汇编模板**：
```
TLBI <tlbi_op>{, <Xt>}
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（4 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |

| `<tlbi_op>` | Is a TLBI instruction name, as listed for the TLBI system instruction group, encoded in the "op1:CRm:op2" field. It can  |


</details>


*PDF 跨页*：p1487-p1490（共 4 页）


### 4.8 `WFE` (C6.2.348)

**语义**：Wait For Event is a hint instruction that indicates that the PE can enter a low-power state and remain there until a wakeup event occurs. Wakeup events include the event signaled as a result of executing the SEV instruction on any PE in the multiprocessor system. For more information, see Wait for Event mechanism and Send event on page D1-2536.


**汇编模板**：
```
WFE
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
Hint_WFE(-1, WFxType_WFE);
```

</details>


*PDF 跨页*：p1512-p1513（共 2 页）


### 4.9 `WFI` (C6.2.350)

**语义**：Wait For Interrupt is a hint instruction that indicates that the PE can enter a low-power state and remain there until a wakeup event occurs. For more information, see Wait For Interrupt on page D1-2540.


**汇编模板**：
```
WFI
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
Hint_WFI(-1, WFxType_WFI);
```

</details>


*PDF 跨页*：p1514-p1515（共 2 页）


### 4.10 `YIELD` (C6.2.354)

**语义**：YIELD is a hint instruction. Software with a multithreading capability can use a YIELD instruction to indicate to the PE that it is performing a task, for example a spin-lock, that could be swapped out to improve overall system performance. The PE can use this hint to suspend and resume multiple software threads if it supports the capability.


**汇编模板**：
```
YIELD
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// Empty.
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
Hint_Yield();
```

</details>


*PDF 跨页*：p1519-p1522（共 4 页）


### 4.11 `DC` (C6.2.75)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：Data Cache operation. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399.


**汇编模板**：
```
DC <dc_op>, <Xt>
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<dc_op>` | Is a DC instruction name, as listed for the DC system instruction group, encoded in the "op1:CRm:op2" field. It can have |


</details>


*PDF 跨页*：p1007-p1009（共 3 页）


### 4.12 `DMB` (C6.2.80)

**语义**：Data Memory Barrier is a memory barrier that ensures the ordering of observations of memory accesses, see Data Memory Barrier (DMB) on page B2-147.


**汇编模板**：
```
DMB <option>|#<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
case CRm<3:2> of 
     when '00' domain = MBReqDomain_OuterShareable; 
     when '01' domain = MBReqDomain_Nonshareable; 
     when '10' domain = MBReqDomain_InnerShareable; 
     when '11' domain = MBReqDomain_FullSystem; 
 case CRm<1:0> of 
     when '00' types = MBReqTypes_All; domain = MBReqDomain_FullSystem; 
     when '01' types = MBReqTypes_Reads; 
     when '10' types = MBReqTypes_Writes; 
     when '11' types = MBReqTypes_All;
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
DataMemoryBarrier(domain, types);
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<option>` | Specifies the limitation on the barrier operation. Values are: SY Full system is the required shareability domain, reads |


</details>


*PDF 跨页*：p1013-p1015（共 3 页）


### 4.13 `DSB` (C6.2.82)

**语义**：Data Synchronization Barrier is a memory barrier that ensures the completion of memory accesses, see Data Synchronization Barrier (DSB) on page B2-150.


**汇编模板**：
```
DSB <option>|#<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
boolean nXS = FALSE; 
  
 case CRm of 
     when '0000' alias = DSBAlias_SSBB; 
     when '0100' alias = DSBAlias_PSSBB; 
     otherwise alias = DSBAlias_DSB; 
  
 case CRm<3:2> of 
     when '00' domain = MBReqDomain_OuterShareable; 
     when '01' domain = MBReqDomain_Nonshareable; 
     when '10' domain = MBReqDomain_InnerShareable; 
     when '11' domain = MBReqDomain_FullSystem; 
 case CRm<1:0> of 
     when '00' types = MBReqTypes_All; domain = MBReqDomain_FullSystem; 
     when '01' types = MBReqTypes_Reads; 
     when '10' types = MBReqTypes_Writes; 
     when '11' types = MBReqTypes_All; 
Memory nXS barrier
(FEAT_XS)
Encoding
DSB <option>nXS|#<imm>
Decode for this encoding
 if !HaveFeatXS() then UNDEFINED; 
 MBReqTypes types = MBReqTypes_All; 
 boolean nXS = TRUE; 
 DSBAlias alias = DSBAlias_DSB; 
  
 case imm2 of 
1
1
0
1
0
1
0
1
0
0
0
0
0
0
1
1
0
0
1
1
CRm
1
0
0
1
1
1
1
1
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11
8
7
6
5
4
3
2
1
0
opc
1
1
0
1
0
1
0
1
0
0
0
0
0
0
1
1
0
0
1
1 imm2 1
0
0
0
1
1
1
1
1
1
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9
8
7
6
5
4
3
2
1
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
ARM DDI 0487G.b
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
C6-1017
ID072021
Non-Confidential
     when '00' domain = MBReqDomain_OuterShareable; 
     when '01' domain = MBReqDomain_Nonshareable; 
     when '10' domain = MBReqDomain_InnerShareable; 
     when '11' domain = MBReqDomain_FullSystem; 
Alias conditions
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<option>` | For the memory barrier variant: specifies the limitation on the barrier operation. Values are: SY Full system is the req |


</details>


*PDF 跨页*：p1016-p1019（共 4 页）


### 4.14 `HINT` (C6.2.92)

**语义**：Hint instruction is for the instruction set space that is reserved for architectural hint instructions.


**汇编模板**：
```
HINT #<imm>
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
SystemHintOp op; 
  
 case CRm:op2 of 
     when '0000 000' op = SystemHintOp_NOP; 
     when '0000 001' op = SystemHintOp_YIELD; 
     when '0000 010' op = SystemHintOp_WFE; 
     when '0000 011' op = SystemHintOp_WFI; 
     when '0000 100' op = SystemHintOp_SEV; 
     when '0000 101' op = SystemHintOp_SEVL; 
     when '0000 110' 
         if !HaveDGHExt() then EndOfInstruction();    // Instruction executes as NOP 
         op = SystemHintOp_DGH; 
     when '0000 111' SEE "XPACLRI"; 
     when '0001 xxx' 
         case op2 of 
             when '000' SEE "PACIA1716"; 
             when '010' SEE "PACIB1716"; 
             when '100' SEE "AUTIA1716"; 
             when '110' SEE "AUTIB1716"; 
             otherwise EndOfInstruction(); 
     when '0010 000' 
         if !HaveRASExt() then EndOfInstruction();    // Instruction executes as NOP 
         op = SystemHintOp_ESB; 
     when '0010 001' 
         if !HaveStatisticalProfiling() then EndOfInstruction();    // Instruction executes as NOP 
         op = SystemHintOp_PSB; 
     when '0010 010' 
         if !HaveSelfHostedTrace() then EndOfInstruction();    // Instruction executes as NOP 
         op = SystemHintOp_TSB; 
     when '0010 100' 
         op = SystemHintOp_CSDB; 
     when '0011 xxx' 
         case op2 of 
             when '000' SEE "PACIAZ"; 
             when '001' SEE "PACIASP"; 
             when '010' SEE "PACIBZ"; 
             when '011' SEE "PACIBSP"; 
             when '100' SEE "AUTIAZ"; 
             when '101' SEE "AUTHASP"; 
             when '110' SEE "AUTIBZ"; 
             when '111' SEE "AUTIBSP"; 
     when '0100 xx0' 
         op = SystemHintOp_BTI; 
         // Check branch target compatibility between BTI instruction and PSTATE.BTYPE 
1
1
0
1
0
1
0
1
0
0
0
0
0
0
1
1
0
0
1
0
CRm
op2
1
1
1
1
1
31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11
8
7
5
4
3
2
1
0

A64 Base Instruction Descriptions 
C6.2 Alphabetical list of A64 base instructions
ARM DDI 0487G.b
Copyright © 2013-2021 Arm Limited or its affiliates. All rights reserved.
C6-1033
ID072021
Non-Confidential
         SetBTypeCompatible(BTypeCompatible_BTI(op2<2:1>)); 
     otherwise EndOfInstruction();
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
case op of
```

</details>


<details><summary>Assembler symbols / 操作数含义（1 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<imm>` | Is a 7-bit unsigned immediate, in the range 0 to 127 encoded in the "CRm:op2" field. The encodings that are allocated to |


</details>


*PDF 跨页*：p1032-p1034（共 3 页）


### 4.15 `IC` (C6.2.95)

> ⚠️ **这是 `SYS` 的别名**。底层编码与 `SYS` 相同，只是汇编器接受不同写法。


**语义**：Instruction Cache operation. For more information, see op0==0b01, cache maintenance, TLB maintenance, and address translation instructions on page C5-399.


**汇编模板**：
```
IC <ic_op>{, <Xt>}
```


<details><summary>Operation 伪代码（点击展开）</summary>

```
The description of SYS gives the operational pseudocode for this instruction.
```

</details>


<details><summary>Assembler symbols / 操作数含义（5 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<ic_op>` | Is an IC instruction name, as listed for the IC system instruction pages, encoded in the "op1:CRm:op2" field. It can hav |

| `<op1>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op1" field. |

| `<Cm>` | Is a name 'Cm', with 'm' in the range 0 to 15, encoded in the "CRm" field. |

| `<op2>` | Is a 3-bit unsigned immediate, in the range 0 to 7, encoded in the "op2" field. |

| `<Xt>` | Is the 64-bit name of the optional general-purpose source register, defaulting to '11111', encoded in the "Rt" field. |


</details>


*PDF 跨页*：p1036-p1037（共 2 页）


### 4.16 `ISB` (C6.2.97)

**语义**：Instruction Synchronization Barrier flushes the pipeline in the PE and is a context synchronization event. For more information, see Instruction Synchronization Barrier (ISB) on page B2-147.


**汇编模板**：
```
ISB {<option>|#<imm>}
```


<details><summary>Decode 伪代码（点击展开）</summary>

```
// No additional decoding required
```

</details>


<details><summary>Operation 伪代码（点击展开）</summary>

```
InstructionSynchronizationBarrier();
```

</details>


<details><summary>Assembler symbols / 操作数含义（2 个，点击展开）</summary>


| 操作符 | 含义 |
|--------|------|

| `<option>` | Specifies an optional limitation on the barrier operation. Values are: SY Full system barrier operation, encoded as CRm  |

| `<imm>` | Is an optional 4-bit unsigned immediate, in the range 0 to 15, defaulting to 15 and encoded in the "CRm" field. |


</details>


*PDF 跨页*：p1039-p1040（共 2 页）


---
## 5. 实测代码

详见：../Lab03_存储层次/ + ../Lab06_内存模型与并发/


---
## 6. 性能预期（飞腾 D3000M @ 2.5 GHz）

| 指令 | latency | 备注 |
|------|---------|------|
| DMB SY | ~50-100 cyc | 全屏障 |
| DMB ST | ~10-20 cyc | 只挡 store |
| DSB SY | ~100-500 cyc | 最强屏障 |
| ISB | ~10-50 cyc | flush 流水线 |
| DC CIVAC | ~50-200 cyc | 单 cache line |
| DC ZVA | ~10-50 cyc | 整块 zero |
| IC IVAU | ~100 cyc | 单 cacheline |
| TLBI ALLE1IS | ~500-2000 cyc | 全 TLB


---
## 7. 缺陷与陷阱

1. **DMB vs DSB vs ISB 强度**：DMB<DSB<ISB，但 DMB 大多数场景够用
2. **DC CIVAC 在用户态不可用**：需要 syscall 或驱动
3. **IC IVAU 是 JIT 必备**：写完代码必须 IC IVAU + DSB ISH + ISB 否则 I-cache 看不到
4. **PoC vs PoP**：Point of Coherency vs Point of Persistence，含义不同
5. **TLB 维护昂贵**：跨核 TLBI 触发 IPI


---
## 8. 进一步阅读

- ARM ARM §C5 (system) / §D12 (barriers)
- ARM Cortex-A Programmer's Guide § Memory Ordering
- Linux `arch/arm64/include/asm/barrier.h`/`asm/cacheflush.h`


---
📌 **下一步**：回到 [`isa_reference/README.md`](./README.md) 看其他扩展。
