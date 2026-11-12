# 讲透 RLBaselines3Zoo

> DLR-RM/rl-baselines3-zoo —— SB3 官方训练基建：超参 YAML 体系 + Optuna 调参 + CLI（train/enjoy）+ 基准复现。
> 本地仓：/usr-data/data1/workspace/rl/rl-baselines3-zoo（commit 3ef9b46，2026-10-01）

## 状态（2026-10-14 全链完成，实例 C）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ 完成 | [deepwiki/](deepwiki)（26 页 100%，276K 字符） |
| understand 中文图谱 | ✅ 完成 | 仓内 `.understand-anything/knowledge-graph.json`（**201 节点/389 边/15 层/16 步 tour**，校验 0 issues 0 warnings，fingerprints 80 文件@3ef9b463） |
| onboarding | ✅ 完成 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（5974 字 8 节 52 锚） |
| explain 系列 | ✅ 完成 | [explain/](explain) 12 篇（合计 80190 字符不计空白，420 个 file:line 锚**全量终验 0 坏**） |

## understand 图谱口径

- scan 80 文件（230 被 ignore 过滤：logs/rl-trained-agents/images/docs 裁剪；hyperparams/*.yml 13 调参矩阵全保留）/ 12 批 4 并发零重派
- merge 201n/382e → 8 条前缀错位悬空边手工回补 7 条（LICENSE 无节点弃 1）→ 389e
- 15 层（自底向上）：核心基座→训练扩展组件→实验编排核心(exp_manager)→包级命令模块→根入口壳→plots→CLI/基准→hyperparams 矩阵(14)→工程配置→Docker→scripts(12)→tests(10)→社区模板→CI/CD→顶层文档
- 边型：contains/exports/imports/configures(24: hyperparams→exp_manager+utils)/tested_by/triggers/deploys/depends_on/documents
- 12 个 layers 缺 id 字段 → onboard_prep.py 自动编号兼容（pipeline-bin 第三处 bug 修复钉版）

## explain/ 十二篇清单

| 篇 | 主题 | 核心源文件 |
|---|---|---|
| [01 CLI 总入口](explain/01-cli-entry.md) | 根壳→cli.py 分发→train | train.py · rl_zoo3/cli.py |
| [02 ExperimentManager](explain/02-exp-manager.md) | 训练编排核心（zoo 灵魂，1011 行） | rl_zoo3/exp_manager.py |
| [03 hyperparams YAML 体系](explain/03-hyperparams-yaml.md) | 13 算法调参矩阵语法 | hyperparams/*.yml |
| [04 Optuna 调参](explain/04-hyperparams-opt.md) | objective/Pruner/sampler | rl_zoo3/hyperparams_opt.py |
| [05 回调装配](explain/05-callbacks.md) | 四 zoo 回调+双装配路径 | rl_zoo3/callbacks.py |
| [06 评估 enjoy](explain/06-enjoy-evaluation.md) | 六段主流程/确定性三层 | rl_zoo3/enjoy.py |
| [07 工具枢纽](explain/07-utils.md) | create_test_env 装配链 | rl_zoo3/utils.py |
| [08 动态环境注册](explain/08-import-envs.md) | 8 外部包 try/except | rl_zoo3/import_envs.py |
| [09 训练曲线](explain/09-plots.md) | Monitor.csv→出图 | rl_zoo3/plots/ |
| [10 基准复现](explain/10-benchmark.md) | subprocess 并行+结果表 | rl_zoo3/benchmark.py |
| [11 HF 模型生态](explain/11-hub-ecosystem.md) | 上传/下载双向管线 | push_to_hub · load_from_hub |
| [12 录像](explain/12-record-video.md) | VecVideoRecorder 装配 | record_video · record_training |

## 本轮实证发现（源码钉版）

1. **her.yml 是 reference-only**：SB3≥1.1.0 起 HER 由 `HerReplayBuffer` 承担，ALGOS 无 her 键（三重证据：ALGOS 字典+图谱无 configures 边+tqc.yml:241-252 现代等价写法）
2. **benchmark 不走 cli.py 分发**：`python -m rl_zoo3.benchmark` 模块级脚本，parser 在 import 时执行（benchmark.py:16-27）
3. **train 与 enjoy 的 `-f` 默认值语义相反**：train=logs（写）/enjoy=rl-trained-agents（读）
4. **Monitor 在 wrapper 链最内层**（SB3 env_util.py:113 先包 Monitor、:116 后包 wrapper），AtariWrapper 等在 Monitor 外——奖励日志不受业务 wrapper 改写影响
5. **版本漂移坑**：wrappers.py velocity_indices 已升 LunarLander-v3，ppo_lstm.yml:163/182 仍写 v2——这两个键跑训练会在 registry 校验直接 not found
6. **off-policy 名单两处维护**：benchmark.py:54 与 enjoy.py:127
7. README L66 "hyperparameters/" 为上游笔误（实际目录 hyperparams/）
8. import_envs 动态注册 8 个外部 pip 包（pybullet_envs_gymnasium/ale_py/highway_env/panda_gym/minigrid 等），全部 try/except 静默降级

## deepwiki/ 目录说明

- 通道：mcp.deepwiki.com/mcp 官方端点直连（10:45 抓取 exit 0 一次过；**注意另一实例 10:52 复测 SB3 时撞 MCP 索引库不同步窗口**——MCP 死≠wiki 不存在）
- 10 章 26 结构页全命中，零 extra 零 MISSING；每页自带 `<details>` 源文件清单
- 入口：[deepwiki/INDEX.md](deepwiki/INDEX.md) · 对账：[deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)

## 生态交叉

- 姊妹仓讲透StableBaselines3（算法层，另一实例同日全链完成：634n/1681e/12层/16步+onboard+explain 12 篇）
- 讲透Gymnasium（环境标准层，另一实例同日：1153n/2819e+onboard+explain）
- 三仓合成 SB3 全家桶知识基座：算法本体→训练基建（本仓）→环境 API
