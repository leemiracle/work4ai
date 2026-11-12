# 06 · DocDancer PDF 线：mineru vendored、三脚本管线与 eval() 注入面

## 角色定位

`projects/DocDancer/` 是论文 **DocDancer: Towards Agentic Document-Grounded Information Seeking**（arXiv 2601.05163，Qwen3-4B/30B-A3B 骨干，MMLongBench-Doc 与 DocBench）在仓内的落地产物，负责两件事：**PDF 预处理**（PDF_preprocess/ 三脚本 + vendored mineru_vl_utils，把 PDF 变成 doc 工具吃的 XML 种子）与**官方口径评测**（eval/ 的 eval_score.py 与两份 MMLongBench prompt，被 03 篇的 evaluator 动态挂载）。这条线是 AgentFlow doc 场景的上游工厂与下游裁判。

## 内部结构

**mineru_vl_utils vendored 包**（PDF_preprocess/mineru_vl_utils/，24 个 Python 文件，0.1.15 版收编）：三层结构——

- `mineru_client.py`（约 500 行）：门面 `MinerUClient`（L263）内部 L356 调 `new_vlm_client` 建底层引擎；`MinerUSamplingParams`（L17）定制采样参数；`MinerUClientHelper`（L82）提供 layout 解析、`post_process`（L183）、批量与 aio 全家桶（L192-260）。包根 `__init__.py` 用 `__lazy_attrs__` 表 + 模块级 `__getattr__`（L21）懒导出 MinerUClient/MinerUSamplingParams/MinerULogitsProcessor——vLLM 等重依赖只在真正取用时加载（03 篇 7 处懒加载先例之一）。
- `vlm_client/`：`base_client.py` 的工厂 `new_vlm_client`（L143）支持**五后端**——`http-client`（远端 OpenAI 兼容服务）、`transformers`（本地 HF）、`mlx-engine`（Apple）、`vllm-engine`（离线 LLM 类）、`vllm-async-engine`（异步引擎），每个分支各自函数内 import（http_client L155 起），选哪个后端就只加载谁的依赖。统一异常三件套 UnsupportedError/RequestError/ServerError 与跨后端一致的 SamplingParams。
- `post_process/`：`__init__.py` L38-68 的主管线做三类事——表格块 `convert_otsl_to_html`（L46-47，OTSL 线性化表格转回 HTML）；公式块过**五连修复器**（L20-26）：`try_match_equation_left_right` → `try_fix_equation_double_subscript` → `try_fix_equation_eqqcolon` → `try_fix_equation_big` → `try_fix_equation_leq`，分别治 \left\right 配对、双重下标、\eqqcolon、大括号、\leq 类 VLM 高频公式病；最后 `_add_equation_brackets`（L29-35）补 `\[ \]` 包裹，equation_block 一律丢弃（L60-61）、PARATEXT_TYPES 页眉页脚等旁文可配置放弃（L10-17）。logits_processor/ 另有 v0/v1 两版 no_repeat_ngram。

**三脚本管线**（PDF_preprocess/）：

1. `1_run_pdf_extract.py`（212 行）：`MinerUPDFProcessor`（L27）用 vLLM 起 MinerU2.5-2509-1.2B（模型名 L31）、`logits_processors=[MinerULogitsProcessor]`（L33），`MinerUClient(backend="vllm-engine", vllm_llm=self.llm)`（L36-39）复用同一引擎——布局检测与内容抽取两步共享显存。**关键坑在 import 解析**：L14 `from mineru_vl_utils import MinerUClient`——脚本与 vendored 目录同层，`python 1_run_pdf_extract.py` 时 sys.path[0] 是脚本目录，**必然命中仓内 vendored 副本而非 pip 安装的 mineru-vl-utils**（即便装了）。这既是可复现性的优点（版本钉死），也是「改了 pip 包不生效」类困惑的根源。
2. `2_process_extracted_data.py`（488 行）：VLM 图像描述器——L21 起的巨型 PROMPT（角色/图像类型分析/组件细节/文本转写/纯客观五段要求）驱动 VLM 为每张图表生成 alt 文本，ProcessPoolExecutor 多进程并跑。
3. `3_get_outline_and_root.py`（302 行）：`DocReader`（L26）读 data.pkl、按标题深度栈构建 `<Document>` XML 树——outline.xml 与 all_content.xml 的最终形态在此定稿，正是 02 篇 doc 工具的输入。`run_pipeline.sh`（154 行）串三脚本。

**eval/ 官方评测**：`eval_score.py`（217 行）——`eval_score(gt, pred, answer_type)`（L115）按类型分支：Int/Float/Str/None 走数值与 ANLS（Levenshtein 相似度，L5 起）路径；**List 分支是危险点**——L137-138 `if isinstance(gt, str) and gt.startswith("["): gt = eval(gt)`，L141-142 同样 `eval(pred)`：把方括号开头的字符串直接喂给 Python `eval()` 做字面量反序列化。`pred` 来自模型输出经 LLM 抽取，`gt` 来自 benchmark JSONL——两者都不是受信输入，`eval()` 在这里是**任意代码执行面**（"[__import__('os').system(...)]" 形态即可穿透）。`show_results` 的 L178-179 再对 evidence_pages/evidence_sources 各 eval 一次，把 benchmark 文件内容也纳入暴露面。`eval_acc_and_f1`（L160-173）算 acc 与含 "Not answerable" 分支的 F1。两份 prompt：`prompt_for_answer_extraction.md`（答案抽取，03 篇 evaluator L534 消费）与 `LasJ_prompt_for_MMLongDocBench.md`（LLM 判官规则——Rule 1 直接答案匹配、Rule 2 引文-only 匹配，判定语义等价输出 YES/NO）。

## 外部连接

上游：benchmark/doc_benchmark/Input 的 doc_benchmark.jsonl（doc_infer.json 的 data_path）+ seeds/doc 种子目录。下游：3 号脚本的 XML 产物经 seeds 流入 doc:search/doc:read 工具；eval/ 被 rollout evaluator 经 importlib 挂载（evaluator.py L522-524 `spec_from_file_location("eval_score", ...)` + exec_module），LasJ prompt 被 `_mmlongbench_doc_lasj`（L413）读取；synthesis 线的 QA 合成同样以这套种子为素材。HuggingFace 侧对应 OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DocDancer 模型与 AgentFlow-DocDancer 数据集（README 链接）。

## 数据流

PDF→分数全链：原始 PDF → 脚本 1（MinerU 布局+抽取，OTSL/公式原文）→ 脚本 2（图表 alt 文本、pickle 化中间态）→ 脚本 3（outline.xml + all_content.xml + figures/tables/page_images）→ seeds/doc + seed.jsonl（kwargs 带 seed_path）→ rollout doc 场景（agent 用 doc 工具检索阅读）→ 最终答案 → evaluator：LLM 按 extraction prompt 抽取 → 格式归一（Int/Float/Str/List）→ eval_score 打分（List 型触发 eval()）→ acc/F1 汇总。

## 设计决策（含批判）

- **vendored 24 文件锁版本**：MinerU 客户端与其公式修复器迭代快、且 1 号脚本要传自定义 logits_processor，收编保复现；代价同 05 篇——上游修复不达，且 shadowing 使「升级 pip 包」的直觉操作无效。
- **五连公式修复器 + OTSL 转换**是整条线最扎实的工程：针对 VLM 输出的系统性错误模式逐一对症，而非笼统统一次 LLM 重写——确定性、可测试、零成本。新人学后处理管线设计应精读 post_process/__init__.py 的 68 行。
- **`eval()` 反序列化是必须钉版的安全债**：官方脚本的「简便」在 agent 评测语境被放大——模型输出是半个攻击者。修法一行：`json.loads` 失败再 `ast.literal_eval`，语义覆盖全部现有用例（列表字面量）而消灭执行面。在 evaluator 经 exec_module 挂载的链路上，这个问题不属于「上游仓库自己的事」。
- **引擎复用**（vllm_llm 直传 client）：省一份显存副本，是好设计；但把 MinerUClient 的生命周期与脚本进程绑定，长跑服务化需要重构为引擎池。
- **评测三层分工**（抽取 LLM / 规则 eval_score / 判官 LasJ）：抽取与判官分离使「模型答对了但格式怪」不至于误杀——MMLongBench 官方设计，本仓忠实搬运并补了 gpt-4o-mini 默认抽取器（evaluator.py L574）。

## 新人提示

1. 跑预处理按序执行三脚本即可，但先确认 GPU 与 poppler（pdf2image 依赖）就位；1 号脚本起 vLLM 引擎需数分钟，卡在 "Initializing vLLM Engine" 是正常不是死机。
2. 改了 pip 的 mineru-vl-utils 没效果？先看本篇的 shadowing 结论——你改的必须是 vendored 副本。
3. doc 工具检索不到内容时，用 xmllint 打开 all_content.xml 对照 section_id 是否真的生成——3 号脚本的标题深度栈对畸形 PDF 偶尔产出空 section。
4. 任何把 eval_score.py 用于不可信 benchmark 的场景，动手前先把 L138/L142/L178/L179 的四处 `eval()` 换成 `ast.literal_eval`，这是性价比最高的一个补丁。
