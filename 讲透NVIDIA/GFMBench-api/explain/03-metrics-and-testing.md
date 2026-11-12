# 03 · 指标体系与测试金字塔：BaseMetric 十七子 + 四层测试防线

> 锚点以 `gfmbench_api/metrics/`（L04 层 19 节点）与 `tests/`（L10 层 19 节点）为准，行号经源码逐条核实。

## 一、角色定位

指标库与测试套件分别占据图谱 L04 与 L10，是基准的**度量衡**与**质检线**。指标侧 17 个具体类全部继承 `BaseMetric`（`base_metric.py:23`），由 `metrics/__init__.py:18-34` barrel 统一汇出，五族分布：分类 4（Accuracy/MCC/AUROC/AUPRC，`:18-21`）、回归 2（PearsonR/R²，`:22-23`）、嵌入相似度 4（代表嵌入 cosine×2 + L2×2，`:30-33`）、SNV 位置级 2（按变异位点抽位向量的 cosine，`:24-25`）、LLR 系 5（整序列 ΣlogP 似然比×2 `:28-29` + masked token 似然比×2 `:26-27` + 预测均值似然比×1 `:34`）。测试侧四层金字塔（`tests/README.md` 规范表）：unit（零网络零 GPU）→ e2e 冒烟（零网络）→ download（真下载）→ heavy（真模型真基线），逐层加权成本、逐层收窄验证面。

## 二、内部结构

**BaseMetric 是教科书级模板方法**。用法契约写在 docstring（`:26-40`）：`reset()` 归零 → 逐 batch `calc()` 存最小中间量 → `get_final_results()` 聚合。`calc()`（`:55-74`）做统一前置检查：任一位置参数为 None 即一次性告警并跳过（`:67-71`，`_none_warned` 标志防刷屏），干净输入才委托给子类 `_calc_impl`。这一个小设计把"模型不支持某输出通道"（适配器返回 None）与"指标返回 None"（报告里 NO_RESULTS）无缝焊在一起——能力降级链路的最后一环。子类要实现的只有三个抽象：`_calc_impl`（`:101`）、`get_final_results`（`:120`）、以及 `name` 抽象属性（`:134-147`）。**`name` 即结果字典键**：`SumProbsLLRAUROC.name` 返回 `"sum_probs_llr_auroc"`（`sum_probs_llr_auroc.py:43-45`），任务层 `base_gfm_supervised_classification_task.py:143` 的 `{metric.name: metric.get_final_results()}` 与报告 CSV 的 metric 列名全部由它供给——改 name 字符串等于改对外 API。

以 `SumProbsLLRAUROC`（`sum_probs_llr_auroc.py:22-81`）看典型实现：`_calc_impl`（`:47-69`）先断言概率落在 [0,1]（`:50-53`），沿序列维求和得每序列对数似然（`:57-58`），作差成 LLR（`:61`），**取负**（`:65`）——因为 LLR 越低越致病、sklearn 要求高分对准正类，这个符号约定是读 LLR 族代码的第一道坎；只存 LLR 分数与标签两个小数组（`:68-69`），内存与 batch 数线性。`ClassificationAccuracy`（`classification_accuracy.py`）同理：argmax 成预测、逐 label 算 accuracy 后宏平均。SNV 位置级指标则多一步索引：`snv_variant_effect_cosine_sim_auprc.py:51` 的 `_calc_impl` 接收 `variant_snv_indices/reference_snv_indices`，按位抽出变异位点处的嵌入向量，归一化后逐对算 cosine（`:93-99`）——这就是 `sequence_pos_to_prob_pos` 位置映射的最终消费端。静态工具 `_reshape_classification_inputs`（`base_metric.py:76-99`）把单标签/多标签概率统一成 `[samples, labels, classes]`，二值多标签自动补 `1-p` 维（`:90-92`），四个分类指标共用。

**测试金字塔四层**：
- **unit 两人**：`test_caching_utils.py` 11 个用例（`:46-220`：全命中跳过/部分命中只补缺/批内去重/禁用旁路/clear 失效/容量为 0/容量满停写保读/tensor dtype 保真/元组槽位还原/额外参数分键/变长嵌入补零）；`test_sampling_utils.py` 12 个用例（确定性、分层比例、多目标覆盖、稀有类最低覆盖、非法参数抛错）。注意：**README 自称 "Thirteen tests"（13 例），源码实测 11 个 `def test_`——文档计数漂移，以源码为准**。
- **e2e 冒烟**：`test_smoke.py` 六测试锁四类任务的指标键集合（`:31-52` 三组常量）、报告往返（`:97-115`）、缺方法降级（`:118-130`，`types.MethodType` 把 `infer_sequence_to_labels_probs` 替换成恒返 None 的 lambda，断言四分数全 None 而非崩溃）。
- **download**：`test_download.py:93` 以空目录参数化遍历 TASK_REGISTRY（除 vepeval_clinvar），`:117` 验证 GUE 下载幂等。
- **heavy**：`test_heavy.py` 双测试共一套 DNABERT2 sanity 配置（linear probe、3 epochs、`--disable_safe_model_call`，argv 组装在 `:107-131`）。

## 三、外部连接

指标库被任务基类双向耦合：分类基类 import 四分类指标并实例化（`gfmbench_api/tasks/base/base_gfm_supervised_classification_task.py:107-112`）；零样本基类挂六通用指标（`base_gfm_zero_shot_task.py:110-117`）、SNV 基类追加四指标（`gfmbench_api/tasks/base/base_gfm_zeroshot_snv_task.py:57-66`）；回归基类用 PearsonR/R²。测试侧的 conftest 体系是三明治结构：**根 `tests/conftest.py`** 注册 `--heavy-data-root` 选项（`:11-21`）并用 `pytest_collection_modifyitems` 给 `test_heavy_update_baseline` 默认打 skip（`:24-40`，只有按名显式调用才执行——防止日常回归误覆盖基线）；**`tests/e2e/conftest.py`** 提供 MockGFMModel 与夹具；`fixture_tasks.py` 提供三个只吃本地 CSV 的任务类。`test_smoke.py:24` 甚至直接 `from tests.e2e.conftest import MockGFMModel`——conftest 里的类被当普通模块导入，这是 `tests/__init__.py` 空文件存在的理由（目录必须是包）。

## 四、数据流

**MockGFMModel（`tests/e2e/conftest.py:49-127`）是纯鸭子类型 mock**——不 import `BaseGFMModel`，却实现协议全部推理方法。它的输出是精心设计的确定性函数：分类概率固定 0.75/0.25 交替（`:71-75`，保证 accuracy 可预测）；代表嵌入对奇数下标整体 `+= 2.0`（`:99-100`），使 fixture 里 label=1 的样本在嵌入空间可分——**cosine/L2 指标由此能断言非 None 且有意义**；masked 概率 0.7/0.6、奇数行变异概率翻成 0.3（`:119-122`），让 masked-LLR 指标同样可分。`fixtures_root`（`:34-41`）每个测试用 `shutil.copytree`（`:40`）把 `tests/fixtures/data/` 整树拷进隔离 tmp 目录——测试对夹具的任何写入互不污染。

夹具数据两族五文件：`gue_promoter_all/` 三件套 train/dev/test.csv（`sequence,label` 两列、32bp 合成序列、各 8 行），消费者是 `GuePromoterAllTask` 与 `test_smoke`；`fixture_variant/` 两件套 train/test.csv（`variant_sequence,reference_sequence,label` 三列、第 16 位单碱基替换、8 行），一个数据集喂三个夹具任务类（`fixture_tasks.py:67/94/120`：有监督 variant、零样本 SNV、零样本 indel）——**SNV_POSITION=16（`:97`）与 CSV 里替换位精确对齐**，位置级指标的测试才成立。

heavy 层数据流：`test_heavy.py:181-205` 跑真基准 → `_assert_all_auroc_metrics_are_finite`（`:74-95`，按族谱推断每任务应有的 AUROC 键）→ 与 pinned 基线比对（`baseline_utils.py:72-105`，`MetricDiff` dataclass `:27-34` 记 task/metric/expected/actual/abs_diff/atol，缺失 actual 判 inf 差）。基线路径由 `_baseline_path`（`:98-104`）动态命名：模型名洗成安全 slug 后拼 `f"{safe}_sanity_baseline.csv"`（`:103`）——换模型跑 heavy 只需放一个对应命名的 CSV（如 `ntv3_100m_sanity_baseline.csv`），零代码改动；基线本体 `tests/fixtures/dnabert2_sanity_baseline.csv` 共 112 行数据（task,metric,expected,atol 四列，atol 统一 0.005）。

## 五、设计决策

**流式累积而非攒全量**：所有指标只存中间量（预测/分数/标签），`get_final_results` 才调 sklearn——AUROC 这类全局指标可以流式算，是因为 ROC 只需逐样本分数；分类断言概率和为 1 放任务层逐 batch 做（`gfmbench_api/tasks/base/base_gfm_supervised_classification_task.py:129-136`），让错误尽早暴露在最小现场。

**Mock 双轨制的分层意图**：conftest 的 MockGFMModel 是**行为 mock**（确定性但语义合理，能撑起指标断言）；教程 `add_new_model_tutorial.ipynb` 的 RandomMockModel/SimpleNTv3Model 是**教学 mock**，且用了 monkey-patch 手法——先在独立 cell 写裸函数 `def infer_sequence_to_sequence(self, ...)`，再 `SimpleNTv3Model.infer_sequence_to_regression = infer_sequence_to_regression` 挂到类上（cell 44）。两个类各挂一套同名 `infer_*`（RandomMock 在 cell 10-20，SimpleNTv3 在 cell 34-44），一节一个方法、随写随挂，把"协议=7 个方法名"这件事变成可逐步执行的教程叙事。生产代码里别学这个写法（IDE 不可见、重构地狱），但读教程时要知道这是刻意的教学体。

**基线更新的显式门槛**：`test_heavy_update_baseline` 默认 skip（根 conftest `:24-40`），必须 `pytest tests/e2e/test_heavy.py::test_heavy_update_baseline` 按名执行——覆盖 112 行 pinned 数字是高危操作，pytest 钩子做成"写权限默认收回"。missing baseline 时 regression 测试直接 `pytest.fail` 并附生成命令（`test_heavy.py:186-191`），错误信息即操作手册。

**atol 双轨**：`test_heavy.py:52` 的 `DEFAULT_ATOL = 0.005` 管写基线时的默认列值；`baseline_utils.py:76` 的 `default_atol=0.02` 只在基线 CSV 缺 atol 列时兜底。容忍度语义：跨硬件复跑 0.005 已够紧，0.02 是给历史基线的宽限。

## 六、新人提示

- 加新指标四步：建文件继承 BaseMetric → 实现 `_calc_impl/get_final_results/name` 三件 → `metrics/__init__.py` 登记 → 在对应任务基类的指标列表里挂上并配 arg_keys。`name` 一旦发布就是稳定 API，起名前先看报告 CSV 里现有键的命名惯例（全小写+下划线+族前缀）。
- 测试 selector 速查：零网络快验跑 `pytest tests/unit tests/e2e/test_smoke.py`；改任务族谱后必跑 smoke（指标键集合断言会抓漂移）；改执行链后跑 heavy regression；只有显式点名才允许 update_baseline。
- 给 heavy 换模型：先跑 `test_heavy_update_baseline` 生成 `{slug}_sanity_baseline.csv`，人工 review 112 行数字的合理性再提交——基线是"pin 住已知行为"，不是"pin 住正确行为"。
- MockGFMModel 的奇偶下标设计（label=1 样本可分）是夹具协同的关键：改 fixture CSV 的 label 分布或 mock 的 `reprs[1::2] += 2.0` 任一处，smoke 的非 None 断言都可能翻车，要动就一起动。
- README 的测试计数（"Thirteen tests"）与源码（11 例）已漂移，写文档或 CI 统计时以 `grep -c "def test_"` 为准；这也提醒：本仓测试的权威描述在 README 表格的"检查什么"列，数量列仅供参考。
