# 🎯 ARM 与 RISC-V 优化圣经：x86 之外的两大世界

> **本文档定位**：[AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) 的**对称续作**。
>
> Agner Fog 是 x86 阵营的圣经，但今天的服务器（AWS Graviton / Ampere / NVIDIA Grace）、桌面（Apple Silicon M1-M4 / 高通骁龙 X Elite）、移动（所有手机）、嵌入式（万物 IoT）和未来 HPC（RISC-V Vector / 十大超算之一）都在 ARM/RISC-V 上。
>
> **关键差异**：ARM/RISC-V 的微架构、内存模型、SIMD（NEON/SVE/SVE2 vs RVV）与 x86 **完全不同**，盲目把 x86 优化经验搬过去会失效甚至变慢。本文给出 ARM/RISC-V 的权威资源地图 + 与 x86 的精确对比 + 跨平台代码原则。
>
> **配套代码**：[`../cmu-cs-projects/topic2-systems/arm_riscv_optimization_demo.py`](../cmu-cs-projects/topic2-systems/arm_riscv_optimization_demo.py)（6 个可运行对比 demo）。

---

## 🗺️ 第 0 部分：资源地图（2026-08 验证可用）

### ARM 阵营（资源分散，需要梳理）

| 资源 | 类型 | 价值 |
|------|------|------|
| ⭐ **[ARM Learn the Architecture](https://developer.arm.com/architectures/learn-the-architecture/a-profile)** | 官方 | A-profile（Cortex-A）系统教程：SVE/SVE2、内存模型、PMU |
| ⭐ **[ARM Cortex-A SOG](https://developer.arm.com/documentation)**（Software Optimization Guide）| 官方 | 每个核心（A78/A715/X4）一份的指令延迟+优化建议 |
| ⭐ **[ARM Neoverse SOG](https://developer.arm.com/architectures/cpu-features/neoverse)** | 官方 | N1/N2/V1/V2 服务器核心优化指南 |
| **ARM Cortex-A TRM**（Technical Reference Manual）| 官方 | 每个核心的微架构细节（pipeline/ROB/端口）|
| **[ARM ARM](https://developer.arm.com/architecture/archive/architecture-reference-manual)**（Architecture Reference Manual）| 官方 | ARMv8-A / ARMv9-A 指令集 + 异常模型 + 内存模型（最权威）|
| ⭐⭐ **[OSACA](https://github.com/RRZE-HPC/OSACA)** | 开源工具 | **ARM 生态的 Agner**：跨 x86+AArch64 的指令级性能分析器，集成进 Godbolt，支持 Cortex-A72/N1/V2/ThunderX2/A64FX/TaiShan/**Apple M1 Firestorm**/NVIDIA Grace |
| **[Dougall's Apple Silicon tables](https://dougallj.appspot.com/apple/firestorm.html)** | 个人逆向 | Apple 不公开微架构，Dougall Johnson 通过微基准**逆向出 M1 Firestorm 的指令延迟表** |
| **[Instlatx64](http://instlatx64.atw.hu/)** | 社区 | 实测指令延迟，含 Apple Silicon / Cortex / Neoverse |
| **[Cloudflare Graviton blog](https://blog.cloudflare.com/tag/aws-graviton/)** | 实战 | 在 Graviton 上做 TLS/HTTP/防火墙优化的真实案例 |
| **[AWS Graviton Performance Runbook](https://github.com/aws/aws-graviton-getting-started)** | 实战 | AWS 官方的 Graviton 应用迁移+优化 cookbook |
| **[Linaro](https://www.linaro.org/)** | 生态 | ARM Linux 工具链核心组织（Linaro Toolchain / OP-TEE / 96Boards）|

### RISC-V 阵营（更年轻、更开放、更分散）

| 资源 | 类型 | 价值 |
|------|------|------|
| ⭐ **[RISC-V International spec](https://wiki.riscv.org/display/HOME/RISC-V+International)** | 官方 | ISA + 各扩展（I/M/A/F/D/V/K/B/C/P）spec |
| ⭐ **[RISC-V Vector spec v1.0](https://github.com/riscvarchive/riscv-v-spec)** | 官方（已 frozen）| V 扩展完整 spec，含 `vfrec7.adoc`/`vfrsqrt7.adoc` 硬件倒数 + `recip.c` Newton-Raphson 参考 |
| ⭐ **[RVV Intrinsic](https://github.com/riscv-non-isa/rvv-intrinsic-doc)** | 官方 | C 层 vector intrinsic（**Clang 19 + GCC 14 支持 v1.0**）|
| **[SiFive Performance Guide](https://www.sifive.com/docs)** | 厂商 | SiFive U7/U8/X系列优化指南（最成熟商用 RISC-V）|
| **[Andes (晶心) Docs](https://www.andestech.com/)** | 厂商 | Andes N/X 系列优化（RISC-V + DSP 扩展）|
| **[T-Head (平头哥)玄铁](https://www.t-head.cn/)** | 厂商 | C910/C920（开源 RTL）|
| **[BOOM (Berkeley Out-of-Order Machine)](https://github.com/riscv-boom/riscv-boom)** | 学术 | Berkeley 开源的 RISC-V OoO 核心，研究用 |
| ⭐ **[Spike / riscv-isa-sim](https://github.com/riscv-software-src/riscv-isa-sim)** | 官方 ISA 仿真器 | 支持 RVV 1.0，调试 RISC-V 代码的金标准 |
| **[QEMU RISC-V](https://www.qemu.org/docs/master/system/riscv.html)** | 仿真 | 系统级 RISC-V 仿真，跨开发必备 |
| **[OSACA RISC-V 路线](https://github.com/RRZE-HPC/OSACA)** | 开源工具 | OSACA 团队已规划 RISC-V 支持（路线图中）|
| **[Krste Asanović 演讲](https://www.youtube.com/results?search_query=krste+asanovic+risc-v)** | 学术 | RISC-V 共同发明人，讲 VLA 设计哲学 |

---

## 📊 第 1 部分：三 ISA 微架构对比矩阵（核心数据）

> 数据来源：OSACA 数据库 + Agner Vol 3（2026-05）+ ARM SOG + SiFive 官方 + Dougall Apple 逆向。

### 1.1 现代核心微架构参数对比

| 参数 | Intel Golden Cove (P-core) | AMD Zen 4 | ARM Cortex-X4 | ARM Neoverse V2 (Grace) | Apple M4 Everest | SiFive P670 |
|------|----------|----------|----------|----------|----------|----------|
| **解码宽度** | 6 | 4 | 5 | 5 | ⭐ **9-10**（行业最宽）| 4-6 |
| **ROB（重排缓冲）** | 512 | 320 | 288 | 320 | ⭐ **600+**（行业最大）| ~200 |
| **执行端口** | 12 | 10 | 15 | 11 | ⭐ **14+** | 8-10 |
| **L1 D-cache** | 48 KB / 14 cycle | 32 KB / 14 cycle | 64 KB / 4 cycle | 64 KB / 4 cycle | 128 KB / 3 cycle | 64 KB / 4 cycle |
| **L2 cache** | 1.25-2 MB | 1 MB | 1 MB | 1 MB | ⭐ **4-16 MB**（共享）| 256 KB - 2 MB |
| **分支预测器** | TAGE + IT-TAGE | Perceptron | Perceptron | Perceptron | 神经网络（细节保密）| Perceptron |
| **误预测代价** | 18-22 cyc | 19 cyc | 16 cyc | 16 cyc | ~15 cyc | ~15 cyc |
| **SIMD 谱系** | AVX-512 | AVX-512 | SVE2 (128/256b) | SVE2 (128b) | NEON+ 独有 | RVV（VLA）|

### 1.2 关键反直觉（来自实测）

1. **Apple M1-M4 的解码宽度是 x86 的 2 倍以上**（9-10 vs 4-6）。原因：ARM 指令**等长 4 字节**，解码器不用对齐边界；x86 指令 1-15 字节变长，解码器要预解码边界，无法做宽。这就是为什么 M1 单核 IPC 经常碾压同代 x86。
2. **A64FX（Fujitsu 富士通）的 HBM2 内存**带宽 1 TB/s，是普通 DDR 的 8×。这是 Fugaku 超算（曾经的 #1）能跑出 442 PFLOPS 的物理基础。
3. **RISC-V 的 VLA（Vector Length Agnostic）**让一份 RVV 代码自动适配 VLEN=128/256/512/1024 bit 的不同硬件——这是 ARM SVE/SVE2 也借鉴的革命性设计。
4. **ARM 的分支预测器 100% 是 Perceptron**（神经网络），比 Intel 的 TAGE 在重复模式上更准。
5. **Cortex-A 的 L1 都是 64 KB**（比 x86 的 32-48 KB 大），但延迟都是 4 cycle——ARM 的设计哲学是"大 L1 容纳更多热数据"。

---

## 🍎 第 2 部分：ARM 优化的 6 个独特点

### 独特点 1：弱内存模型（CSAPP 真相 7 的深化）

**x86 是 TSO（Total Store Order）**——Store 不能重排，Load 可以。**ARM 是 RMO（Relaxed Memory Order）**——几乎所有读写都可重排。

```c
// 同一段代码在 x86 安全，在 ARM 可能崩
data[x] = value;
ready[x] = 1;          // x86：data 写一定先于 ready 写对外可见
                       // ARM：可能 ready 先可见，读者看到 ready=1 但 data 还旧
```

**ARM 必用的屏障指令**：
- `dmb ish`（Data Memory Barrier）—— 强制所有前后内存操作顺序
- `dmb ishst`（仅 Store）—— 等价 x86 的 `sfence`
- `dmb ishld`（仅 Load）—— 等价 x86 的 `lfence`
- `prfm`（Prefetch Memory）—— 软件预取，ARM 比 x86 更重要（L1 大、L2 远）

**C/C++ 抽象层**：`std::atomic<T>` 的 `memory_order_release/acquire` 自动生成对的屏障——**优先用原子，别手写汇编屏障**。

🧪 见 demo §4 `demo_weak_memory_model` —— x86 TSO vs ARM RMO 的合法重排数量对比。

### 独特点 2：NEON → SVE → SVE2 的进化

| 指令集 | 寄存器 | 引入 | 关键差异 |
|--------|--------|------|---------|
| **NEON / AdvSIMD** | 32 × 128b（V0-V31）| ARMv7-A (2010) | **固定 128b**，类似 x86 SSE，无谓词 |
| **SVE**（Scalable Vector Extension）| 32 × **可变长**（128-2048b）| ARMv8.6 (2016) | **VLA！** 一份代码自动适配不同 VLEN；**谓词寄存器**（P0-P15）做条件 SIMD |
| **SVE2** | 同 SVE | ARMv9-A (2020) | SVE 的实用化版本，加 NEON 大部分功能 → 逐步取代 NEON |

**SVE/SVE2 的两大革命**（x86 没有的）：
1. **VLA（Vector Length Agnostic）**：写一份代码，VLEN=128 时一次算 4 个 float，VLEN=512 时算 16 个，VLEN=2048（A64FX）时算 64 个。**指令是 `whilelt` + 循环，不是写死的 SIMD 宽度**。
2. **谓词（Predicate）**：用 P 寄存器掩码，做到"只对符合条件的元素做 SIMD 操作"——比如 `if (x[i] > 0) y[i] = sqrt(x[i])` 一条 SVE 指令搞定，无需分支或 cmov。

### 独特点 3：Apple Silicon 的"反常识"设计

Apple M1-M4 自研核心（Firestorm/Icestorm/Everest/Avalanche/Donan）：
- **解码宽度 9-10**：行业最宽（x86 4-6，Cortex 5）。
- **ROB 600+**：行业最大（x86 512，Cortex 320）。
- **L1 D-cache 128 KB / 3 cycle**：行业最离谱的大+快。
- **统一内存架构（UMA）**：CPU/GPU/Neural Engine 共享同一块 LPDDR，带宽 100-400 GB/s，延迟低于独立显卡。
- **AMX 协处理器**：Apple 独有的矩阵扩展（Apple Silicon 的"Tensor Core"），不公开文档但 [dougallj 已逆向](https://dougallj.appspot.com/apple/firestorm.html)，PyTorch/TensorFlow 已支持。
- **不用 SVE/SVE2**：Apple 只用 NEON + AMX，与 ARM 主流路线分叉。

### 独特点 4：A64FX 的 HBM2 + SVE-512

Fujitsu A64FX（用于 Fugaku 超算）：
- **48 核 + 4 HBM2 内存**：带宽 1024 GB/s（普通 DDR4 是 ~100 GB/s）。
- **SVE-512**：512 bit 向量，每周期 16 个 double FMA。
- **不用 L3 cache，直接 HBM**：因为 HBM 带宽够大，cache 反而是冗余。
- **指令延迟极低**：FMA 8 cycle（vs Skylake 的 4 cycle）但吞吐 2/cycle，依赖链短。

### 独特点 5：AWS Graviton（云上 ARM 的代表）

Graviton 2（Neoverse N1）/ Graviton 3（Neoverse V1）/ **Graviton 4（Neoverse V2）**：
- **价格是同代 x86 实例的 60-70%**，性能 90-110%——**性价比之王**。
- **能效比 x86 高 40-60%**（每瓦算力）——AWS 数据中心省电的关键。
- **Neoverse V2 用 Perceptron 分支预测器 + SVE2**。
- **优化 cookbook**（AWS 官方）：
  - 用 `-march=armv8.2-a+crypto+fp16+rcpc+dotprod` 编译
  - 避免 `gcc` 的 `-march=native`（不同 Graviton 代不同）
  - 内存对齐从 16B 提到 64B（cache line 对齐）

### 独特点 6：与 x86 的"统一 cache line"差异

x86 的 cache line 是 64B，但**支持非对齐访问**（硬件自动跨 line，性能损失但不报错）。ARM 历史上有"对齐陷阱"（unaligned access 触发 fault），ARMv8 后默认支持但**性能损失更大**——所以 ARM 代码的对齐要求更严格。

---

## 🔧 第 3 部分：RISC-V 优化的 7 个独特点

RISC-V 是开放 ISA，**没有"官方微架构"**——同样的 RV64GC 在 SiFive/平头哥/Andes/Tenstorrent 上微架构差异巨大。但 ISA 设计哲学有几个革命性创新。

### 独特点 1：VLA（Vector Length Agnostic）—— RISC-V V 的核心革命

**问题**：x86 SSE 固定 128b，AVX 固定 256b，AVX-512 固定 512b。代码用 AVX 写的，到只支持 SSE 的 CPU 上跑不了。

**RISC-V V 扩展的解药**（与 ARM SVE 同源思想，但更激进）：
- VLEN（Vector Length）由实现决定：32 / 64 / 128 / 256 / 512 / 1024 / 2048 bit 都合法。
- **代码不写死宽度**，而是查询 `vsetvli` 指令动态设置：

```asm
# RVV 求和：一份代码适配 VLEN=128/256/512/1024
loop:
    vsetvli  t0, a1, e32, m1   # 设置向量：元素 32bit，一组 t0 个
    vle32.v  v0, (a0)          # 加载 t0 个 float
    vadd.vv  v1, v1, v0        # 累加到 v1
    slli     t0, t0, 2         # t0 *= 4（字节数）
    add      a0, a0, t0
    sub      a1, a1, t0
    bnez     a1, loop
```

**好处**：SiFive P670（VLEN=128）和未来 SiFive X300（VLEN=512）跑同一份二进制，性能自动适配。**x86/NEON 永远做不到**。

🧪 见 demo §3 `demo_vla_concept` —— 同一份 RVV 风格代码在 VLEN=128/256/512/1024 下的吞吐对比。

### 独特点 2：硬件倒数指令 `vfrec7` / `vfrsqrt7`

RISC-V V 内置硬件倒数指令（7-bit 精度初值），比 x86 `rcpss`（11-bit）粗但比软件快：

| 指令 | 输出精度 | 用途 |
|------|---------|------|
| `vfrec7.v` | 7 bit | `1/x` 近似 |
| `vfrsqrt7.v` | 7 bit | `1/√x` 近似 |
| 加 1 次 Newton-Raphson | ~14 bit | 接近 float16 满 |
| 加 2 次 Newton-Raphson | ~28 bit | 接近 float32 满 |

参考代码在 [riscv-v-spec/recip.c](https://github.com/riscvarchive/riscv-v-spec/blob/master/recip.c)。

### 独特点 3：扩展体系（模块化是 RISC-V 的灵魂）

| 扩展 | 名字 | 用途 |
|------|------|------|
| **I** | Integer | 基础整数（必选）|
| **M** | Multiply | 乘除法 |
| **A** | Atomic | 原子指令（多核）|
| **F/D** | Float / Double | 单/双精度浮点 |
| **V** | Vector | VLA 向量（重点）|
| **C** | Compressed | 16-bit 压缩指令（代码体积 -25%）|
| **B** | Bit Manipulation | 位操作（cttz/clz/popcount 等）|
| **K** | Cryptography | AES/SHA/SM 等密码学 |
| **P** | Packed SIMD | DSP 风格定点 SIMD |
| **Zba/Zbb/Zbc/Zbs** | B 子扩展 | 具体位运算 |
| **Zicbom/Zicboz** | Cache mgmt | cache 行 invalidate/zero |

**`-march=` 编译标志**示例：`rv64gcv_zba_zbb` = 通用 + V 扩展 + 位操作子集。

### 独特点 4：厂商实现差异巨大（同一份 ISA，完全不同的核）

| 厂商 | 核心 | 微架构 | 备注 |
|------|------|--------|------|
| **SiFive** | P450/P670/X390 | OoO，性能级 | 商用龙头 |
| **T-Head/平头哥** | 玄铁 C910/C920 | OoO，**开源 RTL** | 国产代表 |
| **Andes 晶心** | N25F/N45,X278 | OoO + AndeStar 自定义扩展 | 台湾，DSP 强 |
| **Tenstorrent** | Ascalon | 高性能 OoO | Jim Keller 主导 |
| **小米/SpacemiT** | X100 | 高性能 | 国产新势力 |
| **Meta** | RISC-V for video | 定制 | 视频转码 |
| **EsperantoTech** | ET-Minimax/Maxmax | 大量小核 + RVV | AI 推理服务器 |
| **BOOM**（Berkeley）| 开源 | 学术 | 研究用 |

**优化启示**：**没有"通用 RISC-V 优化"**，必须查具体厂商的 SOG（SiFive 有，平头哥有部分，其他厂商看社区）。

### 独特点 5：与 x86/ARM 的内存模型对比

| ISA | 模型 | 强度 |
|-----|------|------|
| x86 | TSO（强）| Store 不重排，Load 可重排 |
| ARM | RMO（弱）| 几乎全部可重排 |
| RISC-V | **RVWMO**（RISC-V Weak Memory Order）| 弱，但**形式化定义**最严谨（学术标杆）|

RISC-V 的 RVWMO 是**学术上第一个形式化证明的内存模型**（文中带 22 条公理），可机器验证。这是相比 x86/ARM 的一大进步。

### 独特点 6：Compressed（C 扩展）的代码体积优势

RISC-V 16-bit 压缩指令占常用指令的 50%+，平均**代码体积比 ARM A64 小 25-30%**，比 x86-64 小 10-15%。对嵌入式（I-cache 紧张）和移动（带宽敏感）是关键优势。

### 独特点 7：开源工具链的成熟度

| 工具 | 状态 |
|------|------|
| **GCC** | v14 支持 RVV intrinsic v1.0 ✅ |
| **LLVM/Clang** | v19 支持 RVV intrinsic v1.0 ✅ |
| **Spike** | 官方 ISA 仿真器，支持 RVV v1.0 ✅ |
| **QEMU** | 系统级仿真，跨开发必备 ✅ |
| **OSACA** | RISC-V 支持路线图（已支持 x86+AArch64）🚧 |
| **likwid** | RISC-V PMU 部分支持 🚧 |

---

## 🔄 第 4 部分：三 ISA 横向对比表

### 4.1 SIMD 谱系映射

| 概念 | x86 | ARM | RISC-V |
|------|-----|-----|--------|
| 128b 向量 | SSE/SSE2 | NEON / AdvSIMD | RVV（VLEN=128 时）|
| 256b 向量 | AVX/AVX2 | （NEON 不支持）| RVV（VLEN=256 时）|
| 512b 向量 | AVX-512 | SVE / SVE2（部分）| RVV（VLEN=512 时）|
| 谓词/掩码 | AVX-512 opmask（k0-k7）| SVE P0-P15 | RVV v0（单谓词）|
| FMA | FMA3（vfmadd213）| NEON vfmla / SVE fmla | V vfwmacc |
| 硬件倒数 | rcpss（11b）| frsqrte（定点版）| vfrec7（7b）/ vfrsqrt7 |
| 可变长（VLA）| ❌ | ⭐ SVE/SVE2 | ⭐ RVV（本质特性）|

### 4.2 关键指令延迟对比（来自 OSACA / Agner Vol 4 / ARM SOG）

| 操作 | x86 Skylake | ARM Cortex-X4 | RISC-V SiFive P670 | 备注 |
|------|------------|--------------|------------------|------|
| 整数 add | 1 cyc | 1 cyc | 1 cyc | 全部一样快 |
| 整数 mul (imul) | 3 cyc | 3 cyc | 3-4 cyc | ARM/X 系列略快 |
| 整数 div (idiv) | 20-30 cyc | 10-20 cyc | 12-40 cyc | 全部慢，避开 |
| 浮点 add (FADD) | 4 cyc | 3-5 cyc | 4-6 cyc | ARM X 系最快 |
| 浮点 mul (FMUL) | 4 cyc | 3-5 cyc | 4-6 cyc | 同上 |
| 浮点 div (FDIV) | 12-14 cyc | 7-15 cyc | 15-30 cyc | RISC-V 多无硬件 div |
| 浮点 FMA | 4 cyc | 3-5 cyc | 4-6 cyc | 训练神经网络的主力 |
| sqrt | 18-30 cyc | 12-30 cyc | 软件实现 | 极慢，用 vfrsqrt7 |

### 4.3 内存屏障成本对比

| 屏障 | x86 mfence | ARM dmb ish | RISC-V fence r,rw |
|------|-----------|-------------|------------------|
| 单次成本 | ~10 cyc | ~50-100 cyc | ~30-80 cyc |
| 启示 | x86 屏障便宜，多核编程相对宽松 | ARM 屏障贵，**减少屏障数比减少屏障强度重要** | 同 ARM |

---

## 🌍 第 5 部分：跨平台优化原则（写一份代码，三 ISA 都快）

### 原则 1：写"VLA 友好"的 SIMD 代码

```cpp
// ❌ x86 思维：写死宽度
#include <immintrin.h>
__m256 sum = _mm256_setzero_ps();  // 写死 256b
for (...) sum = _mm256_add_ps(sum, _mm256_load_ps(&x[i]));

// ✅ 跨平台：用 Eigen / sleef / Highway 库（自动适配 SSE/AVX/NEON/SVE/RVV）
#include <hwy/highway.h>
namespace hn = hwy::HWY_NAMESPACE;
hn::Vec<D> sum = hn::Zero(D);
for (...) sum = hn::Add(sum, hn::Load(D, &x[i]));
```

**推荐跨平台 SIMD 库**：
- ⭐ **[Highway](https://github.com/google/highway)**（Google）：抽象 SSE/AVX/NEON/SVE/RVV/WASM，**最佳选择**
- **Eigen**：线性代数专用，自动 dispatch
- **SLEEF**：数学函数库（sin/cos/exp），三 ISA 优化
- **xsimd**：C++ 模板化 SIMD

### 原则 2：内存屏障统一用 `std::atomic`

```cpp
// 跨平台：std::atomic 自动生成对的屏障指令
std::atomic<int> ready{0};
data = compute();
ready.store(1, std::memory_order_release);  // x86: 无指令；ARM: stlr；RISC-V: fence rw,w

while (ready.load(std::memory_order_acquire) == 0) ;  // x86: 无指令；ARM: ldar；RISC-V: fence r,rw
use(data);
```

**永远不要手写汇编屏障**，除非你做内核或无锁库。

### 原则 3：CPU 特性检测的跨平台 API

| 平台 | API |
|------|-----|
| Linux x86 | `__get_cpuid(count, &a, &b, &c, &d)` |
| Linux ARM | `getauxval(AT_HWCAP)` / `getauxval(AT_HWCAP2)` |
| Linux RISC-V | `getauxval(AT_HWCAP)` 检查 `HWCAP_ISA_V` 等 |
| macOS ARM | `sysctlbyname("hw.optional.neon", ...)` |
| Windows | `IsProcessorFeaturePresent(PF_ARM_V8_*...)` |
| 跨平台抽象 | ⭐ **[simdjson/cpu_detection.h](https://github.com/simdjson/simdjson/blob/master/include/simdjson/generic/numberparsing_macros.h)** 抄 simdjson 的实现 |

### 原则 4：编译选项的跨平台 mapping

```bash
# x86-64 (Skylake+)
gcc -O3 -march=x86-64-v3          # 含 AVX2+FMA+BMI2
gcc -O3 -march=native             # 本机优化（仅本机分发）

# ARMv8.2+ (Graviton 3 / M1)
gcc -O3 -march=armv8.2-a+fp16+dotprod+crypto

# ARMv9 (Neoverse V2 / M2+)
gcc -O3 -march=armv9-a+sve2

# RISC-V RV64GCV
gcc -O3 -march=rv64gcv_zba_zbb    # G=IMAFD, C 压缩, V 向量, B 位操作
```

### 原则 5：Profile 工具的跨平台选择

| 工具 | x86 | ARM | RISC-V |
|------|-----|-----|--------|
| **`perf`** | ✅ Linux 通用 | ✅ Linux 通用 | ✅ Linux 通用（PMU 部分）|
| **`likwid`** | ✅ | ✅（成熟）| 🚧 部分 |
| **VTune** | ✅ 最强 | ✅（Intel 编译器版本）| ❌ |
| **OSACA** | ✅ | ✅（Neoverse N1/V2/M1 等）| 🚧 规划中 |
| **Spike / QEMU profile** | — | — | ✅ 仿真器内 profile |
| **Apple Instruments** | — | ✅（仅 macOS/iOS）| — |

---

## 🧰 第 6 部分：OSACA 详解（ARM 生态的 Agner）

[OSACA](https://github.com/RRZE-HPC/OSACA)（Open Source Architecture Code Analyzer）由 Erlangen-Nürnberg 大学的 HPC 小组开发，是**跨 x86 + AArch64 的指令级性能分析器**。

### 6.1 OSACA 做什么

输入：一段汇编循环（含 OSACA 标记）
输出：
- **Throughput analysis**（吞吐）—— 端口利用率
- **Critical path**（CP）—— 最长依赖链
- **Loop-carried dependency**（LCD）—— 跨迭代依赖

### 6.2 支持的微架构（2026-08）

**x86**：Sandy Bridge → Ivy Bridge → Haswell → Broadwell → Skylake-X → Cascadelake → Icelake (client/server) → Sapphire Rapids → **Granite Rapids**（2026-08 新增）

**AArch64**：
- ARM Cortex-A72
- **ARM Neoverse N1**（Graviton 2）
- **ARM Neoverse V2**（Graviton 4 / NVIDIA Grace）
- Marvell ThunderX2
- **Fujitsu A64FX**（Fugaku 超算）
- HiSilicon TaiShan v110
- ⭐ **Apple M1 Firestorm**（Dougall 逆向数据）
- NVIDIA Neoverse V2 / Grace

### 6.3 怎么用（集成进 Godbolt）

最简方式：[godbolt.org](https://godbolt.org) → 切换语言到 "Analysis" → 粘贴汇编 → 选 OSACA + `--arch=V2`（Neoverse V2）。

命令行：
```bash
pip install osaca
osaca --arch V2 my_kernel.s   # 分析 ARM Neoverse V2
osaca --arch M1 my_kernel.s   # 分析 Apple M1
osaca --arch SKX my_kernel.s  # 对比 x86 Skylake-X
```

输出示例（来自 OSACA README）：
```
                                         Port pressure in cycles
    | 0 - 0DV | 1 | 2 - 2D | 3 - 3D | 4 | 5 | 6 | 7 || CP | LCD |
------------------------------------------------------------------
0.50| 0.50    |   | 0.50   | 0.50   |   |   |   |   || 8.0|    | vmulpd (%r12,%rax),%ymm1,%ymm0
    |         |   | 0.50   | 0.50   |1.0|   |   |   || 5.0|    | vmovapd %ymm0,0(%r13,%rax)
0.25| 0.25    |   |        |        |   |0.25|0.25|   ||    | 1.0| addq $32,%rax
```

### 6.4 OSACA vs Agner Fog

| 维度 | Agner Fog | OSACA |
|------|-----------|-------|
| 覆盖 ISA | x86 only | x86 + AArch64 |
| 数据形式 | PDF/ODS 表格 | 自动化工具 + 数据库 |
| 维护频率 | Vol 3 ~6 个月一次 | 持续 commit（2026-08 还在加 GNR）|
| 集成 Godbolt | ❌ | ⭐ ✅ |
| 商业级支持 | 个人 | 学术组（RRZE-HPC）|

**互补**：Agner Vol 3 的微架构**叙述**更深入（讲设计权衡），OSACA 的**数据 + 自动分析**更实用。两者都看最佳。

> 📖 **OSACA 深度拆解**：仓库结构 + YAML schema + 主类 API + 核心算法（throughput/CP/LCD）+ 怎么扩展新核心，见 **[OSACA_INTEGRATION.md](OSACA_INTEGRATION.md)**（含本地化的 [osaca_data.py](../cmu-cs-projects/topic2-systems/osaca_data.py) 可离线查询 + [osaca_mini.py](../cmu-cs-projects/topic2-systems/osaca_mini.py) 算法复现）。

---

## 🛣️ 第 7 部分：学习路径（按目标）

### 移动开发（iOS / Android）
1. ARM Learn the Architecture → A-profile 基础
2. Apple Silicon：[Dougall's M1 tables](https://dougallj.appspot.com/apple/firestorm.html) + WWDC 性能 session
3. Instruments / Android Profile
4. 实战：用 NEON/AMX 优化一个图像滤镜

### 云服务器（AWS Graviton / Ampere）
1. AWS Graviton Performance Runbook
2. ARM Neoverse SOG（V2/V3）
3. Cloudflare / AWS blog 实战
4. 实战：把一个 x86 微服务迁移到 Graviton，benchmark 性价比

### 嵌入式 / IoT（Cortex-M / RISC-V 嵌入式）
1. ARM Cortex-M TRM
2. RISC-V Embedded Profile spec
3. 平头哥 C910 / SiFive E-series 文档
4. 实战：QEMU 上跑一份 RISC-V 嵌入式代码

### 高性能计算（HPC / AI 算子）
1. A64FX 文档 + SVE-512 实战
2. RVV spec + Spike 仿真器
3. ⭐ **OSACA + Godbolt** 反复分析你的汇编
4. 实战：用 RVV / SVE 写一个矩阵乘，三 ISA 对比

### 编译器 / 工具链工程师
1. ARM ARM / RISC-V Spec 完整读
2. LLVM ARM/RISC-V 后端源码
3. OSACA 源码（怎么测指令延迟）
4. 实战：给 OSACA 加一个新核心支持

### 硬件设计（自研 RISC-V 核）
1. BOOM 源码 + Berkeley CS152/252 课件
2. Chipyard 框架
3. RISC-V Test Suite
4. 实战：在 FPGA 上跑一个 BOOM 设计

---

## 🎯 第 8 部分：与现有文档的关联

| 本文档章节 | 关联文档 |
|-----------|---------|
| 第 1 部分 三 ISA 对比 | [CSAPP_HARDWARE_TRUTHS.md](CSAPP_HARDWARE_TRUTHS.md) 真相 1（cache）、真相 4（分支）、真相 7（内存模型）|
| 第 2 部分 ARM 独特性 | [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) 第 3 部分（x86 微架构）|
| 第 3 部分 RISC-V VLA | [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) 第 5 部分（SIMD）|
| 第 4 部分 横向对比 | [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) 第 4 部分（指令延迟）|
| 第 5 部分 跨平台原则 | [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) 第 2 部分（10 大原则）|
| 第 6 部分 OSACA | [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) 第 9 部分（testp/perf/likwid）|

### 三件套完整链路

```
CSAPP_HARDWARE_TRUTHS.md              ← 为什么（8 个硬件真相的原理，ISA 无关）
    ↓
AGNER_FOG_OPTIMIZATION.md             ← 怎么优化（x86 阵营的指令级手法）
    ↓
ARM_AND_RISCV_OPTIMIZATION.md（本文档） ← 其他 ISA（ARM/RISC-V 的独特性 + 跨平台）
    +
arm_riscv_optimization_demo.py        ← 可跑对比
```

---

## 📚 第 9 部分：核心参考资料

### 必读
- ⭐ **ARM ARMv8-A / ARMv9-A Architecture Reference Manual**（ARM 账户免费下载）
- ⭐ **[RISC-V V spec v1.0](https://github.com/riscvarchive/riscv-v-spec)** + `recip.c` Newton-Raphson 参考
- **[ARM Cortex-A Series Programmer's Guide](https://developer.arm.com/architectures/learn-the-architecture/a-profile)**
- **[OSACA 论文](https://arxiv.org/abs/1910.00214)**（PMBS19）

### 实战博客（持续更新）
- **[Cloudflare Graviton blog](https://blog.cloudflare.com/tag/aws-graviton/)**
- **[AWS Graviton getting started](https://github.com/aws/aws-graviton-getting-started)**
- **[Dougall's Apple Silicon tables](https://dougallj.appspot.com/apple/firestorm.html)**
- **[SiFive blog](https://www.sifive.com/blog)**

### 工具
- ⭐ **[OSACA](https://github.com/RRZE-HPC/OSACA)** —— ARM/Apple 优化的核心分析器
- ⭐ **[Highway](https://github.com/google/highway)** —— 跨平台 SIMD 库
- **[Spike](https://github.com/riscv-software-src/riscv-isa-sim)** —— RISC-V 官方仿真器
- **[SLEEF](https://sleef.org/)** —— 跨平台数学库
- **[godbolt.org](https://godbolt.org)** —— 集成 OSACA，在线分析汇编

### 课程
- **Berkeley CS152/252** —— 计算机架构（RISC-V 设计源头）
- **CMU 18-447** —— Introduction to Computer Architecture（含 ARM/RISC-V）
- **MIT 6.5940** —— AI 算子优化（含 ARM/RISC-V SIMD）

---

**完成日期**：2026-08-12
**作者**：AI Mentor (ai-mentor) + 学生
**版本**：v1.0
**配套**：CSAPP_HARDWARE_TRUTHS.md + AGNER_FOG_OPTIMIZATION.md + arm_riscv_optimization_demo.py
**数据时效**：基于 OSACA GitHub（2026-08-06 最新 commit）+ ARM 官方文档（2026）+ RISC-V V spec frozen v1.0
