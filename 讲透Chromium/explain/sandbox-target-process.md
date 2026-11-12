# 精讲 target_process.cc —— Windows 沙箱的受监禁进程容器

> `sandbox/win/src/target_process.cc`（281 行）＋`target_process.h`（75 行）
> 图谱：沙箱层 Windows 侧核心，8 节点（1 file＋7 function），15 条 imports 边＋1 条 calls 边（`Init`→`SharedMemIPCServer::Init`）；16 步导览收尾步代表文件

## 一、角色定位

`TargetProcess` 是 broker（监管者）手里那间"囚室"的抽象：目标进程的句柄、PID、IPC 共享内存与 broker 侧 IPC 服务器封装在一个类里（`target_process.h:64-69`）。头文件钉死所有权——"Objects of this class are owned by the Policy used to create them"（`target_process.h:22-23`）：每个 `PolicyBase` 拥有一个 `TargetProcess`，生命周期严格嵌套。

它是沙箱四组件（target/policy/broker/policy_engine）的枢纽：站在 broker 一侧，干的却是"向 target 内部搬运基础设施"——把策略字节码、IPC 通道、委托数据写进还挂在半空中的目标进程，然后才放它运行。两个构造——默认指向当前进程（`target_process.cc:75-77`）、接管外部句柄（`:79-85`）——主战场是后者：`InitProcess`（`sandbox_policy_base.cc:653`）接管刚挂起的子进程。

## 二、内部结构

281 行 7 函数，按职责四组：

**构造与析构**。构造（`:79-85`）：`CHECK(::DuplicateHandle(...))` 把调用方句柄复制一份自持（`:80-82`）并取 PID（`:84`）。析构（`:87-104`）防御三连：`WaitForSingleObject` 最多 50ms 给自然死亡机会（`:95`）；仍活则 `TerminateProcess(handle, 1)` 强杀（`:98`——IPC 服务器将亡，留活口只会卡死通道）；最后 `ipc_server_.reset()`（`:103`）——它引用进程句柄，必须先亡。

**跨进程写入原语 `TransferVariable`（`:106-122`）**：`WriteProcessMemory` 把 broker 本地缓冲写进 target 指定地址（`:113-114`），失败/短写报错 57。**主角 `Init`（`:126-245`，120 行）**：建共享内存→灌策略→起 IPC 服务器→传句柄，时序见第四节。

**终止与体检**。`Terminate()`（`:247-251`）一句 `TerminateProcess` 无等待，收尾交给 job 对象。`VerifySentinels()`（`:253-278`）用 `ReadProcessMemory` 回读 target 内两个哨兵 DWORD（`:260`/`:268`）与 `'SAND'`/`'BOXY'`（`:66`/`:73`）比对——不符即拒，机理见五节。

匿名命名空间的 `CopyPolicyToTarget`（`:43-61`）最精巧：`memcpy` 整个 `PolicyGlobal` 后，把 `kSandboxIpcCount`（`ipc_tags.h:34`）个 `entry[i]` 指针减去源缓冲基址 `source.data()`（`:51`）转成相对偏移写回（`:53-60`）——缘由见五节。

## 三、外部连接

图谱 15 条 imports 边，按方向三类：

**上游**：`PolicyBase::InitProcess`（`sandbox_policy_base.cc:643-732`）是唯一生产消费者——`Init` 全部参数（dispatcher/policy/线程池等）由它备齐经 `:689-691` 传入，之后还借 `TransferVariable` 追加三次延迟缓解注入；它由 `FinishSpawnTargetImpl` 触发（`broker_services.cc:631`）。

**下游（IPC 子系统）**：唯一 function 级 calls 边——`Init` 在 `:221-222` `make_unique<SharedMemIPCServer>`，`:224` 调其 `Init`（`sharedmem_ipc_server.cc:70`：头部重解释为协议控制块、每通道造 ping/pong 事件对复制进 target）。`depends_on` 边另指 `sharedmem_ipc_client.h`（target 侧对端）。

**对端镜像**：`SANDBOX_INTERCEPT`（`extern "C"` 宏，`sandbox_types.h:209`）修饰的 `g_shared_section`/`g_shared_IPC_size` 等全局在 target 侧有镜像定义（`sandbox_nt_util.cc:194-197`）；`MapGlobalMemory()`（`:202`）把 section 映进 target 并按 `[IPC｜策略｜委托数据]` 算子区基址（`:227-229`）。策略区由 `EvaluatePolicy` 消费：以 `g_shared_policy_memory` 为基址把 `entry[i]` 偏移加回还原成指针并做越界防御（`policy_target.cc:46-59`）。

## 四、数据流

一次完整孵化，`Init` 居时序中段：

**前奏（target 挂起中）**：`broker_services.cc` 主线 `SpawnTargetAsyncImpl`（`:568`）→`CreateTarget`（`:589`）→`CreateSandboxProcess`（`:265`）：`CreateProcessAsUserW` 以 lockdown 令牌建进程，flags 含 `CREATE_SUSPENDED`（`:275-276`）——**主线程零指令执行**；随即 `SetThreadToken` 换上权限稍宽的 impersonation 令牌（`:301`），否则 target 在 CRT 初始化早期就崩。之后 `FinishSpawnTargetImpl`（`:622`）→`InitProcess` 对冻结进程施加 job 限制/appshim/缓解/拦截/句柄关闭五连（`sandbox_policy_base.cc:662-685`）。

**正段（`Init`）**：① `VerifySentinels()`（`:133`）确认两侧布局一致；② 总尺寸 = IPC＋策略＋委托数据（`:143-149`），`CreateFileMappingW`＋`MapViewOfFile`（`:154`/`:162`）；③ 三区布局：IPC 留零、策略 `CopyPolicyToTarget`（`:172-177`）、委托数据 `memcpy`（`:180-184`），`CHECK_EQ` 收口（`:187`）；④ 三连 `TransferVariable` 写各区尺寸进 target 同名全局（`:192`/`:202`/`:213`）；⑤ 建 broker 侧 IPC 服务器（`:221-225`）；⑥ `DuplicateHandle` 把共享内存句柄复制进 target（`:227-234`）并写入其 `g_shared_section`（`:237-238`）。

**尾声（放行）**：`InitProcess` 收尾 `target_ = std::move(target)`（`sandbox_policy_base.cc:730`）、JobTracker 入完成端口（`broker_services.cc:644-648`）；最终 content 层 `CHECK(ResumeThread(...))`（`sandbox/policy/win/sandbox_win.cc:1025`）——主线程此刻才执行首条指令，醒来时令牌已降、拦截已布、策略就位；越权访问将撞上拦截器→CrossCall→broker 裁决链。

## 五、设计决策

**挂起两段式 vs Linux 一条路**。Windows 没有 Linux `fork()` 后 `execve()` 前的无副作用改造窗口，于是用 `CREATE_SUSPENDED`＋`ResumeThread` 人造一个：所有降权与拦截安装（`sandbox_policy_base.cc:662-691`）发生在 target 冻结期，杜绝"代码在跑而策略未就位"的竞态。对比 Linux 侧 prctl＋seccomp-bpf 在 exec 边界声明式过滤系统调用，Windows 走命令式改造（令牌/句柄表/注入代码），都在新逻辑启动前完成封锁。

**`VerifySentinels` 与"同名变量同地址"假设**。`TransferVariable` 的 `target_address` 取的是 **broker 进程内**该变量地址（`:192`）——赌的是两侧链接同一份 sandbox 代码、同名 `extern "C"` 变量同址。假设不总成立（ASLR、布局差异），故 `Init` 第一步先探测：target 里 `&g_sentinel_value_start` 处若不是 `'SAND'`，立即以错误码 66/67/68 拒绝（`sandbox_types.h:160-164`）——一次只读探测换取对全部跨进程写入的信心。

**指针重定位与单 section 合租**。`CopyPolicyToTarget` 不重建策略，只把 `entry[i]` 减源基址转偏移，target 侧再加回 `g_shared_policy_memory` 基址（`policy_target.cc:52-54`）——两进程映射地址不同，存偏移免重定位。三区共用一个 mapping（`:142-149`）、一次 `DuplicateHandle`（`:229`）带过去，把句柄传递次数（target 攻击面）压到最低。

## 六、新人提示

- **布局即协议**：`g_shared_*` 变量、`PolicyGlobal`（`policy_low_level.h:74-92`）、三区顺序 `[IPC｜policy｜delegate]`（`target_process.cc:169-184` 与 `sandbox_nt_util.cc:227-236` 须同步改）都是跨进程 ABI，漏改只在多进程测试暴露为 `NOTREACHED_NT`/哨兵 mismatch。
- **别在 `Init` 加耗时操作**：整条链发生在挂起期，直接加进启动关键路径（TRACE 事件为此埋点）。
- **`UNSAFE_TODO` 不是待办**：`:47`/`:54` 等处是 buffer-safety 重构的"已人审"标注，新代码应尽量用 span。
- **测试入口**：单元 `sbox_unittests`（`sandbox/win/BUILD.gn:280`）、端到端 `sbox_integration_tests`/`sbox_validation_tests`（`:184`/`:261`）；集成框架 `tests/common/controller.cc` 自做 spawn＋resume（`:323`）。设计文档在 `sandbox/win/docs/`。读码路线：本文件→`InitProcess`→broker spawn→target `MapGlobalMemory`→`EvaluatePolicy`。
