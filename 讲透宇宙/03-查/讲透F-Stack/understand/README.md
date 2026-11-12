# f-stack understand 图谱 · 全链产物

> f-stack/f-stack @52514377（2026-10-28）· 产物 2026-11-08 · 真源本目录

## 状态

| 产物 | 规模 | 状态 |
|---|---|---|
| knowledge-graph.json | 1616 节点 / 2669 边 / 14 层 / 16 步 tour | ✅ validator 双验 0 issues 0 warnings |
| fingerprints 基线 | 298 文件 @52514377 | ✅ 支持增量 |
| ONBOARDING.md | 8925 字 8 节 30+ 行号锚（13/13 抽验命中） | ✅ |
| explain/ | 12 篇 38392 字符 | ✅ 锚两轮核验 0 坏（修正 10 处） |

## 裁剪口径（.understandignore 钉版）

vendored 全裁：dpdk/（6619）、freebsd/（17786）、app/nginx-1.28.0+redis-6.2.6（1391）、tools/ FreeBSD 工具移植（818）；docs/ 只留顶层架构文档裁 spec 子目录与 zh_cn 镜像；lib/opt/*.h 空头排除——图谱主体=adapter 62+lib 136+example 23+tests 108+配置文档 ≈298 文件。

## 批分析实录（22 批 / 298 文件）

- 手扫补 imports 合计 ~160 条（C 仓 .h 系统性盲区；ff_dpdk_if.c 5420 行 tree-sitter 只提 36 函数，后半 35 个核心函数全手补）
- 悬空边 11 条全为前缀错位（file:/config:/service:→pipeline:），按钉版套路回补 10 条
- 重大甄别：**lib/ff_api.c 不存在**——BSD socket 桥实体=ff_api.h+ff_syscall_wrapper.c（两写作代理独立纠正任务书）；ff_kern_timeout.c 的 no-op 桩曾致 TCP 定时器全灭（P0 修复叙事）；FF_KERNEL_FD_BASE=0x40000000 高位 fd 编码双栈共存；文档版本漂移三处（nginx-1.25.2→1.28.0、FreeBSD 13.0→15.0、Roadmap 1.26→v2.0）

## 使用

- 新人：ONBOARDING.md → tour 16 步 → explain/ 12 篇
- agent：knowledge-graph.json + knowledge/f-stack.md 消化文档
- 增量：代码变更后重跑 prepare（fingerprints 跳过未变）
