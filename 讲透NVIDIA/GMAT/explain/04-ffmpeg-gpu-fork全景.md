# 04 · ffmpeg-gpu：fork 全景与构建体系

## 角色定位

ffmpeg-gpu/ 不是"NVIDIA 补丁集"而是**完整的 FFmpeg 全库 fork**：基线 5.1.2（ffmpeg-gpu/RELEASE），libavcodec 2283 文件、libavformat 648、libavfilter 736、libavutil 367、libswscale 78、fftools 14，合计约 4600 文件——与上游同版本树几乎逐文件一致，增量集中在 libavfilter 根目录、libswscale/cuda/、libavutil 像素格式三处。官方增量清单三项（doc/FFMPEG-GPU_User_Guide.md:3-6）：更多 GPU 滤镜、libgpuscale、CUDA Runtime API。它是 metrans 构建的前置依赖（README.md:84-88 需 `make install`），也是 README.md:13-16 所列五滤镜与 libgpuscale 的宿主。

## 内部结构

**增量一：五个新滤镜**。四个 CV-CUDA 系（crop/rotate/flip/smooth_nvcv）+ tensorrt。nvcv 系自带 SPDX/MIT 头（vf_rotate_nvcv.c:2-23），直接 include CV-CUDA 头（vf_rotate_nvcv.c:23-24 的 `nvcv/Tensor.h`+`cvcuda/OpRotate.h`），上下文结构持 NVCVOperatorHandle/NVCVTensorLayout 等 CV-CUDA 原生类型（vf_rotate_nvcv.c:44-59 的 RotateNvcvContext）；configure 侧以 `rotate_nvcv_filter_deps="cudart cvcuda"` 声明依赖（configure:3164-3167）。tensorrt 是复合体：vf_tensorrt.c（216 行）是滤镜外壳，tensorrt.cpp（648 行）是 C++ 引擎封装——IRuntime/deserializeCudaEngine 加载引擎（tensorrt.cpp:182-183）、enqueueV2 提交推理（tensorrt.cpp:295）、TrtLogger 实现 nvinfer1::ILogger（tensorrt.cpp:145）。**增量二：libgpuscale**。libswscale/cuda/ 五文件（swscale_cuda.c/rgb2rgb_cuda.c/yuv2rgb_cuda.cu/yuv2yuv_cuda.cu/datatypes.h），API 面新增 `SWS_HWACCEL_CUDA = 0x1000000`（ffmpeg-gpu/libswscale/swscale.h:95），getContext 检查该 flag（ffmpeg-gpu/libswscale/utils.c:2100），swscale 主分派在 ffmpeg-gpu/libswscale/swscale.c:1042 落到 CUDA 路径；实现直接用 CV-CUDA OpResize（ffmpeg-gpu/libswscale/cuda/swscale_cuda.c:11-12 include `nvcv/Tensor.h`+`cvcuda/OpResize.h`），支持格式清单 swscale_cuda.c:34 起（NV12/P010/YUV420P 系/YUV444 系）。构建挂 CONFIG_CVCUDA（libswscale/Makefile:24）。**增量三：CUDA Runtime**。configure 探测 CUDA Toolkit 后定义 CONFIG_CUDART，滤镜可用 `<<<>>>` 与 nvcc 编译 .cu（doc/FFMPEG-GPU_User_Guide.md:79），官方模板 libavfilter/vf_template_cuda.cpp。**外围增量**：新像素格式 AV_PIX_FMT_RGBPF32LE（ffmpeg-gpu/libavutil/pixfmt.h:315，别名宏 pixfmt.h:443，描述符 ffmpeg-gpu/libavutil/pixdesc.c:2289）——FP32 平面 RGB，专为 TensorRT NCHW 布局发明；format_cuda 滤镜负责 NV12↔RGBPF32 双向 kernel 转换（vf_format_cuda.c:193-204）；select_cuda 滤镜带 GPU scene 检测（vf_select_cuda.c:201 检查表达式含 "scene"，SAD kernel 在 scene_sad_cuda.cu）。全部滤镜经 allfilters.c 注册（scale_cuda :418、select_cuda :430、tensorrt :469、yadif_cuda :520、chromakey_cuda :198 等）。

## 外部连接

**对上游 FFmpeg**：fork 姿态是"寄生增量"——不碰公共 API 语义，只加文件与 configure 分支，rebase 上游成本最小化（git log 单提交压平）。**对 NVIDIA 生态**：依赖三件外部——nv-codec-headers（NVDEC/NVENC 头，doc/FFmpeg_GPU_Acceleration.md 要求先装）、CV-CUDA >= 0.3.0（README.md:34，v0.3.1-beta deb 安装 README.md:48-52）、TensorRT >= 8.2（README.md:33）；探测逻辑 configure:6533（`require libcvcuda nvcv/Version.h nvcvGetVersion`）与 configure:6647（`require_cpp libtensorrt NvInfer.h nvinfer1::Dims2`）——后者用 C++ 特性探测故走 require_cpp。libavfilter/cnpy 子模块（.gitmodules:2-3）供 3DDFA 滤镜读写 npz（doc/3DDFA_filter.md）。**对 metrans**：安装后以 -lavfilter 等链接（metrans/Makefile:13），VidFilt 构造的滤镜图里的 *_cuda 滤镜全部来自这里。

## 数据流

以官方 TensorRT 管线为例（doc/Tensorrt_Filter.md）："解码（NV12@GPU）→ scale_npp 1280:720 → format_cuda=rgbpf32le（NV12→FP32 平面 RGB kernel）→ tensorrt=<engine>（enqueueV2 推理，输入输出均显存）→ format_cuda=nv12 → h264_nvenc"——帧自始至终未离开 GPU，CPU 只做图调度。libgpuscale 同理：`sws_getContext(..., SWS_HWACCEL_CUDA, ...)`（doc/FFMPEG-GPU_User_Guide.md:39-41）后 sws_scale 的 src/dst 指针皆设备指针（ffmpeg-gpu/libswscale/utils.c:2100 init 检查、ffmpeg-gpu/libswscale/swscale.c:1042 分派）。nvcv 滤镜管线（FFMPEG-GPU_User_Guide.md:19）：`-hwaccel cuda -i in.mp4 -vf format=rgb24,hwupload_cuda,crop_nvcv=640:480,flip_nvcv=0,smooth_nvcv=gaussian -c:v hevc_nvenc`——注意四滤镜只吃 RGB（Guide 明示），故需先 format=rgb24 再 hwupload。三套数据流共享同一硬件帧池协议：AV_PIX_FMT_CUDA 格式的 AVFrame + AVHWFramesContext（doc/FFmpeg_GPU_Filter_Implementation.md 详述 cuCtxPushCurrent 纪律与 FF_FILTER_FLAG_HWFRAME_AWARE 标志）。

## 设计决策

①**为什么 fork 而不 upstream**：上游 FFmpeg 拒绝 CUDA Runtime 依赖（坚持 Driver API 免 Toolkit 安装，doc/FFMPEG-GPU_User_Guide.md:77 的论证），也难收 CV-CUDA/TensorRT 这类重依赖滤镜——fork 是唯一出路，代价是长期跟版负担（本树停在 5.1.2）。②**libgpuscale 复用 swscale API 而非新库**：`SWS_HWACCEL_CUDA` 只是 flag（swscale.h:95），调用方式与 CPU 完全一致——存量调用代码零改动即可上 GPU；但它依赖 CV-CUDA 的 OpResize，等于把缩放语义外包给另一个库。③**RGBPF32 发明像素格式**：TensorRT 要 NCHW FP32，FFmpeg 没有，就加一个（pixfmt.h:315）并配转换滤镜（vf_format_cuda.c）——为单一后端动基础库，典型的"以我为主"fork 决策。④**PTX JIT 不支持**（README.md:61）：nvccflags 必须显式 `-gencode`，arch 错则运行时 `no kernel image available`——构建期钉死 GPU 代际。⑤**--disable-ptx-compression**（README.md:57）：新 NVCC 下不显式禁用会构建失败。

## 新人提示

先分清"上游文件"与"增量文件"：libavcodec/h264dec.c 这类与上游一致不必精读，*_nvcv.c/tensorrt.*/swscale/cuda/ 才是 GMAT 血脉。文档拓扑：doc/FFMPEG-GPU_User_Guide.md（总览）→ FFmpeg_GPU_Acceleration.md（hwaccel 用法）→ FFmpeg_GPU_Filter_Implementation.md（写滤镜）→ Tensorrt_Filter.md（推理管线）。编译务必在 NGC 容器（README.md:40/43，tensorrt 滤镜选 tensorrt 镜像）；configure 失败先看 ffbuild/config.log（doc/Tensorrt_Filter.md 述）。验证滤镜注册：`ffmpeg -filters | grep -E "nvcv|tensorrt"`。坑：CV-CUDA 版本敏感（README.md:34 要求 >=0.3.0）；`--enable-nonfree`（TensorRT 必需）后产物不可再分发；L4/Ada 用 compute_89（README.md:61）。

---
*甄别条款：①"与上游 5.1.2 逐文件一致"为推断（无上游树逐字节 diff），实证口径=git log 单提交压平+增量文件清单（configure/allfilters/Makefile 三处登记）+doc 官方三增量声明；②libgpuscale 实现文件在 libswscale/cuda/ 且 CONFIG_CVCUDA 门控（Makefile:24 实证），README:15 称"libgpuscale"是文档名而非库名——链接产物仍叫 libswscale；③tensorrt.cpp:295 的 enqueueV2 是 TRT8 API（TRT10 已废弃），版本锚定与 configure:6647 的 require_cpp 一致。字数不含空格。*
