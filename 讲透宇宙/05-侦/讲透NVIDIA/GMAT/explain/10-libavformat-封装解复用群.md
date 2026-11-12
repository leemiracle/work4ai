# 10 · libavformat 封装/解复用群——635 个文件的 I/O 集装箱码头

## 一、角色定位：GPU 转码管线的首尾两端

图谱 layer:12（libavformat 封装层）637 节点/635 文件，是 GMAT 全库第二大层——仅次于 libavfilter。它的职责一句话说清：**把字节流变成带时间戳的包（解复用），把包变回字节流（复用）**。对 GMAT 而言这层的意义是"码头"：任何 GPU 转码作业，输入侧是 libavformat 从 MP4/HLS/RTMP 里把压缩帧搬出来交给 NVDEC，输出侧是它把 NVENC 产出的 H.264/HEVC 码流按容器规范写回去。GPU 再快，容器的解析与封装仍百分百在 CPU——这层的质量直接决定吞吐上限之前的第一公里与最后一公里。

必须先钉一个口径：**GMAT 在这层零增量**。全目录 grep "NVIDIA" 零命中（对照 libavfilter 里 vf_crop_nvcv.c:1-2 的 SPDX NVIDIA 版权头），341 个 demuxer、175 个 muxer、全部协议栈原封继承上游 FFmpeg 5.1.2（ffmpeg-gpu/RELEASE）。任务书给的"360 文件"与图谱实测 635 不符，采信图谱口径。

## 二、内部结构：三层栈与编译期静态注册

libavformat 的 638 个目录条目分三个清晰层次：

**顶层：demux/mux 引擎。** `demux.c`（2979 行）承载 `avformat_open_input`（demux.c:220）→ `avformat_find_stream_info`（:2415）→ `av_read_frame`（:1438）→ 内部 `read_frame_internal`（:1233）的解复用主循环；`mux.c`（1448 行）是对称的复用引擎；`utils.c`（604 行）只剩公共杂项——5.1 版把 God-object 拆成 demux/mux 两文件正是社区"巨型文件手术"的成果。`avformat.h`（2907 行）定义核心句柄 `typedef struct AVFormatContext`（avformat.h:1215）。

**中层：容器格式插件。** 每个容器一对文件（dec+enc）：MP4 系 `mov.c` 9065 行/`movenc.c` 7947 行（全库最大双巨头，QT/MOV/MP4/3GP 全家桶）、Matroska `matroskadec.c` 4451/`matroskaenc.c` 3402、MXF `mxfdec.c` 4217/`mxfenc.c` 3310、广播流 `mpegts.c` 3450、流媒体 `hlsenc.c` 3194/`dashenc.c` 2433/`dashdec.c` 2379。加协议层 `rtmpproto.c` 3159、`rtsp.c` 2656。

**底层：AVIO 与协议。** `aviobuf.c`（1600 行）实现带缓冲的字节流抽象 AVIOContext，`avio.c`/`avio.h`（842 行头）定义对外 API；更底下是 URLProtocol 协议族（file/http/tcp/ftp/crypto…，注册表在 `protocols.c:24-33` 起的 extern 声明）。

**注册机制是本库最值得学的工程设计**：FFmpeg 5.x 已彻底废除运行时 `av_register_all()`，改为**编译期生成静态数组**——`configure:7920-7921` 的 `print_enabled_components` 按 configure 开关生成 `demuxer_list.c`/`muxer_list.c`（源码树里不存在，构建时产出），`allformats.c:547-548` 直接 `#include` 这两个生成文件，然后 `av_demuxer_iterate`（allformats.c:573 起）遍历静态 `demuxer_list[]` 数组，设备类格式经 `avpriv_register_devices` 原子指针续接在数组尾部。configure 关掉一个 demuxer，二进制里连代码带符号一起消失——零运行时开销的可裁剪设计。

## 三、外部连接：五件套插件契约

每个 demuxer是一个 `const AVInputFormat` 结构体，契约精简到五个函数指针。最简样板 `ac3dec.c:107` `const AVInputFormat ff_ac3_demuxer`：`.read_probe = ac3_probe`（给缓冲头猜格式）、`.read_header = ff_raw_audio_read_header`、`.read_packet = ff_raw_read_partial_packet`（复用 raw 家族通用实现）、`.flags = AVFMT_GENERIC_INDEX`、`.raw_codec_id = AV_CODEC_ID_AC3`——裸 AC-3 文件连解析都是共享代码。复杂端的样板是 `mpegts.c:3427` `ff_mpegts_demuxer`：`.read_header = mpegts_read_header`（mpegts.c:3098，负责 PAT/PMT 建流）、`.read_packet = mpegts_read_packet`（:3248，188/192 字节 TS 包循环 + PES 重组）。

对上游（fftools/用户）暴露的是 AVFormatContext + avformat_open_input 一族；对下游（libavcodec）交付 AVPacket；与 libavcodec 的另一接口是 `demux.c` 头部的 `libavcodec/bsf.h` 引入（demux.c:31）——码流过滤器（如提取前的 dump_extradata）挂在 demux 侧。设备插件（libavdevice）通过 avpriv_register_devices 挂进来，实现"摄像头/采集卡也是输入格式"的扩展。

## 四、数据流：一次转码作业的 I/O 全程

以 `ffmpeg -i input.mp4 ... output.mp4` 为例：`avformat_open_input`（demux.c:220）先经 avio_open 打开 URLProtocol，AVIOContext 由 `fill_buffer`（aviobuf.c:540）从协议层拉数据填充，然后逐个 demuxer 的 read_probe 探测（或按扩展名），选中 mov demuxer 后 read_header 解析 moov 建立 AVStream 数组；`avformat_find_stream_info`（demux.c:2415）预读若干包探测 codec 参数；主循环 `av_read_frame`（demux.c:1438）每次产出一个 AVPacket（内部 read_frame_internal :1233 处理时间戳 wrap——`wrap_timestamp`（demux.c:50）等辅助函数在此）。包交给 NVDEC 解码 → GPU 滤镜 → NVENC 编码，输出的包进 movenc 的交织队列，按 `mdat` 偏移写回 AVIOContext。吞吐敏感点全在 AVIO：`avio_read`（aviobuf.c:641）与 `avio_read_partial`（:713）是 demuxer 拉数据的两个入口，前者跨缓冲边界保证读满、后者允许短读——解析器选错入口就是性能杀手。

## 五、设计决策

- **probe 优先、扩展名兜底**：格式识别靠 read_probe 打分（0-100），这是对"文件名会骗人"的防御；代价是 avformat_find_stream_info 的预读启发式常年是黑盒延迟来源。
- **静态注册替换动态注册**：上面已述，5.x 的这次手术同时消灭了初始化顺序 bug 与线程安全隐患（avpriv_register_devices 用 `atomic_load_explicit` 保设备热插拔场景）。
- **raw 家族共享代码**：ac3/eac3/dts/mp3 等裸流 demuxer 共用 ff_raw_read_partial_packet，`priv_data_size = sizeof(FFRawDemuxerContext)`（ac3dec.c:115）模式让十几个格式各只剩几十行壳——与 libavcodec 的 DSP 契约同构：**框架吃掉共性，插件只写个性**。
- **巨型容器文件的底线**：mov.c 9065 行没有被拆解，因为 MP4 box 语义是一个不可分的状态机——对比 demux/mux 的拆分成功，说明"按职责拆"与"按格式拆"是两回事，后者会把共享的 box 解析撕碎。
- **流媒体协议群是隐藏的第二个子系统**：HLS（hls.c demux + hlsenc.c）、DASH 双向、RTMP/RTSP，这些协议文件加起来近万行，实质是"网络状态机 + 容器解析"的复合体，也是 GMAT 数据中心场景（拉流推流转码）真正会压测的部分。

## 六、新人提示

1. **加新格式的路径**：写 `xxx.c` 含 probe/header/packet 三函数 + `FFMIN_ff_xxx_demuxer` 结构 → Makefile 注册 OBJS → configure 的 DEMUXER_LIST 加名 → 重跑 configure 生成 demuxer_list.c。忘记第三步时函数存在但永不被发现。
2. **调 I/O 性能先看两个缓冲**：AVIOContext 的 buffer_size（ffio_init_context 可调）与 demuxer 内部的探针缓冲；GMAT GPU 管线里常见病是 4K 码流用默认 32KB 缓冲导致协议层 syscall 风暴。
3. **时间戳问题九成在 demux.c**：wrap_timestamp（demux.c:50）与 read_frame_internal（:1233）的组合决定 pts/dts 语义；容器格式只提供原始值，规范化都在引擎层。
4. **读码顺序建议**：avformat.h 的 AVFormatContext/AVStream 注释 → demux.c:220 avformat_open_input 逐行 → ac3dec.c 全文（20 分钟读完的最小 demuxer）→ mpegts.c:3098（真实复杂度）。
5. **行号锚自验**：allformats.c:547-548/573、configure:7920-7921、ac3dec.c:107-116、mpegts.c:273/3098/3248/3427/3432、demux.c:31/50/220/1233/1438/2415、aviobuf.c:540/641/713、avio.h:1215 引用（AVFormatContext 实为 avformat.h:1215）、avformat.h:1215、protocols.c:24-33 均于 2026-11-07 源码核实；341/175 计数来自 allformats.c extern 行实测 grep。

---
**甄别条款记录**：任务书"360→该层文件"与图谱 layer:12 的 635 file 节点（637 层节点）显著不符，本文采信图谱并逐项复核（目录 ls 实测 638 条目含 Makefile/tests 等 4 个非源文件）。"GMAT 零增量"结论基于全目录大小写不敏感 grep NVIDIA 零命中。demuxer_list.c/muxer_list.c 在源码树不存在（configure 构建期生成），直接 ls 验证。
