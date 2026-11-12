# remote-media 新人上手文档（ONBOARDING）

> 基于知识图谱（72 节点 / 136 边 / 5 层 / 6 步导览，commit `cee2e0e5`，fingerprints 24 文件基线）生成，全部行号锚经源码逐行核实。
> 仓库：`/usr-data/data2/repos/agent-repos/NVIDIA/remote-media`（NVIDIA 维护的 OpenBMC remote-media 服务）

## 1. 项目定位与一句话理解

**一句话**：remote-media 是 OpenBMC 的 VirtualMedia 守护进程（D-Bus 名 `xyz.openbmc_project.VirtualMedia`，systemd 单元 xyz.openbmc_project.VirtualMedia.service:20）——把远程或本地的 ISO/磁盘镜像经 NBD 设备 + USB gadget 伪装成 BMC 的虚拟 CD/USB，供主机从远端介质启动或安装系统。

三个协议入口对应三类镜像源：`https://`（curl 拉流）、`smb://`（mount.cifs 挂 CIFS 共享）、`file://`（本地文件）——scheme 谓词统一在 utils.hpp（isFileUrl utils.hpp:112、isHttpsUrl utils.hpp:118、isCifsUrl utils.hpp:124）。业务核心是**每个挂载点一个状态机**：main.cpp 的 App 为配置里每个 MountPoint 建一个 MountPointStateMachine（main.cpp:48-53），全部 1467 行的 state_machine.hpp 承载状态×事件转移、D-Bus 接口暴露、子进程（curl/nbd-server）管理与 USB gadget 生命周期。

**第一颗勘误钉版**：仓根 README.md 是 GitLab 自动生成的空模板（Getting started/Add your files 等样板），**不含任何本项目架构信息**；真实设计文档是 docs/persistent-mount.md（486 行，Status: Implemented，其 Source 栏 :10 直接点名 persistence.hpp/state_machine.hpp/main.cpp 与 systemd 单元四个实现文件）——查设计动机请从它进，别在 README 里找。

本仓最有分量的故事是**持久化挂载**（docs/persistent-mount.md:12-31 的动机与 G1-G6 目标）：BMC 重启后自动恢复 Legacy 挂载、opt-in 槽位资格、不落盘任何秘密、掉电安全原子写——这套机制是全仓测试覆盖的唯一模块，也是本文档第 5 节的主角。

## 2. 五分钟上手

构建（CMakeLists.txt 定义 virtual-media 可执行文件，链接 sdbusplus/udev/boost_coroutine/context/phosphor_logging/systemd；cmake/Findudev.cmake:1 经 PkgConfig 与候选路径探测 libudev）：

```bash
cmake -B build && cmake --build build            # 主目标 virtual-media
cmake -B build -DBUILD_TESTS=ON && ctest --test-dir build   # 26 个 gtest 用例
```

运行形态是 systemd 服务（xyz.openbmc_project.VirtualMedia.service:17-18）：`ExecStart=/usr/sbin/virtual-media`、`Restart=always`、`Type=dbus` 按需拉起。两个关键目录由单元声明：`RuntimeDirectory=virtual-media`（运行期 socket 区，service :9）与 `StateDirectory=virtual-media/persist`（0700 持久化目录，service :15-16，注释 :10-14 明言与 persistence.hpp 的 defaultStateDir 人工同步）。

配置读 `/etc/virtual-media.json`（main.cpp:374）：默认样例 virtual-media.json 定义全局 `InactivityTimeout: 1800`（virtual-media.json:2）与三个挂载点——Slot_0（Mode 0=Proxy，nbd0，virtual-media.json:4-7）、USB1/USB2（Mode 1=Legacy，nbd2/nbd3，virtual-media.json:12,:20）——Mode 枚举 proxy=0/legacy=1 定义在 configuration.hpp:17-27。**注意配置缺失即退出**：loadConfiguration 打不开文件时 Critical 日志 + return false（configuration.hpp:74-79），main 直接返回 -1（main.cpp:375-379）——图谱摘要所谓"警告并以空配置继续"不成立。

## 3. 架构总览（按 5 层图谱）

**L01 服务装配与配置层**（5 文件）：systemd 单元 + main.cpp（App 类 + replay 协程）+ configuration.hpp（Configuration 类 :67 构造即解析，setupVariables :97-263 是全文件最大装配函数，updateAllowedLocalMountPoints :264-279 支持运行时刷新）+ virtual-media.json + 模板 README。

**L02 状态机与持久化核心层**（3 文件）：state_machine.hpp（1467 行业务中枢，fanOut=36 全仓最大）+ persistence.hpp（345 行，刻意与 FSM 解耦的独立头，头注释 persistence.hpp:5-9 写明 standalone 设计与三个窄接口）+ docs/persistent-mount.md（权威设计文档）。

**L03 系统与介质设施层**（4 文件）：system.hpp（NBDDevice :61-189 封装 /dev/nbd* 生命周期；DeviceMonitor :199-362 以 libudev+boost.asio 监视块设备插拔）+ smb.hpp（mount.cifs 封装，凭据注入检查 smb.hpp:29-39）+ utils.hpp（416 行，凭据安全三件套 + URL/ISO 谓词族）+ logger.hpp（编译期分级日志）。

**L04 质量保障层**（1 文件）：tests/test_persistence.cpp（399 行、26 个用例）——专测持久化的原子写/自愈读语义，fixture 经 setStateDir 重定向到临时目录（tests/test_persistence.cpp:147），writeRaw 辅助注入损坏数据（:159）。

**L05 仓库工程化配置层**（11 文件）：CMakeLists + Findudev + 九个 `*-ignore` 文件（内容均为 `*`，对 GitLab 内置九种格式化/lint 工具全量豁免）——体量最大语义最薄的尾巴层。

依赖方向：L02 是语义核心，L01 装配它，L03 被它踩在脚下，L04 测它的持久化半边，L05 纯工程卫生。无环。

## 4. 深潜一：variant 状态机（六状态 × 六事件）

state_machine.hpp 不用继承式状态模式，而以 `using State = std::variant<...>` 表示状态（state_machine.hpp:207-209）。**六个状态全部是 MountPointStateMachine 的嵌套 struct**（tree-sitter 对嵌套类型全盲，图谱这批节点是批分析按源码手工补的）：

| 状态 | 行号 | 职责 |
|---|---|---|
| InitialState | state_machine.hpp:84 | 起点空态 |
| ReadyState | state_machine.hpp:92 | 空闲；onEnter 清理上次挂载（SmbShare::unmount :112） |
| ActivatingState | state_machine.hpp:122 | 激活中；onEnter 复位失败标志并自驱 emitActivationStartedEvent（:128-136） |
| WaitingForGadgetState | state_machine.hpp:139 | 等 USB gadget 就绪 |
| ActiveState | state_machine.hpp:148 | 挂载成功态；**持久化 hook #2 在此**（:155-187） |
| WaitingForProcessEndState | state_machine.hpp:192 | 等子进程退出的收尾态 |

**第二颗勘误**：图谱 tour 描述的状态名（Invalid/Initial/Waiting/Active/Detached/Busy）与源码不符——以上表六个为准。

**六个事件**（BasicEvent 基类 state_machine.hpp:211-253，声明对六种状态的 `virtual State operator()` 重载、默认全部转 transitionError :216-251，派生事件只覆写能处理的状态分支——一张显式状态转移表）：RegisterDbusEvent :255（在 InitialState 上建三类 D-Bus 接口）、MountEvent :622（仅 ReadyState→ActivatingState :627-630，其余状态抛 InvalidStateError "Could not mount on not empty slot" :632-635）、UnmountEvent :638（按四态分别走清理路径，含 **持久化 hook #3** :644-648）、SubprocessStoppedEvent :686（子进程退出回退）、ActivationStartedEvent :732（全文件最大单元约 475 行：按 https/smb/file 三源起子进程、配 USB gadget）、UdevStateChangeEvent :1207（NBD 设备尺寸/就绪变更）。

分发核心 emitEvent（state_machine.hpp:1382-1392）只有两行实质：`state = std::visit(event, state)`（:1388，事件仿函数对当前状态重载分派产生新状态）+ `std::visit([](BasicState& s){ s.onEnter(); }, state)`（:389，进态钩子）——variant 状态机的标准 C++ 惯用法，非法转移由事件抛 InvalidStateError（MountPointStateMachine::InvalidStateError 定义 :29-33）。异常路径经 phosphor-logging 上报 Redfish 事件日志（如 Unmount 成功路径的 sendEvent RESOURCE_DELETED，state_machine.hpp:672-675）。

## 5. 深潜二：掉电安全的持久化（三 hook + 原子写 + 自愈读）

**资格三条件**：槽位在 virtual-media.json 配了非空 AllowedLocalMountPoints（MountPoint 字段 configuration.hpp:38）× 镜像是 file://（isPersistableUrl 同时拒绝内嵌凭据的 URL，persistence.hpp:123-127）× Legacy 模式。https/smb 远程挂载**不持久化**（头注释 persistence.hpp:14-19 与 ActiveState::onEnter 注释 state_machine.hpp:175-177 都钉了这条，待 Redfish EjectPolicy: Persistent）。

**三个 hook 的编号就写在注释里**：

- **hook #1 启动 replay**（main.cpp:62-72）：App 构造完所有槽位后 `boost::asio::post` 异步调 replayPersistedMounts（:94-169）——enumerate 全部 SavedMount（:96），对槽位消失（:107-113）、失去 opt-in（:125-133）、非 Legacy（:137-144）三类**真陈旧**条目清状态；其余交给 driveReplayMount 协程（:190-323）。
- **hook #2 激活即存**（state_machine.hpp:157-186）：ActiveState::onEnter 里 `slotOptedIn && persistable` 即 writeState；注释明言 best-effort——持久化失败不能把用户刚请求的挂载搞砸（:168-170），且 replay 路径会重写同内容以自愈上一次boot的半写文件（:170-172）。
- **hook #3 卸载即清**（state_machine.hpp:644-648）：UnmountEvent 显式清理；**注释特别钉版：SubprocessStoppedEvent 故意不清**（:645-646）——子进程崩溃留下的 descriptor 正是下次启动 replay 的输入。

**原子写四步**（writeState，persistence.hpp:157-219）：JSON 序列化（SchemaVersion/Slot/ImageURL/RW 四字段，:165-169）→ 写 `<slot>.json.tmp` 并 close（:176-194）→ `fsyncPath(tmp)` 刷盘（:197，fsyncPath 实现 :131-150，头注释 :129-130 点破 ofstream flush 只到页缓存）→ `fs::rename` 原子顶替（:203，同文件系统 rename 原子）→ 再 fsync **目录**（:212）让 rename 本身也耐掉电。掉电窗口里只可能存在完整旧文件或完整新文件，永不出现半个 JSON。落盘布局 `/var/lib/virtual-media/persist/<slot>.json`（:28、:56-57）。

**自愈读**（loadState，persistence.hpp:246-300）：解析失败（:295-299）、SchemaVersion 不符（:266-271）、slot 不匹配（:276-280）、空 ImageURL（:281-285）、非 file:// 或带内嵌凭据（:286-292，含老版本程序留下的远程 URL）一律 dropFile 删除——损坏条目永远不会 brick 启动 replay。

**replay 的容错哲学**（driveReplayMount，main.cpp:190-323）：本地文件可能位于"比本服务更晚挂载的文件系统"上——注释 :146-156 钉版当初 stat 不存在就清状态是破坏性 bug（每次输掉 boot 竞态就永久抹掉合法挂载）；现改为 5 次尝试 × 5s 退避（常量 :176-177）+ 120×100ms 轮询 FSM 落定（:181-182），仍失败**保留** descriptor 等下次 boot（:320-322）；仅 AllowedLocalMountPoints 拒绝（每次必失败）才清（:293-305）。

## 6. 深潜三：系统设施与凭据安全三件套

**NBD/udev 设施**（system.hpp）：NBDDevice（:61-189）RAII 管 /dev/nbd*——udev 就绪探测、断连、sysfs 属性；DeviceMonitor（:199-362）把 libudev monitor 挂上 boost.asio 流描述符异步等 uevent，NBD 尺寸/变更回调给 App（main.cpp:55-60 再派发到各槽位状态机的 emitUdevStateChangeEvent，state_machine.hpp:1420-1430）。三组 udev 裸句柄由空 deleter 结构转 unique_ptr RAII（udevDeleter/monitorDeleter/deviceDeleter）。

**SMB 挂载**（smb.hpp）：mount 组装 `sec=ntlmsspi,seal,vers=3.0,cache=none` 固定参数（smb.hpp:24），凭据以 `username=...,password=...` 进选项串（:58-59）——前置 hasInjectionChar 检查拒绝 `\0/,/\n/\r` 注入字符（:29-39），mount 后立即 `utils::secureCleanup(options)` 擦除含密串（:67-68）；无凭据走 guest（:44-45）。unmount 是 `::umount` + `fs::remove_all`（smb.hpp:105、:112）。**勘误**：图谱摘要写 umount2，源码是 umount。

**凭据安全三件套**（utils.hpp）：

1. `secureCleanup` 模板（:161-170）——核心是 glibc `explicit_bzero`（:169），编译器无法把它优化掉，保证内存中不留残影；
2. `Credentials`（:172-203）RAII 持有 user/pass，析构即双 bzero（:180-184），拷贝删除（:197-199）；`CredentialsProvider`（:205-255）pack(formatter) 把凭据按调用方格式（mount.cifs/netrc）填进 SecureBuffer（unique_ptr+自擦除 Deleter :208-222）；
3. `VolatileFile`（:317-415）把凭据文件写临时盘给子进程用——mkstemp 原子建 0600 文件防 TOCTOU（:353-364），**析构先用 '*' 覆写全部字节再 remove**（:328-345）。

配套防线：`hasEmbeddedUrlCredentials` 限制只在 authority 段找 '@'（utils.hpp:136-151），`hasUrlQueryOrFragment` 把 `?token=...` 预签名 URL 当凭据材料对待（:156-159）——与持久化的 isPersistableUrl 联手实现设计文档 G3"不落盘任何秘密"。

## 7. 新人路线图与避坑

**阅读路线**：docs/persistent-mount.md（设计意图）→ persistence.hpp 345 行（独立可读）→ state_machine.hpp 的 BasicState/BasicEvent 骨架（:46-253）+ MountEvent/UnmountEvent（:622-685）→ main.cpp 的 App + replay 协程 → 按需下设施层。

**勘误与陷阱清单**（全部源码实证）：

1. **根 README 是 GitLab 模板**，架构真相在 docs/persistent-mount.md:1-10（含 Status/Source 表）。
2. **六状态真名**是 InitialState/ReadyState/ActivatingState/WaitingForGadgetState/ActiveState/WaitingForProcessEndState（state_machine.hpp:84-209）——图谱 tour 的 Invalid/Detached/Busy 等名不存在于源码。
3. **配置打不开 = 服务退出**（configuration.hpp:74-79 + main.cpp:375-379），不是"警告继续"。
4. **smb 卸载用 ::umount 非 umount2**（smb.hpp:105）。
5. **测试是 26 个用例非 29**（grep -c "^TEST"=26：6 个 URL 谓词 TEST :35-100 + 20 个 PersistenceFsTest TEST_F :174-383）。
6. **logger 是 7 个 tag 非 6 个空结构**：Struct/Debug/Info/Warning/Error/Critical 各带 constexpr value+name（logger.hpp:11-45，多出的 Struct 假级别 value=6 被 LOG_LEVEL=Debug :6 编译期滤掉）；LogMsg 宏 :91-93 经 constexpr if 分发（:76-81）。
7. **StateDirectory 人工同步契约**：service :10-14 注释要求与 persistence.hpp:56-57 的 defaultStateDir 保持一致，改一处必须改另一处。
8. tree-sitter 提取器对嵌套 struct/TEST 宏的盲区（六状态六事件嵌套类型、26 个 TEST/TEST_F 函数体）是图谱已知补偿点，引用图谱时注意这类节点的手工来源。
