# 11 · libavfilter 滤镜群与 fftools 四工具——GPU 增量的主战场

## 一、角色定位：全库最大层 + GMAT 差异化所在

layer:13（libavfilter 滤镜层）721 节点/716 文件是 GMAT 全库最大层，内部构成：根目录视频滤镜 `vf_*` 307 个、音频 `af_*` 97 个、源滤镜 14 个、buffersrc/sink 桥 4 个，外加五个硬件子目录——`x86/` 76（滤镜自己的 SIMD，注意 libavfilter 有独立 SIMD 不靠 libavcodec）、`dnn/` 33（推理后端）、`opencl/` 14 个 `.cl` kernel、`cuda/` 3、`metal/` 3、`aarch64/` 2。加上 layer:14 的 fftools 与 tools 65 文件，本篇覆盖的正是 **GMAT 相对上游 FFmpeg 的几乎全部增量**：configure 里 `--enable-libtensorrt`（configure:278）与 `--enable-cvcuda`（:340）两个开关所点亮的滤镜，全部注册在 `allfilters.c` 的 545 个 extern 之中。

先甄别任务书一处口径：**"ffmpeg_g" 不是源码文件而是链接产物**——ffbuild 先链接未 strip 的 `ffmpeg_g`，再脱符号生成 `ffmpeg` 可执行文件；源码层面四工具是 `fftools/ffmpeg.c`（4579 行）、`ffprobe.c`（4175 行）、`ffplay.c`（3758 行）加共享的 `cmdutils.c`（1018 行）、`opt_common.c` 等。

## 二、内部结构：滤镜契约与图引擎

每个滤镜是一个 `const AVFilter` 结构（`avfilter.h:171` typedef），契约比 demuxer 更重：`preinit`（:254，分配前检查参数）、`init/uninit`（:302 保证 init 失败也调 uninit）、`query_formats`（格式协商）。注册表 `allfilters.c` 收 545 个 extern，NVIDIA 血统七员大将的注册行：crop_nvcv（allfilters.c:224）、flip_nvcv（:278）、hwupload_cuda（:314）、rotate_nvcv（:415）、scale_cuda（:418）、smooth_nvcv（:454）、tensorrt（:469）。

图引擎三件套：`avfiltergraph.c`（1352 行）管生命周期——`avfilter_graph_alloc`（:82）、`avfilter_graph_alloc_filter`（:165）、`avfilter_graph_config`（:1166，格式协商+缓冲分配的终审）；`graphparser.c:549` 的 `avfilter_graph_parse_ptr` 把 `-vf "format=rgb24,hwupload_cuda,crop_nvcv=640:480"` 解析成链；`formats.c`（947 行）做像素格式自动协商。数据面走 `buffersrc`→链→`buffersink` 帧队列。

**dnn/ 子目录是滤镜库内嵌的推理引擎**：`dnn_interface.c:32` `ff_get_dnn_module` 三路 switch——`DNN_NATIVE`（:41-47，纯 C 自研算子，卷积/池化/数学层在 dnn_backend_native_layer_*.c 十余个文件）、`DNN_TF`（:48-58，`#if CONFIG_LIBTENSORFLOW` 编译期门控）、`DNN_OV`（:60-70，OpenVINO 门控），服务 vf_dnn_processing/vf_sr 一族推理滤镜。

## 三、外部连接：GMAT 的三条 GPU 插槽

**插槽一：CV-CUDA 滤镜四件套。** `vf_crop_nvcv.c`（333 行）的头部就是架构说明：`#include <nvcv/Tensor.h>` 与 `#include <cvcuda/OpCustomCrop.h>`（vf_crop_nvcv.c:26-27）——滤镜壳直接消费 CV-CUDA 算子库的 Tensor 抽象，AVFrame 的 GPU 指针包成 nvcv::Tensor 调一个 Op 完事。四件套依赖声明在 configure:3164-3167（`rotate_nvcv_filter_deps="cudart cvcuda"` 一族），文档明言只接受 RGB 输入（`doc/FFMPEG-GPU_User_Guide.md`），典型链 `format=rgb24,hwupload_cuda,crop_nvcv=...,smooth_nvcv=gaussian -c:v hevc_nvenc`。

**插槽二：TensorRT 滤镜。** 双文件结构是全仓唯一 C++ 混编样板：`vf_tensorrt.c`（216 行，C 壳，SPDX NVIDIA MIT 版权 :2-3）+ `tensorrt.cpp`（648 行，C++ 实现体）。configure 的接线三处：Makefile:495 `OBJS-$(CONFIG_TENSORRT_FILTER) += vf_tensorrt.o tensorrt.o`、configure:3162 `tensorrt_filter_deps="libtensorrt cudart"`、:6647 `enabled libtensorrt && require_cpp libtensorrt NvInfer.h nvinfer1::Dims2 -lnvinfer -lnvonnxparser -lcudart`——`require_cpp` 断言 C++ 编译器可用，这是 ffmpeg 主 build 强制 C 环境下开 C++ 天窗的正规姿势。

**插槽三：CUDA 原生滤镜群。** `vf_scale_cuda.c`（645 行，:2 版权行 "Copyright (c) 2017, NVIDIA"——上游 FFmpeg 本就有，GMAT 继承而非新增）配 `.cu` kernel；GMAT 私有的是 `scene_sad_cuda.cu`（76 行，场景切换 SAD 的 GPU 版，服务 metrans 智能解码）与 `format_cuda_kernel.cu`（632 行，GPU 色彩空间转换核函数）。`cuda/` 子目录的 `load_helper.c/vector_helpers.cuh` 是共享的 CUDA 模块加载助手。

## 四、数据流：从命令行到帧循环

用户命令进入 `fftools/ffmpeg.c:4516` `main()` → `ffmpeg_opt.c`（4038 行）解析选项 → `ffmpeg_filter.c` 调 `avfilter_graph_parse_ptr` 建图 → `transcode_init()`（ffmpeg.c:3276）初始化编解码与 hwaccel → 主循环 `transcode()`（:4327）反复 `transcode_step()`（:4237）：demux 出包 → 解码 → 滤镜图（`transcode_from_filter` :4191 等待输入）→ 编码 → `ffmpeg_mux.c` 写容器。注意 5.1 世代还没有 7.x 的 scheduler 抽象（grep SchFilter/sch_ 零命中），4579 行单文件老式循环——GMAT 锁版 5.1.2 的代价之一。`ffprobe.c:4023` 与 `ffplay.c:3658` 的 main 复用同一套 cmdutils 选项表；ffplay 深度绑定 SDL（ffplay.c:60 `SDL_thread.h`），是 GPU 工具链唯一交互式组件。

滤镜内部一帧的路径（以 crop_nvcv 为例）：filter_frame 回调收到 hwupload_cuda 产出的 CUDA 帧 → 壳层校验 hw_frames_ctx → nvcv Tensor 包装 → cvcuda 算子执行 → 新帧返回下游。GPU 帧全程不落系统内存，这是与 CPU 滤镜链（x86 SIMD 军）的本质分界。

## 五、设计决策

- **滤镜 SIMD 独立成军**：libavfilter/x86 76 文件说明滤镜算子（卷积、混合、模糊）与编解码 DSP 是两套性能工程，各维护常量与模板。
- **多 GPU 后端并存而非抽象层**：opencl 14 个 `.cl` + metal 3 + CUDA 系——"每种 GPU 一套滤镜"的代价是功能矩阵碎片化，这正是 GMAT README "解决缺失拼图"定位的技术根源。
- **dnn 后端编译期门控**：CONFIG_LIBTENSORFLOW/CONFIG_LIBOPENVINO（dnn_interface.c:50/62）按链接环境裁剪，与 SIMD 的运行时 CPUID 检测形成对照——GPU 生态 ABI 不稳，编译期决策更稳。
- **cnpy 子模块孤儿状态**：`.gitmodules` 声明 `libavfilter/cnpy`，全仓 C/C++ 零引用，唯一消费者是 `doc/3DDFA_filter.md`——demo 分支遗留的死指针。

## 六、新人提示

1. **找 GMAT 与上游的 diff**：`grep -L "NVIDIA" ffmpeg-gpu/libavfilter/*.c` 反向筛 + configure 里 cvcuda/tensorrt 关键词；全部增量 20 文件以内。
2. **写 GPU 滤镜的模板选择**：轻量算子抄 vf_crop_nvcv.c；自研 kernel 抄 vf_scale_cuda.c + .cu 双文件模式；C++ 推理框架集成抄 vf_tensorrt.c + tensorrt.cpp 的 require_cpp 模式。
3. **图协商失败九成在 query_formats**：nvcv 系只要 RGB，链里漏 format= 转换直接失败——先 `ffmpeg -h filter=smooth_nvcv` 看格式约束。
4. **读 ffmpeg.c 的路线**：main(:4516) → transcode_init(:3276) → transcode_step(:4237)。
5. **行号锚自验**：allfilters.c:224/278/314/415/418/454/469、avfilter.h:171/254/302、avfiltergraph.c:82/165/1166、graphparser.c:549、dnn_interface.c:32/41/50/62、vf_crop_nvcv.c:26-27、vf_tensorrt.c:2-3、vf_scale_cuda.c:2、configure:278/340/3162/3164-3167/6647、Makefile:495、ffmpeg.c:3276/4191/4237/4327/4516、ffprobe.c:4023、ffplay.c:60/3658 均于 2026-11-07 源码核实。

---
**甄别条款记录**：任务书"ffmpeg_g"经核为构建中间产物（ffbuild 链接 ffmpeg_g 后 strip 得 ffmpeg），源码文件仅 ffmpeg.c，文中按源码口径修正。vf_ 前缀文件 307 个为含 .cu/.cpp/.asm 全扩展名计数（纯 .c 为 283）。cnpy 零代码引用结论基于全仓 grep（--include 覆盖 c/cpp/h/md/Makefile/txt），唯一命中 doc/3DDFA_filter.md；3DDFA/Pose 滤镜源码经 ls 确认不在主分支（doc 明言属 ffmpeg-gpu-demo 分支），Dockerfile 的 onnxruntime/eigen/assimp/SDL2 依赖是为该分支服务的主分支残留。
