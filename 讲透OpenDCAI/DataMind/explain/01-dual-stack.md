# 01 · 双栈心智：datamind/ 新栈与仓根 legacy 原型并存

## 角色定位

DataMind 仓同时躺着两套完整栈：**新栈** `datamind/` 包（pydantic 嵌套配置、Registry 插件体系、Codex 宿主），**旧栈** 仓根 `config.py` + `modules/`（v0.1 LlamaIndex 原型）。判别极简：`import datamind` 是新栈，`from config import settings` 是旧栈。仓根三个 `.py` 全是转发兼容壳——头行即自证：`main.py:1` `"""Compatibility launcher for the unified Codex CLI (DataMind 2.0)."""`，`server.py:1` 同款 HTTP/UI 壳，`benchmark.py:1` `Compatibility shim`；真身在 `datamind/cli.py`、`datamind/server.py`、`benchmark/run.py`。新人第一课：先确认文件属于哪栈，别把旧栈 LlamaIndex 依赖当新栈必需。

## 内部结构

新栈是嵌套配置树：`datamind/config.py:288` 的 `Settings` 聚合 llm/codex/workspace/embedding/retrieval/kb/graph/db/memory/data/logging/agent/hooks 子节，环境变量 `DATAMIND__` 前缀 + 双下划线（`datamind/config.py:305-312` `SettingsConfigDict(env_prefix="DATAMIND__", env_nested_delimiter="__")`），例 `DATAMIND__LLM__API_BASE`。旧栈平铺单层：仓根 `config.py:26` 一个 `Settings(BaseSettings)`，`llm_api_base`/`retriever_mode` 等字段直映同名大写环境变量（`config.py:8-11`），`.env` 单文件（`config.py:83`）。旧栈 modules 五件套：`modules/agent/agent.py:14` 用 `llama_index` FunctionAgent 统整工具，`modules/rag/indexer.py:22-29` 直 import llama_index core + ChromaVectorStore，依赖锁在 `requirements-legacy.txt`（首行注释 "Legacy v0.1 compatibility dependencies only...retained so the original...prototype can still be reproduced"）。

## 外部连接

两栈唯一物理连接是仓库根：新栈 `_REPO_ROOT`（`datamind/config.py:31`）与旧栈 `base_dir`（`config.py:59-61`）都锚在仓根。互不干扰是刻意的——`datamind/config.py:18-19` 明写 "Legacy flat vars...left untouched for the old modules/* codepath."。benchmark 也双轨：根壳 `benchmark.py:5` 还在 `sys.path.insert(0,...)`，`benchmark/run.py:1` 自述 "runner for the current `datamind/` stack"。版本号只新栈有：`datamind/__init__.py:2` `"2.1.0"`。

## 数据流

新栈：入口（CLI/MCP/HTTP）→ `Settings` → `assemble_data_plane` 组服务 → Codex 宿主或直调工具。旧栈：`config.settings` 单例 → modules 自建 Chroma/LlamaIndex 索引 → FunctionAgent 挑工具（`modules/agent/agent.py` 头注释：knowledge_search/graph_search/database_query/skill_search 分流）。data 目录布局一脉相承：旧栈 `data/profiles/{data_profile}/`（`config.py:66`），新栈 `data/profiles/<profile>/`（`datamind/config.py:169`）——profile 概念从 v0.1 延续到 v2.1。

## 设计决策（含批判）

保留 legacy 是"可复现原型"策略：不删代码、单独锁 requirements；代价是双份索引逻辑与双套配置心智。**批判**：①`.env` 两栈都读，新栈里 `.env.datamind` 后读优先（`datamind/config.py:306-307` "later entries take precedence"），迁移期同名键易配错栈；②旧栈平铺 import 要求从仓根跑，pip 安装与 checkout 并存时行为分叉；③兼容壳无弃用告警，旧教程会把新人引到壳上。

## 新人提示

跑新栈永远 `python -m datamind` 或 `pip install -e .`；见 `import config`（非 `datamind.config`）即旧栈文件。配置先问哪套：`DATAMIND__EMBEDDING__MODEL` 新栈，`EMBEDDING_MODEL` 旧栈。读码跳过仓根三壳直进 `datamind/`；benchmark 用 `python -m benchmark.run`。仅复现 v0.1 实验时才 `pip install -r requirements-legacy.txt`。
