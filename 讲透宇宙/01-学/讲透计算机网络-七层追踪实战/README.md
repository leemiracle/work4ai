# 讲透计算机网络 · 七层追踪实战（13 节点实验）

> 2026-11-05 全链完成：在 13 节点部署可追踪 OSI L1–L7 的服务 → 采集全部七层真实数据 →
> 攻击面逐一实测 → 补救落地进服务（TLS+认证+限额+白名单）→ **同环境重走全流程对比验证**。
> 特色：环境无 tcpdump/openssl CLI/ping → 全部观测工具用 Python 标准库自写（含 AF_PACKET
> 抓包器、raw ICMP ping、TTL 递增 traceroute、TCP 会话时间线分析器）——"讲透"级实现。

## 状态总表

| 环节 | 状态 | 证据 |
|---|---|---|
| r1 部署+七层追踪 | ✅ | data-r1/（12 文件：pcap+JSONL+L1–L7 快照+访问日志） |
| 攻击面实录 A1–A7 | ✅ | data-r1/attack_demo.txt（全部利用成功） |
| 补救实现 | ✅ | remote/netlab/tracehttp_tls.py（7 项措施） |
| r2 加固轮重走+验证 | ✅ | data-r2/（24 文件；攻击重放全防住） |

## 篇目

1. [01-部署与七层追踪实战.md](01-部署与七层追踪实战.md) — 方案、流量剧本、七层逐层数据详解、5 条工程坑实录（raw socket 含 IP 头 / 缓冲不落盘 / SIGINT 被忽略…）
2. [02-数据字典.md](02-数据字典.md) — 每个数据文件、每个字段怎么读（含 pcap 格式与"应用日志×抓包交叉对照"玩法）
3. [03-安全分析与加固.md](03-安全分析与加固.md) — 威胁模型、A1–A7 攻击实录、补救映射、r2 对比矩阵、残余风险诚实清单

## 数据归档

- `data-r1/` r1 明文基线轮 · `data-r2/` r2 TLS 加固轮（同环境同剧本，唯一变量=服务版本，可直接对比归因）

## 代码（源头在本地仓 remote/netlab/，服务器 /root/luowz/netlab/）

| 文件 | 一句话 |
|---|---|
| sniffer.py | 纯标准库抓包器：Eth/ARP/IP/ICMP/TCP/UDP 逐字节解析 + pcap 落盘 |
| tracehttp.py / tracehttp_tls.py | 被追踪的 L7 应用：v1 教学漏洞版 / v2 加固版 |
| myping.py / mytraceroute.py / l1probe.py / flows.py | L3/L1/L5 教学工具 |
| start/stop_stack.sh · snapshot7.sh · attack_demo.sh | 编排：双接口抓包+服务 / 七层快照 / 攻击演示 |
| netlab.sh（在 remote/） | 13 节点容器操作台（up/down/exec，命令 base64 传输） |

## 环境事实（复现用）

- 13 节点 10.44.11.13，容器 luowz-netlab（NET_RAW+NET_ADMIN，bridge 172.17.0.0/16）
- 端口 127.0.0.1:8188→8080(明文) / 8189→8443(TLS)，仅宿主机侧入口
- 镜像 vllm-metax（python3.11；yum 源不通、无 tcpdump——工具全部自带的理由）
