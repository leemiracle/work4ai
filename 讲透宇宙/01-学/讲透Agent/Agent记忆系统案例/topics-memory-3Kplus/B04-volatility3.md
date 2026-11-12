# B-04 `volatilityfoundation/volatility3`（4.3K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\volatilityfoundation__volatility3（develop HEAD `958be9b`，2026-08）
> Python ≥3.8 ｜ VSL 许可 ｜ pyproject 分发，stable/develop 双分支
> 一句话定位：**内存取证框架**——从一份"死"的原始 RAM 镜像出发，不依赖被调查系统任何配合，逐层重建出进程/对象/时间线等完整运行时状态；对"记忆重建"（从残缺原始数据恢复结构化叙事）是最佳工程参照

## 1. 架构总览（目录地图）

```
volatility3/
├── vol.py / volshell.py          # CLI 入口 / 交互式分析 shell
└── volatility3/
    ├── framework/
    │   ├── automagic/            # ★ 自动配置发现：stacker(层栈)/pdbscan(符号)/windows/linux/mac(各 OS 特化)
    │   ├── layers/               # 16 种地址空间层：
    │   │                         #   physical(FileLayer)/linear/segmented/intel(页表)/vmware/crash/
    │   │                         #   lime/elf/qemu/xen/avml/leechcore/cloudstorage/msf/registry
    │   ├── symbols/              # ISF(JSON) 符号表加载
    │   ├── objects/              # 按符号模板把字节重建为 C 对象（含指针跟随）
    │   ├── plugins/              # ★ 真实插件：windows/ linux/ mac/（各 30+）+ 泛型
    │   │                         #   timeliner/yarascan/banners/vmscan/regexscan/isfinfo/...
    │   ├── interfaces/           # 五大抽象接口（layers/objects/plugins/automagic/configuration）
    │   ├── renderers/            # 输出格式（conversion.py/format_hints.py）
    │   └── contexts/ configuration/ constants/
    ├── plugins/                  # 插件发现路径（--plugin-dirs 外置挂载点；windows/ 下仅剩薄壳）
    └── symbols/                  # 符号包落盘（windows.zip/mac.zip/linux.zip，README:64-89）
```

关键分层思想（每层只依赖下层的抽象接口）：

```
Context（运行态容器：对象表 + 层表 + 配置树，可 clone）
  → Layers（地址翻译栈：物理→格式→页表→进程）
    → Symbols（版本化类型知识 = 读取 schema）
      → Objects（按模板重建的实例）
        → Plugins（分析算法，输出经 Renderer）
```

- Context 的配置树（configuration/）把"怎么读这份镜像"的全部决策序列化——**重建过程本身可存档重放**（LayerStacker 成功后 `build_configuration()` merge 回去，stacker.py:140-144）；
- symbols 包三件套 windows.zip/mac.zip/linux.zip 落盘 `volatility3/symbols/`，Mac/Linux 需 dwarf2json 手制，Windows 可在线查 PDB（README.md:64-89）。

## 2. 核心机制深读

### 2.1 LayerStacker：试错式层栈重建（`framework/automagic/stacker.py`）
- 最高优先级 automagic（`priority = 10`，stacker.py:40），在一切分析之前运行（docstring :34-37 自述"为后续 automagic 提供尽可能完整的配置树"）。
- 成功结果缓存（`self._cached`，stacker.py:96-107）：同进程二次运行直接复用层栈配置——**发现是昂贵的，结论应当缓存**。
- 重建循环（`stack_layer`，stacker.py:208-244）：
  1. 以 `FileLayer`（物理层）起步（:122-125）；
  2. 候选层按 `stack_order` 排序（`create_stackers_list`，:246-261）；
  3. 逐个尝试 `stacker.stack(context, initial_layer)`——某层（如 WindowsIntelStacker）能在现有层之上合法构建（如找到有效页表）就叠上去；
  4. **每类层至多用一次**（成功后从候选移除，:243）；
  5. 直到再也叠不上去，返回层名栈（高→低）。
- **试验不污染真实状态**：在 `context.clone()` 上试叠（:109），成功后仅把最终层 `build_configuration()` merge 回原 context（:140-144；docstring :177-183 明示此五步模式）。
- 失败是常态：stacking 异常只进 VVV 级日志（:227-236）——**试错即协议**；
- `find_suitable_requirements` 把叠好的层绑定到插件的 TranslationLayerRequirement 上（:263+），插件随后按需实例化——发现与使用解耦。

### 2.2 地址翻译层（`framework/layers/intel.py`）
- `Intel` 基类持 `page_map_offset`（DTB/页表基址，intel.py:60），`_translate` 逐级走页表把虚拟地址译回物理（:155-183）；
- 子类区分分页模式：`IntelPAE`（:457）/ `Intel32e`（:473）/ `WindowsMixin`（:492）；
- `is_valid` 校验地址可用性（:308）；脏页检查 `_page_is_dirty`（:322）。
- 16 种格式层（vmware/crash/elf/lime/qemu/xen/...）把各种来源统一成 `DataLayer` 接口——**输入格式的多样性被吸收在最底层**，上层完全不感知。

### 2.3 DTB 发现与符号发现（Windows 例，"无元数据自举"）
- `PageMapScanner` 扫描物理内存找**自引用页表项**（页目录里指向自己的项；`automagic/windows.py:223`）；
  - 判据类 `DtbSelfReferential` 及变体：32/64/PAE/旧 Windows（windows.py:89-190），覆盖各代内核自引用位置差异；
- `KernelPDBScanner`（`automagic/pdbscan.py:36`）：扫 RSDS PDB 签名确定内核 build → 按需下载/生成 ISF 符号表；KDBG 偏移走特征扫描（`method_kdbg_offset`，pdbscan.py:353-359，method 表 :463）。
- 符号 = **外置的、版本化的"读取 schema"**：同一份字节，配上不同符号表会读出不同结构。

### 2.4 对象重建与进程列举（双路验证）
- `framework/objects` 按 ISF 模板把字节解释成 `_EPROCESS` 等 C 结构（指针跟随、引用计数语义）。
- 进程列举双路：
  - **链表遍历**（pslist：沿 ActiveProcessLinks）——快，但链表可被 rootkit 摘链；
  - **池扫描**（psscan：全内存扫 `_POOL_HEADER` + 对象特征）——慢而全；
  - **两者之差 = 隐藏进程**。结构化索引不可信时，全量扫描兜底。

### 2.5 Timeliner：多源时间线重建（`framework/plugins/timeliner.py`）
- 事件类型枚举：`CREATED/MODIFIED/ACCESSED/CHANGED`（timeliner.py:21-25）。
- `TimeLinerInterface.generate_timeline()` 产出 `(description, 类型, datetime)` 三元组流（:28-44）；
  - 接口契约明言"**无需有序，排序后置**"——把顺序责任从数据源移走，降低实现门槛。
- `Timeliner` 插件聚合**所有**实现该接口的插件（`framework.class_subclasses(TimeLinerInterface)`，:61-65），统一排序输出 body 文件。
- 实现方举例：`windows/dlllist.py:21,199`、`linux/lsof.py:109,222`、`linux/bash.py:147`、`mac/bash.py:20,149`（均 `grep` 实证）。
- 这是"episodic 记忆重建"的通用输出形态：**任何能产时间证据的分析器都可插拔进同一条时间线**。

### 2.6 工程细节
- 插件接口版本化：`_version`/`_required_framework_version` 契约（timeliner.py:34,51-52）——框架与插件独立演进。
- 外置插件：CLI `--plugin-dirs` 改写 `volatility3.plugins.__path__`（`cli/__init__.py:283-286`）；develop 分支正把 OS 插件外置分发（`volatility3/plugins/windows/` 仅剩 statistics.py 薄壳，真实实现在 `framework/plugins/windows/`）。
- 泛型插件先行的思路：yarascan（YARA 规则扫内存）、vmscan（在物理内存中找嵌套虚拟机，`PageStartScanner` vmscan.py:28）、banners（Linux 版本横幅扫描）——**不依赖符号的粗粒度分析**永远可用。

## 3. 命令与插件速览（tree/grep 实证）
- 入口：`vol -f <镜像> <插件>`（README.md:35-39 示例 `vol -f stuxnet.vmem windows.info`）；交互式 `volshell.py`。
- 泛型插件（framework/plugins/，不依赖符号先可用）：
  - `banners.py`（Linux 版本横幅扫描）/ `yarascan.py`（YARA 规则扫内存，:39,105）/ `vmscan.py`（物理内存中找嵌套 VM，:28,56）/ `regexscan.py` / `isfinfo.py` / `configwriter.py` / `layerwriter.py` / `timeliner.py`。
- OS 插件（framework/plugins/{windows,linux,mac}/，各 30+ 文件，grep 实证举例）：
  - windows：pslist/pstree/psscan/dlllist/cmdline/cmdscan/consoles/malfind/dumpfiles/driverscan/filescan/bigpools/callbacks/devicetree/desktops/cachedump/envars/debugregisters/etwpatch/direct_system_calls/amcache...
  - linux：pslist/pstree/lsof/lsmod/elfs/envars/kmsg（四代内核日志格式分派 :206-385）/bash/check_syscall/hidden_modules/kallsyms/graphics/fbdev...
  - mac：pslist/pstree/lsof/bash/kevents/netstat/malfind/check_syscall...
- TimeLiner 实现方（generate_timeline 存在性 grep 实证）：windows/dlllist.py:21,199、linux/lsof.py:109,222、linux/bash.py:21,147、mac/bash.py:20,149、linux/boottime.py:14,85。
- 渲染器（framework/renderers/）：conversion.py + format_hints.py——文本/JSON/CSV 输出与类型提示格式化，插件只产数据行，呈现交给渲染器。

## 4. 与 Agent 记忆的可迁移机制（"记忆重建"视角）

1. **层栈 = 记忆读取的多级索引 + 逐级校验**。
   - 向量库/倒排索引/原文 chunk 的关系恰如 intel 层之于物理层：高层读取逐级翻译、每级 `is_valid`；
   - 任何一级损坏只降级不崩溃；Agent 记忆系统几乎从不校验索引-原文一致性——"试验-确认-叠加"循环是直接模板。
2. **符号表 = 与写入时 schema 解耦的读取知识**。
   - 记忆写入方（旧版 prompt/抽取器）与读取方（新版 Agent）之间需要版本化 ISF；
   - 否则字段语义漂移无人察觉；最小实现 = 记忆条目附 schema 版本号。
3. **无元数据自举**：自引用扫描找 DTB、PDB 签名定版本——记忆系统冷启动/灾难恢复时，也应有能力从**裸数据特征**（而非依赖索引）重新定位结构。
4. **双路验证（遍历 vs 扫描）= 记忆一致性审计**：定期全量扫描 vs 增量索引的差集，就是"隐藏/丢失的记忆"。
5. **Timeliner 接口模式 = episodic 重建的总线**：各分析器只吐 `(描述, 事件类型, 时间)`，排序聚合一层完成；Agent 的记忆回放应让对话日志、工具调用、任务事件全部汇入同一条可排序时间线。
6. **context.clone 试错**：破坏性记忆整理（合并、重写）先在克隆上下文演练，成功后仅 merge 结果。
7. **无符号的粗粒度分析永远可用**（yarascan/banners 模式）：符号/索引缺失时退化为特征扫描，功能降级而非不可用。
8. **重建过程可序列化**：Context 配置树把"怎么读这份镜像"的全部决策存档，可重放——Agent 记忆的检索/整理过程同样应可存档复现（审计与调试需要）。

## 5. 局限
- 依赖符号：无符号的内核/加壳进程只能字节级扫描，慢且浅。
- **单时间点快照**：RAM 镜像没有历史，时间线只有元数据自带的时间戳——提醒 Agent 记忆：只存最终状态等于快照，重建叙事必须留事件流。
- 性能：全镜像扫描分钟级，仅离线场景。
- 复杂度门槛：automagic 自动化了大部分，故障时仍需理解层栈调试。
- 工程注记：develop 分支插件外置化进行中（`volatility3/plugins/windows/` 仅剩 statistics.py + registry/ 薄壳）——"框架实现"与"发现路径"分离的过渡态，读源码时勿混淆两处 plugins 目录；
- 首跑符号缓存构建耗时且可断点续跑（README.md:86-87）——重资源初始化要可恢复。
