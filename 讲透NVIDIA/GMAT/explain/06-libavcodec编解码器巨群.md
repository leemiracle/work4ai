# 06 · libavcodec 编解码器巨群：视频主体与家族模板机制

## 角色定位

图谱 layer:06 是全仓最大的单层（1168 节点=1166 file+2 config），即 libavcodec 根目录的编解码器主体——数十个标准家族的 C 实现、解析器、位流过滤器与外库 wrapper 的总集合。任务书把它描述为"视频编解码器巨群（aac 51/dca 30/opus 21 家族）"：经实测甄别，aac*/dca*/opus* 三族的盘上文件数确为 51/30/21（.c+.h 口径），但图谱把它们归入 layer:07 音频编解码群（360 节点）——layer:06 的实测构成是**视频+图像+字幕**（h264 46、hevc 24、vp9 23、rv 19、jpeg/mjpeg 30、vc1/wmv 25、mpeg4+mpeg12 21、av1 9、prores/cfhd/dnxhd/ffv1/png/tiff 等"专业格式军"、字幕族 ass/text/dvb/srt 等 20 余种）。本文以 layer:06 视频主体为纲，音频三族作对照带出（其模板机制同源）。这一层是"仓库为什么这么大"的直接答案，也是 GMAT 与上游完全共享、零 fork 增量的存量世界。

## 内部结构

**H.264 家族（46 文件）是模式标本**：h264dec.c/h 是入口与上下文（ff_h264_decoder ffmpeg-gpu/libavcodec/h264dec.c:1069），职责切分到物理文件——h264_slice.c（切片级解码状态机）、h264_cabac.c/h264_cavlc.c（双熵解码后端）、h264_loopfilter.c（去块滤波）、h264_mb.c/h264_mc_template.c（宏块重建与运动补偿）、h264_direct.c（B 帧直接模式）、h264_parse.c/h2645_parse.c（与 HEVC 共享的 NAL 解析底座，h2645 即"h264 or h265"）、h264_levels.c（级别校验）、两个 bsf（h264_metadata_bsf.c/h264_mp4toannexb_bsf.c——后者正是 metrans Demuxer 处理 mp4→Annex-B 的现役工具）。**模板机制是家族的灵魂**：h264dsp_template.c/h264idct_template.c/h264chroma_template.c/h264_mb_template.c/h264_mc_template.c 等以 `#define BIT_DEPTH n` + `#include "*_template.c"` + `#undef` 的三连双包含实例化出多套符号——h264dsp.c:38-48 实测三连实例化 8/9/10bit 三份，h264chroma.c:23-29 实例化 8/16bit 两份——同一份算法源服务多位深。**HEVC 家族（24 文件）**同构而年轻：ffmpeg-gpu/libavcodec/hevcdec.c:3870 入口、hevc_parse.c/hevc_ps.c 参数集、hevc_filter.c 去块；**AV1（9 文件）**ffmpeg-gpu/libavcodec/av1dec.c:1248 入口+av1_parse.c+obu 解析族；**VP9（23）**vp9.c/vp9block.c/vp9lpf.c/vp9mvs.c+按位深分文件的三件 vp9dsp_8bpp.c/vp9dsp_10bpp.c/vp9dsp_12bpp.c（vp9 家族用"分文件实例化"替代双包含，效果等价）；**RealVideo（rv 19）**与 vc1/wmv（25）是存量兼容军；**专业格式军**：prores（9，Apple 序列帧）、dnxhd（6，广播）、cfhd（8，CineForm）、ffv1（7，无损归档）、magicyuv/png/tiff/webp 图像族。**字幕族**约 30 文件：ass.c/srtdec/dvbsub/xtsub 等全覆盖，走 decode_sub 回调（codec_internal.h:96-97 的 DECODE_SUB 形态）。**外库 wrapper**（lib 前缀 55 文件）：libx264.c:1219 的 ff_libx264_encoder 代表——FFmpeg 只做参数翻译与帧搬运，编码本体在外部库。

## 外部连接

**向上**依赖框架层全部服务：FFCodec 回调注册进 codec_list（allcodecs.c:868 的生成表）、包与帧走 send/receive 泵（decode.c:576/639）、输出帧从 ff_get_buffer（decode.c:1403）取。**向下**依赖 SIMD 军：每个 dsp 文件（h264dsp.c 等）的 init 函数按 cpuflags 挂 x86/aarch64/mips 实现（layer:08-11 的汇编），C 版模板是兜底与语义基准——三层（C/SIMD/GPU）分工中本层提供"语义真相"。**横向**与 hwaccel 协作：h264dec.c 的解码回调被 nvdec_h264.c（layer:05）劫持填充 CUVIDPICPARAMS 后 GPU 接管，同一 h264dec.c 同时是软解与 NVDEC 硬解的宿主——这是"装饰器"模式的复用红利。**与 GMAT 的关系**：零修改（fork 增量不在此层），但被消费极深——NvDecLite 解码的 h264 流、metrans 写出的 hevc 流、HevcParser 解析的 NAL，语义都由本层文件定义；读 hevcdec.c 与读 metrans HevcParser 是同一规范的两个视角（前者含像素重建，后者只到语法）。

## 数据流

以 h264 软解一帧为例：send_packet（decode.c:576）入 Annex-B 包 → h2645_parse.c 把字节流切 NAL 并剥转义 → h264_parse.c 译 SPS/PPS（h264dec.c:696-701 在探测失败时也会试译 extradata）→ 切片 NAL 进 h264_slice.c 的状态机 → 熵解码双选一（CABAC h264_cabac.c/CAVLC h264_cavlc.c）→ 残差经 h264idct 模板反变换 → h264_mc_template.c 运动补偿（参考帧由框架层管理）→ h264_loopfilter.c 去块 → ff_get_buffer 出帧 → receive_frame 交付。10bit 流的每个热点函数调用的是 BIT_DEPTH=10 实例化版本（模板双包含产物）。对照音频侧：aacdec_template.c 同样双包含出 aacdec.c（float）/aacdec_fixed.c（定点）两个编译单元——ffmpeg-gpu/libavcodec/aacdec.c:555 与 aacdec_fixed.c 各自实例化 ff_aac_decoder/ff_aac_fixed_decoder；dca 家族 30 文件里 dcadec.c:413 入口配 xll/xbr/pc 测评解码子件；opus 21 文件 opusdec.c:707/opusenc.c:728 双工，celt/silk 两解码核分文件。这套"模板=算法、包含=实例化"的语言级泛型比 C++ 模板早二十年且至今在岗。

## 设计决策

①**文件即模块边界的粗粒度拆分**：46 个 h264 文件不建子目录、不用构建元数据，靠文件名前缀自解释——在数千文件的目录里保持了 grep 可达性（找去块=直接开 h264_loopfilter.c）。②**模板双包含而非运行时分派**：位深是编译期常量，热点零分支；代价是符号表翻倍与调试困惑（断点命中 *_template.c 但栈帧是实例化名）。③**h2645_parse 共享底座**：H.264/HEVC 的 NAL 语义 80% 重合（起始码/转义/长度前缀），合并实现省一份维护——与 metrans HevcParser 独立成库的选择相反，权衡点是有无 HEVC-only 语法需求。④**专业格式军的"够用即可"**：prores/dnxhd 解码器只实现广播域子集，编码器另配——工业格式按需裁剪而非求全。⑤**lib wrapper 一致化**：libx264/libx265/libvpx/libaom/librav1e/libsvtav1 全部套同一 wrapper 骨架（AVOption 映射+帧搬运+flush 协议），新外库接入成本被骨架摊薄。

## 新人提示

别线性读——按"入口→状态结构→一个垂直功能"三跳：h264dec.c 的 ff_h264_decoder（:1069）看回调面 → h264dec.h 的 H264Context 看状态全集 → 挑 h264_loopfilter.c 一个功能读透闭环。模板文件要认 BIT_DEPTH 宏的 include 头两行（h264dsp.c 对模板的双 include 是理解实例化的钥匙）。字幕族是新手友好区（文本类 <300 行/个）。**甄别提醒**：想找 aac/dca/opus 请直接去根目录搜前缀（它们与视频混居根目录，图谱才分层）；想让某家族支持 10bit，先确认模板已双包含，只改 *_template.c 一处。调试大杀器是 `ffmpeg -debug 3`（逐宏块 trace，仅限软解路径）。与 GPU 侧对照阅读：nvdec_h264.c 里 pic_params 的每个字段赋值，对应 h264_slice.c 里同名语法元素的解析——两边对读一遍，"硬解为什么会有兼容性问题"的直觉就建立了。

---
*甄别条款：①任务书把 aac 51/dca 30/opus 21 计入本层描述，经图谱实测三族在 layer:07（音频 360 节点）、layer:06 为 1166 file 节点且以视频+字幕为主——盘上文件数 51/30/21 属实，本文开头已声明口径并作对照带出；②家族文件数（h264 46/hevc 24/vp9 23/av1 9）为 .c+.h 前缀实测，与图谱 layer:06 家族计数（h264 46/hevc 24/vp9 23/av1 9）一致；③h264dec.c:696-701 的 SPS 试译锚自 grep 实测；④"fork 零增量"依据=configure/allfilters/Makefile 三处登记中无本层文件。字数不含空格。*
