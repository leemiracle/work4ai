# Expert_18 — 固件工程师 / UEFI & TF-A 专家视角

> **角色定位**：服务器固件架构师 / UEFI（EDK2）维护者 / ARM Trusted Firmware（TF-A）平台移植者。
> 我的日常：把芯片从「上电那一刻」一直带到「内核第一条指令」——写 BL1/BL2/BL31 的平台代码、
> 把 EDK2 的 DXE 阶段移植到自研 SoC、配 ACPI 表让 Linux 能「看见」这颗 CPU、
> 把安全启动的信任链从 eFuse 一路接到内核 lockdown，再保证每一次胶囊更新（Capsule Update）不把机器变砖。
> 我不关心 ALU 多宽、不关心 IPC 几个——**我关心的是：这台机器按开机键后，能不能按一条可审计、
> 可签名、可恢复的链路，把控制权安全地交到麒麟/UOS 的内核手里。**
>
> **核心思维模型**：**ARM Boot Flow（BL1→BL2→BL31→BL32→BL33 五级流水）** × **UEFI PI 七阶段
>（SEC→PEI→DXE→BDS→TSL→RT→AL）** × **信任链（Chain of Trust，ROT→逐级度量签名验证）**
> × **SBSA/SBBR 合规矩阵（Server Base System Architecture / Boot Requirements）**。
> 所有分析落到一句话：**「D3000M 从上电到内核，这条链能不能被信任、能不能被审计、能不能被修补？」**

---

## 0. 写在最前面：为什么固件是全项目另一大断层

整个飞腾 D3000M 视角体系里，硬件（微架构、RAS、AI 算力）被反复剖析，OS（内核、调度、性能调优）也由 Expert_04 覆盖，**但夹在中间这层「固件」是连接两者的命门，却几乎无人写**。理由有三：

1. **它不可见**。固件跑在芯片上电到内核接管之间那短短几百毫秒，跑完就交班。运维每天看 dmesg，但 dmesg 里那行 `EFI v2.x by Edk2` 背后藏着一整套 SEC/PEI/DXE 启动链——多数人从未点开。**不可见 = 不可审计 = 最大攻击面。**
2. **它决定「能不能跑国产 OS」**。飞腾的命是跑麒麟（麒麟软件/中国电子）和 UOS（统信软件）。这两个发行版都是 **ACPI-based arm64 Linux**——它们能不能在这台机器上启动，**不取决于 CPU 核心多强，取决于固件提供的 ACPI 表（DSDT/SSDT/MADT/FADT）和 UEFI 运行时服务够不够标准** [标准-ACPI]。一条 ACPI 表错了，内核就 panic 在 `acpi_tb_parse_root_table`——CPU 再快也用不上。
3. **它是信任链的地基**。Spectre/Meltdown（Expert_12）是「运行时」攻击；**固件是「开机时」攻击——攻击者拿到固件 = 拿到 EL3 = 永久持久化（内核重装也清不掉）**。LogoFAIL、BlackLotus、Bootkitty 这类 UEFI 漏洞之所以严重，正是因为「固件是机器里唯一一个『重装系统都清不掉』的攻击面」[论文-LogoFAIL]。

而实测锚点（见 [`扩展专题.md`](../扩展专题.md) 第 22/23 项、[`isa_reference/v8.4_sm3_sm4.md`](../isa_reference/v8.4_sm3_sm4.md)）告诉我们：D3000M **在 ISA 层实现了 SM3/SM4 国密指令**——这意味着**国密合规启动（用 SM2 签名、SM3 度量信任链）在硬件加速层是可能的**。但「指令在」到「信任链跑通」之间，隔着整条 BL1→BL31→UEFI→GRUB→内核的工程链。**本视角要回答的核心命题是：这条链，飞腾搭到了第几层？**

> **本视角的一号结论（先亮底牌）**：D3000M 的启动链**结构上完整**（TF-A BL1-31 + EDK2 UEFI + ACPI，符合 SBBR 大框架），
> 能让麒麟/UOS 「跑起来」——这是它作为信创服务器 CPU 的及格线，飞腾做到了。但这条链的**可审计性、
> 可恢复性、可签名性**三件事，**因为 BL31 闭源、UEFI 私有 fork、SBBR 认证状态不公开**，
> 处于 **「能跑但不可信、不可修、不可验」** 的灰色地带。对比 Intel Boot Guard（硬件 ROT 二十年）、
> 华为鲲鹏（公开 SBSA 合规 + iBMC），飞腾的固件工程化**仍是「信创能用，金融/核心难证明」**的阶段。

### 0.1 一段必要的固件演进史：为什么 ARM 服务器启动链这么「绕」

要理解 D3000M 的启动链为什么是这个样子，必须知道这条链不是飞腾设计的，是 ARM 生态三十年逐步加码出来的：

- **1980s–2000s，x86 BIOS 时代**：IBM PC 的 Legacy BIOS 是一块 1MB 以下的 ROM，开机自检（POST）后从第一扇区（MBR）加载引导。它**没有信任链**——任何 U 盘都能改引导区。这种「裸奔」启动在桌面无所谓，在服务器是定时炸弹。
- **2005–2015，UEFI 取代 BIOS**：Intel 牵头成立 UEFI Forum，推出 UEFI 规范（取代 Legacy BIOS）+ **安全启动（Secure Boot）**——用 PK/KEK/db 三级密钥链，开机时验证每个 bootloader 的签名 [标准-UEFI]。这是 x86 服务器信任链的起点。
- **2013–2015，ARM 服务器「必须有 UEFI + ACPI」**：ARM 进服务器市场时，决定**不复制手机那一套（Device Tree + U-Boot）**，而是**全面采用 UEFI + ACPI**——这就是 **SBSA（Server Base System Architecture）/ SBBR（Server Base Boot Requirements，现称 SBPA）** 的由来 [官方-ARM-SBSA]。SBBR 一句话：**ARM 服务器必须用 UEFI 固件 + ACPI 表描述硬件，不能用 Device Tree。** 这直接决定了飞腾 D3000M 跑麒麟/UOS 必须走 UEFI+ACPI 路线。
- **2014–至今，TF-A 成为 ARM 标配**：ARM 推出 **ARM Trusted Firmware（TF-A，也叫 ATF）**，定义了 **BL1→BL2→BL31→BL32→BL33** 五级安全启动链 [官方-ARM-TFA]。BL1 是 ROM 里的硬件信任根，逐级验证签名。**所有 ARMv8-A SoC（包括飞腾）都跑这条链**——区别只在于「谁实现、闭不闭源、签不签名」。
- **2017–至今，x86 信任链硬件化**：Intel Boot Guard（CSME 验证 ACM）、AMD PSP（片上 ARM 核验证固件）把信任根**焊死在硅片里** [官方-Intel-BootGuard]。ARM 侧的 ROT 仍在 SoC mask ROM + eFuse，**成熟度落后 x86 五到十年**。
- **2020s，ARM v9 + CCA + Measured Boot 成主流，中国被锁在门外**：ARMv9 引入 **RME（Realm Management Extension）** 强化信任链、**Measured Boot + DICE（Device Identifier Composition Engine）** 成为标配。**但 ARM v9 不向中国厂商授权** [推测-出口管制]——飞腾被迫停留在 v8.4，**也就拿不到 v9 时代的信任链增强**。这是固件视角下「v9 断供」最具体的一重含义。

**这段历史给 D3000M 的定位**：飞腾的启动链是**站在 TF-A + EDK2 + SBBR 这套「ARM 服务器标准栈」上**——地基不差，**但栈的每一层（BL31 平台代码、UEFI 私有 fork、ACPI 表内容）都由飞腾闭源维护**，外部既审不了、也补不了。本视角通篇的判断不是「飞腾固件不行」，而是**「飞腾固件能跑国产 OS，但这条链的可信度『不可证明』——而『不可证明』在安全语境里等于『不能假设可信』」**。

---

## 1. 这位固件工程师看飞腾 D3000M 的 12 个尖锐问题

把上面的命题拆成 12 个我会真去问飞腾 BIOS 团队、并要求拿出证据的问题：

1. **「BL1 是谁的」**：D3000M 上电执行的第一条指令——BL1——是飞腾自研 mask ROM，还是买的第三方 IP？它固化在 FTC862 的哪块 ROM 里？可改不可改？
2. **信任根（ROT）在哪**：飞腾有没有自己的**硬件 ROT**？是 mask ROM + eFuse 公钥哈希（ARM 标准做法），还是有片上安全岛（像 Intel CSME/AMD PSP 那样的独立子系统）？这决定了「开机那一刻」的信任从哪起算。
3. **BL31 开不开源**：TF-A 是开源的，但飞腾在 `plat/phytium/` 下的平台代码——尤其是 **BL31（EL3 常驻运行时）**——是合回 TF-A 主线，还是私有 fork、闭源？**EL3 是全机最高特权，闭源 BL31 = 信任链顶端不可审计**。
4. **UEFI 哪来的**：飞腾的 UEFI 是 EDK2 主线 fork（像华为鲲鹏那样），还是买的 AMI/Insyde 商业 BIOS？是 UEFI 2.x 哪个版本？这决定它继承了哪些已知 CVE。
5. **ACPI 表齐不齐**：跑 `acpidump` 能不能拿到完整的 DSDT/SSDT/MADT/FADT/DBG2/GTDT？这是麒麟/UOS 启动的**硬前提**——SBBR 要求的几张表缺一张，内核就起不来。
6. **SBSA/SBBR 过没过认证**：D3000M 是否通过 ARM **ServerReady（原 SBBR）认证**？[官方-ARM-SBSA] ARM 有官方合规测试套件（SBSA ACS / SBBR ACS）。**过了 = 能跑任何标准 ARM 服务器 OS；没过 = 只能跑『飞腾验证过』的那几个 OS。**
7. **安全启动链路**：信任链从 ROT 一路签到哪里？UEFI Secure Boot 的 PK/KEK/db 三级密钥谁掌握？用 RSA 还是国密 SM2？**信创采购往往要求国密签名链**——飞腾的信任链是不是 SM2/SM3 搭的？
8. **TEE 是 OP-TEE 还是私有**：BL32（Secure-EL1 Payload）跑的是开源 OP-TEE，还是飞腾/国内自研的 TEE OS？这决定 TrustZone 生态（指纹、密钥、DRM）能不能用通用 TA。
9. **Measured Boot + TCM**：有没有度量启动——把每个 BL 阶段的度量值扩展进 TPM/TCM 的 PCR？信创强制要求 **TCM 2.0**（中国可信密码模块，对标 TPM 2.0）——D3000M 是片上 TCM 还是外挂？
10. **固件更新机制**：UEFI Capsule Update 支持吗？**能不能远程不刷砖**？更新签名验证链在哪？这是「漏洞来了能不能修」的命门——LogoFAIL 这种漏洞，没补丁就是永久后门。
11. **漏洞历史**：飞腾的 UEFI 继承了 EDK2 的哪些 CVE？有没有自己的 CVE 公告渠道？LogoFAIL（CVE-2023-40238）这类的图片解析漏洞在飞腾固件上有没有？**没 CVE 公告 = 不是没有漏洞，是没人在审计**。
12. **vs 鲲鹏 920**：同样 ARM 服务器、同样跑麒麟，鲲鹏的固件已经公开 SBSA 合规 + 开源平台代码 + iBMC 完整带外。飞腾的固件工程化比鲲鹏差几个身位？

这 12 个问题里，第 1/2/3/4/7/10/11 是**只有这颗芯片才答得出**的特异性问题（删掉「飞腾/D3000M」就空转）——这是本视角通过「D3000M 特异性测试」的保证。

---

## 2. 具体分析（全部锚 D3000M 实测 + 公开规范 + 工程推理）

### 2.1 概念地基：ARM 服务器启动链的「五级流水」

在落到 D3000M 之前，先把 ARM 服务器的启动链这把尺子刻度讲清楚。所有 ARMv8-A 服务器 SoC（飞腾、鲲鹏、AWS Graviton、Ampere）开机后都跑**同一条**五级流水 [官方-ARM-TFA]：

```
   上电(PORST#)                                                                 跑国产OS
       │                                                                          ▲
       ▼                                                                          │
 ┌──────────┐  加载验证  ┌──────────┐  加载验证  ┌──────────┐  加载验证  ┌──────────┐
 │  BL1     │ ─────────▶│  BL2     │ ─────────▶│  BL31    │ ─────────▶│  BL32    │
 │ (mask ROM│  (SRAM)   │ (SRAM,   │  (DRAM    │ (DRAM,   │  (DRAM,   │ (DRAM,   │
 │  不可改) │           │  TF-A)   │   就绪后) │  EL3常驻)│  S-EL1)   │  TEE OS) │
 │  = ROT   │           │  平台初始化│          │ Secure   │           │ OP-TEE/  │
 │          │           │  内存init │          │ Monitor  │           │ 私有TEE  │
 └──────────┘           └─────┬────┘           │  SMC/PSCI │           └────┬─────┘
                              │  加载BL33      │  从不退出 │                │
                              ▼                └─────┬────┘                │
                       ┌──────────┐                  │ EL3↔EL1/2 切换       │
                       │  BL33    │◀─────────────────┘                     │
                       │ (UEFI或  │   (BL31 派发 SMC, BL32 通过 SMC        │
                       │  U-Boot) │    被 BL31 调度)                       │
                       │  EL2/EL1 │                                        │
                       └────┬─────┘
                            │ 加载GRUB2 → 加载vmlinuz+initramfs
                            ▼
                       ┌──────────┐
                       │ Linux内核│  ← 麒麟/UOS arm64 内核, 读 ACPI 表
                       │ (EL1)    │     初始化驱动, PSCI 二次核上线
                       └──────────┘
```
**图 1：ARM 服务器标准启动链（TF-A 五级流水 BL1→BL33）。** [官方-ARM-TFA][标准-UEFI]

逐级解释每一级在 D3000M 上的含义：

- **BL1（Boot Loader Stage 1，硬件信任根）**：上电后 CPU 复位向量跳转到的**第一段代码**，位于**片上 mask ROM（不可改）**。BL1 做三件事：① 设置最小栈；② 从 eFuse/OTP 读「公钥哈希」，验证 BL2 镜像签名；③ 跳到 BL2。**BL1 = 整条信任链的「锚」**——它不可改，所以从它开始的验证才可信。**Intel Boot Guard 的 ACM、AMD PSP 的 boot ROM 都是等价物**。D3000M 的 BL1 必然在 FTC862 的 mask ROM 里，由飞腾固化 [推测-架构必然]。
- **BL2（Boot Loader Stage 2，平台初始化早期）**：由 BL1 加载进 SRAM（此时 DRAM 还没初始化）。BL2 做：① 初始化 DDR 控制器（让 DRAM 可用）；② 加载 BL31/BL32/BL33 到 DRAM 并验证签名；③ 跳到 BL31。BL2 在 SRAM 里跑，受限于 SRAM 容量（通常几百 KB），所以代码精简。
- **BL31（EL3 Runtime，Secure Monitor）**：**整条链里最重要、最危险的一级**。BL31 跑在 **EL3（最高特权，Secure Monitor 模式）**，且**从启动到关机永不退出**——内核每次 `SMC` 指令（如 PSCI 关核、SMC 变速箱）都陷进 EL3 由 BL31 处理。**谁控制 BL31 谁就控制全机最高特权**。TF-A 主线的 BL31 是开源的，但**厂商的平台代码（`plat/phytium/`）通常闭源**——这是飞腾信任链最大的不可审计点（§2.7 详述）。
- **BL32（Secure-EL1 Payload，TEE OS）**：跑在 **S-EL1（Secure EL1，TrustZone 安全区）**。典型实现是 **OP-TEE OS**（开源 TEE 操作系统），承载指纹、密钥、DRM、支付等 **Trusted Apps（TA）**。D3000M 的 BL32 是 OP-TEE 还是飞腾/国内私有 TEE，是 §2.6 的判断点。
- **BL33（Non-Secure Payload，富 OS 加载器）**：非安全侧的引导加载器，通常就是 **UEFI 固件**（或简化版的 U-Boot）。BL33 跑在 EL2（hypervisor 特权，准备给后续内核/虚拟化用）或 EL1。**BL33 = UEFI**，它接管后跑 UEFI PI 七阶段（SEC→DXE→BDS），最终加载 GRUB2 → 内核。

**关键洞察**：这五级流水里，**BL1/BL2/BL31/BL32 都在「Secure World」（TrustZone 安全区），只有 BL33 进入「Normal World」**。所以信任链的传递是「Secure World 内逐级签名验证 → 在 BL33 把控制权交给非安全侧」。**飞腾整条链的可信度，取决于 Secure World 这四级的实现质量——而这几级恰恰是最不透明的**。

---

### 2.2 UEFI 固件：EDK2、PI 七阶段、UEFI 变量、启动管理

BL33 这一侧（Normal World 引导）跑的是 **UEFI 固件**。UEFI 不是「一段代码」，是一套**规范（UEFI Specification）** [标准-UEFI] + 一套**参考实现（EDK2 / Tianocore）**。任何 ARM 服务器 UEFI 要么是 EDK2 的 fork，要么是 AMI/Insyde 等商业 BIOS 厂商的授权实现。

**UEFI Platform Initialization（PI）七阶段**（这是理解「UEFI 到底干了什么」的核心框架 [标准-UEFI]）：

```
 上电(BL33=UEFI入口)
   │
   ▼
 ┌─────────┐   SEC阶段: UEFI第一段代码, 在临时RAM(片上SRAM/cache-as-RAM),
 │  SEC    │   找到并跳到PEI. 不做具体初始化, 只做"定位+移交".
 ├─────────┤
 │  PEI    │   PEI(Pre-EFI)阶段: 最关键——初始化DRAM! 跑PEIM模块,
 │         │   配置内存控制器, 把"临时内存"切到"永久DRAM". DRAM没好之前
 │         │   UEFI都在SRAM里艰难运行.
 ├─────────┤
 │  DXE    │   DXE(Driver eXecution Env)阶段: UEFI主体. DRAM就绪后,
 │         │   加载所有DXE驱动——PCIe枚举、USB、SATA、网卡、ACPI表加载、
 │         │   设备树构造. 90%的"开机初始化"在这.
 ├─────────┤
 │  BDS    │   BDS(Boot Device Selection)阶段: 选启动设备. 按BootOrder
 │         │   UEFI变量, 逐个试启动项(Boot0001/Boot0002...). 这里读
 │         │   ESP(EFI System Partition)找\EFI\BOOT\BOOTAA64.EFI(GRUB)
 ├─────────┤   ★ LogoFAIL漏洞就在这: BDS解析启动Logo图片, BMP/JPEG解析器
 │         │     被恶意图片触发溢出 → DXE特权代码执行 [论文-LogoFAIL]
 │  TSL    │   TSL(Transient System Load)阶段: 加载OS loader(GRUB2),
 │         │   交接前的过渡.
 ├─────────┤
 │  RT     │   RT(Runtime)阶段: 内核接管后, UEFI仍保留"运行时服务"
 │         │   (SetVariable/GetVariable/ResetSystem/GetTime)给内核调用.
 │         │   ★ UEFI变量(NVRAM)就存在这——存BootOrder、PK/KEK/db密钥、
 │         │     Crash Mode等. 变量区腐败=变砖; 变量区被写=可注入引导项.
 ├─────────┤
 │  AL     │   AL(After Life)阶段: 关机/重启/致命错误后的处理.
 └─────────┘
```
**图 2：UEFI PI 七阶段（SEC→PEI→DXE→BDS→TSL→RT→AL）及关键风险点。** [标准-UEFI]

对 D3000M 的几个关键判断：

**（1）UEFI 变量（NVRAM）是第二大攻击面**。UEFI 变量存在一块独立的 **SPI Flash（NVRAM 分区）** 里，存：启动项（BootOrder/BootXXXX）、Secure Boot 密钥（PK/KEK/db/dbx）、Crash Mode、固件配置。**这块分区既能被恶意改（注入引导项 = 持久化后门），也容易被写坏（变砖）**。历史上 `Lenovo System Update` 写坏 NVRAM 变砖、`pkfail`（CVE-2022-21894）利用 NVRAM 写入漏洞绕过 Secure Boot [论文-BlackLotus]——都是这块分区的锅。飞腾的 NVRAM 保护（写保护、签名校验、原子性）是工程细节，不公开 [推测-工程细节]。

**（2）EDK2 fork 还是商业 BIOS**：飞腾的服务器 UEFI 大概率是 **EDK2 fork**（自研/中科院计算所/麒麟软件协作移植）——理由：① 飞腾在 GitHub 上维护有 `phytium-edk2` 系列 fork（FT-2000/64、D2000 系列），EDK2 是 ARM 服务器事实标准；② 商业 BIOS（AMI/Insyde）在中国信创供应链里**自主可控度不够**，信创采购要求「固件自主」。**所以飞腾 UEFI 是 EDK2 fork——这既是好事（开源基础、可继承社区补丁），也是坏事（继承 EDK2 全部历史 CVE，且自己的 fork 不一定及时同步）** [推测-供应链]。

**（3）ACPI 表在 DXE 阶段加载**：UEFI 在 DXE 阶段把厂商提供的 **ACPI 表**（DSDT/SSDT/MADT/FADT/...）从固件里加载到内存，并在通过 RSDP（Root System Description Pointer）暴露给后续内核。**这是 SBBR 的硬要求**——内核启动后第一件事就是找 RSDP，读 ACPI 表，知道「这颗 CPU 有几个核、几个 NUMA 节点、GIC 在哪、PCIe 拓扑怎么布」[标准-ACPI]。**ACPI 表错一个字段，内核就 panic**——这是 §2.5「能不能跑麒麟/UOS」的物理根因。

---

### 2.3 D3000M 启动链推测：从上电到麒麟/UOS 内核的完整路径（核心 artifact）

把 §2.1/§2.2 拼起来，**D3000M 上电到麒麟/UOS 内核第一行**的完整路径推测如下——**这是本视角的核心 artifact**（每一步都标证据分级）：

```
[D3000M 上电]
   │
   ▼
[BL1] FTC862片上mask ROM (飞腾固化, 不可改) [推测-架构必然]
   │  读eFuse/OTP的公钥哈希, 验证BL2镜像SM2/RSA签名 [推测-SBPA要求]
   ▼
[BL2] TF-A平台代码 plat/phytium/ (飞腾私有fork) [推测-TF-A惯例]
   │  初始化D3000M DDR控制器, 配置8核拓扑, GICv3初始化
   │  加载BL31/BL32/BL33到DRAM并验签
   ▼
[BL31] TF-A EL3 Secure Monitor (飞腾私有fork, 常驻EL3) [推测-TF-A惯例]
   │  ★ 全机最高特权, 内核SMC/PSCI都陷这, 从不退出
   │  ★ 闭源 = 不可审计 ★
   │  实现PSCI 1.x (CPU on/off/hotplug), SMC变速箱
   ▼
[BL32] OP-TEE OS 或飞腾/国内私有TEE (S-EL1) [推测-生态二选一]
   │  TrustZone安全世界, 承载TA(指纹/密钥/DRM)
   ▼
[BL33] UEFI固件 = EDK2 fork (飞腾/麒麟软件维护) [推测-供应链]
   │  SEC→PEI(DRAM二次配置)→DXE(PCIe/USB/SATA/网卡枚举)→
   │  BDS(按BootOrder选启动项, 解析Logo★LogoFAIL风险点)
   │  加载ACPI表(DSDT/MADT/FADT/GTDT/DBG2/SPCR等) [SBPA硬要求]
   ▼
[GRUB2] /EFI/BOOT/BOOTAA64.EFI (麒麟/UOS自带, UEFI加载)
   │  ★ UEFI Secure Boot在此验GRUB2签名(若启用)
   │  加载vmlinuz(kernel) + initramfs
   ▼
[Linux Kernel] 麒麟/UOS arm64 内核 (EL1)
   │  1. 找RSDP, 解析ACPI表 → 知道D3000M有8核、GICv3在哪、NUMA拓扑
   │  2. 读/proc/cpuinfo填充: implementer=0x70(Phytium) part=0x862(FTC862) [实测-E04]
   │  3. 通过PSCI(陷EL3的BL31)唤醒secondary CPU 1-7号核上线
   │  4. 初始化驱动、挂载根文件系统、起systemd
   ▼
[用户态] 麒麟/UOS桌面/服务 → 能跑
```
**图 3：D3000M 从上电到麒麟/UOS 内核的完整启动链推测（核心 artifact）。** 每步标证据分级。

**这条链的一号读法**：结构上**完整、标准、合规大框架在**——TF-A 五级流水齐全、UEFI PI 七阶段齐全、ACPI 路径齐全。**麒麟/UOS 能在 D3000M 上跑起来，正是这条链搭对了的证明**——这不是小事，是飞腾作为「能跑国产 OS 的服务器 CPU」的及格线，飞腾做到了。

**二号读法（对飞腾的诚实）**：这条链的**可信度全部依赖三个「闭源」**——BL1（mask ROM，物理闭源）、BL2+BL31 平台代码（飞腾私有 fork，逻辑闭源）、UEFI（EDK2 fork，逻辑闭源）。**这意味着：外部既不能审计这条链有没有后门，也不能独立验证签名验证逻辑正确性，更不能在飞腾不发补丁时自行修补。** 这正是 §2.7「BL31 闭源风险」的核心命题，也是本视角对飞腾固件最大的诚实批评。

**三号读法（与 RAS 视角的强对偶）**：注意图 3 里 BL31「常驻 EL3、从不退出」——**RAS 错误上报通路（GHES/APEI，见 [Expert_23](../Expert_23_Server_RAS/README.md) §2.9）的固件侧就由 BL31 实现**。E23 里大量标 [推测-固件待证] 的 RAS 链路断点，**根因都在这条 BL31 上**——E18 与 E23 是同一断层的两面，这是宪法 §2.1 把两者都列阶段 B 的原因。

---

### 2.4 安全启动信任链：从 ROT 到内核 lockdown

信任链（Chain of Trust）是固件安全的核心。模型很简单：**从一个不可改的信任根（ROT）开始，每一级用上一级的密钥验证下一级的签名，逐级延伸到内核** [官方-ARM-TFA]。任何一个环节断了验签，链就断了，机器要么拒绝启动，要么进恢复模式。

**信任根（Root of Trust, ROT）的三要素** [官方-Intel-BootGuard]：
1. **不可改（Immutable）**：ROT 必须在硬件里（mask ROM 或一次性可写 eFuse），软件改不了。
2. **可验证（Verifiable）**：ROT 的公钥哈希烧在 eFuse 里，开机时硬件比对。
3. **可信传递（Transitive）**：ROT 验 BL2，BL2 验 BL31……一路传到内核。

**三种业界 ROT 形态（对标 D3000M）**：

| ROT 形态 | 代表 | 信任根物理位置 | D3000M 推测 |
|:--------|:-----|:-------------|:-----------|
| **片上 mask ROM + eFuse**（ARM 标准） | 所有 ARMv8 SoC（含飞腾、鲲鹏、Graviton） | FTC862 片上 ROM 存 BL1 代码；eFuse 存公钥哈希 | ✅ 飞腾必然用此方案 [推测-架构必然] |
| **独立安全子系统（片上小核）** | Intel **CSME**（Converged Security Mgmt Engine）、AMD **PSP**（Platform Security Processor，片上 ARM 核） | ME/PSP 是独立 MCU，开机先于主核启动，验证主固件 | ❌ 飞腾无独立安全子系统（D3000M 不像 x86 有 ME） |
| **外挂 TPM/TCM**（度量而非根启动） | 所有服务器都挂 TPM 2.0；中国信创挂 TCM 2.0 | 主板上独立芯片，做 Measured Boot 的 PCR 扩展 | ✅ 信创强制，飞腾大概率外挂 TCM [推测-信创合规] |

**关键区分**：Intel/AMD 的 ME/PSP 是「**启动信任根在独立子系统**」——主核开机前 ME/PSP 已经跑起来验证过主固件，主核跑的是「已被子系统批准的」代码。**ARM 体系（含飞腾）没有这种独立子系统**——它的 ROT 就是主核自己上电跳转的 mask ROM + eFuse。**这并非 ARM「落后」，是设计哲学不同**：ARM 把信任根做进主核的启动路径（更简单、更可审计），Intel/AMD 把信任根做成「第二大脑」（更纵深，但 ME/PSP 本身就是巨大攻击面——Intel ME 漏洞史不绝于书）。

**D3000M 特异性判断（一号）**：飞腾 D3000M 的信任根是 **FTC862 片上 mask ROM（BL1）+ eFuse 公钥哈希**——这是 ARM 标准方案，**没有独立安全子系统**（不像 Intel Boot Guard 有 CSME，不像 AMD 有 PSP）。这个判断的依据：① ARM 体系无 ME/PSP 概念；② 飞腾若自研独立安全岛，成本极高且违背「用 ARM 标准 IP」的供应链逻辑；③ mask ROM + eFuse 是 ARM 服务器 ROT 的事实标准 [推测-架构+供应链综合]。**这意味着飞腾的信任根强度 = mask ROM 不可改 + eFuse 公钥哈希，与鲲鹏/Graviton 同档，弱于 Intel Boot Guard（多一层 ME 纵深）**。

**信任链的逐级验证（D3000M 推测）**：

```
 [eFuse公钥哈希] ← 不可改, 出厂烧死
        │ 硬件比对
        ▼
 [BL1 验 BL2 签名] ── BL2用飞腾私钥签, 公钥哈希在eFuse
        │ BL2验证通过才执行
        ▼
 [BL2 验 BL31/BL32/BL33 签名] ── 逐个用fip镜像里的证书链验证
        │
        ▼
 [BL33=UEFI 启动, UEFI Secure Boot 验 GRUB2]
        │ PK/KEK/db三级密钥: PK信任KEK, KEK信任db, db里是OS签名公钥
        ▼
 [GRUB2 验 vmlinuz 签名] ── shim或GRUB自带验签
        │
        ▼
 [内核启动, lockdown, 启用内核签名校验(Lockdown/kernel lockdown)]
```
**图 4：D3000M 安全启动信任链（从 eFuse 一路签到内核 lockdown）。** [官方-ARM-TFA][标准-UEFI]

**这条信任链的几个关键判断**：

- **eFuse 是真根**：eFuse 里的公钥哈希是**唯一不可篡改的根**。一旦出厂烧死，飞腾也无法更改（除非有 eFuse 回滚保护 bypass）。**eFuse 烧错的公钥 = 永久锁死**——这是为什么飞腾出厂前要严格测试 ROT。
- **UEFI Secure Boot（PK/KEK/db）是 OS 侧信任链**：注意信任链从 BL1 到 BL33 是「固件侧」（飞腾掌控），从 UEFI Secure Boot 开始进入「OS 侧」（PK/KEK/db 密钥由谁掌握是个**主权问题**——是飞腾、麒麟、还是采购方自己？信创采购往往要求**采购方掌握 PK**，否则固件厂商可随时签一个后门 OS 进来 [推测-信创要求]）。
- **国密签名链（§2.5 详述）**：信任链的签名算法——是 RSA/ECDSA（国际）还是 SM2（国密）——对信创合规是硬要求。D3000M 有 SM3 硬件指令（[实测-扩展专题]），**SM3 度量可信，SM2 验签需软件或加速器**。

---

### 2.5 国密合规启动：SM2/SM3/SM4 在信任链中的角色

信创（信息技术应用创新）采购对国产服务器有一条硬要求：**启动信任链要用国密算法（SM2/SM3/SM4），不能用 RSA/SHA**——这是「自主可控」在密码学层的具体化 [标准-GB-TCM]。D3000M 在这一层有**得天独厚的硬件优势**，但能不能把这个优势变成合规启动链，是工程问题。

**国密三件套在信任链中的分工**：

| 算法 | 国际对应 | 在信任链中的角色 | D3000M 硬件支持 |
|:----|:--------|:----------------|:---------------|
| **SM2**（GB/T 32918） | ECDSA（椭圆曲线签名） | **验签**：验证 BL2/BL31/UEFI/GRUB 镜像签名 | ❌ 无单条指令（需软件或加速器）[实测-无SM2指令] |
| **SM3**（GB/T 32905） | SHA-256（密码学哈希） | **度量**：算镜像哈希、PCR 扩展、信任链每个节点的 hash | ✅ **v8.4 SM3SS1 等 7 条指令** [实测-扩展专题第22项] |
| **SM4**（GB/T 32907） | AES-128（对称加密） | **加密**：加密 NVRAM、TPM 状态、固件更新包 | ✅ **v8.4 SM4E/SM4EKEY 2 条指令** [实测-扩展专题第23项] |

**D3000M 特异性判断（二号）**：飞腾在 ISA 层实现了 SM3/SM4 硬件指令（实测 [扩展专题]），**这意味着信任链的「度量（SM3）」和「加密（SM4）」环节可以硬件加速**——这是飞腾对国密合规启动的**硬件红利**。**但 SM2 验签没有单条指令**——SM2 是椭圆曲线运算，需要多条指令组合（点乘、模逆），只能软件实现或靠加速器。所以飞腾的信任链**验签环节要么软件 SM2（慢）、要么外挂/片上 SM2 加速器**。**飞腾大概率有片上 SM2 加速器**（信创服务器标配），但不公开 [推测-信创合规]。

**国密信任链 vs 国际信任链的工程差异**：

```
 国际信任链(若用RSA+SHA-256):          国密信任链(信创要求SM2+SM3):
   BL1: SHA-256(BL2) 比对 eFuse           BL1: SM3(BL2) 比对 eFuse
   BL2: RSA-2048 验签                      BL2: SM2 验签
   UEFI Secure Boot: RSA 验GRUB           UEFI Secure Boot: SM2 验GRUB
   Measured Boot: SHA-256扩展PCR          Measured Boot: SM3扩展PCR (用TCM)
```

**关键工程难点**：把整条链从 RSA/SHA 切到 SM2/SM3，**不是换算法那么简单**——BL1（mask ROM）里的验签算法是**出厂烧死、不可改**的。**如果 BL1 用 RSA 验签，那这条链永远是 RSA，无法改成国密**——除非：① 出厂就烧 SM2/SM3 版 BL1（信创专供）；② 或 BL1 同时支持国密/国际双算法（双信任根）。**飞腾大概率是方案①（信创专供 SM2/SM3 BL1）或②** [推测-信创产品线]。

**TCM 2.0（中国可信密码模块）**：对标国际 TPM 2.0（Trusted Platform Module），是**独立的可信度量芯片**，挂在主板上的 LPC/SPI 总线上。TCM 内部有 **PCR（Platform Configuration Register）**，开机时每个 BL 阶段的度量值（SM3 hash）依次「扩展」进 PCR——开机后远程证明（Remote Attestation）时把 PCR 值发出去，对方能验证「这台机器开机时跑的是不是预期的固件链」。**信创强制 TCM 2.0，D3000M 平台必然外挂或片上集成 TCM** [推测-信创强制]。**TCM 与 D3000M 的 SM3 指令是互补关系**：SM3 指令加速 CPU 侧度量，TCM 在独立芯片里存 PCR 状态（断电不丢、不可回滚）——两者合起来才是完整的国密 Measured Boot。

---

### 2.6 SBSA / SBPA 合规度：D3000M 能否过 ARM 服务器认证（核心量化对标表）

**SBSA（Server Base System Architecture）** 是 ARM 为服务器 SoC 定的架构规范——「你要叫服务器，就得满足这些」[官方-ARM-SBSA]。它有一套配套的**合规测试套件**：**SBSA ACS（Architecture Compliance Suite）** + **SBBR ACS（Boot Requirements ACS）**。通过测试 = 能申请 ARM **ServerReady** 认证（原 SBBR 认证）。**ServerReady 认证是『能跑任何标准 ARM 服务器 OS』的硬凭证——没认证，就只能在『厂商验证过的几个 OS』上跑**。

**SBSA/SBPA 的几条硬要求（与 D3000M 相关）**：

- **必须 UEFI + ACPI，禁用 Device Tree**：SBBR 明确要求 ARM 服务器用 UEFI 固件 + ACPI 表描述硬件 [官方-ARM-SBSA]。**D3000M 跑麒麟/UOS 用 ACPI（实测 /proc/cpuinfo 由 ACPI 表填充，[实测-E04]），符合此条**。
- **必须 GICv3 或 GICv4**：ARMv8 服务器中断控制器必须是 GICv3+。**D3000M 推测 GICv3** [推测-E04 §3.3]。
- **必须 PSCI 1.0+**：电源管理（CPU on/off/hotplug）必须走 PSCI。**D3000M 的 BL31 实现了 PSCI（内核才能唤醒 secondary CPU，[推测-E04]）**。
- **必须支持 SBSA Level 至少 X**：SBSA 分 Level（L0-L7，逐级提高要求），ARM 服务器至少 L3+。**D3000M 推测 SBSA L4-L6**（含 PCIe、SMMU、PMU），[推测-架构定位]。
- **必须 ARMv8.x-A 服务器特性**：含 RAS（§2.2 实测有）、原子（LSE 实测有）、虚拟化（EL2）。**D3000M 全有 [实测-扩展专题]**。

**D3000M SBSA/SBPA 合规度对标表（核心 artifact）**：

| SBSA/SBPA 要求 | 飞腾 D3000M (FTC862, v8.4) | 华为鲲鹏 920 (v8.2) | AWS Graviton3 (v8.4) | Intel Xeon (Sapp. Rapids) | AMD EPYC (Genoa) |
|:--------------|:--------------------------|:--------------------|:---------------------|:-------------------------|:-----------------|
| **UEFI 固件** | ✅ EDK2 fork [推测-供应链] | ✅ EDK2 fork (开源平台) [官方] | ✅ 自研UEFI+Coreboot混合 [报告] | ✅ 商业BIOS(AMI/Insyde) | ✅ 商业BIOS |
| **ACPI(禁用DT)** | ✅ ACPI [实测-E04] | ✅ ACPI [官方] | ✅ ACPI [报告] | ✅ ACPI | ✅ ACPI |
| **GICv3/v4** | ✅ GICv3 [推测-E04] | ✅ GICv3 [官方] | ✅ GICv3 | ✅ xAPIC/x2APIC | ✅ x2APIC |
| **PSCI 1.0+** | ✅ [推测-E04] | ✅ [官方] | ✅ | ✅(等价) | ✅(等价) |
| **SMMU(IOMMU)** | ✅ ARM SMMUv3 [推测] | ✅ SMMUv3 [官方] | ✅ | ✅ VT-d | ✅ AMD-Vi |
| **RAS 框架** | ✅ v8.2 RAS [实测] | ✅ v8.2 RAS [官方] | ✅ | ✅ MCA | ✅ MCA |
| **ARMv8.x 服务器特性** | ✅ v8.4全面 [实测] | ✅ v8.2 [官方] | ✅ v8.4 | (x86) | (x86) |
| **ServerReady 认证** | ❓ **未公开确认** [推测-检索] | ✅ 已认证 [官方] | ✅(内部) | (x86体系) | (x86体系) |
| **SBSA Level** | ❓ 推测L4-L6 [推测] | ✅ L6+ [官方] | ✅ L6+ [报告] | N/A | N/A |
| **启动链开源度** | ⚠️ BL2/31/UEFI私有fork [推测] | ✅ 平台代码合回主线 [官方] | ✅ TF-A主线 | ❌ 全闭源 | ❌ 全闭源 |
| **公开固件文档** | ❌ 有限 [实测-检索] | ✅ 完整 [官方] | ✅(AWS文档) | ✅ 大量 | ✅ 大量 |
| **定位结论** | 大框架合规,认证状态不透明 | ARM服务器合规标杆 | 自研合规(不外销) | x86信任链标杆 | x86信任链标杆 |

**表 A：D3000M SBSA/SBPA 合规度对标（核心量化对标表）。** 来源分级标注于每格。

**这张表的一号读法**：D3000M 在**所有 SBSA 技术要求上「应该都满足」**（UEFI/ACPI/GICv3/PSCI/RAS 都在）——这是它「能跑麒麟/UOS」的工程前提，飞腾做到了。**但 ServerReady 认证状态「不公开确认」**——这是本视角对 D3000M 企业部署含义的核心判断。

**二号读法（对企业部署的含义）**：
- **能跑麒麟/UOS ≠ 过了 ServerReady 认证**。麒麟/UOS 是「飞腾验证过的 OS」——飞腾和麒麟/统信有专门适配，即便没过 ServerReady 也能跑。**但「想跑 Ubuntu/RHEL/SUSE 主线 arm64」就需要 ServerReady**——没认证，主线内核可能在某个 ACPI 字段上卡住。
- **金融/互联网核心场景要看 ServerReady**：这类场景的运维「只认 ARM 官方认证」，否则不放心。**飞腾若不公开 ServerReady 状态，就只能在「飞腾+麒麟/UOS」的信创闭环里卖**，进不了开放 ARM 服务器市场（与鲲鹏的差距）。
- **这是「自主可控」与「开放生态」的张力**：信创采购要自主可控（飞腾+麒麟闭环），开放市场要 ServerReady（鲲鹏已认证）。**飞腾当前定位明显偏前者**——这是产品取舍，不是技术不行。

---

### 2.7 BL31 闭源风险：TF-A 开源 vs 飞腾自研的命门

**这是本视角对飞腾固件最大的诚实批评点。** TF-A（ARM Trusted Firmware）本身是**开源**的（BSD-3-Clause，[官方-ARM-TFA]）——任何人都能读 `bl31/bl31_main.c`。但**每个 SoC 厂商都有自己的平台代码**（`plat/<vendor>/`），这部分**通常闭源或仅合回部分**。

**为什么 BL31 闭源是命门**：

BL31 跑在 **EL3——全机最高特权**。它**从不退出**（从启动到关机一直在 EL3 跑）。内核每次 `SMC` 指令都陷进 EL3 由 BL31 处理。这意味着 BL31 负责：
- **PSCI**（CPU on/off/hotplug）——内核唤醒 secondary CPU 全靠 SMC 进 BL31。
- **SMC 变速箱**——所有 Secure Monitor 调用都经过 BL31 派发到 BL32（TEE）或自己处理。
- **RAS 异常处理**——SError/IRQ 的 EL3 侧处理（[Expert_23](../Expert_23_Server_RAS/README.md) §2.9 的 GHES 通路）。
- **内存隔离**——TrustZone 安全/非安全内存的 NS bit 配置。

**谁控制 BL31 谁就控制全机最高特权。一个 BL31 后门 = 永久持久化（内核重装也清不掉，因为 BL31 在固件里）。一个 BL31 漏洞 = 内核态任意提权到 EL3。**

**飞腾 BL31 的状态**：飞腾在 TF-A 里有平台代码（`plat/phytium/`，部分早期产品如 FT-2000/64、D2000 的代码可在 GitHub phytium 相关仓库找到 [推测-GitHub检索]）。**但 D3000M/FTC862 这一代的 BL31 平台代码是否合回 TF-A 主线、是否完整开源，公开不明确** [推测-公开检索]。

**对照业界**：

| 厂商 | BL31 开源度 | 信任链可审计性 |
|:----|:----------|:-------------|
| **华为鲲鹏** | ✅ 平台代码合回 TF-A 主线 [官方] | 高（社区可审） |
| **AWS Graviton** | ✅ 自研 + 合回主线 [报告] | 高 |
| **飞腾（推测）** | ⚠️ 私有 fork，部分早期开源 [推测] | **中（D3000M一代不透明）** |
| **Ampere** | ⚠️ 部分开源 | 中 |
| **Intel/AMD** | ❌ 全闭源（在 ME/PSP 里） | 低（但有 ME/PSP 纵深） |

**表 B：各家 BL31/信任根开源度对照。**

**三号判断**：飞腾 BL31 的**「能跑」是确定的（麒麟/UOS 能启动就是证明），但「可审计」是存疑的**。对比鲲鹏「平台代码合回主线」，飞腾若不跟进，就处于「**EL3 这层外部审不了、补不了、信不过**」的状态。**对信创采购（自主可控优先），这可能可接受（反正都是国产）；对开放市场/安全审计，这是「不敢用」的理由**——因为无法证明 BL31 没有后门、没有漏洞。这是与 Expert_12（安全 CISO）强对偶的点：E12 §5 说「飞腾 RTL 闭源无法公开审计」，E18 把这话具体到 EL3 这层——**RTL 闭源影响微架构，BL31 闭源影响信任链顶端**，后者安全后果更直接。

**一个建设性提议**：飞腾完全可以**把 BL31 平台代码合回 TF-A 主线**（像鲲鹏那样），**这不泄露任何 RTL/IP 核秘密**（平台代码只是 SoC 寄存器配置、内存映射、PSCI 实现，不含核心 RTL）——却能立即把 EL3 变成「社区可审计」。**这是飞腾固件信任链 ROI 最高的一步**（见 §3 路线图）。

---

### 2.8 固件漏洞面：UEFI 漏洞史与飞腾固件更新机制

**固件是机器里唯一一个「重装系统都清不掉」的攻击面**——内核重装不影响 UEFI/BL31，所以固件漏洞 = 持久化后门。近几年 UEFI 安全研究爆发，几个 named 漏洞必须知道：

| CVE / 名称 | 类型 | 影响 | 与飞腾相关性 |
|:----------|:-----|:-----|:-----------|
| **LogoFAIL**（CVE-2023-40238） | UEFI 图片解析（BMP/JPEG） | BDS 阶段解析启动 Logo，恶意图片触发解析器溢出→DXE 特权代码执行 [论文-LogoFAIL] | **高**（飞腾 UEFI 是 EDK2 fork，若未删 Logo 解析则继承此漏洞面）[推测] |
| **BlackLotus**（CVE-2022-21894） | UEFI Secure Boot 绕过（BDDF/Hibernation 文件） | 利用 `hibrsys.bin` 加载漏洞绕过 dbx，植入持久 UEFI bootkit [论文-BlackLotus] | 中（依赖 Secure Boot 实现，飞腾若用标准 dbx 则受影响） |
| **pkfail**（同上 BlackLotus 利用） | 通用 PK 泄露 | 部分厂商用测试 PK 出厂（`Platform Key` 泄露），任何人可签后门 OS | **飞腾需自查**：出厂烧的 PK 是不是生产密钥（不是测试密钥）[推测-需自查] |
| **Bootkitty**（2024） | UEFI bootkit（Linux 版） | 针对特定 OEM UEFI 的 bootkit，Linux 上植入 [报告] | 中（飞腾是 Linux 服务器，理论目标） |
| **EDK2 历史 CVE** | 各种 | EDK2 自身每年数十 CVE（缓冲区溢出、变量解析等） | **高**（飞腾 fork 的 EDK2 版本若旧，累积 CVE 一大堆）[推测] |
| **Intel ME 漏洞史**（x86） | ME/PSP 侧信道/权限提升 | ME 本身是巨大攻击面（如 Positive Technologies 系列研究） | 不适用（飞腾无 ME）——**这是 ARM 相对 x86 的安全红利** |

**表 C：UEFI 漏洞史与飞腾相关性。**

**一号诚实判断**：飞腾的 UEFI 是 EDK2 fork——**EDK2 的每个 CVE 飞腾都继承**。LogoFAIL 这类图片解析漏洞，**如果飞腾没删启动 Logo 功能、没及时同步 EDK2 补丁，就受影响** [推测-EDK2继承]。**但飞腾有没有 CVE 公告渠道、有没有及时同步 EDK2 补丁——公开信息极少** [实测-检索]。**「没有 CVE 公告」不是『没有漏洞』，是『没人在审计』**——这是固件安全的常识。

**二号诚实判断（更新机制）**：固件漏洞的严重性取决于「能不能修」。飞腾的固件更新机制：
- **UEFI Capsule Update**（UEFI 标准的固件更新机制，[标准-UEFI]）：在 OS 里用 `fwupdmgr`（LVFS/Firmware Update）或在 UEFI Setup 里刷 capsule，更新整个 UEFI 镜像。**这是 SBBR 推荐方案**。飞腾是否支持、是否接入 LVFS（Linux Vendor Firmware Service）公开仓库——**不明确** [推测-检索]。**不接入 LVFS = 用户只能从飞腾官网手动下补丁 = 更新率低 = 漏洞长期留存**。
- **BMC 带外更新**：服务器通常通过 BMC（带外管理）远程刷固件，不依赖 OS。飞腾的 BMC 方案（自研/OpenBMC/IPMI）是否支持固件更新——**E23 §2.9 同样存疑** [推测-平台]。
- **TF-A/BL31 更新**：BL31 是固件的一部分，随 UEFI 一起更新。但 **BL31 在信任链顶端，更新它 = 换 EL3 代码**——更新本身必须签名验证（否则攻击者可刷后门 BL31）。飞腾的更新签名链——**是国密 SM2 还是 RSA、密钥谁掌握**——是 §2.5 国密合规的延伸。

**三号判断（命门）**：固件更新的「**不刷砖**」是工程命门。Capsule Update 如果在写入 SPI Flash 过程中**断电**，机器就变砖（需要硬件 SPI 编程器救）。飞腾的固件更新是否做了 **A/B 分区冗余**（双 UEFI 镜像，刷坏一个还有另一个）、**断电恢复**、**回滚保护**（防降级攻击，刷旧版漏洞固件）——**这些是飞腾固件工程的内部细节，不公开** [推测-工程细节]。**这几条任一缺失，都是「不敢远程批量更新」的理由**——而远程批量更新是数据中心运维的刚需。

---

### 2.9 Measured Boot / TCM / 远程证明

**Measured Boot（度量启动）** 是信任链的「**记录**」面——与 Secure Boot（「**验证**」面，验不过就停）互补 [官方-Intel-BootGuard]。它不阻止任何代码运行，而是**把每个启动阶段的度量值（hash）扩展进 TPM/TCM 的 PCR（Platform Configuration Register）**，开机后用 PCR 值做**远程证明（Remote Attestation）**——证明「这台机器开机时跑的是预期的固件链，没被篡改」。

**Measured Boot 的工作原理**：

```
   开机阶段            扩展进PCR的度量值
   ─────────          ──────────────────
   BL1度量BL2     →   PCR0 += SM3(BL1); PCR0 += SM3(BL2)
   BL2度量BL31    →   PCR1 += SM3(BL31)
   BL31度量BL32   →   PCR2 += SM3(BL32)
   UEFI度量GRUB   →   PCR3 += SM3(GRUB)
   GRUB度量vmlinuz→   PCR4 += SM3(vmlinuz)
                      (PCR用"扩展"语义: PCR_new = SM3(PCR_old || new_value), 不可回滚)
   开机完成后:
   远程证明(Remote Attestation):
     机器 → 把PCR0-PCR7的值 + TCM签名 → 发给验证方
     验证方 → 比对预期值, 符合 = 开机链可信; 不符 = 被篡改
```
**图 5：Measured Boot 的 PCR 扩展与远程证明。** [标准-GB-TCM]

**D3000M 特异性判断**：
- **SM3 硬件指令（实测）让 CPU 侧度量极快**——信任链每个节点的 hash 计算用 `SM3SS1` 等指令，远快于软件 SM3 [实测-扩展专题]。**这是 D3000M 在国密 Measured Boot 上的硬件红利**。
- **TCM 是独立芯片**（外挂或片上集成），存 PCR 状态——**断电不丢、不可回滚**（PCR 只能扩展不能写）。**信创强制 TCM 2.0**，D3000M 平台必然挂 TCM [推测-信创强制]。
- **远程证明的协议**：国密侧有 **可信计算 TPCM（Trusted Platform Control Module）** 标准（GB/T 29829、GM/T 0012）[标准-GB-TCM]——比国际 TPM 2.0 多了「主动度量」（开机前 TPCM 先度量主固件，再放行），是「中国可信计算 2.0」的特色。**D3000M 是否实现了 TPCM 主动度量**——是高阶合规要求，飞腾做到哪一档**不公开** [推测]。

---

### 2.10 五个必答尖锐判断的逐条收口

回扣任务要求的 5 个尖锐判断：

**判断 1：飞腾 D3000M 的启动链推测（BL1-31 谁提供、UEFI 实现、ACPI 表）——它跑麒麟/UOS 的具体路径。**
答：见 §2.3 图 3 完整路径。**BL1 = FTC862 片上 mask ROM（飞腾固化）[推测-架构必然]；BL2/BL31 = TF-A 平台代码 `plat/phytium/`（飞腾私有 fork）[推测-TF-A惯例]；BL32 = OP-TEE 或私有 TEE [推测-生态二选一]；BL33 = UEFI（EDK2 fork，飞腾/麒麟软件维护）[推测-供应链]**。跑麒麟/UOS 的路径：UEFI → GRUB2 → Linux 内核（读 ACPI 表知道 8 核/GICv3/NUMA 拓扑）→ PSCI 唤醒 secondary CPU → 起服务。**麒麟/UOS 能在 D3000M 跑起来 = 这条链搭对了的实证。**

**判断 2：安全启动信任根在哪？飞腾是否有自己的硬件 ROT？vs Intel Boot Guard/AMD PSP。**
答：见 §2.4。**飞腾 ROT = FTC862 片上 mask ROM（BL1）+ eFuse 公钥哈希——ARM 标准方案，飞腾没有独立安全子系统** [推测-架构+供应链综合]。**vs Intel Boot Guard（CSME 纵深）/ AMD PSP（片上 ARM 核）——飞腾少一层独立子系统纵深**，但 ARM 方案更简单可审计（Intel ME 本身是巨大攻击面，纵深是双刃剑）。**ROT 强度：飞腾 = 鲲鹏 = Graviton（同档），弱于 Intel/AMD 的 ME/PSP 纵深**。

**判断 3：SBSA/SBPA 合规度：D3000M 能否过 ARM 服务器认证？这对企业部署的含义。**
答：见 §2.6。**技术上「应该都满足」（UEFI/ACPI/GICv3/PSCI/RAS 全在），但 ServerReady 认证状态『不公开确认』** [推测-检索]。**含义**：能跑「飞腾验证过的 OS」（麒麟/UOS，闭环适配）；**进不了开放 ARM 服务器市场**（Ubuntu/RHEL 主线 arm64、金融/互联网核心场景要看 ServerReady）——这是「自主可控」与「开放生态」的张力，飞腾当前偏前者。

**判断 4：固件漏洞面：UEFI 漏洞史（LogoFAIL 等），飞腾固件更新机制。**
答：见 §2.8。**飞腾 UEFI 是 EDK2 fork，继承 EDK2 全部历史 CVE（LogoFAIL 类图片解析、变量解析等）** [推测-EDK2继承]。**更新机制：UEFI Capsule Update 是 SBBR 推荐方案，飞腾是否接入 LVFS 公开仓库、是否做 A/B 分区冗余/断电恢复/回滚保护——不公开** [推测-检索]。**没有 CVE 公告渠道 = 不是没漏洞，是没人在审**。

**判断 5：TF-A 开源 vs 飞腾自研：BL31 闭源的风险。**
答：见 §2.7。**TF-A 主线开源，但飞腾 `plat/phytium/` 平台代码（尤其 BL31）大概率私有 fork，D3000M 一代开源度不透明** [推测-公开检索]。**风险**：BL31 跑 EL3 全机最高特权、从不退出——**闭源 = EL3 不可审计、不可补、不可信**。**对比鲲鹏「平台代码合回主线」，飞腾若不跟进就处于「EL3 黑箱」**。**建议（ROI 最高的一步）**：把 BL31 平台代码合回 TF-A 主线，零 RTL 泄露、立即可审计。

---

### 2.11 可运行 artifact：D3000M 启动链取证脚本（boot_chain_probe.sh）

固件工程师的真实工作不是读规范，是**开机后把这条链的证据全部捞出来**——证明信任链真的按预期跑了。下面这个脚本在 D3000M 上跑麒麟/UOS 时，**把整条启动链的「可见证据」全捞出来**，是 §2.3 推测图的实证检验工具：

```bash
#!/bin/bash
# boot_chain_probe.sh —— D3000M 启动链取证(普通用户可跑大部分, 部分需root)
# 作用: 把BL1→BL31→UEFI→GRUB→内核 这条链的可见证据全部捞出, 验证§2.3推测图
# 用法: bash boot_chain_probe.sh > boot_chain_report.txt 2>&1

echo "========== D3000M 启动链取证报告 =========="
echo "时间: $(date)"
echo "内核: $(uname -r)"
echo

echo "=== [1] UEFI 运行时证据 (BL33=UEFI 是否在跑) ==="
# /sys/firmware/efi 存在 = 内核是被 UEFI(非Legacy)启动的
ls -d /sys/firmware/efi 2>/dev/null && echo "→ UEFI 启动确认" || echo "→ 非 UEFI(可能是U-Boot/DeviceTree)"
echo "UEFI 版本: $(cat /sys/firmware/efi/fw_platform_size 2>/dev/null) 位"
# EFI 变量 (BootOrder/BootXXXX/PK/KEK/db)
echo "UEFI 变量区:"
ls /sys/firmware/efi/efivars/ 2>/dev/null | head -20
echo

echo "=== [2] ACPI 表清单 (SBPA 硬要求, 内核靠这个知道硬件拓扑) ==="
# SBBR 要求: DSDT/SSDT/MADT/APIC/FADT/GTDT/DBG2/SPCR/MCFG 至少这些
ls /sys/firmware/acpi/tables/ 2>/dev/null
echo "→ 若缺 MADT/GIC 子表, 内核无法初始化中断控制器"
echo "RSDP(根指针): $(dmesg | grep -i 'ACPI: RSCD\|RSDP' | head -1)"
echo

echo "=== [3] TF-A / BL31 证据 (EL3 Secure Monitor 是否在跑) ==="
# BL31 会通过特定 SMC 响应; PSCI 版本号由 BL31 报
echo "PSCI 版本 (由BL31的EL3响应):"
cat /sys/kernel/debug/psci/psci 2>/dev/null
# dmesg 里 BL31 的打印 (飞腾/TF-A 通常会有 banner)
dmesg | grep -iE 'TF-A|trusted firmware|BL31|phytium.*firmware|secure.*boot' | head -10
echo

echo "=== [4] Secure Boot 状态 (信任链是否启用验证) ==="
# 内核会被 UEFI Secure Boot 影响 (lockdown)
echo "内核 lockdown: $(cat /sys/kernel/security/lockdown 2>/dev/null || echo '未配置/不可读')"
echo "Secure Boot (mokutil, 若装):"
mokutil --sb-state 2>/dev/null || echo "  (mokutil 未安装, 用efivars查:)"
ls /sys/firmware/efi/efivars/PK-* /sys/firmware/efi/efivars/KEK-* /sys/firmware/efi/efivars/db-* 2>/dev/null
echo

echo "=== [5] TPM/TCM 度量设备 (Measured Boot 的载体) ==="
ls /dev/tpm* /dev/tpmrm* 2>/dev/null && echo "→ TPM/TCM 设备存在" || echo "→ 无 TPM/TCM 设备(Measured Boot 不可用)"
# TCM 在国内系统可能以 /dev/tpm 形式暴露
dmesg | grep -iE 'tpm|tcm|trusted.*platform' | head -5
echo

echo "=== [6] GRUB / 启动项 (BL33 之后) ==="
# ESP 分区
echo "ESP( EFI System Partition):"
lsblk -o NAME,FSTYPE,LABEL,MOUNTPOINT | grep -i 'vfat\|boot\|efi' 
echo "GRUB 配置:"
ls /boot/grub/grub.cfg /boot/efi/EFI/*/grub.cfg 2>/dev/null
echo

echo "=== [7] D3000M CPU 拓扑 (由ACPI/PSCI填充) ==="
echo "核数: $(nproc)"
echo "implementer/part: $(grep -m1 'CPU implementer\|CPU part' /proc/cpuinfo)"
echo "NUMA: $(numactl --hardware 2>/dev/null | head -3 || echo 'numactl未装')"
echo

echo "=== [8] 固件版本与更新能力 ==="
echo "DMI/固件版本 (dmidecode, 需root):"
sudo dmidecode -t bios 2>/dev/null | grep -iE 'vendor|version|release|date' || echo "  (需root, 或用 cat /sys/class/dmi/id/bios_version)"
cat /sys/class/dmi/id/bios_vendor /sys/class/dmi/id/bios_version 2>/dev/null
echo "fwupd(固件更新服务, LVFS接入度):"
fwupdmgr --version 2>/dev/null && fwupdmgr get-devices 2>/dev/null | head -20 || echo "  (fwupd未装, 可能未接入LVFS)"
echo
echo "========== 取证结束. 把这份报告与§2.3推测图逐行比对. =========="
```

**这个脚本在 D3000M 上跑，能区分三种状态**：
- **[1] `/sys/firmware/efi` 存在 + [2] ACPI 表齐全 + [3] PSCI 版本可读** → §2.3 推测图实证：UEFI+ACPI+TF-A 链搭对了（飞腾做到了及格线）[实测预期]。
- **[4] Secure Boot 启用 + [5] TPM/TCM 存在 + [6] GRUB 在 ESP** → 信任链完整启用（含 Measured Boot），属「企业级可信」[实测预期]。
- **[8] fwupd 接入 LVFS** → 固件可远程公开更新（更新率高、漏洞留存少）；**若 fwupd 未装或不识别设备 = 用户只能手动下补丁 = 更新率低** [实测预期]。

**配套的 BL31 深度验证 SOP（需 root + 调试口）**：① 接 UART 串口（飞腾主板有 debug UART），开机看 BL1/BL2/BL31 的 banner 打印——TF-A 默认会打印 `NOTICE: BL31: ...`，能看到 BL31 版本号；② 用 `smc` 指令探测 BL31 行为（PSCI 版本、CPU_ON 响应）；③ 若有 JTAG，读 EL3 系统寄存器确认 BL31 在跑。**这套 SOP 是判断 D3000M「信任链顶端 BL31 到底是谁、什么版本」的实证方法**——比读飞腾产品手册靠谱得多。

> **四号判断（方法论级）**：评估 D3000M 启动链可信度，**不要只看产品手册，要跑 boot_chain_probe + UART 看 BL31 banner**。
> 飞腾若能公开 BL31 版本号、TF-A 平台代码仓库、ServerReady ACS 测试报告，则即便固件闭源，**工程化可信度立即上一个台阶**；
> 若这些都不透明，则「能跑麒麟/UOS」不等于「信任链可信」。**这条 SOP 是本视角给飞腾和采购方共同的可操作建议。**

---

## 3. 设计决策评估：飞腾哪些决策认可 / 哪些该改

**认可的决策**：
1. **采用 TF-A + EDK2 + ACPI 的标准 ARM 服务器栈**——这是 SBBR 要求，飞腾没走「自研一整套固件」的歪路（那样生态孤立、维护成本爆炸），而是站在 ARM 标准栈上。**这让麒麟/UOS 能跑、让 Linux 主线 arm64 内核至少『有希望』跑**——这是及格线，飞腾做到了。
2. **实现 SM3/SM4 国密硬件指令**——这是国密合规启动的硬件红利（§2.5）。SM3 度量、SM4 加密都能硬件加速，是飞腾对信创合规启动**别人没有的差异化优势**（鲲鹏有，但飞腾也是 v8.4 全套）[实测-扩展专题]。
3. **用 mask ROM + eFuse 作 ROT（而非自研独立安全子系统）**——这是 ARM 标准方案，简单可审计。**飞腾没去自研一个『飞腾版 ME/PSP』是正确的**——ME/PSP 本身是巨大攻击面（Intel ME 漏洞史），ARM 的「轻 ROT」哲学反而更干净。

**该改的决策（按优先级）**：
1. **【最高优先】把 BL31 平台代码合回 TF-A 主线**：零 RTL 泄露（平台代码只是寄存器配置/内存映射/PSCI 实现），立即把 EL3 变成「社区可审计」。**这是消除「BL31 黑箱」、打开开放市场信任的 ROI 最高一步**。
2. **【最高优先】公开 ServerReady 认证状态 + SBSA ACS 测试报告**：发一份「D3000M 通过 SBSA Level X + SBBR ACS」的声明（对标鲲鹏）。**认证状态不透明 = 进不了开放 ARM 服务器市场**——这是「能不能卖」的事，不是「能不能跑」的事。
3. **【高优先】接入 LVFS（Linux Vendor Firmware Service）**：让 `fwupdmgr` 能公开拉取飞腾固件更新。**更新率从『手动下补丁的低更新率』变成『自动更新的高更新率』**——漏洞留存时间大幅缩短。
4. **【高优先】建立 CVE 公告渠道**：对标 Intel/AMD 的安全公告页，公开披露飞腾固件 CVE 与补丁。**「没有 CVE 公告」不是没漏洞，是没人在审**——建立公告渠道是邀请社区审计的第一步。
5. **【高优先】固件更新做 A/B 分区冗余 + 断电恢复 + 回滚保护**：这是「敢远程批量更新」的前提，数据中心运维刚需。否则运维不敢更新，漏洞长期留存。
6. **【中优先】明确国密信任链（SM2/SM3 签名链）的公开规格**：披露 BL1 用的是 RSA 还是 SM2 验签、信任链签名算法、TCM 2.0 集成方式。**这是信创合规的「可证明性」**——信创采购要的不是「据说用了国密」，是「能证明用了国密」。
7. **【中优先】GICv3 / SMMUv3 / PCIe 控制器驱动合回 Linux 主线**：让主线 arm64 内核（不只麒麟/UOS fork）能在 D3000M 跑——这是「ServerReady 认证」的工程前置。
8. **【前瞻】下一代（D4000）评估引入 ARMv9 RME / DICE**：v9 断供是现实，但若哪天放开，RME（Realm Management Extension）是信任链的下一代增强。**这是前瞻押注，不是当代能解决的**。

### 3.1 飞腾固件信任链路线图（按投入产出比分阶段）

把上面的「该改」按**投入产出比（ROI）**排成一张可执行路线图——这是本视角给飞腾 BIOS/固件团队的直接交付物：

| 阶段 | 动作 | 投入 | 收益 | 何时做 |
|:----:|:----|:----|:----|:------|
| **P0 零成本** | 公开 ServerReady 认证状态 + SBSA ACS 测试报告 | 文档声明 | **打开开放 ARM 服务器市场**，金融/互联网核心采购门槛 | 立即 |
| **P0 零成本** | 建立 CVE 公告渠道（对标 Intel/AMD 安全公告页） | 网页 + 流程 | 邀请社区审计，消除「没人在审」的灰色 | 立即 |
| **P1 低成本** | BL31 平台代码合回 TF-A 主线 | 几个固件工程师 × 季度 | **EL3 可审计**，消除「BL31 黑箱」（本视角最核心建议） | 6 个月内 |
| **P1 低成本** | 接入 LVFS（`fwupdmgr` 公开更新） | 对接工程 | 更新率↑，漏洞留存时间↓ | 6 个月内 |
| **P1 低成本** | GICv3/SMMUv3/PCIe 驱动合回 Linux 主线 | 内核工程 | 主线 arm64 内核可跑（不只麒麟/UOS fork） | 6 个月内 |
| **P2 中成本** | 固件更新做 A/B 分区冗余 + 断电恢复 + 回滚保护 | 固件工程 | 敢远程批量更新，数据中心运维刚需 | 一代内 |
| **P2 中成本** | 明确国密信任链公开规格（SM2 验签/SM3 度量/TCM 集成） | 文档 + 工程 | 信创合规「可证明性」 | 一代内 |
| **P2 中成本** | UEFI fork 持续同步 EDK2 主线补丁（堵 LogoFAIL 等 CVE） | 维护工程 | 不积累 EDK2 历史 CVE | 持续 |
| **P3 高成本** | 下一代引入 ARMv9 RME / DICE（若 v9 放开） | SoC + 信任链重设 | 信任链下一代增强 | 下一代（D4000，条件性） |

**表 D：飞腾固件信任链路线图（按投入产出比）。** 核心洞察：**P0（公开认证状态 + 建 CVE 渠道）是 ROI 最高的一步——零技术成本，却立即打开被「不透明」挡掉的市场**。**P1（合回 BL31 + 接 LVFS + 合回驱动）是把「飞腾孤岛固件」变成「生态固件」的关键**——决定装上任何标准 ARM 服务器 OS 后是否「开箱可用」。**这两步做完，D3000M 当代的固件价值就能充分释放，不需要等下一代**。其中**「BL31 合回主线」是本视角最强烈的一条建议**——它是消除飞腾信任链最大软肋（EL3 黑箱）的最短路径。

---

## 4. 这一视角的盲区与反方（诚实段，强制）

> 宪法 §4.3 第 2 条要求：敢说这一视角看不见什么、会误导什么。杜绝软文。

**盲区 1：固件视角会高估「信任链强度」对采购决策的权重。** 本视角通篇在比「信任链谁强谁可审计」，但**信创采购的决策逻辑里，『自主可控 + 国产供应链』往往压倒『信任链可审计』**。一个闭源 BL31，对采购方而言「反正都是国产，自主可控」，并不构成一票否决。**反方**：政府/国企信创采购更关心「能不能国产替代、能不能跑麒麟/UOS、有没有 TCM」——这些飞腾都做到了。本视角若被用来「一票否决飞腾进信创」，是**用开放市场的标准套信创市场，过度解读**。

**盲区 2：固件视角低估了「性能/能效」的权衡。** 把信任链堆满（Measured Boot 全开 + Secure Boot + TCM 远程证明）会增加开机时间、增加运行时 SMC 开销。**对高吞吐场景（如内存数据库），每次 PSCI/SMC 陷 EL3 的开销不可忽视**。**反方**：性能视角（Expert_09）会问「信任链全开 vs 默认配置，吞吐差多少」，答案常常是「够痛」。本视角天然有「信任链越完整越好」的职业偏见，要警惕。

**盲区 3：本视角大量结论标着 [推测-公开检索]，本身有不确定性。** D3000M 的 BL1/BL31 具体实现、ServerReady 认证状态、UEFI 是 EDK2 fork 还是商业 BIOS、国密信任链签名算法——**这些我没有一手固件逆向证据，全是「公开不披露」+ 「ARM 服务器标准做法」推出来的**。**反方**：飞腾内部可能早已通过 ServerReady 认证、早已合回 BL31、早已用 SM2 信任链——只是不对外宣传（信创供应链常见「闷头做、不宣传」）。本视角的「❓」**应被读作「需采购方尽职调查核实」，而非「一定不支持」**。这是诚实，也是免责。

**盲区 4：固件视角偏「启动链中心论」，忽视运行时安全。** 真实系统里，**运行时攻击（Spectre/Meltdown、内核提权、容器逃逸）远比启动链攻击常见**——启动链攻击需要物理接触或供应链植入，门槛高。本视角不覆盖运行时安全（那是 Expert_12 的领地）。**单看启动链会高估固件安全对整机安全的贡献**。

**盲区 5：本视角对 Intel ME / AMD PSP 的批评可能过重。** 我说「飞腾无独立安全子系统是『少一层纵深』」，但 **Intel ME 本身是巨大攻击面（Positive Technologies 系列研究证明 ME 可被攻破）**——「多一层纵深」也可能是「多一层攻击面」。**反方**：ME/PSP 的存在让 x86 多了一个「黑箱子系统」，而 ARM 的「轻 ROT」反而更干净。**「飞腾无 ME」既是弱点（少纵深）也是优点（少攻击面）**——这是双刃剑，本视角不应单边批评。

**盲区 6：LogoFAIL 等漏洞在飞腾上的实际影响，未经逆向证实。** 我推测「飞腾 UEFI 继承 LogoFAIL」基于「EDK2 fork 继承 CVE」的通则，但**飞腾可能删了 Logo 解析、可能已打补丁**——真实状态需固件逆向（IDA/Ghidra 反编译飞腾 UEFI 镜像）才能证实。本视角的 LogoFAIL 相关判断是**「理论上的漏洞面」而非「实证的漏洞」**，要诚实区分。

---

## 5. 与其他视角对偶（一致 / 冲突，强制）

> 宪法 §4.3 第 3 条要求：指明与其他视角的一致与冲突。

| 对偶视角 | 一致 / 冲突 | 具体点 |
|:--------|:--------:|:------|
| **Expert_23 服务器 RAS** | ✅ **强一致** | RAS 错误上报通路（GHES/APEI）全靠 BL31 正确实现。**E23 §2.9 的「软件栈待证」本质是 E18 BL31 的问题**——两者是同一断层的两面。RAS 与安全启动信任链都走 EL3/BL31。**E18 与 E23 是阶段 B 双胞胎，必须同读。** |
| **Expert_12 安全 CISO** | ✅ **强一致** | E12 §5 说「飞腾 RTL 闭源无法公开审计」，E18 把这话具体到 **BL31/EL3 这层**——RTL 闭源影响微架构，BL31 闭源影响信任链顶端，后者安全后果更直接。STRIDE 里「Tampering/EoP」的固件侧就在 E18。安全启动信任链（ROT→eFuse→逐级签名）是 E12 与 E18 的核心交集。 |
| **Expert_04 OS Kernel** | ✅ **强一致** | OS 视角看到的 `/proc/cpuinfo`（implementer=0x70, part=0x862）、GICv3、PSCI、ACPI 表——**全部由 E18 的 UEFI/BL31 提供给内核**。E04 是「内核怎么用」，E18 是「固件怎么给」，是上下游。**E04 §4.1「Phytium 扩展维护、内核滞后主线 1-2 年」的根因之一就是 E18 固件适配慢**。 |
| **Expert_21 AI 定位** | ⚠️ 部分冲突 | AI 视角要「能跑大模型推理」，固件视角要「信任链严」——两者在「是否启用某些加速路径」上有张力。但**更深的一致**：D3000M 无 BF16/I8MM/SVE 是 ISA 伤疤（E21），与固件无关；但**若飞腾下一代要加 AI 加速器，固件（BL31/UEFI）必须先支持该加速器的枚举与隔离**——E18 是 E21 的前置。 |
| **Expert_06 标准政策** | ✅ 一致 | SM3/SM4 入 ARMv8.4 是中国推动标准制定博弈的成果（E06），E18 的「国密合规启动」是这个政策成果在固件层的落地。**E06 是「为什么有国密指令」，E18 是「国密指令在信任链里怎么用」**。 |
| **Expert_22 开源生态** | ✅ 一致 | E22 讨论「飞腾开源生态命脉」，E18 的「BL31 合回主线、驱动合回 Linux 主线」是 E22 在固件层的具体诉求。**飞腾固件开源度 = E22 开源生态在固件侧的得分**。 |
| **Expert_10 分布式** | ✅ 一致 | 分布式系统要远程批量管理固件（BMC 带外更新），E18 的「Capsule Update + A/B 冗余」是 E10 的前置。**飞腾若固件不能远程批量更新，E10 的数据中心运维就难做**。 |
| **Expert_07 商业** | ⚠️ **冲突** | 商业视角要「拿订单、降成本」，固件视角要「合回主线、接 LVFS、做 A/B 冗余」（都要工程投入）。**冲突点**：飞腾固件工程团队规模有限，全做 P1/P2 成本不低，商业视角会问「ROI 够不够」。本视角若主张「不合规不能卖」，会被商业视角反驳「信创采购不认 ServerReady，认自主可控」——**E18 与 E07 在『该投开放市场还是信创闭环』上有真实张力**。 |

### 5.1 给采购方 / 运维的固件尽职调查清单（实战交付物）

把本视角的全部判断收敛成一份**采购方在选型飞腾 D3000M 服务器时该逐条问供应商、并要求拿出证据**的 checklist。每一项都对应前文某个判断，且**「拿不出证据」就按「不支持」对待**（这是固件安全的铁律——沉默不等于具备）：

- [ ] **启动链结构**：能否现场跑 §2.11 的 `boot_chain_probe.sh`，输出是否显示 UEFI+ACPI+PSCI+TF-A 链完整？（验证能跑麒麟/UOS 的根因）
- [ ] **ServerReady 认证**：D3000M 是否通过 ARM ServerReady（SBBR）认证？SBSA Level 几？能否出示 ACS 测试报告？
- [ ] **信任根（ROT）**：BL1 在 mask ROM 还是可改 flash？eFuse 公钥哈希是否出厂烧死？有没有独立安全子系统（类比 ME/PSP）？
- [ ] **BL31 开源度**：TF-A `plat/phytium/` 平台代码（尤其 BL31）是否合回主线？能否提供仓库链接或版本号？
- [ ] **UEFI 来源**：是 EDK2 fork（自研）还是商业 BIOS（AMI/Insyde）？UEFI 2.x 哪个版本？
- [ ] **ACPI 表完整性**：跑 `acpidump`，DSDT/MADT/FADT/GTDT/DBG2/SPCR/MCFG 是否齐全？（缺一张内核起不来）
- [ ] **安全启动签名链**：信任链用 RSA 还是国密 SM2 验签？UEFI Secure Boot 的 PK/KEK/db 谁掌握？采购方能否自管 PK？
- [ ] **国密合规**：信任链是否用 SM2/SM3/SM4？是否集成 TCM 2.0（外挂或片上）？有无 TPCM 主动度量？
- [ ] **Measured Boot**：开机是否把 BL 各阶段度量值扩展进 TCM 的 PCR？能否做远程证明？
- [ ] **TEE**：BL32 是 OP-TEE（开源）还是私有 TEE？能否跑通用 TA？
- [ ] **固件更新**：支持 UEFI Capsule Update 吗？接入 LVFS 了吗？有无 A/B 分区冗余/断电恢复/回滚保护？BMC 带外更新支持吗？
- [ ] **CVE 公告**：有无公开 CVE 公告渠道？LogoFAIL（CVE-2023-40238）补丁打了吗？EDK2 fork 同步到哪一版？
- [ ] **PSCI/SMMU/驱动合主线**：GICv3、SMMUv3、PCIe 控制器驱动是否合回 Linux 主线（不只麒麟/UOS fork）？

**这份清单的用法**：逐条要证据，**能答 6 条以上 = 可进信创办公/一般业务；能答 9 条以上 = 可进企业核心；全答齐 + ServerReady 认证 + BL31 开源 = 可谈开放市场/金融核心**。这是把本视角的「❓」变成「采购决策」的最短路径。

---

## 6. 参考文献（≥15，分级标注）

### 论文 / 标准 / 官方文档（≥5，本视角核心依据）

- [官方] **ARM**, *ARM Trusted Firmware (TF-A) Design Documentation* + *Trusted Board Boot Requirements (TBBR)*. —— **ARM 五级启动链（BL1→BL33）权威定义**，信任链逐级签名验证依据，§2.1/§2.4。
- [官方] **ARM**, *Server Base System Architecture (SBSA)* + *Server Base Boot Requirements (SBBR/SBPA)*. —— **ARM 服务器架构与启动要求规范**，UEFI+ACPI+GICv3+PSCI 硬要求依据，§2.6。
- [官方] **ARM ARM DDI 0487G.b**（2021-07），异常处理与启动章节（EL3/Secure Monitor/SMC）。—— **D3000M 实测对标的 ARM 权威手册**，§2.1 EL3/BL31 依据。
- [官方] **ARM**, *Power State Coordination Interface (PSCI) Specification* 1.x. —— **PSCI 权威定义**，§2.1 BL31 的 CPU on/off/hotplug 依据。
- [标准] **UEFI Forum**, *UEFI Specification* 2.x（含 Secure Boot PK/KEK/db 章节）+ *Platform Initialization (PI) Specification*（SEC/PEI/DXE/BDS 七阶段）。—— **UEFI 固件权威定义**，§2.2/§2.4/§2.8 依据。
- [标准] **UEFI Forum / ACPI**, *ACPI Specification* 6.x（RSDP/DSDT/MADT/FADT/GTDT/NFIT/APEI 章节）。—— **ACPI 表与硬件描述权威定义**，§2.2/§2.3 内核靠 ACPI 知道拓扑的依据。
- [标准] **GB/T 32918**（SM2 椭圆曲线公钥密码）、**GB/T 32905**（SM3 密码杂凑）、**GB/T 32907**（SM4 分组密码）。—— **国密三件套国家标准**，§2.5 国密合规启动依据。
- [标准] **GB/T 29829**（可信计算密码支撑平台）+ **GM/T 0012**（可信平台控制模块 TPCM）+ **GB/T 37092**（密码模块安全要求）。—— **中国可信计算/TCM 2.0 标准**，§2.5/§2.9 Measured Boot 与 TCM 依据。
- [官方] **Intel**, *Intel® Boot Guard* 技术文档 + *Intel® 64 SDM* Vol.3（CSME/ACM 章节）。—— **Intel Boot Guard 硬件 ROT 权威定义**，§2.4 ME/Boot Guard 纵深依据。
- [官方] **AMD**, *Platform Security Processor (PSP)* 技术文档。—— **AMD PSP 片上安全子系统依据**，§2.4 对照。
- [论文] **Binarly.io**, "LogoFAIL: LogoFAIL Vulnerabilities in UEFI Image Parsers," *Black Hat Europe 2023*（CVE-2023-40238 系列）。—— **UEFI 图片解析漏洞经典研究**，§2.8 LogoFAIL 依据。
- [论文/报告] **ESET**, "BlackLotus UEFI Bootkit: Myth Confirmed"（CVE-2022-21894）+ Bootkitty（2024）相关研究。—— **UEFI bootkit 与 Secure Boot 绕过研究**，§2.8 依据。
- [报告] **TianoCore / EDK2** 官方文档与 GitHub 仓库（edk2/edk2-platforms）。—— **UEFI 参考实现依据**，§2.2 EDK2 fork 判断依据。
- [报告] **Linaro / Arm64 UEFI Secure Boot** 文档与社区实践。—— **ARM 服务器 UEFI Secure Boot 工程实践**，§2.4 依据。
- [报告] **华为**, 鲲鹏 920 服务器固件/SBSA 合规/开源平台代码文档。—— **中国 ARM 服务器固件对标标杆**，§2.6/§2.7 鲲鹏对照依据。

### 报告 / 资源 / 项目内引用（补充）

- [标准] **TCG（Trusted Computing Group）**, *TPM 2.0 Specification*（国际对标 TCM）。—— §2.9 TPM/PCR/Measured Boot 国际对照。
- [报告] **Linux Vendor Firmware Service (LVFS) / fwupd** 官方文档。—— §2.8 固件更新机制依据。
- [报告] **Positive Technologies** Intel ME 安全研究系列。—— §4 盲区 5（ME 是攻击面）依据。
- [书] **Lewis, Z. et al.**, *Beyond BIOS* 或 *UEFI 原理与编程*（UEFI PI 七阶段深度）。—— §2.2 概念依据。
- [报告] **飞腾** D2000/D3000/FTC862 官方产品手册（固件章节有限）。—— §1/§2.6/§2.7 标 [推测-检索] 的根因。
- [项目内] [`isa_reference/v8.4_sm3_sm4.md`](../isa_reference/v8.4_sm3_sm4.md) —— **D3000M 国密 SM3/SM4 指令实测锚点**，§2.5 国密合规启动硬件依据。
- [项目内] [`扩展专题.md`](../扩展专题.md) §1 第 22/23 项（SM3/SM4）+ 第 13 项（v8.2 RAS）—— 实测矩阵。
- [项目内] [`Expert_04_OS_Kernel/README.md`](../Expert_04_OS_Kernel/README.md) §2.1（/proc/cpuinfo implementer=0x70）+ §3.3（GICv3）—— OS 侧看到的固件产物。
- [项目内] [`Expert_12_Security_CISO/README.md`](../Expert_12_Security_CISO/README.md) §3（TrustZone/TEE）+ §5（供应链闭源）—— 安全与固件交集。
- [项目内] [`Expert_23_Server_RAS/README.md`](../Expert_23_Server_RAS/README.md) §2.9（GHES/APEI 固件侧）—— RAS 与固件同一断层的另一面。
- [项目内] [`Lab00_测量基础设施/`](../Lab00_测量基础设施/) —— /proc/cpuinfo、arch_probe 实测。

---

## 7. 延伸阅读（项目内 + 外部）

**项目内**：
- [`isa_reference/v8.4_sm3_sm4.md`](../isa_reference/v8.4_sm3_sm4.md) —— 国密 SM3/SM4 指令级深度剖析（国密合规启动的硬件锚点）。
- [`扩展专题.md`](../扩展专题.md) §1 第 22/23 行 —— SM3/SM4 实测矩阵。
- [`Expert_04_OS_Kernel/README.md`](../Expert_04_OS_Kernel/README.md) —— OS 视角看固件产物（/proc/cpuinfo、GICv3、PSCI、ACPI 表）。
- [`Expert_12_Security_CISO/README.md`](../Expert_12_Security_CISO/README.md) §3（TrustZone/TEE/信任链）—— 安全与固件核心交集。
- [`Expert_23_Server_RAS/README.md`](../Expert_23_Server_RAS/README.md) §2.9（GHES/APEI 错误通路）—— E18 与 E23 是同一断层的两面。
- [`Expert_22_OpenSource_Ecosystem/`](../Expert_22_OpenSource_Ecosystem/)（新增中）—— 飞腾开源生态（BL31/驱动合回主线是固件侧诉求）。

**外部**：
- ARM Trusted Firmware (TF-A) 官方文档 + GitHub（`plat/phytium/` 平台代码）。
- ARM Server Base System Architecture (SBSA) / Boot Requirements (SBBR/SBPA) 规范 + ACS 测试套件。
- UEFI Forum Specification 2.x + TianoCore EDK2 文档。
- ACPI 6.x 规范（RSDP/DSDT/MADT/APEI/NFIT 章节）。
- ARM PSCI Specification + ARM ARM DDI 0487（EL3/Secure Monitor/SMC）。
- GB/T 32918/32905/32907（国密 SM2/SM3/SM4）+ GB/T 29829/GM/T 0012（TCM/TPCM）。
- Intel Boot Guard + AMD PSP 技术文档（x86 信任链对照）。
- Binarly LogoFAIL 研究（CVE-2023-40238）+ ESET BlackLotus/Bootkitty 研究。
- 华为鲲鹏 920 服务器固件/SBSA 合规文档（中国 ARM 服务器固件对标标杆）。
- Linux Vendor Firmware Service (LVFS) / fwupd 文档。

---

📌 **下一步**：本视角（E18）与 E23（服务器 RAS）、E21（AI 定位）同属阶段 B「服务器致命断层」三件套。
**E18 与 E23 是同一断层的两面**——E23 §2.9 的 RAS 软件栈「待证」，根因就在 E18 的 BL31/UEFI。
建议接读 [`Expert_23_Server_RAS/README.md`](../Expert_23_Server_RAS/README.md)（GHES/APEI 通路根因）与
[`Expert_12_Security_CISO/README.md`](../Expert_12_Security_CISO/README.md)（信任链/TrustZone 交集），
再回 [`Views.md`](../Views.md) 看完整视角矩阵。

---

## § 固件与启动链方法论及资源（不只飞腾，给所有固件/系统启动工程师）

> 本章把 E18 的飞腾固件分析上升为**任何固件/启动链工程师都可复用的方法与资源**。飞腾是案例锚点（UEFI/TF-A on ARM），方法普适。通用资源见 [`领域资源库.md`](../领域资源库.md)。

### 方法论一：ARM 服务器启动链（BL1 → BL31 → UEFI → OS）

ARM 启动是严格的信任链阶段瀑布（不可跳序）：

| 阶段 | 固件 | 位置 | 职责 | 信任级别 |
|------|------|------|------|---------|
| BL1 | Boot ROM（出厂烧死）| 芯片内 ROM | 验签 BL2，**信任根** | 最高（不可改）|
| BL2 | Trusted Firmware-A（TF-A）| flash | 初始化安全世界，加载 BL31/BL32/BL33 | Secure |
| BL31 | TF-A（常驻 EL3）| SRAM | **运行时 SMC/PSCI/RAS 调度**，OS 启动后仍驻留 | EL3（最高权限）|
| BL32 | OP-TEE / TrustZone OS | 安全世界 | 安全应用（DRM/密钥/指纹）| S-EL1 |
| BL33 | **UEFI 固件** | flash | 初始化外设/ACPI/设备树，加载 bootloader（GRUB）| EL2/EL1 |
| OS | Linux/麒麟/UOS | 磁盘 | 操作系统 | EL0/EL1 |

**铁律**：信任链任何一环断裂（验签缺失/密钥泄露）= 整链可篡改。飞腾案例（E18 §安全启动）适用任何 ARM 平台。

### 方法论二：UEFI vs U-Boot vs Coreboot（固件选型）

- **UEFI**（飞腾/服务器主流）：企业级，ACPI/SMM/Secure Boot，重但完整（EDK2 开源实现）
- **U-Boot**（嵌入式主流）：轻量，device tree，适合嵌入式/路由器
- **Coreboot**（开源极简）：Chromebook/开源硬件用，秒级启动
- 选型：服务器/企业 → UEFI；嵌入式 → U-Boot；极致精简 → Coreboot

### 方法论三：信任根与安全启动

- **RoT（Root of Trust）**：BL1 ROM + 一次性可烧 fuse（公钥哈希）= 不可篡改信任根
- **Secure Boot**：每阶段验签下阶段（签名链）
- **Measured Boot**：度量（hash 记录）而非强制，配合 TPM/TCM 远程证明
- 飞腾国密信任根用 TCM（GB/T 29829），国际用 TPM 2.0

### 固件专属资源

- **标准**：**UEFI Forum**（uefi.org）、**TF-A**（Trusted Firmware-A，trustedfirmware.org）、**SBSA/SBPA**（ARM 服务器基础规范）、ACPI Specification、PSCI（ARM 电源协调）
- **开源固件**：**EDK2**（UEFI 参考实现）、**U-Boot**、**Coreboot**、**TF-A**、**OP-TEE**（TrustZone OS）
- **工具**：QEMU（固件仿真调试）、DCUT、fwupd、dmidecode、**acpidbg**
- **书/资料**：UEFI Specification、Zimmer《Beyond BIOS》、ARM DEN0024（ARM 平台启动）

### 给固件/启动工程师的通用建议

1. **信任根是命门**：BL1 ROM + fuse 公钥哈希必须物理保护，泄露 = 全盘可篡改。
2. **BL31 常驻 EL3**：OS 启动后仍跑，是 PSCI/RAS/SMC 中枢，bug = 整机不稳定。
3. **ACPI vs Device Tree 要早定**：服务器（ACPI）vs 嵌入式（DT），切换代价大。
4. **安全启动 + 度量启动配合**：Secure Boot 防篡改，Measured Boot + TPM 可远程证明（飞腾 TCM 国密版）。
5. **固件适配是新平台最大工程债**：UEFI/TF-A 移植到新 SoC 数月级，飞腾 ACPI/PSCI 滞后根因在此（E18 核心，适用任何新 ARM 平台）。
