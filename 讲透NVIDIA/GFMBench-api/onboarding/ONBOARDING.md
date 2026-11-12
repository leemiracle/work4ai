# GFMBench-api 新人入门指南（ONBOARDING）

> 基于知识图谱（279 节点 / 677 边 / 10 层 / 15 步 tour，commit `a80bde0f`）与源码逐锚核实撰写。

## 一、项目定位：GFMBench 是什么

GFMBench-api 是**基因组基础模型（GFM）标准化基准接口**——一套评测中间件：不训练任何模型，而是把 DNABERT-2、Nucleotide Transformer、HyenaDNA、Evo2 这类 DNA 长序列基础模型接到统一评测任务上，实现跨模型可比。论文 *GFMBench-API: A Standardized Interface for Benchmarking Genomic Foundation Models*（bioRxiv 2026，doi `10.64898/2026.02.19.706811`，`README.md:5`）。

三条设计主轴，读代码前先记住：

1. **任务与模型彻底解耦**：互不感知，只通过推理方法名协作（鸭子类型优先于继承）；
2. **核心依赖极简**：`basic_requirements.txt:1` 仅 16 行 11 包（torch/datasets/huggingface_hub/pyfaidx/biopython 等），模型专属依赖按需另装；
3. **两类任务两种协议**：有监督（先微调后评测）与零样本（直接评预训练能力，数据统一为 variant/ref 序列对）。

对应图谱 **step-01「项目全景」**：先读 `README.md`（552 行，22 任务总表+运行命令）、`basic_requirements.txt`、`THIRD_PARTY_NOTICES.md`。

## 二、技术栈与代码版图：10 层图谱导读

Python ≥3.10 + PyTorch；数据面走 HuggingFace Hub 与 UCSC hg38 参考基因组（`fileutils.py:319` `ensure_reference_genome`）。代码根两处：`gfmbench_api/`（库）与 `usage_examples/`（CLI+适配器+微调器），`tests/` 独立成层。10 层自底向上：

| 层 | 名称 | 要点 |
|---|---|---|
| L01 | 项目文档与依赖声明 | README/NOTICES/requirements（step-01） |
| L02 | 通用工具与日志 | `utils/` 八件套：fileutils 下载物化、preprocutils 序列预处理、sampling_utils 分层限样、caching_utils 推理缓存、logutils、lrb_local 绕 datasets≥4.0（step-07/08/09） |
| L03 | 任务抽象协议 | `tasks/base/` 全部基类，`base_gfm_model.py:22` 与 `base_gfm_task.py:23` 两大根（step-02） |
| L04 | 评测指标库 | 17 指标类全继承 `metrics/base_metric.py:23`（step-05/06） |
| L05 | 结果聚合报告 | `benchmark_report.py:22` BenchmarkReport（step-12） |
| L06 | 有监督具体任务 | 13 类：GUE×3 + LRB×4 + VariantBenchmarks×6（step-10） |
| L07 | 零样本具体任务 | 10 类：BEND×2/BRCA1/ClinVar×2/LOL-EVE/LRB-OMIM/songlab/TraitGym×2（step-11） |
| L08 | CLI 入口与微调组件 | `run_benchmark.py` + `trainers/`（step-13） |
| L09 | 模型适配器示例 | `sanity_models/` 6 适配器 + 教程笔记本（step-14） |
| L10 | 测试与夹具数据 | unit/e2e/download/heavy 四类 + fixtures（step-15） |

**关键版图事实（源码甄别）**：L06 有 13 个有监督任务类，但 `run_benchmark.py:71` TASK_REGISTRY 只登记 22 项——**LRB CAGE 回归（`lrb_cage_task.py:32`）未注册**，因 `run_benchmark.py:387-390` 示例微调器只支持 classification。注册表 = 有监督 12（全分类）+ 零样本 10。

## 三、核心架构：任务族谱与指标契约

### 3.1 任务族谱（step-02→04）

```
BaseGFMTask (base_gfm_task.py:23)
├─ BaseGFMSupervisedTask (base_gfm_supervised_task.py:24)
│  ├─ …ClassificationTask (base_gfm_supervised_classification_task.py:34)
│  │  ├─ …SingleSeqTask (base_gfm_supervised_single_seq_task.py:25) → (sequence,label)
│  │  └─ …VariantEffectTask (base_gfm_supervised_variant_effect_task.py:25) → (variant,ref,label)
│  └─ …RegressionTask (base_gfm_supervised_regression_task.py:28) → binned 回归
└─ BaseGFMZeroShotTask (base_gfm_zero_shot_task.py:37)
   ├─ …SNVTask (base_gfm_zeroshot_snv_task.py:31)         → 追加 cosine/masked-LLR 四指标
   └─ …GeneralIndelTask (base_gfm_zeroshot_general_indel_task.py:24) → 钩子置空
```

`BaseGFMTask.__init__`（`base_gfm_task.py:26-67`）解析 task_config（batch_size/max_num_samples/cache_size 等），**构造时即下载数据建三份 dataset**（:67）。最值得精读 `_safe_model_call`（:102）：任务调模型一律经它包裹，方法缺失或抛异常返回 None 元组而非崩溃——能力探测与指标自动跳过全靠这层。分类基类在 `base_gfm_supervised_classification_task.py:108-111` 实例化 Accuracy/MCC/AUROC/AUPRC，逐 batch 断言概率和为 1（:129），结果字典按 `{metric.name: …}` 动态组装（:143）。

零样本侧 `base_gfm_zero_shot_task.py:111-114` 直接挂 SumProbsLLR 与嵌入相似度共六个通用指标，:122 用 SequenceInferenceCache 缓存参考序列推理；SNV 子类 `base_gfm_zeroshot_snv_task.py:58-64` 追加四指标并以 abstractmethod 强制实现变异位点定位（:84）；indel 子类把钩子固化为空实现（`base_gfm_zeroshot_general_indel_task.py:38-52`）——**钩子默认全开、indel 层显式关掉**是理解零样本指标组合的钥匙。

### 3.2 指标契约（step-05/06）

17 个指标全继承 BaseMetric（`metrics/__init__.py:17-34` 统一汇出），五族：分类 4、回归 2、嵌入相似度 4、SNV 位置级 2、LLR 系 5。契约四件套：`reset`/`_calc_impl`/`get_final_results`/`name` 抽象属性。`calc()` 模板方法（`base_metric.py:55-74`）：任一位置参数为 None 告警一次并跳过——模型"不支持某输出通道"与"指标返回 None"由此打通。`name` 即结果字典键（`classification_mcc.py:41-43` 返回 `"classification_mcc"`；`sum_probs_llr_auroc.py:43-45` 返回 `"sum_probs_llr_auroc"`），报告 metric 列名直接来自它。`_reshape_classification_inputs`（`base_metric.py:76`）把单/多标签概率统一为 `[samples,labels,classes]`，二值多标签自动补 `1-p` 维。

## 四、run_benchmark 执行链（step-13）

`usage_examples/run_benchmark.py` 主入口，链路（行号核实）：

1. **初始化**：`init_logger` → `set_seed`（:233；:27-28 设 CUBLAS 确定性）→ `BenchmarkReport(csv_path)`（:288，CSV 存在则续写）；
2. **模型守门**：:296-297 对 Evo2 硬校验，未加 `--linear_prob` 直接 ValueError（配套 `evo2_model.py:94` `force_linear_probe=True`）；
3. **懒加载**：`get_model_class`（:143-150）按 MODEL_REGISTRY（:97，7 条目）走 `importlib.import_module`（:147）——不装 Evo2 依赖也能跑 DNABERT2，这是懒加载的全部意义；
4. **实例化任务**：:337-341 遍历 TASK_REGISTRY（22 项，`--exclude_tasks` 可跳过），构造即下载数据；
5. **任务循环**（:364 起）：每任务 set_seed 复位 + **重建模型**（:379，任务间零状态泄漏）→ 有监督走 `GFMFinetuner.fine_tune()`（:433），零样本直接用原模型（:437）→ `task.eval_test_set`（:442）→ `report.add_scores`+`save_csv`（:449-450，**每任务即存盘**，中断不丢结果）。

微调器 `trainers/finetuner.py:27`：`only_proj_layer=True` 只训投影头（:126-127），False 全模型（:129）；优化器 Adam/AdamW/SGD（:108-115）。骨干+投影头由 `trainers/model_wrapper.py:27` `GFMWithProjection(BaseGFMModel)` 包装成单一模型交回评测。

## 五、模型接入契约：BaseGFMModel 与鸭子类型（step-14）

`base_gfm_model.py:22` 定义协议，**7 个推理方法中 6 个抽象、1 个可选**：

| 方法 | 行号 | 用途 |
|---|---|---|
| `infer_sequence_to_labels_probs` | :39 | 序列→分类概率（监督分类） |
| `infer_sequence_to_regression` | :59 | 回归输出（**非抽象**，默认 None） |
| `infer_sequence_to_sequence` | :75 | 三元组（逐位概率/逐位嵌入/代表嵌入），零样本 LLR 与 cosine 的数据源 |
| `sequence_pos_to_prob_pos` | :117 | 输入碱基位→输出 token 位（BPE/k-mer/自回归三类 tokenizer 差异的统一解法，:138-153 四例说明） |
| `infer_masked_sequence_to_token_probs` | :165 | masked 预测变异/参考碱基概率（SNV masked-LLR 专用） |
| `infer_variant_ref_sequences_to_labels_probs` | :213 | variant/ref 对→分类概率 |

**鸭子类型是官方立场，落地是混合风格（源码甄别）**：6 适配器中 3 个显式继承 BaseGFMModel（`dna_bert_model.py:27`/`ntv3_model.py:145`/`isolated_mock_model.py:204`），3 个只实现方法名不继承（`dna_bert2_model.py:26` `class DNABERT2Model(nn.Module)`、`hyena_dna_model.py:31`、`evo2_model.py:79` 普通类）——任务侧一视同仁，因为全走 `_safe_model_call` 按名探测。两种姿势都合法；教程 `add_new_model_tutorial.ipynb` 从零实现 RandomMockModel 走鸭子路线。

三个代表适配器覆盖三种骨干形态：DNABERT2（HF MaskedLM+BPE）、Evo2（Megatron 并行+NGC checkpoint，:63 起单卡初始化）、HyenaDNA（长上下文，注册表 cap 8192）。`isolated_mock_model.py` 示范进程隔离：每次 infer_* spawn 独立 worker 解释器（:29-30），证明协议可跨环境边界。

## 六、添加新任务 / 新模型的最短路径

**新任务四步**：①在 `tasks/concrete/` 建文件继承对应基类；②实现数据集构建（直接复用 `fileutils.py:42` `ensure_hf_hub_file` / :136 `ensure_verified_download`（SHA-256 原子下载）/ :182 `materialize_csv_splits_from_zip`）；③实现元信息方法（字段清单见 `base_gfm_task.py:146-163` docstring）；④`run_benchmark.py:71` 登记一行。最薄样板 `gue_promoter_all_task.py:46`（300bp 二分类，约 140 行）；零样本可抄 traitgym 双子。

**新模型三步**（照教程走）：①建 `sanity_models/my_model.py`，实现你要参与的方法（不支持返回 None，指标自动跳过），**必须实现 `get_hidden_dim()` 与 `eval()`**（run_benchmark:385/:441 直接调用）；②MODEL_REGISTRY 登记 module/class/max_length；③首跑加 `--sanity_check_mode`（每数据集限 100 样本，:330-332）。BPE 类模型必须认真实现 `sequence_pos_to_prob_pos`（返回 -1 表不可定位），否则 SNV 位置级指标全失效。

## 七、测试金字塔（step-15）

四层（`tests/README.md` 有规范表，前两层零网络零 GPU）：

- **unit**：`test_caching_utils.py:46` 起 12 用例（命中/去重/禁用/容量/类型保真）；`test_sampling_utils.py:14` 起 12 用例（确定性分层/最低覆盖/非法参数）；
- **e2e 冒烟**：`test_smoke.py:55-118` 六测试，用 `tests/e2e/conftest.py:49` **MockGFMModel——纯鸭子类型 mock 不继承 BaseGFMModel**，固定 0.75/0.25 概率保证可断言；配 `fixture_tasks.py:67/94/120` 三夹具任务 + `tests/fixtures/data/` 本地 CSV，零网络走通四类任务+报告+缺方法降级；
- **download**：验证各任务自动下载物化；
- **heavy 回归**：`test_heavy.py:181` 用 DNABERT2（:51）跑全部任务 sanity 模式，与 `tests/fixtures/dnabert2_sanity_baseline.csv`（112 行数据+atol 容差）逐项比对；基线刷新须显式点名 `test_heavy_update_baseline`（`tests/conftest.py:24-40` 收集钩子默认跳过）。

## 八、上手清单与避坑

**半天路径**：读 README 任务总表（step-01）→ 精读 step-02 两基类与 `_safe_model_call` → 按 step-05/06 过 BaseMetric+一个具体指标 → 跑 `pytest tests/unit tests/e2e/test_smoke.py` → `--sanity_check_mode` 跑 IsolatedMock 全链 → 按 step-10/11 对照族谱精读两个具体任务 → 过教程笔记本。

**已知问题甄别清单（均源码核实）**：
1. `logutils.py:396-421` `get_log_prefix` **if/else 疑似写反**：:407 `if log_path is None` 走查 handler，:414-415 `else: return "unknown"`——**显式传 log_path 反而返回 "unknown"**，与 docstring 相反。当前仓内无调用方属休眠 bug，复用前必修；
2. `bend_vep_disease_task.py:62-63` 与 `bend_vep_expression_task.py:62-63`：docstring 写 1048576bp，实际 `return 512`——窗口按 512 截断，引用任务能力以代码为准；
3. padding 字符不一致：`preprocutils.py:74` `pad_sequence` 越界补 **'N'**（模糊碱基），:140 `pad_sequence_centered_variant` 补 **'P'**（非标准字符）——两条 pad 路线喂给 tokenizer 的越界语义不同；
4. `traitgym_complex_task.py` 与 `traitgym_mendelian_task.py` 复制孪生仅 5 处差异（:127/:129/:152/:155/:163），改公共逻辑两边都要改；
5. `brca1_task.py:324` `_run_predict_evo2` 不走 Python API 而拼 `predict_evo2` CLI 子进程（:336，:358 `subprocess.run`）——要求宿主另装 evo2 CLI，与适配器进程是两套环境；
6. 注册表不含 LRB CAGE 回归（见第二节）；Evo2 必须 `--linear_prob`；
7. MockGFMModel 未实现 `infer_sequence_to_regression`，冒烟不覆盖回归链路，回归改动需手工验证。

**图谱阅读顺序**：step-01→02（契约）→03/04（族谱）→05/06（指标）→07/08/09（数据缓存）→10/11（实例）→12/13（聚合 CLI）→14（适配器）→15（测试）——先契约后实例，约两小时建立全图。
