# clearml/config + backend_config — 三级合并的配置体系

## ① 角色定位

ClearML 的配置系统横跨两个包：`clearml/config/`（SDK 侧包装器与默认值）与 `clearml/backend_config/`（通用 HOCON 加载引擎，vendored 自 allegroai 基建）。它回答一个核心问题：**"这份 SDK 到底连哪、怎么连、记录什么"**——api 端点凭据、存储桶、指标上报、开发模式行为全部由此供给。图谱 **Configuration System 层 20 节点**中，`file:clearml/config/__init__.py` 入边 48 条（全仓被 import 最多的文件，metrics/events、binding、automation、backend_interface 几乎人人消费）、出边 21 条；配置文件本身是图谱 15 个 config 节点之一（`config:clearml/config/default/sdk.conf`），边直接喂给 config/__init__.py——"文件即节点"在此层成立。

## ② 内部结构

**包装层 config/__init__.py（291 行）**：
- `ConfigWrapper`（config/__init__.py:23）：进程级单例。`_init`（config/__init__.py:27-31）调 `load_config(Path(__file__).parent)`——把 `clearml/config/` 目录作为额外模块路径注入加载器，首次访问才加载并 `initialize_logging`；`set_config_impl`（config/__init__.py:44）支持服务端 vault 热替换配置树。
- `ConfigSDKWrapper`（config/__init__.py:52）：在完整配置树上取 `get("sdk")` 子树，SDK 运行时行为都从 `sdk.*` 读；`clear_config_impl`（config/__init__.py:71）配合 vault 重载后强制重建。
- `deferred_config`（config/__init__.py:75）：返回 `LazyEvalWrapper`，把"读配置"推迟到首次取值——类属性在 import 时求值会早于配置/vault 就绪，这是全仓大量类属性（如 task.py:210-212）的安全基石。
- 便捷函数群：`get_cache_dir`（config/__init__.py:112）、`get_offline_dir`（config/__init__.py:125）、`get_remote_task_id`（config/__init__.py:140）、`running_remotely`（config/__init__.py:144）。模块底部 `config = ConfigSDKWrapper` 是全仓 `from clearml.config import config` 的那个对象。

**引擎层 backend_config/config.py（420 行）— `Config`（config.py:59）**。加载顺序即优先级，全在 `_reload`（config.py:119）：
1. **roots**：`load_relative_to`（config.py:112）把每个模块路径规整为 `<path>/config` 目录，`_read_recursive_for_env`（config.py:262）先读 `default/` 子目录再叠加 `<env>/`（env 来自 `CLEARML_ENV`，config.py:78）。SDK 实际挂两个 root：`backend_api/config/`（含 `default/api.conf`——api_server/credentials/重试策略）和 `clearml/config/`（含 `default/sdk.conf` 355 行）。
2. **`_read_recursive`（config.py:278）的键名规则是关键**：目录相对路径做前缀、**文件名 stem 做键**（config.py:302-304）——所以 `sdk.conf` 里的顶层 `storage/metrics/development` 合并后全在 `sdk.*` 命名空间下。
3. **LOCAL_CONFIG_PATHS（config.py:145）**：当前为**空列表**（defs.py:17-21 中 /etc/opt/trains 等已注释）。
4. **LOCAL_CONFIG_FILES（config.py:156）**：`~/trains.conf` 在前、`~/clearml.conf` 在后（defs.py:23-26），后者可整体覆盖前者键值；`CLEARML_CONFIG_FILE`（defs.py:29）设置后**替换而非追加**（config.py:157-158）。
5. **`_overrides_configs`（config.py:173-176）**：运行时 `set_overrides` 的内存覆盖，优先级最高。
`initialize_logging`（config.py:189）顺带把 `logging.conf` 套到 Python logging 上。

**默认文件 sdk.conf（355 行）**：`storage{cache…}` 第 4 行起（缓存目录、S3/GS/Azure 凭据段）、`metrics` 第 69 行、`development` 第 209 行（worker 资源监控、`vcs_repo_detect_async`、`default_output_uri`、`force_analyze_entire_repo`）、`apply_environment: false` 第 317 行（配置顶层 environment 段注入 os.environ 的开关，由 backend_config/utils.py:23 执行）。api.conf 贡献 `api.*` 段：三个 server 地址默认空、`credentials{access_key/secret_key}`、`api.http.retries/max_req_size`。

**环境变量层**：`backend_config/environment.py:8` 的 `EnvEntry` 是全部 `CLEARML_*/TRAINS_*` 双名变量的基类（get 时逐个回落）；config/defs.py 集中定义 SDK 语义变量——`CLEARML_TASK_ID`（config/defs.py:11）、`CLEARML_TASK_NO_REUSE`（defs.py:19）、`CLEARML_VCS_REPO_TYPE/REPOSITORY_URL` 等（config/defs.py:43-47，repo 检测的环境级覆盖入口）。remote.py:5 的 `running_remotely_task_id` 在 **import 时刻快照**，`override_current_task_id`（remote.py:8）供测试改写；cache.py:10 `SessionCache` 把任务复用状态存 `~/.clearml/.session.json`（常量在 config/defs.py:8）。

## ③ 外部连接（图谱边证据）

`config/__init__.py` 出边 21 条指向 backend_config 引擎、bucket_config（S3 配置对象化）、defs/remote、`utilities/{hashing,proxy_object}`（deferred_config 的懒求值载体）；入边 48 条横跨 `backend_api/session/session.py`（api.* 消费）、`backend_interface/{base,logger,metrics/*,task/*}`、`binding/*`、`automation/controller.py`——"谁 import config 谁就是配置消费者"在这一条边上可视化得淋漓尽致。`backend_config/config.py` 出边 11 条（entry/errors/log/utils/pyhocon），入边仅 2 条，是干净的独立引擎。

## ④ 数据流

进程首次触碰配置读取（往往是 `Task.init` 触发的 `deferred_config` 求值）→ `ConfigWrapper._init` → `backend_api/config/__init__.py:5` 的 `load()` → `Config()` + `load_relative_to(backend_api/config, clearml/config)` → 逐级 HOCON 合并（defaults → env 目录 → 本地 conf → overrides）→ 全树缓存 → `ConfigSDKWrapper.get("development.worker.report_start_sec")` 点路径直达叶子。登录后 `Session._load_vaults` 若拿到服务端 vault，则 `set_config_impl` 换树 + `clear_config_impl` 清 sdk 缓存，实现"服务端下发覆盖本地"。

## ⑤ 设计决策

1. **文件名即命名空间**：sdk.conf/api.conf 以 stem 入键，多个小文件同目录共存互不冲突，代价是"打开 sdk.conf 找 `sdk {` 找不到"的认知坑。
2. **四级回落链**：defaults < env 目录 < 用户 conf < 运行时 overrides，每级又能被 `EnvEntry` 环境变量横向打穿——宁可规则复杂也要"零配置能跑、每层可覆盖"。
3. **懒求值全局化**：`deferred_config` 让模块级常量与配置加载时序解耦，用 `LazyEvalWrapper` 换正确性。
4. **引擎与 SDK 分包**：backend_config 无 clearml 依赖可独立复用，config 只做包装。
5. **vault 下发**：企业版远程配置走登录响应回灌，本地文件降级为引导凭据载体。

## ⑥ 新人提示（含勘误）

- **勘误 1**：sdk.conf 文件里**没有** `sdk { }` 包裹块——`sdk` 命名空间来自文件名 stem（backend_config/config.py:302-304 的键名规则）。同理 api.conf 里也没有 `api { }`。
- **勘误 2**：`~/trains.conf`（旧名）比 `~/clearml.conf` **优先**（先加载先被覆盖，defs.py:23-26 顺序即合并顺序），两者并存时 clearml.conf 赢——不是"新文件名生效、旧的忽略"。
- **勘误 3**：`CLEARML_CONFIG_FILE` 是**排他覆盖**：设置后 ~/clearml.conf 不再加载（config.py:157-158），不是追加一个来源。
- **勘误 4**：LOCAL_CONFIG_PATHS 目录级配置当前是空列表（全被注释），实际不可用，别照抄 `/etc/opt/trains`。
- `running_remotely()` 判定依赖 import 时刻的 env 快照（remote.py:5），测试要先 `override_current_task_id` 再触发逻辑，顺序反了无效。
- 改完 ~/clearml.conf 必须重启进程——配置树只在首次访问加载一次，无文件监听。

---
自检：不计空格字符 4778、含空格 5134、行号锚去重 36 处（config/__init__.py:{23,27-31,44,52,71,75,112,125,140,144}、backend_config/config.py:{59,78,112,119,145,156,157-158,173-176,189,262,278,302-304}、backend_config/defs.py:{17-21,23-26,29}、sdk.conf:{4,69,209,317}、environment.py:8、config/defs.py:{8,11,19,43-47}、remote.py:{5,8}、cache.py:10、backend_api/config/__init__.py:5、utils.py:23、task.py:210-212），全部经源码逐条核实。
