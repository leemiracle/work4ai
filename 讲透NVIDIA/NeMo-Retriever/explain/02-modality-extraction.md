# 02 · 多模态抽取：operators/extract 算子群 + common/modality 共享层

> 路径相对 `nemo_retriever/src/nemo_retriever/`。

## 角色定位

这是 NeMo-Retriever 的主营业务：把 PDF/Office/HTML/文本/图像/音频/视频变成可嵌入的结构化内容。代码分两层——`operators/extract/`（39 个算子，按模态分 12 个子包）是执行层，每个算子继承 01 篇的基座；`common/modality/`（图谱 30 节点、12 个子包）是共享逻辑层，沉淀各模态的转换/切分/探测代码。分层的动机很实际：同一种"转 PDF"逻辑既被 DOCX 抽取用，也被表格抽取用；ffmpeg 探测既服务音频 ASR 也服务视频帧抽取——放算子里会重复，放 modality 里一处维护。

## 内部结构

**PDF 主战场**：`operators/extract/pdf/extract.py` 负责页级抽取，`operators/extract/pdf/split.py` 负责 PDF 分块（服务模式按 chunk 摄取的支撑件）。任何 Office 文档先经 `common/modality/convert/to_pdf.py:47` `convert_to_pdf_bytes` 转 PDF 再走统一抽取；批量入口 `convert_batch_to_pdf`（`:103`）作用于整批 DataFrame；CPU 变体算子 `DocToPdfConversionCPUActor`（`:170`）与原型算子 `DocToPdfConversionActor`（`:193`）构成"转 PDF"站。

**HTML/文本**：`common/modality/html/convert.py:69` `html_to_markdown` 是核心转换（含 `_HTMLTextFallbackParser`（`:29`）在解析器缺失时退化为纯文本提取）；分块入口 `html_file_to_chunks_df`（`:113`）与 `html_bytes_to_chunks_df`（`:163`）。文本切分全家在 `common/modality/txt/split.py`：`split_text_by_tokens`（`:45`）按 token 切，`split_df`（`:100`）作用 DataFrame，`txt_file_to_chunks_df`（`:183`）/`text_to_chunks_df`（`:212`）/`txt_bytes_to_chunks_df`（`:279`）三种输入形态入口；tokenizer 由 `common/modality/txt/tokenizer_provider.py` 提供。

**OCR 四路**：`operators/extract/ocr/` 下 `cpu_ocr.py`/`gpu_ocr.py`（OCR 推理双变体）与 `cpu_parse.py`/`gpu_parse.py`（版面解析双变体），`ocr.py` 是聚合入口；共享配置在 `common/modality/ocr/config.py`——`resolve_ocr_v2_model_dir`（`:16`）解析本地模型目录、`resolve_ocr_v2_lang`（`:36`）解析语言；`common/modality/ocr/shared.py`（1436 行）是 OCR 后处理的最大共享件。

**音频**：`operators/extract/audio/` 四 actor——`asr_actor.py`（Parakeet ASR 推理）、`chunk_actor.py`、`cpu_actor.py`、`gpu_actor.py`；全部站在 `common/modality/audio/media_interface.py:243` `MediaInterface` 上：ffmpeg/ffprobe 可用性探测族（`:42-67`）、`probe_media`（`:249`）、`split`（`:297`）、`extract_frames`（`:371`）、`find_num_splits`（`:422`）、`_get_audio_from_video`（`:171`）抽音轨。缺 ffmpeg 时 `missing_media_dependencies`（`:67`）返回缺失清单，服务层据此 501。

**视频**：`operators/extract/video/` 五件——`frame_actor.py` 帧抽取、`ocr_actor.py` 帧内 OCR、`audio_visual_fuser.py` 音视融合、`text_dedup.py` 跨帧去重、`split.py`。融合与去重都是自连接算子（要全量同块数据），内容类型定义在 `common/modality/video/_content_types.py`。

**图表/表格/caption/版面**：表格结构重建在 `common/modality/table_and_chart.py`——`assign_boxes`（`:27`）框分配、`_join_yolox_table_structure_and_ocr_output`（`:64`）YOLOX 结构+OCR 文本对齐、`build_markdown`（`:178`）输出 markdown 表格、`join_table_structure_and_ocr_output`（`:408`）公共入口、`reorder_ocr_for_infographic`（`:446`）信息图重排；执行算子在 `operators/extract/table/`（cpu/gpu actor + `table_detection.py`）。caption 模型画像在 `common/modality/caption/model_profiles.py`：远程模型 ID 常量（`:20,25`）、`CaptionCapabilities`（`:40`）与 `CaptionModelProfile`（`:51`）两个 dataclass、`get_caption_model_profile`（`:152`）、`resolve_caption_model_name`（`:176`）——OMNI 模型默认关思考链的 extras 在 `:36`（`enable_thinking: False`）。版面元素共享层 `common/modality/page_elements/`（shared.py+local.py），抽取算子在 `operators/extract/page_elements/`；Nemotron Parse 的后处理在 `common/modality/parse/nemotron_parse_postprocessing.py`，算子在 `operators/extract/parse/nemotron_parse.py`。

## 外部连接

每个模态算子向上接 `AbstractOperator`/`CPUOperator`/`GPUOperator`/`ArchetypeOperator`（见 01 篇）。向下依赖模型层：OCR→`models/local/nemotron_ocr_v2.py` 或 NIM endpoint、ASR→parakeet、caption→`models/local/vlm_captioner.py`、版面→`models/local/page_elements_v3.py`。`common/modality/pipeline/content.py:51` `explode_content_to_rows` 把多模态内容行爆炸成"每内容一行"，是抽取段通向嵌入段的桥。服务层引用 `media_interface.py` 的常量做启动横幅（`service/app.py:95-100` 导入）。

## 数据流

统一货币是 DataFrame：文件 bytes+path 进 →（转 PDF）→（OCR/版面/表格）→ 文本 chunk+content_type+bbox+page_number 出 → 嵌入 → LanceDB。音频视频先过 `probe_media` 定时长，切分后视频走"帧抽取→帧 OCR→音视融合"三连，音频走"切分→ASR"。所有模态的产物行都带 `content_metadata`（type/subtype/page_number），供下游 `records.py` 的 `_client_record_from_graph_row`（`common/vdb/records.py:288`）转成向量库记录。

## 设计决策

1. **先归一 PDF**：Office 全走 to_pdf 转换而非各写解析器——用 pdfium 一条链吃掉 DOCX/PPTX 等 6 种格式，代价是多一次转换。
2. **执行/共享两层分仓**：算子只做"三段式编排+actor 化"，模态知识全部下沉 modality——CPU 单测可以直接测 modality 函数，不必拉起 Ray。
3. **CPU/GPU 双变体成对出现**：OCR/parse/表格/嵌入都给 `cpu_*`/`gpu_*` 双实现，由 archetype 或执行期资源探测挑选，笔记本与大集群同一张图。
4. **caption 画像集中管理**：模型 ID/revision/extras 不散在算子里而在 model_profiles 一张表，换模型只改一处。
5. **自连接算子显式声明**：音视融合/去重要求同块全量数据，通过类属性让执行器强制单块（见 03 篇 `REQUIRES_GLOBAL_BATCH`）。

## 新人提示

- 新增文件类型支持的路径：`convert/to_pdf.py` 加转换 → 复用 PDF 抽取链；只有无法转 PDF 的模态才值得新开 extract 子包。
- ffmpeg 是音频视频的硬依赖：本机跑不通先查 `is_media_available()`（`media_interface.py:443`），服务模式看启动 WARNING。
- `table_and_chart.py` 的 YOLOX+OCR 对齐逻辑对 bbox 顺序敏感，动 `reorder_boxes`（`:243`）前先跑表格回归测试（ci/ 里有 bbox 基线 CSV）。
- caption 模型默认本地 OMNI（`model_profiles.py:30`），显存吃紧可切 NANO 远程档——改 `resolve_caption_model_name` 的入参而非改常量。
- 读 `ocr/shared.py`（1436 行）建议从后处理主函数入手倒着读，它是 OCR 输出到 metadata schema 的唯一译者。
