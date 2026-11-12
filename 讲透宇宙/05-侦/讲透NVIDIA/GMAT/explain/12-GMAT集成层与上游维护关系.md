# 12 · metrans 之外的 GMAT 集成层——构建基座、周边库与上游维护关系

## 一、角色定位：三块拼图外围的"胶水层"

GMAT 仓根只有六个顶层条目：`metrans/`（GPU 转码 SDK，另篇专述）、`ffmpeg-gpu/`（GPU 增强版 FFmpeg）、`doc/`（GMAT 专属文档 6 篇）、`Dockerfile`、`README.md`、`LICENSE.md`。本篇覆盖图谱对其余部分的归层：layer:01 仓根与构建基座（6 节点）、layer:04 ffmpeg-gpu 构建配置（52 节点：configure/ffbuild/compat/MAINTAINERS/RELEASE 一族）、layer:16 周边库与测试残留（307 节点/291 文件：libavdevice 74、libswscale 70、libavutil 52、libswresample 40、libpostproc 9、各库 tests 目录与 tests/ref FATE 参考数据）。这层的角色是**集成与维系**：它不实现任何编解码功能，却决定 GMAT 能否被构建、复现、跟进上游——读懂这层即拿到 GMAT 与上游关系的完整地图。

## 二、内部结构：三段式

**仓根段**：README.md 开宗明义——"GPU toolkit on Multimedia, AI and Transcoding"，并交代身世：GMAT 由 ffmpeg-gpu-demo 升级而来，demo 管线（3DDFA/Pose 滤镜）保留在 ffmpeg-gpu-demo 分支。`doc/` 六篇：FFMPEG-GPU_User_Guide.md（80 行官方手册）、FFmpeg_GPU_Acceleration.md（104 行）、Filter_Implementation、Tensorrt_Filter、Pose_Filter、3DDFA_filter——后三篇讲 demo 分支滤镜，主分支只留文档。`.gitmodules` 声明唯一子模块 `ffmpeg-gpu/libavfilter/cnpy`。

**构建段**（layer:04）：`configure` 是心脏，GMAT 在上游 5.1.2 之上开了口子——`--enable-libtensorrt`（configure:278）、`--enable-cvcuda`（:340）、CUDA 编译路径一族，以及独有的 `--disable-ptx-compression`（:504 "don't compress CUDA PTX code even when possible"，:6506 与 zlib_gzip/gzip 依赖联动）。`ffbuild/` 是 GNU make 构建骨架；`compat/` 屏蔽平台差异（stdatomic 五种实现、w32dlfcn 等），其中 `compat/cuda/cuda_runtime.h` 与 `dynlink_loader.h` 是 CUDA 头兼容垫片。MAINTAINERS/RELEASE/RELEASE_NOTES 原封保留上游（RELEASE_NOTES 即 FFmpeg 5.1 "Riemann" LTS 原文）。

**周边库段**（layer:16）：五个卫星库——libavdevice（76 条目，采集/输出设备，avfoundation.m/audiotoolbox.m/decklink_*.cpp 的 Objective-C 与 C++ 混编是特色）；libswscale（70 文件，**含 GMAT 独有 cuda/ 子目录 6 文件**）；libswresample（40 文件，音频重采样，自带 x86/arm/aarch64 SIMD）；libpostproc（11 条目，最古老 GPL 遗产库）；以及 libavutil tests 家族（52 个）。`ffmpeg-gpu/tests/` 完整保留上游 FATE 基建：fate-run.sh/fate.sh、ref/ 参考输出（acodec/fate/lavf/lavf-fate/pixfmt 五类）、checkasm 差分测试。

## 三、外部连接：GMAT 与上游 FFmpeg 的维护关系（本篇核心）

钉版事实清单：**基线**——ffmpeg-gpu/RELEASE 标 5.1.2，RELEASE_NOTES 标 5.1 "Riemann" LTS；**导入方式**——GMAT 仓 git 历史仅一个 commit（b1aea74 "Add ffmpeg-gpu user guide"），上游历史被 squash，无法用 git 考古增量；**增量面**——经前几篇 + 本篇排查，GMAT 相对上游 5.1.2 的全部差异落在四处：①libavfilter 的 tensorrt/nvcv/cuda 滤镜群与 configure 接线（第 11 篇）；②libswscale 的 GPU 化——`swscale.h:95` `#define SWS_HWACCEL_CUDA 0x1000000` 这个新公开 flag、`utils.c:2100` `if (flags & SWS_HWACCEL_CUDA)` 分支、`ff_sws_init_swscale_cuda`（:2057）与 `cuda/swscale_cuda.c`（478 行）+ 三个 .cu kernel（947+371+48 行），对外即 README 说的 "libgpuscale"，用法保持 `sws_getContext(..., SWS_HWACCEL_CUDA, ...)` 与 CPU 版同构；③configure/ffbuild 的构建口子（上节）；④doc/ 与 Dockerfile。**零改动面**——libavcodec/libavformat/libavutil/libavdevice/libswresample/libpostproc 的全部源码 grep "NVIDIA" 零命中（六层 3000+ 文件原样继承），连 MAINTAINERS 上游维护者名单都没动。

GMAT 的维护姿态由此清晰：**不是 fork 分叉，而是"上游 LTS + 独占插件包"的薄增量模式**。好处是跟进上游 5.1.x 补丁时冲突面极小；代价是永锁 5.1 世代 API（ffmpeg 6/7 的 channel layout 重构、scheduler 拆分全被放弃），目标用户是"把 GMAT 抠出来嵌进自己管线"的集成者。

## 四、数据流：一次完整构建的依赖链

README 给的标准路径：NGC 容器（cuda:12.2.0-devel 或 tensorrt:23.07-py3，devel 标签必需——需要 NVCC 与头文件）→ 装 CV-CUDA deb → `./configure --disable-ptx-compression --enable-cvcuda --enable-libtensorrt ... --nvccflags='-gencode arch=compute_86,code=sm_86'` → make。configure 探测 CUDA/TensorRT/CV-CUDA/nv-codec-headers（Dockerfile 里有 `git clone FFmpeg/nv-codec-headers && make install`——NVDEC/NVENC 的头文件独立仓库，是 ffnvcodec 体系的正规依赖）后生成 config.h/config_components.h 与 demuxer_list 等静态注册表（第 10 篇），ffbuild 骨架按 library.mak 先编各 libav* 静态/动态库，链接出 ffmpeg_g 再 strip 成 ffmpeg（--disable-ptx-compression 的意义：默认 PTX 压缩省 fatbin 体积，但部分 CUDA 驱动对压缩 PTX 的 JIT 兼容性差，GMAT 让用户可关）。README 特别提醒 nvccflags 的 arch 必须匹配实卡，否则运行时报 "no kernel image available"——FFmpeg 不支持 PTX JIT 兜底，这是 GPU 集成层最常踩的坑。

**Dockerfile 的身份甄别**：它 FROM `nvcr.io/nvidia/pytorch` 并安装 onnxruntime 1.8.1、Eigen 3.4.0、Assimp、SDL2——这些是 demo 分支 3DDFA/Pose 滤镜的依赖（doc/3DDFA_filter.md 依赖清单逐项对应），主分支 tensorrt/cvcuda 路线并不需要。**Dockerfile 服务的是 demo 分支，主分支属残留**；cnpy 子模块同理（第 11 篇已证零代码引用）。集成者应以 README 的 NGC 容器为准。

## 五、设计决策

- **锁 LTS + 薄增量**：选 5.1.2 而非 master，工业用户要 API 稳定；增量全部做成 configure 可关的插件（不开 --enable-libtensorrt 时 GMAT≈上游）。
- **squash 导入换取仓库轻量**：squash 后克隆秒级；代价是丢失 blame 能力，考古增量只能靠 grep 版权头与选项名。
- **GPU 化 swscale 而非另立库**：SWS_HWACCEL_CUDA 复用 SwsContext API，老代码改一个 flag 即上 GPU——集成摩擦最小化，README "missing puzzle pieces" 哲学的落地。
- **FATE/checkasm 全量保留**：291 个周边文件里 tests 占近半，GMAT 接受上游完整质量基建。
- **文档双轨**：doc/ 留 demo 时代文档 + README 指向分支——用文档而非代码承载历史。

## 六、新人提示

1. **判断"这文件是上游的还是 GMAT 的"**：一手抓版权头（SPDX NVIDIA），二手抓 configure 选项名，三手抓 Makefile 的 OBJS-$(CONFIG_*) 行；三招覆盖 95% 场景。
2. **跟进上游安全补丁**：以 5.1 分支为基 diff 本仓，冲突只会出现在 libswscale/utils.c 与 swscale.h 的 CUDA 插桩点、libavfilter/Makefile 与 allfilters.c。
3. **构建最小化**：不要 Dockerfile 不要 cnpy：NGC cuda devel 容器 + nv-codec-headers + `./configure --enable-cuda-nvcc` 即可复现基础 GPU 支持。
4. **跑测试**：`make fate` 需下载 FATE 样本；轻量验证用 `make check`（checkasm）。
5. **行号锚自验**：configure:278/340/504/6506、swscale.h:95、utils.c:2054/2057/2100/2509、RELEASE（5.1.2）、RELEASE_NOTES（Riemann LTS）、git b1aea74、Dockerfile 依赖段均于 2026-11-07 源码核实；"ptx-compression 为 GMAT 引入"基于选项语义与上游 5.1 惯例推断（无上游 checkout 对照，置信度中）。

---
**甄别条款记录**：任务书"tests 残留"采信但扩充为"FATE 基建全量保留"（非残缺）。Dockerfile/cnpy 的"demo 分支残留"结论由依赖清单（doc/3DDFA_filter.md）与全仓 grep 零代码引用交叉实证。"squash 导入"由 git log 仅 1 commit 实证。libpostproc 条目数 11（含版本头与 .v 导出文件），layer:16 的 9 为 file 节点数，口径已在文中注明。GMAT 增量清单的完整性受"无上游对照 checkout"限制，方法为反向排除（全库 NVIDIA grep + configure/Makefile 选项扫描），若存在无版权头标记的隐性改动，该方法不可见——标注为方法学局限。
