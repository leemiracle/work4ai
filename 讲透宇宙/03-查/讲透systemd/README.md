# 讲透 systemd（网络线侧重）

> systemd/systemd @7c6c0851f1 起跟踪（2026-11-05 克隆，每日跟踪中）· 产物生成 2026-11-07
> 真源：/usr-data/data2/kylin/network/systemd/（活体克隆）· 本目录=DeepWiki 快照+网络线深度消化

## 产物清单

| 产物 | 规模 | 状态 |
|---|---|---|
| deepwiki/ | 43 页 1.4M | ✅ TRUE_100（dw_reconcile_dir 终判，43/43 零缺失） |
| knowledge-systemd-network.md | 22.4k 字符 | ✅ 网络子系统深度消化（networkd 状态机/38 种 netdev/自研协议库/resolved/systemd×eBPF 交汇五处源码实证） |

## 阅读指引

- 先读 knowledge-systemd-network.md——网络线（networkd/resolve/协议库/udev link-config/BPF 交汇）成体系的中文深剖，全带源码路径锚
- deepwiki/ 为全仓 43 页英文结构化 wiki：1-overview → 2-core-concepts（unit 管理/进程沙箱）→ 3-system-configuration → 4-networking → 5-daemons-and-services → 6-development-and-testing 等，INDEX.md 可导航
- 网络专项疑问优先本目录两件；systemd 全家桶（journald/homed/boot 等）疑问走 deepwiki/

## 同工作区姊妹篇

讲透eBPF/（awesome-ebpf 288 条知识库）· knowledge/{f-stack,passt}.md（f-stack/passt 无 DeepWiki 收录，消化文档是唯一知识源——TIRx 先例同型）

## understand 图谱（2026-11-08 新增 · 史上最大）

| 产物 | 规模 | 状态 |
|---|---|---|
| understand/knowledge-graph.json | **23980 节点 / 56339 边 / 16 层 / 16 步 tour**（18.7MB） | ✅ validator 双验 0 issues |
| understand/ONBOARDING.md | 7717 字 8 节 46 锚 | ✅ |
| understand/explain/ | 12 篇 43373 字符 | ✅ 216 锚 0 坏 |

真源：仓内 /usr-data/data2/kylin/network/systemd/.understand-anything/（fingerprints@ca78951b 3618 文件支持增量；裁剪口径与 170 批实录见其 README）
