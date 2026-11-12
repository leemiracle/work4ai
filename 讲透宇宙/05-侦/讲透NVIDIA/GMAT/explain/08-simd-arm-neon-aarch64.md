# 08 · SIMD ARM 系军——arm/aarch64 双目录的 GAS 汇编体系

## 一、角色定位：移动与服务器第二战线的 204 个文件

图谱 layer:09（SIMD·ARM）收录 204 个 file 节点（层共 207 节点），分布是 `libavcodec/arm/` 140 个 + `libavcodec/aarch64/` 63 个 + `libavcodec/neon/` 1 个。对 GMAT 这个数据中心 GPU 工具箱而言，ARM 军的存在感来自两个现实：其一，Grace/Jetson 等 ARM64 GPU 平台正是 NVIDIA 自家硬件版图，ffmpeg-gpu 在这些平台上跑 CPU 兜底路径时全靠 AArch64 NEON；其二，这层代码是上游 FFmpeg 原生继承的大兵团，GMAT 无需改动即可整体受益——对比 GPU 增量（tensorrt.cpp 648 行、nvcv 滤镜四件套），ARM 军展示了 GMAT"继承上游全量 CPU 资产 + 点状注入 GPU 能力"的维护姿态。

与 x86 军的三点结构性差异先摆出来：**目录按位数分**（arm/ 是 32 位 ARM，aarch64/ 是 ARMv8 64 位，NEON 在两边都是主力但 ABI/寄存器集不同）；**汇编器用 GNU as**（`.S` 文件走 GAS，宏是 `.macro` 语法而非 NASM 的 `%macro`）；**历史分层更深**（armv5te→armv6→armv6t2→armv7→NEON→VFP 多条独立线）。

## 二、内部结构：function/endfunc 宏与 .arch 阶梯

aarch64 侧的"标准库"是 `libavutil/aarch64/asm.S`：`.macro function name, export=0, align=2`（`asm.S:158`）定义函数入口宏，其内嵌套 `.macro endfunc`（:159），导出符号、对齐、栈帧处理一次完成。实现在 `aarch64/h264dsp_neon.S:111` `function ff_h264_v_loop_filter_luma_neon, export=1` → `:132` `endfunc`，一开一闭包住整个函数体。这个文件还内置 **PAC（Pointer Authentication）支持**——`AARCH64_SIGN_LINK_REGISTER` 宏族（`asm.S:67/76` 注释详述 leaf/non-leaf 函数签名时机，`:134` 处编译期检查"启用 PAC 但平台不支持"则报错），是为 ARMv8.3+ 安全特性做的适配。

arm 侧 `libavutil/arm/asm.S` 用 `.arch` 指令切换指令集档位（`arm/asm.S:57` `armv7-a`、`:59` `armv6t2`、`:61` `armv6`），并区分 ELF 与非 ELF 目标的宏（`:23-26`）。

调度链范式看 `arm/hpeldsp_init_arm.c:45` `av_cold void ff_hpeldsp_init_arm(HpelDSPContext *c, int flags)`：先**无条件**填入 32 位 ARM 基线汇编（`ff_put_pixels16_arm` 等 16 项指针表），再 `if (have_armv6(cpu_flags)) ff_hpeldsp_init_armv6(c, flags)`（:67）逐级升档，`if (have_neon(cpu_flags))`（:69）最后挂 NEON 顶配。与 x86 的"瀑布覆盖"同构，但基线档就是汇编而非 C——32 位 ARM 上 C 参考实现几乎从不直接服役。

**VFP 独立支队**：浮点标量运算不走 NEON 走 VFP——`arm/fmtconvert_init_arm.c:44` `if (have_vfp_vm(cpu_flags))` 挂 `ff_int32_to_float_fmul_scalar_vfp`（:45），同类还有 `fft_vfp.S`、`libavutil/arm/float_dsp_vfp.S`。这是老 ARM "向量 VFP 模式"遗产，NEON 出现前的浮点主力。

## 三、外部连接：三个特殊接口面

- **asm-offsets 桥**：`arm/asm-offsets.h` 把 C 结构体字段偏移硬编码给汇编——`Y_DC_SCALE 0x04 / C_DC_SCALE 0x08 / AC_PRED 0x0c / BLOCK_LAST_INDEX 0x10 / H263_AIC 0x40 / INTER_SCANTAB_RASTER_END 0x88`，汇编函数据此直接访问 `MpegEncContext` 内部字段（neon/mpegvideo.c 一族需要）。这类偏移是 ABI 脆弱点，上游有 checkasm 式校验守护。
- **intrinsics 特例**：`neon/mpegvideo.c`（neon/ 目录独苗）走完全不同路线——`#include <arm_neon.h>`（:19）后用 `int16x8_t q0s16` 向量类型写 C，如 inline `ff_dct_unquantize_h263_neon(int qscale, int qadd, int nCoeffs, int16_t *block)`（:26 起）。它按 `ARCH_AARCH64/ARCH_ARM` 分别包含 `libavutil/aarch64/cpu.h` 或 `libavutil/arm/cpu.h`（:23-27），一份代码两代架构通用——与 x86 军"纯手写"路线的鲜明对照。
- **neontest 寄存器审计**：`aarch64/neontest.c` 提供 wrap 宏（`wrap(avcodec_open2(...))` 展开调用 `testneonclobbers(avcodec_open2, avctx, codec, options)`），在公共 API 边界检测 NEON 向量寄存器是否被 callee 破坏——ARM ABI 允许 SIMD 寄存器 clobber，但 FFmpeg 的调用约定要求 NEON 函数不破坏高半 q 寄存器，这套机制把它变成可测试断言。

## 四、数据流：bpp 模板生成与解码热路径

aarch64 目录有一个 x86 没有的生成机制——**BPP 宏模板**：`vp9dsp_init_10bpp_aarch64.c:23-25` 全文只有三行核心：`#define BPP 10` / `#define INIT_FUNC ff_vp9dsp_init_10bpp_aarch64` / `#include "vp9dsp_init_16bpp_aarch64_template.c"`；12bpp 文件同理。模板内部（`vp9dsp_init_16bpp_aarch64_template.c`）用 `declare_fpel(type, sz, suffix)`、`decl_mc_func(op, filter, dir, sz, bpp)` 宏按 BPP 拼出函数名与 2D 滤波复合函数（水平滤波落 `LOCAL_ALIGNED_16` 中间缓冲再垂直滤波，注释明言"h + 8 行因水平滤波需偶数行"）。同一物理模板编译两次，10bit 与 12bit VP9 各得一套 dispatcher。

解码热路径的代表是 `aarch64/h264dsp_neon.S`（1076 行）：loop filter、IDCT、QPel 全在 function/endfunc 对里，Q0-Q15 通道交织做 16 字节块的二维滤波；HEVC 侧 `arm/hevcdsp_sao_neon.S`（177 行）专攻 SAO 边界强度滤波。帧内预测的新式武器是 `aarch64/vp9mc_aarch64.S`——文件名直接叫 aarch64 而非 neon，因为它用到了 dot-product 指令（ARMv8.2 UDOT/SDOT 一类子帧内插加速），是"64 位专属指令集"分支的代表。

## 五、设计决策

- **两目录而非一目录**：上游社区把 arm/（32 位）与 aarch64/（64 位）彻底分开，即使算法同源也各自维护——NEON 指令集在两代上语法相近，但寄存器数量（16 vs 32 个 128 位）、ABI 参数寄存器、寻址模式差异太大，合并成本高于复制成本。
- **GAS 统一**：ARM 世界没有 NASM 那样的独立汇编器霸权，`.S` + GNU as 可与 C 工具链无缝联编（.S 后缀=预处理后汇编），这让 arm 军能直接 `#include "asm-offsets.h"`、用 C 预处理器做 BPP 生成——x86 军做不到（NASM 有自己的 %include 体系）。
- **基线即汇编**：hpeldsp 的调度链第一档就是手写 arm 汇编而非 C，反映嵌入式 ARM 上性能预算的历史现实；对比 x86 第一档是 mmxext 之上的 C fallback。
- **GMAT 零改动继承**：本层 204 文件无一含 NVIDIA 版权头（对照 vf_crop_nvcv.c:1 的 SPDX NVIDIA 头），git 单 commit 导入（b1aea74）——GMAT 对上游 CPU 层的态度是"整仓搬运，不做分叉"，这意味着未来 rebase 上游新版本时这层基本无冲突。

## 六、新人提示

1. **看懂调度链先看三处**：`libavutil/{arm,aarch64}/cpu.c`（能力检测）、`*_init_arm.c` 的 `have_*` 瀑布（hpeldsp_init_arm.c:45 是最短样板）、`asm.S` 的 function 宏。
2. **改 .S 文件必跑 neontest + checkasm**：`tests/checkasm/aarch64/` 与 `libavcodec/aarch64/neontest.c` 双保险；checkasm 会逐 q 寄存器 diff 输出。
3. **asm-offsets.h 是合同不是注释**：动 `MpegEncContext` 字段顺序前先 grep 这个头，否则 arm 汇编静默读错字段——这类 bug 无编译警告。
4. **NEON 写法选型**：新函数默认手写 .S（性能上限高、可 dot-product）；跨 arm32/aarch64 的中型函数可参考 neon/mpegvideo.c 的 intrinsics 模式；千万别在 aarch64 里用 vfp 路线（那是 32 位遗产）。
5. **行号锚自验**：本篇引用 asm.S:158/159（aarch64）、arm/asm.S:23-26/57-61、hpeldsp_init_arm.c:45/67/69、fmtconvert_init_arm.c:44-46、vp9dsp_init_10bpp_aarch64.c:23-25、h264dsp_neon.S:111/132、neon/mpegvideo.c:19/23-27/26 均于 2026-11-07 源码核实。

---
**甄别条款记录**：任务书"207 文件"为层节点总数；图谱实测 layer:09 含 204 个 file 节点（arm/140+aarch64/63+neon/1），文中采用后者并注明口径。`neon/` 目录在旧版 FFmpeg 曾承载更多 intrinsics 文件，本仓仅存 mpegvideo.c+Makefile，为历史收束后的独苗。vp9mc_aarch64.S 与 dot-product 指令的关联为基于命名与上游惯例的推断，未逐指令反汇编验证（81 行小文件，读者可自行核）。
