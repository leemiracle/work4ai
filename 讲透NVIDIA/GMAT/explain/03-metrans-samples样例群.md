# 03 · metrans/samples：22 个样例与 GPU 解码/渲染链

## 角色定位

samples/ 是 MeTrans SDK 的可执行说明书：20 个根目录 .cpp + AppNvDecGL/ 子目录，每个都是 36-418 行、自带 main 与命令行解析的独立程序，全部由 metrans/Makefile:23-27 的 BIN/BIN_GL/BIN_HEIF 列表编排。它们不是玩具——README.md:18 的"GPU codec tools: Programs to access and benchmark nvdec/nvenc/nvjpeg"直接指的就是这批产物，其中 Perf 双雄（AppNvDecPerf/AppNvEncPerf）就是官方基准工具，metrans/doc/perf.xlsx 的数据即出自它们。样例群按引擎分三族：FFmpeg 软件路径（App 前缀 + Vid/Aud/Mux，11 个）、Nv 硬件路径（AppNv*，8 个）、图像编解码（AppHeif*，2 个，编入 BIN_HEIF 档）。

## 内部结构

**FFmpeg 族**展示 AvToolkit 全家桶的最小用法，代码短到极致：AppVidDec.cpp 49 行走完"Demuxer→VidDec→SaveFrame"（DecodeVideo 在 AppVidDec.cpp:22，do-while 循环 35-42 行）；AppVidFilt.cpp:25-35 读裸帧文件进 VidFilt，滤镜串是硬编码的 `"scale=1280:720,hflip"`（AppVidFilt.cpp:31）；AppMux/AppVidTrans/AppAvTrans 分别演示容器写、视频转码、音视频合流。**Nv 族**按"访问→性能→组合"递进：AppNvDec（230 行）是 GPU 解码入门，DecodeFile() 36-63 行给出 Demuxer→NvDecLite→写文件闭环（AppNvDec.cpp:41 构造时传 cropRect/resizeDim，NVDEC 硬件级裁剪缩放）；AppNvEnc（418 行，最长样例）演示 NvEncLite 全参数面；AppNvTrans（189 行）是全 GPU 转码最小样本——`NvDecLite dec(cuContext, true, ...)` 帧留显存（AppNvTrans.cpp:131），编码器按需做位深转换 kernel（AppNvTrans.cpp:152-163 的 ConvertUInt8ToUInt16/UInt16ToUInt8 分支）后 `EncodeDeviceFrame` 直接吃 GPU 指针（AppNvTrans.cpp:154），全程无一次 D2H；AppNvjpegDec 独立演示 nvjpeg 库（AppNvjpegDec.cpp 起 `nvjpegCreate(NVJPEG_BACKEND_DEFAULT,...)`）。**Perf 双雄**是多线程压测器：AppNvDecPerf 的 DecProc 起向量线程（AppNvDecPerf.cpp:155-162），AppNvEncPerf 同构（-thread 默认 2，AppNvEncPerf.cpp:46），衡量的是**多会话并发吞吐**而非单流延迟。

**渲染链三件套**（本篇重点）：AppNvDecGL/ 仅两文件——AppNvDecGL.cpp（109 行）与 FramePresenterGL.h（256 行）。链路是 Demuxer→`NvDecLiteImageProvider`→FramePresenterGL：AppNvDecGL.cpp:32-38 构造三方，主循环 `while (presenter.GetDeviceFrameBuffer(&dpFrame, &nPitch) && dec.GetNextImageAsBgra((uint8_t *)dpFrame, nPitch, true))`（AppNvDecGL.cpp:42-44）——一帧一个 GL 事件循环迭代。

## 外部连接

依赖面上，样例群是 metrans/include/ 的全量消费者矩阵：AppNvDec.cpp:16-18 include Demuxer/NvDecLite/NvCommon 三件；渲染链额外拉进 NvDecoderImageProvider.h（AppNvDecGL.cpp 经由它把 NvDecLite 变成"图像迭代器"——GetNextImageAsBgra/BgrPlanar/Bgra64 三个格式出口，NvDecoderImageProvider.h:80-88）。构建依赖分档：AppNvDecGL 单独编（metrans/Makefile:26/92，需 GLEW/glut 全家，metrans/Makefile:15 的 LDFLAGS_GL），README.md:96 明示它要本地图形环境、远程 DISPLAY 很难配；HEIF 两个样例挂 -lheif_writer_shared（metrans/Makefile:16）。AppNvDecPerf 与 AppNvDecScan 这类工具不写输出文件时就是纯基准/扫描模式，是 ops 侧巡检 GPU 解码能力的现成工具（AppNvDec 的 ShowDecoderCapability 本身就打印全 GPU 解码能力矩阵，AppNvDec.cpp:65-108）。

## 数据流

渲染链的完整一帧：①NvDecLite 解码出 NV12 设备帧（锁帧版 DecodeLockFrame 防池复用，NvDecoderImageProvider.h:97）；②GetNextImageAsFormat 在 GPU 上跑 ColorSpace.cu 的 Nv12ToBgra32 kernel（NvDecoderImageProvider.h:124-128），色彩矩阵取自码流 VUI 的 matrix_coefficients（NvDecoderImageProvider.h:81）——BT.601/709 自动适配；③目的地不是主机内存而是 FramePresenterGL 在显存里的 dpFrame 缓冲（FramePresenterGL.h:129 `cuMemAlloc(nWidth*nHeight*4)`）；④FramePresenterGL 独立消息线程的 Display() 把 GL PBO 注册进 CUDA（cuGraphicsGLRegisterBuffer，FramePresenterGL.h:147）、映射出设备指针（:151）、`cuMemcpy2DAsync` 设备到设备搬运（FramePresenterGL.h:153-162），再 glTexSubImage2D 从 PBO 上纹理（:169），用一段 ARB 汇编着色器采样（!!ARBfp1.0，FramePresenterGL.h:117-123——2017 年代代码，当时 GLSL 还不是唯一选择）；⑤窗口超过 1280x720 会按比例缩放窗口（FramePresenterGL.h:83-87）。全程帧只存在于显存与 GL 缓冲对象间，零主机往返——这正是 CUDA-GL interop 的教科书流程，也解释了为何它必须本地图形栈。

## 设计决策

①**样例即 API 文档**：没有 doxygen，NvDecLite 的 cropRect/resizeDim（AppNvDec.cpp:41）、NvEncoderInitParam 的透传（AppNvTrans.cpp:82-87 把所有非 `-i/-o` 参数归集给编码器）等用法全靠样例演示，改动 API 必须同步改样例。②**Provider 中间层**：NvDecLiteImageProvider 把"解码器+格式转换"包成 GetNextImageAsBgra 迭代器（NvDecoderImageProvider.h:65-79），解耦了消费速度与解码吞吐——deque 帧队列空了才补解码（:91-102）。③**GL 线程独占模型**：FramePresenterGL 用独立线程 + `while(!pInstance) sleep`（FramePresenterGL.h:37-40）等窗口就绪，主线程与 GL 线程只通过 GetDeviceFrameBuffer 的返回值握手——回避了 GL 上下文的跨线程陷阱，代价是 GetDeviceFrameBuffer 实为"查询窗口是否还活着"（返回的是内部缓冲指针，FramePresenterGL.h:48-56）。④**输出格式自描述**：AppNvDec 按 8/10bit 与 planar 开关四路输出 nv12/p010/iyuv/yuv420p16（AppNvDec.cpp:59-62），省去用户猜格式。⑤**Perf 与功能样例分离**而非塞一个 -perf 开关，让基准工具可以长期冻结不被功能迭代污染。

## 新人提示

跑样例前先 `make -j10`（essentials 档），默认输入是 bunny.h264/bunny.mp4（AppNvDec.cpp:188），没有该文件会直接退出（CheckDefaultFileExists）。推荐上手序列：AppVidDec（49 行，软解）→ AppNvDec（硬解+能力表）→ AppNvTrans（全 GPU 转码）→ AppNvDecPerf `-thread 4`（看多会话伸缩）→ 有本地屏幕再战 AppNvDecGL。读代码时注意 AppNvDec.cpp:24-34 的 ConvertToPlanar 用的是 NvCommon.h 里的 YuvConverter 模板——**主机侧**格式转换，与 NvDecoderImageProvider 的**设备侧**转换是两套路径，别混。坑位提示：-crop/-resize 参数必须偶数（AppNvDec.cpp:167-169 显式检查）；AppNvDecGL 用 CU_CTX_SCHED_BLOCKING_SYNC 建上下文（AppNvDecGL.cpp:106）与其他样例的默认 flags 不同，是为了 GL 事件循环的 CPU 友好。

---
*甄别条款：①样例计数口径=20 个根目录 .cpp + AppNvDecGL 目录程序，BIN 列表 21 项中 AppNvDecScan/AppExtract/AppSelect 在 app/ 也有门面版（Makefile:23-24 含三者），samples/ 与 app/ 的界线是"演示"vs"产品"；②"22 个示例"沿用任务书与图谱 tour 口径（20 根目录样例+GL 两件套之二元计法），Makefile 实编 BIN 21 个二进制；③AppVidFilt 滤镜串锚 AppVidFilt.cpp:31 经 grep 精确复核；④FramePresenterGL.h:117-123 ARB 着色器与 cuMemcpy2DAsync 锚自 Read 实读。字数不含空格。*
