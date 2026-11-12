# sandbox-local/src/index.ts — LocalSandboxProvider：本地沙箱的 Provider 端

> 原文件：[`packages/sandbox/sandbox-local/src/index.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/sandbox/sandbox-local/src/index.ts)（567 行）

## 角色定位

`LocalSandboxProvider` 是沙箱能力缝在**本机 Provider 端**的实现：它不发明沙箱技术，而是把四种平台级隔离机制组织成一个可探测、可选择的 runner 链——Linux 上 bubblewrap（bwrap）、Linux 备选 Landlock、macOS 的 Seatbelt（sandbox-exec）、Windows 的 ACL restricted token。`confine` 接口按策略把一条普通命令产出为受限命令（改写后的 argv + 环境约束 + 授权），并管理 ACL 授予与临时目录的完整生命周期。

它是 tool-bash 那条 Consumer 链的对面：模型说"跑这条命令"，tool-bash 说"以这个策略跑"，本文件说"那就在这台机器上用这个 runner 把它关起来跑"。

## 内部结构

**runner 链与探测**：构造/首次使用时对候选 runner 做**功能探测一次并缓存**——探测结果（内核支持、二进制存在、能否创建规则）决定链上真正可用的成员。Linux 上 bwrap 优先、Landlock 兜底；macOS 走 Seatbelt；Windows 走 ACL restricted token。探测一次的设计把启动成本摊平，且运行期不再重复探测。

**fail-closed 原则**：若策略要求的隔离在当前主机上**无法建立**（runner 缺失、内核不配合），`confine` 直接失败——**绝不回退到裸 argv 执行**。"沙箱不可用就别跑"是刻进控制流的承诺，不是文档里的愿望。

**confine 的产出**：受限命令 = 包裹后的 argv（前置 runner 程序与其参数）+ 环境约束 + 授权说明。请求/规范分离的仓库规则在这里同样生效：策略默认值的决策在显式 resolve 步骤完成。

**Windows 写授权的双 SID**：restricted token 下的写权限分两条 SID 管理——`workspaceWriteSid`：从**规范化后的工作区路径**派生，同工作区的 ACE（访问控制项）构建一次进缓存复用；`tempWriteSid`：**每会话随机生成**的私有临时目录 SID，会话 dispose 时撤销。工作区与 temp 因此互不越界，不同会话的 temp 互相不可见。

**临时目录生命周期**：私有 temp 随会话建立、随 dispose 销毁，与 SID 撤销同步。

**诚实记录 partial enforcement**：Windows 的 WRITE_RESTRICTED 机制保留 Everyone 读、NTFS 硬链接可别名——这些已知不完备处被如实记录（文档化而非假装安全），并以此解释为什么某些场景仍需上层策略补充。

## 外部连接

包内依赖 `profiles.ts`（策略→runner 参数的档案映射）。跨包：实现 `dsh-sandbox` 能力缝（Service Definition 在 `packages/sandbox/sandbox`——升级编排 API、路径助手、`SANDBOX_UNAVAILABLE`/`SandboxUnavailableError`）；被 tool-bash 经 `ctx.shell` 消费；Linux 链末端的 Landlock runner 调用 `native/landlock-run` 构建出的原生二进制（见下一篇）。图谱上本文件无入边（Provider 由 profile 组合挂载），出边即 profiles.ts。

能力缝的另一侧还提供升级编排：`packages/sandbox/sandbox` 的 `escalation.ts`（升级编排 API）与 `roots.ts`（根路径助手）定义"策略不够时要走的审批升格路径"；`SANDBOX_UNAVAILABLE`/`SandboxUnavailableError` 是"沙箱建不起来"的正式错误面——本 Provider 的 fail-closed 失败最终以它向上冒泡，交给 tool-bash 的升级审批接手。

## 数据流

初始化：探测各 runner（一次）→ 缓存能力矩阵。执行：confine(命令, 策略) → 按平台与能力选 runner → 策略经 profiles.ts 翻成 runner 参数（只读路径、读写路径、环境白名单）→ 产出包裹 argv；Windows 侧额外确保 workspace ACE（缓存复用）与本次会话的 temp SID 就绪 → 受限命令交给进程执行 → 退出码与输出原样回流（沙箱不解释结果）。收尾：会话 dispose → temp 目录删除、tempWriteSid 撤销；workspace ACE 留在缓存供同工作区复用。

## 设计决策

**fail-closed 优于可用性**：安全机制的失败模式必须是"拒绝执行"而不是"降级裸跑"。这个选择贯穿全文件：探测不出就失败、规则建不起来就失败、内核不强制就失败。

**链序即能力序**：更强的隔离（独立命名空间级的 bwrap）优先，内核内的 Landlock 兜底。选择逻辑集中在探测结果上，新增平台只需插入新 runner 与其探测。

**探测一次+缓存**：避免每条命令都付探测成本；代价是运行期外部长态变化（如突然装上 bwrap）不被感知——换取行为确定性，划算。

**双 SID 分权**：工作区写授权按路径派生（稳定、可复用），temp 授权按会话随机（隔离、可撤销）——两种需求两种键，不硬塞进一个 SID。

**诚实记录不完备**：把 WRITE_RESTRICTED 保留 Everyone、硬链接别名写进已知限制，是"partial enforcement 也要明说"的工程操守：安全边界文档化后才能被上层补偿。

## 新人提示

加新平台支持前，先读探测缓存的结构——你的 runner 要在能力矩阵里有名字、有探测函数，链选择逻辑会自然找到它。排查"命令没被包住"时查两处：策略 resolve 给出的 spec 是否真的要求了隔离（`'none'` 策略是合法值）；runner 链选择是否落到预期成员（探测缓存可打日志）。Windows 行为的钥匙在双 SID 注释：工作区 ACE 是缓存复用的，"删了重建不生效"多半是缓存命中；temp 的随机性则意味着跨会话共享临时文件本来就不该工作。最后记住本文件的世界观：它只回答"怎么关起来"，不回答"该不该跑"——后者在 tool-bash 的升级审批与策略解析里。读懂本文件后可以做一个验证练习：同一策略在有无 bwrap 的两台 Linux 上各跑一次，对比探测缓存选中的 runner 与生成的包裹 argv——你会看到"策略不变、实现可换"这句话变成看得见的行为；再顺手读一遍 profiles.ts 里策略到参数的映射表，新增一条只读路径的端到端链路就通了。
