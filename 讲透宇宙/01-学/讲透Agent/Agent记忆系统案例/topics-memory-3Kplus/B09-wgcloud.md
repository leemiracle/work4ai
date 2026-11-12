# B-09 `tianshiyiben/wgcloud`（5.2K★）[结构档-未克隆]
> 来源：deepwiki（索引 2025-04-20, d62dac）+ GitHub README_cn/tree ｜ Java（SpringBoot）｜ 开源版+商业混合
> 一句话定位：**server-agent 架构**的轻量分布式监控（SpringBoot + OSHI）——agent 定时采集主机 CPU/内存/磁盘指标经 HTTP 心跳上报，server 落 MySQL 并告警

## 1. 定位与形态
- 自述：轻量、高性能分布式监控，微服务 SpringBoot 架构，覆盖服务器/应用/数据库/网络设备（deepwiki 引 README.md:13-24）。
- 双组件 Maven 工程（tree 实证）：`wgcloud-server/` 与 `wgcloud-agent/` 各自独立构建部署。
- 版本现状：v2.3.7 起用 **OSHI** 组件替代 sigar 采集主机指标（deepwiki 引 README.md:15-19；README_cn:17）——JVM 生态里 OSHI 正是 psutil 的对应物（见 B05）。
- 平台面极宽（deepwiki Supported Platforms 表）：Linux/Windows/Unix(Solaris/BSD)/macOS(AMD64/ARM64)/ARM/Android/RISC-V64/S390X/树莓派/AIX；数据库支持 MySQL 5.6+/MariaDB/PostgreSQL/Oracle；JDK 1.8 或 11。

## 2. 架构与核心模块（来源：deepwiki System Architecture + git tree）
### 2.1 agent 端（tree 实证 wgcloud-agent/src/main/java/com/wgcloud/）
- `ScheduledTask.java`：定时采集调度（默认每 2 分钟心跳上报，README_cn:19，可配）；
- `OshiUtil.java`：OSHI 封装，采 CPU/内存/磁盘/网络指标；
- `RestUtil.java`：HTTP 上报通道；
- `entity/`：AccountInfo/AppInfo/AppState 等上报实体；
- 辅件：ApplicationContextHelper/CommonConfig/FormatUtil/MD5Utils。

### 2.2 server 端
- SpringBoot 接收 + MySQL 持久化 + 阈值比对 → 告警通道（邮件/微信/短信，deepwiki 引 README）；
- Web UI + 大屏（tree 有 `daping/` 大屏资源目录）；
- 扩展目录（tree 实证）：`docker/ k8s/ GPU/ redis/ nginx/ process/ shell/ crontab/ firewall/`——容器、GPU、中间件监控各有专区。

### 2.3 数据流与通信（deepwiki Communication Model，引 README.md:20-21,83-85）
```
agent（OSHI 采集 → ScheduledTask 定时触发）
  → HTTP POST 指标包 → server
    → MySQL 落库 → 阈值比对 → 告警分发
    → Web UI/大屏展示
```
- 监控能力面（deepwiki Monitoring Capabilities）：主机指标、应用进程存活与资源、数据库、SNMP 网络设备与拓扑、web SSH 与远程命令执行。

### 2.4 顶层目录速览（tree 实证，2335 条目）
| 目录 | 用途 |
|---|---|
| wgcloud-server / wgcloud-agent | 双 Maven 工程主体 |
| sql/ | 建表脚本（server 依赖） |
| docker/ k8s/ | 容器化部署与 K8s 监控 |
| GPU/ | GPU 指标专区 |
| redis/ nginx/ | 中间件监控配置 |
| daping/ | 大屏展示资源 |
| bin/ shell/ crontab/ firewall/ | 运维脚本 |
- agent 端全部类不过 10 个上下（ScheduledTask/OshiUtil/RestUtil + entity）——**采集端刻意保持无脑**，复杂度全部集中 server 侧。

## 3. 与 Agent 记忆的可迁移机制
1. **采集与存储分离的 heartbeat 模式**：
   - agent 只产数据不管历史，server 集中沉淀——对应 Agent"记忆采集端"（轻量、随处部署、只管上报）与"记忆服务端"（持久化、检索、治理）解耦；
   - 采集端失效/下线不丢服务端历史。
2. **sigar→OSHI 的替换教训**：采集层依赖要选维护活跃的跨平台抽象库——记忆采集的 embedding/抽取后端同理应走可替换抽象（与 B05 平台抽象层互证）。
3. **低频心跳 + 阈值告警**：指标型记忆（健康度、成本、延迟）只需 2 分钟级心跳 + 异常才动作的推送语义，避免全量流式处理的成本。
4. **多源统一 entity 信封**：主机/进程/DB/网络各 entity 但同一上报协议——Agent 记忆的事件源（对话、工具调用、任务）也应归一到同一信封 schema，server 端再分表。
5. **单 server+MySQL 的瓶颈反例**：集中式写入有吞吐上限（对照 Prometheus 的拉模型+TSDB）——记忆服务端的写入分片要前置设计。
6. **大屏（daping）作为治理界面**：监控数据的人读出口独立成模块——记忆系统的"可解释出口"（面板/报告）应与数据管道解耦演进。

## 4. 局限
- 结构档未核 Java 源码（行号缺）；开源/商业混合，部分高级能力闭源；
- 文档中文为主，社区代码质量口碑一般；单 server MySQL 写入瓶颈；
- web SSH/远程命令执行是双刃剑——监控面扩大攻击面（tree 有 firewall/ 目录自证安全敏感）；
- 取其架构模式（心跳/分离/信封），不建议直接复用实现；
- 告警通道配置（邮件/微信/短信）耦合在 server，扩展新通道需改代码而非插件化。
