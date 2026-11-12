# 09 · SIMD 侧翼军团与死架构遗存——MMS/LSX/AltiVec/坟场 README

## 一、角色定位：两条侧翼层加一片基因库

图谱把非 x86/ARM 的 SIMD 全部收进两条层：layer:10（SIMD·MIPS，120 节点/119 文件，全在 `libavcodec/mips/`）与 layer:11（SIMD·其他，101 节点/98 文件）——后者含 `loongarch/` 45、`ppc/` 35、`alpha/` 14，以及四个象征性存在：`avr32/mathops.h`、`bfin/README`、`sh4/README`、`sparc/README` 各一。对 GMAT 这个 NVIDIA GPU 工具箱来说，这 217 个文件全部是**上游 FFmpeg 的继承资产，零 NVIDIA 增量**；但它们恰恰是 FFmpeg "地球上所有 CPU 都要跑"哲学的化石剖面——从 DEC Alpha（1990s 工作站）到龙芯 LSX/LASX（2020s 国产自主指令集），一部 SIMD 进化史横跨三十年被完整冻结在仓库里。归档价值是本篇的主叙事：这层代码的读者不是 GMAT 用户，而是指令集考古者与移植工程师。

## 二、内部结构：mips 三线与 loongarch 双宽度

**mips/ 的三条优化线**由 configure 定义：`--disable-mipsdsp / --disable-mipsdspr2 / --disable-mipsfpu`（`configure:459-462`）对应 MIPS DSP ASE R1/R2 扩展与硬浮点；文件层面则是 `_mmi` 后缀 17 个 + `_msa` 后缀 34 个 + 无后缀 C 重写若干（如 `aaccoder_mips.c`）。MMI 是**龙芯私有的 MIPS 扩展**——`configure:2646` `mmi_deps_any="loongson2 loongson3"`，这是龙芯世代之前（LoongISA 时代）在 MIPS 框架内加的多媒体指令；MSA（MIPS SIMD Architecture）则是 MIPS r5 标准的 128-bit 向量单元。调度范式同 x86/ARM：`mips/h264dsp_init_mips.c:31` `if (have_mmi(cpu_flags))` 先挂 MMI，`:81` `if (have_msa(cpu_flags))` 再挂 MSA。第三条线是 `aaccoder_mips.c` 这类**纯 C 指令级优化**——重写心理声学模型利用 MIPS 分支延迟槽与乘加特性，不碰任何向量单元。

**loongarch/ 是 mips/mmi 的直系后代**：龙芯弃 MIPS 自立 LoongArch 指令集后，上游社区把原 MMI 汇编移植成 LSX（128-bit，对标 MSA）与 LASX（256-bit，对标 AVX2）。宽度依赖链在 `configure:2647-2648`：`lsx_deps="loongarch"`、`lasx_deps="lsx"`——LASX 是 LSX 的超集扩展。文件计数 13 个 `_lsx` + 15 个 `_lasx`，覆盖 h264/hevc/vp8/vp9/idct/hpel 全家。调度见 `loongarch/hevcdsp_init_loongarch.c:30` `if (have_lsx(cpu_flags))` 与 `h264chroma_init_loongarch.c:30` `if (have_lasx(cpu_flags))`，命名习惯 `_lasx.c` 存 C intrinsic 实现（lasx intrinsic 由 LoongArch 工具链提供）。

## 三、外部连接：ppc 的 intrinsics 路线与 alpha 的手工指令宏

**ppc/ 走第三条路线：AltiVec intrinsics**。PowerPC 的向量 C 扩展由编译器内建（`vec_s16`/`vec_u8`/`vec_mladd`），所以 ppc 目录几乎全是 `.c` 文件，唯一的 `.S` 是 `fft_altivec.S`。典型实现 `ppc/h264chroma_template.c:24` 起的 `CHROMA_MC8_ALTIVEC_CORE(BIAS1, BIAS2)` 宏——四路 `vec_mladd` 乘加链做 8 抽头色度插值，BIAS 参数化 rnd/no_rnd 两个变体，文件头注释直言前提 "stride % 16 == 0"。ppc 内部又有**两代向量线**：AltiVec（`configure:2637` `altivec_deps="ppc"`，G4/G5 时代）与 VSX（`:2641` `vsx_deps="altivec"`，POWER7+ 的扩展），`fft_vsx.c`/`fft_altivec.S` 并存即此历史。同目录 `h264qpel_template.c`、`hevcdsp_template.c` 复用同一宏模板法。

**alpha/ 是最古老的一档**：DEC Alpha 的运动视频指令 MVI。`alpha/asm.h:40` 定义能力位 `AMASK_MVI (1 << 8)`（运行时读 amask 指令判断 CPU 是否有 MVI），`:103-106` 手写 `prefetch/ prefetch_en/ prefetch_m/ prefetch_men` 四种预取指令的 GCC 内联汇编封装，`:107-109` 起是 `cmpbge/extql/extwl` 字节比较与提取指令族。三个 `.S` 文件（`hpeldsp_alpha_asm.S` 125 行、`idctdsp_alpha_asm.S` 167 行、`me_cmp_mvi_asm.S` 179 行）配 `regdef.h`（DEC 汇编的寄存器助记名）。这是 FFmpeg 里唯一还在维护构建的"前 SIMD 时代"向量代码。

**avr32/mathops.h 是活化石中的活化石**：Atmel AVR32 32 位 MCU 的 95 行头文件，全部内容是用 `muls.d / machh.w / mulhh.w` 指令内联汇编实现 `MULL/MULH/MUL64/MAC64/MAC16/MUL16/mid_pred`（mathops.h:26 起 MULL）。AVR32 芯片 2010 年前后停产，这份文件留存的唯一理由是"还没人提交删除"。

## 四、数据流：坟场 README 的交接协议

四个死架构目录里三个只剩 README，且内容是标准化的墓志铭格式——`bfin/README`：Blackfin 优化已在 commit `880e2aa23645ed9871c66ee1cbd00f93c72d2d73` 移除，最后含优化版本 `fa4e17c14035ebf43130fb369e1728cdd98d0b72`；`sh4/README`：SH4 在 `d6096a67422534918405abb46dafbbac4608cbc3` 移除；`sparc/README` 同构（sparc 的 vis 指令优化移除得更早）。README 尾部都附同一句："如果你想维护这些（或其他）BFIN 优化，请联系 ffmpeg-devel@ffmpeg.org"。

这个模式值得注意：**上游用目录墓碑 + commit 双指针完成知识交接**——任何人 git checkout 那个"最后版本"哈希即可复活整套实现，README 又给出了复活流程（联系邮件列表认领维护权）。移除的原因也很现实：无维护者的 SIMD 代码在 CI 盲区里腐烂，寄存器约定与 C 结构体演进脱节后比没有更危险。GMAT 整仓导入时原样保留了这些墓碑（git 单 commit b1aea74），它们现在是仓库里最接近"负资产"的文件，却也是最便宜的文档。

## 五、设计决策：为什么留着它们

- **移植市场的长尾**：FFmpeg 编译目标里 MIPS（路由器/盒子）、LoongArch（国产化替代）、PPC（AIX/老 Mac/嵌入式工业）都有真实部署；GMAT 虽然只关心 NVIDIA GPU 平台，但 fork 整个上游意味着将来 diff/rebase 上游时这些目录零冲突。
- **MMI→LSX 移植范本**：loongarch/ 与 mips/mmi 的函数名几乎一一对应（h264dsp、vp9dsp……），是研究"ISA 更替期如何搬运向量代码"的现成教材——同一算法在 MMI（MIPS 编码）、LSX/LASX（LoongArch 编码）、NEON（ARM 编码）、x86inc（x86 编码）四套语法下的对照，全仓可得。
- **三种实现策略并存的活实验**：x86 手写宏汇编 / ARM GAS 汇编 + 少量 intrinsics / PPC 全 intrinsics / MIPS C 重写——性能上限、可移植性、维护成本四个维度的取舍在同一仓库内全部可对比。
- **能力检测一律 runtime**：从 alpha 的 AMASK_MVI（asm.h:40）到 loongarch 的 have_lasx，全部遵循 av_get_cpu_flags 体系——同一二进制可跑全家族芯片，这是嵌入式分发（SDK 出一个 so）的硬需求。

## 六、新人提示

1. **别在这两层找 GPU 相关任何东西**：GMAT 的增量集中在 libavfilter（tensorrt/nvcv/cuda 滤镜）与 libswscale/cuda；mips/loongarch/ppc/alpha 是纯上游继承，grep NVIDIA 一无所获是正常的。
2. **读懂 configure 的 ISA 依赖图**：`configure:2637-2648` 一段浓缩了 ppc/loongarch 全部档位关系（altivec⊂vsx，lsx⊂lasx，mmi 绑 loongson2/3），比读任何文档都快。
3. **移植新 codec 到新 ISA 的模板**：抄 hevcdsp 的三件套结构（init + 实现 + Makefile），从 `have_*` 调度抄到 `*_template.c` 宏——mips/loongarch 两目录的 h264dsp_init 就是现成骨架。
4. **死架构复活流程**：README 给的 commit 哈希是入口，`git log --diff-filter=D -- libavcodec/bfin/` 可考古完整删除史；若真要复活，先跑 tests/checkasm 验证寄存器约定没被岁月破坏。
5. **行号锚自验**：configure:459-462/2637/2641/2646-2648、h264dsp_init_mips.c:31/81、hevcdsp_init_loongarch.c:30、h264chroma_init_loongarch.c:30、ppc/h264chroma_template.c:24、alpha/asm.h:40/103-109 均于 2026-11-07 源码核实；avr32 MULL 行号约 :26（文件短，肉眼可核）。

---
**甄别条款记录**：任务书"221 文件"为两层层节点总数（120+101）；图谱实测 file 节点 119+98=217，差异为非 file 节点（config 类），文中采用双口径注明。bfin/sh4/sparc 的移除 commit 哈希直接引自各自 README 原文，未回溯 git 历史验证（GMAT 仓 git 仅 1 个 commit，历史压缩无法本地验证）。"MMI→LSX 直系后代"表述基于函数名对照与上游公开演化史，属合理推断。
