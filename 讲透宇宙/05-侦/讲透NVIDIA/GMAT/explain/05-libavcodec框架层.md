# 05 · libavcodec 框架层：编解码引擎骨架与硬件加速体系

## 角色定位

libavcodec 是 fork 的心脏（2283 文件占全仓一半），其中**框架层**（图谱 layer:05，102 文件）是服务全部数百个编解码器的公共骨架——注册、调度、数据结构、线程、硬件加速桥。它回答的问题与具体 codec 无关："一个编解码器如何被发现、被调用、被喂包吐帧、被甩到硬件上"。对 GMAT 而言这层尤其关键：NVDEC 是通过本层的 hwaccel 体系（nvdec.c 一族 11 文件）接入的，metrans 的 VidDec/NvDecLite 两条解码路径分别在 avcodec_send_packet（本层 decode.c）与 cuvid（旁路本层）两端消费同一个体系。102 文件构成上是"~50 核心骨架 + ~52 硬件加速桥"两半。

## 内部结构

**注册子系统**：allcodecs.c（966 行）声明全部编解码器 extern 符号（allcodecs.c:32-45 起），`codec_list[]` 在编译期由 configure 生成的 codec_list.c 填充（allcodecs.c:868-874，树上无此生成文件）；运行时查找是 av_codec_iterate 线性迭代（allcodecs.c:886），find_codec 按 codec_id 优先非 experimental（allcodecs.c:909-930），find_codec_by_name 供 `avcodec_find_decoder_by_name("h264_cuvid")` 这类调用（allcodecs.c:940-960）。编解码器的类型契约在 codec_internal.h：FFCodec 内嵌公开 AVCodec（codec_internal.h:116），cb_type 三比特区分六种回调形态（codec_internal.h:91-110：DECODE/DECODE_SUB/RECEIVE_FRAME/ENCODE/ENCODE_SUB/RECEIVE_PACKET）——5.1 版本把回调统一进 union 的重构刚落定。**主循环子系统**：decode.c（1637 行）——avcodec_send_packet（decode.c:576）入包，decode_receive_frame_internal（decode.c:523）驱动，decode_simple_internal（decode.c:277）是真正调 codec->cb 的内环，avcodec_receive_frame（decode.c:639）出帧；ff_get_buffer 分配输出帧（decode.c:1403）。encode.c（632 行）对称：send_frame（encode.c:357）/receive_packet（encode.c:390）。**数据结构子系统**：avpacket.c（647 行）引用计数包管理（av_packet_alloc 声明 packet.h:473）、codec_par.c 独立的流参数结构（AVCodecParameters，与 AVCodecContext 解耦是为了 libavformat 能不依赖完整编解码器描述流）、get_bits.h（858 行）/bytestream.h/golomb.c 位流读取三件（HevcParser 的 BitstreamReader 是它们的精神同源）。**杂务子系统**：options.c+options_table.h（AVOption 表驱动全部编码器参数）、profiles.c（codec profile 名字表）、version*.h 四件（ABI 版本门）、bsf.c（562 行位流过滤器框架，Demuxer.h:9 的 h264_mp4toannexb 消费者）、parser.c（289 行，分帧解析器）、pthread 三件（pthread_frame.c 1169 行帧级多线程）。

**硬件加速桥**是另一半 52 文件，按厂商/ API 分七族：nvdec 一族 11（nvdec.c 核心 762 行 + nvdec_h264/hevc/av1/vp8/vp9/mpeg12/mpeg4/mjpeg/vc1 逐 codec 适配）、dxva2 一族 8（Windows）、vdpau 一族 8、qsv 4（Intel）、mediacodec 6/v4l2_m2m 5（Android/Linux）、vaapi 2/videotoolbox 4（macOS）。统一协议是 AVHWAccel 结构（hwaccels.h 集中 extern，如 ff_h264_nvdec_hwaccel hwaccels.h:35）+ hwconfig.h 的四种接入方法宏（hwconfig.h:49-61：HW_DEVICE_CTX/HW_FRAMES_CTX/AD_HOC/INTERNAL）。

## 外部连接

**向上**（libavfilter/fftools）：avcodec.h 是全仓 fanIn 之王（图谱实测 768），avcodec_send/receive 的包/帧直接进滤镜图（metrans 的 AvFilt.h:33 消费 buffersrc 就是链上终端）。**向下**（codec 实现）：layer:06/07 的千余 codec 文件只实现 FFCodec 回调，buffer/packet/options/线程全由本层供给——decode.c:277 的内环调用、ff_get_buffer 的帧池、options_table 的参数。**横向**（其他 hw 体系）：hwaccel 选择发生在 decode.c:1009-1058——hw_config->hwaccel 匹配用户请求的 pix_fmt（decode.c:958-979），hwaccel_init 建立上下文（decode.c:1051-1058）；nvdec.c 的 ff_nvdec_decode_init（nvdec.c:331）在此被触发，CUVIDDECODECAPS 能力探测（nvdec.c:103-106）与 metrans 侧 AppNvDec.cpp:65-108 的探测表是同一 API 的两端。GMAT 增量在这层几乎为零（nvdec.c 等与上游一致），真正的 GPU 增量在 libavfilter/libswscale——这正说明 fork 的"寄生"策略。

## 数据流

一次硬解调用的框架层旅程：ffmpeg CLI 以 `-hwaccel cuda` 请求 → avcodec_open2 时 ff_hwaccel_get_hw_config 遍历 codec 的 hw_configs（decode.c:1009 附近），AV_PIX_FMT_CUDA 匹配 nvdec 适配器 → hwaccel_init（decode.c:1051）调 ff_nvdec_decode_init（nvdec.c:331），内部建 CUVID 解码器与 AVHWFramesContext 帧池 → 运行期 avcodec_send_packet（decode.c:576）入包 → decode_simple_internal（decode.c:277）取包给 h264 解码器的 start_frame 回调——但此时回调已被 nvdec_h264.c 改造为填充 CUVIDPICPARAMS（nvdec.c:641 的 pp 组装）→ 硬件解码后 ff_get_buffer（decode.c:1403）从帧池取 AV_PIX_FMT_CUDA 帧 → avcodec_receive_frame（decode.c:639）交出。软解路径同构，只是回调指向 C/SIMD 实现。metrans 的 NvDecLite 完全绕开此层直连 nvcuvid（NvDecLite.cpp:271），换来 crop/resize 直通硬件（NvDecLite.h:45-46）——两条路径是"标准 vs 极致"的活教材。

## 设计决策

①**send/receive 双泵模型**（5.0 引入，本树定型）：把"喂包"与"取帧"拆成两个非阻塞调用，取代古老的 decode2/video_recv_frame——调用方自然获得背压控制（metrans AvDec.h:34-51 的 while-EAGAIN 循环即标准用法）。②**cb_type 压缩进位域**（codec_internal.h:128）：用 3 比特枚举区分六回调形态而非六个函数指针，省内存且编译期强制单形态。③**codec_list 编译期生成**：configure 按 enabled 组件生成 codec_list.c，关闭编解码器不进表——查找 O(n) 但 n 受构建裁剪；代价是 configure 与 allfilters/allcodecs 三处必须同步登记（GMAT 加滤镜时正因如此要动 configure:3162）。④**hwaccel 做成 codec 的装饰而非子类**：AVHWAccel 挂在 FFCodec 的 hw_configs 列表（hwconfig.h 宏），同一 h264dec.c 可同时服务软解/nvdec/vaapi/dxva2——这是 NVDEC 能即插即用的结构原因。⑤**AVCodecParameters 与 AVCodecContext 分家**：流描述（codec_par.c）不携带执行状态，Demuxer 只需前者（Demuxer.h:8）——接口窄化降低耦合。

## 新人提示

阅读顺序建议 allcodecs.c 的 find_codec 段（909-960）→ decode.c 的 576-680（send/receive 协作）→ decode.c:1009-1060（hwaccel 匹配）→ codec_internal.h 全文（278 行，读透 FFCodec 就读懂了半层）。调试利器是 AV_LOG_TRACE + `-debug 1`；查注册表 `ffmpeg -decoders | grep cuvid` 能直接看到 codec_list 生成结果。两个易混点：hwaccel 与 cuvid 是**两条不同 NVDEC 通路**（前者 `h264 + -hwaccel cuda` 走本层 hwaccels.h:35 的适配器，后者 `h264_cuvid` 走 cuviddec.c 独立 codec，metrans NvDecLite 又是第三条）；AVCodecContext.get_buffer2 回调只影响软解帧池，硬解帧来自 AVHWFramesContext（decode.c:979）。改这层代码要过 ABI 版本检查（version_major.h），FFCodec 结构变更必须同步 bump。

---
*甄别条款：①任务书称本层"102 文件"，图谱 layer:05 实测 102 个 file 节点、构成=~50 骨架+~52 hwaccel 桥，本文按此展开；②decode.c:1009-1058 的 hw_config/hwaccel_init 锚自 grep 实测行号（1009/1020/1051/1057）；③"cb_type 六形态"依据 codec_internal.h:91-110 枚举原文；④nvdec 11 文件口径=nvdec.c/.h+9 个 nvdec_*.c 适配器（layer:05 清单实测）。字数不含空格。*
