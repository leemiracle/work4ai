# 讲透 passt

> passt.top/passt @6aa4f88（2026-10-25，每日跟踪中；origin 已切 https://passt.top/passt——git:// 端口被墙钉版）· 产物 2026-11-07
> 真源：/usr-data/data2/kylin/network/passt/（活体克隆）· DeepWiki 未收录且 GitHub 无官方镜像（钉版），**本消化文档是唯一结构化知识源**

## 产物

| 产物 | 规模 | 说明 |
|---|---|---|
| knowledge-passt.md | 12.3k 字符 | 8 节深剖：设计哲学（无特权"协议翻译器"）/三层架构逐层（tap→L2/L3 应答→L4 转发+TCP_INFO 窗口镜像）/33 文件速查/vs libslirp（4-50×）/TCP_REPAIR 迁移线与 passt-repair 特权帮手/坑 9 条（含 16MiB 窗口顶、无 SACK/PAWS） |

## 一句话定位

"网络协议翻译器"流派教科书：不做 TCP/IP 栈，做会说网络协议的普通进程——零 capability 让 rootless 容器/VM 联网成为事实标准后端；2025-26 新增 vhost-user 单拷贝与连接迁移。

## 关联

- 四路线横向对比：../讲透eBPF/姊妹篇四路线对比-README.md
- passt 源码特色：每个 .c/.h 文件头部几十行设计长注释即最好架构文档（消化时已利用）

## understand 图谱（2026-11-08 新增）

| 产物 | 规模 | 状态 |
|---|---|---|
| understand/knowledge-graph.json | 989 节点 / 1819 边 / 16 层 / 16 步 tour | ✅ validator 双验 0 issues |
| understand/ONBOARDING.md | 5998 字 8 节 | ✅ |
| understand/explain/ | 12 篇行号锚精讲 | ✅ 413 锚 0 真坏 |

真源：仓内 /usr-data/data2/kylin/network/passt/.understand-anything/（fingerprints@6aa4f88b 支持增量）
