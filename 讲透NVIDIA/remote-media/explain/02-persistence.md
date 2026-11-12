# 02 · src/persistence.hpp + src/main.cpp — 掉电安全的持久化与启动 replay

> 源码：`src/persistence.hpp`（345 行）+ `src/main.cpp`（407 行）+ `xyz.openbmc_project.VirtualMedia.service`（23 行）· 图谱定位：5 层第 2 层「状态机与持久化核心层」· 配套设计文档 docs/persistent-mount.md（486 行，Status: Implemented）

## 一、角色定位：BMC 重启后挂载不丢的守护者

没有这套机制时，virtual-media 挂载随服务进程消亡——BMC 固件升级、掉电、看门狗重启都会丢光挂载，运维必须重新下发 Mount（docs/persistent-mount.md:12-22 的动机）。持久化模块解决"主机从 BMC 自 hosted 的镜像启动"这类无人值守场景：设计目标 G1-G6（重启存活 :24、按槽位 opt-in :26、**不落盘任何秘密** :27、掉电/损坏不 brick 启动 :28、容忍后挂载文件系统 :29、与 FSM 解耦可单测 :30，docs/persistent-mount.md:24-31）。

工程形态是三个文件的协作：persistence.hpp 是纯函数库（不依赖 FSM 任何内部类型，头注释 :5-9 钉版 standalone 与"三个窄接口"），main.cpp 的 App 提供 hook #1（启动 replay :62-72），state_machine.hpp 提供 hook #2/#3。本文按"资格→写→读→恢复"四段讲透。

## 二、内部结构：SavedMount POD + 槽位文件 + 四个自由函数

落盘模型极简：每槽位一个 JSON 文件 `/var/lib/virtual-media/persist/<slot>.json`（:28），内容是 SavedMount POD（slot/imageUrl/rw 三字段，:68-73）+ SchemaVersion=1（:61，版本不符即弃，:66-71 读取侧）。目录由 systemd `StateDirectory=virtual-media/persist` 以 0700 root:root 建好（service:15-16，注释 :10-14 与 persistence.hpp:56-57 的 defaultStateDir 互为镜像、人工同步）；代码侧 ensureStateDir 兜底 create_directories + owner_all 权限（:98-113）。测试经 mutable 单例 stateDirRef/setStateDir 重定向（:77-91，tests/test_persistence.cpp:147 即用）。

**资格判定 isPersistableUrl**（:123-127）：`utils::isFileUrl && !utils::hasEmbeddedUrlCredentials`——file:// 且 URL 不带 `scheme://user:pass@` 内嵌凭据（后者 fail closed，防秘密落盘）。槽位侧的 AllowedLocalMountPoints opt-in 由 FSM 检查（:14-19 头注释明确"本模块不自裁资格"）。

**原子写 writeState**（:157-219）四步：序列化四字段 JSON（:165-169）→ 写 `<slot>.json.tmp`（:172-194，写失败即删 tmp 返回）→ fsyncPath(tmp)（:197）→ fs::rename 原子顶替（:203，同文件系统 rename(2) 原子）→ fsyncPath(stateDir()) 刷目录项（:212）。fsyncPath（:131-150）的注释 :129-130 点破关键常识：ofstream 的 flush/close 只到页缓存，::fsync 才让字节与目录项真正耐掉电。任何一步失败都 best-effort 返回 false——调用方约定"持久化失败绝不阻塞挂载"（:154-156）。

**自愈读 loadState**（:246-300）：dropFile lambda（:255-260）删坏文件；五类废品——解析异常（:295-298）、SchemaVersion 不符（:266-271）、Slot 字段与文件名不符（:276-280）、空 ImageURL（:281-285）、非 file:// 或带凭据（:286-292，连老版本程序落盘的远程 URL 也一并清掉）。**enumerateSavedSlots**（:305-343）扫目录取全部合法条目，损坏文件作为 loadState 副作用被清，下次 boot 只 replay known-good。**clearState**（:224-241）删除槽位文件，不存在也算成功（幂等）。

## 三、外部连接：三个 hook 的注入点

- **hook #1（启动 replay，main.cpp:62-72）**：App 构造尾部 `boost::asio::post` 异步触发——挂在事件循环而非内联，保证子进程 spawn 发生在 main() 的 ioc.run() 上下文（注释 :67-70）。
- **hook #2（激活即存，state_machine.hpp:157-186）**：ActiveState::onEnter；replay 路径会重写同样内容自愈半写文件（:170-172）。
- **hook #3（卸载即清，state_machine.hpp:644-648）**：UnmountEvent 三分支都清；SubprocessStoppedEvent **故意不清**（:645-646）——崩溃留下 descriptor 正是 replay 输入。

测试面：tests/test_persistence.cpp 的 PersistenceFsTest fixture 每用例建独立 tmp 目录 + setStateDir（:133-154），writeRaw 注入任意字节（:159）；20 个 TEST_F 覆盖命名/往返/JSON 形状/五类废品/幂等清理/枚举过滤（:174-383），另有 6 个 UrlPredicates TEST（:35-100）。

## 四、数据流：一次掉电与一次重启的走读

**掉电窗口**：writeState 任一时刻断电——tmp 写一半（正式文件未动，读到旧状态）、rename 已做但目录未 fsync（rename 要么在要么不在，都是完整文件）。不存在"半个 JSON 被当真"的路径。

**重启 replay**（replayPersistedMounts，main.cpp:94-169）：enumerate（:96）→ 逐条对账：槽位已从配置消失→clearState（:107-113）；失去 AllowedLocalMountPoints opt-in→clearState（:125-133）；非 Legacy 模式→clearState（:137-144）；其余交给协程 driveReplayMount（:164-167，spawn 到 ioc）。**driveReplayMount**（:190-323）每轮：非 ReadyState 则留待下次 boot（:204-210）；file:// 先等后端文件系统（注释 :146-156 钉版当初"stat 不存在就清"是破坏性 bug——后挂载分区的 boot 竞态会永久抹掉合法挂载）；重播 target 种子（:241-242，ReadyState::onEnter 会 reset 所以每轮重种）→ emitMountEvent（:249）→ 120×100ms 轮询落定（:265-282）；Active 即成（:284-289）；唯一立即清除的条件是 allow-list 拒绝（错误消息匹配 localMountNotAllowedError，state_machine.hpp:43-44，:293-305）；其余失败 5 次 × 5s 退避（常量 :176-177）后**保留 descriptor**（:320-322）。

## 五、设计决策：四条可迁移的工程格言

1. **窄接口解耦**：persistence 只说 slot 字符串与 POD，FSM 只经 save/clear/enumerate 三点接入（:5-9）——26 个用例能单测全部语义，靠的就是这条边界。
2. **写路径三明治（tmp+fsync+rename+dirsync）**：比 O_DIRECT 简单、比锁文件可靠，是嵌入式掉电安全的标准姿势；代价是每次写两个 fsync，但挂载是低频操作。
3. **读侧永远自愈、写侧永远 best-effort**：损坏输入不 brick 启动（G4），持久化失败不阻塞业务（writeState 注释 :154-156）——两个方向都朝"服务可用性优先"倾斜。
4. **重试策略区分"必败"与"偶败"**：allow-list 拒绝每次必败立即清；文件系统竞态偶败退避且永不删——replay 注释（main.cpp:291-305）把判定依据写得明明白白。

## 六、新人提示

- 改 JSON 字段必须 bump stateSchemaVersion（:59-61），否则老文件按新格式误读——loadState 的版本闸（:266-271）就是为此。
- 目录位置是双源真值：systemd StateDirectory 与 defaultStateDir 人工同步（service:10-14），搬目录两处一起改。
- 想本地做掉电实验：BUILD_TESTS=ON 跑 ctest 后，在 tmp 状态目录里手工制造 truncate 一半的 JSON，再起服务看 dropFile 日志——自愈读眼见为实。
- 调 replay 失败时按三问排查：槽位还有 opt-in 吗（:125）？是 Legacy 吗（:137）？文件系统挂了吗（:216-237）？三者分别对应清除、清除、保留三种结局。
- 别把远程 URL 塞进 SavedMount——isPersistableUrl 在写读两侧都拦（:123-127 + :286-292），绕过它就违反 G3"不落盘任何秘密"的红线。
