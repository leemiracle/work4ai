# 02 · 任务基类族谱与双契约：BaseGFMTask 十基类 + BaseGFMModel 七方法

> 锚点以 `gfmbench_api/tasks/base/` 十文件与 `tasks/concrete/` 代表任务为准，行号经源码逐条核实。图谱 L03「任务抽象协议」13 节点 = 3 个 `__init__.py` barrel + 10 个基类模块。

## 一、角色定位

`gfmbench_api/tasks/base/` 是整个基准的**宪法层**：L03 的 13 个节点里没有一行数据下载或指标计算的具体实现，全部是抽象骨架。它同时定义了两份契约——**任务侧**（`base_gfm_task.py:23` 的 `BaseGFMTask` 族谱，规定数据集怎么建、属性怎么报、评测循环怎么走）与**模型侧**（`base_gfm_model.py:22` 的 `BaseGFMModel`，规定模型适配器必须会哪些推理方法）。两份契约互不 import 对方：任务拿到的永远是 `model: Any`（如 `base_gfm_task.py:102` 的 `_safe_model_call(self, model: Any, ...)`），模型也从不 import 任务。**解耦的落点是方法名字符串**——这是全仓鸭子类型路线的根。

族谱全景（每个类名后为定义文件与行号）：

```
BaseGFMTask (base_gfm_task.py:23)
├─ BaseGFMSupervisedTask (base_gfm_supervised_task.py:24)
│  ├─ BaseGFMSupervisedClassificationTask (gfmbench_api/tasks/base/base_gfm_supervised_classification_task.py:34)
│  │  ├─ BaseGFMSupervisedSingleSeqTask (gfmbench_api/tasks/base/base_gfm_supervised_single_seq_task.py:25) → (sequence, label, cond)
│  │  └─ BaseGFMSupervisedVariantEffectTask (gfmbench_api/tasks/base/base_gfm_supervised_variant_effect_task.py:25) → (variant, ref, label, cond)
│  └─ BaseGFMSupervisedRegressionTask (gfmbench_api/tasks/base/base_gfm_supervised_regression_task.py:28) → sequence/binned 回归
└─ BaseGFMZeroShotTask (base_gfm_zero_shot_task.py:37)
   ├─ BaseGFMZeroShotSNVTask (gfmbench_api/tasks/base/base_gfm_zeroshot_snv_task.py:31) → 追加 4 个位置级指标
   └─ BaseGFMZeroShotGeneralIndelTask (gfmbench_api/tasks/base/base_gfm_zeroshot_general_indel_task.py:24) → 钩子固化为空
```

## 二、内部结构

**根类 BaseGFMTask 是"重构造器"**：`__init__`（`base_gfm_task.py:26-67`）解析 `task_config` 六键（batch_size/num_workers/max_num_samples/disable_safe_model_call/cache_size/max_sequence_length），算出有效序列长度 `min(任务默认, 用户配置)`（`:69-85`），然后**立即**调 `_create_datasets()`（`:67`）——任务对象诞生之时数据已就位，这也是 `run_benchmark.py:337-341` 构造任务列表会触发全部下载的原因。八个抽象方法里最关键的是 `get_task_attributes()`（`:146-163`），其 docstring 规定了 12 个必需键（has_finetuning_data/task_type/classification_mode/num_labels/num_classes/output_spatiality/is_variant_effect_prediction 等）——这份 dict 就是任务向执行器自我介绍的**元信息协议**，`run_benchmark` 的微调/零样本二分完全靠它驱动。

**`_safe_model_call` 是解耦的操作化**（`:102-138`）：任务对模型的一切调用都走它。默认模式（`:126-138`）先 `hasattr` 探测方法存在，再 try-except 包住执行，失败返回 `tuple([None]*num_outputs)`；`--disable_safe_model_call` 时直呼（`:118-123`）。模型"不支持某能力"由此从异常降级为数据流里的 None，再由指标层消化。

**分类基类实现完整评测循环**（`gfmbench_api/tasks/base/base_gfm_supervised_classification_task.py:81-143`）：建 DataLoader、实例化 Accuracy/MCC/AUROC/AUPRC 四指标（`:107-112`）、逐 batch 委托子类 `_batch_to_probs` 抽概率与标签、`np.allclose` 断言每条类分布和为 1（`:129-136`），最后按 `{metric.name: metric.get_final_results()}` 动态组装结果（`:143`）。子类只需回答三个问题：几个 label、几类、batch 怎么变概率——`SingleSeqTask` 答第三问的方式是固定调 `infer_sequence_to_labels_probs`，`VariantEffectTask` 固定调 `infer_variant_ref_sequences_to_labels_probs`（两者 `_is_variant_effect_prediction` 分别硬编码 False/True）。

**零样本侧是钩子组合模式**：`ZeroShotTask._eval_dataset`（`base_gfm_zero_shot_task.py:85-173`）先挂 6 个通用指标（SumProbsLLR×2 + 嵌入 cosine/L2×4，`:110-117`），对 reference 序列走 `SequenceInferenceCache.cached_call`（`:122`/`:134-139`）省一半推理；SNV 子类通过 `_get_additional_metrics`（`gfmbench_api/tasks/base/base_gfm_zeroshot_snv_task.py:57-66`）追加 4 指标，并在 `_update_additional_metrics`（`:84-112`）里现场调 `sequence_pos_to_prob_pos` 做位置映射（`:87-92`）、调 `infer_masked_sequence_to_token_probs` 拿 masked 概率（`:97-101`）。indel 子类则把两个钩子显式置空（`gfmbench_api/tasks/base/base_gfm_zeroshot_general_indel_task.py:38-52`）——**钩子默认必选、中间层决定填或不填**，是理解指标矩阵差异的钥匙。

## 三、外部连接

任务侧向下连接：数据工具（`fileutils` 下载、`preprocutils.pad_sequence_centered_variant` 定中心窗口、`sampling_utils.diverse_sample_dataframe` 分层限样）与指标库（L04 层 17 类）。向上被三处消费：`run_benchmark.py:71` 注册表、`tests/e2e/fixture_tasks.py:67/94/120` 三个夹具任务、`test_heavy.py:57-71` 的 `_expected_auroc_metrics`——后者用 `issubclass(task_cls, gfmbench_api/tasks/base)` 按基类推断每任务应产出哪些 AUROC 指标，**族谱直接参与测试断言的生成**，类层次即测试语义。

具体任务盘点（grep 实证）：concrete 目录 23 个任务类 = 有监督 13（GUE×3 SingleSeq + LRB causal_eqtl/VariantBenchmarks×6 走 VariantEffect + LRB enhancer/histone 走 SingleSeq + CAGE 回归）+ 零样本 10（SNV 系 8 + GeneralIndel 系 2）。图谱 L06/L07 的 14/10 节点数里，L06 含 1 个 `__init__.py` barrel，**任务类实数 13+10=23，注册表收录 22 = 12 有监督全分类 + 10 零样本**，唯一落榜者是回归的 CAGE（`lrb_cage_task.py:32`）。

## 四、数据流

以零样本 SNV 任务为例（traitgym/brca1/clinvar 全走这条）：`_create_test_dataset` 从 parquet/VCF 式表出发，`pad_sequence_centered_variant` 以变异位为中心截窗，产出 `(variant_seq, ref_seq, label, conditional_input)` 四元组列表；评测循环每个 batch 调两次 `infer_sequence_to_sequence`（variant 走直呼 `:128-130`，reference 走缓存 `:134-139`），得三元组（逐位概率/逐位嵌入/代表嵌入）塞进 outputs dict（`:142-150`）；6 个通用指标按 arg_keys 取数 calc（`:153-155`），SNV 钩子再补 4 个位置级指标（`:158-162`）；循环毕，`results[metric.name] = metric.get_final_results()`（`:167-171`）汇总返回。有监督路径则多一个前置消费者：`get_finetune_dataset()` 的 train_dataset 先被 `run_benchmark.py:401` 拿去喂 `GFMFinetuner`。

## 五、设计决策

**BaseGFMModel 的 7-1 不对称**：7 个协议方法中 6 个 `@abstractmethod`（`base_gfm_model.py:28/38/74/116/164/212`：`__init__`、labels_probs、sequence 三元组、pos 映射、masked 概率、variant_ref 对），唯独 `infer_sequence_to_regression`（`:59-72`）非抽象、默认 `return None`——回归是全家最年轻的能力（只服务 CAGE 一个任务），强制抽象会令 6 个存量适配器瞬间不可实例化。这是**可选能力的默认降级模式**：新方法先以 None 默认值进协议，模型按需覆写，指标层遇 None 自动跳过。

**继承是混合风格、且官方默许**：显式继承 `BaseGFMModel` 的有 `dna_bert_model.py:27`、`ntv3_model.py:145`、`isolated_mock_model.py:204`；纯鸭子类型的有 `dna_bert2_model.py:26`（`class DNABERT2Model(nn.Module)`）、`hyena_dna_model.py:31`、`evo2_model.py:79`（普通类）。两者在任务侧一视同仁——`_safe_model_call` 按名探测，继承与否不影响任何行为。教程 `add_new_model_tutorial.ipynb` 新写的模型走的也是鸭子路线。

**复制孪生优于参数化**：`traitgym_complex_task.py` 与 `traitgym_mendelian_task.py` 全文 diff 仅 5 处——类名（`:127`）、类 docstring（`:129`）、`dataset_config` doc（`:152`）、`self.dataset_config` 赋值（`:155`，`"complex_traits"` vs `"mendelian_traits"`）、`get_task_name`（`:163`），连共享辅助函数 `_load_traitgym_dataset`（两文件 `:53-122`）都整段复制。353 行换 5 行差异，看似浪费，实则让每个任务文件可以独立演进（一个要改窗口策略时不碰另一个）；代价是修 bug 必须双写—— `_get_default_max_seq_len` 的 docstring 就同时在两处失真。

**docstring 与实现漂移要警惕**：`bend_vep_disease_task.py:61-63`（expression 版同）docstring 写 "(1048576bp)"，下一行 `return 512`。以代码为准：BEND 任务默认窗口 512bp；1048576 是从 traitgym/brca1（`brca1_task.py:65-66` 确为 `return 1048576`）复制模板时的注释残留。**brca1 的 predict_evo2 脚手架**（`brca1_task.py:324-358`）同样要读准：`_run_predict_evo2` 组装 `predict_evo2` CLI（命令名在 `:336`，`subprocess.run(check=True)` 在 `:358`），配套 `_write_dedup_fasta`（`:281`）与 `_load_predictions`（`:304`）——但**三个模块级函数在全仓零调用**，是为 Evo2 走外部 CLI 批量打分预留的离线通道，当前评测仍走类内 `_safe_model_call` 协议路径。

## 六、新人提示

- 加新任务先选对中间基类：数据是 `(variant, ref, label)` 就继承 VariantEffect/SNV，是 `(sequence, label)` 就 SingleSeq，连续值才碰 Regression。选错基类 = 白写 `_batch_to_probs`。
- 必实现清单以基类 docstring 为准（如 `gfmbench_api/tasks/base/base_gfm_supervised_classification_task.py:43-50` 列 7 项）；最薄样板是 `gue_promoter_all_task.py:46`（约 140 行），零样本抄 traitgym 双子。
- `_get_task_data_dir_name`（`base_gfm_task.py:288-296`）默认返回任务名，多个任务共享磁盘目录时覆写它——traitgym 双子正是靠不同 task_name 天然分目录。
- 写模型适配器时三方法不可缺：`eval()`、`get_hidden_dim()`、构造签名 `(device, max_length, **kwargs)`（`run_benchmark.py:305/:379/:385/:441` 直接调用）；其余方法不支持就别定义，比定义了返回错形状安全。
- `sequence_pos_to_prob_pos` 是 BPE/k-mer 模型的生死线（`base_gfm_model.py:138-159` 给了 4 类 tokenizer 的映射示例）：定位错了，SNV 位置级指标整组报废；返回 -1 表示不可定位是协议明文允许的出口。
- 改基类前先跑 `pytest tests/e2e/test_smoke.py`——六测试锁死了四类任务的指标键集合，族谱任何语义漂移会被当场抓住。
