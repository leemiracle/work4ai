# B-12 `sysstat/sysstat`（3.4K★）[结构档-未克隆]
> 来源：deepwiki（索引 2025-05-19, 5278c5）+ GitHub README/tree ｜ C ｜ GPL-2
> 一句话定位：Linux 性能监控的**祖师级全家桶**（sar/sadc/sadf/iostat/mpstat/pidstat）——"采样→二进制归档→多格式回放"的迷你时序数据库，30 年演进的 cron 级节律设计

## 1. 定位与形态
- 职责四分（deepwiki Purpose and Scope）：采集（内核指标）→ 存储（二进制历史）→ 报告（人类可读）→ 分析（瓶颈定位）；设计目标是对被监控系统影响最小。
- tree 实证 5197 条目，根级 ~30 个 .c 文件（activity.c/sa_common.c/rd_stats.c/pr_stats.c/...），man/ 全套手册，xml/ 带 DTD/XSD schema；另有 contrib/ 与测试目录。

## 2. 架构与核心模块（来源：deepwiki Core Components + Data Storage Format）
### 2.1 三分工
- **采集**：
  - `sadc`（System Activity Data Collector）：后台采集器，写二进制；
  - `sa1`：包装脚本，cron/systemd timer 触发（典型每 10 分钟），建日文件 `/var/log/sa/saDD`（DD=日期，按月循环覆盖）；
  - 数据源：/proc 与 /sys（rd_stats.c 采集各类 activity）。
- **回放**：
  - `sar`：读二进制出文本（可实时可历史）；
  - `sadf`：转 **CSV / XML / JSON / SVG / PCP / 文本** 六种格式（sadf.h/sadf.c；DTD 见 xml/sysstat-3.17.dtd）——同一份归档多消费者。
- **专题报告器**：iostat（磁盘+CPU）、mpstat（CPU）、pidstat（**进程级**）、tapestat/cifsiostat；公共代码 sa_common.c/common.c/count.c。

### 2.2 关键机制
- **activity ID 注册表**：每种监控活动一个稳定 ID，定义在 `sa.h:27-71`（deepwiki 引）——格式版本间靠 ID 对齐。
- **自定义二进制格式**（deepwiki 引 sa.h:442-527）：文件头（版本/arch/位数）+ 按时间戳分组的记录集；格式即 ABI，`sa_conv.c` 专门迁移旧版本归档。
- **老化策略**（deepwiki Configuration，引 man/sysstat.in）：
  - `HISTORY=7` 天保留（默认）；
  - `COMPRESSAFTER=10` 天后压缩——**保留窗口与压缩窗口分离的显式配置**；
  - `SADC_OPTIONS` 传参，`SA_DIR=/var/log/sa`。

### 2.3 自动化与输出（deepwiki Configuration / Supported Output Formats）
- 自动化两路线：
  - cron：`sa1`（10 分钟采集）+ `sa2`（每日汇总报告，cron.daily）；
  - systemd：sysstat-collect.timer / sysstat-summary.timer（cron/sysstat.*.timer 实证 tree）。
- 输出格式六向（sadf 选项）：
  | 格式 | 选项 | 用途 |
  |---|---|---|
  | 文本(sar 式) | -p | 传统人读 |
  | CSV | -d | 表格/数据库导入 |
  | XML | -x | 带 DTD 的结构化（xml/sysstat-3.17.dtd） |
  | JSON | -j | Web 应用 |
  | SVG | -g | 浏览器图表 |
  | PCP | -l | Performance Co-Pilot 生态互操作 |
- 通用 CLI 语法：`sar [options] [interval [count]]`——间隔+次数的采样语义全家族一致。

## 3. 与 Agent 记忆的可迁移机制
1. **"原始指标二进制存、展示格式读时定"**：
   - 一份 saDD 归档可随时重放为 sar 文本/CSV/SVG——对应 Agent 记忆"原文不可变存储 + 视图按需渲染"；
   - 反例警示：写入时就烙死呈现格式的记忆，换消费场景就得重算。
2. **固定节律 + 日粒度分片 + 循环覆盖**：
   - 10 分钟节律是"监控记忆"的甜点频率（够看趋势、成本近零）；
   - 按天分片让"N 天热数据"天然可整体淘汰；
   - Agent 遥测记忆（成本/延迟/质量指标）可直接套"日志分片 + HISTORY 保留窗 + 延迟压缩"三段老化。
3. **activity ID 注册表**：记忆事件类型应有全局注册的稳定枚举，schema 演进不破坏旧档（与 B03 状态版本号、B04 ISF 互证）。
4. **sadf 六向导出**：同一份数据面向不同消费者（人看 SVG、库吃 JSON、迁移走 PCP）——导出器与存储解耦。
5. **sa_conv 的存在即教训**：二进制格式一旦有用户就必须带迁移工具——Agent 记忆的序列化格式同样要版本化 + 迁移脚本。
6. **pidstat 的进程级下钻**：系统级(CPU 总量)与个体级(单进程)同格式报告——记忆统计也应支持"全局概览 + 单条目下钻"两级视图。

## 4. 局限
- Linux 专属；无语义层（只有计数器，无"为什么"）；
- 10 分钟默认粒度错过突发（sar 可手动高频补采但有开销）；
- 单机工具，无分布式（对照 B09）；结构档未核 C 源码行号（引 deepwiki）；
- 二进制格式版本随发行版演进（12.x→13.x 曾有格式断裂），跨版本读旧档需同版本 sadf 或 sa_conv。
