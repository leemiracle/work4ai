# 视角 4：编译器专家（Compiler Engineer）

> **审查时间**：2026-06-30
> **审查者**：作者亲自撰写（councillor delegate 超时，基于已掌握信息整理）
> **背景假设**：LLVM ARM backend / GCC auto-vectorizer / oneDNN codegen 经验
> **方法**：从工具链对比、codegen 质量、auto-vectorization 角度审查

---

## 1. 视角定位

我关注的是：**编译器对代码的翻译质量**——同一段 C 源码在 PhyGCC 12.3.2 / gcc-9 / clang-10 下生成的 ARMv8.2 机器码差异、auto-vectorizer 的能力边界、intrinsics vs inline ASM 的工程权衡、`-march/-mtune/-ffast-math` 的实际效果、LTO/PGO 收益。我不看算法，只看 codegen。

## 2. 八个盲区（编译器视角）

### ① 三套编译器零系统性横评
项目实测了 PhyGCC vs 手写 ASM（v0.4，差距 < 0.3%），但**从没把 PhyGCC 12.3.2 / gcc-9 / clang-10 放在同一份代码上跑过同 bench**。PhyGCC 是飞腾定制 GCC 12.3.2，理论上对 FTC862 微架构做了 `-mtune=phytium-ftc862` 之类的调度调优；clang-10 较老（2020）但 NEON backend 历来优于 GCC。**关键问题：clang vs PhyGCC 在 NEON GEMM 上谁快？** 这是 v0.10 的第一个 P0 实验。

### ② `-ffast-math` 从未测过
当前 `-O3` 不开 fast-math。GEMM 是数值密集型，`-ffast-math` 允许编译器：
- 重排 FP 指令（破坏严格结合律，可能改变 NEON 累加顺序）
- 假设无 NaN/Inf（QA/安全视角会很警惕）
- 把 `a*b+c` 收缩成单条 `vfmaq`（FP contraction）

**预期**：对 GEMM，`-O3 -ffast-math` 可能 +5-15%（FMA contraction 让 `mul+add` 融合）。但会改变 `gemm_f32_scalar` 的 reference 行为——QA 视角说"oracle 不能同源"就是这问题。

### ③ Auto-vectorize 从未对比
手写 `vfmaq_laneq_f32` vs gcc `-ftree-vectorize` 自动向量化，谁更快？项目假设手写胜出，但 PhyGCC 12.3.2（GCC 12）的 vectorizer 已经很强。**写一个 `gemm_naive_for_auto.c`（无 intrinsics，纯标量循环），开 `-O3 -ftree-vectorize -fopt-info-vec` 看 GCC 能否自动向量化**。如果能，工作量大幅减少；如果不能，记录 GCC 失败的循环模式。

### ④ `-march` vs `-mcpu` 选择缺失
当前 `-march=armv8.2-a+fp16+dotprod` 是 ISA level。`-mcpu=phytium-ftc862`（如果 PhyGCC 支持）会让编译器按 D3000 的具体 pipeline 调度（issue width、FVU latency、cache 行为）。**未知 PhyGCC 是否定义了 `-mcpu=phytium-ftc862`**——`/opt/apps/phygcc-12.3.2/bin/gcc --help=target | grep phytium` 一查就知道。

### ⑤ FP16 反直觉发现的 codegen 根因未验证
v0.8 发现 FP16 MR=8 比 MR=2 慢 12%，归因"`vfmaq_laneq_f16` 单 instr 吞吐 < 4/cyc"。但**没看 disassembly**：
```bash
objdump -dS bin/gemm_f16 | grep -c 'fmla.*v'   # 数 FMLA 指令数
objdump -dS bin/gemm_f16 | grep -c 'str.*q'    # 数寄存器溢出
```
如果 MR=8 版本 `str q` 数 > 0（寄存器溢出），那是真因。性能架构师也指出了这一点。

### ⑥ LTO / PGO 零探索
LTO（Link-Time Optimization）跨文件 inline，对算子库收益小（每个 .c 独立）；但 **PGO（Profile-Guided Optimization）** 对 GEMM 可能有 +5%：编译时插桩，跑 representative bench，再用 profile 重新编译，让编译器按真实 branch 频率调度。

### ⑦ Cross-compilation 矩阵缺失
项目假设 D3000 自身编译。但实际部署可能：x86 host → cross-compile → D3000 target。**`aarch64-linux-gnu-gcc` 已经在系统里**（devops 实测），但没测过它 vs PhyGCC 的 codegen 差距。

### ⑧ SVE 探测缺失（与硬件视角交叉）
`-march=armv8.6-a+sve2` 是否在 D3000 上 work？需要先 `mrs ID_AA64PFR0_EL1` 探测 SVE 字段。**D3000 FTC862 大概率是 ARMv8.2-A，无 SVE**，但应实测确认。若有 SVE，`whilelo`/`ld1rqw` 能让 INT8 GEMM 再省 4-6 instr/iter。

## 3. 改造建议（按优先级）

### P0（最高 ROI，1-2 天）

1. **`scripts/compiler-compare.sh`**：一键三编译器横评
   ```bash
   for CC in phygcc gcc-9 clang-10; do
       $CC -O3 -march=armv8.2-a+fp16+dotprod src/gemm_f32.c -o /tmp/gemm_$CC -lm
       echo "=== $CC ==="; ./tmp/gemm_$CC | grep GFLOPS
   done
   ```
2. **Makefile 加 `make cmp-compiler` 目标**：跑 P0.1，输出 markdown 对比表
3. **`objdump` FP16 vs FP32 disasm 分析**：写 `scripts/disasm-analyze.sh` 数 spill

### P1（结构性收益）

4. **加 `-ffast-math` build variant**：`make CFLAGS+=-ffast-math all`，重跑 bench，标注哪些算子受益、哪些受损（precision lens 重跑）
5. **`gemm_naive_for_auto.c`** + `-fopt-info-vec-missed` 报告：理解 GCC vectorizer 边界
6. **`-mcpu` 探测**：`gcc --help=target | grep -i phytium`，若有则 Makefile 默认加 `-mcpu=phytium-ftc862`

### P2（长期）

7. **LTO/PGO 实验**：`-flto` + `-fprofile-use`
8. **SVE 探测 + armv8.6-a BF16/BFDOT**（与算法科学家 P0 重叠）
9. **Cross-compile matrix**：x86 host 编 D3000 target 的代码大小/性能差距

## 4. 关键洞察

1. **"PhyGCC -O3 已达手写 ASM 水平"（v0.4 结论）可能不是 PhyGCC 强，是 ASM 没写好**。GCC 12 在 NEON 上 codegen 已极强，手写 ASM 只在特殊指令（SDOT lane、LD1RQ、prefetch）才有优势。重新做手写 vs C 内联时，要写"高质量 ASM"（双缓冲 + 软流水），不是 v0.4 那种"逐指令对照"。

2. **FP16 MR=8 反直觉发现最可能的 codegen 根因是寄存器溢出**，不是 instr 吞吐。8 个 float16x8_t 累加器（8 reg）+ 8 个 a（8 reg）+ 1 bm（1 reg）= 17 reg，理论够用，但 lane-broadcast 形式编译器需临时寄存器，可能挤爆。objdump 是金标准。

3. **clang-10 vs PhyGCC 12.3.2 在 NEON GEMM 上的胜负未知**，但 clang-10（2020）通常比 GCC 12 在 vectorizer 上更强，可能跑出 +5-10%。这是 v0.10 必做的零成本实验。

4. **`-ffast-math` 是把双刃剑**：可能让 GEMM +5%，但会破坏 precision lens 的 FP32 reference（编译器自己 FMA 收缩）。建议作为可选 build variant 而非默认。

5. **算子库的"代码可移植性"由编译器视角决定**。如果代码只在 PhyGCC + `-march=armv8.2-a` 下最优，换到 Graviton/Apple M-series 就废。应该写"portable C"（用 `__ARM_ARCH` 等 macro 分支）。

## 5. 新增实验清单

| 文件 | 跑什么 | 回答的问题 |
|---|---|---|
| `scripts/compiler-compare.sh` | 三编译器横评 gemm/conv/attention | PhyGCC vs clang vs gcc 谁快 |
| `scripts/disasm-analyze.sh` | `objdump -dS bin/* \| grep -c 'str q\|fmla'` | FP16 MR=8 真因是寄存器溢出？|
| `src/gemm_naive_for_auto.c` | 纯标量循环 + `-fopt-info-vec` | GCC vectorizer 能否自动向量化 GEMM |
| `analysis/lens-march-mcpu.c` | sweep `-march=armv8.{2,4,6}-a` × `-mcpu` | 哪个 march/mcpu 最优 |
| `analysis/lens-fast-math.c` | `-O3` vs `-O3 -ffast-math` × {GEMM, Attention} | fast-math 增益多少 + 精度损失 |
| `analysis/lens-sve-probe.c` | `mrs ID_AA64PFR0_EL1` 解析 | D3000 是否有 SVE |

**底线判定**：项目从 v0.4 起就停在"PhyGCC 已达手写水平"这个旧结论上，从未做过编译器维度的系统性实验。**v0.10 的第一个 commit 应该是 `scripts/compiler-compare.sh`**——这是 30 分钟工作量，但能解答"PhyGCC 真的比 clang 强吗"这个根本问题。
