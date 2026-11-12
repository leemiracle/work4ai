# 讲透 agentgateway

> agentgateway/agentgateway —— agent 流量网关（Envoy 系，Rust）：A2A/MCP/LiveKit 等 agent 协议的反向代理+策略+可观测，K8s Controller 带态。
> 本地仓：/usr-data/data2/repos/aaif-projects/repos/agentgateway（HEAD f51a7fbc，2026-10-21 聚合）

## 状态（2026-10-24 全链完成 ✅）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki)（**109 页 100%**，全文 1.72M 字符——AAIF 系最大，mcp.deepwiki.com 直连，2026-10-21） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**7792 节点/19479 边/16 层/16 步 tour，validator 0 issues 0 warnings，fingerprints 1482 文件@f51a7fbc**——understand 流水线史上最大图谱；95 批 4 并发含 1308 团灭复活，2026-10-24；backup-batches/ 全量备份） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（4064 汉字/91 锚/8 节） |
| explain 系列 | ✅ | [explain/](explain) 12 篇（合计 33,937 汉字/256,880 非空白字符，每篇 57-224 锚全源码核验，2026-10-24） |

字数口径（SB3 轮钉版双轨）：汉字数=正则计数；非空白字符=`tr -d '[:space:]'`（含 markdown 语法与行号锚）。

## explain 12 篇索引

| # | 篇 | 主角 | 汉字 |
|---|---|---|---|
| 01 | [gw_controller reconcile](explain/01-gw-controller-reconciler.md) | 非典型 reconciler/两级 AGWP 合并/SessionKeys 仲裁 | 2823 |
| 02 | [translator 与 plugins](explain/02-translator-plugins.md) | 路由模型翻译/策略双巨头 47 类/krt 响应式 | 2466 |
| 03 | [xDS 下发链](explain/03-xds-pipeline.md) | syncer/krtxds/AdsClient/结构化 NACK 对偶 | 2478 |
| 04 | [数据面骨架](explain/04-dataplane-skeleton.md) | app.rs 装配/CAS 乐观并发/热更新三路 select | 2752 |
| 05 | [HTTP 过滤器矩阵](explain/05-http-filter-matrix.md) | 24 步固定链/retry 64KB 回放/令牌桶退款 | 3904 |
| 06 | [MCP 网关与 A2A](explain/06-mcp-gateway.md) | 会话网关/工具重写/A2A v0.3+v1.0 双形态 | 2055 |
| 07 | [LLM 翻译引擎](explain/07-llm-translation-engine.md) | N×2 互译矩阵/8 种 provider/虚拟模型四模式 | 3293 |
| 08 | [CEL 表达式栈](explain/08-cel-policy-stack.md) | fork 增量 HeaderLookup/环检测/CEL 2.0 提交考古 | 2989 |
| 09 | [guardrail 预算遥测](explain/09-guardrail-budget-telemetry.md) | 六类护栏/PII 默认 Mask/双方言 budget SQL | 3394 |
| 10 | [React 管理界面](explain/10-react-ui.md) | types.ts 中枢/15 路编辑器分派/SSE 仅日志线 | 2833 |
| 11 | [Helm 四套 chart](explain/11-helm-charts.md) | Go 内嵌第四套/checksum 双机制/Helm 当模板引擎 | 2687 |
| 12 | [e2e 测试体系](explain/12-e2e-test-system.md) | TestInstallation/testbox 十合一 mock/kind DAG | 2263 |

## 源码级实证勘误（explain 系列产出，12 条钉版）

1. **全 controller 无 finalizer**——grep Finalizer 零命中，清理靠 ownerReferences GC+PruneRemovedResources（01）
2. `agentgateway_parameters.go` 在 deployer 包非 controller 包；helm 只渲染不部署（DryRunClient+占位 release 名）（01）
3. **"九类 LLM 策略"实为 backend 段 14 个 appendPolicy 分支 + auth 内部 9 种凭证来源；pluginsdk 真契约在 plugins/interfaces.go**（02）
4. syncer 实际在 `pkg/syncer/`；`control/mod.rs` 是传输连接器非消费点（真消费在 state_manager.rs:69-77）；**Go/Rust 两侧结构化 NACK 协议精确对偶**；pushOrder 恒空变量（03）
5. lib.rs 是类型定义层，真装配在 app.rs:21-214；**K8s 内反而禁止 config.yaml 兜底**（KUBERNETES_SERVICE_HOST 检测语义反转）（04）
6. **cors 在独立 crate `crates/policies/cors`**（http/mod.rs 仅重导出）；真实过滤器编排中心在 proxy/httpproxy.rs:233（24 步固定顺序）非 http/mod.rs；outlierdetection 是四家 429 头方言解析库非熔断器（05）
7. **legacy-rmcp 双版本是 dev-dependencies 测试基建不进生产二进制**（Cargo.toml:206 注释：官方 SDK 删 SSE 传输而保留）；A2A 双形态兼容官方注释在 a2a/mod.rs:94-109（06）
8. **provider 实为 8 种非 6/7 种；3579 行 mod.rs 属数据面非 agent-llm crate（crate 主文件是 lib.rs 698 行）**；互译是 N×2 矩阵（07）
9. **批 37"guardrail 唯一消费者"说法被推翻**——Expression 编译调用遍布 27 个非测试文件；celx 实为六模块；fork 动机完整记录在 CEL 2.0 提交（86k→400k QPS）（08）
10. url_recognizer 是死代码（#![allow(dead_code)] 压警告，接线 5 个）；**PII 默认 Action=Mask 是改写非只检测**（builtin 命中替换 `<ENTITY_TYPE>`）（09）
11. **Playground LLM 对话是非流式 JSON**（sendChatCompletion 未传 stream）；真 SSE 仅 logsApi tail 与 MCP 响应解析两处（10）
12. **实为四套 chart 非三套**（第四套 Go 内嵌 pkg/helm/agentgateway 承担 Deployment/DaemonSet 互斥+configmap 三段合并）；`AgentgatewayDefaultTag` 常量不存在（过期注释）；validationLevel helper 死代码；Helm 被当纯模板引擎（release-name-placeholder 硬编码，数据面永不走 helm 安装）（11）

## DeepWiki 章节速览（16 章）

1 Overview · 2 Core Architecture · 3 Configuration System · 4 Policy System · 5 Security and Authentication · 6 Traffic Management · 7 HTTP Processing and Transformation · 8 LLM and AI Gateway · 9 Agent Protocols · 10 Observability · 11 Network and Transport · 12 Web UI and Management · 13 Deployment · 14 Development Guide · 15 Kubernetes Controller · 16 Glossary

深水区提示：4 章 Policy 与 9 章 Agent Protocols（A2A/MCP 适配）是本仓灵魂；x1 PII 检测脱敏 / x2 流式 guardrails 两个三级页在 deepwiki/ 单独落盘。

入口：[deepwiki/INDEX.md](deepwiki/INDEX.md) · 覆盖率：[deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)（含 2026-10-22 三级页口径甄别结论）
