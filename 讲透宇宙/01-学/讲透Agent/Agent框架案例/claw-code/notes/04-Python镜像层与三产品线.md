# 04 · Python 镜像层与三产品线

> card_id: claw-code-04
> universe: Agent框架案例
> burke: 场景=一夜 Python 重写与 Rust 正典并存；主体=src/ 镜像工作区 + claw-analog + claw-rag-service；能动=镜像优先移植法；行动=快照对账+NDJSON 合同+旁路 RAG；目的=可审计可复现的移植；张力=镜像不是替身 vs 必须先跑起来；弧线=主角→伴生参考区→方法论遗产
> status: 已完成（2026-08-20，HEAD `08106b0`）
> refs: src/ 68 文件 + claw-analog/claw-rag-service 源码实测；concept.md/how_to_run.md（俄语）
> updated: 2026-08-20

## 1. `src/`：镜像优先的移植工作区（68 个 .py，632K）

**定位演变**：README.md:111——"src/ + tests/ 是伴生 Python/参考工作区与审计助手，**不是主运行面**"。它从 4 月 1 日的主角退位为坐标系。

三层结构（魔都水滴框架 + 本地实证）：

1. **镜像数据层** `src/reference_data/`：commands_snapshot.json / tools_snapshot.json / archive_surface_snapshot.json + **subsystems/ 29 份 JSON 快照**（assistant/bootstrap/bridge/**buddy**/cli/coordinator/hooks/memdir/native_ts/screens/skills/state/voice/vim…每份对应泄露 TS 的一个子系统）——原版结构先变成**数据**再谈实现。
2. **对账层**：`port_manifest.py`（52 行，扫描 src/ 统计模块聚合为 Markdown）；`parity_audit.py`（138 行）：17 个根文件映射（QueryEngine.ts→QueryEngine.py 等）+ 35 个目录映射；输出根文件覆盖/目录覆盖/命令条目/工具条目四组比值。**关键品格**（parity_audit.py:85-88）：archive 不在本地时直接说"无法比较"——不把缺数据伪装成没差异。
3. **骨架引擎层**：`query_engine.py`（200 行）的 `QueryEnginePort`——max_turns=8 / max_budget_tokens=2000 / compact_after_turns=12 的小引擎：submit_message 产出 TurnResult（matched_commands/tools/permission_denials/usage/stop_reason）、stream_submit_message 产出 message_start→delta→stop 事件流、compact/persist/replay 全套接口。**它不调真 LLM——是引擎形状的镜像**（turn 结果/流事件/拒绝追踪/转录持久化每块都有），供对账与测试用。`commands.py`/`tools.py` 从快照构造 PortingModule，`execute_command()` 的语义是"这个镜像命令若存在会由哪条目处理"——**镜像执行而非真实执行**。

> 方法学结晶（可直接搬到任何"重写闭源系统"任务）：**代码可以先是镜像，不必先是替身；模块可以先是骨架；审计先衡量覆盖而非假定等价；runtime 先能报告再慢慢能执行。**

## 2. claw-analog：给 CI 和外部 agent 的极简面（concept.md 产品线 2）

同一 `api` crate 之上的瘦壳（lib.rs 87 个 fn；how_to_run.md 整篇俄语——贡献者地理分布的活证据）：

- **默认只读**（lib.rs:342 `default (read-only)`）；危险模式在非交互下硬阻断，除非 `--accept-danger-non-interactive`（:50）。
- **NDJSON 稳定合同**：`NDJSON_SCHEMA="claw-analog-ndjson"` / `NDJSON_FORMAT_VERSION=1`（:239-241）——run_start 带 schema+format_version，tool_result 结构化；**给外部 agent 消费的事件协议**（"Observability for agents"）。
- 工具面窄而显式：read_file/list_dir/glob_workspace/grep_workspace + 可选 write_file + **`retrieve_context`**（:670/:879/:987：设 `RAG_BASE_URL` 时暴露，POST {base}/v1/query，ReadOnly 权限）。**MCP/plugins/bash 不进极简面**——攻击面收敛是设计目标（concept.md §6）。
- `doctor` 子命令自成一派：配置合并预览（CLI/TOML/default 谁胜出的 provenance）、env 只报 set/unset 不报值、`--tcp-ping` 探 ANTHROPIC_BASE_URL、`--no-build`/`--release-build` 避免 Windows 嵌套 cargo 的文件锁——**每个坑都有旗标**。
- 预设：`audit` preset 的系统提示要求"优先安全/正确/可疑模式，引用文件路径与证据，倾向只读调查"（:141）——**安全审查作为产品模式**。

## 3. claw-rag-service：重索引移出 agent 进程（concept.md 产品线 3）

- 独立进程：`ingest`（全量重建索引：chunks+embeddings 入 SQLite）+ `serve`（axum HTTP：`/health` `/v1/stats` `/v1/query`）+ 最小 web UI 人工查验。
- 向量存储：SQLite 线性余弦（MVP）→ 可选 Qdrant（qdrant_index.rs）——"先线性后 ANN"的诚实演进路线。
- 架构原则（concept.md §3 原图）：**重索引与 embedding 密钥不进 agent**，agent 只持 HTTP 客户端——与 MCP 外置工具同构，但更彻底：连数据带算力全在服务侧。

## 4. 三产品线的切分逻辑

```
claw (全量 CLI, 55 工具, REPL/一次性/JSON)   ← 开发者日常
claw-analog (只读默认, NDJSON, audit preset) ← CI/脚本/外部 agent 编排
claw-rag-service (旁路索引/检索)             ← 重 IO 与密钥隔离
```

判据（concept.md §4）：安全默认/显式限额/agent 可观测/模块共享/parity 测试。**同一 api/runtime 底座上按"使用者是人/是机器/是服务"切面**——比"一个 CLI 加一堆 flag"的常见做法干净得多。

## 5. 与 work4ai 的接口

- `讲透RAG` 系列可引 claw-rag-service 作"RAG 服务化"最小实现样本（SQLite 线性余弦→Qdrant 的升级路径即讲透 RAG 的检索底座章节大纲）。
- deepseek 五 harness 里的 rl/llm 冒烟三级降级与 claw-analog 的 doctor/NDJSON 合同同族——**"agent 消费的机器可读合同"在两个项目里独立收敛**，可作为讲透Agent 的通用模式条目。
