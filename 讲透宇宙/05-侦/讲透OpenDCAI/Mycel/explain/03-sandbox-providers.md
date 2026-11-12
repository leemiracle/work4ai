# 03 · 沙箱执行域：五家 Provider / SandboxManager / SyncManager / runtime_handle

## 角色定位

`sandbox/`（约 8700 行）与 `backend/sandboxes/inventory.py` 共同构成 Mycel 的代码执行底座：agent 的每一次 Bash、文件读写、终端命令最终都落在某个"沙箱"里跑。这层的职责是——把五家异构执行后端（本机进程、AgentBay 云沙箱、本地 Docker、E2B、Daytona）统一到一个 Provider 抽象后面，再由 SandboxManager 管理会话生命周期、SyncManager 负责工作区文件双向同步、runtime_handle 把"运行时"持久化成可恢复的状态机。01 篇的 idle_reaper 与 02 篇的子 agent 沙箱最终都消费这里的接口。

## 内部结构

**五家 Provider（inventory.py:69-151 实证）**：`_build_providers` 的装配顺序是 local → agentbay → docker → e2b → daytona。local 的 `LocalSessionProvider` 永远第一位、无条件注册（inventory.py:75-81，直接在本机 workspace_root 跑）；随后若配置目录存在，逐个 `glob("*.json")` 读取沙箱配置（每个 json 文件名=provider 实例名），按 `config.provider` 字段分派：agentbay（inventory.py:89-103，需要 AGENTBAY_API_KEY 或配置内 key，缺 key 跳过并告警）、docker（L104-113，镜像/挂载路径/绑定挂载）、e2b（L114-126，E2B_API_KEY+template）、daytona（L127-145，DAYTONA_API_KEY+api_url/target）。**不存在 "fake" provider**——网上若有人写 "local/docker/e2b/daytona/fake"，少了 agentbay 且多了不存在的 fake。daytona 分支有专门的窄契约注释（@@@daytona-inventory-contract，L133-137：不许重新引入旧的宽参数集，除非 provider 和 schema 一起长出那些字段）。整个清单是进程级单例（`init_providers_and_managers`，inventory.py:43-50，@@@sandbox-inventory-singleton：本地 dev 里 provider 配置是进程生命周期状态，建一次全复用，避免每条 API 路径反复实例化会失败的 provider）。

**能力声明**：`ProviderCapability`（sandbox/provider.py:78）用数据类声明八项能力键——can_pause/can_resume/can_destroy/supports_webhook/supports_status_probe/eager_instance_binding/inspect_visible/runtime_kind 加 mount 结构（inventory.py:21-32 的 `_capability_to_dict` 即此清单）。上层（如 monitor 的孤儿巡检 L226 按 `inspect_visible` 决定是否展示）只看能力不看品牌。`available_sandbox_types`（inventory.py:154-205）把它们输出成 API 可见的沙箱类型清单，配置了但实例化失败的条目会带 `available: False` 与原因（L186-193）——失败也是可观测状态。

**SandboxManager（sandbox/manager.py:249-282 起，1005 行）**：每个 provider 一个 manager，构造时建 terminal_store/sandbox_runtime_store/chat_session_repo 三件 SQLite 存量与 ChatSessionManager、SandboxVolume（manager.py:261-279）。核心职责链：`get_sandbox`（manager.py:472）为线程取/建沙箱能力对象——对暂停线程任何新活动先触发恢复（@@@activity-resume，L481）；持久化线程的内存 chat session 丢失时要重水化（@@@paused-runtime-rehydrate，L516）；远程运行时首条命令前必须完成 volume 挂载/同步（@@@volume-strategy-gate，L536）。local 有豁免：本地 shell 不走 volume 门（@@@local-shell-no-volume-gate，L319）也不做 volume 同步（@@@local-no-volume-sync，L434）——本机会话直接在宿主 cwd 执行。`enforce_idle_timeouts`（manager.py:638）是 idle_reaper 每轮调用的回收器：会话空闲超 idle_ttl 或存活超 max_duration 即销毁，**local 豁免**（L645 注释：留着不花钱）。`sync_uploads`（manager.py:454-465）是手工触发上传的入口。

**SyncManager 与增量策略（sandbox/sync/）**：SyncManager（sync/manager.py:6）按能力选策略；`IncrementalSyncStrategy`（sync/strategy.py:159-224）是主力，**上传路径不对称于下载路径**：
- 上传（strategy.py:163-197）：`@RetryWithBackoff(max_retries=3, backoff_factor=1)` 装饰；先 `state.detect_changes` 找新增或 SHA256 变化的文件（sync/state.py:29-46，@@@checksum-change-detection），只传变化集；传输首选 provider SDK 原生 `upload_bytes`，否则 tar 打包批量执行（@@@native-first，L181-185）；传完在**单事务**里批量登记校验和（@@@batch-track，L187-197）。
- 下载（strategy.py:199-204）：**不做变更检测，全量拉回**（原生或 tar），然后 `_update_checksums_after_download`（L209-224）把本地全部文件重新 rglob 一遍重登记校验和。不对称是有意的：远端是权威副本（agent 在沙箱里改文件），本地无从增量判断，索性全量；副作用是下载后上传方向立刻"干净"（校验和已对齐），不会回环重传。
- `RetryWithBackoff`（sync/retry.py:8-29）只对 OSError/ConnectionError/TimeoutError 三类瞬态异常退避重试（backoff_factor^attempt 秒），其余异常直接抛。

**runtime_handle 与 schema 契约（sandbox/runtime_handle.py，1136 行）**：`SandboxRuntimeHandle`（L101）是"一个沙箱运行时"的抽象句柄，SQLite 实现 `SQLiteSandboxRuntimeHandle`（L175）维护 desired_state/observed_state 双状态、事件追加（L330）、快照持久化（L364）。与 05 篇的 SQLite repo 层有一个硬契约：runtime_handle.py:32-69 导出三组 `REQUIRED_SANDBOX_RUNTIME_COLUMNS / REQUIRED_INSTANCE_COLUMNS / REQUIRED_EVENT_COLUMNS` 列集合，repo 的 `ensure_tables` 建完表后用 `PRAGMA table_info` 核对，缺列直接 RuntimeError 并指示"Purge the configured sandbox sqlite db and retry"（storage/providers/sqlite/sandbox_runtime_repo.py:508-529）。这是**fail-loud 而非自动迁移**的 schema 策略——列集合的权威定义放在运行时层（谁消费谁声明），校验放存储层。对比之下同仓 message_queue 表是真自愈：缺 `metadata_json` 列就 `ALTER TABLE ADD COLUMN` 补上（storage/providers/sqlite/queue_repo.py:140-142）；chat_sessions 表还会检测旧 schema 残留的 UNIQUE(thread_id) 索引并拒启（chat_session_repo.py:133-137，@@@single-active-per-terminal：多终端模型要求"每 terminal 一个活跃会话"而非每 thread）。

## 外部连接

- 上游消费：02 篇 LeonAgent 的 `self._sandbox.fs()`、AgentService 的 `_normalize_child_sandbox`；01 篇 lifespan 注入的 `init_providers_and_managers`（inventory.py:43 即被注入函数本体）。
- 横向：backend/sandboxes/ 的 thread_resources/provider_boundary 做线程级资源配属与 provider 边界；monitor 域用 `list_provider_orphan_runtimes`（inventory.py:208-253）找"provider 侧存在但库里没登记"的孤儿运行时——判定规则是 status 不在 {deleted,dead,stopped} 且 instance_id 未被库登记（L227-231），孤儿以 `(orphan)` thread_id 入清单（L235）。
- 存储：三个 SQLite repo（terminal/sandbox_runtime/chat_session）与 05 篇的 supabase 双轨；`_use_supabase_storage`（runtime_handle.py:75）决定走哪轨。

## 数据流

一次远程沙箱命令的完整路径：线程首次要沙箱 → manager.get_sandbox → 查 chat session 与 runtime 绑定（@@@existing-sandbox-runtime-identity，manager.py:166 复用必须重新绑定身份）→ 无则建 runtime+instance → volume 门：SyncManager 增量上传本地工作区（校验和差异集）→ 命令在 provider 实例内执行 → 结果回流。线程空闲 30 秒一轮（01 篇 reaper）→ manager.enforce_idle_timeouts → 到期销毁实例并写事件。用户手动保存/同步时 `sync_uploads` 全链再走一次上传；拉取远端改动时 download 全量覆盖+全量重登记。会话暂停/恢复经 pause_instance/resume_instance（runtime_handle.py:146-149），状态变迁全部经 `_transition_instance_via_strategy_repos`（L616）落事件表——审计即数据。

## 设计决策（含批判）

1. **能力键而非 provider 品牌**：上层逻辑写 `capability.can_pause` 而非 `provider == "daytona"`，新增第六家 provider 时 manager 零改动。批判：八项能力键粒度偏粗，实际代码里仍有 daytona 专属分支（manager.py:324 销毁托管 volume、L341 首启建 volume），抽象漏了一角。
2. **上传增量/下载全量的不对称**：承认"谁是权威副本"这个语义差异，比强行双向 rsync 简单可靠。代价：大工作区每次下载都是全量 tar，成本随目录 size 线性涨；好在 agent 工作区通常不大。
3. **schema fail-loud + purge 指令**：与其写脆弱的自动迁移，不如缺列就大声失败并告诉开发者清库重来——本地 dev 的 sqlite 数据本来就可弃。但对新人是堵墙：报错文案必须可执行（"Purge the configured sandbox sqlite db"），这个文案本身就是设计的一部分。
4. **local 豁免链**：不进 volume 门、不做同步、不参与 idle 回收——三条豁免分散在三处 @@@ 注释里（manager.py:319/434、645）。理解 local 与远程的真实分界必须把三条读完，这是隐性知识的地雷。
5. **进程级单例清单**：避免反复实例化会失败的 provider（如无 key 的云沙箱每请求告警一次会很吵），但也意味着改配置要重启进程才生效——文档没写这条，新人容易在"改了 json 不生效"上卡半天。

## 新人提示

- 加第六家 provider 的清单：providers/ 下新建实现类（对照 local.py 496 行最小）→ config.py 加配置段 → inventory.py `_build_providers` 加分支与 key 校验 → capability.py/provider.py 不用动。三处缺一不可。
- 沙箱行为诡异先查能力键与豁免：`provider.get_capability()` 输出决定上层走哪条路径；local 的三条豁免（volume 门/同步/idle）是最常见"为什么本地和云端行为不一样"的答案。
- 同步出问题先看 SQLite 里的校验和表：上传只传 diff，若怀疑"没传上去"，调 `state.detect_changes` 看它认为的变更集，而不是盯文件 mtime。
- Runtime 报 "schema mismatch: missing [...]" 不是 bug 是契约：按报错清掉沙箱 sqlite 库重启；不要手写 ALTER TABLE 救——REQUIRED_* 集合（runtime_handle.py:32-69）与真实建表语句可能还有其他分歧。
- 孤儿沙箱（provider 侧有、库里无）走 `list_provider_orphan_runtimes`，monitor 页的 (orphan) 条目即来源于此；清理它们要谨慎——instance_id 未登记不代表没人用，可能是跨库迁移残留。
