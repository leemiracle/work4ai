# 06 · inference 受管推理与受管启动

对象：`src/lib/inference/vllm-station-cluster-lifecycle.ts`（1833 行，双站 vLLM 集群生命周期）、`src/lib/onboard/managed-startup/profile.ts`（2423 行）、`image-runtime.ts`（1978 行）、`shared-state-transaction.ts`（1574 行）。图谱层"inference 推理域与 vLLM 双站受管集群"与"runtime-provider 契约与受管工作负载状态机"的代表节点。

## 角色定位

受管推理回答的是"沙箱里的 agent 用什么模型"：双站（head+worker 两台 GPU Station）vLLM 集群由 lifecycle 模块以 Docker 标签为产权证明做事务化启停。受管启动回答的是"镜像第一次起来时如何落配置"：profile 是 host 侧构造、经严格校验的版本化配置契约；image-runtime 是镜像内以 root 执行的落地器；shared-state-transaction 给 agent 状态根提供备份-变更-回滚-提交的事务。

## 内部结构

lifecycle 用 13 个 Docker 标签建模产权（lifecycle.ts:25-37）：`managed-vllm`/`vllm-role`/`vllm-cluster`/`vllm-transaction`/`vllm-api-key-fingerprint`/`gpu-smoke` 等，容器就是账本；观察结果五态 `absent | managed | legacy-managed | foreign | ambiguous/unknown`（:164-177）。`startDualStationManagedVllm`（:1432）在生命周期锁内：先重跑 GPU smoke（注释明言模型下载耗时长，紧贴替换前再测一次以关闭 TOCTOU 窗口，:1440-1442）→拓扑检查→双容器 transactionId 一致且可复用则走重用快路径（:1458-1470）→否则起 worker、再事务化处理 legacy head 切换（legacy head 保持存活直到新 worker 证明 running，:1502-1504）、最后起 head；失败即 `rollbackExact`/`rollbackNewPairAndRestoreLegacy` 精确回滚。legacy 迁移有独立 commit/rollback 对（:1619/:1655）。profile 契约是"有界 schema"：schema v2（profile.ts:17）、64KB 解码上限（:20）、JSON 节点 4096/深度 32（:30-31），63 个校验函数里最有味道的是凭据形状检测——字段名按 `token/key/secret/password` 复合/驼峰后缀多模式匹配（:45-57），值内嵌 URL 再用 `URL_CANDIDATE_RE` 抓凭据材料（:43/:1290），messaging 凭据占位另有别名集合（:65-72）。image-runtime 的交换面全在 `/tmp`：runtime env 文件（image-runtime.ts:51）、完成标记（:55）、合并 CA bundle（:54）；`main`（:1828）暴露四个子命令——`--apply-root-stdin`（root 落地）、`--release-startup-hold`（commit 后放行启动保持）、`--verify-completion`/`--wait-for-completion`、内部兼容哈希写入。落地原语：`atomicWriteRootFile`（:422）与 `readStableRegularFileSnapshot`（:835，inode 级稳定读），Hermes 受管策略以 0o444 只读落盘（:891-892）。事务（sst）：目录 0700/文件 0400（sst:26-29），`begin`（:1144）幂等——已有 commit receipt 则校验 agent+profile 指纹+bootstrapIdentity 后拒绝重放（:1158-1169），pending manifest 归属三重校验不匹配即 fail（:1171-1183），随后 `verifyAllBackups` 复核备份。

## 外部连接

lifecycle 的协作圈：`vllm-station-cluster.ts`（计划构造 `DualStationVllmPlan`）、`vllm-station-lifecycle-lock.ts`（控制器 UID 断言+锁）、`vllm-station-ssh-binding.ts`（跨站 SSH 绑定文件断言）、`vllm-api-key.ts`（API key 指纹）、`vllm-docker-env.ts`/`vllm-models.ts`（环境与分布式 serve 命令）；消费方 `inference/local.ts` 与 `vllm.ts`。managed-startup 三件套互相咬合：profile 被 snapshot 受管克隆、`managed-startup-coordinator`、`runtime-provider/podman-host-local-inference` 等 67 个连接消费；image-runtime 被 `managed-startup/root-apply.ts` 与 `provider-root-apply.ts` 调用，还有 `tools/mcp-tool-discovery-runtime` 的直接入口。

## 数据流

受管 vLLM：plan（模型/镜像 sha256/GPU UUID）→ clusterId（:327）与 API key 指纹（:341）→ 容器标签写入 run args（`buildDualStationVllmRunArgs` :542）→ worker/head 依序启动、master 端口 6379（:38）→ `getDualStationManagedVllmBaseUrl`（:1784）返回给沙箱侧 inference 路由。受管启动：host 构造 profile → 编码（profile.ts:2373）跨界传入镜像 → image-runtime 以 root 生成动作计划（生成器/消息/CA 等）原子落盘 → shared-state-transaction 备份 agent 状态根并变更 → commit 写 receipt（:1446）→ `--release-startup-hold` 发布完成标记 → 启动侧 `--wait-for-completion` 等到标记才放行 agent。中断恢复：进程死在变更中途时，下次 `begin` 看到 pending manifest 且归属匹配即续跑，`rollback`（:1410）则用 0400 备份恢复状态根。

## 设计决策

①**标签即产权**：所有"能不能动这个容器"的判定都从 Docker 标签读回（transactionId/clusterId/fingerprint），host 侧状态文件不是权威——容器活着，账本就在。②**先 worker 后 head + legacy 存活**：切流永远在新 peer 证明可用之后，legacy head 的删除是事务提交点而非开始点。③**不可变引用强制**：镜像必须 sha256 digest（:56）、GPU UUID/事务 ID 全模式校验（:59-62），杜绝名字碰撞注入。④**non-root 运行时**：Station 镜像的 `/home/vllm` 非 root 就绪，挂 owner-only tmpfs 并以探明的 model-cache 属主运行（:41-43）。⑤**profile 是凭据禁区**：校验器宁可误报"credential-shaped"也拒绝可能携带密钥的字段，占位符体系把 messaging 凭据隔离到运行时注入。⑥**稳定读+原子写配对**：root 文件先 fstat-inode 读快照、比对后再写，0400/0o444 模式让后续变更必须显式 chmod——配置篡改要留痕迹。

## 新人提示

排障双站集群先 `docker inspect` 看 13 个标签（:25-37），transactionId 不一致就是上次事务没收尾；`vllm-station-cluster-lifecycle.test.ts` 与 `vllm-ownership.test.ts` 用标签组合穷举了拓扑分支。受管启动读码顺序：profile.ts 的常量区（:16-100）先看懂"什么被禁止"，再看 `decodeManagedStartupProfile`（:2378）的调用链；image-runtime 改动必须保持 `--apply-root-stdin` 的 argv 契约（argv 长度就是分派键，:1835-1841）。事务模块测试以"receipt 重放"与"manifest 归属漂移"为主线，改 begin 前先确认幂等语义没有破坏——它是断电恢复的第一道门。
