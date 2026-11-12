# 01 · src/state_machine.hpp — MountPointStateMachine：variant 状态机的六态六事件全景

> 源码：`src/state_machine.hpp`（1467 行，全仓最大文件）· 图谱定位：5 层第 2 层「状态机与持久化核心层」· fanOut=36 全仓第一 · 每个挂载点一个实例，App 只是装配者（src/main.cpp:48-53）

## 一、角色定位：整个服务的业务中枢

VirtualMedia 的一切业务——D-Bus 接口注册、三种镜像源的挂载、NBD 子进程（curl/nbd-server）管理、USB gadget 配置与拆除、udev 设备变更响应、持久化时机——全部收敛在这一个头文件的单个类 `MountPointStateMachine`（state_machine.hpp:27）。它不是被谁调用的库，而是**自驱动的 actor**：外部只管投递事件（emitRegisterDBusEvent state_machine.hpp:1394、emitMountEvent state_machine.hpp:1400、emitUdevStateChangeEvent state_machine.hpp:1420），转移表决定其余一切。

选型动机：传统继承式状态模式（每个状态一个多态类 + 状态机持指针）在 C++ 里要处理所有权与回退，这里用 `std::variant` + 事件仿函数 `std::visit` 的组合——状态是值类型（拷贝即快照），转移是纯函数（返回新 State），编译器强制你写全六种状态的处理分支（少写一个不编译）。

## 二、内部结构：六状态、六事件、一张显式转移表

**六状态**（全部嵌套 struct，state_machine.hpp:84-205）：InitialState（state_machine.hpp:84，起点）→ ReadyState（state_machine.hpp:92，空闲；onEnter 卸载残留 SMB 目录并复位 target，state_machine.hpp:105-117；带 optional\<Error\> 记录上次失败 state_machine.hpp:119）→ ActivatingState（state_machine.hpp:122，激活中；onEnter 复位 exitCode/authFailure/certFailure 三标志并自驱 ActivationStarted，state_machine.hpp:128-136）→ WaitingForGadgetState（state_machine.hpp:139，等 USB gadget）→ ActiveState（state_machine.hpp:148，挂载成功，持 process weak_ptr）→ WaitingForProcessEndState（state_machine.hpp:192，等子进程退场）。`using State = std::variant<...六者>`（state_machine.hpp:207-209）。基类 BasicState（state_machine.hpp:46-82）只带 machine 引用 + stateName，构造即打 Debug 日志（state_machine.hpp:55-57）。

**六事件**（BasicEvent 基类 state_machine.hpp:211-253）：基类对六种状态各声明一个 `virtual State operator()(const XState&)`，默认全部走 transitionError 打 Critical 日志后原状态返回（state_machine.hpp:216-251）——任何事件×状态的"未定义组合"天然有声，不会静默吞掉。六个派生事件只覆写自己有语义的分支：

| 事件 | 行号 | 关键转移 |
|---|---|---|
| RegisterDbusEvent | state_machine.hpp:255 | InitialState 上建 Process/MountPoint/Service 三类 D-Bus 接口（Legacy 与 Proxy 路径不同） |
| MountEvent | state_machine.hpp:622 | 仅 ReadyState→ActivatingState（state_machine.hpp:627-630）；其余状态抛 InvalidStateError("Could not mount on not empty slot")（state_machine.hpp:632-635） |
| UnmountEvent | state_machine.hpp:638 | 四态四路：Activating 清存返 Ready（state_machine.hpp:648-650）；WaitingForGadget 停进程（state_machine.hpp:652-657）；Active 拆 gadget+清存+停进程+发 RESOURCE_DELETED（state_machine.hpp:660-676）；末两态幂等 no-op（state_machine.hpp:677-685） |
| SubprocessStoppedEvent | state_machine.hpp:686 | 子进程退出码驱动回退 ReadyState |
| ActivationStartedEvent | state_machine.hpp:732 | 全文件最大单元（约 475 行）：按 https/smb/file 三源起子进程、写 configfs gadget、迁 ActiveState |
| UdevStateChangeEvent | state_machine.hpp:1207 | NBD 尺寸/就绪变更，ActiveState 上同步 D-Bus 属性（mediaType 判定 state_machine.hpp:1320-1334） |

**分发核心** emitEvent（state_machine.hpp:1382-1392）：先 visit 取当前 stateName 打日志（state_machine.hpp:1384-1386），`state = std::visit(event, state)` 完成转移（state_machine.hpp:1388），再 visit 调新状态的 onEnter（state_machine.hpp:1389）。十行不到，就是"转移 + 进态副作用"两拍。

## 三、外部连接：谁投事件、它调谁

上行投递者三路：App 构造时逐槽位 emitRegisterDBusEvent（main.cpp:48-53）；D-Bus 方法（Mount/Unmount/EjectMedia）由 RegisterDbusEvent 注册的接口回调转成事件；DeviceMonitor 的 udev 回调经 App 广播给所有机器（main.cpp:55-60 → emitUdevStateChangeEvent state_machine.hpp:1420-1430）。下行依赖：persistence.hpp 的 writeState/clearState（hook #2 state_machine.hpp:183-185、hook #3 state_machine.hpp:648/:653/:664）、smb.hpp 的 SmbShare::unmount（state_machine.hpp:112）、system.hpp 的 NBDDevice 与 stopProcess、utils.hpp 的凭据与 URL 谓词。旁路：phosphor-logging 的 Redfish 事件上报（state_machine.hpp:672-675）与 sdbusplus 对象服务器。头文件依赖全收在 state_machine.hpp:3-8 的七个本地 include。

## 四、数据流：一次 Mount 的完整轨迹

ReadyState 收到 MountEvent（state_machine.hpp:627）→ ActivatingState::onEnter 复位三标志（state_machine.hpp:131-133）→ 自驱 ActivationStartedEvent（state_machine.hpp:135）→ 大事件内按 Target（state_machine.hpp:1432-1439，镜像 URL/rw/挂载目录/CredentialsProvider 四元载荷）分源起子进程、等 gadget（或直接）→ ActiveState::onEnter 触发**持久化 hook #2**（state_machine.hpp:157-186）：槽位 opt-in 且 file:// 才 writeState。卸载走 UnmountEvent 的 ActiveState 分支（state_machine.hpp:660-676）：removeUsbGadget（state_machine.hpp:1336-1348，从 configfs 摘 function 与符号链接，失败只记日志不阻断）失败则带 device_or_resource_busy 退回、成功则 clearState + stopProcess + 发 Redfish RESOURCE_DELETED → WaitingForProcessEndState 等子进程收尸 → SubprocessStoppedEvent 终回 ReadyState。任何非法组合（如 ReadyState 再收 MountEvent 之外的怪事件）由基类默认分支 Critical 报警。

## 五、设计决策：四个值得偷师的取舍

1. **值语义状态**：variant 状态可拷贝可快照，排障时把 State dump 出来就是完整现场；对比指针式状态模式省掉全部生命周期管理。
2. **默认全报错的转移表**：BasicEvent 的六个默认 operator()（state_machine.hpp:222-251）把"忘了处理某组合"从运行时静默 bug 变成 Critical 日志——状态机健壮性的廉价保险。
3. **事件即对象、onEnter 即副作用容器**：转移（operator() 返回新状态）与进态动作（onEnter）分离，hook #2 这种"每次进 Active 都执行"的逻辑有唯一挂点（state_machine.hpp:155）。
4. **持久化故意不挂在崩溃路径**：hook #3 注释钉版 SubprocessStoppedEvent 不清状态（state_machine.hpp:644-647）——崩溃留下的 descriptor 正是启动 replay 的输入；把"清"限定在显式 Unmount 是数据保全与状态准确性的折中。

## 六、新人提示

- 读码顺序：BasicState 家族（state_machine.hpp:46-209）→ BasicEvent 基类默认分支（state_machine.hpp:211-253）→ MountEvent/UnmountEvent 两个小事件（state_machine.hpp:622-685）体感转移表 → 再啃 475 行的 ActivationStartedEvent（state_machine.hpp:732-1206）。
- 嵌套 struct 是 tree-sitter 盲区：图谱里六状态六事件节点是手工补的，命名以源码为准（图谱 tour 曾把状态名写错成 Invalid/Detached/Busy）。
- InvalidStateError（state_machine.hpp:29-33）是唯一自定义异常；捕获它意味着"事件投错了状态"，App 的 replay 协程据此判断槽位是否可重试（main.cpp:251-258）。
- 改状态机先改转移表再改 onEnter；给新事件起名照 `XxxEvent` 惯例并接一个 `emitXxxEvent` 包装（如 state_machine.hpp:1394-1398 范式），外部只见 emit 不见事件构造。
- 验证练习：把 MountEvent 在 ReadyState 的返回改成 WaitingForGadgetState（state_machine.hpp:627-630），跑 BUILD_TESTS=ON 的测试套并手玩一次挂载，观察 onEnter 链——十分钟即可建立对两拍节奏的直觉。
