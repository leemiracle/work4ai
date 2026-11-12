# 09 · 配置全家族 48：四层 JSON 家族 + 25 个 MCP YAML 的秩序与断链

> 所属仓库：OpenDCAI/AgentFlow（图谱 909 节点/1857 边）。AgentFlow 的全部配置恰好 **48 份**：`configs/sandbox-server/` 7 份 + `configs/infer/` 4 份 + `configs/trajectory/` 4 份 + `configs/synthesis/` 8 份 + `sandbox/server/backends/resources/mcp/configs/` 25 份 YAML。本篇做全家族盘点——它们彼此的层级关系、两套不同的占位符体系、以及散落各处的断链。

## 一、角色定位

48 份配置分成两个世界：

- **configs/ 四子目录 23 份 JSON**——按"消费者"分层：sandbox-server 层（沙箱服务怎么起）、synthesis 层（造数据怎么跑）、infer 层（跑基准评测）、trajectory 层（纯采集轨迹）。同一域（doc/ds/rag/web）在每层各有一份，名字同前缀。
- **MCP configs/ 25 份 YAML**——归 sandbox 的 mcp 资源后端私有（Toolathlon-GYM 生态），描述 25 个 MCP stdio 子进程怎么拉起。

分层的价值在于**关注点分离**：换被测模型只动 infer 层；换数据供应商只动 sandbox-server 层；造数据的提示词只在 synthesis 层。四层之间靠文件路径互相引用（如 infer/ds_infer.json 的 `sandbox_config_path: "configs/sandbox-server/ds_config.json"`），没有中心化注册表——路径写错就是运行时才炸。

## 二、内部结构

### 第一层：sandbox-server 七配置——两种形态

七份配置分两类骨架：

**`apis` 型**（无会话状态的 API 后端）——doc_config.json（apis.doc）、ds_config.json（apis.ds）、text2sql_config.json（apis.text2sql）、web_config.json（apis.websearch）。特点：没有 `backend_class` 字段、没有 `warmup` 段，起服务即用。doc_config.json:19-28 配 VLM 问答（`vlm_model: openai/gpt-4o-mini`+`${VLM_API_KEY}` 走 OpenRouter），web_config.json:23-31 配 serper 搜索+jina 访问+LLM 摘要三件套。

**`resources` 型**（有状态资源+动态类加载）——GUI_config.json（resources.vm）、mcp_config.json（resources.mcp）、rag_config.json（resources.rag）。骨架统一是：

```json
"resources": { "<name>": {
    "backend_class": "sandbox.server.backends.resources.vm.VMBackend",
    "config": { ... 展开环境变量后的参数 ... } } },
"warmup": { "enabled": true, "resources": ["vm"] }
```

`backend_class` 是完整 Python 路径，config_loader.py:289 用 `importlib.import_module` 动态定位、config_loader.py:334-357 实例化——没有 backend_class 的资源直接告警跳过（config_loader.py:357）。三份分别指向 VMBackend（Docker 桌面自动化，GUI_config.json:12-30）、ToolathlonGymBackend（mcp_config.json:11，默认只开 filesystem/terminal/snowflake 三台 MCP，mcp_config.json:15）、RAGBackend（E5+Faiss 双卡布局，rag_config.json:14-20 的 device 注释写明 `cuda:0/cuda:1` 表示编码器与索引分卡）。

**凭据纪律**：七配置的敏感值**全部**走 `${VAR}` 或 `${VAR:-default}` 占位——`vlm_api_key: ${VLM_API_KEY}`（doc_config.json:24）、`${SERPER_API_KEY}/${JINA_API_KEY}`（web_config.json:25-26）、RAG 三路径 `${RAG_EMBEDDING_MODEL_PATH}/${RAG_INDEX_PATH}/${RAG_CORPUS_PATH}`（rag_config.json:24-26，注释明言"avoid committing absolute paths"）、text2sql 七个库路径全 `${TEXT2SQL_*_DB_PATH:-}` 空默认（text2sql_config.json:15-23）。展开由 `expand_env_vars`（config_loader.py:44-84）递归完成：正则 `\$\{([^}:]+)(?::-([^}]*))?\}`（config_loader.py:60），未设置且无默认时**保留原占位符并告警**（config_loader.py:73-74）而非硬崩。

但注意三个"有默认值的凭据"：`client_password: ${VM_CLIENT_PASSWORD:-password}`（GUI_config.json:27）与 mcp 的 `PGUSER:-eigent`/`PGPASSWORD:-camel`（mcp_config.json:19-20）——兜底默认是弱口令/明文，内网演示方便，生产环境等于没设防。

### 第二层：infer 四配置——待测模型的考场

四份骨架一致：`model_name/api_key/base_url`（全占位：`YOUR_MODEL_NAME`、空 api_key、`VLLM_URL`）+ `available_tools` + `system_prompt`（JSON 数组逐句拼接）+ 评测段 + 数据路径。差异在评测指标：doc 用 `MMLongBench-Doc_LasJ`（doc_infer.json:27）、ds 用 `exact_match`（ds_infer.json）、rag 用 `f1_score`（rag_infer.json）、web 用 `contains_answer`（web_infer.json）——四种指标对应四种答案形态（长文档抽取/精确数值/词面重叠/包含判定）。judges 统一 `openai/gpt-oss-120b`，但 `evaluator_api_key: "sk-"` 是残缺假 key（doc_infer.json:30），跑评测前必须自己填。

**断链**：ds_infer.json 的 `data_path: "benchmark/ds_benchmark.jsonl"` 指向不存在的文件（benchmark/ 下只有 rag/web/doc 三个 jsonl）——ds 域的基准数据没进仓。doc_infer.json 没有sandbox_server_url 字段（rag/web/ds 都有），靠 rollout 侧默认值兜住。

### 第三层：trajectory 四配置——纯采集车间

四份全部 `"trajectory_only": true, "evaluate_results": false, "save_summary": false"`（doc_trajectory.json 等），即只跑 rollout 存轨迹、不打分不汇总——产出给训练/蒸馏用。与 infer 层最本质的区别在模型字段：**trajectory 层填的是具体强模型**（`openai/gpt-oss-120b`、rag_trajectory.json 的 `gpt-4.1-2025-04-14`）+ 真实端点（`${OPENROUTER_API_KEY}`+openrouter.ai），infer 层留白等被测模型。设计意图明显：**强模型造轨迹（教师），待测模型考 infer（学生）**。ds_trajectory 的 system_prompt 比 ds_infer 多一条"Be careful about summary rows (e.g., a row where nation is 'total')"（ds_trajectory.json）——造数据的人踩过的坑沉淀进了教师提示词。

### 第四层：synthesis 八配置

第 07 篇已详表，家族视角补三笔：八份是全家族唯一带 `sampling_tips/synthesis_tips/qa_examples` 提示词字段的层；断链最集中（GUI 的 seeds/vm 与 vm_config.json 双断、doc_ds 的 configs/server 目录不存在、text2sql 两处 `/path/to/AgentFlow/` 占位）；`target_qa_count` 是被 SynthesisConfig.from_dict 静默吞掉的无效字段（synthesis/core/config.py:68-69）。

### 第五层：MCP 25 YAML——另一个占位符宇宙

结构统一（filesystem.yaml 为例）：`type: stdio` + `name` + `params.command/args/env/cwd` + `client_session_timeout_seconds` + `cache_tools_list`。按拉起方式三分类：

- **19 份 vendored 本地**：command 是 node/uv，args 引用 `${local_servers_paths}/...` 下的本地构建产物（如 filesystem.yaml 的 `${local_servers_paths}/filesystem/environment/dist/index.js`）——离线可用，需预装 Toolathlon 的 local_servers 目录；
- **5 份 registry 拉包**：`npx -y howtocook-mcp`（howtocook.yaml）、`@modelcontextprotocol/server-memory`（memory.yaml）、`@tokenizin/mcp-npx-fetch`（npx-fetch.yaml）、`@lockon0927/playwright-mcp-with-chunk`（playwright_with_chunk.yaml）、`uvx mcp-scholarly`（scholarly_search.yaml）——首次跑要联网拉 npm/PyPI 包；
- **1 份全局命令**：arxiv_local.yaml 的 `uv run arxiv-mcp-server`，既不 vendored 也不带版本锁，依赖环境里装好。

**关键陷阱：占位符有两套，互不相通**。config_loader 的 `${VAR:-default}` 展开**环境变量**；而 MCP client 侧的 `_SUPPORTED_PLACEHOLDERS = {"local_servers_paths", "agent_workspace", "task_dir"}`（mcp/client.py:18）只认**路径三元组**。`resolve_mcp_value`（mcp/client.py:23-48）遇到环境变量式占位符会记 debug 日志后**跳过替换保留原文**（mcp/client.py:43-48）——在 MCP YAML 里写 `${SOME_API_KEY}` 不会报错，只会把字面量传给子进程。

**文件名≠name 实测 5 处**（任务口径 4 处，源码实测为准）：`12306.yaml→rail_12306`、`arxiv-latex-mcp.yaml→arxiv-latex`、`npx-fetch.yaml→fetch`、`scholarly_search.yaml→scholarly`、`youtube_transcript.yaml→youtube-transcript`（下划线连字符之差）。enabled_mcp_servers 引用的是 name 而非文件名（mcp_config.json:15），对不上号就静默不加载。

细节亮点：npx-fetch.yaml 特意清空四个代理环境变量并在注释里说明原因（"TLS certificate verification through MITM proxies... clear proxy vars to prevent injection"）——宿主代理注入会弄坏 Node 原生 fetch，这是踩坑后留下的防御。

## 三、外部连接

- **configs/infer → configs/sandbox-server**：`sandbox_config_path` 直引（ds_infer.json），auto_start=true 时 rollout 会替你拉沙箱。
- **configs/synthesis → configs/sandbox-server**：同款直引（rag_config.json 的 sandbox_config_path）；→ seeds/ 目录（seeds_file）。
- **sandbox-server/mcp_config → MCP YAML 群**：`enabled_mcp_servers: ["filesystem","terminal","snowflake"]`（mcp_config.json:15）按 name 点名 25 中的 3 个。
- **环境变量面**：全家至少 14 个变量——VLM_API_KEY、OPENAI_API_KEY/URL、OPENROUTER_API_KEY、SERPER_API_KEY、JINA_API_KEY、VM_CLIENT_PASSWORD/IMAGE_PATH/RECORDING_PATH、RAG 三路径、TOOLATHLON_WORKSPACE_ROOT、PG 五件套、TEXT2SQL 七路径。install.sh 与 start_sandbox_server.sh 是主要的设置入口。
- **数据面**：infer/trajectory 层 → benchmark/*.jsonl（ds 断链）；synthesis 层 → seeds/*/seeds.jsonl（GUI 断链）。

## 四、数据流

以一次 ds 域完整实验为例看配置如何接力：

```
configs/sandbox-server/ds_config.json        (沙箱：ds 三工具+LLM摘要)
        ▲ sandbox_config_path
configs/trajectory/ds_trajectory.json        (教师 gpt-oss-120b 采轨迹)
        ‖ 产 trajectory_results/ds/
configs/synthesis/ds_config.json             (同沙箱造 QA，seeds/ds/seeds.jsonl)
        ‖ 产 results/ds_synthesized_qa/
configs/infer/ds_infer.json                  (学生模型考 exact_match)
        ‖ 产 infer_results/ds/
```

四层各持一份 ds 配置、共享一个沙箱配置——域内自洽，跨域零复用。

## 五、设计决策（含批判）

**做得好的**：①四层按消费者分层，职责边界清楚；②敏感值 100% 走占位符，仓里**没有**硬编码的真实密钥（与 MCP 生态常见的高危样例成对比）；③`${VAR:-default}` 的"未设置保留原样+告警"策略比静默空串好排查；④MCP YAML 的注释纪律好——每份都标 Source/Toolathlon Version 出处，可追溯性堪比 lockfile。

**要批判的**：

1. **路径引用无校验**：全家至少 6 处断链/占位（ds_benchmark.jsonl 不存在、seeds/vm、vm_config.json、configs/server、/path/to×2），全部要到运行时才暴露。48 份配置配一个"启动前路径体检"脚本（遍历 path 类字段 test -e）本是举手之劳。
2. **占位符双轨制无提示**：`${VAR:-default}` 与 `${local_servers_paths}` 语法同形、语义不同、在不同层展开，MCP 层遇到环境变量占位符只给 debug 级日志（mcp/client.py:44）——排查"MCP 子进程收到字面量 ${KEY}"这种故障要对源码很熟。
3. **弱默认凭据**：`:-password`、`:-eigent`、`:-camel` 三处，演示友好生产危险，且 config_loader 展开后不再有任何"你在用默认口令"的告警。
4. **infer 层的 `sk-` 假 key 与 `VLLM_URL` 占位**混在真配置里，分不清"待填"与"已废"。
5. **同名域四份配置间的提示词漂移**：ds 两层的 system_prompt 就差一行"summary rows"警告——手工维护四份近似文件必然漂移，提示词应抽公共片段。

## 六、新人提示

- **改配置前先画引用图**：拿 `grep -n "config_path\|data_path\|seeds_file" configs/ -r` 列出所有路径引用，核一遍存在性再动手——断链密度不低。
- **起沙箱的最小验证**：`python -c "from sandbox.server.config_loader import ConfigLoader; ..."` 或直接 start_sandbox_server.sh 带 --config，看告警日志里的"Environment variable not set"就知道缺哪些变量。
- **MCP 按需开**：默认只开 3 台（filesystem/terminal/snowflake），要加就在 mcp_config.json:15 的 enabled_mcp_servers 里加 **name 字段值**（不是文件名）——五个改名的坑见上文。
- **调教师/学生模型**：造数据改 trajectory 层，评测改 infer 层，别弄反——infer 层填了真模型就变成"自己考自己"。
- **检查占位符残留**：跑完后 grep 输出目录里的 `${`，有命中说明环境变量没设全（展开失败的占位符会原样渗进数据）。
- **ds 域跑通前的心理准备**：benchmark/ds_benchmark.jsonl 缺失，得先用 synthesis 线造或自备数据补上。
