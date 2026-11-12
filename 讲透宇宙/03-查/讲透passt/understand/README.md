# passt understand 图谱 · 全链产物

> passt.top/passt @6aa4f88b（2026-10-25）· 产物 2026-11-08 · 真源本目录

## 状态

| 产物 | 规模 | 状态 |
|---|---|---|
| knowledge-graph.json | 989 节点 / 1819 边 / 16 层 / 16 步 tour | ✅ validator 0 issues 0 warnings（双验） |
| fingerprints 基线 | 225 文件 @6aa4f88b | ✅ 支持增量更新 |
| ONBOARDING.md | 5998 字 8 节 23 行号锚 | ✅ |
| explain/ | 12 篇（2500-4800 字/篇） | ✅ 413 锚 0 真坏（唯一标记=IP 冒号误报） |

## 批分析实录（14 批 / 225 文件）

- 手扫补 imports 边合计 58 条（scanner 对 .h 的 #include 全盲系 C 仓系统性盲区：passt.h 12 条、fwd_rule.h 4 条等）
- tree-sitter C 盲区实证：tcp.c 4121 行提取 0 函数、tcp_splice.c 0、udp.c 0、fwd_rule.c 2/16——全部手扫补齐并逐条 static 实测
- 构建产物甄别 4 项：seccomp.h/seccomp_pesto.h/seccomp_repair.h（seccomp.sh 构建期生成）与 pasta.1（由 passt.1 派生）——正确不建边
- 深度发现：13 个 test DSL 文件系 passt 自有测试语言（非 shell）由 test/lib/test 解释执行；test/ci 与 test/run_demo 实为 test/run 符号链接（basename $0 分发三模式）；UDP checksum 含 AVX2(BESS 移植)/VSX 双 SIMD 段

## 使用

- 新人：ONBOARDING.md → tour 16 步 → explain/ 12 篇
- agent：knowledge-graph.json（989n）+ 仓内 knowledge 消化文档 /usr-data/data2/kylin/network/knowledge/passt.md
- 增量：代码变更后重跑 prepare（fingerprint 指纹跳过未变文件）→ 只重析变动批
