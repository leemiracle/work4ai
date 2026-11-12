# 09 · MCP 三件套：datamind_mcp 引导器、datamind-context 插件与 CCR 启动脚本

> 对象：`plugins/datamind-context/`（Codex 桌面插件，v2.1.0）+ 其 `src/datamind_mcp.py` 29 行引导器 + 仓根 `scripts/start_ccr.sh`。三者合成"把 DataMind 数据工具暴露给外部 agent 宿主"的完整链路。

## 一、角色定位

DataMind 有两条对外暴露通道：HTTP API（datamind/server.py）和 MCP（Model Context Protocol）。MCP 线的核心主张写在测试里：**目录里只有直连数据工具，没有嵌套 agent**——`test_datamind_mcp.py` L14-15 断言 `datamind_operation_begin`、`datamind_graph_schema`、`datamind_graph_neighbors`、`datamind_db_query_sql`、`datamind_skill_get`、`datamind_workspace_publish` 存在，L16 断言 `datamind_ask`、`datamind_store`、`datamind_graph_query`、`datamind_workspace_ask` **不存在**。消费方（Codex）自己做抽取、查询规划、SQL 生成与答案合成——这是 v2.0 删除 StoreAgent/RetrieveAgent 后的契约固化。

三件套分工：`datamind_mcp.py` 是插件侧引导器（把仓根挂上 sys.path 然后转发）；`plugins/datamind-context/` 整包是 Codex 桌面市场的本地插件（含安装器、技能文档、双平台 MCP 配置）；`start_ccr.sh` 是给 SDK 后端起的 claude-code-router 翻译代理。

## 二、内部结构

**src/datamind_mcp.py（29 行）**：L9 `PLUGIN_ROOT = Path(__file__).resolve().parents[1]`；L11-20 `repo_root()` 三级解析——`DATAMIND_REPO_ROOT` 环境变量 → 插件根下的 `.datamind-repo-root` 指纹文件（L15-19，install 时写入的一行绝对路径）→ 兜底 `PLUGIN_ROOT.parents[1]`（插件在 `plugins/datamind-context/` 下，两级上是仓根）；L22-24 把仓根插进 `sys.path`；L26 `from datamind.mcp import execute, handle, main`——**真 MCP server 在 `datamind/mcp.py`（232 行）**：L35 `definitions()` 出工具目录、L61 `load_settings`、L73 `execute`、L194 `handle`（JSON-RPC 分发）、L219 `main`（stdio 主循环）。插件里的引导器不含任何协议逻辑。

**双平台 MCP 配置**：`.mcp.json` 用 `"command": "./src/run_datamind_mcp.sh", "cwd": "."`；`.mcp.windows.json` 改用 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./src/run_datamind_mcp.ps1`——**Windows 靠文件名 `.mcp.windows.json` 覆盖激活**，宿主按平台选择同名配置。两个 runner（sh 29 行 / ps1 约 70 行）逻辑互为镜像：REPO_ROOT 三级解析（sh L6-14：env → `.datamind-repo-root` → `../..` 探测）→ **`cd "$REPO_ROOT"`（sh L19）**，因为 Settings 按 cwd 找 `.env/.env.datamind`，而 Codex 是从插件缓存目录拉起进程的——不 cd 就读不到凭据；再按三级选解释器（sh L21-29：`DATAMIND_PYTHON` → `<repo>/.venv/bin/python` → PATH 上的 python3；ps1 对应 `.venv\Scripts\python.exe`，最后还能 `py -3` 兜底）。

**install.sh（294 行）**：L70-77 `detect_bundled_repo` 以 **`pyproject.toml` 存在且 `datamind/` 目录存在**为仓库根指纹；L78-95 三段探测（脚本自身向上 → `../..` → 报错要求 `--repo-root`）。L118-135 rsync 把插件布到 `~/.codex/marketplaces/datamind/plugins/datamind-context/`（排除 `__pycache__`、`.venv`、`.datamind-repo-root` 本身，L129-133）。L137-143 处理"插件拷贝里捆绑了整个仓"的场景后重探根；**L145 把最终 REPO_ROOT 写成目标插件的 `.datamind-repo-root` 指纹文件**——运行期三级解析的第二级就是它。L150-153 从 `.env.datamind.example` 引导 `.env.datamind`；L155-161 建 venv 并 `pip install -e`。L165-212 用内嵌 Python 幂等合并 `marketplace.json`（同名插件替换）；**L216-279 幂等 patch `~/.codex/config.toml`**：注释 L227-229 说明 stdlib 只有 TOML reader 没有 writer，于是按文本编辑——`replace_or_append_section`（L242-263）用正则定位 `[marketplaces.datamind]` / `[plugins."datamind-context@datamind"]` 两个 section 头，存在则整段替换、不存在则追加，重跑安全。

## 三、外部连接

- 插件 manifest `.codex-plugin/plugin.json` 声明 `mcpServers: "./.mcp.json"`、`skills: "./skills/"`，interface 段带三条中文 defaultPrompt；`skills/datamind-context/SKILL.md` 教 Codex "You are the main Codex agent"：先 `datamind_operation_begin` 拿 operation_id，读模式默认钉当前发布版本，写模式变更活库或构建新快照。
- 仓根 `scripts/install_codex_plugin.sh` 是 8 行转发器：L7 `exec "${REPO_ROOT}/plugins/datamind-context/install.sh" --repo-root "${REPO_ROOT}" "$@"`。
- CI 的 codex job（python-ci.yml L121-141）把 `plugins/datamind-context/tests/test_datamind_mcp.py` 列进必跑清单；该测试 L27-50 用子进程验证**双入口**（插件 `src/datamind_mcp.py` 与 `python -m datamind.mcp`）在无 LLM 凭据下完成 initialize→tools/list→operation_begin→graph_schema 的真 stdio 往返。
- `datamind/mcp.py` 复用数据平面（L73 execute 走 build_data_plane），与 HTTP API 同源。

## 四、数据流

Codex 桌面启动 → 读 `~/.codex/config.toml` 发现 marketplace → 按插件内 `.mcp.json`（Windows 用 `.mcp.windows.json`）以插件缓存目录为 cwd 拉起 runner → runner 解析仓根并 `cd` 过去 → 选 venv 解释器 exec `datamind_mcp.py` → 引导器补 sys.path、import `datamind.mcp` → stdio JSON-RPC：initialize（instructions 含 main-agent 契约、serverInfo 2.1.0）→ tools/list（>20 个工具）→ tools/call 按 operation_id 关联调用，写操作走 08 篇数据平面同一条路。

`start_ccr.sh` 是独立旁路：配 `DATAMIND__AGENT__BACKEND=sdk` 时 agent loop 用 Anthropic /v1/messages 打到 CCR（L16-19 注释），CCR 翻译成 OpenAI 格式转上游。L61-87 现场生成 CCR config（Providers+六路由）；L93-98 lsof 清旧实例；L101-104 隔离 HOME、清空代理环境变量后 `exec node`。

## 五、设计决策（含批判）

1. **指纹文件 + 三级解析**贯穿三层（引导器/runner/install），比环境变量单一通道鲁棒，代价是三处实现要人肉保持同步——sh 与 ps1 已经是两份平行代码，改解析规则必须双改。
2. **文本级 TOML patch 是务实妥协**：Python stdlib 无 TOML writer（3.11 时代），手写正则限定"section 头到下一个 `[`"的替换域足够窄。批判：若用户 config.toml 里有数组 of tables 或同名 section 出现在嵌套上下文，正则会错切——好在目标文件是 Codex 自家的、结构可控。
3. **引导器 29 行、协议 232 行分离**：插件永远只是 sys.path 挂载器，升级 MCP 协议不用碰插件包。测试 L27-50 同时压两个入口防漂移。
4. **start_ccr.sh 的硬编码坑**：L36 `DEFAULT_ENTRY="/Users/lianghao/Desktop/DataMind/KDD-CUP-DataAgent/vendor/claude-code-router/..."` 是**作者个人 macOS 绝对路径**，且指向兄弟仓的 vendored CCR——仓库间隐式依赖无文档提示。L37 可 `CCR_SERVER_ENTRY` 覆盖，L39-43 缺文件 fatal exit 2 带 hint，属可绕过而非死路。
5. `.mcp.windows.json` 靠命名约定覆盖，非官方标准——宿主不认就退化为手工指定。

## 六、新人提示

- 改 `datamind/mcp.py` 的工具目录后，跑 `pytest plugins/datamind-context/tests/test_datamind_mcp.py`——L12-24 的目录断言（直连在、agent 型不在、readOnlyHint 正确）是最容易踩的契约。
- 插件装完"没反应"排查顺序：`~/.codex/config.toml` 两个 section 是否都在 → 目标插件目录有没有 `.datamind-repo-root` 且指向存在的仓 → 仓根 `.env.datamind` 凭据 → 完全退出 Codex（macOS Cmd+Q）再开（install.sh L293-294 的提示）。
- 在 Linux 服务器上用 SDK 后端：必须显式 `export CCR_SERVER_ENTRY=<CCR 的 index.js 路径>`，否则 start_ccr.sh L36 的 macOS 默认路径直接 fatal。
- 别在插件目录里改代码期望生效——install 是 rsync 拷贝，改完要 `--force` 重装。
- `run_datamind_mcp.sh` L19 的 cd 是凭据能被读到的关键：如果自己写宿主集成，务必以仓根为 cwd 或设 `DATAMIND_REPO_ROOT`。

行号锚：plugins/datamind-context/src/datamind_mcp.py:9/11-20/22-24/26 · datamind/mcp.py:35/61/73/194/219 · run_datamind_mcp.sh:6-14/19/21-29 · .mcp.windows.json（powershell 覆盖） · install.sh:70-77/78-95/129-133/137-143/145/150-153/165-212/216-279/227-229/242-263 · tests/test_datamind_mcp.py:12-24/27-50 · scripts/install_codex_plugin.sh:7 · scripts/start_ccr.sh:16-19/36/37/39-43/61-87/93-98/101-104 · skills/datamind-context/SKILL.md（main agent 契约）
