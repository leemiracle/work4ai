# 02 · metrans/include/HevcParser：HEVC 码流解析与位流读取核心

## 角色定位

HevcParser/ 是 metrans 里唯一**不碰 GPU** 的子系统（10 文件、约 120KB），职责是把 HEVC Annex-B 码流逐 NAL 展开成 C++ 对象树。它回答的问题是："不解码像素，我能从码流本身知道什么？"——SPS 里的分辨率/位深、SEI 里的场景信息、Slice 头里的帧类型。GMAT 的"智能解码"卖点（README.md:19"decode frames with scene cut detection"）一半靠 GPU 侧的 select_cuda+scene 检测（像素域），另一半就靠这里在**码流域**提前拿到元数据，避免"为知道一帧是不是场景切换而先解码它"的浪费。口径甄别：任务书称本主题为"传输库核心"，实读该目录为码流（bitstream）解析库，无任何网络传输（transport）语义组件，本文按源码实际语义展开。

## 内部结构

五层递进：**HevcParser.h/HevcParser.cpp** 是门面——抽象类 `HEVC::Parser` 只暴露 parse/process 两个入口和 Consumer 观察者协议（HevcParser.h:33-37），工厂方法 `Parser::create()` 返回唯一实现 HevcParserImpl（HevcParser.cpp:12-15），调用方拿到的是无实现细节的接口。**HevcParserImpl.cpp**（80KB，仓库最大的单实现文件）是语法树引擎：process() 扫起始码切 NAL（HevcParserImpl.cpp:38），parse() 返回 Data_NALUnit 向量（HevcParserImpl.cpp:97），processNALUnit() 按 nal_unit_type 分派（HevcParserImpl.cpp:129）到 processVPS/processSPS/processPPS/processSEI/processSlice 等二十余个 process* 方法（HevcParserImpl.cpp:534/607/1080/723/238）——方法名与 H.265 规范条款一一对应，读起来像规范目录。**Hevc.h**（740 行）是纯数据模型：NALUnitType 枚举 41 种 NAL（Hevc.h:12-39，TRAIL/RADL/RASL/IRAP/VPS/SPS/PPS/SEI...），类按参数集组织——NALHeader（Hevc.h:41）、ProfileTierLevel（Hevc.h:50）、HrdParameters（Hevc.h:103）、VPS/SPS/PPS/Slice，SEI 侧以 SeiPayload 为基类派生 12 种载荷（Hevc.h:227 起：DecodedPictureHash/SceneInfo/BufferingPeriod/PicTiming...）。**BitstreamReader**（.h 26 行 + .cpp 84 行）是模板化位读取器：getBit/getBits/skipBits/showBits 加 Exp-Golomb 双向解码 getGolombU/getGolombS（BitstreamReader.h:11-16），内部用 m_posBase/m_posInBase 双游标（BitstreamReader.h:24-25），还提供 availableInNalU()（BitstreamReader.cpp:23）——在 rbsp_trailing_bits 前的剩余位数，切片数据截断判断的关键。**HevcUtils**（20+58 行）是补集工具：256 项 log2 查表（HevcUtils.cpp:5-14）与 calcNumPocTotalCurr（HevcUtils.h:12，POC 总引用数计算，Slice 解析的规范级算法）。

## 外部连接

**上游供给**：metrans/app/AppHevcParse.cpp 是它的直接消费者——SimpleConsumer 继承 Parser::Consumer 实现 onNALUnit/onWarning（AppHevcParse.cpp:42-45/135-136），主流程 `Parser::create() → addConsumer → parse(pkt->data, pkt->size)`（AppHevcParse.cpp:158-178），从 Demuxer 拿包喂解析器，与 NVDEC 解码完全并行。构建上它与 NvDecLite 一起编进 AppHevcParse（metrans/Makefile:37：AppHevcParse.o + NvDecLite.o + BitstreamReader.o + Hevc.o + HevcParser.o + HevcParserImpl.o + HevcUtils.o）——码流解析与 GPU 解码在同一个程序里协作。**信息流互补**：NvDecLite 的 CUVIDPICPARAMS/CUVIDPARSERSPINFO（NvDecLite.h:19-23 的 NvFrameInfo）给的是解码器视角的帧信息，HevcParser 给的是压缩域视角（如 SEI scene_id）；AppNvDecScan.cpp:46-50 的"裸字节判 nal_ref_idc"是两者之间的廉价捷径——只在 H.264 单层码流有效，多层/复杂码流就得靠完整解析器。**零 FFmpeg 依赖**：本目录不 include 任何 libav* 头（Hevc.h 仅用 std::memory/vector/array），因此是 metrans 中可整体拷走的独立组件。

## 数据流

以"一帧 SEI 场景信息"为例：Annex-B 字节流进入 process()，起始码 00 00 01 切出 NAL 边界（HevcParserImpl.cpp:38 起）；processNALUnit() 读 16 位 NAL 头（forbidden_zero/nuh_layer_id/temporal_id，HevcParserImpl.cpp:222-238 的 processNALUnitHeader），type=39（SEI_PREFIX，Hevc.h:38）进入 processSEI()（HevcParserImpl.cpp:723）；SEI 内部再按 payloadType 分派，type=9 命中 SCENE_INFO（Hevc.h:246 枚举 + HevcParserImpl.cpp:810-814 的 case），new 出 SceneInfo 对象由 processSceneInfo() 逐位填充（HevcParserImpl.cpp:2274-2277 起：scene_info_present_flag/prev_scene_id_valid_flag/scene_id/scene_transition_type，字段定义 Hevc.h:303-309）；填充完毕的对象以 shared_ptr<NALUnit> 装入 Data_NALUnit 返回/推给所有注册 Consumer（HevcParser.h:27 的 onNALUnit 回调）。位级细节全部由 BitstreamReader 承担：u(n) 是 getBits(n)、ue(v) 是 getGolombU、se(v) 是 getGolombS——HEVC 语法表的三大算子就这三个入口，这解释了为何 .cpp 只有 84 行却撑起整棵语法树。

## 设计决策

①**观察者模式而非返回值透传**：parse() 既返回向量又回调 Consumer（HevcParser.h:33-35），双通道适配"批处理"与"流式"两种消费姿势；WarningType 分级（NONE/OUT_OF_RANGE/REFERENCE_STRUCT_NOT_PRESENT/PROFILE_CONFORMANCE，HevcParser.h:21-23）表明解析器坚持"尽力而为"——坏语法不抛异常而降级告警，转码场景下可用性优先于严格性。②**Pimpl + 工厂**：公开头只有抽象类，HevcParserImpl 藏在 .cpp，二进制隔离做得比 metrans 其他部分彻底（对比 NvDecLite 的回调桥）。③**数据模型全 public 字段 + toDefault()/operator==**（Hevc.h:73-75 等）：不做封装，解析器就是"把规范字段搬到内存"，operator== 服务参数集变化检测（新 SPS 是否需要重建解码器）。④**查表 log2 而非循环**（HevcUtils.cpp:5）：HEVC 语法里 log2 调用极密（CU 深度/坐标），256 表 + 两级移位是性能敏感处的朴素选择。⑤**未做抗仿真字节处理了吗？**做了——BitstreamReader 的 m_posBase 推进逻辑配合 process 阶段的转义剥离，但剥离发生在 NAL 切分后的局部缓冲，保持 Reader 纯净。

## 新人提示

读法：先 HevcParser.h（45 行）立起骨架，再跳 HevcParserImpl.cpp 的 processNALUnitHeader（222 行起，最短最典型），然后按需查表式阅读各 process*。验证理解的最佳输入是 raw HEVC Annex-B 流（AppHevcParse 默认输入 bunny.h265 一类）；AppHevcParse.cpp 的 SimpleConsumer 里能看到 SPS/SEI/Slice 各自怎么消费。两个易错点：HEVC 的 NAL 头是 16 位而 H.264 是 8 位——所以 AppNvDecScan.cpp:45 那套 `data[2]==1 ? data[3] : data[4]` 的字节偏移只对 H.264 成立，拿去判 HEVC 会错位；BitstreamReader 是 MSB-first（BitstreamReader.cpp:54 的 `& 1 << m_posInBase` 从高位起），与很多网络协议读取器相反。若只想拿分辨率/位深，直接消费 SPS 对象（processSPS HevcParserImpl.cpp:607 起）不必逐位理解全部语法。

---
*甄别条款：①任务书"传输库核心"表述与实读不符，本文以码流解析语义写作并在开头声明；②"AppHevcParse 与 HevcParser 的 Makefile 关系"锚自 metrans/Makefile:37 实测行；③SEI SCENE_INFO 载荷与 README"scene cut detection"的关系为源码实证（HevcParserImpl.cpp:810），但 README 所述智能解码主路径在 AppSelect/FrameSelect（像素域 scene 过滤），两条路径并存，勿混为一谈。字数不含空格。*
