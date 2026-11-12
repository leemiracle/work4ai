# 讲透 OpenShell（NVIDIA/OpenShell 全链知识库）

NVIDIA 的 agent 安全外壳/监督器：多语言 Rust workspace（38 crate）+ proto 契约 + Go/Python/TS 三语言 SDK。核心安全模型：沙箱生命周期管理 + 策略证明（containment prover）+ L7 网关默认拒绝 + OCSF 遥测 + credential 供应。

| 环节 | 状态 | 产物与指标 |
|---|---|---|
| deepwiki | ✅ 2026-10-26 | TRUE_100 |
| understand 图谱 | ✅ 2026-11-05 | 7661n/17189e/16 层/16 步 tour（历史第二大图）；双 validator 0/0；fingerprints 1195 文件@76cfd0e3；图谱在仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 2026-11-05 | 8 节+勘误清单，16509 字符（不计空格），19 锚终验全好 |
| explain | ✅ 2026-11-05 | 12 篇 54437 字符（不计空格），193 锚终验真坏 0（114 歧义锚归位行号零改动；剩 3 处为 DNS 地址误报） |

## explain 索引（核心安全 6 + 服务端外围 6）

01 proto 契约面 / 02 openshell-core / 03 policy 策略子系统 / 04 prover containment 证明器 / 05 sandbox 隔离层 / 06 supervisor-network L7 / 07 server 服务端 / 08 gateway-interceptors / 09 五驱动横评 / 10 ocsf 遥测 / 11 SDK 三语言 / 12 agent 协作层

## 源码级勘误清单（12 条，全部行号锚实证）

1. **Rust scanner 跨 crate use+完全限定路径双盲**（流水线实证）：84 批累计手补 ~600 边；Go 侧 scanner 包展开病态致生产→`*_test.go` 假边累计剔 ~500 条
2. `.claude/agent-memory` MEMORY.md 过时：grpc.rs 已拆分为 grpc/ 目录；grpc_client.rs/plans/ 均已不存在
3. RFC 0005 所称 supervisor-process 拥有的 netns+nftables bypass monitor——全仓零 nftables 实现（namespace 捕获已移交 supported runtimes）
4. sigv4 双语境：中间件 builtin 系纯规划未实现；provider credential_signing 语境已实现（sigv4.rs 585 行+localstack E2E）
5. OCSF schema 双版本：v1.7.0 系遗留快照（validation 只加载 v1.8.0，零代码引用）；connection_info.json 是 404 占位 stub（vendored 打包失败残留，v1.8.0 才有真 schema）
6. supervisor-network 用内嵌 regorus 引擎非 OPA sidecar；EnforcementMode 默认 Audit 非拒绝
7. prover registry 的 claude.yaml：bypasses_l7 实为 false，风险走 spawns 渗出链（AI agent CLI 被建模为渗出源）
8. gateway-interceptors 路由白名单实测 25 方法（文档写 24）；PostCommit 阶段强制 fail_open
9. go 工具链版本三口径并存（mise 1.25.14/go.mod 1.25.13/README "1.25.13+"）
10. SQLite 迁移编号跳过 002/003 系从未存在（git 首提交即 001+004-008）；007 移除 inference_route 改 sandbox 域 provider attachment
11. 文档漂移两处：`.agents/agents/` 目录不存在；update-docs 目录名与技能名 update-docs-from-commits 双层不一致；TESTING.md/CI.md 各一死链
12. mxc 驱动整 crate Windows-only（lib.rs 全部 pub use 带 cfg(windows)）；ETW FFI 实际在 mxc 的 etw_consumer 非 ocsf

## 流水线备注

- 2026-11-04~05 单仓全链：84 批历经 1308 第三次团灭（b1-b4）与 b2 死前产物手术修正（剔 27 Test 节点+144 假边）
- b32 首分片误写 batch-32.json 基名——merge 两种形态都收（假警报实证）；importMap 恢复 2613 条 imports 边
- agent 协作实证层：20 个 `.agents/skills/` 内部贡献者技能（issue→PR 全流程）+ CLAUDE.md=@AGENTS.md 单行转发 + `.claude/` 子代理人格与记忆体
