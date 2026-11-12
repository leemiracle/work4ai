# Megatron-LM 新人导航（ONBOARDING）

> 知识图谱版（commit 05fb87cd，4913 节点/11723 边/16 层，2026-11-05）；行号锚均经源码核实。

## 一、一图看懂

NVIDIA 巨型 LLM 训练框架：核心资产是 `megatron/core`（五维并行+FP8/FP4），`megatron/training` 编排，examples/tools/CI 外围。README.md:96/109：2B-462B 最高 47% MFU、6144 卡 H100 训 462B。16 层：

| 层 | 职责 | 代表文件 |
|---|---|---|
| L01 配置与并行状态基座 | 配置+进程组单例 | core/parallel_state.py |
| L02 通信与多维并行 | TP/PP/CP/DP 原语与调度 | pipeline_parallel/schedules.py |
| L03 Transformer/SSM 内核 | 注意力/MoE/Mamba 积木 | transformer/transformer_layer.py |
| L04 模型实现群 | GPT/BERT/混合/多模态 | models/gpt/gpt_model.py |
| L05 数据集与分词 | 混合采样+mmap+分词 | datasets/gpt_dataset.py |
| L06 优化器与分布式检查点 | 分布式优化器+分片 ckpt | optimizer/distrib_optimizer.py |
| L07 推理引擎与在线服务 | 生成+PD 分离+导出 | inference/engines/dynamic_engine.py |
| L08 融合算子与外部扩展 | 融合 kernel+TE+量化 | extensions/transformer_engine.py |
| L09 训练运行时与入口 | 主循环+参数+ckpt | training/training.py |
| L10 强化学习线 | rollout/训练双角色 | train_rl.py |
| L11 后训练与弹性训练 | ModelOpt 量化蒸馏 | post_training/ |
| L12 多模态示例 | VLM 预训练/SFT | examples/multimodal/train.py |
| L13 经典与学术示例 | gpt3/llama/mamba 等 | examples/gpt3/ |
| L14 预处理与运维工具 | 预处理+转换+守护 | tools/preprocess_data.py |
| L15 CI/CD 与容器 | Dockerfile+流水线 | docker/Dockerfile.ci.dev |
| L16 文档与协作资产 | 14 skills+规范 | skills/、AGENTS.md |

依赖方向：L01 被所有人依赖→L02-L08 逐层向上→L09 编排 L04-L06→L10/L11 站其上→L12-L16 外围。

## 二、五分钟路线（16 步 tour→6 里程碑）

**M1 全景（步1）**：读 README.md、AGENTS.md 与 docs/get-started/quickstart.md。**M2 并行底座（步2-5）**：megatron/core/parallel_state.py:622 `initialize_model_parallel` 是一切进程组的单一事实来源；再扫 tensor_parallel/layers.py、schedules.py:54（1F1B）与 distributed/fsdp/（M-FSDP）。**M3 积木与后端（步6-9）**：fusions/ 与 extensions/transformer_engine.py（约 4000 行 TE 桥接）；transformer_block.py:268/transformer_layer.py:329 标准层；spec_utils.py:10 ModuleSpec 双实例化切换本地/TE 实现；进阶 moe/moe_layer.py、multi_latent_attention.py:176 与 ssm/。**M4 模型与数据（步10-11）**：models/gpt/gpt_layer_specs.py:444：一列 ModuleSpec 描述整个模型；datasets/ 与 tokenizers/。**M5 训练闭环（步12-13）**：optimizer/ 与 dist_checkpointing/，然后走第四节全链。**M6 上层（步14-16）**：inference/ → train_rl.py → examples/tools/CI，跑通小模型即入门。

## 三、核心子系统深读

### 3.1 并行基座 parallel_state
megatron/core/parallel_state.py:622 `initialize_model_parallel`（2773 行）构建 TP/PP/CP/DP/EP 全部进程组，约 95 个访问器；core/process_groups_config.py 的 ProcessGroupCollection 承接 AGENTS.md「新代码禁直读全局组、改注入传参」政策。调度选路 pipeline_parallel/schedules.py:54（:724 无流水/:1020 interleaved）。

### 3.2 Transformer 内核与 MoE
transformer/spec_utils.py:10 `ModuleSpec`+:76 `build_module`：同一份 spec 可实例化本地或 TE 实现。MoE 三段式在 transformer/moe/moe_layer.py:227（router:274/token_dispatcher:213/experts）；MLA 在 multi_latent_attention.py:176；experimental_attention_variant/ 收 absorbed_mla、dsa、deepseek_v4_hybrid_attention。

### 3.3 推理引擎
inference/engines/dynamic_engine.py:447 `DynamicInferenceEngine` 装载训练侧模型；text_generation_controllers/text_generation_controller.py:214 驱动逐 token 生成；dynamic_text_gen_server/ 暴露 OpenAI 兼容端点；disaggregation/ 做 PD 分离、export/ 导出 TRT-LLM。启动器 tools/run_dynamic_text_generation_server.py。

### 3.4 RL 训练线
train_rl.py:385 复用训练运行时与推理引擎做 rollout/训练双角色；megatron/rl/agent/rollout_pipeline.py 与 rollout_bank.py 管轨迹生成与回放；megatron/rl/server/ 把环境侧与推理侧拆成独立进程；样例 examples/rl/environments/countdown/countdown_agent.py。

## 四、数据流走查：pretrain_gpt.py 的一生

1. **启动静音**：pretrain_gpt.py:6 记录启动时刻；调 megatron/rank_log_setup.py:19 静音非 rank0 日志（须在 torch 导入前）。
2. **参数**：training/arguments.py:92 `parse_and_validate_args`（3881 行，30 余参数组），映射成分层 config。
3. **并行初始化**：training/initialize.py:50 `initialize_megatron` → :395 调 core/parallel_state.py:622 建全部进程组。
4. **三 Provider**：model_provider.py:21 选模型；gpt_builders.py 造数据与损失；pretrain_gpt.py:224 `loss_func` 与 :297 `forward_step`。
5. **主循环**：pretrain_gpt.py:583 调 training/training.py:1595 `pretrain()`（6208 行），:2894 `setup_model_and_optimizer` 装配模型/优化器。
6. **单步**：training.py:3302 `train_step` → schedules.py:54 选调度器，微批 1F1B 流水；梯度经 distributed/finalize_model_grads 收敛。
7. **落盘**：training/checkpointing.py:658 `save_checkpoint` / :2617 `load_checkpoint`（3421 行），走 dist_checkpointing/mapping.py:48 ShardedTensor 分片抽象。

## 五、依赖地图（枢纽 top10，按 fanIn）

| 枢纽文件 | fanIn | fanOut | 角色 |
|---|---|---|---|
| core/utils.py | 225 | 61 | 工具中枢：版本探测/sharded tensor/API 装饰器 |
| core/__init__.py | 119 | 9 | 包根（mpu 别名） |
| transformer/transformer_config.py | 91 | 21 | 超参中枢（4034 行） |
| core/parallel_state.py | 87 | 60 | 并行状态单例 |
| core/process_groups_config.py | 78 | 11 | 进程组显式传参 |
| training/__init__.py | 76 | 4 | barrel：get_args/pretrain |
| transformer/module.py | 68 | 29 | 模块基类层 |
| transformer/spec_utils.py | 60 | 10 | ModuleSpec 延迟实例化 |
| tensor_parallel/__init__.py | 55 | 7 | TP 公共 API 面 |
| transformer/enums.py | 54 | 16 | AttnMaskType 等公共枚举 |

（均省略 megatron/ 前缀。）规律：L01 基座霸榜，改 utils/parallel_state 等于全仓重编译；大量 `__init__.py` 是 barrel 枢纽，追实现须穿透看真实路径；process_groups_config.py 的 fanIn 78 是「进程组注入」迁移的证据；training 侧枢纽为 global_vars.py（fanIn 51）。

## 六、坑与勘误（源码级发现）

1. **CLAUDE.md 是 AGENTS.md 逐字节孪生**：md5 一致（`31f0df24…`，62 行），改政策须同步两处。
2. **CONTRIBUTING.md 仅 3 行占位**：跳转官方贡献指南，仓内无全文。
3. **空 `__init__.py` 陷阱**：megatron/core/datasets/__init__.py 是 0 行空文件（须按完整路径导入）；models/hybrid/layers/__init__.py 仅 1 行版权注释。
4. **kitchen.py 永久 stub**：core/extensions/kitchen.py:3 `HAVE_KITCHEN=False` 恒假，15 个符号全 MagicMock。
5. **GTP 静默降级与 no-op 垫片**：core/tensor_parallel/gtp_api.py:49 TE 缺失或过旧时置 `HAVE_GTP=False`+no-op stub；core/telemetry/fallbacks.py:11 在 nemo-lens 缺席时给 no-op。
6. **sys.modules shim**：core/resharding/nvshmem_copy_service/compat.py:24-26 因 cuda-core≥0.5 删私有子模块而 nvshmem4py 仍引用，把新路径注册回旧路径——依赖升级断点区。
7. **vendored 子树独立血统**：core/nccl_allocator.py:17-19 注释明言「复制并修改自 APEX」；core/distributed/fsdp/src/megatron_fsdp/ 自带 pyproject.toml 自包含，PR 上游归属不同。
8. **兼容壳与死枚举**：core/enums.py:13 `encoder_and_decoder=2` 仅为旧 checkpoint 保留；hybrid_layer_specs.py 保留 mamba_*/gdp_* 别名；post_training/arguments.py 的 MambaModel 仅向后兼容。
9. **import 副作用**：core/__init__.py 导入即用 weights_only 安全实现替换 `torch.storage._load_from_bytes`（safe_globals.py 白名单）。
10. **yaml 占位路径**：examples/multimodal 的 pretrain_blend.yaml/sft_dataset.yaml 路径为占位符，须自备 energon 数据集。

## 七、如何跑起来

**入门**：docs/get-started/quickstart.md + install.md（PyPI/源码装 megatron-core）；examples/run_simple_mcore_train_loop.py 最简训练循环。**预训练**：仓根 pretrain_gpt.py（GPT/SFT）/pretrain_vlm.py/pretrain_hybrid.py/pretrain_mamba.py 按族分置；数据先经 tools/preprocess_data.py 成 mmap 索引；规模样例 examples/gpt3/train_gpt3_175b_distributed.sh、examples/llama/train_llama3_8b_h100_fp8.sh。**推理**：tools/run_dynamic_text_generation_server.py 起动态生成服务；examples/inference/launch_inference_server.py:6 演示 `MegatronAsyncLLM.serve` 高层路径。**其余**：train_rl.py + examples/rl/；multimodal 走 energon 栈；post_training/modelopt/ 量化蒸馏。**容器 CI**：docker/ 四路 Dockerfile（ci.dev/ci.lts/ci.nemo/linting）+ .gitlab-ci.yml 多阶段流水线。

## 八、延伸阅读

- docs/get-started/（quickstart/install/overview）；docs/user-guide/（data-loading、deterministic-training 等）；docs/mcore-inference-user-guide.md 推理文档；docs/developer/（contribute/oncall）。
- skills/ 14 个 agent 技能（mcore-cicd、mcore-testing、mcore-run-on-slurm、mcore-migrate-gpt-to-hybrid、update-golden-values 等）——AGENTS.md 强制「先读工件→选技能→再作答」。
- 子域 README：megatron/rl/README.md、core/inference/README.md、fsdp/src/ 内文档。
- 图谱资产：tour 与 30 枢纽见 .understand-anything/onboard-input.json，完整 knowledge-graph.json 可下钻。

---
*行号随上游演进可能漂移，以语义定位为准。*
