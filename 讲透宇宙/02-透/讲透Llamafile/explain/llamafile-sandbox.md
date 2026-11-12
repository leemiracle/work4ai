# llamafile/sandbox.c 精讲 — pledge/unveil 双沙箱安全模型

## 角色定位

sandbox.c（421 行）回答一个问题：**如何让用户放心运行来路不明的 GGUF 文件**。llamafile 分发的模型是任意第三方数据，解析即攻击面；沙箱在解析前落锁，默认拒绝出网、写盘、exec。它包装 Cosmopolitan Libc 两个原语：`pledge()`（系统调用白名单，Linux 上由 cosmo 用 SECCOMP BPF 模拟，无需特权）与 `unveil()`（文件系统路径围栏，Linux 用 Landlock LSM，内核 5.13+）。macOS/Windows 上两者皆 no-op，如实报告「未沙箱」而非假装安全。

## 内部结构

文件分四段：

1. **promise 速查与三条军规**（头注释）：stdio（已开 fd 读写+futex+线程，够 mmap 权重推理）、rpath（只读 open）、wpath/cpath（写/建文件）、inet/anet（anet 是关键创新：只许 accept 不许 connect——被攻破的 server 也拨不出外线）。军规一：过滤器只挂当前线程、仅其后新建线程继承——必须先沙箱后起 worker，还要冻结先存后台线程；军规二：GPU 驱动仍要碰 /dev 节点，GPU 模式整体跳过并明说；军规三：unveil 必须先于 pledge——锁规则集本身需要 Landlock 调用。违例返回 EPERM（温和 IO 错误）而非 OpenBSD 的 SIGABRT。

2. **策略门与安装**：`sandbox_skip_status` 统一裁决（--unsecure→UNSECURE、GPU→GPU、OS 不支持→UNSUPPORTED、否则 ACTIVE）；`llamafile_sandbox/promises/enter` 是 CLI/chat 入口链，`llamafile_sandbox_apply` 绕过策略门给单测。返回七态，describe 给人话、is_active 给布尔。

3. **server 专属**：`llamafile_sandbox_server_promises` 纯函数推导 promise 串（可单测）：默认 `stdio anet rpath`，needs_outbound（--rpc/工具/MCP 代理）放宽 inet，配置写目标（slot 保存/缓存）加 wpath cpath。`llamafile_sandbox_server` 主流程：算 has_rw → confine 且可治理则 unveil_apply（可执行文件自身 r——内嵌权重要重开自己；/etc/hosts、resolv.conf r；容器 r/rwc）→ unveil(0,0) 锁定 → 装 pledge。细节见功力：目录 unveiled 身、文件 unveiled 父目录（多分片 GGUF 兄弟顺带可见），但根下文件的父是 "/" 会暴露一切——特判用文件本身。

4. **可治理性探针**（unveil_is_governable）：fork 一次性子进程，选定金丝雀（/etc/os-release——世界可读、在一切规则之外）；锁定后验证：该可读的都能读（排除 virtiofs/9p/NFS 上 Landlock 过度拒绝）、金丝雀确实被拒（排除内核无 Landlock 时 cosmo 静默 no-op）。任一不满足按「未围栏」报告，宁可不承诺也不假承诺。

## 外部连接

消费方三处：main.cpp（--unsecure/--confine-reads）、chatbot_main.cpp（加载权重前 enter("stdio rpath wpath cpath tty")——保留写权为 /dump /push）、补丁版 server.cpp（启动早期、load_model 之前）。docs/security.md 是官方安全承诺文档，对照阅读；tests/sandbox_test.c 在 fork 子进程直接驱动各 promise 集。

## 数据流

```
server 启动（补丁注入，load_model 之前）
  ├─ sandbox_skip_status: --unsecure? GPU? OS支持? ──跳过并报告
  ├─ 推导 promises: "stdio [anet|inet] rpath [wpath cpath]"
  ├─ (confine?) fork探针: 应读全可读 && 金丝雀被拒?
  │     ├─ 是 ──▶ 真围栏，父进程再装一次
  │     └─ 否 ──▶ ACTIVE_UNCONFINED（如实降级）
  ├─ unveil_apply: exe自身r + hosts/resolv r + 容器r (+rw rwc)
  │     └─ unveil(0,0) 锁定
  └─ pledge(promises) ──▶ ACTIVE[_CONFINED]
此后: 违规syscall=EPERM，违规路径=ENOENT
```

## 设计决策

1. **默认安全、显式放宽**：CPU 模式默认落锁，--unsecure 才全关；unveil 反向——默认不围栏（server 按请求路径开多模态媒体文件，启动时锁死不现实），--confine-reads 才 opt-in。
2. **诚实降级**：GPU/旧内核/virtiofs 宁可报告「未保护」也不假装沙箱在场——探针验证 Landlock 真的「咬」，防安全剧场。
3. **anet 语义**：威胁模型是「权重或提示注入把进程变成肉鸡」，只禁 connect 就切断数据外传，且不影响正常服务。
4. **EPERM 惩罚模式**：违例以 IO 错误浮出而非崩溃，可诊断，也避免内核/驱动误触发团灭。

## 新人提示

- 改 server 沙箱先读头注释三条军规，违反军规一（线程时序）是最常见回归：pledge 前创建的后台线程游离在过滤器外。
- 新增需要新权限的功能要同时改 promises 推导与 unveil_apply，漏一边就是运行时 EPERM 且难排查——`--verbose` 会打印实际 promise 串。
- 探针子进程 _exit 而非 return，别顺手改掉导致锁死父进程规则集。
- macOS/Windows 上是 no-op，跨平台断言要条件化；Linux CI 内核版本决定 Landlock 可用性。
