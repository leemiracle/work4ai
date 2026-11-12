# 10 · config_updater + common/etcd：管理面热更通道——三方共享键、六字段白名单与零磁盘 apply

> 所属仓库：openJiuwen-ai/agent-gateway。本篇覆盖 `agent_gateway/extensions/agentos/config_updater/`（4 文件约 700 行）与 `agent_gateway/common/etcd/`（2 文件约 330 行），并串起消费端 `AgentOSRouterClient.apply_remote_overrides`。cron 的 etcd 存储见 05 篇，这里聚焦配置热更线。

## ① 角色定位

这套东西解决的问题是：**运行中的 Gateway 沙箱资源参数（CPU/内存/空闲回收）需要运维在不重启进程的情况下调整**。`config_updater/__init__.py:2` 的模块头一句话定性——"Update local config from the AgentOS data-plane configuration"：watch 一个 etcd 键，把管理面下发的受管字段叠加到 Gateway 的内存全量配置快照上。

它是**纯单向管理面通道**：Gateway 只读不写。写方是管理面（AgentOS 控制器），另一个读者是 jiuwenbox——`config_updater/__init__.py:18-19` 把契约钉死："External contract shared with the management plane (writer) and jiuwenbox (another reader) -- do not change without coordinating all three"。共享键 `CONFIG_SYNC_KEY = "/agentos/config/data-plane"`（`:20`）。

`common/etcd/` 则是被两处消费（cron store + config updater，`agent_gateway/common/etcd/client.py:1-4`）的最小 etcd v3 客户端——"stdlib + httpx only, no business dependencies"，走 etcd 的 gRPC-gateway JSON API（`/v3/kv/*` 与 `/v3/watch`），不引入 grpc 依赖。

## ② 内部结构

**common/etcd/client.py（305 行）**——纯基础设施层：
- `EtcdJsonClient`（`:90`）：多 endpoint 轮转（`_next_base` 取模轮询，`:110-115`），每次请求失败换下一个 endpoint 重试一轮（`_post_json` 的 for 循环，`:131-151`）。
- KV 操作三件套 `range/put/delete`（`:163/182/189`）+ CAS 写 `put_if_mod_revision`（`:196`，etcd txn 的 `MOD EQUAL` 比较，失败抛 `EtcdCasError`，`mod_revision=0` 表示键必须不存在）。
- `watch_prefix`（`:226`）：POST 流式长连接，`timeout=None`；`_iter_watch_events`（`:267`）手工增量解码 JSON 流（`decoder.raw_decode` + 缓冲区），事件抽取遇 `canceled` 或 `compact_revision` 立即报错（`:290-291`）——watch 被压缩说明进度落后，必须重 range。
- `prefix_range_end`（`:38`）：前缀扫描的 range_end 计算（末位非 0xFF 字节 +1）。

**config_updater 三件套**——I/O 与决策分离（`client.py:4-5` 明言 "I/O only; application decisions live in service.py"）：
- `client.py`（155 行）：`ConfigUpdaterClient` 负责 pull + watch 单个键、YAML 解码、抽取 `gateway:` 段。构造器注入一切输入，**绝不读 config.yaml**（`:39-41` 注释：那会经 `get_config` 成环）。
- `merge.py`（236 行）：纯函数库（"No I/O, no config access"，`:2-6`）——抽取/过滤/校验/合并四步。
- `service.py`（291 行）：`ConfigUpdaterApplier`（`:47`）做合并决策，`ConfigUpdaterService`（`:179`）持有 watcher 任务生命周期。

## ③ 外部连接

- **etcd 集群**：endpoint 复用 cron 的配置（`agent_gateway/app_gateway.py:2086` 的 `load_cron_store_settings(full_cfg).endpoints`）——cron 与 config updater 共享同一 etcd 拓扑。
- **app_gateway 装配**：`app_gateway.py:2074-2076` 注释钉版边界——"Data-plane settings are AgentOS-only. A personal Gateway using etcd for cron must not start this service"：只有 `is_agentos_routing_client(client)` 且 client 有 `apply_remote_overrides` 方法才启动（`:2078-2094`），`overrides_handler=client.apply_remote_overrides` 直连路由客户端；`:2536-2537` start、`:3676-3677` stop。
- **AgentOSRouterClient**：`agent_gateway/extensions/agentos/agentos_router/router_client.py:2545` 的 `apply_remote_overrides` 是热更的最终落点。
- **cron store**：`agent_gateway/runtime/cron/etcd_store.py:27` 的 `EtcdCronJobStore` 同用 `EtcdJsonClient` 与 `prefix_range_end`，但键空间不同（`/jiuwenswarm/cron/jobs/`，`:24`）。
- **jiuwenbox 与管理面**：共享键的另两方（只读/读写），契约靠 `CONFIG_SYNC_KEY` 常量对齐。

## ④ 数据流

**取数（client.watch_loop，`client.py:90`）。** 先 `range` 精确读一次键（`_pick_exact` 按 `kv.key == key_bytes` 过滤并取最大 mod_revision，`:150-152`——因为 watch 是前缀流，`.../data-plane-backup` 这类同前缀键也会来事件，必须精确过滤，`:96-98` 注释）；然后从 **snapshot_revision + 1** 起播 watch（`:113`），把"读快照→开 watch"之间的窗口缝死（`:99-100` 注释："closing the range-to-watch race even when applying the initial value is slow"）。流断开则指数退避重连（2s 起 60s 封顶，`:22-23` 与 `:127-128`）。键值是 YAML，解析失败产空 section 而非异常（`_decode`，`:131-138`）。

**应用（service.ConfigUpdaterApplier.apply，`service.py:72`）。** 每个事件走五道闸，每道都有独立 skip 理由：

1. **revision 闸**：`mod_revision <= last_applied` 或 `< pending` 一律 "revision-unchanged"（`:78/84`）。
2. **白名单过滤**：`filter_managed_section` 把 section 投影到 `_MANAGED_FIELDS` 六字段树上，未管字段路径全部记入 ignored 并 WARNING（`:86-93`）。
3. **校验闸**：`validate_section` 逐字段验类型，失败整批拒绝 "validation-failed"（`:100-108`）。
4. **合并**：managed_overrides（历史叠加态）与 base config（`config_provider` 现读）各自 deepcopy 后 `merge_section` 叠加（`:110-125`）；与当前 effective 相同则 "no-change" 短路（`:126-130`）。
5. **刷新**：`_refresh`（`:145`）先调 `overrides_handler`（运行时窄接口，改的是活的路由客户端），成功才提交 `_effective_config` 并清 pending（`:168-175`）。任一步失败标 `retryable`，revision 留在 pending 态。

**重试与不饿死**。`_watch`（`service.py:236`）里 watcher 与 applier 是两个任务：`_receive` 只更新 latest 并 set 事件（`:244-248`）；`_apply_latest`（`:250`）对 retryable 结果指数退避（1s 起 30s 封顶）重试，但退避等待期间若来了**更新的 revision 则立即放弃旧重试**（`:260-265` 注释："A newer management revision supersedes the pending one instead of starving"）。

**落点（apply_remote_overrides，`router_client.py:2545-2575`）。** 六字段分两组生效：`agent_sandbox.idle_timeout` 变化会启停 idle reaper（`_apply_idle_timeout`，`:2577`——从正数变 ≤0 取消任务，从 ≤0 变正数重启任务，同正只更新值）；`agent_sandbox.cpu/memory` 只影响**之后**创建的沙箱；tool_sandbox 三值通过环境变量转发给**新建** AgentServer 实例。docstring 钉版两条语义：管理面 rank 高于 env（env 只做启动种子）；**远端文档删掉某字段 = 保持现值**，绝不回落到 env/yaml 默认（"deleting the field does not roll anything back"，`:2554-2556`）。

## ⑤ 设计决策与权衡

**决策一：六字段白名单是安全边界。** `_MANAGED_FIELDS`（`agent_gateway/extensions/agentos/config_updater/merge.py:18-25`）只放行 `agent_sandbox.{idle_timeout,cpu,memory}` 与 `tool_sandbox.{idle_timeout,cpu,memory}` 六条路径，且两组**故意分命名空间**（`:16-17` 注释）。`filter_managed_section` 用一棵 `_LEAF` 标记树做投影（`:68-105`）：不在树上的路径、非 dict 的中间节点全部丢弃并留痕。这防住了"管理面被攻破后改写 Gateway 任意配置"的横向风险——`__init__.py:10-13` 的 Trust boundary 注释直说：这个键是管理面输入，能改本地资源/回收参数，etcd 端点必须限制在可信网络并部署 ACL，明文 HTTP 只适合隔离内网。

**决策二：显式 None 保留给校验拒绝。** `filter_managed_section` 的 docstring（`:70-73`）："Explicit values, including None, are retained so validation can reject invalid attempts instead of treating them as absent"——字段显式写了 `null` 是一次**非法尝试**，要报错而非当作没写。配合 `_validate_field` 的 bool 陷阱检查（`:189-191`，bool 是 int 子类，写 true 几乎必是笔误）。

**决策三：pending 两阶段提交。** refresh handler 失败时 revision 留在 `_pending_refresh_mod_revision`，下次同 revision 事件直接复用已算好的 `_pending_config`（`service.py:112-116`），不重算合并；这同时保证"重试期间网关配置永远处于上一个完全生效版本"，不存在半应用状态。

**决策四：不落盘。** apply 全程 "without disk I/O"（`service.py:73` docstring）——热更只改内存快照与运行时对象，重启后回到 config.yaml + env 种子。这与 09 篇登录会话的落盘策略形成对照：配置的可信源是管理面（重启重拉），会话的可信源是本机（落盘保活）。

**决策五：etcd 客户端自研而非引依赖。** etcd v3 原生是 gRPC，官方 Python 客户端拖 grpcio 全家桶；这里用 gRPC-gateway 的 JSON HTTP API 只覆盖 range/put/delete/txn/watch 五个动词（`client.py:91`），约 300 行零业务依赖。代价是 watch 的流式 JSON 要手工增量解码（`:267-281`），且没有 lease/keepalive——对本用例（watch 一个键）够用。

## ⑥ 新人提示与坑

1. **改 `CONFIG_SYNC_KEY` 或键内容结构要三方协调**（管理面写方 + Gateway + jiuwenbox 读方），`__init__.py:18-19` 是变更红线注释；本地改了键名测试时管理面写的是旧键，Gateway 静默收不到。
2. **个人版 Gateway 用 etcd 存 cron 不会**启动 config updater（`app_gateway.py:2074-2076`）——etcd 配了但热更不生效时，先确认 `gateway.agent_client.type` 是不是 agentos_router 系。
3. **同前缀键的干扰**：watch 是前缀流，任何 `/agentos/config/data-plane*` 键（如备份键）都会触发事件，靠 `_pick_exact` 过滤（`client.py:97-98`）——新增同前缀键无需担心，但调试日志里看到"收到事件但没应用"先想到这层。
4. **watch 被压缩（compact_revision）不是普通错误**：`_extract_watch_kvs` 遇到直接 raise（`common/etcd/client.py:290-291`），外层重连后会重新 range 全量——所以 config updater 天然能从"进度落后太多"自愈，不需要额外补偿逻辑。
5. **managed_overrides 是叠加态不是快照态**：每次 apply 从 `_managed_overrides` deepcopy 后再 merge 新 section（`service.py:117-118`），历史管理值不会因新文档缺字段而丢失。想让管理面"收回"某字段只能显式写合法新值，删除字段=保持现值（`router_client.py:2554-2556`）。
6. **`normalize_section` 的 int 保真**：`600` 不会被改写成 `600.0`（`merge.py:225-226`）——tool_sandbox 的 idle_timeout 会被下游 `int()` 强转（07 篇 config.py 注释），float 化在这里提前防住。
7. **apply 顺序是 overrides 先于 refresh**（`service.py:147-156`）：运行时窄接口（改活对象）先成功，全量配置快照才提交——顺序反了会出现"配置显示已生效但运行时还是旧值"的窗口。

**关联阅读**：沙箱 idle reaper 与 warmup 见 07 篇；etcd cron store 双活主备见 05 篇；`common/` 母仓镜像模式见 12 篇。
