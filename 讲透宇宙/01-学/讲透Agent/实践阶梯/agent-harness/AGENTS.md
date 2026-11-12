# AGENTS.md — 端侧事实记忆 Agent · 开发宪法

> 本文件给**开发本项目的 AI 编码会话**（opencode 等）读。
> 来源：learn-harness-engineering 五子系统之 Instructions（会话生命周期见 progress.md 头部）。

## 项目是什么

CPU-only 端侧 agent：Qwen2.5-0.5B 从中文话语抽取事实存 memory + 意图识别。
设计文档：`../00-需求与架构决策.md`（矫正分层 + 速度预算，改动前必读）。

## 环境（开发-运行分离）

- **开发侧**（本机）：写脚本到 `../experiments/`，git 仓库根在 `work4ai/`
- **运行侧**：内部服务器 docker 容器（96 核 CPU），容器内 `/work/` = 宿主 `/root/工作容器/`
- 模型：容器内 `/work/models/Qwen2.5-0.5B-Instruct`（f32，954M）——**模型/日志绝不进 git**
- 部署命令：`scp <脚本> root@<server>:/root/工作容器/experiments/` → `docker exec -d 工作容器 bash -c "cd /work/experiments && python3 <脚本> > <log> 2>&1"` → 轮询 `docker exec 工作容器 cat /work/experiments/<log>`

## 硬约束（违反 = 返工）

1. CPU-only，`torch.set_num_threads(4)`（实测多线程无收益）
2. 贪心解码（do_sample=False）：一切结论必须可复现
3. 生成预算：单次 ≤150 token，重试 ≤1 次（7 tok/s 的速度预算）
4. 评估只用固定任务集（`../experiments/` 内 DATASET），禁止边看结果边改任务集
5. 任何"变好了"的声称必须有版本对照数字支撑

## 会话生命周期（每次会话严格遵守）

```
START   读本文件 → 读 progress.md → 读 feature_list.json → cat 最新 log
SELECT  只挑一个 in-progress 的 feature
EXECUTE 写/改代码 → 容器跑 → 回收日志存档 experiments/
WRAP UP 更新 progress.md（含实测数字）→ feature 状态推进 → 失败也记录
```

## 代码约定

- 校验器三件套（parse_json/validate/collapse_count）定义在 01_l1_bare_loop.py，后续脚本 import 复用，禁止复制分叉
- 指标名固定：json_rate/cat_ok/grounded/collapse/hallu/pass（定义见 00 章 §三）
