# render-process-host — RenderProcessHostImpl：浏览器侧的渲染进程宿主

文件：`content/browser/renderer_host/render_process_host_impl.cc`（6585 行）＋头文件

## 一、角色定位

头注释（L5-6）钉死职责："Represents the browser side of the browser <--> renderer communication channel."——每个 renderer 进程在 browser 侧对应一个 `RenderProcessHostImpl`，管生命周期（spawn→复用→死亡→清场）、IPC/mojo 通道（ChannelProxy＋Mojo invitation）、进程调度（优先级/内存/进程数）。

上层 `site_instance_impl.cc` 定进程策略，下层 `ChildProcessLauncher` fork/exec——本类是执行与宿主。内嵌四个进程分配辅助类（见下节），进程数与站点归属裁决就在本文件。

## 二、内部结构

**四个内嵌辅助类**（挂 BrowserContext UserData）：

- `SiteProcessMap`（L390）：SiteInfo→宿主映射，process-per-site 单宿主保证；`RegisterProcess`（L396）遇 race 保留旧条目。
- `RenderProcessHostIsReadyObserver`（L446）：等 `RenderProcessReady` 后投递挂起 task，销毁自删（L467）。
- `SiteProcessCountTracker`（L715）：按 site 计数进程需求（L731/L745 增减），供导航预热判断。
- `UnmatchedServiceWorkerProcessTracker`（L1044）：追踪为 ServiceWorker 起但无导航落入的进程，`MatchWithSite`（L1072）领走最新者。

**宿主关键方法**（按生命周期）：静态工厂 `CreateRenderProcessHost`（L1635，组装 guest/JIT/PDF/WebUI flags 后 `new` L1695）；构造（L1722）生成唯一 `id_`（L1746）、注册进 `ChildProcessSecurityPolicyImpl`（L1776）与全局 IDMap（L1779；`GetAllHosts` L348）、首调 `InitializeChannelProxy`（L1793），析构 L1863；`GetMaxRendererProcessCount`（L1522）桌面公式（L1576-1592）＝内存 MiB÷2（L1582）÷85MB/WebContents（64 位，L1576），clamp [3, 平台上限（L1503）]，Android（L1531）默认不限（L1549）；`Init`（L1913）启动、`ProcessDied`（L5732，`ResetIPC` L5822 防僵尸）、`Cleanup`（L4518）清场、`GetProcessHostForSiteInstance`（L5426）复用调度——见第四节；命令行组装传播 L3802/L3893，launch 回调 L6164/L6313；三档终止＝`Shutdown`（L4240 优雅）/`FastShutdownIfPossible`（L4261 绕过 unload）/`FastShutdown`（L5807 终杀）；匹配判据 `IsSuitableHost`（L4966）/`MayReuseAndIsSuitable`（L5169）＝BrowserContext/策略/StoragePartition 一致且未失响应；legacy IPC 面：`AddRoute`/`RemoveRoute`（L3244/L3259）路由注册、`ShutdownForBadMessage`（L3304，配合 L6428 `OnMojoError`）恶意消息 kill；`UpdateProcessPriority`（L6044，输入 L5987）合成 OS 级优先级；IO 线程版 `ChildProcessHost`＝`IOThreadHostImpl`（头文件 L1020，实现 L1467，`Ping` L1491）。

## 三、外部连接

图谱实证：13 节点（1 file＋4 class＋8 function）、116 条 outgoing imports 边。聚合：`content/browser` 30、`content/public` 23、base 系 13，零 blink/ 依赖。

关键上游：`site_instance_impl.h`（策略）、`child_process_launcher.h`（spawn）、`child_process_security_policy_impl.h`（安全锁）。反向：全仓 90 文件 include 本头，典型消费者 site_instance_impl/site_instance_group/embedded_worker_instance。public 只暴露抽象基类，embedder 不见 Impl（pimpl）。

## 四、数据流

**spawn 新 renderer**（Init 主线）：
1. 幂等闸（L1916 `IsInitializedAndNotDead`）→ 取 renderer 路径，失败早退。
2. `InitializeChannelProxy()`（L1995/L2244）：重置 `mojo_invitation_`，挂三根管——`ChildProcess` primordial 管道（L2254）、`ChildProcessHost` receiver（L2259）、legacy IPC bootstrap（L2264）；再 `IPC::ChannelProxy::Create` 建 legacy 通道（过渡化石，pause 路径 TODO(crbug.com/448511116) 待删 L2184）。
3. GPU 通道早发：L2004 `AttachMessagePipe(kGPUChannelAttachmentName)`，随 invitation 带 launch。
4. `RenderProcessWillLaunch`（L2038）→ `CreateMessageFilters`＋`RegisterMojoInterfaces`（L2049-2050）→ 先发 `InitializeRenderer`（L2070）。
5. 分叉：`run_renderer_in_process()`（L2077）走进程内线程；否则组装命令行（L2125）→ `ChildProcessLauncher`（L2161）异步 spawn，按需 pause 通道等 launch 后再 unpause，保证初始化先于导航 commit。
6. 成功 → `OnProcessLaunched`（L6164）：unpause、`SetClientPid`、发 `OnRenderProcessHostCreated`。

**进程复用决策**（`GetProcessHostForSiteInstance` L5426 瀑布）：
① `process_reuse_policy` switch（L5440）：kProcessPerSite 走 `GetSoleProcessHostForSite`（L5383）；子帧/worker 走 `FindReusableProcessHostForSiteInstance`（L6367）→ ② SW 未匹配进程领养（L5486 `MatchWithSite`）→ ③ 空进程复用 → ④ embedder 偏好（L5352 `GetExistingProcessHost`）→ ⑤ spare（L5516 `MaybeTakeSpare`）→ ⑥ 达上限（L5533/L5312）强制复用既有 → ⑦ 落空才造新（L5578）。防错闸：`MayReuseAndIsSuitable`（L5554）不满足即 `NOTREACHED`（L5560）。

**死亡与清场**：进程退出 → `ProcessDied`（L5732）→ `Cleanup`（L4518）决策树：单进程不清理；observer 重入置 delayed（L4534）；仍有活 listener/keep-alive（L4574）/shutdown delay（L4586）/worker（L4598）/pending reuse（L4610）ref 就只 `FastShutdown`（L4652）杀进程留宿主；全过则置 `deleting_soon_`（L4670）、广播 Destroyed、`DeleteSoon`（L4711）、`ResetIPC()`/`UnregisterHost`、断指针（L4715 起）。

## 五、设计决策

**进程池为何 browser 侧管？** 站点隔离安全模型：renderer 是不可信代码，"和谁共享进程"不容其参与判断。进程上限、site 锁（`SetProcessLock` L3640）等匹配必须可信侧裁决——`IsSuitableHost`（L4966）那串布尔判断就是安全边界的代码化。

**cleanup 为何是决策树而非直接析构？** 宿主被 observer/worker/keep-alive 多方引用，且回调可能重入（L4534 防 crbug.com/339504）。拆"杀进程"（可提前）与"删对象"（等引用归零）两段，中间 `DelayProcessShutdown`（L2695）挂起，保证 `RenderProcessHostDestroyed` 恒最后回调。

**上限公式为何这么土？** "内存÷2÷85MB"（L1576-1592）显式妥协（假设变更须同步 ThirtyFourTabs 基准）：防 OOM 护栏非预算，弹性靠 spare 与瀑布。

## 六、新人提示

- **行号时效**：基于 2026-10 快照，此文件高频改动，先 `grep -n` 重新锚定。
- **测试**：`render_process_host_unittest.cc` 单测＋`render_process_host_browsertest.cc`、`render_process_host_shutdown_delay_browsertest.cc`、`spare_render_process_host_manager_browsertest.cc` 全跑；站点隔离另跑 `site_per_process_browsertest.cc`。
- **改复用判据**必看 `ChildProcessSecurityPolicyImpl`（L1776 注册处建 site 锁），漏一条→跨 site 复用＝安全漏洞（L5560 NOTREACHED 是最后防线）。
- **坑**：①`Cleanup()` 置 `deleting_soon_`（L4670）后无 return，改前重读 L4645 起分支；②`--single-process` 无数分支短路，勿只测多进程；③`id_` 迁 `ChildProcessId` 进行时（L4421 `GetDeprecatedID`/L4425 `GetID` 并存）；④Android `#if` 分支多，桌面验证不了。
- **文档**：Site Isolation 官方文档（chromium.org/Home/chromium-security/site-isolation/）与 `site_instance_impl.cc` 注释是复用策略权威；`chrome://process-internals` 可直接观察复用瀑布产物。
