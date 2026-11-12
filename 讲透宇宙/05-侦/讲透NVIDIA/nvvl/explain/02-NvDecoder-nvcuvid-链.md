# 02 · NvDecoder：nvcuvid 回调驱动的解码状态机

## 角色定位

`src/detail/NvDecoder.cpp`（482 行）是全库心脏：把 VideoLoader 送来的压缩包变成 NVDEC 解码帧，再排队等 convert 线程取走。它继承自 `Decoder` 抽象（`src/detail/Decoder.h:46`），后者定义了请求语言 `FrameReq{filename, frame, count}`（`:25-29`）、`CUStream` RAII（`:31-44`）和四个虚接口 push_req/receive_frames/finish/decode_av_packet（`:57-63`）。仓里只有 NvDecoder 一个实现——抽象层是为"将来接 ffmpeg 软解"预留的（VideoLoader.cpp 里留过 "todo setup an ffmpeg decoder?" 注释，`src/VideoLoader.cpp:312-316`）。

## 内部结构

构造即装配流水线（`src/detail/NvDecoder.cpp:31-125`）：`cuInit`（`:44`）→ NVML 查内核模块版本决定流策略（<384 用默认流，`:78-82`；NVML 出错也保守降级，`:88-94`）→ `CUContext`（`:96`）→ codec 三路 switch 只认 H264/HEVC（`:102-115`）→ `CUVideoParser(codec, this, 20, extradata)`（`:117`）→ 起 convert 线程（`:124`）。成员四件套 device/context/parser/decoder（`src/detail/NvDecoder.h:96-99`）对应驱动 API 的四级对象；`frame_in_use_` 位图（`:104`）+ 三条队列 recv/frame/output（`:105-107`）；纹理缓存以 `tuple<uint8_t*, ScaleMethod, ChromaUpMethod>` 为键（`:110-122`）。包装类都极薄：CUVideoParser 模板构造函数注册三回调（`src/detail/CUVideoParser.h:41-69`），CUVideoDecoder::initialize 查 caps 后按 NV12/自适应去隔行/20 解码面建解码器（`src/detail/CUVideoDecoder.cpp:159-183`）。

## 外部连接

向上被 `src/VideoLoader.cpp` 持有与驱动（首文件打开时 new，`:245-247`；`decode_packet` 在 read_file 循环里被逐包调用，`:468,510`）；向下经 `src/nvcuvid/nvcuvid.h` + `cuviddec.h`（仓内自带的 NVDEC SDK 头拷贝，`#include "cuviddec.h"` 同目录相对解析）调 `cuvidParseVideoData/cuvidDecodePicture/cuvidMapVideoFrame`（`src/detail/NvDecoder.cpp:150,207,229`）；横向把纹理对交给 imgproc kernel（03 篇），把事件 record 进 PictureSequence。

## 数据流

包进帧出的完整回路：`decode_av_packet` 把 AVPacket 塞进 `CUVIDSOURCEDATAPACKET`（pts 标记 TIMESTAMP，`:141-144`；空包即 ENDOFSTREAM flush，`:145-148`），`cuvidParseVideoData` 一调，控制权就交给 nvcuvid 回调。三回调即状态机三拍（trampoline 见 `:156-171`）：**handle_sequence** 记帧率基并 lazy-initialize 解码器（`:173-180`），序列中途换格式会被 `initialize` 拒绝（`src/detail/CUVideoDecoder.cpp:102-110`）；**handle_decode** 先自旋等 `frame_in_use_[CurrPicIdx]` 清位（`src/detail/NvDecoder.cpp:187`，usleep(500) 轮询 `:198`，超时默认关闭 `:186`）再 `cuvidDecodePicture`（`:207`）；**handle_display** 做"帧号对账"——pts 从 1/10^7 时基 rescale 成帧号（`:301`），与 `current_recv_` 比对：请求队列空→弃帧（`:304-319`，注释承认小概率扔掉未来要的帧），帧号不符→弃帧（`:334-340`），匹配→推进请求游标、置位图、入 frame_queue（`:347-351`）。convert 线程 `MappedFrame` 构造时 `cuvidMapVideoFrame` 拿 NV12 指针（`:215-234`），析构 unmap（`:243-249`），处理完清位图并写 frame_num meta（`:467-471`）。

## 设计决策

(1) **静态回调 + 模板分发**：nvcuvid 回调是 C 函数指针，虚表不可用；CUVideoParser 用模板参数 `Decoder*` 在编译期绑定 `Decoder::handle_sequence` 等静态成员（`src/detail/CUVideoParser.h:59-61`），NvDecoder 侧 `reinterpret_cast` 找回 this（`src/detail/NvDecoder.cpp:157`）——零运行时开销的 C ABI 桥。(2) **位图自旋而非锁**：decode 回调里等面空闲用忙等而非 condvar，因为回调运行在 nvcuvid 内部线程上下文，阻塞它风险更大；默认不开超时（`enable_timeout = false`，`:186`）。(3) **纹理三元组缓存**：假设 (指针, 缩放法, 色度法) 唯一标识纹理（`src/detail/NvDecoder.h:110-122` 注释），省去每帧重建纹理对象的开销；哈希手写异或（`:115-119`）。(4) **隔行帧硬抛异常**（`:220-221`）——2018 年的取舍，YCbCr 输出与 doc 示例都只走 progressive。工程毛边两处：位图 32 格 vs parser 20 面的常量不一致（`:36` vs `:117`）；CUVideoParser.h:51 在 HEVC 分支里给 `ulMaxNumDecodeSurfaces` 赋的 20 会被 `:57` 的统一赋值立即覆盖，是死赋值。

## 新人提示

调试先开 debug 日志（构造传 LogLevel_Debug，`pytorch/nvvl/dataset.py:186`），`handle_display_` 的弃帧日志会告诉你 seek 是否算准（"Ditching frame N since we are waiting for M"，`src/detail/NvDecoder.cpp:337-339`）。读这条链的正确顺序是 NvDecoder.cpp → CUVideoParser.h → CUVideoDecoder.cpp，三个包装类都不到 210 行。改解码面数量要同时动 `src/detail/NvDecoder.cpp:36` 的位图大小和 `:117` 的 parser 参数，两处没有静态约束兜底。`src/nvcuvid/` 两个 SDK 头是纯 C 声明，图谱工具对它们零提取属预期，不是漏分析。
