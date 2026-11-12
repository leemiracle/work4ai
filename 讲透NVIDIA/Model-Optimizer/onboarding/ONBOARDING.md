# NVIDIA Model-Optimizer（ModelOpt）Onboarding

> 基于 understand-anything 图谱（10540 节点/23823 边，16 层/16 步导览，commit `e3c903c`）撰写，全部 `路径:行号` 锚经源码 Read 核实。

## 1. 项目定位与安装

ModelOpt（PyPI 包名 `nvidia-modelopt`，`pyproject.toml:16`）是 NVIDIA 开源的模型量化与压缩全栈框架：**torch 主线**（`modelopt/torch/`）、**ONNX 图量化**（`modelopt/onnx/`）、**TensorRT 部署封皮**（`modelopt/deploy/`）。一句话定位：把 FP16/BF16 的 PyTorch/HF/Megatron 模型，经由假量化与校准，产出可在 TensorRT-LLM / vLLM / llama.cpp 上运行的低精度 checkpoint。

它同时是重度 **agent-first 仓库**：根目录 `AGENTS.md`（112 行）是 AI 协作约定正本，`CLAUDE.md` 是其符号链接（`ls -la` 实证 `CLAUDE.md -> AGENTS.md`）；技能卡、子代理、MCP server 均作为可安装插件随仓发布（第 6 节）。

安装面：Python 3.10–3.14（`pyproject.toml:22`）；核心仅依赖 torch/numpy 级基础包，transformer_engine/megatron/vllm 等宿主按 extras 可选。文档在 `docs/source/`（Sphinx）。测试入口遵循 `AGENTS.md:24-27`：从 `tests/` 挑聚焦测试跑。

协作铁律（对人类与 agent 同等生效）：技能树在 `plugins/modelopt/skills/`（`AGENTS.md:10`）；签名提交 `git commit -s -S`（`AGENTS.md:31`）；**未经当轮批准禁止 `git push`**（`AGENTS.md:34`）；PR 新增源码 ~500 行内、超预算先提拆分方案（`AGENTS.md:49` 起）。

## 2. 目录结构导览（图谱 16 层）

| 层 | 名称 | 内容 |
|---|---|---|
| L01 | 仓库治理与文档基座 | README/AGENTS.md/CONTRIBUTING/构建定义/CI 与 docs/ |
| L02 | Agent 技能插件体系 | `plugins/modelopt` 插件：16 张技能卡 + 6 个子代理定义 |
| L03 | torch 量化主线 | `modelopt/torch/quantization` 与 `opt/`（第 3、4 节展开） |
| L04 | torch 压缩族 | sparsity/nas/prune/distill/peft/fastgen |
| L05 | torch utils | 模型遍历换装、DDP 兼容、.mopt 序列化等公共地基 |
| L06 | torch kernels | 原生 CUDA/triton kernel：量化 GEMM、稀疏 attention、融合算子 |
| L07 | torch models | HF/多模态模型的 AutoModelClass 注册与配置映射 |
| L08 | export 链路 | ONNX 导出、图手术、TensorRT-LLM 引擎转换封皮 |
| L09 | speculative decoding | medusa/eagle/dflash 三族投机解码 |
| L10 | puzzletron | Puzzle 论文的 MIP 结构剪枝实验框架 |
| L11 | onnx 与发布通道 | 图级 Q/DQ 量化 + 自动调优；recipe 执行器与 deploy 封皮 |
| L12 | experimental DMS | Dynamic Memory Sparsification：可学习 KV cache 逐出 |
| L13 | tools 工具链 | launcher（SLURM/Docker 作业）+ mcp（FastMCP 服务器）等 |
| L14 | modelopt_recipes | 201 个 yaml/md 配方（188+13），数值格式在此声明 |
| L15 | tests | 498 个测试文件：unit/gpu/gpu_megatron/gpu_vllm/gpu_trtllm/regression |
| L16 | examples | 26 个顶层示例目录 448 个样例，可被 launcher/recipes 直接索引 |

（勘误：图谱摘要"17 技能卡/501 测试/204 yaml"为建图时点计数，当前 HEAD 实测 16/498/201，以源码为准。）

定位口诀：**改算法看 L03/L06，适配模型看 L07+plugins，接引擎看 L08/L11，跑集群看 L13/L14，学用法看 L16。**

## 3. 量化体系全景

### 3.1 QAT 与 PTQ 的统一入口

QAT 与 PTQ 共用同一套"把 `nn.Linear`/`nn.Conv2d` 换成量化模块"的机制，差别只在换装后立即恢复（PTQ）还是继续训练（QAT/LSQ）。用户面 API 集中在 `model_quant.py` 的 `__all__`（`model_quant.py:55-67`）：`quantize`/`calibrate`/`auto_quantize`/`fold_weight`/`print_quant_summary` 等。

`mtq.quantize(model, config, forward_loop)`（`model_quant.py:233`）三参数即缩影：

- `config`：`{"quant_cfg": [...], "algorithm": "max"}`。`quant_cfg` 是**有序通配符列表**，后项覆盖前项（docstring 示例 `model_quant.py:273-283`）；量化器命名约定 `*weight_quantizer` 与 `*input_quantizer`，分管权重与激活。
- `forward_loop`：`forward_loop(model)` 可调用对象，把校准数据灌进模型（三种写法示例 `model_quant.py:296-322`）。

### 3.2 假量化模块机制（fake quantization + STE）

换装产物是 `nn/modules/` 量化模块族：`QuantModule`（`quant_module.py:41`，继承 `DynamicModule` 保留原模块引用以便还原）、`QuantLinear`（`quant_linear.py:56`）及 Conv/Embedding/RNN/LayerNorm 等 11 类模块文件（实测清单）。

每个量化模块持有 `TensorQuantizer` 实例（`tensor_quantizer.py:136`，1919 行）。它是核心状态机，三态语义（`tensor_quantizer.py:138-143`）：量化态（if_quant，forward 假量化，输出仍 float 但数值落在目标网格）；校准态（if_calib，只收集 amax 交给 calibrator）；关闭态（直通）。

假量化梯度走 **STE（straight-through estimator）**：`tensor_quant.py:291` 的 `_fake_tensor_quant_backward` 核心一行——`torch.where(inputs.abs() <= amax, grad_outputs, zero)`，clip 内直通、外置零，`@torch.jit.script` 加速；autograd 封装在 `FakeTensorQuantFunction`（`tensor_quant.py:319`）。这是 QAT 端到端训练的数学基础。动态块级量化（NVFP4/MXFP4 block scale）走 `DynamicBlockQuantizationFunction`（`tensor_quant.py:497`），静态 FP4 走 `StaticBlockwiseFP4FakeQuantFunction`（`:571`），底层统一落 `_tensor_quant`（`:607`），CUDA 实现在 `modelopt/torch/kernels/quantization/gemm/tensor_quant.cu`。

### 3.3 校准算法族

`calibrate()`（`model_quant.py:71`）经 `apply_mode` 派发（`model_quant.py:119-124`），注册表在 `modelopt/torch/quantization/mode.py` 的 `CalibrateModeRegistry`——实测 12 个校准 mode：None/Max/NVFP4ActHeadroom/Mse/LocalHessian/SmoothQuant/AWQLite/AWQClip/AWQFull/SVDQuant/GPTQ/LSQ（`modelopt/torch/quantization/mode.py:413` 起注册，Max `:425`，LSQ `:562`）。实现集中在 `model_calib.py`（当前 2410 行）：

| 算法 | 实现锚 | 要点 |
|---|---|---|
| max | `modelopt/torch/quantization/calib/max.py:26` `MaxCalibrator` | 最简，weight-only 不需 forward_loop |
| mse | `modelopt/torch/quantization/calib/mse.py:31`；NVFP4 变体 `modelopt/torch/quantization/calib/mse.py:175` | 逐层搜 amax 最小化量化 MSE |
| entropy/percentile | `modelopt/torch/quantization/calib/histogram.py:35`，weights 后处理 `modelopt/torch/quantization/calib/histogram.py:346` | 直方图 clipping |
| NVFP4 act headroom | `modelopt/torch/quantization/calib/nvfp4_act_headroom.py:36` | NVFP4 动态激活裕量 |
| bias | `modelopt/torch/quantization/calib/bias.py:100` | 偏置校正 |
| smoothquant | `model_calib.py:1281` | per-channel 权重缩放迁移激活离群值，alpha 搜索 |
| awq_lite/clip/full | `model_calib.py:1369` 派发，lite `:1402`、clip `:1732` | 激活感知权重量化 |
| local_hessian | `model_calib.py:1011` | 局部 Hessian 误差（AWQ clip 与 SVDQuant 共用） |
| svdquant | `model_calib.py:1987` | 低秩残差分支（配套 `quant_linear.py:65`） |
| gptq | `model_calib.py:2255` | Hessian 逐层误差补偿，block_size=128 |
| lsq | `model_calib.py:2362` | 先 scale 校准（`:2340`）再 `enable_lsq` 转可学习 amax——PTQ 到 QAT 的桥梁 |

`auto_quantize`（`model_quant.py:511`）在格式×算法组合上自动搜索（白名单 `model_quant.py:348-357`）。

### 3.4 数值格式与 qtensor（真实量化 vs 假量化）

**假量化**服务校准/QAT；**真实量化**（张量真变低比特存储+scale）由 `qtensor/` 承担：`modelopt/torch/quantization/qtensor/__init__.py:18-25` 导出 8 个模块——base_qtensor（BaseQuantizedTensor 协议）+ fp8/int4/int8/mxfp4/mxfp8/nf4/nvfp4 七种格式，代表类 `FP8QTensor`（`qtensor/fp8_tensor.py:33`，per-tensor scale）、`NVFP4QTensor`（`qtensor/nvfp4_tensor.py:49`，block-16 e2m1+e4m3 双层 scale）。

真实量化 GEMM 落地在 `backends/`：`gemm_registry.py:31` 的 `GEMMRegistry` 按 dtype 路由到 cuBLAS/CUTLASS（nvfp4_gemm.py 为 Blackwell FP4 路径），`gemm_registry.py:104` 开启；mode 描述符 `RealQuantizeModeDescriptor`（`modelopt/torch/quantization/mode.py:165`）。

**IQ 码本量化**：`ggml/` 把 llama.cpp 的 IQ1_S/IQ1_M/IQ2_S/IQ2_XS/IQ2_XXS 带进 torch 工作流（各格式独立文件，`modelopt/torch/quantization/ggml/registry.py:35` 统一注册）——GPU 校准出的 1-2 bit 权重可直接服务 llama.cpp。

格式速查（与 recipes/numerics 一一对应）：FP8（e4m3/e5m2）、INT8（per-tensor/channel）、INT4（per-block/AWQ）、NVFP4（e2m1 block-16+FP8 scale，Blackwell 主推）、MXFP4/MXFP8/MXINT8（OCP MX）、NF4（QLoRA）、IQ1/IQ2 系（ggml 码本）。

## 4. 核心数据流：quantize → 假量化 → 校准 → 导出

一次典型 PTQ 的完整链路：

1. **换装**：未量化模型走 `apply_mode(model, mode=[("quantize", dict(config))], registry=QuantizeModeRegistry)`（`model_quant.py:332`）递归替换 `nn.Linear → QuantLinear`；已量化则只应用新 `quant_cfg`（`:335`）。
2. **生效自检**：换装后立即 `_check_weight_quantization_took_effect`（`model_quant.py:337`，定义 `:157`）——宁可在校准前失败，不导出没量化的 checkpoint。
3. **校准**：`return calibrate(model, config.get("algorithm"), forward_loop=...)`（`model_quant.py:338`）。`calibrate` 切 eval（`:117`），在 `forward_with_reshard` 上下文跑派发算法，结束后逐量化器校验 `_amax`/`_pre_quant_scale`（`:126-129`）。
4. **恢复/折叠**：`restore` 还原结构；或 `fold_weight`（`model_quant.py:1014`）/`temporarily_fold_weights`（`:1026`）把假量化折叠进权重。
5. **导出**：`modelopt/torch/export/` 三线——quant_format 定义格式转换；trtllm/ 生成 TensorRT-LLM 配置；unified_export_hf/megatron 双路统一导出。宿主对接在 `quantization/plugins/`——实测 17 个宿主适配 py（accelerate/fairscale/huggingface/megatron/peft/transformer_engine/transformers/trl/vllm + diffusion 下 diffusers/fastvideo/ltx2 等）。

线上实样：`examples/hf_ptq/hf_ptq.py:549` 的 `mtq.quantize(language_model, quant_cfg, forward_loop=calibrate_loop)`——支持矩阵（`examples/hf_ptq/README.md:96`）里全部 HF 模型的统一入口。

`opt/` 是流之上的编排层：`Optimization` 把 quantize/distill/prune/sparsity 排成一条流水线（可叠加，如 QAT+distill）。

## 5. recipes 配方库体系：配方即语言

`modelopt_recipes/` 的设计哲学：**数值格式与作业拓扑声明在 yaml 里，而不是代码里**。实测 188 yaml + 13 md，四层组织：

- **`configs/numerics/`（17 个 yaml）**：纯量化器属性单元。文件头部 `modelopt-schema:` 锚定到 `QuantizerAttributeConfig`（`modelopt_recipes/configs/numerics/fp8.yaml:18`），正文即属性字典：`fp8.yaml:19` 是 `num_bits: e4m3`+空 axis（per-tensor）；`modelopt_recipes/configs/numerics/nvfp4.yaml:19` 是 `num_bits: e2m1`+block_sizes（-1:16, dynamic, scale_bits e4m3），且带 autoquant 修正 `effective_bits: 4.5`（`nvfp4.yaml:25-26`：4 值 bit+每 16 元素一个 FP8 scale，num_bits 低估为 4.0）。两者均在 `modelopt_recipes/configs/numerics/` 下，覆盖 fp8/int8/int4/nvfp4/mxfp4-8/mxint8/iq 系。
- **`configs/auto_quantize/`、`configs/ptq/`**：AutoQuant 排除/禁用层清单与通用 PTQ 配置。
- **`general/`**：通用管线配方（auto_quantize/distillation/ptq/qad/speculative_decoding）。
- **`model_type/` 与 `models/`**：先按架构家族（qwen3_5、qwen3_vl、gemma、nemotron_llama/vl、step3p7、vit、mpt 等），再按 org（Qwen/meta-models/deepseek-ai/mistralai/moonshotai/nvidia 等）落模型专属配方；另有 `timm/` 视觉线。

配方是 `tools/launcher` 的直接输入语言（launcher CLAUDE.md 的 YAML Config Format 节：顶层 key → `launch()` 参数，`pipeline.task_N` 声明任务，`<<global_vars.*>>` 变量替换）。`quant-recipe-search` 卡的存在说明 NVIDIA 把"在 200 个配方里检索"本身当成 agent 一等任务。

## 6. agent-first 协作体系

ModelOpt 是 agent 协作工程的重度样本——agent 资产不是散落提示词，而是**可安装插件 + 三入口暴露 + MCP 执行面**的完整体系：

- **正本与链接**：`CLAUDE.md -> AGENTS.md`（根目录符号链接实证）；`.agents/skills -> ../plugins/modelopt/skills`、`.claude/skills/* -> ../../.agents/skills/*` 两级相对符号链接把技能树暴露给仓内 agent；`.agents/README.md` 开篇声明整套目录约定。三入口（.agents/.claude/.codex，后者在 `.codex/agents/`）共享同一份 canonical 资产。
- **插件本体**：`plugins/modelopt/.claude-plugin/plugin.json` 声明 name=modelopt、Apache-2.0，并**内嵌 mcpServers 定义**（`uvx --from git+...#subdirectory=tools/mcp modelopt-mcp`）；`.codex-plugin/` 与 `.mcp.json` 副本并列。
- **技能卡**：`plugins/modelopt/skills/` 实测 **16 张 SKILL.md**（勘误：图谱摘要作 17；含 common 公共卡）：ptq、quant-recipe-search、debug、deployment、day0-release、release-cherry-pick、run-agentx、launching-evals、benchmark-model-kernels、accessing-mlflow、monitor、compare-results、evaluation、qad、speculative-decoding、common。主卡 `plugins/modelopt/skills/ptq/SKILL.md` 五段工作流：Step 1 Environment（`:19`）、Step 2 支持表核查（`:30`）、Step 3 格式选择（`:55`）、Step 4 运行（`:81`）、Step 5 验证输出（`:160`，期望 config.json+model-*.safetensors）；frontmatter 写明触发词与**反向排除**（多候选探索用 quant-recipe-search 而非 ptq）。后者定义"选指标→选基线→设计 delta→解读敏感度→定下一候选"循环并在 description 做六卡互斥路由——技能卡之间是一张显式路由图。
- **子代理定义**：`plugins/modelopt/agents/` 6 个角色（quantizer/recipe-searcher/downloader/evaluator/benchmarker/deployer）。
- **MCP 执行面**：`tools/mcp/modelopt_mcp/server.py`（603 行）用 FastMCP 暴露 **9 个 typed 工具**（`@mcp.tool` 实数）：`list_examples`（`:66`，submit_job 前先发现 YAML）、`verify_setup`（`:85`，先探活）、`submit_job`（`:160`）、`job_status`（`:357`）、`job_logs`（`:378`）、`wait_for_experiment`（`:407`）、`provision_passwordless_ssh_dry_run`（`:462`）、`read_cluster_artifact`（`:508`）、`open_draft_pr`（`:549`）。`bridge.py` 是纯桥接层（不 import launcher 包，走子进程探测，test_bridge.py 1764 行护航）；`SCOPE.md` 划界：**环境工具不做工作流决策**。
- **launcher 的 agent 接口**：`tools/launcher/CLAUDE.md:1` 起是给 agent 读的操作手册；`tools/launcher/launch.py:125` 的 `launch(job_name, job_dir, pipeline, hf_local, ...)` 是 SLURM/Docker 双执行器公共入口。

串起来：**技能卡（决策）→ recipes yaml（声明）→ launcher（执行）→ MCP 工具（远程操控）→ AGENTS.md（规则）**——"用 agent 的方式使用 ModelOpt"（图谱 T02 步）的完整闭环，本仓最大工程特色。

## 7. 实验线：投机解码、DMS、Puzzletron 与压缩家族

主量化线之外四条研究/实验线（图谱 L04/L09/L10/L12）：

- **投机解码**：`modelopt/torch/speculative/` 三族 medusa/eagle/dflash，统一配置 `EAGLE3_DEFAULT_CFG`（`modelopt/torch/speculative/config.py:49`）；eagle3 差异在 `use_aux_hidden_state`/`use_last_layernorm` 开关（`modelopt/torch/speculative/config.py:44-45`）。各子包含 conversion+动态模块，与量化线正交可叠加。
- **DMS（Dynamic Memory Sparsification，arXiv 2506.05345）**：`experimental/dms/` 独立 pyproject，可学习 KV cache 逐出——`experimental/dms/dms/core.py:243` Gumbel 门控离散化；`attention.py`（270 行）FlexAttention 训练软门控/FlashAttention 推理硬逐出双态；`cache_paged.py`（1054 行）分页 KV；README 给 Qwen3-8B 8×H100 适配路径。
- **Puzzletron**：`modelopt/torch/puzzletron/`，基于 Puzzle 论文（`modelopt/torch/puzzletron/README.md:2` 锚 arXiv:2411.19146）的 MIP 局部架构搜索结构剪枝（Llama 3.1 PoC）：anymodel/ 架构无关 HF→AnyModel 转换、mip/ 求解器、sewing_kit/ 与 replacement_library/ 组成"块库+缝合"流水线；examples/puzzletron（76 样例）是用法面。
- **压缩家族**：`sparsity/`（2:4 半结构化，`SparseGPTSearcher` 在 weight_sparsity/sparsegpt.py:144）、`nas/`（ENTD）、`prune/`、`distill/`、`peft/`（LoRA×量化）、`fastgen/`（注意力变体选择）。共享 `opt/` 配置面。

## 8. 测试验证面与新人上手路径

**验证面**：`tests/` 实测 498 个文件——unit/、gpu/、gpu_megatron/、gpu_vllm/、gpu_trtllm/（上游引擎集成）、regression/、examples/（冒烟）。MCP 层自带 `tools/mcp/tests/test_bridge.py`（1764 行）。ONNX 线用 trtexec 双路基准做 Q/DQ 插入点自动调优（`modelopt/onnx/quantization/autotune/`；勘误：在 quantization/ 子目录下而非 onnx/ 顶层）。examples/ 26 个顶层目录覆盖 hf_ptq/llm_qat/megatron_bridge/vllm_serve/onnx_ptq/puzzletron 等全谱系。

**新人上手路径**（由轻到重）：

1. **读两张卡**：`AGENTS.md`（协作规则）+ `plugins/modelopt/skills/ptq/SKILL.md`（五段工作流，引导读 hf_ptq README 支持矩阵）。
2. **跑最小 PTQ**：`examples/hf_ptq/hf_ptq.py`（`mtq.quantize` 调用点 `:549`），单卡产出量化 checkpoint；对照第 3 节理解通配符如何落到 `TensorQuantizer`。
3. **改格式只需换配方**：在 17 个 numerics yaml 里换引用不动代码；多候选用 quant-recipe-search 卡。
4. **上集群**：`uv run launch.py --yaml <配方> --dryrun --yes -v` 先干跑看解析结果再实跑（launcher CLAUDE.md 原句）。
5. **深入源码**：按第 4 节顺序读 model_quant → tensor_quantizer → model_calib → tensor_quant；进阶读 `qtensor/`+`kernels/` 与 `opt/`。
6. **改代码前**：CONTRIBUTING 规范 → 聚焦测试 → 签名提交 → ~500 行 PR 预算（`AGENTS.md:49`）。

**勘误汇总**（图谱摘要 vs 当前 HEAD e3c903c）：技能卡 17→16；测试 501→498；recipes 204→201；model_calib.py 2068→2410 行；cache_paged.py 874→1054 行；autotune 位于 onnx/quantization/ 之下。均为演进差异，以源码为准。
