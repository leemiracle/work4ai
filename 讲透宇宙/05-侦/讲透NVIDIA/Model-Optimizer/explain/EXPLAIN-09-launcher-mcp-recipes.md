# EXPLAIN-09 · 作业执行与配方体系：tools/launcher + tools/mcp + modelopt_recipes

## 一、角色定位

这三个目录构成 Model-Optimizer 的**运行自动化层**：**tools/launcher** 是作业提交器（README.md:3："Submit ModelOpt quantization, training, and evaluation jobs to Slurm clusters or run them locally with Docker"），输入 pipeline YAML 产出 Docker/Slurm 上的 nemo_run 实验；**tools/mcp** 是 agent 门面（mcp README.md:3："exposing the ModelOpt launcher as typed tools for codex / Claude Code agents"）；**modelopt_recipes** 是配方库（README.md:7："single, version-controlled source of truth"）。链路：**recipe（内容）→ launcher YAML（编排）→ MCP 工具（agent 入口）**；同一 recipe 驱动 `load_recipe`/`--recipe`/内置 `*_CFG` 三端（README.md:12）。

## 二、内部结构

**launcher**（core.py 899 行 + launch.py 186 行 + slurm_config.py 109 行）：launch.py 是入口（:16 docstring，:22-29 环境变量），启动即注册 `set_slurm_config_type` + `register_factory("slurm_factory",...)`（launch.py:49-50），是 YAML `_factory_` 反序列化前提（core.py:100）。core.py 内核：`SandboxTask`（:111）+ Task0-4 定长槽（:134-156）+ `SandboxPipeline`（:234）；`create_task_from_yaml`（:159）在 :170 弹 `_factory_` 调工厂。`run_jobs`（:737）按 `hf_local` 分流（:805-806 Docker / :818 Slurm）包进 `run.Experiment`（:778）；`build_docker_executor`（:590）把 hf_local 挂 `/hf-local`（:605）并以宿主 uid:gid 跑（:627-629）。slurm_config.py：`SlurmConfig`（:31）与 `slurm_factory`（:69）。common/ 是打包上集群的脚本库，launch.py:100-101 交 `run.PatternPackager`（:111）；dev checkout 自动建 `modules/Model-Optimizer` 符号链接并打包源码与子模块（:70-76、:103-109）。

**mcp**（server.py 603 行 + bridge.py 2384 行）：`_build_server`（server.py:48）注册 **9 个 typed 工具**（参数全 `Annotated[..., Field]`）：`list_examples`（:56）、`verify_setup`（:69 探活，MFA 走 ControlMaster :107-115）、`submit_job`（:143，hf_local/cluster_host 互斥定模式，:300-321 dry_run 只验 YAML）、`job_status`（:348）、`job_logs`（:370）、`wait_for_experiment`（:397）、`provision_passwordless_ssh_dry_run`（:442 只打印命令不碰密码）、`read_cluster_artifact`（:489 经 tunnel 读集群产物）、`open_draft_pr`（:534）。**勘误：server.py:21-26 docstring 仍写"Phase 1"只列 5 个，权威清单在 SCOPE.md:92-95（9 个）。** stdio 传输（:591-599）。bridge.py 是"Thin Python bridge"（:16-31，"deliberately doesn't expose anything the MCP tools don't need"）；提交前按 `source_ref` 物化受管 checkout（:394 → 按 SHA 建缓存 :440 → 物化+子模块 :456 → `uv run --project ...`，mcp README.md:73）。

**modelopt_recipes**：`configs/` 是积木——numerics/ **17 个量化器属性文件**（实测：fp8/int8/int4_per_block/mxfp4/mxfp8/mxint8/nvfp4 系列/iq 系列）+ ptq/units//presets/，"Not run directly"（README.md:43-48）。nvfp4.yaml 范本：:18 `modelopt-schema` 声明 `QuantizerAttributeConfig`，:19 `num_bits: e2m1`，:20-23 `block_sizes: {-1:16, type:dynamic, scale_bits:e4m3}`，:26 `effective_bits: 4.5` 供 autoquant。四级 `general/`/`model_type/`（13 架构）/`timm/`/`models/` fallback（README.md:56）；`model_type/` 前身 `huggingface/` 靠链接+别名兼容（:50）。ptq.md（560 行）必读：命名语法 `<formats-scope>-<kv-mode>[-<algorithm>].yaml`（:19），full-model/scoped/weight-only/KV-cache 分章（:77/:90/:121/:155），:258 怎么选，:440 checkpoint 镜像。

## 三、外部连接

- **nemo_run**：执行层全架其上（launch.py:39/:111）。
- **Megatron-LM**：git 子模块（launch.py:104-106）。
- **HF Hub**：SLURM_HF_LOCAL/HF_TOKEN（launch.py:27-28）+ `/hf-local` 挂载（core.py:605）。
- **codex / Claude Code**：`claude mcp add modelopt -- uvx ... modelopt-mcp`（mcp README.md:40-42）。**两包都不在 PyPI**（README.md:82）。
- **modelopt 主库**：recipes 由 `modelopt.recipe.load_recipe`（recipes README.md:20-21）加载。

## 四、数据流

典型 Slurm PTQ 全链：

1. **选配方**：按 README.md:56 顺序查 models→model_type→general；读 ptq.md:258 决策。
2. **pipeline YAML**：`examples/Qwen/Qwen3-8B/megatron_lm_ptq.yaml` 三任务流水（头注释 :1-16：task_0 NVFP4 量化+MMLU+export、task_1 FP8、task_2 TRT-LLM 评测）；每任务 `script: common/megatron_lm/quantize/quantize.sh`（:25）+ `QUANT_CFG: NVFP4_DEFAULT_CFG`（:30-31）+ `slurm_config: {_factory_: "slurm_factory",...}`（:39-40）；共享值 `<<global_vars.X>>` 插值。
3. **提交**：`launch()`（launch.py:125-134）→ `run_jobs`（core.py:737）构建 executor 调度；`--dryrun` 只预览。
4. **agent 路径**：`list_examples` 发现 → `verify_setup` 探活（server.py:73-75 明说不探测就烧 30+ 秒）→ `submit_job` 拿 experiment_id → `wait_for_experiment` 等终态 → `job_status`/`job_logs`（读 `_DONE` 与 `status_*.out`，server.py:351-354）→ `read_cluster_artifact` 取产物 → `open_draft_pr`。工具全返回 `{ok, reason, diagnostic}`（server.py:28-30）。

## 五、设计决策

1. **MCP 边界政策成文**：SCOPE.md 是仓内 agent 工程宪法——MCP 只放"环境工具"（跨工作流原语），工作流策略放 SPEC+agent 推理（SCOPE.md:8-14）；:21-27 对照表（✅ `submit_job(...)` vs ❌ `bench_eagle3_against_baseline()`）；:29-41 错位症状；:68-80 加新工具四问。理由 :49-54：目录可学习→少幻觉，工具描述即文档、schema 即契约。
2. **纯桥不掺业务**：9 工具 1:1 映射 `*_impl`（bridge.py:29-31）。
3. **凭据红线**：MCP 线上不碰密码——免密工具只打印命令（server.py:444-459），verify 用 BatchMode 拒密码（:80-82）。
4. **受管 checkout 按 SHA 键控**（mcp README.md:70-76）：多 agent 不同分支各得独立源码根。
5. **launcher 与 MCP 解耦**：MCP 是薄包装（README.md:9），人用 launch.py、agent 用工具，同归 `run_jobs`。
6. **recipe 三端同源+$import**：17 个 numerics 积木拼上百 preset；`modelopt-schema`（nvfp4.yaml:18）让 YAML 与配置类互查。
7. **Docker 产物不落 root**（core.py:627-629）。

## 六、新人提示

- 第一次跑：本地 Docker `uv run launch.py --yaml examples/Qwen/Qwen3-8B/megatron_lm_ptq.yaml hf_local=/mnt/hf-local --yes`（launch.py:20）；先 `--dryrun --yes -v`。Slurm 前置设 launch.py:22-29 变量。
- agent 配 MCP：一条 `claude mcp add`（mcp README.md:40-42）；别用 pip，`[tool.uv.sources]` sibling 依赖会解析失败（README.md:82）。
- 结构约束：SandboxPipeline 只有 task_0..4 五槽+tasks 列表（core.py:239-244）。
- 选 recipe 入口是 ptq.md 不是 ls：先读 :258 与 :19 命名语法。
- YAML 校验免费通道：`submit_job(dry_run=True)` 不碰集群不起容器（server.py:302-318）。
- 坑：typed task 半成品——megatron_lm_ptq.yaml 头注释 :12-14 明说 `MegatronLMQuantizeTask` 未接进 SandboxPipeline。
- 坑：server.py docstring 滞后，工具清单以 SCOPE.md:88-95 为准。
