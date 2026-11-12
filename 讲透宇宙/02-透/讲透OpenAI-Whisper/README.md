# 讲透 OpenAI-Whisper

openai/whisper @ 86098128（版本 20250625）知识库。鲁棒语音识别 ASR 官方 PyTorch 推理实现：编码器-解码器 Transformer，68 万小时弱监督训练，多语言转写/X→英翻译。本仓只有推理代码，24 个 py 文件、11 个核心模块。

图谱：130 节点 / 306 边 / 14 层 / 14 步 tour（`.understand-anything/onboard-input.json`）。

## 产物清单

| 产物 | 状态 | 说明 |
|---|---|---|
| onboarding/ONBOARDING.md | ✅ | 8 节新人导航，6492 不计空格字符，85 行号锚全核实 |
| explain/01-model.py-Transformer骨架.md | ✅ | 编码器-解码器与 KV 缓存 hook，62 锚 |
| explain/02-normalizers-评测文本归一化.md | ✅ | English/Basic 归一化（评测专用，推理链路零消费），37 锚 |
| explain/03-tokenizer.py-词表与BPE.md | ✅ | GPT-2 BPE、token id 布局算术、中文 Unicode 切词，56 锚 |
| explain/04-transcribe.py-滑窗与温度回退.md | ✅ | 30s 滑窗/温度阶梯/幻觉防御三阈值，68 锚 |
| explain/05-timing+triton_ops-词级时间戳DTW.md | ✅ | 交叉注意力 QK→DTW 对齐双实现，62 锚 |
| explain/06-__init__+utils-API面与输出层.md | ✅ | load_model 装配线与六格式 writer，55 锚 |

锚点口径：`whisper/xxx.py:行号`（全路径）；全部经 sed/grep 现场核实（425 锚零坏）。字数口径：不计空格字符。

## 勘误摘要（详见各篇勘误节）

1. decoding.py:660 真 bug：`return TypeError` 应为 `raise`，dtype 校验形同虚设。
2. 任务书/图谱的 "AudioEncoderChunked" 不存在（实为 AudioEncoder）；仓库亦无 vad.py——06 篇按源码实际改为 utils 输出层。
3. `_MODELS` 14 键/12 唯一 URL（图谱称 13；README 表只列 6 档）。
4. cantonese(yue) 在 LANGUAGES 表但官方词表无其 token（num_languages=99 截断）。
5. compression_ratio 实现是 zlib，docstring 写 gzip（文档漂移）。
6. normalizers 的 `regex` 硬依赖未列入 pyproject 依赖声明。
7. dtw_cuda 隐性 1024 文本 token 上限（BLOCK_SIZE 断言）。
8. transcribe.py:179 标点常量与参数默认值不联动（配置漂移）。
