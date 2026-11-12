# EXPLAIN-08 · modelopt/torch/puzzletron：MIP 局部 NAS 结构剪枝（Puzzle）

## 一、角色定位

`modelopt/torch/puzzletron` 是主包内的结构化压缩子系统，实现 Puzzle 论文（arXiv 2411.19146，README.md:2）的"局部 NAS + MIP 全局拼装"两段式剪枝。核心命题：各层剪枝敏感度不同，与其全网均匀剪，不如为每层独立挑"替换块"（更窄 FFN、更少 KV head、no-op attention），再用 MIP 求满足内存/延迟约束的最优组合——产物是**异构架构**（examples/puzzletron/README.md:10、:13-14）。与 ptq/pruning 数值域优化互补，这是结构域；复用 `modelopt.torch.prune` 重要性钩子（ffn_pruning.yaml:11），经 `mtn.convert`/`mtn.search`（examples/puzzletron/main.py:97、:115）挂进 NAS 插件体系。

## 二、内部结构

**五步主管线**（entrypoint.py:49-77）：Step 0 hydra 配置 → Step 1 `launch_score_activations`（分布式打分）→ Step 2 `launch_prune_ckpt`（剪枝候选）→ Step 3 `launch_build_library_and_stats`（建库+量测）→ Step 4 `launch_scoring`（单块精度分）→ Step 5 `launch_mip_and_realize_model`（求解落地）；步间 `dist.barrier()`（entrypoint.py:66、:71）。

三大子系统：

1. **anymodel/**（模型无关层）：`Converter` 基类（converter/base.py:39）把 HF checkpoint 重组为 subblock 格式——`_get_weight_map`（:43）兼容分片/单文件；`convert_model_weights`（:66）按 descriptor 的 `get_weight_groups`（model_descriptor/base.py:238）分组，每组存 `subblocks_safetensors/<subblock>.safetensors`（base.py:84、:120-125）。`ModelDescriptor`（base.py:29）用 `layer_name_predicates`（:153）正则归组张量名，`block_config_to_layer_overrides`（:44）把每层 BlockConfig 翻成 HF 加载覆盖——异构模型靠它加载。**勘误与实数：anymodel/models 实际 8 个模型族**（gpt_oss/llama/mistral_small/nemotron_h×2/qwen2/qwen3/qwen3_vl）。
2. **activation_scoring/**：`launch_score_activations`（score_pruning_activations.py:132）委托 `validate_model`（:142）；续跑由 `check_scoring_completion`（:50）判定——`rank_*.pth`（:70）+`args.json`（:76）双条件；只有实现 save_state/load_state 的方法可安全续跑（:40-45 白名单），多卡结论 broadcast（:123）。
3. **mip/**：run_puzzle.py（764 行）是 CLI 与度量汇聚——`PuzzleConstraints`（run_puzzle.py:72）支持 MIP 原生约束（stats.memory_mib/runtime_ms）与"人类约束"白名单（:79-86 target_memory/target_throughput 等）；`to_mip_constraints`（:154）换算，如吞吐→runtime 上限 `batch*seq/target`（:175-181）。求解器在 mip_with_multi_layer_replacements.py：PuLP 建模（:27、:60），约束一"每层恰好选一个替换"（:79-81），约束二"成本总和≤上限"（:83-93），solve 后 **Trust But Verify**（:107）用解重算成本逐项 assert（:129-144），不信任求解器返回值。

支撑件：block_config.py 的 `BlockConfig/AttentionConfig/FFNConfig/MoEConfig/MambaConfig`（:126/:201/:149，`no_op` 与 `replace_with_linear` 互斥 :136）；pruning/ 四 mixin；replacement_library/ 候选块库。

## 三、外部连接

- **transformers**：消费 PretrainedConfig，异构加载靠 per-layer overrides；gpt-oss 的 mxfp4 packed 张量用 `convert_moe_packed_tensors` 解包（base.py:104-109）。
- **modelopt.torch.prune**：重要性钩子共享（ffn_pruning.yaml:11）。
- **PuLP**：MIP 前端（mip_with_multi_layer_replacements.py:27）。
- **examples/puzzletron**：教程+配置集（**实测 77 文件，任务书口径 76**），README.md:18 招牌数字：Llama-3.1-8B 113 GiB→96 GiB（15%），token_accuracy_top_10 回归 <1%。
- **NeMo**：生产级分布式走 feature/puzzletron_v2 分支（examples/puzzletron/README.md:5）。

## 四、数据流

以 examples/puzzletron/configs/qwen3-8b_pruneffn_memory 走全链：

1. **转换**：`convert_model(input_dir, output_dir, converter="qwen3")`（convert_any_model.py:28）——两工厂按同名取 descriptor 与 converter（:58-60）；`Converter.convert`（base.py:169）三步：拷非权重文件（:182）→ 每层 BlockConfig 写进 config（base.py:143-145）→ 权重重排（:187）。
2. **打分**：ffn_pruning.yaml:13-14 配 `method: iterative`、`target_layer: "mlp.down_proj"`，钩子在校准数据累积通道贡献落 rank_*.pth。
3. **候选生成**：`intermediate_size_list: [256]`（ffn_pruning.yaml:17，teacher 14336）展开每层变体；MIP 搜索空间是顶层 yaml:22 的 `[2560, 5120, 7424, 9984]`；pruning mixin 按 descriptor 层路径（llama_model_descriptor.py:122）定位权重物理剪枝。
4. **建库量测**：对每候选块实测 memory/runtime 落 subblock_stats 当 MIP 成本系数。
5. **MIP**：顶层 yaml:16-17 只写 `human_constraints: target_memory: 78_000`（78 GiB），换算 `stats.memory_mib≤78000`，目标默认 `metrics.loss` 最小化（mip_with_multi_layer_replacements.py:184）。
6. **落地评估**：realize 成异构 HF checkpoint；换 `target_latency_seconds` 即切延迟预算（examples README.md:369）。

## 五、设计决策

1. **局部搜索+全局 MIP 分层**：单块精度分只在小空间测，组合爆炸交给 MIP 线性结构；代价是单块度量须可线性加和（精度用 loss 代理）。
2. **subblock 文件化**：按层拆独立 safetensors（base.py:84），"替换第 N 层 FFN"退化为换文件+改 index（:124-125）。
3. **人类约束白名单+换算层**（run_puzzle.py:79-86、:154-194）：产品语言译成 MIP 键；延迟换算依赖负载形状，缺 batch_size/generation_seq_len 即报错（:158-160）。
4. **Trust But Verify**（mip_with_multi_layer_replacements.py:107-144）：对求解结果独立复核 assert。
5. **续跑的数学安全性**：只有带 save_state/load_state 的方法可 resume（score_pruning_activations.py:40-47）。
6. **双工厂同键名**（convert_any_model.py:58-60）：一个名字取 descriptor+converter。
7. **hydra 组合配置**：defaults 链（qwen3_8b_pruneffn_memory.yaml:1-3），"换模型不动算法、换约束不动剪枝配置"。

## 六、新人提示

- 入口 `python examples/puzzletron/main.py`（main.py:64 `run_full_puzzletron`，日志 1/8…8/8 打点 :70/:123）；只重解 MIP 用 `run_mip_only`（main.py:126），搜索空间全在 hydra config（main.py:117-119）。
- 改约束在顶层 config `mip.human_constraints`（yaml:16-17）；按延迟优化看 examples README.md:369。
- 新模型四步照 anymodel/README.md：descriptor 写 `layer_name_predicates`（README:11；llama 正则示例 llama_model_descriptor.py:88-117）→ converter 写 `create_block_configs_from_main_config`（README:17）→ 导出 → 注册。张量名去 HF "Files info" 抄，别猜。
- examples/configs 覆盖 llama/qwen/mistral/nemotron/gptoss 九套；gpt-oss 有 mxfp4 解包额外步骤（GPTOSS.md）。
- 坑：单文件模型也能转（base.py:56-59 合成 weight map），报 "Neither…found" 才是真缺权重。
- 坑：PuLP 约束不能有 inf/NaN——run_puzzle 把非约束 report 项设 inf（:86-88），MLR 侧剔除 NaN/inf 替换（mip_with_multi_layer_replacements.py:49-54），两端配合才不炸。
- 冒烟：`python -m pytest tests/gpu/torch/puzzletron/test_puzzletron.py -k "Qwen3-8B"`（examples README.md:46）。
