# 10 · seeds 五域与 benchmark 数据：AgentFlow 的燃料库

> 所属仓库：OpenDCAI/AgentFlow（图谱 909 节点/1857 边）。synthesis 线吃 seeds 造 QA（第 07 篇），infer/trajectory 线吃 benchmark 跑评测（第 09 篇）。本篇盘点这两个数据目录的全部家底：17 颗种子、四份基准、一份文档解析产物，以及数据里藏着的坑。

## 一、角色定位

**seeds/ 是"造数据的原料"**：五域 17 条记录，每条 `{content, kwargs}` 两字段（pipeline.py:263-268 强制校验）。content 是探索起点（一句话任务或整份文档大纲），kwargs 附带路径类参数（如 ds 的 `seed_path` 指向 CSV 目录）。

**benchmark/ 是"考题"**：三份 jsonl 共 22 题（doc 7+rag 10+web 5），每题带标准答案；doc 域另附整份文档解析产物。ds 域基准**缺席**（ds_infer.json 引用的 `benchmark/ds_benchmark.jsonl` 不存在，见第 09 篇）。

两者规模都很小——这不是生产数据集，是**跑通流水线的演示/开发数据**。真实规模数据在文档注释里写得明白：要接 MMLongBench-Doc、DocBench 等公开基准（README.md:224-239 的成绩表都是这些大基准的）。

## 二、内部结构

### seeds 五域逐家底

**seeds/doc/**——1 条记录（seeds.jsonl 44523 字符），content 是一整份 PDF 解析出的**大纲 XML**（`<Outline><Section section_id=...>` 层级结构），kwargs.seed_path 指向 `seeds/doc/seed/2210.02442v1/`。该目录是 DocDancer 解析产物全家桶：`2210.02442v1.json`（结构化解析，145KB）+ `outline.xml`（大纲，45KB）+ `all_content.xml`（全文，130KB）+ `data.pkl` + `figures/` + `page_images/` + `tables/`。种子 content 里忠实转录了论文首页字符串 `arXiv:2210.024442v1 [cs.CV] 5 Oct 2022`（Making Your First Choice: 冷启动推荐系统论文）——注意这串 9 位 ID 本身疑似原文档水印数字重复（正常 arXiv ID 是 8 位），属于从 PDF 无脑拷贝的痕迹；目录名用的则是 `2210.02442v1`。

**seeds/ds/**——4 条记录全指向同一 `seed_path: seeds/ds/seed`，内含**星型三表**：`users.csv`（user_id/user_name/department/signup_date）、`products.csv`（product_id/product_name/category/unit_price）、`orders.csv`（order_id/user_id/product_id/quantity/order_date），orders 的 user_id/product_id 外键挂另两表，每表 20 行数据。外键齐整，天然出多表 join 题（ds_config.json 的 synthesis_tips 就要求"At least 1 question must involve multi-table joins (3+ tables)"——但星型只有两张事实表可 join，3+ 表 join 意味着 users+orders+products 三表全上）。种子 content 一条泛化指令（"Analyze the data in the provided CSV files"）+ 三条具体分析题（东欧 vs 西欧奖牌榜对比等——**内容与 CSV 的电商用户/订单域完全无关**，是典型"种子文案与数据不配套"的遗留）。

**seeds/GUI/**——5 条记录（注意 `wc -l` 只报 4，最后一条无换行符），全是 VM 桌面操作叙事："open file manager, create a folder, and rename a file"、"open a terminal, run a basic command"、"use a web browser to visit a local or internal page" 等。kwargs 全空——GUI 沙箱配置不走种子。

**seeds/rag/ 与 seeds/web/**——两文件 `diff` 为空：**逐字相同的 4 条**（Python programming language / Machine learning / Natural language processing / Deep learning frameworks），全是"起始实体"型种子，不带 kwargs。rag 靠沙箱的 RAGBackend 知识库消解、web 靠 websearch API 消解——同一实体种子在两条管线里长出不同的轨迹树，这正是合成线设计者留的对照实验：**种子恒定，工具域决定轨迹形态**。

### benchmark 四份（实存三份）

**rag_benchmark.jsonl**——10 条常识问答（task_001-010：法国首都/莎士比亚/化学符号/二战结束年……）。混着两道**零跳题**：光速 299792458 与 sqrt(144)=12 根本不需要检索，参数知识直接可答——对 RAG agent 基准而言是污染项（模型不调工具也满分，拉高 baseline）。

**web_benchmark.jsonl**——5 条（web_001-005）：东京人口（"approximately 14 million"——答案带模糊限定词）、Python 首发年、OpenAI CEO "as of 2024"（**时效题**，答案随时间腐化）、最高楼、PyTorch 实现语言。数量最少、时效坑最多。

**doc_benchmark/**——结构最重的域。`Input/doc_benchmark.jsonl` 7 条任务（task_001-007），字段九个：task_id/only_question/question/doc_type/answer/evidence_pages/evidence_sources/answer_format/kwargs。三个关键设计：

1. **7 题共指一文**：kwargs.seed_path 全部指向 `Input/0b85477387a9d0cc33fca0f4becaa0e5/`（一份 "NAVAL MEDICAL RESEARCH AND DEVELOPMENT" 文档，doc_type 标 Administration/Industry file，32 张页图+41 张插图）——一次解析、多题复用，MMLongBench-Doc 官方模式。
2. **"三视图"同文档**：该文档目录提供同一内容的三种表示——`outline.xml`（大纲视图，question 里嵌的就是它）、`all_content.xml`（全文视图）、`page_images/`+`figures/`（视觉视图，doc:read 工具按页取图）；外加 `0b85...e5.json`/`data.pkl` 两份结构化表示。doc 后端按需取用，评测侧则配 **LasJ/F1/Acc 三指标族**（rollout/core/evaluator.py:181-184）从三个口径打分。
3. **question 双字段**：`only_question` 是裸题干（"Who is the commanding officer in the first figure on the second page?"），`question` 是**拼装好的完整题面**——大纲 XML 全文+"Answer the following question based on the content of the document:"+题干。评测时 question 直接喂 LLM judge。

题型覆盖刻意：答案格式 answer_format 三种（Str/List/Int，task_005 答案是 Python 列表字符串 `['Walter Gwenigale', 'Fatorma Bolay', 'Vernon Graham']`）；**两道 Not answerable 题**（task_002/004，answer 就是字面 "Not answerable"，evidence_pages 空）——考模型"知不答"的能力；证据页数从单页（[2]/[1]/[7]）到五页跨跳（task_006 的 [2,4,5,14,15]）难度递增。

**MMLongBench prompt md**——评测口径的"宪法"在 `projects/DocDancer/eval/LasJ_prompt_for_MMLongDocBench.md`（113 行）：judge 按两级规则判 YES/NO——Rule 1 直接答案匹配（语义等价即对）、Rule 2 引用匹配（预测只给引用时，引用内容含答案也算对）；专设 "Not Answerable" 处理节（标准答案为 Not answerable 时，预测说"不可答"或指出原因或改写问题后正确作答都算 YES，硬答算 NO）。rollout/core/evaluator.py:419-447 的 `_load_prompt` 用四段 fallback 路径定位它（绝对路径→相对→上级目录），找不到直接 FileNotFoundError。同目录 `prompt_for_answer_extraction.md`（34 行）是答案抽取模板。

## 三、外部连接

- **synthesis 线**：五域 seeds.jsonl 是 configs/synthesis 八配置里 `seeds_file` 的目标（GUI/text2sql 两处断链见第 07/09 篇）；种子进 pipeline 后由 `generate_source_id`（pipeline.py:33-36）算 md5 指纹成 source_id。
- **rollout 线**：benchmark jsonl 是 configs/infer 与 configs/trajectory 的 `data_path` 目标；doc 任务的 kwargs.seed_path 被沙箱 doc 后端用来定位文档解析产物。
- **DocDancer 项目**：seeds/doc 与 doc_benchmark 的文档目录格式同构（json/outline/all_content/pkl/figures/page_images 六件套），都是 DocDancer 解析器的输出（第 06 篇）；evaluator 的两份 prompt md 也寄居在 projects/DocDancer/eval/ 下——**rollout 核心代码跨目录依赖 projects/ 子项目的静态文件**。
- **MMLongBench-Doc 上游**：LasJ prompt 与三指标口径复刻官方实现（evaluator.py:31-33 注释"official"），doc_infer.json:27 的 `MMLongBench-Doc_LasJ` 即此。

## 四、数据流

种子侧（造数据）：

```
seeds/doc/seeds.jsonl (大纲XML种子)
   └─ content 塞进 sampler 的 exploration prompt (sampler.py:269)
      → doc-search/doc-read 工具在沙箱 doc 后端查 0b85.../2210.02442v1 文档
      → 轨迹树 → QA 对 (results/ds_synthesized_qa/)
```

基准侧（考模型）：

```
doc_benchmark.jsonl 一条任务
   → rollout runner: question(含大纲) 作为首轮 user message
   → 模型调 doc_search/doc_read → 最终答案
   → evaluator: metric=MMLongBench-Doc_LasJ
      → 读 projects/DocDancer/eval/LasJ_prompt_for_MMLongDocBench.md
      → judge(messages=[prompt, Question/Answer/Prediction]) → YES/NO
   → 按题聚合 acc；换 F1/Acc 口径再跑
```

## 五、设计决策（含批判）

**做得好的**：①doc 域基准的设计水平明显高于 rag/web——Not answerable 负例、三种 answer_format、证据页标注、五页跨跳题、一文档多题复用，是个像样的基准切片；②rag/web 同种子对照是便宜而有效的能力探针；③LasJ prompt 的两级匹配规则+NA 专门节把"引用也算对""拒答也得分"这些灰色地带写死了，评测可复现；④ds 星型三表麻雀虽小外键齐全。

**要批判的**：

1. **规模是玩具级**：17 种子/22 题，除 doc 域外撑不起任何统计结论（web 5 题，一题就是 20 个百分点）；ds 域基准干脆缺失。README 的大表格成绩全部来自外部大基准，本仓数据只是烟雾测试。
2. **rag 基准混入零跳题**（光速/平方根）：这两题考的是参数记忆不是检索，作为 RAG agent 基准是负资产。
3. **ds 种子与数据域错位**：种子文案谈"东欧西欧奖牌榜"，CSV 里是电商订单——合成出的题若真按文案方向走会在数据里撞空。
4. **rag/web 基准答案无出处锚**：web_001 "approximately 14 million" 这种答案没有来源页/检索时间戳，web 基准的时效腐化（CEO as of 2024）不可审计。
5. **evaluator 跨目录依赖 projects/DocDancer/eval/ 的 md**：把 rollout 核心的评测资产放在另一个子项目里，四段 fallback 路径（evaluator.py:426-443）本身就是设计欠账的补丁——删掉 projects/ 目录 doc 评测就瘸。
6. **GUI seeds 尾行无换行符**（5 条只显 4 行）：靠 `wc -l` 做计数的脚本会少数一条。

## 六、新人提示

- **加一颗种子**：往对应域的 seeds.jsonl 追加 `{"content": "...", "kwargs": {...}}`；ds 域必须带 `seed_path`（沙箱靠它找 CSV），doc 域的 content 直接放文档大纲 XML。
- **自建 doc 基准的正道**：用 DocDancer 解析 PDF 得到六件套目录 → 放 benchmark/doc_benchmark/Input/<hash>/ → jsonl 里每题 kwargs.seed_path 指过去，evidence_pages 手工标，answer_format 按答案形态填 Str/List/Int。
- **验数据完整性**：`python -c "import json;[json.loads(l) for l in open('benchmark/rag_benchmark.jsonl')]"` 一行就能抓 JSONL 断行；GUI 域别信 wc -l。
- **跑 doc 评测前**：确认 `projects/DocDancer/eval/LasJ_prompt_for_MMLongDocBench.md` 在位（evaluator.py:426 四段路径之一命中），且 evaluator 三件套（evaluator_model_name/api_key/base_url）已填——doc_infer.json:30 的 `sk-` 是假 key。
- **想扩 rag/web 基准**：删掉两道零跳题再扩，并给 web 题附检索日期；否则评测数字没有纵向可比性。
- **对照实验的现成素材**：rag/web 同种子已经摆好，跑完 synthesis 后 diff 两域产出的 trajectories.jsonl，能直观看到"工具域如何塑造轨迹形态"——这是理解整条 synthesis 线设计意图的最快途径。
