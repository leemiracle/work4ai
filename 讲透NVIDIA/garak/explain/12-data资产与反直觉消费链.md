# 12 · data 资产与反直觉消费链

## 一、角色定位

`garak/data/` 是随包发行的评测资产库：约 40 个子目录/文件，从 cloze 语料（book_cloze.tsv 等）到 profanity 词表到 payload 组。入口 `garak/data/__init__.py` 的 `LocalDataPath`（:29）继承 pathlib.Path，`ORDERED_SEARCH_PATHS`（:32-35）定义**用户 data_dir 优先、包内 data 兜底**的两级查找——restricted Path 只对已存在资源放行，越界拼路径直接抛 GarakException（:46-54）。本篇核心是四条"看名字猜不到消费者"的链与两个零消费判定。

## 二、内部结构

资产三形态：① 平铺文本/TSV（book_cloze_80.tsv、nyt_cloze.tsv、potter_cloze.tsv、guardian_cloze.tsv、slurprompts.jsonl、ldnoobw-en.txt、profanity_en.csv、tags.misp.tsv、typology_payloads.tsv、inthewild_jailbreak_llms.json、graph_connectivity.json、primality_testing.json、senator_search.json…）；② 带专属目录的包（harmbench/、fitd/、xss/、payloads/、cas/、calibration/、detectors_eval/、beast/、confidence_intervals/ 等）；③ 可执行资产（payloads/*.json 既是数据又是攻击载荷本体）。装载中枢是 `garak/payloads.py`：Director._scan_payload_dir 用 glob `**/*.[jJ][sS][oO][nN]` 扫描（:138），PAYLOAD_SCHEMA（:19-41）以 jsonschema 校验 garak_payload_name/payload_types/payloads 三必填，PayloadGroup._load（:53-135）加载成功即向报告写 `payload_init` 记录（:106-127，含文件大小与 mtime 溯源）。

## 三、外部连接（四条反直觉链+两个判定）

**链 1：harmbench → fitd。** data/harmbench/harmbench_prompts.txt 的唯一消费者是 `probes/fitd.py:249`——**仓内没有 harmbench probe**。FITD（FakeInstructThenDestroy 式红队）在 `_create_init_attempts`（fitd.py:236-253）把这些 prompts 当种子，random.sample 抽 initial_prompt_count 条生成初始攻击轮。数据集名 ≠ probe 名。

**链 2：cloze 语料 → leakreplay。** 四份 *_cloze.tsv 全部进 `probes/leakreplay.py`（:160, :176, :194, :210, :227, :243, :260, :276）：书/纽约时报/卫报/哈利波特四域 × Cloze/Complete 两形态 × Full/Lightweight 两量级（NonFullMixin 混入裁剪，:170-174），评测训练数据泄漏的完形填空法。

**链 3：xss/ → web_injection。** data/xss/ 8 项资产（domains/var_names/injection_markers/injected_actions/encodings/link_display_texts 六词表 web_injection.py:289-306 + 两类 prompt 模板目录 :309-315）全部被 `probes/web_injection.py` 消费——probe 已从 xss 改名 web_injection（fixer/20250908_xss_rename.py:8-27 迁移同步改配置），**数据目录名保留旧名**，目录与 probe 命名解耦。

**链 4：payloads → exploitation 双端。** probes/exploitation.py:73 的 DEFAULT_PARAMS 默认 `payload_name: python_code_execution`，detectors/exploitation.py:78, 119 两处 `garak.payloads.load("python_code_execution")` 同名取载荷——**同一 payload 组同时喂 probe（造题）与 detector（验伤）**。勘误级发现：该文件 git 索引在册（8d1259e 快照 new file）但**工作区已删**（git status ` D garak/data/payloads/python_code_execution.json`），运行 exploitation probe 时 PayloadGroup._load 将 FileNotFoundError→PayloadFailure——盘上 16 个 payload 组与插件默认值的断链。

**零消费判定 1：confidence_intervals.pkl。** grep 全仓（garak/ tests/ tools/）无任何 .pkl 路径引用，判定为外部工具产出的数据存档而非运行时依赖（图谱不挂消费边是正确口径）。**零消费判定 2：beast/suffixes.txt 为空占位**——真实对抗后缀由 resources/beast/beast_attack.py 运行时生成，probes/suffix.py 只引用生成器不读该文件。

## 四、数据流

payload 全生命周期：Director 扫描建 name:path 索引（类级缓存 payload_list）→ probe __init__ 里 `garak.payloads.load(name)`（exploitation.py:75-84：取 payloads 逐条 format 进 template 生成 prompts，顺带继承 payload 的 intent 字段）→ 运行期 payload_init 记录随报告落盘 → digest 的 payloads 区（report_digest.py:79-84 以 pprint 摘要呈现）。数据覆盖流：用户在 data_dir 放同名文件即覆盖包内版（detector_metrics.py:22-27 注释明确利用此机制让自测 Se/Sp 优先）。

## 五、设计决策

1. **路径对象受限化**（data/__init__.py:31-52）：把"资源必须存在"从运行时 OSError 前移到路径构造期，probe 代码可大胆 `/` 拼接。
2. **数据目录名不随 probe 改名**（xss 案例）：数据是历史积累，probe 名是 API 表面——解耦避免每轮改名搬数据。
3. **payload schema 只校验结构不校验内容**：恶意载荷本身就是要"毒"，jsonschema 只管字段齐不齐（payloads.py:23-27）。
4. **intent 字段内嵌 payload**（payloads.py:99-101 + exploitation.py:76-78）：载荷自带攻击意图编码，意图链无需 probe 二次声明。
5. **随机抽样种子化于运行时**（fitd.py:252-253 random.sample，默认 initial_prompt_count=5 见 :58）：harmbench 全集仅抽 5 条起评，控制评测成本。
6. **零引用资产留仓**（confidence_intervals.pkl）：分析工具的输入输出共存于 data/，属"档案"而非"依赖"——图谱消费边判据应为代码引用而非文件存在。

## 六、新人提示

加新资产的标准动作：文件入 data/<族>/ → probe 里 `data_path / "族" / "文件"` 引用 → 若是 payload 组再过 PAYLOAD_SCHEMA 三必填 + 意图编码（S 系）。三个坑：① 找某数据集的消费者**别按数据名猜 probe 名**，直接全仓 grep 文件名——本篇四条链全都名不副实；② 本地 clone 若曾清理过大文件，exploitation 类 probe 跑前先 `ls garak/data/payloads/ | grep python` 验默认载荷在位（本仓快照即缺）；③ 改 xss/ 目录下文件会同时影响 web_injection 全部 6 个 probe 的生成面，模板目录（full_uri/concat_prompt_templates）与词表是乘法关系。
