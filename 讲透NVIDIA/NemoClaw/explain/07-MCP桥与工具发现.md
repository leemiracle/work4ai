# 07 · MCP 桥与工具发现（mcp-bridge / mcp-lifecycle-lock / tool-discovery runtime）

## 一、角色定位

MCP 桥是 NemoClaw"宿主机凭据不进沙箱"承诺的执行端：宿主侧把用户登记的 MCP 服务器凭据写进 OpenShell 的 provider 存储，沙箱内 agent 只能拿到 OpenShell 占位符；随后由一个锁版本的 Node runtime 在沙箱内完成**只列名字**的工具发现（names-only discovery），并把结果以受限 JSON 协议带回宿主。该线由三块组成：provider 变动（`src/lib/actions/sandbox/mcp-bridge-provider-mutation.ts`）、跨进程互斥（`src/lib/state/mcp-lifecycle-lock*.ts` 四件套）、工具发现（`src/lib/actions/sandbox/mcp-bridge-tool-discovery.ts` + `tools/mcp-tool-discovery-runtime/`）。

## 二、内部结构

**provider-mutation 的头注释（`mcp-bridge-provider-mutation.ts:4-16`）就是一份完整设计文档**：OpenShell v0.0.99 的 provider 写入有服务端 resource-version CAS，但 `provider update` 不暴露调用方期望版本——另一个客户端可以在 NemoClaw 预检与变更之间竞写。补偿三件套 = 随机 provider 名 + MCP 生命周期锁 + 变更后强制复检不可变身份。核心函数 `upsertMcpProvider`（`:66`）的防御链：`requireExisting` 拒绝凭据重发布时 provider 消失（`:109-113`）、无稳定 ID 的半成品 provider 拒绝收养（`:119-123`）、凭据形状漂移拒绝更新（`:124-131`）。`:139-155` 的块注释按 invalidState/sourceBoundary/whyNotSourceFix/regressionTest/removalCondition 五段式归档这个补偿的来龙去脉——`removalCondition` 明写"等 OpenShell 提供原生 CAS 或不可变 provider ID 后删除本补偿"。真正的心脏是 inspect-mutate-inspect 三明治：`:156` 变更前再检一次（create 时同名 provider 冒出即拒绝 `:161-169`），`:183-198` 执行 create/update，`:207-224` 变更后复检身份+凭据形状+resourceVersion 单调性（update 后版本必须严格大于变更前 `:218`），任何失败一律 fail closed。`refreshMcpProviderEnvironment`（`:234`）则用"零字段 update"推进 provider revision，让 Docker sidecar 拿到 post-policy generation 完成同步（`:227-233` 注释）。

**生命周期锁**（`mcp-lifecycle-lock-acquisition.ts`）：100ms 轮询（`:35`）、默认 30 分钟超时（`:36`）、损坏锁 30s 宽限（`:37`）；同步等待用 `SharedArrayBuffer` + `Atomics.wait`（`:61,72`）而非忙等。锁身份（`mcp-lifecycle-lock-identity.ts:12` schema v1）记录 hostIdentity 与 pidNamespaceIdentity，注释钉版"foreign owner 绝不被本地 PID 检查回收"（`:20`，`:228` 处再申"绝不用本进程 PID 表回收外族 owner"）——跨机/跨 PID namespace 的锁只能等或判定损坏，不能抢。`withConnectSandboxLifecycleLock` 是同一函数的 const 别名（`mcp-lifecycle-lock.ts:8`），与 portable host fence 构成两级锁序。

**工具发现**：沙箱内命令由 `buildMcpToolDiscoveryCommand`（`mcp-bridge-tool-discovery.ts:103`）生成——先校验记录的 URL 信任意图随行（`:113-119`，漏带曾致 #11377 误跳过健康注册），再拼 `if [ ! -r …runtime ]` 缺失兜底 JSON（`:148-153`），runtime 路径钉死 `/usr/local/lib/nemoclaw/mcp-tool-discovery-runtime/mcp-tool-discovery.mjs`（`:33-34`）。宿主侧分类器 `classifyMcpToolDiscoveryResult`（`:177`）是一条 paranoid 校验链：marker 帧、256KiB 输出上限（`:42`，按 500 个 256 字节名字全转义的最坏情形定容 `:39-41`）、协议号 2（`:35`）、count==tools.length、名字去重+排序确定性（非确定性清单也判失败 `:251-259`）、ok 与 detail/failedStage 互斥（`:279-288`）、过 `redactBridgeSecretsForDisplay` 后再验尺寸（`:298-306`）。

## 三、外部连接

沙箱内 runtime 是独立 npm 包 `tools/mcp-tool-discovery-runtime/`，把 **`@modelcontextprotocol/sdk` 精确锁在 `1.30.0`**（`tools/mcp-tool-discovery-runtime/package.json:10`，devDeps 的 esbuild/typescript 同样精确锁版）。`mcp-tool-discovery.ts:7-9` 只 import SDK 的 Client/StreamableHTTPClientTransport/ErrorCode 三件；`:24` 写结果时统一带 `protocol` 字段。SDK 的非类型化解析错误在 `:35` 注释里被显式归类为协议失败而非远程工具失败。产出物经 `build-reviewed-runtime.ts` 用 esbuild 打成 CJS bundle（`:36-46`，target node22、minifyWhitespace、legalComments eof），构建前先读回冻结的 `managed-startup-image-runtime.bundle` 再清目录重写（`:13-19,30-33`）——自举式保持"冻结产物不被重建漂移"。上游适配走 `OpenShellProviderAdapter`（provider-mutation `:18`），探测复用全仓就绪轮询根实现 `src/lib/core/wait.ts`（其 NeighborMap 显示十余个消费方）。

## 四、数据流

`mcp add` 登记 → 生命周期锁 acquisition → `ensureMcpBridgeProviderProfile` 导入 endpointless profile（`:47-64`，防止把 MCP 凭据挂到不符契约的既有 provider）→ `upsertMcpProvider` 三明治写凭据 → 策略生成绑定 → `refreshMcpProviderEnvironment` 零字段推进 revision → 状态命令触发 `discoverMcpTools`（`mcp-bridge-tool-discovery.ts:323`）：readiness 五级预检跳过原因（`:76-95`）→ 沙箱 exec → 分类器 → 状态输出。凭据值全程只在 OpenShell 占位符形态进入沙箱环境（`:109-114` 注释：runtime 只收 key 名，从自身进程环境读 revisioned 占位符，其余一律拒绝）。

## 五、设计决策

1. **补偿性设计必须自带删除条件**：provider-mutation 与两个 hermes patch 一样，头注释写明 removalCondition，防止补偿永久化。
2. **从不从副证推断成功**：update 后 resourceVersion 上涨不等于本次提交成功（`:199-206` 注释），非零结果一律歧义处理。
3. **names-only 是保密边界而非功能选择**：工具清单只回名字不回 schema，恶意 server 无法借 description/凭据派生文本外传（`:112-114` 注释直说 parser validation 不是保密证明）。
4. **确定性即正确性**：清单未排序也判失败，让结果可被 diff 与缓存。
5. SDK 1.30.0 精确锁版 + bundle 冻结 + 双通道（seed 清单+审计 CI）构成供应链三保险。

## 六、新人提示

改 provider 逻辑先读 `:4-16` 头注释与 `:139-155` 五段式，再动代码；回归测试入口在 `mcp-provider-ownership.test.ts`（模拟并发 resource-version 写者）。动 runtime 必须同步看 `reviewed-runtime-bundle/` 是否需要重建（`--check` 模式校验）。生命周期锁的测试靠注入 `monotonicNow`/probes 保持确定性（`mcp-lifecycle-lock-identity.ts:40` 的 injectable probes 契约），不要真等 30 分钟超时。图谱侧注意：`src/lib/state/mcp-lifecycle-lock/decisions.ts` 等子目录文件与 `-acquisition/-identity/-storage` 平铺文件并存，搜边时两条路径都要查。
