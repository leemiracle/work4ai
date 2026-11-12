# 讲透 Megatron-LM（NVIDIA org · understand 全链 2026-11-05）

NVIDIA Megatron-LM 大模型分布式训练框架（megatron-core：张量/流水线/上下文/专家并行，预训练与后训练 RL）知识库。本仓为 NVIDIA org A 层战役第 5 仓，夜 2 完成。

## 全链状态表

| 阶段 | 状态 | 数据 |
|---|---|---|
| prepare | ✅ 11-04 | 1176 代码文件 → 78 批（tests/docs 裁剪；.claude/ 实为 14 空目录+1 settings.json 无内容，未收录） |
| 批分析 | ✅ 11-05 | 78/78 批，4 并发+1308 断点续跑（13:02 首灭 4 代理，b73 死前落盘验收采纳，19:40 新池续收 b74-78） |
| merge | ✅ | **4913 节点 / 11723 边**（53 悬空边归因：31 前缀错位回补 25 条、22 真缺失诚实弃——json 数据文件未入扫描集/docs+tests+.github 裁剪区/2 符号未提取） |
| layers/tour | ✅ | 16 层（1191 file 节点全覆盖零重复）/ 16 步导览（159 节点 16/16 层覆盖） |
| finalize | ✅ | 双 validator 0 issues/0 warnings，fingerprints 1176 文件@05fb87bc |
| onboarding | ✅ | 8 节 6581 字符（不计空格），36 个 path:line 锚全源码核实 |
| explain | ✅ | 12 篇 70360 字符 537 锚（组1 核心链路 6 篇 294 锚+组2 外围训练线 6 篇 243 锚），独立抽验 24 锚：19 好/4 basename 歧义归位/1 真坏已修（scheduler.py 15→17） |

图谱在仓内 `/usr-data/data2/repos/agent-repos/NVIDIA/Megatron-LM/.understand-anything/knowledge-graph.json`。

## explain 索引

- [01-parallel-state-并行基座](explain/01-parallel-state-并行基座.md) — 2773 行进程组中枢 TP/PP/CP/DP/EP/GTP
- [02-transformer-moe-核心](explain/02-transformer-moe-核心.md) — spec 层装配+MoE 全家桶+GTP 广义张量并行
- [03-deepseek-v4-特性线](explain/03-deepseek-v4-特性线.md) — DSA/CSA/mHC/MLA 进 mcore，DSV4_COMPRESS_RATIO_MAP{CSA:4,HCA:128,WINDOW:0}
- [04-hybrid-混合架构](explain/04-hybrid-混合架构.md) — Mamba/GDN/GDP 三 mixer+ops/gdp=fla v0.5.1 推理 fork
- [05-inference-引擎](explain/05-inference-引擎.md) — DynamicInferenceContext 5326 行+MTP 投机解码
- [06-推理服务栈](explain/06-推理服务栈.md) — quart 动态服务+新旧双栈+解析器家族
- [07-rl-训练线](explain/07-rl-训练线.md) — rollout 五阶段+agent 契约+反射注册表
- [08-fsdp-分布式优化](explain/08-fsdp-分布式优化.md) — vendored fsdp 双路导入+NVSHMEM 256MB×4 双缓冲
- [09-checkpoint-体系](explain/09-checkpoint-体系.md) — schema 四级继承+convert 插件反射
- [10-tokenizer-家族](explain/10-tokenizer-家族.md) — 三层门面+gigatoken 热切换
- [11-examples-多模态线](explain/11-examples-多模态线.md) — mimo 异构/NVLM/modelopt conf 动态 source
- [12-基建与协作资产](explain/12-基建与协作资产.md) — CI 双轨+skills 生态+AGENTS≡CLAUDE

## 源码级勘误清单（批分析+explain 甄别汇总）

1. `.claude/skills/` 14 个目录全空——"NVIDIA 内部 30+ skills"在 Megatron 仓不成立（TRT-LLM 另核）
2. `AGENTS.md` 与 `CLAUDE.md` diff 逐字节一致（孪生双入口）；hybrid/ 下另有一对同款孪生
3. `pyproject.toml` classifier 代差：仍列 Python 3.10/3.11+BSD，与 requires-python>=3.12+Apache 2.0 矛盾
4. CI 笔误两处：`--platform dgx_gb2100` 疑似 gb200 且产物被同名覆盖永不生效；`CLUSTER_GB200` description 误写 "H100 workloads"
5. CI artifact 悬空：`functional-test-job-dev-GB200.yaml` 从未生成但被 trigger include 引用；legacy 两份单测 YAML 无消费方
6. 悬空示例群：tasks/msdp 六脚本引用已删目录（git 三重验证）；tools/checkpoint 的 BERT 回退分支断链；detxoify_lm finetune 入口上游已删
7. `kitchen.py` 是 Kitchen 未发布扩展的 MagicMock stub（HAVE_KITCHEN 恒 False）
8. audio 包生产零消费（仅单测引用；mimo 用自有 audio 子模块）；nemo_transformer_encoder 的 GPTConfig/手写 MHA 为上游逐字保留死代码
9. `muon.py` 纯 shim（并入 get_megatron_optimizer 分支）；`torch_layer_norm.py` 4 行重导出 shim；mamba 系多文件为 models/hybrid 迁移后兼容垫片
10. TRTLLMHelper 转发漏传 `reduce_fusion` 参数（调用面缺口）；`HFDatasetAgent` 引用未声明 `self.split`
11. 笔误嫌疑：`qwen_3_32b.sh` tokenizer 挂 Qwen3-4B；Qwen2.5-0.5B-Instruct.sh 默认指向 base 模型；`install_nccl.sh` shebang 在许可头后非首行
12. `${that sGOLDEN_DIR}` 坏变量替换（bisect.sh:69）；`${DATA_BLEND}`/`${LOAD_NAME}` 未定义变量（遗留 bug）
13. skills 生态矛盾：mcore-cicd/bump-base-image BENCHMARK=FAIL 与 skill-card "ready for use" 声明冲突；Tier 3 活体评估全缺
14. `batch_invariant_kernels` 版权源自 Thinking Machines batch_invariant_ops（非 NVIDIA 原创）；`async_stream.py` 采自 vLLM（Apache-2.0）
15. scanner 盲区实录（工具链资产）：stdlib `import logging` 误解析仓内同名文件 17+ 条假边；tree-sitter 对 try/quart async 端点全盲；tools/ sys.path 注入型导入大面积漏（b28 单批手补 31 条）

台账：`/usr-data/data2/repos/agent-repos/deepwiki-batch/understand-nv-a-layer.md`
