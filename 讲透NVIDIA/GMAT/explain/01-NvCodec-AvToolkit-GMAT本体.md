# 01 · metrans/include/NvCodec + AvToolkit：GMAT 的本体层

## 角色定位

metrans/include/ 是 MeTrans SDK 的全部核心（README.md:17-20 的三大能力全部落在这 32 个文件里）：`NvCodec/` 管 GPU 引擎（NVDEC/NVENC/NVJPEG/HEIF），`AvToolkit/` 管 FFmpeg 世界（容器/编解码/滤镜），两者在应用层拼成全 GPU 转码流水线。设计哲学与 GMAT 总定位（README.md:22"补缺拼图"）一致——不造抽象框架，只做**header-only 的薄封装**：AvToolkit 12 个头全部无 .cpp，NvCodec 仅 5 个 .cpp（NvDecLite.cpp 16.6KB、NvEncLiteUnbuffered.cpp 13.2KB 等实现文件 + vendored 官方头），加起来约 1.2 万行就把 CUDA Driver API 和 FFmpeg C API 两个"难缠对象"各包了一层可读的 C++ 皮。

## 内部结构

**NvCodec/ 20 文件分四组**。①解码：`NvDecLite`（NvDecLite.h:32）持有 CUvideoctxlock/CUvideoparser/CUvideodecoder 三句柄（NvDecLite.h:78-80），构造时把三个静态回调注册给 nvcuvid（NvDecLite.cpp:271-273 的 pfnSequenceCallback/pfnDecodePicture/pfnDisplayPicture），回调里再转回虚函数 HandleVideoSequence/HandlePictureDecode/HandlePictureDisplay（NvDecLite.h:62-68）——序列/解码/显示三阶段是 cuvid 的固有契约。帧管理用 vector 帧池 + mutex（NvDecLite.h:91-103），Decode() 返回帧指针数组（NvDecLite.cpp:350-367），DecodeLockFrame() 变体则把已取帧从池中移除、交给调用方 UnlockFrame 归还（NvDecLite.cpp:369-379）。②编码：`NvEncLite`（NvEncLite.h:22）继承 `NvEncLiteUnbuffered`（NvEncLiteUnbuffered.h:29，无输入缓冲队列的会话管理，含 EndEncode 冲刷与 Reconfigure 动态改参 NvEncLiteUnbuffered.h:37-38），派生类补 EncodeDeviceFrame/EncodeHostFrame 双入口（NvEncLite.h:26-27）与设备帧缓冲池（NvEncLite.h:43-45 的 vpDeviceFrame/vRegisteredResource/vDeviceInputBuffer）；编码参数解析独立在 `NvEncoderInitParam`（NvEncoderParam.h:27，572 行，把 `-codec h264 -preset p4` 这类命令行 token 解析成 GUID，NvEncoderParam.h:50-55）。③HEIF：NvHeifWriter/NvHeifReader 复用编码器产 HEVC 码流、解码器还原。④CUDA kernel：ColorSpace.cu（350 行 NV12/P016→BGRA/BGR planar/BGRA64 全套）、Resize.cu 与 Resize_bicubic.cu（各 160 行，内容逐字节相同仅插值核不同）、BitDepth.cu（37 行 uint8↔uint16）。

**AvToolkit/ 12 头是严格的类家族**：AvCommon.h 是地基——`ckav/cknn` 错误检查宏（AvCommon.h:18/34）+ `PitchToAlignment`（AvCommon.h:41-53，把 GPU pitch 反推成 FFmpeg 对齐参数，静态 map 缓存）；AvFilt 基类（AvFilt.h:19）管 AVFilterGraph/buffersrc/buffersink 生命周期与 Filter 循环（AvFilt.h:30-51，EAGAIN/EOF 驱动）；VidDec/AudDec 继承 AvDec（AvDec.h:17，avcodec_send_packet/receive_frame 标准 pumping，AvDec.h:34-51）；VidEnc（VidEnc.h:11）支持 `usePrimCuCtx` 时给 nvenc 挂 AV_HWDEVICE_TYPE_CUDA 设备上下文（VidEnc.h:28-35）；Demuxer（Demuxer.h:16）内置内存源 BufferDataProvider（Demuxer.h:18-55）与 AVBSF 过滤，Demux() 的契约是"EOF 后仍返回 size=0 的 packet 而非 NULL"（Demuxer.h:92-94 的中文注释，专为喂解码器设计）。

## 外部连接

向上：metrans/samples 全部 22 个示例与 app/ 六个应用都只 include 这两处（如 AppNvDec.cpp:16-18、AppNvTrans.cpp:16-19）。向下：NvCodec 链接驱动自带库（metrans/Makefile:14 的 `-l:libnvidia-encode.so.1 -l:libnvcuvid.so.1`），AvToolkit 链接 ffmpeg-gpu 安装产物（metrans/Makefile:13 的 -lavformat 等，metrans 构建前置是 `sudo make install` ffmpeg-gpu，README.md:84-88）。横向：VidFilt 依赖 libavutil/hwcontext_cuda.h（VidFilt.h:6），NvDecLite.h:111-126 的 `FFmpeg2NvCodecId()` 把 AVCodecID 映射成 cudaVideoCodec（MPEG1/2/4、VC1、H264、HEVC、VP8/VP9、JPEG 九种，NvDecLite.h:114-123），是两大世界互通的唯一桥——且用 `#if defined AVCODEC_AVCODEC_H` 条件编译，只有包含方先引了 avcodec.h 才编译（NvDecLite.h:111）。

## 数据流

核心是**零拷贝 GPU 帧的旅程**。NvDecLite 以 bUseDeviceFrame=true 构造时帧留在显存（NvDecLite.h:45），Decode 返回的 uint8_t* 实为 CUdeviceptr；进入滤镜链时不 memcpy，而是 VidFilt::Filter(pFrame, nPitch, ...) 一条龙（VidFilt.h:13-26）：`av_buffer_create(pFrame, GetFrameSize(), cudaBufferFree, ctx, 0)`（VidFilt.h:18）把这个裸指针包装成带引用计数的 AVBuffer——释放回调 cudaBufferFree 直调 `cuMemFree((CUdeviceptr)data)`（VidFilt.h:79，注意 71-81 行大量注释掉的 ctx push/pop，说明曾依赖调用方上下文）；随后 `av_image_fill_arrays` 以 pitch 反推的 alignment 填 data/linesize（VidFilt.h:22-23）。滤镜图侧，构造函数给 buffersrc 设 `par->hw_frames_ctx`（VidFilt.h:53-56），ParseFilter 再把 device_ref 注入图内**每个**滤镜的 hw_device_ctx（AvFilt.h:73-82），帧从而以 AV_PIX_FMT_CUDA 格式（VidFilt.h:41）在 *_cuda 滤镜间流转；buffersink 出来的帧可继续喂 NvEncLite::EncodeDeviceFrame（GPU 指针进 NVENC），或 VidEnc 走 nvenc 硬编路径。对照上游 Video Codec SDK 官方 demo 常年停留在"解码→下载→CPU 处理"，这层封装的价值就是把 FFmpeg 滤镜图变成 GPU 内存中的驻留管线。

## 设计决策

①**零拷贝靠"借用 AVBuffer"而非"扩展 AVFrame"**：不改 FFmpeg 结构体，用 av_buffer_create 挂外部释放函数，代价是 cudaBufferFree 里无法安全 push 上下文（VidFilt.h:75-81 注释保留的尝试），要求消费全程在同一 CUDA context。②**三回调→虚函数的转接**（NvDecLite.h:62-65）保住 C 回调世界与 C++ 继承世界兼容，子类只需覆写 Handle*。③**错误处理双轨**：FFmpeg 侧 ckav 记 ERROR 继续（AvCommon.h:9-18），CUDA/NVENC 侧 check 记 FATAL（NvCommon.h:27-43，NVENCSTATUS 有 25 项错误名全表 NvCommon.h:45-73）——宽容度差异反映两类 API 的容错文化。④**header-only 的代价**：AvToolkit 无编译单元带来 include 即用，但 AvCommon.h:40 的 `static std::map` 在多翻译单元下各自一份（线程安全靠只增不改）。⑤Resize.cu 与 Resize_bicubic.cu 文件级复制（两文件均 160 行 7527 字节）是最朴素的"改一处分叉"策略。

## 新人提示

阅读顺序：AvCommon.h（54 行）→ AvDec.h（56 行）→ AvFilt.h（99 行）→ VidFilt.h（84 行）→ NvDecLite.h（126 行）→ NvEncLite.h（46 行），全程不到 500 行。调试时记住三件事：帧 pitch 不等于宽（NvDecLite.h:51 GetFramePitch 按 10bit 加倍）；GetFrameSize 按 NV12 3/2 系数算（NvDecLite.h:53）；VidFilt 构造的 pix_fmts 约束在 bOutputNv12 分支（VidFilt.h:40-43），带 hw_frames_ctx 时输出格式是 CUDA 而非 NV12。跑通验证用 AppNvTrans（AppNvTrans.cpp:131 的 bUseDeviceFrame=true + 143-163 行位深转换分支），它是零拷贝链的最小可运行样本。注意 NvCommon.h:21-23 引 Logger.h 而 metrans/include/Logger.h 只是 simplelogger 的工厂转发，日志设施全在 NvCommon.h 的 simplelogger 命名空间。

---
*甄别条款：本文档口径以源码为准——任务书提示"VidFilt hwcontext_cuda 零拷贝 GPU 帧 cudaBufferFree"经核实锚定 VidFilt.h:18/69-82；AvToolkit 实为 12 头（非"12 个 header-only"表述全对：VidFilt/AvFilt 等确实 header-only，Demuxer/Muxer 亦无 .cpp）；NvCodec 含 4 个 .cpp 实现文件非纯头库。字数不含空格。*
