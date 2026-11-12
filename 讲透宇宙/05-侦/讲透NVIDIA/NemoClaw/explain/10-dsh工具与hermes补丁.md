# 10 · .dsh 工具目录与 Hermes 补丁层（68 个 ambient 工具 + 3441 行 start.sh + 12 个 patch-*.py）

## 一、角色定位

`.dsh/tools/` 是 DSH（Deep Shell）宿主的**团队自动化目录**：68 个工具目录各含一个 source-first `index.ts`（外加 AGENTS.md 编写指南与 README.md，合计 70 项）。它们不是 NemoClaw 产品 API——AGENTS.md 开篇即声明"内部团队自动化、不携带目录格式之外的兼容性保证、Agent skills 不依赖本目录"。工具在会话内以 `tools.*` ambient API 互相调用（如 `tools.run_github_cli`），把 PR/E2E/CI 证据收集做成可组合原子。Hermes 侧则是两个资产：`agents/hermes/start.sh`（实测 3441 行、86 个顶层函数定义）作为沙箱入口的防御式 bash 巨构，与 12 个 `patch-*.py` 对钉版 Hermes 做带删除条件的外科手术。

## 二、内部结构

**工具宪法**（`.dsh/tools/AGENTS.md`）：每工具一目录一权威 `index.ts`、恰好一个命名 `async default` 导出、目录名==函数名、不加 manifest（`:25`）；临时目录必须 `mktemp -d` 私有化并清理、禁止可预测共享 /tmp 协调（`:29`）；**禁止内嵌 Python 或 `python -c`**（`:30`）；agent 委派走 DSH `subagent` 工具而非拉起 Pi CLI 子进程（`:31`）；GitHub 操作四路由——CLI 文本/JSON 走 `run_github_cli`、REST 分页走 `read_github_pages`、PR 身份走 `read_nemoclaw_pr`、评审线程走 `read_nemoclaw_review_threads`（`:32`）；变更操作必须显式 `apply`/`dryRun`、GitHub 写绑定完整期望 commit ID（`:35`）。**实证一个工具**：`read_nemoclaw_pr/index.ts` 输入校验 number 正整数与 repository `owner/name` 正则（`:20-21`），核心体只是 `await tools.run_github_cli({args:["pr","view",…]})`（`:24` 起）——叶子工具薄、组合发生在调用方。README 定义了六步 E2E 调查模式：summary 归一化→diff 按精确 job 名比对→failure_evidence 提取有界脱敏签名→tested_commit_range 列测试区间→root_cause_correlator 分组（"有界的第一分类，不是最终因果判断"）→investigation_report 渲染 proven/hypothesis/notVerified/nextSteps（`:10-15`）——证据收集与因果分析被刻意分离，`proven` 等字段必须由 agent 复核证据后才能填。

**start.sh**：头部 `:7-14` 说明镜像 `scripts/nemoclaw-start.sh`（OpenClaw 版）的差异——无浏览器配对、YAML 配置、网关内口 18642 经 socat 转发 8642、dashboard 私有环回口转 18789（`:11-12`，常量见 `:241,275`）。安全设计三连：`:23-25` 解析任何 root 启动助手前先锁死 PATH；`:17-20` direct-root 网关以独立用户运行使沙箱 agent 无法控制其进程生命周期；`:28-40` `nemoclaw_runtime_state_mutation_hold_supervisor_failure`——当 provider 侧 mutation gate 处于活动态（exit 75）时，启动 shell 用 `kill -STOP $$` 冻结自己保住 PID/start 身份，等 USR2 认证重试，而非让 `set -e` 换掉进程身份。布局修复族以 `fail_hermes_startup_layout`（`:1779`）为闸：拒绝就地修复、要求恢复可信快照或重建沙箱（`:1782-1784`）；`HERMES_LAYOUT_REPAIR_REFUSED_STATUS=78`（EX_CONFIG）与 `HERMES_LOG_REPAIR_LIMIT_STATUS=75`（`:1787-1790`）两个退出码区分"必须隔离"与"可监督重试"；`repair_hermes_startup_layout`（`:1793`）对 sessions/gateway/runtime 三状态目录维持 group-writable（备份恢复与网关写入双方便利，`:1795-1799`）。批阶段甄别笔记钉版其风格："几乎每个 ensure/repair 函数都幂等可重入；恢复机制用文件标记+PID 追踪跨信号存活"。其余名函数：`cleanup_orphan_socat_forwarders`（`:622`）、`remove_stale_hermes_gateway_files`（`:663`）、跨 UID 状态目录 `ensure_hermes_cross_uid_state_dir`（`:970`）。

**12 个 patch-*.py** 的统一范式 = 文档化动机 + 源形状锚定 + fail closed + 删除条件。`patch-gateway-process-identity.py:4-22`：NemoClaw 把真实入口改名 `/usr/local/bin/hermes.real`，而钉版 Hermes 的网关匹配器只认 basename `hermes/hermes.exe`，导致 `hermes status` 误报网关已停（#7804）——补丁只放宽入口 token 白名单、不动子命令语法（`:23-24`），尾注"上游按内容或配置解析入口后移除本补丁"。`patch-mcp-http-proxy.py:4-17`：v0.21.3 的 caller-owned `httpx.AsyncHTTPTransport` 会禁用环境代理发现，使 MCP 流量绕过 `HTTPS_PROXY` 与策略面——补丁让钉版 httpx 重建标准代理挂载再包上既有 body cap；"exact source-shape checks fail closed when the pinned Hermes transport changes"。同类还有 external-supervisor 恢复/重启、discord 恢复权限、gateway 运行时元数据、sqlite temp store、cron 执行/排空、auxiliary token 上限、profile 策略默认值、session list 预览。配套 `mcp-config-transaction.py:5-16` 自述边界："从不代理 MCP 流量、从不触碰原始服务凭据，一次性 sandbox exec、无常驻控制监听"，动机直引上游 issue 690/52417。

## 三、外部连接

`.dsh` 工具的消费方是 DSH 宿主会话（maintainer 技能运作其上，但契约独立）；`refresh_locked_npm_cache_seed` 工具直通第 11 篇的种子缓存刷新流程。Hermes 线的连接面：宿主侧 `src/lib/hermes-tool-gateway-broker.ts`（broker 以 detached spawn 跑 agents/hermes/host/ 下的运行时文件，脚本被哈希校验）、`resolve-shared.ts` 从域生命周期定义派生 `HERMES_PORTABLE_OPENSHELL_VERSION`；容器侧 Dockerfile.base 以 ARG 级钉扎（npm sha512 integrity+版本）延续仓级供应链模式。`hermes-cli-adapter-v1.json`/`manifest.yaml`/`validate-cli-adapter.py` 构成 CLI 适配合同。

## 四、数据流

DSH 会话装载目录 → `dsh-tool-authoring` 读 index.ts 得契约 → agent 以 `tools.<name>` 调用 → 叶子工具出 `gh` 命令/REST 分页 → 有界脱敏文本返回 → 组合工具（correlator/report）聚合。Hermes 补丁流：Docker 构建期 patch-*.py 对钉版 Hermes 源做精确锚定替换（形状不符即构建失败）→ start.sh 启动期做布局修复/孤儿清理/权限消毒 → 运行期 broker 与 mcp-config-transaction 完成受控变更。

## 五、设计决策

1. **ambient 互调优于共享库**：工具间依赖是运行时 `tools.*` 引用而非 import 图，使每个工具可独立评审与替换。
2. **证据/因果分离**：correlator 只给第一分类，proven 字段留给读证据的 agent——反幻觉的结构化设计。
3. **补丁即债务台账**：每个 patch 头尾写清 why/边界/removal condition，升级 Hermes 时按清单逐个淘汰。
4. **冻结优于重试**：mutation gate 活动期用 SIGSTOP 保进程身份，是"崩溃一致性优先于可用性"的 shell 级实现。
5. 退出码语义分级（75 可重试/78 必须隔离）让监督循环有可编程的处置分支。

## 六、新人提示

写新 DSH 工具先照抄 AGENTS.md 清单（`:25-40` 的 authoring rules 逐条是评审标准）；输出保持"安静"——计数、ID、状态、截断证据，全文读取只对选定条目。读 start.sh 用函数名做地图（`grep -nE '^[a-z_0-9]+\(\) *\{'` 86 个定义），从 `:28` 的 supervisor hold 与 `:1779` 的修复闸两处最难的地方入手。改 patch 先确认钉版 Hermes 未升级——源形状锚定失败是预期行为而非 bug。图谱注意：`.dsh` 各 index.ts 间无 imports 边（ambient 调用），跨工具关系要读 JSDoc 与 README 的路由条款。
