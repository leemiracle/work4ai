# A64 ISA 指令参考（飞腾 D3000M 实测导向）

> 本目录把 **ARM Architecture Reference Manual Armv8, for A-profile architecture (DDI 0487G.b, 2021-07)**
> 8696 页全本中**飞腾 D3000M (FTC862) 实测可用**的部分，按 HWCAP 扩展分组做**指令级深度剖析**。
>
> 与 ARM ARM 原文的差异：
> - **粒度**：每条指令给出助记符 + 汇编语法 + 编码 + 语义 + intrinsic + **实测代码 + 性能数据 + 陷阱**（实验项目风），而非纯字典
> - **范围**：聚焦飞腾实测支持的扩展；不支持但列入对照（SVE/BF16/I8MM/FHM）
> - **导向**：每条指令都回答"**这条指令在 Lab 哪个实验里被跑过 / 怎么自己跑一遍**"

---

## 0. 数据来源与提取方法

| 维度 | 数据 |
|------|------|
| 源文档 | `CPU性能优化/Arm-Architecture-Reference-Manual-Armv8-for A-profile-architecture-DDI0487G_b_armv8_arm.pdf` |
| 源文档体量 | 8696 页 / 50 MB / Arm Limited 2021-07 |
| 提取范围 | Chapter C5 (System) + C6 (Base, 354 小节) + C7 (Advanced SIMD/FP, 391 小节) |
| 提取方法 | PyMuPDF 扫描 + 正则识别 `C[567].N.N` 小节号 + 助记符行 + `(FEAT_xxx)` 标签 |
| 数据库 | `isa_instructions.json`（共 755 个指令条目，36 个 FEAT 分组） |
| HWCAP 实测 | `Lab01_ISA与汇编/src/isa_features.c`（飞腾 D3000 真机） |

---

## 1. 索引：按 ARMv8.x 版本

### v8.0（基线，飞腾全部支持）

| 文件 | 主题 | 指令数 | HWCAP | 杀手应用 |
|------|------|--------|-------|---------|
| [`v8.0_asimd.md`](./v8.0_asimd.md) + [`_a_to_g`](./v8.0_asimd_a_to_g.md) / [`_h_to_p`](./v8.0_asimd_h_to_p.md) / [`_q_to_z`](./v8.0_asimd_q_to_z.md) | **NEON (Advanced SIMD, ASIMD)** | ~267（按字母分 3 文件） | HWCAP_ASIMD | GEMM / 向量化 / 图像处理 |
| [`v8.0_crypto.md`](./v8.0_crypto.md) | **AES + SHA1 + SHA256 + PMULL** | 15 | HWCAP_AES/SHA1/SHA2/PMULL | TLS / 磁盘加密 / 区块链 |
| [`v8.0_crc32.md`](./v8.0_crc32.md) | **CRC32 (硬件加速)** | 8 变体 | HWCAP_CRC32 | 网络包校验 / Zlib / BTRFS |

### v8.1（飞腾全部支持）

| 文件 | 主题 | 指令数 | HWCAP | 杀手应用 |
|------|------|--------|-------|---------|
| [`v8.1_lse.md`](./v8.1_lse.md) | **LSE 大内存原子指令** | **55** | HWCAP_ATOMICS | 无锁队列 / 引用计数 / 计数器 |
| [`v8.1_rdm.md`](./v8.1_rdm.md) | **RDM 饱和乘加（SQRDMLAH）** | 4 | HWCAP_ASIMDRDM | 音频处理 / GEMM Low-bit 量化 |
| [`v8.1_lor.md`](./v8.1_lor.md) | **LOR 低开销 Load/Store（LDLAR/STLLR）** | 6 | HWCAP_LOR | LL/SC 替代变体 |
| [`v8.1_lrcpc.md`](./v8.1_lrcpc.md) | **LRCPC v1（LDAPR load-acquire）** | 3 | HWCAP_LRCPC | RCpc 内存序（C++ atomic） |

### v8.2（飞腾全部支持）

| 文件 | 主题 | 指令数 | HWCAP | 杀手应用 |
|------|------|--------|-------|---------|
| [`v8.2_fp16.md`](./v8.2_fp16.md) | **FP16 标量 + NEON（FHP+ASIMDHP）** | **68** | HWCAP_FPHP + HWCAP_ASIMDHP | fp16 推理（比 fp32 快 2× SIMD 宽度） |
| [`v8.2_ras_cvap.md`](./v8.2_ras_cvap.md) | RAS (ESB) + DC CVAP 持久化内存屏障 | 1+ | (系统寄存器) | 服务器 RAS / NVM |

### v8.3（部分支持 — 需 HWCAP 复核）

| 文件 | 主题 | 指令数 | HWCAP | 飞腾状态 |
|------|------|--------|-------|---------|
| [`v8.3_fcma.md`](./v8.3_fcma.md) | **FCMA 复数乘累加（FCMLA/FCADD）** | 3 | HWCAP_FCMA | ⚠️ HWCAP 未报，需字节码验证（已在 Lab01.7 做） |
| [`v8.3_misc.md`](./v8.3_misc.md) | **JSConv (FJCVTZS) + PAuth (PAC/AUT) + LRCPC v2 (LDAPUR/STLUR)** | 25 | HWCAP_JSCVT/PACA/ILRCPC | ⚠️ 部分待测 |

### v8.4（飞腾核心支持 — 国密 + 现代密码 + int8）

| 文件 | 主题 | 指令数 | HWCAP | 杀手应用 |
|------|------|--------|-------|---------|
| [`v8.4_dotprod.md`](./v8.4_dotprod.md) | **DotProd（UDOT/SDOT int8 点积）** | 4 | HWCAP_ASIMDDP | int8 量化 CNN / GEMM |
| [`v8.4_sha3_sha512.md`](./v8.4_sha3_sha512.md) | **SHA3 (Keccak) + SHA512** | 8 | HWCAP_SHA3 + HWCAP_SHA512 | Web3 / Ed25519 / 现代签名 |
| [`v8.4_sm3_sm4.md`](./v8.4_sm3_sm4.md) | **国密 SM3 (哈希) + SM4 (分组密码)** | 9 | HWCAP_SM3 + HWCAP_SM4 | 国密合规必备 |

### v8.5+（部分支持 / 不支持）

| 文件 | 主题 | 状态 |
|------|------|------|
| [`v8.5_misc.md`](./v8.5_misc.md) | **v8.5+ Misc (BTI / FRINTTS / FlagM / MTE / WFxT / SPECRES 等)** | 40+ | (多个 HWCAP) | ⚠️ 飞腾基本不支持 |
| [`v8.x_unsupported.md`](./v8.x_unsupported.md) | **SVE / SVE2 / BF16 / I8MM / FHM** —— 不支持说明 + 替代方案 | - | - | ❌ |
| **[`intrinsic_mapping.md`](./intrinsic_mapping.md)** | **指令 → C/C++ intrinsic 速查表**（按扩展 + 常见代码模式） | - | - | 必读工具 |
| **[`deep_dive_core.md`](./deep_dive_core.md)** | **核心指令算法层深度专题**（AESE/SHA256H/UDOT/SM3SS1/SM4E/FCMLA） | - | - | 进阶必读 |

---

## 2. 索引：按 Lab 实验顺序

| Lab | 用到的指令 | 本目录文件 |
|-----|----------|----------|
| Lab01.1 C→汇编 | ADD/LDR/STR/B/BL/MOV/BFM | [`a64_base_overview.md`](./a64_base_overview.md) → 拆分文件 |
| Lab01.2 调用约定 | STP/LDP/RET/BLR | [`a64_base_overview.md`](./a64_base_overview.md) → 拆分文件 |
| Lab01.3 NEON 入门 | FMLA/LD1/ST1/FADD | [`v8.0_asimd.md`](./v8.0_asimd.md) → 拆分文件 |
| Lab01.5 FP16 性能 | FMLA fp16/FADD fp16 | [`v8.2_fp16.md`](./v8.2_fp16.md) |
| Lab01.6 Dot Product | UDOT/SDOT | [`v8.4_dotprod.md`](./v8.4_dotprod.md) |
| Lab01.7 FCMLA 复数 | FCMLA/FCADD | [`v8.3_fcma.md`](./v8.3_fcma.md) |
| Lab01.9 AES/SHA | AESE/SHA256H | [`v8.0_crypto.md`](./v8.0_crypto.md) |
| Lab01.10 SM3/SM4 | SM3SS1/SM4E | [`v8.4_sm3_sm4.md`](./v8.4_sm3_sm4.md) |
| Lab02.5 LSE vs LL/SC | LDADD/CAS/SWP | [`v8.1_lse.md`](./v8.1_lse.md) |
| Lab02.6 字节原子 | LDADDB/CASB | [`v8.1_lse.md`](./v8.1_lse.md) |
| Lab03 cache | DC CIVAC/IC IALLU | [`a64_system_instructions.md`](./a64_system_instructions.md) |
| Lab05 GEMM | FMLA/LD1/ST1/UDOT | [`v8.0_asimd.md`](./v8.0_asimd.md) + [`v8.4_dotprod.md`](./v8.4_dotprod.md) |
| Lab06 内存模型 | LDAR/STLR/LDADD/LDAPR/DMB/DSB | [`v8.1_lrcpc.md`](./v8.1_lrcpc.md) + [`a64_system_instructions.md`](./a64_system_instructions.md) |
| Lab07 密码学 | AESE/SHA256H/SM3SS1/SM4E/CRC32W | [`v8.0_crypto.md`](./v8.0_crypto.md) + [`v8.4_sm3_sm4.md`](./v8.4_sm3_sm4.md) + [`v8.0_crc32.md`](./v8.0_crc32.md) |

**辅助文件**：
- [`a64_base_overview.md`](./a64_base_overview.md) + [`_a_to_g`](./a64_base_a_to_g.md) / [`_h_to_p`](./a64_base_h_to_p.md) / [`_q_to_z`](./a64_base_q_to_z.md) — **A64 350 条基础指令**（按首字母拆 3 文件）
- [`v8.0_asimd.md`](./v8.0_asimd.md) + [`_a_to_g`](./v8.0_asimd_a_to_g.md) / [`_h_to_p`](./v8.0_asimd_h_to_p.md) / [`_q_to_z`](./v8.0_asimd_q_to_z.md) — **NEON 267 条指令**（按首字母拆 3 文件）
- [`a64_system_instructions.md`](./a64_system_instructions.md) — **DMB/DSB/DC/IC/AT/TLBI + option 详表**

---

## 3. 每个详细 md 的统一结构

```
# <扩展名> (FEAT_xxx) 指令详解

## 目录（含指令跳转锚点）
## 0. 一句话
## 1. 现象：为什么需要它？
## 2. 引入版本 & 飞腾状态
## 3. 指令清单总表
   | 助记符 | 变体 | 章节号 | ARM 页 | PDF 页 | 别名 / 被别名 |
## 4. 每条指令详解
   ### 4.x MNEMONIC
   - 别名提示（alias_of / used_by_aliases）
   - 语义
   - 汇编模板（含所有变体）
   - 版本/限制
   - 检测字段（ID_AA64ISAR0_EL1.X）
   - Decode 伪代码（可折叠）
   - Operation 伪代码（可折叠）
   - Assembler symbols / 操作数含义（可折叠表格）
   - PDF 跨页信息
## 5. 实测代码（链接到 LabXX/src/）
## 6. 性能预期
## 7. 缺陷与陷阱（在飞腾 D3000 上的具体表现）
## 8. 进一步阅读
   - ARM ARM 章节 + 页码
   - 相关论文 / blog
   - Linux kernel 用法
```

> 找 intrinsic 函数 → 直接看 [`intrinsic_mapping.md`](./intrinsic_mapping.md)（按扩展 + 常见代码模式）。

---

## 4. 工具与编译选项速查

### 编译开启各扩展

```makefile
# 一次性开启所有飞腾支持的扩展（v8.4-a 全集）
CFLAGS += -march=armv8.4-a+crypto+crc+simd+lse+rcpc+flagm+jscvt+fcma+dotprod+sm4+sm3+sha3+sha512+rng+preserveregs
# 或针对飞腾直接用 -mcpu
CFLAGS += -mcpu=ftc86x    # D3000M (FTC862)
CFLAGS += -mcpu=ftc66x    # D3000  (FTC663)
```

### 运行时检测

```c
#include <sys/auxv.h>
unsigned long hw  = getauxval(AT_HWCAP);
unsigned long hw2 = getauxval(AT_HWCAP2);

if (hw & HWCAP_ASIMDHP)   { /* FP16 NEON 可用 */ }
if (hw & HWCAP_ASIMDDP)   { /* UDOT/SDOT 可用 */ }
if (hw & HWCAP_SM3)       { /* 国密 SM3 可用 */ }
if (hw & HWCAP_ATOMICS)   { /* LSE 可用 */ }
// ...详见 Lab01/src/isa_features.c
```

---

## 5. 与原 PDF 的对应关系

| 本目录文件 | ARM ARM 章节 | 物理页范围 |
|----------|------------|----------|
| `a64_base_overview.md` | C3 + C6.2 总览 | C3-216 ~ C3-282 / C6-872 ~ C6-905 |
| `a64_system_instructions.md` | C5 + C6.2 系统部分 | C5-394 ~ C5-869 / 散见 C6 |
| `v8.0_asimd.md` | C7.2（无 FEAT 标记的 ASIMD 部分） | C7-1522 ~ C7-2344 中段 |
| `v8.0_crypto.md` | C7.2.7-10 (AES) / .215 (PMULL) / .239-248 (SHA1/256) | C7-1537 ~ C7-2079 |
| `v8.0_crc32.md` | C6.2.66-67 | C6-990 ~ C6-993 |
| `v8.1_lse.md` | C6.2.40-59 (CAS) / .99-101 (LDADD) / .118-149 (其余原子) / .251-253 (STADD) / .322-324 (SWP) | C6-944 ~ C6-1475 |
| `v8.1_rdm.md` | C7.2.293-296 | C7-2181 ~ C7-2189 |
| `v8.1_lor.md` | C6.2.126-128,131-133 | C6-1099 ~ C6-1117 |
| `v8.1_lrcpc.md` | C6.2.102-104 | C6-1048 ~ C6-1052 |
| `v8.2_fp16.md` | C7.2 中所有 FEAT_FP16 标记的条目 | 散布于 C7-1537 ~ C7-2449 |
| `v8.2_dc_cvap.md` | C5（DC 指令变体） | C5-506 ~ C5-567 |
| `v8.3_fcma.md` | C7.2.62-63, 357 | C7-1662 ~ C7-1666 |
| `v8.3_pauth.md` | C6.2 多处 | C6 多处 |
| `v8.3_lrcpc2.md` | C6.2.105-113 | C6-1054 ~ C6-1075 |
| `v8.4_dotprod.md` | C7.2.237-238 (SDOT) / .356-357 (UDOT) | C7-2066 ~ C7-2347 |
| `v8.4_sha3_sha512.md` | C7.2.249-252 (SHA512) / .322-325 (SHA3) | C7-2081 ~ C7-2179 |
| `v8.4_sm3_sm4.md` | C7.2.261-267 (SM3) / .268-269 (SM4) | C7-2106 ~ C7-2125 |

---

## 6. 总览统计（从 PDF 提取的真实数字）

| 维度 | 数字 |
|------|------|
| A64 base instructions (C6.2) | **354** 小节 |
| A64 Advanced SIMD/FP (C7.2) | **391** 小节 |
| 合计 A64 指令条目 | **745** 小节 |
| FEAT 标签种类 | **36** 个 |
| 飞腾 D3000 实测可用扩展 | **19** 项（v8.0-v8.4 主体） |
| 飞腾 D3000 不支持扩展 | 4 项（SVE/BF16/I8MM/FHM） |

---

📌 **下一步**：
- 想看**基础指令全景**（ADD/SUB/LDR/B 是怎么编码的）→ [`a64_base_overview.md`](./a64_base_overview.md)
- 想看**飞腾杀手锏**（fp16/UDOT/SM3/SM4）→ [`v8.2_fp16.md`](./v8.2_fp16.md) / [`v8.4_dotprod.md`](./v8.4_dotprod.md) / [`v8.4_sm3_sm4.md`](./v8.4_sm3_sm4.md)
- 想看**实测代码** → [`../Lab01_ISA与汇编/src/`](../../体系结构实验/Lab01_ISA与汇编/src/)
