# garak ONBOARDING —— NVIDIA LLM 漏洞扫描器全景导览

> 知识图谱基线：1690 节点 / 4052 边 / 14 层 / 16 步 tour / validator 0 issues / fingerprints 861 文件 @ commit `8d1259ef`（v0.17.1.pre1）。
> 本文所有行号锚均在源码逐一核实（2026-11-08），锚格式 `文件:行号`。

---

## 1. 项目定位：LLM 界的 nmap

garak 是 NVIDIA 开源的 **LLM 漏洞扫描器**（README.md:1 自我定位 "LLM vulnerability scanner"）。README.md:5 一句话说透本质："garak checks if an LLM can be made to fail in a way we don't want"——探测幻觉、数据泄漏、提示注入、越狱（jailbreak）、毒性生成等 40+ 类弱点，并给出量化报告。若你知道 `nmap` 或 Metasploit，garak 对 LLM 做的就是同类的事。

**三大核心概念构成一个扫描矩阵**：

| 概念 | 职责 | nmap 类比 | 数量 |
|---|---|---|---|
| **probe 探针** | 定义并执行某类攻击面（产出提示、绑定判定器） | NSE 漏洞脚本 | 45 模块 / 132 探针类 |
| **generator 生成器** | 被测模型接入层（OpenAI/HF/REST/NIM…） | 扫描目标 | 26 模块 / 24 家后端 |
| **detector 探测器** | 对模型输出打分判定是否"失守" | 指纹/版本判定 | 32 模块 |

矩阵的运行时编排靠 **harness**（`probe × detector × generator` 织成执行矩阵）与 **evaluator**（结果汇聚），产物是 `.report.jsonl`，再由 analyze 管线转 digest、供 garak-report 前端展示——一条从 CLI 命令到可视化报告的完整数据流闭环。

配套资产：`garak-paper.pdf`（学术论文）、`PROJECTS.md`（衍生生态）、`AGENTS.md`（AI agent 协作开发规范——NVIDIA 也在用 agent 参与开发本仓）、`docs/`（Sphinx 159 件）。版本与打包：`pyproject.toml:7` `version = "0.17.1.pre1"`（与 `garak/__init__.py:3` 的 `__version__` 一致），CLI 入口 `pyproject.toml:229` `garak = "garak.__main__:main"`。

与"红队 LLM 框架"的差异化：garak 的 probe 不是散装 prompt 集合，而是带 **tier 分级**（garak/probes/_tier.py:9）、**MISP 标签**、**intent 意图编码**（对齐 CAS trait typology）的工程化插件体系；其判定也分层——从子串匹配到 HF 模型再到"模型当法官"（ModelAsJudge），可校准、可算置信区间。

**矩阵语义再拆一层**。probe 决定"问什么"：它负责构造攻击提示（静态词表、数据载荷或自适应算法实时生成）、声明配套 detector（谁最懂这次输出算不算失守）；generator 决定"问谁"：同一个 probe 无差别作用于本地 GGUF、云端 API 还是 NVIDIA NIM 微服务，这正是"扫描器"而非"评测脚本"的关键——目标可替换；detector 决定"怎么判"：返回 0-1 浮点而非布尔，为校准与置信区间保留了统计空间。三者任意组合，评测结果按 probe 分组呈现为"攻击成功率"（ASR），再对齐校准基线算 z 分数——所以 garak 报告能回答的不是"过没过"而是"这个模型在这类风险上比典型模型差多少"。

**意图体系是 0.17 世代的新骨架**：probe 的 `intent` 属性（对齐 `garak/data/cas/trait_typology.json` 的 trait 编码）让"攻击面"从 MISP 标签的平面枚举升级为可组合、可屏蔽、可按意图动态装配探测器的层级分类（intentservice 支持子意图递归展开与 fail-closed 校验）。前端的技术×意图矩阵（techniqueIntentRollup）就是它的展示面。理解了 probe→intent→detector 这条线，就看懂了 garak 从"探测器集合"向"风险分类学驱动扫描"的演进方向。

## 2. 架构总览：14 层双维分层

图谱 14 层是"**管线职责 × 资产工程面**"双维组织：L01-L08 是扫描管线的执行纵深（从入口到离线分析），L09-L14 是支撑这根管线的资产与工程面（资源词表、数据、前端、文档、测试、CI）。

| 层 | 名称 | 文件数 | 职责一句话 |
|---|---|---|---|
| L01 | 入口与核心运行时 | 17 | CLI 三件套+配置装载+插件骨架+Attempt 总线+报告落盘 |
| L02 | probes 探测族 | 45 | 132 个探针类，Mixin 组合扩展 |
| L03 | detectors 探测器族 | 32 | 从子串匹配到 LLM 判决的判定层 |
| L04 | generators 生成器适配 | 26 | 24 家后端，OpenAICompatible/HFCompatible 双复用基类 |
| L05 | buffs 与攻击算法库 | 17 | 提示变形+GCG/AutoDAN/BEAST/TAP 四大自适应攻击 |
| L06 | 评测编排与执行外围 | 11 | harnesses/evaluators/intent·lang 双服务 |
| L07 | fixer 迁移族与 intents | 17 | 配置版本迁移框架+意图分类体系 |
| L08 | analyze 分析管线 | 17 | digest/AVID/校准/置信区间/专题分析 |
| L09 | 运行时公共资源与词表 | 23 | garak.core.yaml 基座+plugin_cache+匹配评分工具 |
| L10 | data 数据资产 | 128 | 探测弹药库：payloads/DAN 模板/毒性词表/校准基线 |
| L11 | garak-report 报告前端 | 133 | React+Vite+KUI 报告站 |
| L12 | docs 文档体系 | 159 | Sphinx+automodule 全插件 API 参考 |
| L13 | tests 测试体系 | 182 | 按包镜像的 pytest 全家桶 |
| L14 | 工具链·CI·项目治理 | 54 | 数据集离线构建+14 条 GitHub Actions |

**枢纽节点（fanIn top）** 勾出真正的骨架：`garak/__init__.py`（fanIn 169）、`garak/_config.py`（165）、`garak/attempt.py`（155）、`garak/probes/base.py:Probe`（96）、`garak/_plugins.py`（91）——配置、数据总线、插件加载是全仓被依赖最重的三根柱子。

**227 条 inherits 边构成星号链**（图谱实测）：`Probe`（94 个直接子类）→ `Detector`（26）→ `Generator`（22）→ `StringDetector`（17）→ `Configurable`（7）→ `LangProvider`（5）→ `PackageHallucinationDetector`（5）→ `OpenAICompatible`（5）。这张继承星图就是理解 garak 插件生态的钥匙：四个根基类（Probe/Detector/Generator/Buff 全部继承 garak/configurable.py:24 的 `Configurable`，获得统一的配置注入能力），加上两类"复用放大器"（StringDetector/OpenAICompatible——一个让词表探测器零成本量产，一个让 OpenAI 协议后端零成本量产）。

数据总线视角：`Attempt` 对象（garak/attempt.py:173）贯穿全管线——probe 铸造它、generator 回填 outputs、detector 写入 detector_results、evaluator 汇聚、harness 把 `as_dict()`（attempt.py:268）逐行写进 `.report.jsonl`（garak/harnesses/base.py:279-281）。

**怎么用这张图导航**：4052 条边里，imports 边回答"改这个文件会牵连谁"（改 attempt.py 慎重，155 入边全仓最敏感的运行时文件之一）；inherits 边回答"这类插件的家族谱系"（找某探针的兄弟实现，沿继承边一跳即达）；data 资产边（payloads/detectors 数据装载）回答"这个探测器到底拿什么词表在判"。新人接到任一任务，先在图上定位目标文件所属层，再看该层的对外接缝（probes 的接缝是 Attempt 流、detectors 的接缝是 detect 返回值、generators 的接缝是 generate_call），改动就不会越界。

## 3. 核心运行时：CLI、配置、插件骨架与 Attempt 总线

**入口三件套**。`python -m garak` 经 `garak/__main__.py`（全 14 行，纯引导）进入 `garak/cli.py:39` 的 `main()`——793 行的巨型函数，覆盖 argparse 全家（cli.py:67 的 parser 描述即 "LLM safety & security scanning tool"）、run.spec 装配、插件选择、命令分发与进程编排。`garak/command.py` 是配套命令层（419 行），NOTES 甄别指出其风格特征：**全部重依赖放在函数体内 import 的延迟导入**（如 cli.py:529 `from garak.interactive import interactive_mode`、cli.py:586 `from garak.resources import fixer`），压 CLI 启动开销并规避循环导入。

**cli.py 主流程**（按行号走读）：

1. `parse_cli_plugin_config`（cli.py:9）解析 `--generator_option_file` 等插件级配置；
2. args 归仓：逐参数判断归属 `system/run/plugins/reporting` 四桶（cli.py:396-406），不认识的进 ignored_params；
3. **run.spec 统一选型**（cli.py:413-444）：`--spec` 优先（"--spec wins"，cli.py:421-431），已废弃的 `--probes/--probe_tags/--buffs` 触发 deprecation notice（版本 0.15.1.pre1，cli.py:420）并经 `legacy_selection_spec` 映射到 spec；detectors 不入 run.spec，保留独立 legacy 面（cli.py:409-411）；
4. 并行/ bootstrap 参数校验：`worker_count_validation`（cli.py:449，上限对齐 `system.max_workers`）与 bootstrap 三参数校验（cli.py:473-494）；
5. 命令分发（cli.py:528-648）：`--interactive`、`--plugin_info`、`--list_probes/detectors/buffs/generators`、`--list_config`、`--fix`（cli.py:585，调 fixer.migrate 改写配置，cli.py:615/628）、`--report`（cli.py:641，转 AVID 报告）；
6. **扫描主链**（cli.py:651-776）：`_check_selection`（cli.py:678，区分 rejected 与 inactive——全模块插件 inactive 是 issue #830 的已知态）→ `_selection.resolve_spec` 解析（cli.py:708）→ intent 轴存入 transient（cli.py:713-716）→ `ThresholdEvaluator(_config.run.eval_threshold)`（cli.py:740）→ `_plugins.load_plugin` 装载生成器（cli.py:744）→ `command.start_run()`（cli.py:758）→ **按 detector_spec 空否分流**：空则 `probewise_run`（cli.py:764，按 probe 推荐探测器跑），非空则 `pxd_run`（cli.py:768，probe×detector 全展开）→ `end_run()`。

**配置中枢 `_config.py`**（487 行）。模块**导入即执行**默认配置装载；`GarakSubConfig`（_config.py:51）/`TransientConfig`（:63）构成配置对象体系，`BuffManager`（:56）管理 buff 实例池；`load_config`（:354）分层加载（系统/用户/运行目录/CLI）并多层 dict merge+lock；`_map_legacy_selection`（:236）做旧选择键迁移；HTTP UA 统一设置（:304-333）。配置基座是 `garak/resources/garak.core.yaml`（42 行）——settings_files 的起点。

配置优先级从低到高：内置默认 → `garak.core.yaml` → 用户级 `garak.site.yaml` → 运行目录 yaml → `--config` 传参 → CLI 单参数。这套分层让"组织基线策略 + 项目覆盖 + 单次实验微调"可以叠加而不互相踩。**插件参数的注入通道**同样分层：`Configurable._load_config`（configurable.py:72）会从 `_config.plugins.<类型>.<模块>.<类>` 里捞本插件专属配置，再叠 CLI 的 `--generator_options` JSON——这就是为什么每个插件类只需声明 `DEFAULT_PARAMS` 类属性（如 garak/generators/base.py:25、garak/detectors/base.py:42，StringDetector 还用 `dict |` 合并语法扩展基类参数，garak/detectors/base.py:200），运行时即可被四层配置覆盖，而插件代码里完全看不到配置装载逻辑。`_config.transient` 则是只存活于本次进程的运行态仓（cli_args、reportfile、active_probes、intent_spec 都寄存在此），与持久配置严格隔离。

**run.spec 语法**（`garak/_spec.py`，280 行）：一条 spec 同时描述 probes/buffs/intents 的选型与排除（如 `probes.lmrc !probes.lmrc.SlurUsage intents.S003` 的组合语义），`parse_spec_string`（_spec.py:115）/`parse_spec_file`（:142）产出结构化 spec，`legacy_selection_spec`（:258）承接旧三参数，`_selection.resolve_spec`（_selection.py:103）再对插件名、标签、tier 与 inactive 状态做消解（garak/_selection.py:25 `_resolve_plugin_paths`、:77 `_tier_of`）。spec 也是报告里的运行凭证——digest 的 header 会回显它，前端 runSpec.ts 据此展示"这次跑了什么"。

**插件骨架 `_plugins.py`**（484 行）。`enumerate_plugins`（_plugins.py:363）枚举全部 probe/detector/generator/buff/harness 类；`load_plugin`（:396）按命名空间路径动态加载（如 `generators.openai.OpenAIGenerator`）；`PluginCache`（:39）+ `_build_plugin_cache`（:165）维护 `garak/resources/plugin_cache.json`（10746 行元数据）——CI 的 maintain_cache workflow 专职保鲜，本地重建用 `tools/rebuild_plugin_cache.sh`（其 :29 用 `touch -d "2024-07-01"` 的 **mtime 欺骗**做缓存失效，比手删全部缓存精准）；`PluginProvider`（:335）做可共享插件实例的中央注册表。

**Attempt 数据总线**（garak/attempt.py，458 行）。四层结构：`Message`（:22，单条消息）→ `Turn`（:91，带角色）→ `Conversation`（:120，多轮会话）→ `Attempt`（:173，一次探测尝试的全量载体）。`Conversation.from_openai`（:157）兼容 OpenAI 消息格式；`Attempt.__init__`（:228）持有 status/prompt/probe_classname/targets/outputs/notes/detector_results/goal/seq/intent 全部状态；`as_dict()`（:268）序列化落盘。**Attempt 与源 prompt 严格 1:1**，conversations 内部按 generation 数展开多条历史（类注释 :204-214 钉版）。

## 4. probes 探测族：Mixin 组合的 132 探针军团

**Probe 基类**（garak/probes/base.py:31，继承 Configurable）定义插件属性面：`doc_uri`/`lang`（BCP47）/`tags`（MISP 格式）/`goal`（祈使句攻击目标）/`intent`（:49，对齐 `garak/data/cas/trait_typology.json` 的 trait 编码，经 `_mint_attempt` 传播到每个 Attempt）/`recommended_detector`（:51，默认 `["always.Fail"]`——不覆写就故意报错给你信号）/`primary_detector`（:53）/`modality`（:64，输入模态集）/`tier`（:68，默认 UNLISTED）。构造器内含 recommended_detector→primary_detector 的弃用迁移（base.py:87-106）。执行生命周期核心是 `probe()`（base.py:385）：产出 Attempt 流。

三个执行变体（base.py 内）：`TreeSearchProbe`（:483，树搜索多轮攻击，内部直接 `load_plugin` 装探测器并即时判定，:531/:605）、`IterativeProbe`（:691，基于上轮响应迭代）、`IntentProbe`（:846，按意图动态选探测器的探针，与 intentservice 联动）。

**探针生命周期**（`probe()` base.py:385 展开）：`generate_prompts` 构造提示 → 逐 prompt `_mint_attempt`（base.py:217）铸造 Attempt（写入 probe_classname/goal/intent/seq）→ 喂给 generator 拿 outputs → buff 后处理钩子 `_postprocess_buff`（:199）与 `_postprocess_hook`（:211）修正 → `_postprocess_attempt`（:282）收尾归一。这些钩子点是扩展探针行为的官方接缝：buff 的 transform/untransform、多轮攻击的上下文续写、以及把 targets/notes 回填进 Attempt，都挂在这条钩子链上。另有一个工程细节值得注意：探针默认并行（`parallelisable_attempts` :57 为 True），harness 层据此决定是否用进程池展开 attempts——这是 garak 大规模扫描的吞吐基础。

**Tier 分级**（garak/probes/_tier.py:9，IntEnum）：`OF_CONCERN=1`（低通过率即需上报安全/对齐团队）/`COMPETE_WITH_SOTA=2`/`INFORMATIONAL=3`/`UNLISTED=9`（:55-58）——报告侧 tbsa 分析按 tier 加权。

**Mixin 组合范式**是 probes 族的最大工程特征（94 个类直接继承 Probe，其余经 Mixin/中间基类）：

- **encoding.py**：`EncodingMixin`（:192）+ 20 个编码注入探针（`InjectBase64` :288 / `InjectHex` :355 / `InjectROT13` :428 / `InjectBraille` :461 / `InjectMorse` :511 / `InjectZalgo` :609 / `InjectLeet` :639 …全文件 23 个 class），rot13(:56)/braille(:60)/morse(:141) 等编码器内联实现；
- **latentinjection.py**：`LatentInjectionMixin`（:28）+ `TranslationMixin`（:111）+ `FactSnippetMixin`（:149）组合出翻译注入（EnFr :219/EnZh :235）、简历注入（:391）、事实片段注入（:500/:537）、LatentJailbreak（:571）、LatentWhois（:638）等；
- **leakreplay.py**：`ClozeProbeMixin`（:27）/`CompleteProbeMixin`（:100）/**`NonFullMixin`**（:143）——"Full 全量 / 裁剪版"双类模式（LiteratureClozeFull :154 → LiteratureCloze :163）；
- **web_injection.py**：`MarkdownExfilMixin`（:275）派生 markdown 图片外传/URI 注入（:369/:421）；
- **dan.py**：`DANProbeMeta` 元类（:28）自动装配模板类——`Dan_11_0`（:156）到 `Dan_6_0`（:212）、DUDE/STAN/AntiDAN、`AutoDANCached`（:352）/`AutoDAN`（:367，接 autodan 资源）、`DanInTheWildFull`（:445，在野越狱样本库）。

**ABC 中间基类**模式：packagehallucination.py:63 `PackageHallucinationProbe(ABC)` 定义"诱导模型幻觉一个不存在的包"骨架，Python(:109)/Ruby(:125)/JavaScript(:141)/Rust(:157)/RakuLand(:174)/Perl(:190)/Dart(:206) 七个生态各挂真实包索引对照。

**自适应攻击探针**（suffix.py 232 行）：`GCGCached`（:22，直接吃 `data/gcg/gcg.txt` 缓存后缀，:18 定位路径）、`GCG`（:63，运行时梯度搜索，:110-113 延迟绑定 `run_gcg`）、`BEAST`（:182，:209-219 绑定 `run_beast`）。atkgen.py:36 `Tox` 是生成式红队代表；exploitation.py:35 `JinjaTemplatePythonInjection`/:88 `SQLInjectionSystem` 覆盖利用类注入。

## 5. detectors 与 generators：判定层与接入层的双基类范式

**Detector 契约**（garak/detectors/base.py:21，继承 Configurable）：核心只有一个方法 `detect(attempt)`（:74），对 Attempt 的每条输出返回一个 `[0,1]` 浮点（1=失守）。基类族四件套：

- `StringDetector`（:197）——子串匹配，`matchstrings` 任一命中即正，最常用轻量探测器（**17 个子类**，是继承星图第四大星）；
- `HFDetector`（:82，`Detector, HFCompatible` 双继承）——挂 HuggingFace 模型打分；
- `TriggerListDetector`（:275）——从 attempt.notes 取触发词；
- `FileDetector`（:307）——文件类输出。

代表性探测器：**judge.py 是"模型当法官"**——`ModelAsJudge`（:20，`Detector, EvaluationJudge` 双继承）派生 `Refusal`（:123）与 `Jailbreak`（:176）；unsafe_content.py 是**词表探测器量产线**——`S_nlpDetox`（:12）挂 HF 模型，`SurgeProfanity`×9 / `OfcomOffensive`×5 / `LDNOOBW`（:402）/ `SlursReclaimedSlurs`（:428）全走 StringDetector+词表数据；always.py 是**控制流哨兵**——`Fail`（:13）/`Pass`（:22）/`Passthru`（:31）/`Random`（:48）；mitigation.py:243 `ModernBERTRefusal(HFDetector)` 用 ModernBERT 识别拒绝前缀；packagehallucination.py:33 `PackageHallucinationDetector(ABC)` + `PythonPypi`（:141）/`RubyGems`（:184）等按生态核对幻觉包名；promptinject.py:13 `AttackRogueString` 是 PromptInject 的配套判定。

**公共判定工具**（被各族复用）：`garak/resources/matching.py:5` `ngram_contained_match`（n-gram 容错匹配，对付模型输出的格式漂移）；`garak/resources/scoring.py:10` `aggregate`（默认 `lower_quartile` 聚合多次 detector 分数——保守取下四分位）。

**判定层的设计哲学**：探测器刻意做"薄"——一个类只回答一种失败信号，复杂语义靠组合（any/always/mitigation 控制流探测器做逻辑包装，judge 做语义兜底）。这带来两个工程红利：一是探测器可以独立评测（`data/detectors_eval/` 与 `analyze/detector_metrics.py` 就是给探测器本身算 precision/recall 的——判定器也需要被判定）；二是 PxD harness 的全笛卡尔模式才有意义：同一批 probe 输出喂给 N 个探测器，横向对比谁的召回更稳。新人写自定义探测器时最常见的错误是把阈值逻辑塞进 detect()——阈值属于 evaluator（ThresholdEvaluator），detect() 只负责给证据强度。

**Generator 契约**（garak/generators/base.py:21）：`DEFAULT_PARAMS` 含 `temperature`（:27）等通用参数；`parallel_capable`（:39，能否并行请求）；`supports_multiple_generations`（:46-47，一次请求能否拉多条采样）；子类实现 `generate_call`（:75 签名）；基类 `generate()`（:138）管理迭代、类型检查、并行展开（multiprocessing/tqdm 分支 :161-230）。

**两大复用基类**是本层的架构看点：

1. **OpenAICompatible**（openai.py:135，492 行文件）——封装流式/重试/多模态/工具调用，派生 `OpenAIGenerator`（:421）→ `OpenAIReasoningGenerator`（:475，reasoning 模型专用）。复用者图谱实测 5 家：`GroqChat`（groq.py:11）、`AzureOpenAIGenerator`（azure.py:32）、NIM 三件套（nim.py:17 `NVOpenAIChat` → :113 `NVOpenAICompletion` → :139 `NVMultimodal` → :226 `Vision`——NVIDIA 推理微服务的完整模态线）。
2. **HFCompatible**（huggingface.py）——`Pipeline`（:46，本地 transformers pipeline）、`Model`（:367）、`LLaVA`（:505，视觉语言）。

其余接入面：通用协议 `RestGenerator`（rest.py:31，含 :459 `_MtlsAdapter` mTLS 支持）与 `WebSocketGenerator`（websocket.py:27）；聚合器 `LiteLLMGenerator`（litellm.py:68，一个口接百家）；本地函数 `function.py:54 Single`；云原生 `BedrockGenerator`（bedrock.py:39）、`AnthropicGenerator`（anthropic.py:14）；**测试空转族 test.py**——`Blank`（:14）/`Repeat`（:27）/`Single`（:40）/`Nones`（:59）/`Lipsum`（:72）/`ReasoningLipsum`（:112）/`BlankVision`（:193），让 CI 不依赖外部 API 也能全链路跑探针。

## 6. attacks 资源库：buffs + 四大自适应攻击 + PromptInject 数据引擎

**Buff 是"提示扩编器"**（garak/buffs/base.py:18，继承 Configurable）：`transform`（:69）把编码/小写/改写施加到任意探测提示，`untransform`（:75）把模型输出还原，`buff()`（:79）串起两段。现有 buff 族：encoding/lowercase/paraphrase/low_resource_languages——任意 probe × 任意 buff 正交组合，是矩阵之外的第三维。

**四大自适应攻击算法**（garak/resources/ 下，均为"论文级攻击的工程化移植"）：

| 攻击 | 算法 | 关键入口 | 搜索机制 |
|---|---|---|---|
| GCG | Greedy Coordinate Gradient | generate_gcg.py:20 `run_gcg` | attack_manager.py:64 `sample_ids_from_grad` 按梯度采样 token 候选；:114 `AttackPrompt` / :489 `GCGAttack` 两级状态机 |
| AutoDAN | 遗传搜索 | autodan.py:78 `autodan_generate` | genetic.py:61 `autodan_ga` / :120 `autodan_hga`（层次遗传）；:288 `gpt_mutate` 用 LLM 做变异算子；:172 轮盘赌选择；:547 `get_score_autodan` 适应度 |
| BEAST | Beam-EScape Attack SucceSSfulness | beast_attack.py:338 `run_beast` | :56 `_get_perplexity` 困惑度正则项；:107 `_score_candidates` 候选打分；:175 `_sample_tokens`；:266 `_attack` 主循环 |
| TAP | Tree of Attacks with Pruning | tap_main.py:276 `run_tap` | :76 `TAPConversation` 状态；:118 `AttackManager(EvaluationJudge)` 树节点评估+剪枝 |

**重要甄别**（NOTES-DIGEST 钉版）：`garak/data/beast/suffixes.txt` 是**空占位文件**——真实后缀由 beast_attack.py 运行时生成，garak/probes/suffix.py:182 的 BEAST 探针只在运行时调用 `run_beast`，不预置数据。

**PromptInject 数据引擎**是"数据即代码"的样板：`garak/resources/promptinject/prompt_data.py`（690 行）几乎全是字面量字典/列表（:15-20 定义 `attack_instruction`/`attack_rogue_string`/`attack_scoring`/escape/delimiter 等攻击维度键）——tree-sitter 对这种纯赋值模块提取不到函数，故图谱节点以 file 级为主；`prompting.py` 的 `_product_from_iterables`（:207）把各维度做**笛卡尔积**批量生成攻击提示，`build_prompts`（:264）是总装入口。这解释了 promptinject 探针为什么"一个类覆盖数百变体"：类只是维度组合器的壳，攻击面全在数据维度里，改一个 escape 长度就批量变体。

**四算法的共性设计**值得新人细品：它们都不直接继承 Probe，而是作为**可被任意探针调用的函数库**存在（suffix.py 的 GCG/BEAST 探针是官方接线示范），攻击对象（generator）、判定（内置 judge 或候选打分）都由调用方注入——算法与插件体系解耦，同一套 GCG 可以扫任意后端模型。代价是这几个模块自带 torch 重依赖，所以全部延迟导入；也因此 nightly CI 与 test_linux 才需要对 GPU/环境做专门编排。

攻击库与 probes 的接线方式统一为**延迟绑定**：suffix.py:110-113 在构造时才 `from garak.resources.gcg import run_gcg`，BEAST 同理（:209-219）——攻击算法的重依赖（torch 等）只在真正选用时才进内存。

## 7. 评测与报告：harness 执行模型 → report.jsonl → digest → 前端

**Harness 执行模型**（garak/harnesses/base.py:82 `Harness`）。核心是 `run()`（:159）主循环，每个 probe 一轮：

1. `_modality_match`（:293 实现，:201 调用）核对 probe 与 generator 的输入模态，不匹配直接跳过；
2. `probe.probe(model)`（:213）拿到 Attempt 流；
3. **IntentProbe 特殊分支**（:218-275）：普通 probe 对全部 detector 逐个 `_run_detector`（:136）；IntentProbe 则先收集 attempts 的 intent 集，再按 `intentservice.get_detectors(intent)`（:246）动态装配探测器、按 intent 分桶跑子集，并补发 plugin_cache 条目（:274，保持 report.jsonl 的插件清单完整）；
4. 每个 attempt 标记 `ATTEMPT_COMPLETE` 并逐行写 `.report.jsonl`（:277-281，`json.dumps(attempt.as_dict())`）；
5. `evaluator.evaluate(attempt_results)`（:286）汇聚。

两个具体 harness：**ProbewiseHarness**（probewise.py:18，`run` :30）——按每个 probe 自带的 primary/extended detectors 跑，是默认路径（CLI 未给 detector_spec 时，cli.py:763-766）；**PxD**（pxd.py:22，`run` :23）——probe×detector 全笛卡尔展开，用于横向对比探测器（cli.py:767-774 分流点）。外围服务在 harness 装载时拉起：`_initialize_runtime_services`（base.py:28）——intent 意图标注服务（intentservice.py:180 `load`，:85 `_expand_intent_spec` 子意图递归展开+fail-closed 校验 :125，:354 `get_intent_stubs` 三格式 stub 供给）与 language 翻译服务（langservice.py:67 `load`，:105 `get_langprovider` 正反向；langproviders 三实现 local/remote/base:137 `LangProvider`）支撑跨语言探测。

**Evaluator 判定汇聚**（garak/evaluators/base.py:28 `Evaluator`）：`test()`（:53）是打分阈值判定（`ZeroToleranceEvaluator` :481 零容忍 / `ThresholdEvaluator` :491 可调阈值，CLI 默认后者，cli.py:740）；`_evaluate_one_detector`（:62）逐探测器聚合；`evaluate()`（:224）总入口；`get_z_rating`（:313）给出相对校准基线的 z 分数评级，`print_results_wide`（:332）打印宽表。

**报告落盘与转换**。运行期：`command.start_run`（command.py:42）建 `garak.<uuid4>.report.jsonl`、`end_run`（:124）收尾，`write_report_digest`（:411）触发 digest。离线：`garak/report.py:15 Report` 类 `load()`（:49）回读 JSONL、`export()`（:87）转 AVID 报告（`garak/analyze/report_avid.py:16 convert_to_avid` 是其实现面）。

**analyze 管线**（17 件工具，核心是 `report_digest.py` **814 行**）：`_parse_report`（:58）解析 JSONL → `_init_populate_result_db`（:165）建 **SQLite 内存结果库**（evals 表按 probe_class/detector/评分落行，后续全部聚合走 SQL 而非重复扫 JSONL——这是 814 行能扛 7424 行报告的秘密）→ `_get_report_grouping`（:247）/`_get_group_aggregate_score`（:257）做分组聚合（probe 按模块名/MISP tag 归组，:200-221）→ `_compute_technique_intent_matrix`（:507）算技术×意图矩阵 → `build_digest`（:581）产出全量 digest（header :121 + 分组 + probe 明细 + detector 明细 + 校准视图 :479）→ `build_html`（:692）可直出 HTML。统计侧：`calibration.py:17 Calibration` 维护校准基线；`ci_calculator.py:67 calculate_ci_from_report` + :188 `update_eval_entries_with_ci` 把置信区间回填报告条目；`bootstrap_ci.py:90 calculate_bootstrap_ci`（底层 :12 `_bootstrap_calculation`）；`tbsa.py:60 digest_to_tbsa`（:32 `build_tiers` 按 Tier 加权的总分）；`misp.py:25 misp_report` MISP 分类视图；`aggregate_reports.py:74 main` 聚合多报告；`count_tokens.py:22` 计量。

**garak-report 前端**（133 文件：components 55/hooks 30/types 13）。技术栈 React 19 + Vite 7（package.json:2 `@nvidia/garak-report`），UI 框架以 **vendor tarball 锁定**（package.json:20 `@kui/react: ./src/assets/kui-foundations-react-external-0.504.1.tgz`，不走 registry）。数据注入是**构建期内联**：vite.config.ts:38 在打包时把 digest JSON 写成 `<script>window.__GARAK_INSERT_HERE__ = ...</script>`；运行时兜底 `window.reportsData`。消费端 `useReportData`（useReportData.ts:55，BUILD_REPORTS 常量 :20 定义构建期注入点）→ `Report.tsx:43` 页面组件 :45 解构使用。汇总工具：`runSpec.ts:26 isRunSpecObject` / :45 `runSpecTokens` 解析运行规格；`techniqueIntentRollup.ts:151 buildAxisGroups` / :220 `findNotablePairings` / :268 `buildMatrixView` 做技术×意图上卷矩阵；components/index.ts 是 55 组件的 barrel re-export。联调夹具：`garak-report/extracted_digest.json`（7424 行，真实运行 digest 抽本）。

前端与 Python 侧的契约只有一份 digest JSON：`build_digest` 的输出结构就是 `types/ReportEntry.ts` 的 TypeScript 类型镜像。这意味着改 digest 字段名是跨语言破坏性变更——CI 里 `test_report_build` workflow 用 extracted_digest.json 夹具守着这层契约。选择"构建期注入"而非"运行时 fetch"也有讲究：报告是纯静态产物，可以整包塞进 release artifacts 或任意静态托管，扫描完成即永久可看，不需要为看报告再起服务。

## 8. 新人上手：迁移族、数据资产、阅读路线与坑

**五分钟跑通**：`pip install garak` 后 `garak --model_type openai --model_name gpt-4o --spec probes.promptinject`（docs/source/usage.rst:18-19 给了按族/按类两种选型写法；默认全探针扫描，:9）。列插件用 `--list_probes/--list_detectors/--list_generators/--list_buffs`，看插件详情 `--plugin_info probes.dan.Dan_11_0`，改旧配置 `--fix`。想离线体验全链路（不烧 API 额度）：`--model_type test.Blank` 或 `test.Lipsum`——测试生成器族让 CLI→probe→detector→report 每一环都能空转走通，是新人理解数据流最快的路径。

**新探针从哪抄起**：docs/source/extending.probe.rst 是官方教程；实操上最快的模板是 encoding.py（Mixin+一个类属性表就是一个新编码探针）与 packagehallucination.py（ABC 中间基类+生态子类的"家族扩展"样板）。新 generator 抄 groq.py（OpenAICompatible 最小复用，11 行起）；新 detector 抄 unsafe_content.py 的任一 StringDetector 子类（词表+三行类体）。记住三条扩展公约：插件必须可被 `_config` 注入（继承链上挂 Configurable）、必须带 docstring（docs automodule 与 plugin_cache 的 description 都取自它，report_digest.py:54 `plugin_docstring_to_description`）、探针要声明 tier 与 intent 才能进主流报告。

**fixer 迁移族**（garak/resources/fixer/）：`Migration` 基类（__init__.py:16）+ 模块级 `migrate()`（:45）串起 11 个按日期命名的迁移脚本——`20260612_run_spec.py:32 MapLegacySelectionToSpec`（把旧 probes/buffs 选型语法统一到 run.spec，:12 `_reject_unknown_selectors` 拒绝未知选择器）是最新一次大迁移；改名系（20240628_gcg_rename/20250220_unsafe_content_rename/20250908_xss_rename/20260223_templateinjection_rename）与 `20250224_lightweight_probe_defaults.py`（批量修 14 个轻量探针默认值）；`_plugin.py:12 rename` 是通用路径改写辅助。行为锁：`tests/resources/test_fixer.py`（328 行）全量断言。

**data 资产使用法**（garak/data/，128 文件）：入口 `garak/data/__init__.py:29 LocalDataPath`——只读寻径类，限制只能指向已存在的资源文件。四类资产：①payloads 载荷库（`data/payloads/*.json`：harmful_behaviors/encoded/markdown_js/keyedprod_win10…，由 payloads.py:131 `Director` 统一 `load`/`search` :176）；②探针词表（dan 模板 14 件、xss 9 件、realtoxicityprompts 7 件、fitd/donotanswer/goat/harmbench…）；③**校准基线**（`data/calibration/` 7 件，供 analyze 层 z 分数比对）与 `data/confidence_intervals/confidence_intervals.pkl`（**甄别钉版：全仓无 .pkl 消费边，是外部工具产出的数据存档**）；④`data/cas/trait_typology.json` 人格/风险分类学（由 `tools/cas/process_policy.py` 从未入库的 trait_typology.txt 生成）。运行时资源另有 `resources/`（plugin_cache.json 10746 行、matching/scoring 工具、四大攻击算法、promptinject 引擎）。

**推荐阅读路线**（16 步 tour 的精华浓缩，每步 1-2 小时）：
README → `garak/cli.py`（main 全流程）→ `_config.py`（配置装载）→ `_plugins.py`（插件加载）→ `attempt.py`（数据总线）→ `probes/base.py` + `_tier.py` → `detectors/base.py` → `generators/base.py` + `openai.py` → `buffs/base.py` + `resources/{gcg,beast,autodan,tap}` → `harnesses/base.py`（run 主循环）→ `evaluators/base.py` → `report.py` + `analyze/report_digest.py` → `garak-report/src/`（useReportData→Report.tsx）→ 挑一个 Mixin 族精读（encoding.py 或 latentinjection.py）。

这条路线的编排逻辑是"先主干后枝叶、先契约后实现"：前五步全是 L01 层的骨架件——CLI 让你看见一次扫描的完整时序，config/plugins 让你明白"一切皆插件、一切可配置"，attempt 让你手里始终握着那根贯穿全仓的数据线；中间五步按管线的自然顺序走完 probe→detector→generator→harness→evaluator，每一步只需要理解"上一步递给我什么、我递给下一步什么"；最后三步是输出侧与一个具体攻击面的深潜。倒着读（从 data 词表倒推到 CLI）适合以"加一个检测能力"为目标的贡献者；顺着读适合以"理解扫描器设计"为目标的学习者。另一个实用建议：读 garak/harnesses/base.py:159 的 run() 时开着一次 `--model_type test.Blank` 的真实运行对照日志，两百行代码二十分钟就能在脑内建成全链路心智模型。

**工程规范与 CI**：tests/ 182 件按包镜像（probes 33/generators 30/detectors 28/analyze 12，根级 14 件含 test_main_entrypoint/test_reqs/test_docs——连文档与依赖一致性都有测试）；14 条 GitHub Actions（test_linux/macos/windows 三平台、nightly 回归、release、docs、**maintain_cache**（插件缓存保鲜）、**test_report_build**（前端构建验证）、lint/labels/stale/needs_triage/prepare_package/remote_package_install）；DCO 签核+pre-commit+pylintrc。

**已知坑与甄别（图谱批阶段钉版）**：①`tests/generators/test_generators_base.py` 仅含 SPDX 版权声明无测试体，勿当参考；②`tests/generators/test_muiltiprocessing_support.py` 文件名 muiltiprocessing 误拼是仓内原样，改名会破坏引用；③`data/beast/suffixes.txt` 空占位勿删（BEAST 运行时生成真实后缀）；④plugin_cache.json 手改无效——用 `tools/rebuild_plugin_cache.sh`（mtime 欺骗触发重建）；⑤`command.py` 的延迟导入风格意味着 grep import 看不全依赖面，追调用链要看函数体；⑥detector 分数聚合默认 lower_quartile（scoring.py:10），做对比实验时要意识到这个保守口径。

**下一步练习**：①给 `--spec probes.encoding.InjectBase64` 跑一次扫描并打开生成的 report.jsonl，逐行对照 attempt.py:268 `as_dict` 的字段；②仿照 encoding.py 的 EncodingMixin 模式写一个新编码探针（如 SHA 家族十六进制变体）；③用 `analyze/tbsa.py` 对两次扫描算 tier 加权总分并比较 z 评级；④在 garak-report 里 `npm run dev` 后换 extracted_digest.json 夹具观察矩阵图变化。

**一页总结**：garak 的全部设计可以压缩成三句话——一切攻击面是插件（probe 继承星图+tier 意图分类学），一切目标是适配器（generator 双基类复用），一切证据流经同一根数据总线（Attempt→report.jsonl→digest→前端）。把这三句话带回任何一个具体文件、任何一次代码审阅，都不会迷路。祝扫描愉快，祝每个模型都被问得哑口无言。



