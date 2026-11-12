# 08 · TypeScript 适配器群：opencode / cline / strands 的嵌入式 SDK 与 fs 临时目录工程

## 角色定位

`adapters/typescript/` 下八个 TS 适配器（opencode/cline/droid/kilo/kiro/pi/qwen/strands）共享 `common/` 包的 lifecycle（448 行）与 acp-runner（464 行），代表三条集成路径：**opencode** 把 OpenCode v2 以嵌入式 host 跑在适配器进程内（`opencode/src/opencode-sdk.ts`，972 行，群内最大）；**cline** 动态加载 `@cline/sdk@0.0.83` 并用运行时合成的 agent plugin 注入 skills/MCP（`cline/src/cline-sdk.ts`，612 行）；**strands** 走 Agent Client Protocol 拉起 CLI 子进程（`strands/src/strands-acp.ts` 335 行 + `runtime.ts` 187 行）。

## 内部结构

**cline-sdk.ts 的 fs 临时目录管理是命题核心**。`prepareRuntimeFiles`（cline-sdk.ts:264）先 `mkdtemp(join(tmpdir(), "nemo-fabric-cline-"))` 建运行时根，再合成一个完整 Cline agent plugin：`plugin.json` manifest（cline-sdk.ts:277-283，agent-plugins.org schema 1.0.0，name 即 `CLINE_PLUGIN_NAME = "nvidia.fabric.cline"` cline-sdk.ts:20）；skills 逐个 realpath 校验含 `SKILL.md` 后 `cp(recursive, errorOnExist)` 进 `plugin/skills/<name>`（cline-sdk.ts:287-313，同名碰撞抛 `cline_skill_collision`）；MCP server 规范化为三态（cline-sdk.ts:198-254）写入 `plugin/mcp.json`（cline-sdk.ts:320）；任何失败 `rm(root, recursive, force)` 清场（cline-sdk.ts:334）。插件写完还要实证：`validateRuntimePlugin`（cline-sdk.ts:339）用 SDK `loadAgentPluginPackages` 真加载一遍，断言零 error 且 skills/MCP 计数与期望一致（cline-sdk.ts:353-368），然后才把 `agentPluginPaths` 传给会话（cline-sdk.ts:591）。另一精妙点是 `withClineDataDir`（cline-sdk.ts:76-98）：`CLINE_DATA_DIR` 是进程级全局，适配器用 promise 链互斥量把"设→操作→恢复"串行化防并发互踩。会话（cline-sdk.ts:458-522）：首 prompt 走 `core.start`，后续 `core.send(sessionId)`（cline-sdk.ts:476-484）；stop 按 stop→dispose→cleanup 三连（cline-sdk.ts:495-521）。

**opencode-sdk.ts 是隔离工程大全**。环境层 `leaseEnvironment`（opencode-sdk.ts:753）快照 `process.env`，按 `INHERITED_ENVIRONMENT_NAMES` 白名单（opencode-sdk.ts:705-742）重建后整体替换（opencode-sdk.ts:744-751），返回 lease 恢复原状。配置层 `hostConfigContent`（opencode-sdk.ts:88）生成配置 JSON，用户值可能含 `{}`，故用 UUID 占位符替换回填并转义（opencode-sdk.ts:96-99、158-161）。skills 同样快照进临时目录（opencode-sdk.ts:182、189），复制后 `rejectAdditionalDiscoverableSkills`（opencode-sdk.ts:165）递归拒绝"目录里藏额外可发现 skill"，再 `verifyLoadedSkills`（opencode-sdk.ts:236）轮询 `client.skill.list` 直到全部入 catalog（5 秒窗 opencode-sdk.ts:61）。权限层 `NONINTERACTIVE_SESSION_PERMISSIONS`（opencode-sdk.ts:50-56）显式 deny external_directory/`*.env`/question。SDK 入口有私有文件 workaround：`loadEmbeddedOpenCodeCreate`（opencode-sdk.ts:690-699）从包根 resolve `./promise.js` 拿双参 create——"convenience namespace 会静默忽略 embed 参数"（opencode-sdk.ts:911-917）。

**strands-acp.ts 是子进程 + HOME 沙盒**。`StrandsAcpSessionFactory.create`（strands-acp.ts:245）：自定义端点注入 `LITELLM_BASE_URL`/`LITELLM_API_KEY`（strands-acp.ts:265-267）；`mkdtemp` 建一次性 HOME（strands-acp.ts:268），源 HOME 的 `.aws` 以 symlink（Windows junction）链过去（strands-acp.ts:274-282）——保住 AWS 凭证链（含 SSO cache）同时隔离 CLI 状态；写 `~/.strands/cli/config.json` 关掉 mcpDiscovery/skillDiscovery/telemetry（strands-acp.ts:289-299）；`startAcpSession`（strands-acp.ts:301）以 `--acp-server --session off --memory off --skills off` 拉起（strands-acp.ts:303-321）。Windows 下 npm `.cmd` shim 不被 ACP 直接 spawn 认账，`command()`（strands-acp.ts:221-243）在 PATH 定位 `strands.js` 用 `process.execPath` 启动。usage 归一（strands-acp.ts:141-184）校验 input+output==total 且 cache 不超 input，缺失缓存计数按 CLI 0.2.1 默认零（strands-acp.ts:165）。

## 外部连接

cline 对 SDK 是动态 `import()` + API 形状探测（cline-sdk.ts:109-135，缺 `ClineCore.create`/`getClineDefaultSystemPrompt`/`loadAgentPluginPackages` 任一即 `cline_harness_incompatible`）；opencode 双包 resolve `@opencode/sdk`@2.0.23 与 `@opencode/core`（opencode-sdk.ts:667-688），模型端点经 `ModelEndpointProxy` 代理（opencode-sdk.ts:17）；strands 只经 acp-runner 的 ACP 协议，错误翻译 `translateRunnerError`（strands-acp.ts:108-135）刻意不透传目标错误文本——"可能含凭证或 prompt 内容"（strands-acp.ts:128）。上层包装薄：`StrandsAdapterRuntime`（strands/runtime.ts:48）加 100 次调用上限（runtime.ts:53）与 deadline 检查（runtime.ts:103-117），stopReason 非 `end_turn` 一律失败（runtime.ts:155）。

## 数据流

opencode 的 invoke（opencode-sdk.ts:819）体现"增量取证"：先 `sessions.context` 抓 prompt 前消息 id 集（opencode-sdk.ts:822），提交并 `sessions.wait` 等空闲后再抓一次，用 `extractOpenCodePromptOutcome`（opencode-sdk.ts:625）按 id 差集过滤新 assistant 消息取末位，usage 由新增消息累加（opencode-sdk.ts:571），文件改动经 `sessions.diff` 提取 patch（opencode-sdk.ts:830）。cline 结果归一 `normalizeResult`（cline-sdk.ts:414-456）：finishReason 白名单五值（cline-sdk.ts:417），session_id/finish_reason/iterations/model 全进 extensions。健康检查 opencode 用 `sessions.get` 判未 archived 并二次校验防竞态（opencode-sdk.ts:800-817）。

## 设计决策

1. **临时目录即安全边界**：cline 的 plugin 合成、opencode 的 skills 快照、strands 的 HOME，同一哲学——把易变的文件系统状态复制进 `mkdtemp` 私有目录，失败/停止强制 `rm -rf`，宿主零污染。
2. **版本锁死写进错误信息**：cline 安装命令常量（cline-sdk.ts:19）、opencode 的 `npm install @opencode/core@2.0.23 @opencode/sdk@2.0.23`（opencode-sdk.ts:679）直接进 LifecycleError 消息。
3. **不支持的配置显式拒绝**：cline 对 MCP authentication/allowed_tools/blocked_tools 全抛错（cline-sdk.ts:199-219）；opencode 拒绝 tool filters 与非回环 HTTP 端点（opencode-sdk.ts:395-450）。
4. **embed 隔离**：opencode `loadIsolatedEmbedOptions`（opencode-sdk.ts:75）用 override 关掉 project/global 配置发现，session 仍留 Fabric workspace——嵌入式 host 不吃宿主全局配置。
5. **strands 凭证链保全**：symlink `.aws` 而非复制（不丢 SSO 缓存）。

## 新人提示

先读 `common/src/lifecycle.ts` 与 `acp-runner.ts` 再读具体适配器，否则 ACP 系的 `startAcpSession` 来龙去脉不清。cline-sdk.ts 难点只有 promise 链互斥（cline-sdk.ts:76-98）与 plugin 三文件合成。opencode-sdk.ts 从底部 `OpenCodeSdkSessionFactory.create`（opencode-sdk.ts:885）倒读——它是资源获取顺序总目录（lease→sdk→proxy→config→client→skills→session→MCP wait），catch 块嵌套 finally 清理链（opencode-sdk.ts:932-965）是 TS 资源管理教科书。注意 retryable 语义：opencode 只在"prompt 可能尚未提交"时 true（opencode-sdk.ts:836-838）。测试在 `tests/adapters/test_{cline,opencode,strands}_adapter.py`，e2e 侧 `tests/e2e/test_{opencode_checks,strands}.py`。
