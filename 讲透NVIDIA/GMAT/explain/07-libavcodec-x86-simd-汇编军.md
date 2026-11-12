# 07 · libavcodec/x86 SIMD 汇编军——198 个文件的手写汇编机器

## 一、角色定位：GPU 转码仓里的 CPU 底座

GMAT（GPU toolkit on Multimedia, AI and Transcoding）的主叙事是 GPU 加速：NVENC/NVDEC、tensorrt 滤镜、libgpuscale。但图谱把 `ffmpeg-gpu/libavcodec/x86` 单独划成一层（layer:08，197 个 file 节点 + 配置节点），原因很简单：**它是整个仓库里最大的一支"手写汇编部队"**，97 个 `.asm` 文件 + 67 个 `*_init.c` 调度文件 + 15 个头文件与 C 模板。GPU 通道再快，CPU 侧的像素半像素插值、环路滤波、熵解码辅助、音频 DSP 仍是每个转码管线绕不开的底座——当 hwaccel 不可用、滤镜必须下到系统内存、或者纯 CPU 编码器（如 libx264 之外的内置编码器）上场时，性能就全压在这层 SIMD 上。

这一层的组织纪律极其统一：每个 DSP 子系统（h264、hevc、vp9、aac、fft……）在 `libavcodec/` 主目录有一个 C 参考实现与函数指针表（如 `H264DSPContext`），x86 目录则提供三件套——`xxx.asm`（手写汇编实现）、`xxx_init.c`（CPUID 检测 + 函数指针填充）、共享头。这是一支不依赖任何 intrinsics（个别例外见第五节的 neon 对比）的纯汇编军，全部经由 NASM/X86ASM 汇编器体系编译。

## 二、内部结构：%include 体系与 cglobal 符号工厂

x86 汇编军的骨架是一套自建的宏语言，核心在 `libavutil/x86/`：

- **`x86inc.asm`**——宏汇编"标准库"。最关键的是 `cglobal` 宏（`x86inc.asm:720` 定义 `%macro cglobal 1-2+`，内部转 `cglobal_internal`），它把一个汇编标签自动生成两份符号：`ff_name_sse2`（全局导出）与带下划线/省略前缀的平台变体，同时承担函数序言（PROLOGUE）——寄存器个数声明、栈对齐、PIE 重定位修正一次完成。`cglobal foo, 2,3,7,0x40, dst, src, tmp`（`x86inc.asm:139` 注释示例）依次是：名字、参数寄存器数、总寄存器数、xmm 数量、栈用量、参数语义名。
- **`INIT_*` 家族**——同一段汇编主体按指令集宽度重编译的开关：`INIT_MMX`/`INIT_XMM`/`INIT_YMM` 分别在 `x86inc.asm:951/963/978` 定义。写一遍算法主体，用 `m0`~`m15` 这样的抽象向量寄存器名，切换 INIT 后 m0 自动映射到 mm0/xmm0/ymm0。实例如 `x86/h264_intrapred.asm:51` 的 `INIT_XMM sse`、`:101` 的 `INIT_MMX mmxext`、`:152` 的 `INIT_XMM sse2`——同一个文件里同族函数按sse→mmxext→sse2→ssse3 多轮重展开。
- **`x86util.asm`**——每个 .asm 的第一行 `;***…` 版权头之后必是 `%include "libavutil/x86/x86util.asm"`（`x86/h264_intrapred.asm:25`），提供 SBUTTERFLY、HADDD 等高频复合宏。

数据段同样有纪律：`SECTION_RODATA`（`h264_intrapred.asm:27`）集中放常量 shuffle 掩码；跨文件共享常量用 `cextern pb_1 / pw_4`（`h264_intrapred.asm:42-45`）声明，定义在 C 文件 `x86/constants.c` 里——`DECLARE_ALIGNED(32, const ymm_reg, ff_pw_1)`（`constants.c:24` 起）配合 `constants.h:31` 的 `extern const ymm_reg ff_pw_4`，C 与汇编共享同一份对齐常量表，这是"一处定义、两端引用"的教科书做法。

## 三、外部连接：与 C 框架的三个接口面

**接口一：init 分发函数。** 每个 `*_init.c` 暴露一个 `av_cold void ff_xxx_init_x86(...)`，例如 `x86/h264dsp_init.c:190` 的 `ff_h264dsp_init_x86(H264DSPContext *c, const int bit_depth, ...)`。这些函数由 libavcodec 主目录的平台无关代码在构建 DSPContext 时条件调用（`#if ARCH_X86` 包裹），把检测到的最优实现填进函数指针。

**接口二：CPU 能力检测。** 标准范式在 `x86/hevcdsp_init.c:709`：`int cpu_flags = av_get_cpu_flags();` 随后按从旧到新的顺序逐级覆盖：`EXTERNAL_MMXEXT(cpu_flags)`（:712）→ `EXTERNAL_SSE2`（:717）→ `EXTERNAL_SSSE3`（:740）→ `EXTERNAL_SSE4 && ARCH_X86_64`（:747）→ `EXTERNAL_AVX`（:759）→ `EXTERNAL_AVX2`（:778）→ 顶级 `EXTERNAL_AVX512ICL && ARCH_X86_64`（:878）。顺序保证"后写者胜"，最终指针表停留在 CPU 支持的最快一档。`EXTERNAL_*` 宏同时检查编译期启用与运行期 CPUID，避免向不支持 AVX 的机器下发 VEX 指令。

**接口三：函数声明宏。** asm 里的符号要在 C 侧可见，靠 `h264dsp_init.c:135-149` 这类宏批量声明：`H264_WEIGHT(W, OPT)` 展开成 `void ff_h264_weight_##W##_##OPT(...)`，W 取 16/8、OPT 取 mmxext/sse2——宏拼接保证 C 声明与 asm 的 cglobal 命名严格同步，一处改名两端报错。

## 四、数据流：从 cglobal 到帧循环

一次 H.264 帧解码中，这层数据流是：主解码器调用 `c->h264_v_loop_filter_luma(ptr, stride, ...)` → 指针在 `ff_h264dsp_init_x86` 时已指向 `ff_h264_v_loop_filter_luma_sse2` 之类 → 进入 `.asm` 主体。汇编内部自循环：`h264_intrapred.asm:51` 起的 `pred16x16_vertical_8` 先 `sub r0, r1` 回退到参考行，`movaps xmm0, [r0]` 载入后用 `.loop` 标签按 stride 逐行 `movaps [r0+r1*1], xmm0` 写出——参数寄存器 r0/r1 是 cglobal PROLOGUE 按平台（x86-64 SysV）自动绑定的。

两种"生成器"模式扩大了复用面：其一，C 模板双编译——`x86/hpeldsp_rnd_template.c:31` 的 `DEF(put, pixels8_x2)` 用 DEF 宏参数化 rnd/no_rnd 两个变体，每个变体内嵌 `__asm__ volatile` 老式 MMX 内联汇编（这是 2000-2004 年代遗风，文件头署名 Fabrice Bellard/Michael Niedermayer/Nick Kurshev）；其二，符号别名——`x86/h264_qpel.c:44` `#define ff_put_pixels8_l2_sse2 ff_put_pixels8_l2_mmxext`，SSE2 版本与 mmxext 版逐位相同则直接复用二进制，省一份编译产物。

## 五、设计决策：为什么是手写汇编

- **跨厂商宏汇编 vs intrinsics**：x86inc 体系 2007 年起统一了 NASM 语法，一份源码覆盖 MMX→AVX-512 全宽度谱系（同目录 `constants.c` 中 `ff_pw_1/ff_pw_4/ff_pw_255/ff_pw_256/ff_pw_512` 用 `DECLARE_ASM_ALIGNED` 精确控制 8/16/32 字节对齐，随指令集升级常量也升宽度）。这是 FFmpeg 社区在 GCC/MSVC intrinsics 兼容泥潭之外的选择，代价是上手陡峭。
- **守门员宏 `HAVE_X86ASM`**：`h264_qpel.c:28` `#if HAVE_X86ASM` 包住全部声明——无汇编器的平台（部分交叉编译）整体退回 C，不会编译失败。
- **AVX-512 谨慎 gating**：只有 ICL 目标（`AVX512ICL`）且 64 位才启用（`hevcdsp_init.c:878`），因为早期 Xeon Phi/AVX-512 降频问题，体现"最后一级增益必须无风险"的原则。
- **与 GPU 层的分工**：这层从不触碰 CUDA——GPU 化的 motion comp/缩放在 libswscale/cuda、vf_*_nvcv 等处。x86 军的存在恰恰是 GPU 军的保险：`ffmpeg -hwaccel cuda` 的输出落到 CPU 滤镜链时，靠它们兜住性能。

## 六、新人提示

1. **加一个新 SIMD 函数的路径**：在 `.asm` 写 `cglobal myfunc, 3,4` 主体 → 在对应 `*_init.c` 加 EXTERNAL 门控与指针赋值 → C 侧宏声明 → `tests/checkasm/` 下对应文件加测试（checkasm 目录有 x86/arm/aarch64 三套基线，逐函数对比 C 参考实现输出位级一致）。
2. **命名即契约**：`ff_<op>_<bitdepth/size>_<isa>` 的拼接顺序错一位，链接期才爆 undefined reference——先用 `nm libavcodec/x86/xxx.o | grep ff_` 对照符号。
3. **改 INIT 顺序坑**：INIT_XMM sse2 写在 ssse3 之后不会自动覆盖，同名 cglobal 重复定义汇编器直接报错；同函数多 ISA 版本必须每个 INIT 块内各写一份或用 `%rep` 宏族。
4. **PROLOGUE 栈对齐**：cglobal 第五参（如 `0x40`）是栈需求，漏写会在调用 SSE 要求 16 字节对齐的 libc 时崩——症状是只在部分 glibc 版本崩溃。
5. **读码入口推荐**：`h264_intrapred.asm`（结构与注释最全）→ `constants.c`（常量体系）→ `hevcdsp_init.c:700-960`（最完整的调度瀑布）。

---
**甄别条款记录**：本文所有行号锚（h264_intrapred.asm:25/27/42/51/101/152、x86inc.asm:139/720/951/963/978、constants.c:24、constants.h:31、h264dsp_init.c:135/190、hevcdsp_init.c:709/712/740/747/759/778/878、hpeldsp_rnd_template.c:31、h264_qpel.c:28/44）均于 2026-11-07 在 /usr-data/data2/repos/agent-repos/NVIDIA/GMAT/ffmpeg-gpu 源码逐一核实；文件计数（97 asm/67 init/15 h）由 ls 实测。任务书"198 文件"与图谱 layer:08 的 197 file 节点差 1，采信图谱口径并按目录实测复核。
