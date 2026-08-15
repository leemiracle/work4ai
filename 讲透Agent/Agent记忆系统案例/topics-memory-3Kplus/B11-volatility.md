# B-11 `volatilityfoundation/volatility`（8.1K★，legacy v2）[结构档-未克隆]
> 来源：deepwiki（索引 2025-04-19, a438e7）+ GitHub README/tree ｜ Python 2 ｜ GPL
> 一句话定位：内存取证框架的**上一代**（2007-2019）——200+ 插件生态的集大成者，但其"profile 硬编码"架构正是 v3 要推翻的东西；本篇以与 v3 的差异为主

## 1. 定位与形态
- 五件套架构（deepwiki Framework Architecture，引 README.txt:4-13）：
  Address Spaces（地址空间栈）→ Object System（vtypes 解释原始字节）→ Profile（OS+版本绑定的类型与配置包）→ Command/Plugin 系统 → Renderer。
- tree 实证（491 条目）：
  - `volatility/plugins/overlays/windows/win10_x64_19041_vtypes.py` 等**每内核版本一个手写 vtypes 大文件**（含 17763/18362/19041 的 x64/x86 变体）；
  - 插件按域分目录：gui/linux/mac/malware/registry/addrspaces/overlays；
  - `contrib/` 放第三方扩展，`tools/` 放符号制作工具。
- 支持面（deepwiki Supported Platforms/Memory Formats）：Windows XP~Win10/Server2016、Linux 2.6.11~5.5、macOS 10.5~10.15；输入格式 raw/休眠文件/crash dump/VirtualBox/VMware/EWF/LiME/Mach-O/QEMU/FireWire/HPAK（README.txt:74-88）。
- 使用范式两步走（deepwiki Basic Usage）：
  1. `python vol.py imageinfo -f memory.raw` 猜 profile；
  2. `python vol.py --profile=Win10x64_19041 pslist` 显式指定后跑插件。
- 交互式 volshell 与 v3 同名继承（deepwiki Advanced Features）；自定义插件开发文档化（deepwiki Developing Custom Plugins）。
- 200+ 插件覆盖进程/注册表/网络/文件系统/恶意软件检测（README.txt:136-486）。

## 3. 插件域分类（deepwiki Plugin Categories + tree 实证）
| 域 | 代表插件（目录实证） | 对应能力 |
|---|---|---|
| 进程分析 | plugins/ 下 pslist/pstree/psscan/dlllist/cmdline | 链表遍历 vs 池扫描双路 |
| 内存与对象扫描 | bigpagepools.py（deepwiki 引 :179-237） | 池标签扫描 |
| 恶意软件检测 | malware/svcscan.py（deepwiki 引 :540-594）、malfind/apihooks | 服务/注入/钩子检测 |
| 注册表分析 | plugins/registry/ | 离线注册表解析 |
| 文件系统 | filescan/dumpfiles | 从内存恢复文件 |
| 网络 | connections/sockets | 从池与对象重建连接表 |
| GUI | plugins/gui/（含 vtypes 子目录） | 窗口/消息取证 |
| 地址空间 | plugins/addrspaces/ | 各镜像格式的翻译层 |
- overlays 结构（deepwiki Object System，引 win10.py:42-322）：base 对象类型 → OS 特化 overlay → 版本特化 vtypes——**三层继承最大化复用**，这是 v2 最优雅的部分，被 v3 的 ISF+objects 继承。

## 4. 与 v3 的关键差异（本篇重点，一段带过 + 对照表）
v2 的 Profile 是**编译期绑定的知识包**：类型定义、系统调用表、内核偏移全部硬编码在仓库的 per-version Python 文件里；新增 OS 版本 = 社区提交新 profile 文件；分析前必须人工选对 profile，选错则全盘乱解。

| 维度 | v2（本仓） | v3（见 B04） |
|---|---|---|
| 类型知识 | 手写 vtypes .py 硬编码在仓库 | ISF JSON 符号表外置，可运行时下载/生成 |
| 配置发现 | 人工 imageinfo + --profile | automagic 自动层栈（LayerStacker priority=10） |
| Windows 符号 | profile 文件携带 | PDB 签名扫描 → 自动下载生成（KernelPDBScanner） |
| 插件接口 | 隐式约定 | 版本化契约（_version/VersionableInterface） |
| 语言 | Python 2（EOL） | Python 3.8+ |
| 维护状态 | 停止维护 | 活跃（develop 分支插件外置化进行中） |

v2 的历史价值在插件算法思想（池扫描找隐藏进程、VAD 树遍历、api hook 检测、svcscan）——全部被 v3 继承重写。

## 5. 与 Agent 记忆的可迁移机制
1. **"硬编码 schema 每版本一文件" vs "外置符号+自动发现"** 的演进是记忆系统的直接教训：
   - 记忆的解释知识（写入时 schema/prompt 版本）若硬编码在代码里，每次记忆格式演进都要发版；
   - 外置 + 版本化 + 运行时匹配（v3 的 ISF + automagic）才是可维护路径。
2. **人工两步流程是架构债的信号**：记忆读取方若需要"人工指定元信息"才能正确解码（v2 的 --profile），说明 schema 发现没有自动化——对照 B04 的 automagic。
3. **三层 overlay 继承**（base 类型 → OS 特化 → 版本特化）仍值得抄：记忆条目的类型系统可按"基础字段 → 领域扩展 → 版本扩展"分层叠加，而非每次版本升级复制全量 schema。
4. **插件生态先于框架完美**：v2 靠 200+ 插件立住生态地位，即便架构被推翻，插件算法思想完整迁移到 v3——记忆系统的"分析器生态"（过滤器/摘要器/审计器）比存储内核更长寿。

## 6. 局限
- Python 2、无维护、新内核不支持；除历史参照与算法思想外不建议投入；
- 结构档：未核源码，架构论断依赖 deepwiki/README/tree 交叉印证；
- 每支持一个新 OS 版本的边际成本极高（手写 vtypes），这是它被 v3 取代的根本原因；
- 快照单时间点限制与 v3 相同（见 B04 §5）；
- 输入格式支持列表看似很长（11 种），但每种的地址空间层各自实现——格式层的复用不如 v3 的统一 DataLayer 抽象；
- 深度休眠/crash dump 等格式的解析正确性随 OS 版本漂移，v2 后期维护跟不上是常态。
