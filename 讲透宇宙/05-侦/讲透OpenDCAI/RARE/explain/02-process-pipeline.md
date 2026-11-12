# 02 process/ 数据构建族：双胞胎 RAG 脚本与四个单领域变体

## 角色定位

`process/` 是流水线第一站：把六个领域的原始数据集统一加工成 RARE 约定格式——`instruction`（检索文档+题目+`<think>/<answer>` 格式要求）与 `output`（`<answer>X</answer>` 金标）。七个脚本分两类：`process_medqa.py` 与 `process_pubmed.py` 是**双胞胎 RAG 脚本**，自带 embedding+向量检索；其余四个 process_*.py 是单领域直出变体；`select_true.py` 留待 05 篇。

## 内部结构

**双胞胎（251 行 vs 255 行，diff 仅 10 行：4 行注释 + 输出文件名 + target_names）**。核心是 `DocumentProcessor` 类（process_medqa.py:34，pubmed 同行号）：构造器加载 `BAAI/llm-embedder`（L35）并起 `QdrantClient(":memory:")` 内存向量库（L44）；`extract_document_blocks` 按 `## source:` 行切块（L46-66）；`get_embedding` mean pooling（L68-76）；`rank_blocks` 是"一次性检索"——每次建临时 collection（L91）、灌点（L98）、search 取 top-k（L112）、用完删库（L119），k 固定 `min(len(blocks), 3)`（L110）。模板（L19-31）声明 `<answer>A/B/C/D</answer>` 输出契约。真差异仅三处：medqa 输出名变量插值（L216），pubmed **硬编码** `_pubmed.json`（L220）；target_names 一个 `["medqa"]`（L234）一个 `["pubmedqa"]`（L238）——pubmed 内部名 pubmedqa、落盘名 pubmed，靠硬编码抹平。

**单领域变体**走两条路线：

- `process_pubhealth.py`：HF 直下 `bigbio/pubhealth`（L32），四分类映射 A-D（L35-40），train+validation 并入训练文件（L44）。
- `process_casehold.py`：五选项映射 A-E（L27-33），citing_prompt 整段作检索文档（L58）。
- `process_finfact.py`：true/false/NEI 映射 A-C（L35-40），evidence 拼接且防 NaN（L46）；seed 42 洗牌后 80/20 切分（L65-71）——唯一自带切分（Fin-Fact 无官方测试集）。
- `process_mmrait.py`：唯一 sharegpt 多模态产出。读 M2RAG fact_verify 的 train/val jsonl（L5、L8），Support/Refute/Insufficient 映射 A/B/C（L40-45），套带 `<image>` 占位的模板（L17-35），生成 `messages`（L52-57）、图片路径改写到 `data/{train,val}_document_images/`（L59-67）并整目录拷贝（L71-86）。产出 `train_mmrait.json` 与 `test_mmrait.json`（L6、L9）——后者正是 05 篇拼写坑的正主。

## 外部连接

双胞胎不读 HF 数据集，而是读 `process/rare_share/system=planner_addret,dataset=all_{train,dev,test},debug=False/output_all.json`（L141-143 拼路径）——论文组预生成的检索包（readme.md:93-96 有下载命令），每条样本的 `pred.doc_path` 指向文档原文（L161-165 校验）。其余变体依赖 `datasets.load_dataset` 或预下载的 M2RAG。产出统一写 `data/`（L209-211）。

## 数据流

双胞胎：`load_dataset(all_train+all_dev)` → 按 `name` 过滤（L167-169）→ 读 doc_path 原文 → 切块检索选 3 块 → 套模板 → `output=f"<answer>{gold}</answer>"`（L196）→ 分 train/test 落盘。变体更短：下载 → 映射 → 渲染 → 落盘。output 均带 `<answer>` 包裹，是与 eval/select_true 的格式契约。

## 设计决策（含批判）

**每题重建向量库**（L91/119）是显眼取舍：为单条样本的十几个块建删 collection，换来零状态、零端口、随处可跑——研究场景合理，规模场景荒谬。embedding 用 `llm-embedder`+mean pooling 而非专用检索模型，因为 RARE 主张推理靠模型、检索只是背景知识。**双胞胎复制而非参数化**（一个硬编码文件名就分家）与**模板六处各写一份**，是仓级"零共享"风格的缩影；pubmed 版多出的 4 行中文注释（L171-180）可见是从 medqa 拷出去各自演化的。

## 新人提示

1. 跑双胞胎前必须先下载解压 rare_share 三个 zip（demo/llama_pubmedqa_rare.sh:3-6），否则 `load_dataset` 静默返回空列表（L149-151 只 log error），最终产出 0 条样本。
2. `doc_path` 带 `process/` 前缀时脚本会剥前缀重试（L176-182），工作目录必须在仓根。
3. pubmed 的"内部名 pubmedqa、落盘名 pubmed"错位要记牢，注册表与脚本变量两边名字都对不上。
4. mmrait 图片目录名 train/val 与输出文件名 train/test 是两套命名（L12-15），读 select_true.py:83-88 目录判定时务必对齐。
