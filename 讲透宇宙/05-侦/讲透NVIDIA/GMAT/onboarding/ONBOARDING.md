# GMAT 仓库导览（ONBOARDING）

> 仓库：NVIDIA/GMAT @ b1aea7427929dc44c39935894e26c8bf55851f02 · 图谱 24261 节点 / 42011 边 / 16 层 / 16 步 tour（`.understand-anything/knowledge-graph.json`）
> 口径钉版：GMAT = **GPU toolkit on Multimedia, AI and Transcoding**（README.md:5），面向数据中心 GPU 的视频/图像处理与转码工具集，**不是**内存分析工具（同名词 GMAT 内存分析器与本仓库无关）。

## 1. 项目定位：一块"补缺拼图"而非全家桶

GMAT 前身是 ffmpeg-gpu-demo（README.md:9-10），2022 年重组后以新名发布，官方口径是"收集用户反馈中缺失的 GPU 视频处理工具"（README.md:10）。仓库由两大主体构成（README.md:13-21）：

- **ffmpeg-gpu**：完整的 FFmpeg 全库 fork（基线 **5.1.2**，见 ffmpeg-gpu/RELEASE），叠加 GPU 能力——crop/rotate/flip/smooth/tensorrt 滤镜、libgpuscale（GPU 版 libswscale）、CUDA Runtime API 支持；
- **MeTrans SDK**（metrans/）：GPU 转码工具集——NVDEC/NVENC/NVJPEG 工具与基准程序、智能解码（均匀抽帧+场景切换检测）、HEIF 图像编解码。

最要紧的定位声明在 README.md:22：GMAT **不**提供完整的 GPU 视频处理 API，目标是"solve the missing puzzle pieces"，与既有管线（如上游 FFmpeg、DALI、CV-CUDA）拼合使用，"carve out whatever you need"。理解这句话就能理解整个仓库形态：metrans 大量复用 FFmpeg C API 做 C++ 薄封装，ffmpeg-gpu 只在上游 5.1.2 上做增量而非重构。许可证为 MIT（README.md:98-100），但 ffmpeg-gpu 以 `--enable-nonfree` 构建时受 FFmpeg LGPL/GPL 约束。

## 2. 仓库拓扑与构建体系

顶层五项：`README.md`、`LICENSE.md`、`Dockerfile`、`doc/`（6 篇深度文档 + images）、`ffmpeg-gpu/`、`metrans/`（图谱 layer:01 仅 6 节点——构建基座极薄）。

**metrans 侧**是单 Makefile 工程（metrans/Makefile），三档目标（metrans/Makefile:32-34）：`essentials`（默认，不含 HEIF/GL）→ `all_but_gl`（+AppHeifDec/AppHeifEnc/AppExtractPerf）→ `all`（+AppNvDecGL）。链接产物四类（metrans/Makefile:28）：三个 ctypes 桥 so（CFrameExtractor.so/CHeif.so/CSwscale.so）+ libmetrans.so。链接行直接点名厂商库（metrans/Makefile:14）：`-l:libnvidia-encode.so.1 -l:libnvcuvid.so.1 -lnvjpeg`，说明 NVENC/NVDEC 走驱动自带库而非 Video Codec SDK 安装包。

**ffmpeg-gpu 侧**沿用上游 configure 体系，新增 GPU 开关：`--enable-libtensorrt`（configure:278）、`--enable-cvcuda`（configure:340），依赖映射在 configure:3162-3167（tensorrt_filter_deps/crop_nvcv_filter_deps 等），CV-CUDA 库探测在 configure:6533（`require libcvcuda nvcv/Version.h nvcvGetVersion`）。注意 configure:3830 把 `cvcuda_extralibs` 挂给了 swscale——libgpuscale 的构建寄生在 cvcuda 开关上。

**容器化**：Dockerfile:2 基于 `nvcr.io/nvidia/pytorch` 镜像（为 doc/3DDFA_filter.md 的 libtorch 滤镜服务），安装 onnxruntime/eigen/assimp 并写 EGL vendor JSON（Dockerfile:10）。ffmpeg-gpu/libavfilter/cnpy 是 git 子模块（.gitmodules:2-3，rogersce/cnpy，npz 读写，服务 tensorrt 滤镜元数据）。

## 3. metrans 本体：include/ 三支柱（图谱 layer:02，44 节点）

metrans/include/ 下三目录 + 根 Logger.h，共 42 文件、约 1.2 万行，是 SDK 的全部核心：

- **NvCodec/**（20 文件）：GPU 编解码引擎封装。`NvDecLite`（NvDecLite.h:32）精简包装 nvcuvid 的 parser/decoder 句柄，三个静态回调桥到虚函数（NvDecLite.h:62-65：序列/解码/显示）；`NvEncLite`（NvEncLite.h:22）继承 NvEncLiteUnbuffered 会话管理，暴露 EncodeDeviceFrame/EncodeHostFrame 双入口（NvEncLite.h:26-27）；`NvHeifWriter/NvHeifReader` 复用双引擎读写 HEIF；三个 .cu 提供 CUDA kernel——ColorSpace.cu（350 行 NV12↔BGRA 色彩转换）、Resize.cu/Resize_bicubic.cu（缩放）、BitDepth.cu（8↔10bit 深度转换）。vendored 头文件 nvEncodeAPI.h（3844 行）/cuviddec.h（1190 行）/nvcuvid.h（436 行）是 Video Codec SDK 官方头。
- **AvToolkit/**（12 文件，全 header-only）：FFmpeg C API 的 C++ 面向对象薄层。核心是 `VidFilt`（VidFilt.h:9）——把裸 GPU 指针包装成 AVFrame 送入滤镜图：`av_buffer_create(pFrame, size, cudaBufferFree, ctx, 0)`（VidFilt.h:18）挂自定义释放回调直调 `cuMemFree`（VidFilt.h:79），实现解码器输出到滤镜图的**零拷贝**；构造时给 buffersrc 设 `hw_frames_ctx`（VidFilt.h:53-56）并把 device_ref 注入全图每个滤镜（AvFilt.h:73-82）。其余：Demuxer（Demuxer.h:16，含内存 BufferDataProvider Demuxer.h:18-55）、Muxer、AvDec/VidDec/AudDec、AvEnc/VidEnc（VidEnc.h:28-35 支持 nvenc 主上下文）、AvFilt 基类。
- **HevcParser/**（10 文件）：纯 C++ HEVC 码流解析器，详见 explain 02。

## 4. metrans 应用生态（图谱 layer:03，49 节点）

三层结构：

- **samples/（22 个示例）**：FFmpeg 路径 11 个（AppMux/AppVidDec/AppVidEnc/AppVidFilt/AppVidTrans/AppAvTrans/AppAudDec/AppAudEnc/AppAudFilt/AppAudTrans/AppVidEncPerf）+ GPU 路径 9 个（AppNvDec/AppNvDecPerf/AppNvDecImageProvider/AppNvEnc/AppNvEncPerf/AppNvTrans/AppNvjpegDec/AppHeifDec/AppHeifEnc）+ OpenGL 目录 AppNvDecGL/。每个都是 <450 行的可独立编译样例，metrans/Makefile:36-60 显式列每个目标的依赖 .o。
- **app/（GMAT 门面）**：AppMeTrans/（AppMeTrans.cpp + TransData/TransDataConverter/FpsLimiter/RoundQueue 等流水线组件）是主转码程序；FrameExtractor.h（305 行）实现智能抽帧，其 VideoDemuxer 用**双 Demuxer 游标**（FrameExtractor.h:146 的 m_dm/m_dmSeek）做关键帧探测；AppNvDecScan.cpp:50 靠裸字节判断 H.264 非参考帧直接跳过（`nal_ref_idc==0 && nal_unit_type==1`）；AppSelect.cpp:102 走 `gt(scene,0.4)` 场景切换选择（注意甄别：FrameSelect.h:12 硬编码滤镜名 `select_gpu`，但 ffmpeg-gpu 中注册名是 `select_cuda`，见 vf_select_cuda.c:604，当前代码树上该串会解析失败，疑为跨版本遗留）。
- **python/（7 文件）**：ctypes 桥。frame_extractor.py:5 直接 `CDLL('../build/CFrameExtractor.so')`，暴露 `extract_to_device_buffer`（frame_extractor.py:52，目标指针是**设备显存指针**，抽帧结果零拷贝进 PyTorch/CV-CUDA 生态）；heif_format.py:8-19 声明 CHeif.so 的 NvHeifWriter/NvDecLite C 接口协议。

## 5. ffmpeg-gpu fork：对上游 FFmpeg 5.1.2 的增量定位

fork 全景约 4600 文件（libavcodec 2283/libavformat 648/libavfilter 736/libavutil 367/libswscale 78/fftools 14），其中**绝大多数文件与上游 5.1.2 完全一致**，增量集中在五处（详见 explain 04）：

1. **五个新滤镜**：crop/rotate/flip/smooth_nvcv（基于 CV-CUDA 库，如 vf_rotate_nvcv.c:23-24 直接 include `nvcv/Tensor.h`+`cvcuda/OpRotate.h`）+ tensorrt（vf_tensorrt.c/tensorrt.cpp）。
2. **libgpuscale**：libswscale/cuda/ 目录五个文件（swscale_cuda.c 等），新 API flag `SWS_HWACCEL_CUDA`（ffmpeg-gpu/libswscale/swscale.h:95），入口分派在 ffmpeg-gpu/libswscale/swscale.c:1042，构建挂 CONFIG_CVCUDA（libswscale/Makefile:24）。
3. **CUDA Runtime API**：CONFIG_CUDART 探测（doc/FFMPEG-GPU_User_Guide.md:79），滤镜可写 `<<<>>>` kernel，模板 vf_template_cuda.cpp。
4. **新像素格式 RGBPF32**（FP32 planar RGB，TensorRT NCHW 需要）：ffmpeg-gpu/libavutil/pixfmt.h:315 + ffmpeg-gpu/libavutil/pixdesc.c:2289 + format_cuda 转换滤镜。
5. **cuda 滤镜家族扩充**：select_cuda（含 scene 检测，vf_select_cuda.c:201 检测表达式含 "scene"）、scene_sad_cuda.cu、chromakey_cuda、hwupload_cuda 等，注册表 allfilters.c:198-520。

## 6. libavcodec 六层解剖（图谱 layer:05-11，合计 2256 节点）

图谱把 libavcodec 拆成六层，是仓库最大的分析单元：

- **框架核心**（layer:05，102 节点）：编解码器注册与主循环。allcodecs.c:868-874 的 `codec_list[]` 编译期生成（codec_list.c 不在树上，由 configure 生成后 include）；查找走 av_codec_iterate 线性扫（allcodecs.c:909-937）。解码主循环 decode.c：avcodec_send_packet（decode.c:576）→ decode_receive_frame_internal（decode.c:523）→ decode_simple_internal（decode.c:277）；编码对称（encode.c:357/390）。FFCodec 内部结构（codec_internal.h:112）以 cb_type 区分六种回调形态（codec_internal.h:91-110）。
- **视频编解码群**（layer:06，1168 节点）：根目录主体。家族规模实测（.c+.h 口径）：h264* 46、aac* 51、dca* 30、hevc* 24、vp9* 23、opus* 21、mpeg4* 11、av1* 9。入口锚：ffmpeg-gpu/libavcodec/h264dec.c:1069（ff_h264_decoder）、ffmpeg-gpu/libavcodec/hevcdec.c:3870、ffmpeg-gpu/libavcodec/av1dec.c:1248、libx264.c:1219（外库 wrapper 代表）。
- **音频编解码群**（layer:07，360 节点）：ffmpeg-gpu/libavcodec/aacdec.c:555/aacenc.c:1142、dcadec.c:413、opusdec.c:707/opusenc.c:728，fft/mdct/sinewin 共享 DSP。
- **SIMD 四军**（layer:08-11）：x86 198 节点（SSE2/AVX2/AVX-512，x86util.asm 公共宏）、ARM 系 207（arm/ 传统 NEON + aarch64/ 64 位 + neon/ 公共宏，Jetson 宿主）、MIPS 120（MMI/MSA 龙芯）、其余 101（loongarch LSX/LASX、ppc AltiVec、alpha 遗存）。init+asm 成对出现是统一模式。

## 7. 外围库与 CLI（图谱 layer:12-16）

- **libavformat**（layer:12，637 节点）：容器世界。metrans 的 Demuxer/Muxer 最终落到 avformat.h API（Demuxer.h:6）。
- **libavfilter**（layer:13，721 节点）：GMAT 与上游的最大交点层——滤镜图引擎（buffersrc/buffersink，AvFilt.h:33-47 消费）+ 全部 *_cuda/tensorrt 滤镜 + dnn/ 推理后端目录。
- **fftools**（layer:14，65 节点）：ffmpeg.c CLI 状态机、ffplay/ffprobe；GPU 开关最终在这里暴露。
- **libavutil**（layer:15，313 节点）：AVFrame/AVBuffer 引用计数（VidFilt 零拷贝的 av_buffer_create 即此层 API）、hwcontext_cuda.c（CUDA 设备/帧池管理）、pixfmt/pixdesc 色彩系统、opt.h AVOption（fanIn 790，全图最高）。
- **周边**（layer:16，307 节点）：libswscale（含 cuda/ 子目录）、libswresample、libavdevice、libpostproc 及测试残留。

## 8. 新人上手路线

**按图谱 16 步 tour 对应**：tour1-5 是 GMAT 定位与 metrans 全链（README → NvCodec → AvToolkit → HevcParser → 应用层），tour6 是 fork 构建全景，tour7-11 是 libavcodec 六层，tour12-16 是外围库收尾。新人建议顺序与之同构，具体四步：

1. **编译跑通**（README.md:38-59）：NGC CUDA 12.2 devel 容器内 `./configure --disable-ptx-compression --enable-cuda-nvcc ... --nvccflags='-gencode arch=compute_86,code=sm_86 ...'`；**坑**：nvccflags 的 arch 必须匹配 GPU（README.md:61 明示 FFmpeg 不支持 PTX JIT，arch 错则运行时报 `no kernel image available`）；L4/Ada 要 compute_89。metrans 需先 `make install` ffmpeg-gpu（README.md:84-93）。
2. **从 AppNvDec.cpp（230 行）读起**：36-63 行的 DecodeFile 是"Demuxer→NvDecLite→写文件"最小闭环；65-108 行 ShowDecoderCapability 展示 cuvidGetDecoderCaps 能力探测表（11 种 codec×位深组合）。
3. **进阶零拷贝链**：VidFilt.h:13-26 的 Filter(pFrame, nPitch, ...) 看 GPU 指针如何变成 AVFrame；再读 AppNvTrans.cpp:129-182 的"解码→位深转换 kernel→编码"全 GPU 转码；最后 AppMeTrans/ 流水线与 FrameExtractor.h 双游标抽帧。
4. **fork 侧按需索引**：写 GPU 滤镜先读 doc/FFmpeg_GPU_Filter_Implementation.md（HW flag `FF_FILTER_FLAG_HWFRAME_AWARE`、cuCtxPushCurrent 纪律）+ vf_template_cuda.cpp；用 TensorRT 读 doc/Tensorrt_Filter.md（pipeline：scale_npp→format_cuda=rgbpf32le→tensorrt→format_cuda=nv12）；用 libgpuscale 读 doc/FFMPEG-GPU_User_Guide.md:32-46（sws_getContext 传 SWS_HWACCEL_CUDA）。

**常见坑速查**：AppNvDecGL 必须本地图形环境（README.md:96，远程 DISPLAY 配置棘手）；HEIF 功能需先装 nokiatech/heif（README.md:69-78）且用 `make all_but_gl`；`--disable-ptx-compression` 在较新 NVCC 上必加；GMAT 仓库 MIT 但 ffmpeg-gpu 默认构建引入 LGPL 组件、`--enable-nonfree` 后不可再分发；metrans python 桥的 so 路径写死 `../build/`（frame_extractor.py:5），跨目录使用需改。

---

*写作口径：字数不含空格；锚点全部源码核实（Read/Grep 于 2026-11-07，仓库 commit b1aea74），全文裸 `README.md:N` 一律指仓库根 README.md。甄别条款：任务书原文称 explain 02 主题为"传输库核心"，实读该目录为码流解析库（BitstreamReader/HevcUtils），无"传输"（transport）语义组件，按源码实际语义写作；任务书将 aac/dca/opus 计入"视频编解码器巨群"，经图谱实测三族属 layer:07 音频群（layer:06=1166 file 节点，以视频+字幕为主），已在 explain 06 声明口径；FrameSelect.h:12 的 `select_gpu` 与 fork 注册名 `select_cuda`（vf_select_cuda.c:604）不匹配已在上文标注。锚点终验 0 坏（58 锚全过存在性+行界检查）。*
