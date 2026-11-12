# 02 · 安全与敏感命令线 — sysIface 闸、BIOS 密码、PAM bootstrap 与 metrics redact

## 一、角色定位

本仓四条安全线分布在四个文件：**注册期特权闸**（`Privilege::sysIface`，全仓 22 处）、**Grace BIOS 密码命令的通道+时窗双闸**（`Grace/src/ghoemcommands.cpp:1302` verifyBiosPasswordAccess）、**PAM 随机凭据 bootstrap**（`Grace/src/ghoemcommands.cpp:1679` pamUpdatePasswd）、**metrics 日志的敏感载荷 redact**（`src/nvidia-metrics-logging.cpp:218` isSecretBearingCommand）。它们共同回答一个问题：一台 BMC 上，谁能拿到/写下真实秘密。历史脉络写在 commit 1266083——"Set/Get BIOS Password (3Ch/36h/37h) 未查通道与主机启动状态"是本仓近年最重要的安全修复。

## 二、内部结构

**1) sysIface 特权闸。** `ipmi::registerHandler(..., ipmi::Privilege::sysIface, ...)` 把命令钉死在带内系统接口：LAN/远程用户无论多高权限都到不了。典型：BF TorSwitch Set 与 DPU 网络重供应（`src/BF/oemcommands.cpp:2921-2930`）、BF2 PowerCap Set（`src/BF/BF2/oemcommands.cpp:173`）、三平台 bootstrap 账户的 `registerGroupHandler`（DGX `src/oemcommands.cpp:4453-4455`、Grace `Grace/src/ghoemcommands.cpp:3106-3113`、BF `src/BF/oemcommands.cpp:2933-2940`）——bootstrap 返回明文用户名+密码，必须只有带内 BIOS 能取。

**2) BIOS 密码双闸（Grace 专属）。** `verifyBiosPasswordAccess`（`Grace/src/ghoemcommands.cpp:1302`）先查 `getChannelInfo` 判定系统接口，再查 `isCpuBootDone`（:1258）——新电源控制读 D-Bus 属性 `xyz.openbmc_project.State.Host ... CpuBootDone`（:143），旧电源控制回退探测文件 `/run/bmc-state/CPU_BOOT_DONE-I`（:147）；任一表示"主机已启动完"即拒 0xD5。命令本体 Set/Get（:1336/:1405）命令号 0x36/0x37（`Grace/include/ghoemcommands.hpp:70-71`），载荷是 salt+PBKDF2 哈希而非明文（迭代 1000、salt 32B、hash≤64B，`Grace/include/ghoemcommands.hpp:76-85`），落盘到 `/var/lib/bios-settings-manager/seedData`。

**3) PAM bootstrap。** `ipmiGetBootStrapAccount`（Grace :1751）在 CredentialBootstrap 开启时生成 16 字符随机用户名（`getRandomUserName` :1573，/dev/urandom 逐字节筛 alnum、首字符强制 alpha）与 16 字符四类字符集密码（`getRandomPassword` :1614，bitset 保证每类字符至少出现一次且相邻字符不连续）；经 D-Bus CreateUser（只授 redfish-hostiface 组、priv-admin）+ `pamUpdatePasswd`（:1679）——`pam_start("passwd")+pam_chauthtok` 走 PAM 对话（`pamFunctionConversation` :1522 只应答 PAM_PROMPT_ECHO_OFF）。BF3 路线不同：密码只存 RAM（`src/BF/oemcommands.cpp:1885` ipmiGetBootStrapAccountBFInternal，"Password is not saved in RAM" 即拒），BMC 重启即失。

**4) metrics redact。** `NvidiaMetricsLogging` 构造时 `ipmi::registerFilter(prioOemBase, ...)` 挂旁路（`src/nvidia-metrics-logging.cpp:154`），**永远返回 ccSuccess 不拦截**；`isSecretBearingCommand`（:218）只圈定 App NetFn 的 Set User Password（0x06/0x47），命中则载荷置空+`RequestDataMode::redact`（:240-246），随后 `metrics::submit`（:248）外发，其余命令全量 hex 进 4096B 记录（`src/nvidia-ipmi-metrics.cpp:167-181`）经非阻塞 UNIX 数据报 socket `/run/bmc-cmd-metrics.sock`（:24,:117）外发。

## 三、外部连接

- **PAM**：`/etc/pam.d/passwd` 栈（libpam 链接 `CMakeLists.txt:240`）；**OpenSSL**：PBKDF2（`PKCS5_PBKDF2_HMAC` 调用点 `Grace/src/ghoemcommands.cpp:1360,:1462`）；**phosphor 用户管理器**：CreateUser/Delete/用户存在性（isValidUserName :1700 查 ObjectMapper subtree）；**BIOS/UEFI 侧**：sysIface 命令的真实调用方（带内 KCS）。
- SBMR 发送命令限 medium 白名单（smbusV20/systemInterface/oem，`src/sbmr-bootprogress.cpp:51-59`）——错误日志写 "supported only in SSIF" 但判定实际宽于日志（勘误见 README）。

## 四、数据流

BIOS 每次启动早期经带内发 0x52/0x02（bootstrap）：metrics filter 先记录（载荷仅 1 字节开关值，不敏感）→ groupHandler 查 CredentialBootstrap → 生成凭据 → 异步 D-Bus CreateUser + PAM 改密 → **用户名+明文密码回给 BIOS**（响应体），随后 `setCredentialBootStrap`（`Grace/src/ghoemcommands.cpp:1495`）按 0xa5 语义关闸。BIOS 密码种子则反向：BIOS 把 PBKDF2(salt, pw, 1000) 写到 BMC，BMC 侧永不见明文——两个方向的设计哲学截然不同（一次性回显 vs 只存哈希）。

## 五、设计决策

- **三档防御梯度**：sysIface（注册期、零运行时开销）> 通道+时窗检查（handler 内、可演化）> redact（审计侧兜底）。新命令按此顺序选闸。
- **为什么 BIOS 密码不是 sysIface 而是 Admin+双闸**：注册期特权是静态的，时窗检查（CPU 未启动完）必须动态判定——历史的 1266083 修复选择在 handler 内补闸而非改注册特权，保留了同命令号多通道语义。
- **redact 名单极小的理由**：本仓 OEM 命令载荷不含明文口令（BIOS 密码传哈希、bootstrap 敏感在响应不在请求），唯一例外来自 IPMI 标准域的 Set User Password。
- **陷阱**：BF2/BF4/Spectre 的 sysIface 拒绝桩也用 `Privilege::sysIface` 注册（如 `src/BF/spectre/oemcommands.cpp:157`）——先特权后桩行为，语义仍是"带内专属（且本平台不支持）"。

## 六、新人提示

审查任何新增 OEM 命令的安全属性时走四问：载荷有无秘密？→ 需不需要 sysIface？→ 通道/时窗检查放 handler 还是注册期？→ metrics 侧要不要进 redact 名单（`src/nvidia-metrics-logging.cpp:218`）？改 Grace BIOS 密码线必须同时读 commit 1266083 的根因分析；验证双闸可用 `ipmitool raw 0x3C 0x36` 分别在带内/带外、开机前后各打一次观察 0xD5。

---
字数 3674（非空白字符）/锚 26（唯一行号锚：全路径 18+上下文 8）
