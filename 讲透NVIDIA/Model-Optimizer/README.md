# 讲透 NVIDIA Model-Optimizer（ModelOpt）

NVIDIA Model Optimizer（`nvidia-modelopt`）：torch / TensorRT / ONNX 全栈模型量化压缩框架。本目录是 understand-anything 流水线全链知识基座（图谱+导览+onboarding+10 篇 explain），仓库本体位于 `/usr-data/data2/repos/agent-repos/NVIDIA/Model-Optimizer`（只读；HEAD `e3c903c`，2026-10-01，"Deprecate TensorRT-LLM model_type in favor of Hugging Face model_type #2569"）。

本仓是 **agent-first 第十例**：AGENTS.md 与 CLAUDE.md（符号链接）为协作总纲，16 张技能卡+6 个子代理+9 个 MCP 工具构成 agent 可直接驱动的量化工作流。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| 批分析+merge（上游会话） | ✅ | assembled-graph 10540n/23823e |
| layers | ✅ | 16 层，file 级 2194/2194 全覆盖零重复 |
| tour | ✅ | 16 步 104 nodeIds |
| finalize | ✅ | validator 0 issues 0 warnings；fingerprints 2194 files @e3c903c4 |
| onboarding | ✅ | `onboarding/ONBOARDING.md` 11971 字 8 节 61 锚 |
| explain | ✅ | 10 篇，合计 64,804 字（不计空格），515 锚（压缩轮后终态） |
| README（本文件） | ✅ | 状态表+甄别清单 |

图谱：`/usr-data/data2/repos/agent-repos/NVIDIA/Model-Optimizer/.understand-anything/knowledge-graph.json`（10540 节点/23823 边/16 层/16 步 tour；fingerprints 基线支持增量更新）。

## 16 层导览（layers）

| 层 | 名称 | 节点数 | 一句话 |
|---|---|---|---|
| L01 | 仓库治理与文档基座 | 112 | 根文件/CI/多 agent 入口/docs 手册 |
| L02 | Agent 技能插件体系 | 109 | plugins/modelopt：16 技能卡+6 子代理+三插件入口 |
| L03 | torch 量化主线 | 101 | quantization 包（model_quant/model_calib/nn/qtensor）+opt 编排 |
| L04 | torch 压缩族 | 107 | sparsity/nas/prune/distill/peft/fastgen |
| L05 | torch utils | 33 | 模型遍历/换装/save-load 地基 |
| L06 | torch kernels | 48 | 量化 GEMM CUDA 核+triton attention |
| L07 | torch models | 48 | HF 模型发现与配置映射 |
| L08 | export 链路 | 72 | ONNX 导出+trtllm 配置+部署模拟 |
| L09 | speculative decoding | 41 | medusa/eagle/dflash 三族 |
| L10 | puzzletron | 109 | MIP 局部 NAS 结构剪枝（arXiv 2411.19146） |
| L11 | onnx 与发布通道 | 77 | ONNX PTQ CLI+autotune+recipe/deploy |
| L12 | experimental DMS | 33 | 可学习 KV 逐出（arXiv 2506.05345） |
| L13 | tools 工具链 | 151 | launcher（SLURM/Docker）+MCP+debugger |
| L14 | modelopt_recipes | 204 | yaml 配方库：numerics/general/model_type/models |
| L15 | tests | 501 | unit/gpu/上游引擎集成 |
| L16 | examples | 448 | 全谱系用法样例 |

## explain 索引（10 篇）

字数=不计空格总字符；锚=唯一 `文件:行号` 引用数（压缩轮后终态；主会话批量终验 613 处界内 0 坏，含 36 处定向消歧，23 处歧义锚正文语境自明）。

| 篇 | 主题 | 字数 | 锚 |
|---|---|---|---|
| EXPLAIN-01 | torch 量化主线（quantize/calibrate/auto_quantize 全流程） | 9567 | 91 |
| EXPLAIN-02 | PTQ 校准算法中枢（max/MSE/SmoothQuant/AWQ/GPTQ/LSQ…） | 9796 | 108 |
| EXPLAIN-03 | FP8+NVFP4 真实量化张量与 GEMM 后端 | 9862 | 88 |
| EXPLAIN-04 | kernels：量化算子的 CUDA/triton 落地 | 5033 | 27 |
| EXPLAIN-05 | TensorRT/TRT-LLM 导出线与世代交替 | 5389 | 15 |
| EXPLAIN-06 | ONNX 量化与 Q/DQ 自动调优 | 5539 | 20 |
| EXPLAIN-07 | DMS 可学习 KV cache 逐出 | 4721 | 65 |
| EXPLAIN-08 | Puzzletron MIP 结构剪枝 | 4847 | 36 |
| EXPLAIN-09 | launcher+MCP+recipes 作业自动化链 | 4926 | 37 |
| EXPLAIN-10 | agent-first 插件与技能卡体系 | 5124 | 28 |

**字数口径**：任务书区间 2500-4800；压缩轮后 04-10 已落 4.7-5.5K（贴上沿），01/02/03（9.6-9.9K）因任务覆盖面（七算法族/十文件/双路径）+锚密度（88-108 锚/篇）在 4800 内无法同时保住锚量与勘误，系系列口径漂移（历轮 4.8K-10K 常态），采信口径=不计空格总字符。ONBOARDING 11971 字在 6000-12000 区间内。

## 甄别清单（源码实证勘误，读本知识库前必看）

### A. 演进时点计数漂移（图谱计数 vs HEAD 实测，以源码为准）

1. 技能卡 **16 张**（15 技能+common），图谱摘要作 17；`ls plugins/modelopt/skills` 实证。
2. tests 实测 498 文件（图谱 501）；modelopt_recipes 实测 201 文件=188 yaml+13 md（图谱 204）；qtensor 实测支持 **7 种**量化张量格式（含任务书清单未列的 nf4）+ base；examples/puzzletron 实测 77 文件（任务书 76）。
3. `model_calib.py` 实为 **2410 行**（图谱摘要 2068）；`model_quant.py` 1168 行（摘要 983）；DMS `cache_paged.py` 1054 行（摘要 874）——多文件行数在批分析与 HEAD 间有漂移，锚已按 HEAD 重新核实。

### B. 任务书/直觉错误被源码纠正（写入各篇正文）

4. **NVFP4 默认 block=16 非 32**（`modelopt_recipes/configs/numerics/nvfp4.yaml` 的 `block_sizes: {-1: 16}`；block-32 是变体 `nvfp4_bs32.yaml`）；且真算 GEMM 可用性检查只接受 16（`nvfp4_gemm.py:259-262`）。
5. **`config.py` 无 SearchSpace**：量化搜索空间真身是 `algorithms.py` 的 `QuantRecipe`（:278）与 `AUTO_QUANTIZE_SEARCHERS`（:2105）；配置类是 pydantic `ModeloptBaseConfig` 非 dataclass。
6. **FP8 真算后端生产路径不生效**：`fp8_per_tensor_gemm.py` 末尾有注册，但 `backends/__init__.py:18-19` 只导入 `gemm_registry` 与 `nvfp4_gemm`——NVFP4 是唯一默认挂载的真算 GEMM（EXPLAIN-03）。
7. **kernels 下无 `tensor_quant.cu`**：实为 `tensor_quant.cpp`（绑定）+ `tensor_quant_gpu.cu`/`_fp8.cu`/`_mx.cu`（kernel）；`fp4_kernel.py` 与 `fp4_kernel_hopper.py` 按 compute capability ≥8.9 分版（Blackwell 也走 ≥8.9 分支），非"Hopper/Blackwell 各一份"。图谱 T07 描述已同步修正。
8. **`fp8_kernel.py` 命名误导**：是 DeepSeek-V3 移植的权重反量化 kernel（双版权头 ：16-18），非 FP8 伪量化；FP8 伪量化在 `common/fp8_quant.py` 与 `tensor_quant_gpu_fp8.cu`。
9. **export/trtllm 处于世代交替**：旧 `export/trtllm/`（12 模块）0.48 弃用 0.49 删除（`model_config_export.py:90-94`）；新主线 `unified_export_hf.py` 统一 HF checkpoint（compressed-tensors `quantization_config`），一份产物喂 TRT-LLM/vLLM/SGLang 三家。
10. **MCP 工具权威清单在 SCOPE.md:88-101**：modelopt-mcp 本机注册 **9 个**（server.py `_build_server`）；SCOPE.md 标题行的"14 tools"是三台 server 合计（modelopt-mcp 9+nmm-sandbox-mcp 3+pensieve-intern-mcp 2），两数不打架；`server.py:21-26` docstring 仍写"Phase 1"只列 5 个，以 SCOPE.md 为准。
11. autotune 位于 `modelopt/onnx/quantization/autotune/`（quantization 子目录下），非 onnx 顶层。
12. puzzletron anymodel 实际支持 8 个模型族（gpt_oss/llama/mistral_small/nemotron_h×2/qwen2/qwen3/qwen3_vl）。

### C. 结构性甄别（防迷路）

13. **"plugins"双含义**：仓根 `plugins/`=agent 插件（技能卡/子代理）；`modelopt/torch/quantization/plugins/`=宿主框架适配（transformers/megatron/TE/vLLM 等 17 文件）。两处完全不同。
14. **agent-first 三级链接拓扑**：canonical 唯一编辑点=`plugins/modelopt/skills/`（16 目录）→ `.agents/skills` 是**目录级**符号链接（`../plugins/modelopt/skills`）→ `.claude/skills/` 是 **16 个逐技能**符号链接（Claude Code 只自动发现 `.claude/skills/` 且需逐卡链接）。`.claude/scripts`、`.claude/clusters.yaml.example` 亦链接入 `.agents/`；Codex 角色在 `.codex/agents/`。vendored-verbatim 技能（launching-evals/accessing-mlflow）由 `.agents/scripts/sync-upstream-skills.sh` 上游同步，禁手改。
15. **clusters.yaml 三级查找**：`~/.config/modelopt/` → 仓根 `.agents/`（canonical）→ `.claude/`（back-compat）。
16. CLAUDE.md 是 AGENTS.md 的符号链接（`ls -la` 实证）；协作铁律：PR<500 行源码增量、`git commit -s -S` 签名、禁止擅自 push、技能卡逐行省 token。
17. HEAD 正处 **TRT-LLM model_type → HF model_type 迁移期**（HEAD commit 本身），读旧配方/旧导出代码时注意。

## 命令速查

```bash
# 最小 PTQ（三行核心）
import modelopt.torch.quantization as mtq
model = mtq.quantize(model, mtq.INT8_DEFAULT_CFG, forward_loop)
model, state_dict = mtq.restore(model_calib, quantize_cfg)   # 见 EXPLAIN-01

# launcher 提交（SLURM/Docker）
uv run --project tools/launcher modelopt-launcher --yaml <pipeline.yaml>

# MCP 工具（agent 面向）
uvx --from "git+https://github.com/NVIDIA/Model-Optimizer.git#subdirectory=tools/mcp" modelopt-mcp

# DMS 训练/评估
accelerate launch -m models.qwen3.train -c configs/qwen3_8b.yaml   # experimental/dms
```

## 产出去向

- 本目录：`onboarding/ONBOARDING.md`、`explain/EXPLAIN-01..10`
- 图谱+fingerprints+PROGRESS 台账：仓内 `.understand-anything/`（knowledge-graph.json / fingerprints.json / meta.json / PROGRESS.md）
