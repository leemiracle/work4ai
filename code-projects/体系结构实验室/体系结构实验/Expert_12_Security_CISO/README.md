# Expert_12 — 首席安全官视角（CISO / 威胁模型专家）

> **角色定位**：企业 CISO / 安全研究员 / 红队队长 / 信任根设计师。
> 我不只会跑 [View_02 cache timing](../View_02_Security/) POC——**我关心完整威胁模型、信任链全链路、
> 以及供应链里那颗谁也看不见的芯片到底能不能信**。
>
> **核心思维模型**：**STRIDE**（微软威胁分类法）× **Lockheed 杀伤链**（Cyber Kill Chain®）×
> **ARM 信任根架构**（TrustZone / CCA / ROT）× **推测执行攻击与缓解经济学**（Spectre 性能代价量化）。
> 一句话总结我怎么看一颗 CPU：**CPU 既是攻击目标（侧信道泄漏）、攻击工具（推测执行原语），
> 也是攻击载体（供应链 / 硬件木马 / 信任链植入）。** 我把这三层全要问一遍「能证明安全吗？不能证明 = 不能假设安全。」

---

## 0. 写在最前面：CISO 看飞腾 D3000M 的一号结论

> **先亮底牌**：飞腾 D3000M 作为国产 ARMv8.4 服务器 CPU，**密码学硬件地基扎实**（SM3/SM4/AES/SHA
> 全部 ISA 级实现 [实测-扩展专题]），**Meltdown 天生免疫**（ARM 大部分核不含 x86 那种特权检查旁路），
> 这是它作为信创安全 CPU 的**两张硬牌**。但它有三个 CISO 必须正视的结构性短板：
>
> 1. **信任链「能跑但不可证明」**：启动链结构完整（mask ROM → BL31 → UEFI → 内核，接 [Expert_18](../Expert_18_Firmware_Boot/README.md)），
>    但 BL31 闭源、RTL 闭源、ServerReady 认证状态不透明——**「能跑麒麟/UOS」≠「信任链可审计」**。
> 2. **缺 v8.5+ 推测执行硬件缓解**：D3000M 停在 ARMv8.4，**BTI（v8.5）必然缺失、SSBS/MTE 不确定**。
>    对 Spectre v2/v4 的防护**只能靠软件补丁**，性能代价（5–15%）可能比有硬件缓解的竞品更高。
> 3. **硬件后门「不可证否」**：飞腾自研 FTC862 核是好事（不买 ARM 现成核 = 供应链更短），
>    但 RTL 闭源 = 外部无法审计有没有硬件木马。**「国产自研」降低了一个风险面（外国植入），
>    却无法消除另一个风险面（自家后门 / 无意缺陷）**——这正是 [Expert_19](../Expert_19_Geostrategy/) 地缘视角与安全视角的交汇点。

这三个判断是本视角通篇的骨架。下面逐层展开。

---

## 1. 看飞腾 D3000M 的 10 个核心安全问题

1. **信任链从哪开始？**（信任根 / Root of Trust——mask ROM 不可改，还是可改 flash？）
2. **信任链每一级谁验谁的签名？**（BL1→BL2→BL31→UEFI→GRUB→内核→应用，接 [Expert_18](../Expert_18_Firmware_Boot/README.md) §2.4）
3. **ARM TrustZone / CCA 在飞腾上能用吗？**（TEE 是 OP-TEE 还是私有？Realm 隔离有没有？）
4. **Spectre / Meltdown 缓解到什么程度？性能代价多大？**（v8.4 缺 BTI/SSBS/MTE 的后果）
5. **供应链：芯片设计 / 流片 / 封装 / 测试 各环节如何审计？**（硬件木马怎么查？）
6. **国密 SM2/SM3/SM4 的实现可信吗？**（指令在 ≠ 信任链跑通）
7. **飞腾自研 FTC862 核 vs 买 ARM 核——哪个更难植入后门？**
8. **PAuth（指针签名）在飞腾上有没有？**（v8.3 OPTIONAL，[扩展专题] 标 ⚠️，是 ROP 防护关键）
9. **等保 2.0 / GB 标准合规——飞腾能不能过「三级」？**（CISO 治理）
10. **出事了怎么响应？**（事件响应 IR——固件级持久化怎么清？）

第 1/2/4/5/7 是**只有这颗芯片才答得出**的特异性问题——这是本视角通过「D3000M 特异性测试」的保证。

---

## 2. 完整威胁模型（STRIDE / Lockheed 杀伤链）

### 2.1 STRIDE 模型应用到 CPU

| 威胁类型 | 在 CPU 上的体现 | 飞腾现状 |
|---------|---------------|---------|
| **S**poofing（伪装）| 假冒硬件身份（如伪装 GPU / 假芯片调包）| 飞腾 + 主板 TCM + eFuse unique ID |
| **T**ampering（篡改）| 硬件 backdoor / 调试后门 / 固件植入 | JTAG 锁 / eFuse / mask ROM 不可改 |
| **R**epudiation（抵赖）| 操作日志被绕过 | ARM v8.2 RAS + auditd + TCM PCR 度量 |
| **I**nformation Disclosure（信息泄漏）| **侧信道（Spectre/Meltdown/Rowhammer）** | **本视角核心，见 §4** |
| **D**enial of Service | Rowhammer / 故障注入 / 软错误风暴 | ECC DDR4 + SEC-DED（[Expert_23](../Expert_23_Server_RAS/README.md) §2.4）|
| **E**levation of Privilege | 推测执行滥用 / ROP / 容器逃逸 | v8.5 SSBS/CSV3 **缺失或不确定**（见 §4）|

**表 1：STRIDE 威胁模型应用到 D3000M。**

### 2.2 攻击向量分类（三层）

```
┌────────────────────────────────────────────────────┐
│  软件层（OS / 应用 / 运行时）                          │
│   ├─ Spectre v1（边界检查绕过 BCB）                    │
│   ├─ Spectre v2（分支目标注入 BTI）                    │
│   ├─ Meltdown（特权数据泄漏）   ← ARM 大部分免疫        │
│   ├─ Spectre v4（推测 store 旁路 SSPP）                │
│   ├─ Spectre-BHB（分支历史注入）                        │
│   ├─ Retbleed（推测 unret）  ← ARM 影响小              │
│   ├─ Downfall（AVX gather 旁路）  ← x86 专有            │
│   └─ Cache timing（Flush+Reload / Prime+Probe）       │
├────────────────────────────────────────────────────┤
│  硬件层（RTL / 物理）                                  │
│   ├─ 硬件 backdoor（隐藏指令 / 预留特权后门）           │
│   ├─ 故障注入（电压 glitch / 时钟 / 电磁 / 激光）       │
│   ├─ Rowhammer（DDR bit 翻转）                         │
│   └─ 光学探测（开盖 / 红外 / FIB 改线）                 │
├────────────────────────────────────────────────────┤
│  供应链（设计 → 流片 → 封装 → 物流）                    │
│   ├─ RTL 中恶意逻辑（硬件木马）                         │
│   ├─ 流片时 mask 篡改（代工厂加料）                     │
│   ├─ 封装 / 测试 backdoor（测试 pattern 植入）          │
│   └─ 物流替换（真假芯片调包 / remark）                  │
└────────────────────────────────────────────────────┘
```
**图 2：攻击向量三层分类（软件层 / 硬件层 / 供应链层）。**

### 2.3 Lockheed 杀伤链还原：攻击者要拿下飞腾服务器得走几步

把 STRIDE 映射到 [Lockheed Martin Cyber Kill Chain®](https://www.lockheedmartin.com/cyber/kill-chain) 的七阶段，能看清**哪一步是飞腾的防御强项、哪一步是软肋**：

```
  侦察 → 武器化 → 投递 → 利用 → 安装 → 命令控制 → 行动目标
   │       │       │       │       │        │         │
   │   钓鱼邮件  恶意附件  内核漏洞  rootkit  C2回连   窃数据
   │                                          │
   ▼                                          ▼
 [飞腾强项]                              [飞腾强项]
  Spectre v1/v2 ← 软件补丁                 TCM 度量启动 ← 国密合规
  Meltdown ← 天生免疫                      SM4 磁盘加密 ← 硬件加速
                                          
 [飞腾软肋]                              [飞腾软肋]
  无 BTI/MTE ← v8.4 缺失                   BL31 闭源 ← 持久化清不掉
  PAuth 不确定 ← ROP 防护弱                固件漏洞 ← 无 CVE 公告渠道
```
**图 3：Lockheed Cyber Kill Chain® 七阶段映射到飞腾强项 / 软肋。** [资源-Lockheed-KC]

**关键洞察**：杀伤链的前四步（侦察→利用）主要靠 OS / 应用层补丁，与 CPU 关系不大；**但「安装」与「行动目标」两步——如果攻击者拿到了固件级持久化（BL31/UEFI 后门），重装系统也清不掉**。这正是 [Expert_18](../Expert_18_Firmware_Boot/README.md) §2.7「BL31 闭源 = EL3 黑箱」的安全后果——**固件是机器里唯一一个「重装系统都清不掉」的攻击面** [论文-LogoFAIL]。

---

## 3. 信任链完整还原：从 mask ROM 到应用（核心深化，接 E18）

> 本节回答一号必答问题：**信任链从哪来？** 这是 CISO 评估一颗 CPU「能不能信」的根基。

### 3.1 ARM TrustZone（飞腾 D3000M 必然支持）

```
┌──────────────────────────────────────────────────┐
│  Normal World（REE - Rich Execution Environment）│
│   ├─ Linux / 麒麟 / UOS                              │
│   ├─ 用户应用                                        │
│   └─ 普通 driver                                    │
├──────────────────────────────────────────────────┤
│  ↑ 监控模式切换（SMC 指令）                         │
├──────────────────────────────────────────────────┤
│  Secure World（TEE - Trusted Execution Env）       │
│   ├─ OP-TEE（开源 TEE OS）                          │
│   ├─ Trusted Apps（TA）                             │
│   └─ 密钥 / 安全存储                                │
├──────────────────────────────────────────────────┤
│  ↑ EL3                                              │
├──────────────────────────────────────────────────┤
│  ARM Trusted Firmware（BL31 etc.）                 │
└──────────────────────────────────────────────────┘
```

**飞腾现状**：
- ✅ ARMv8 强制 TrustZone [官方-ARM-TrustZone]
- ✅ TF-A（ARM Trusted Firmware）已适配 Phytium（`plat/phytium/`）[推测-GitHub检索]
- ⚠️ 国产 OP-TEE 替代（如阿里 / 蚂蚁自研 TEE）或飞腾私有 TEE——**生态二选一，不公开** [推测-生态]

### 3.2 信任链逐级还原：mask ROM → BL31 → UEFI → 内核 → 应用

信任链（Chain of Trust）的本质是**从一个不可改的信任根（ROT）开始，每一级用上一级的密钥验证下一级的签名，逐级延伸** [官方-ARM-TFA]。任何一环验签失败，链就断——机器要么拒绝启动，要么进恢复模式。

把 [Expert_18](../Expert_18_Firmware_Boot/README.md) §2.3/§2.4 的固件启动链，用 CISO 的「信任传递」视角重新画一遍——**每一级标「信任从哪来、传递给谁、断了会怎样」**：

```
 [eFuse 公钥哈希]  ← 出厂烧死, 不可改, 全链唯一真根 [推测-架构必然]
        │ 硬件比对
        ▼
 [BL1: FTC862 片上 mask ROM]  ← 飞腾固化, 不可改 = ROT
   信任来源: eFuse
   传递给: 验 BL2 签名(SM2 或 RSA)
   断了: 机器拒绝启动(砖)
        │ BL2 验签通过才执行
        ▼
 [BL2: TF-A 平台代码 plat/phytium/]  ← 飞腾私有 fork [推测-TF-A惯例]
   信任来源: BL1 验它
   传递给: 初始化 DDR, 加载验签 BL31/BL32/BL33
   断了: 启动链断在 BL2
        │
        ▼
 [BL31: EL3 Secure Monitor]  ← ★全机最高特权, 从不退出★ [推测-TF-A惯例]
   信任来源: BL2 验它
   传递给: 实现PSCI/SMC变速箱/RAS异常处理(接E23 §2.9)
   ★ 闭源 = EL3 不可审计 = 信任链顶端黑箱 ★
   断了: 后门可永久持久化(内核重装清不掉)
        │
        ▼
 [BL32: OP-TEE 或私有 TEE]  ← S-EL1, 承载 TA(指纹/密钥/DRM)
        │
        ▼
 [BL33: UEFI 固件 = EDK2 fork]  ← 飞腾/麒麟软件维护 [推测-供应链]
   信任来源: BL2 验它
   传递给: UEFI Secure Boot 验 GRUB2 (PK/KEK/db 三级密钥)
   断了: LogoFAIL/BlackLotus 类漏洞可植入 bootkit
        │
        ▼
 [GRUB2 → vmlinuz 内核]  ← 麒麟/UOS arm64
   信任来源: UEFI Secure Boot 验 GRUB, GRUB 验内核
   传递给: 内核 lockdown, 启用内核签名校验
        │
        ▼
 [应用层]  ← systemd → 业务进程
   信任来源: 内核(进程隔离/权限)
   最终用户态: 信任链到此传递完毕
```
**图 1：D3000M 安全启动信任链——从 eFuse 一路签到应用层。** 每级标信任来源与断裂后果。 [官方-ARM-TFA][标准-UEFI]

**CISO 的三重读法**：

**一号读法（信任根在哪）**：飞腾的 ROT = **FTC862 片上 mask ROM（BL1）+ eFuse 公钥哈希**——ARM 标准方案 [推测-架构必然]。**没有独立安全子系统**（不像 Intel Boot Guard 有 CSME、不像 AMD 有 PSP 片上 ARM 核）。这意味着飞腾信任根强度 = mask ROM 不可改 + eFuse 烧死，与鲲鹏/Graviton 同档，**弱于 Intel/AMD 的 ME/PSP 纵深**（但 ME/PSP 本身也是巨大攻击面——见 §8 盲区 4）。

**二号读法（信任链的灰色地带）**：这条链**可信度全部依赖三个「闭源」**——BL1（mask ROM 物理闭源）、BL2+BL31 平台代码（飞腾私有 fork 逻辑闭源）、UEFI（EDK2 fork 逻辑闭源）。**外部既不能审计有没有后门，也不能独立验证签名逻辑正确性，更不能在飞腾不发补丁时自行修补。** 这是与 [Expert_18](../Expert_18_Firmware_Boot/README.md) §2.7 强一致的核心批评。

**三号读法（国密签名链）**：信任链的签名算法是 RSA/ECDSA 还是国密 SM2——对信创合规是硬要求。D3000M 有 SM3 硬件指令（7 条）和 SM4 指令（2 条）[实测-扩展专题]，**SM3 度量可信、SM4 加密可信，但 SM2 验签无单条指令**（需软件或加速器）[实测-无SM2指令]。所以飞腾信任链**验签环节要么软件 SM2（慢）、要么片上 SM2 加速器（信创服务器标配，推测有但不公开）** [推测-信创合规]。

### 3.3 ARM CCA（Confidential Compute Architecture）

ARM 2021 推出的 CCA 是 TrustZone 的下一代：
- **RME（Realm Management Extension）**：硬件隔离的「Realm」——虚拟机级隔离
- **可证明执行**（Remote Attestation）——第三方能验证「这段代码在可信环境里跑过」

**飞腾现状**：D3000M 是 ARMv8.4，**不支持 RME**（v9 才有）[官方-ARM-CCA]。下一代 D4000 推测会加（若 v9 放开授权）。**这意味着 D3000M 做不了「机密计算」——无法给云租户提供硬件级 VM 隔离证明**，这是进公有云 / 多租户场景的硬伤 [推测-代差]。

---

## 4. Spectre / Meltdown 实测深化：缓解状态与性能代价量化

> 本节回答二号必答问题：**D3000M 对 Spectre 的真实缓解代价？** 这是 CISO 决定「要不要开缓解」的依据。

### 4.1 缓解状态矩阵（飞腾 v8.4 实测）

| CVE | 类型 | 飞腾 D3000M 状态 | 硬件缓解 | 软件缓解 | 备注 |
|-----|------|:--------------:|:------:|:------:|------|
| **Meltdown (CVE-2017-5754)** | 数据 cache 旁路 | ✅ **天生免疫** | — | — | ARM 大部分核免疫 [论文-Meltdown] |
| **Spectre v1 (CVE-2017-5753)** | 边界检查绕过 | ⚠️ 受影响 | — | Load fence 插桩 | 软件补丁,编译器级 [论文-Spectre] |
| **Spectre v2 (CVE-2017-5715)** | 分支目标注入 | ⚠️ 受影响 | ❌ **无 BTI(v8.5)** | retpoline / BTB flush | **v8.4 缺 BTI 是硬伤** |
| **Spectre v3a (CVE-2018-3640)** | 系统 register 旁路 | ⚠️ 部分受影响 | — | 内核态隔离 | — |
| **Spectre v4 (CVE-2018-3639)** | 推测 store 旁路 | ⚠️ 受影响 | ❌ **SSBS 不确定** | 软件 STLF 屏障 | SSBS 是 v8.5,飞腾 v8.4 待证 |
| **Spectre-BHB (CVE-2022-23960)** | 分支历史旁路 | ⚠️ 受影响 | ❌ 无 BTI | 软件循环清 BTB | 无 BTI 靠软件 [论文-Spectre-BHB] |
| **Retbleed (CVE-2022-29900/1)** | 推测 unret | 🟡 ARM 影响小 | — | — | 主要影响 x86 retpoline [论文-Retbleed] |
| **Downfall (CVE-2022-40982)** | AVX gather 旁路 | ✅ ARM 不受影响 | — | — | x86 专有 [论文-Downfall] |
| **Inception (CVE-2023-20569)** | 分支预测中毒 | ✅ ARM 不受影响 | — | — | AMD Zen 专有 |

**表 2：D3000M (v8.4) Spectre/Meltdown 缓解状态矩阵。**

**D3000M 的关键发现（CISO 必须知道）**：

D3000M 停在 **ARMv8.4**，而 ARM 把推测执行**硬件级缓解**主要放在了 **v8.5-A**：
- **BTI（Branch Target Identification，`bti` 指令，v8.5）**：D3000M **必然缺失**——这是防 Spectre v2 的核心硬件机制，缺失意味着只能靠软件 retpoline/BTB flush。
- **SSBS（Speculative Store Bypass Safe，PSTATE 位，v8.5）**：D3000M **不确定**——可能作为可选扩展实现，也可能没有。需跑 `ID_AA64PFR1_EL1` 实测确认。
- **CSV3（v8.5）**：同上不确定。
- **MTE（Memory Tagging Extension，v8.5+）**：D3000M **缺失**——这是防内存安全的下一代机制（标签化内存），v9 才标配。

**这意味着**：D3000M 对 Spectre v2/v4 的防护**比有 BTI/SSBS 的 v8.5+ 核（如 Cortex-A78+/X3）更依赖软件补丁**，性能代价可能更高（见 §4.2）。**这是 v8.4「卡版本」在安全层的具体代价——与 BF16/I8MM/SVE 缺失（[Expert_21](../Expert_21_AI_Positioning/)）是同一个根因（ARM v9 不授中国）。**

### 4.2 缓解性能代价量化

**飞腾真实缓解效果（性能损失，标来源分级）**：

| 缓解配置 | 性能损失 | 来源 | CISO 建议 |
|---------|:-------:|------|----------|
| 全部缓解开启 | **~5–15%** | [推测-ARM通用] | 金融 / 核心数据库必开 |
| 默认 Linux 配置 | ~3–8% | [推测-ARM通用] | 一般业务默认即可 |
| 关闭缓解 `mitigations=off` | 恢复 | [实测-通用] | **仅隔离测试环境，有安全风险** |
| 单开 Spectre v1 (fence) | ~1–3% | [报告] | 代价低,建议开 |
| 单开 Spectre v2 (无BTI,软件retpoline) | **~3–7%** | [推测-v8.4无BTI] | **代价偏高(因无硬件BTI)** |
| 单开 Spectre v4 (无SSBS,软件) | ~2–5% | [推测-v8.4无SSBS] | 代价中,视场景 |

**表 3：缓解性能代价量化。**

**关键洞察**：Spectre v2 的软件缓解（retpoline/BTB flush）在**没有硬件 BTI 的情况下代价更高**——因为每次间接分支都要软件清 BTB 或插 retpoline 序列，无法用硬件 `bti` 指令高效过滤。**这是 D3000M v8.4 的安全性能税——比 v8.5+ 核（有 BTI）多付几个百分点。**

**命令行控制（实测可跑）**：
```bash
# 查看当前缓解状态
cat /sys/devices/system/cpu/vulnerabilities/*
#spectre_v1: Mitigation: Load fences
#spectre_v2: Mitigation: Branch predictor hardening (若显示 "Vulnerable" = 没缓解!)
#meltdown: Not affected                          ← ARM 免疫
#spec_store_bypass: Mitigation: Speculative Store Bypass disabled

# 关闭所有缓解（仅在隔离测试环境，CISO 不建议生产开）
sudo grubby -u --args="mitigations=off"
```

### 4.3 可运行 artifact：侧信道信噪比探测（接 View_02）

[View_02 Security](../View_02_Security/) 已有 cache timing POC。CISO 的补充视角是**量化信噪比（SNR）**——同样跑 Flush+Reload [论文-FLUSH+RELOAD]，D3000M 的 LLC（8MB shared @ 14ns [实测-Lab03]）越大，攻击者 Prime+Probe 的分辨率越依赖 LLC 拓扑。**一个快速的 SNR 探测**：

```c
/* spectre_snr_probe.c —— D3000M 侧信道信噪比粗测 (接 View_02 cache_timing.c)
 * 编译: gcc -O2 -o spectre_snr spectre_snr_probe.c
 * 作用: 跑 Flush+Reload N 次, 算命中/未命中的时间分布重叠度 → SNR 越高 = 越易被攻击
 * 注: 这是教育性 POC, 非武器化利用 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
static inline void flush(void *p){ __builtin___clear_cache(p, p+64); }
static inline uint64_t rdtsc(void){
  uint64_t v; __asm__ volatile("mrs %0, cntvct_el0":"=r"(v)); return v; }
static inline uint64_t probe(char *p){
  uint64_t t0=rdtsc(); *(volatile char*)p; uint64_t t1=rdtsc(); return t1-t0; }
int main(){
  char buf[64]; memset(buf,1,64); const int N=100000;
  /* 测命中时间分布(cached) */
  uint64_t hit_min=~0,hit_max=0; double hit_sum=0;
  for(int i=0;i<N;i++){ buf[0]=2; uint64_t t=probe(buf); hit_sum+=t;
      if(t<hit_min)hit_min=t; if(t>hit_max)hit_max=t; }
  /* 测未命中时间分布(flushed) */
  uint64_t miss_min=~0,miss_max=0; double miss_sum=0;
  for(int i=0;i<N;i++){ flush(buf); uint64_t t=probe(buf); miss_sum+=t;
      if(t<miss_min)miss_min=t; if(t>miss_max)miss_max=t; }
  double hit_avg=hit_sum/N, miss_avg=miss_sum/N;
  /* SNR ≈ (miss_avg - hit_avg) / 命中分布宽度; >1 = 可区分 = 侧信道可行 */
  printf("== D3000M 侧信道 SNR 探测 ==\n");
  printf("命中(cached):  avg=%.0f cyc, min=%lu, max=%lu\n",hit_avg,hit_min,hit_max);
  printf("未命中(flush): avg=%.0f cyc, min=%lu, max=%lu\n",miss_avg,miss_min,miss_max);
  double gap=miss_avg-hit_avg, width=hit_max-hit_min;
  printf("间隔=%.0f cyc, 命中宽度=%lu cyc → SNR≈%.1f\n",gap,hit_max-hit_min, width>0?gap/width:0);
  printf("SNR>1.0 = Flush+Reload 可行(侧信道存在); SNR<0.5 = 难以区分\n");
  /* D3000M L3@14ns(~35cyc@2.5GHz) 预期 miss 远大于 hit, SNR 应 >2 */
  return 0;
}
```
**预期结果**：D3000M 的 L3 @ 14ns（[实测-Lab03]）≈ 35 cyc @2.5GHz，与 L1 命中（~4 cyc）间隔 >30 cyc，**SNR 应 >2.0 = Flush+Reload 可行**——证明 D3000M **不免疫 cache 侧信道**，缓解靠软件（不在共享 secret 旁放敏感数据 / KPTI / 页隔离）。

---

## 5. 供应链安全与硬件 backdoor 审计（核心深化）

> 本节回答三号必答问题：**硬件 backdoor 怎么审计？** 这是 CISO 评估「国产自研」到底安不安全的关键。

### 5.1 RTL 阶段风险

飞腾作为国产 CPU，**理论上**供应链更可控（设计在国内、流片在成熟制程），但仍有风险：
- 飞腾 RTL 是**闭源**——无法公开审计 [推测-公开检索]
- 商业 IP（如 Synopsys USB / PCIe 控制器、ARM 兼容总线）的不可信部分 [推测-供应链]
- 第三方验证工具（JasperGold 形式验证）本身可能是后门载体 [推测-供应链]

**缓解**：内部 code review + 形式验证 + 关键 IP 用开源替代（如 OpenTitan Root of Trust）。

### 5.2 FTC862 自研核 vs 买 ARM 核——哪个更难植入后门？

这是 CISO 评估飞腾的独特视角。**飞腾自研 FTC862 核**（不像华为鲲鹏买 ARM Cortex-A72 现成 IP），这个决策在安全层有两面：

| 维度 | 自研核（FTC862） | 买 ARM 核（如 Cortex-A76） |
|------|:---------------:|:------------------------:|
| **外国植入风险** | ✅ 低（RTL 全在国内团队手里） | ⚠️ 中（ARM 提供 RTL GDS，理论可植入） |
| **自家后门风险** | ⚠️ 不可证否（闭源，外部审不了） | ✅ 低（ARM 是国际公司，有审计声誉） |
| **无意缺陷风险** | ⚠️ 高（自研核历史短，errata 可能多） | ✅ 低（ARM 核经大量客户验证） |
| **国际审计** | ❌ 无（无外部研究者审过 FTC862） | ✅ 有（Cortex 核被学术界反复测） |
| **侧信道研究** | ❌ 几乎空白 | ✅ 大量论文（Spectre PoC 多在 Cortex 上跑）|

**表 4：自研核（FTC862）vs 买 ARM 核安全维度对照。**

**CISO 判断**：自研核**降低了「外国植入」风险面**（这是地缘视角 [Expert_19](../Expert_19_Geostrategy/) 看重的「自主可控」），但**增加了「无人审过」风险面**——FTC862 没有被国际安全社区测过，**可能藏着连飞腾自己都不知道的侧信道缺陷**（类似 Intel 当年不知道有 Meltdown）。**这是「自主可控」与「安全可证明性」的根本张力——E12 与 E19 在此交汇。**

### 5.3 硬件木马审计方法

硬件木马（Hardware Trojan）是植入在 RTL 或 GDS 中的**恶意微电路**，在特定触发条件下（特定输入 pattern、特定时间、特定温度）改变芯片行为。学术界对此有成熟的方法论 [论文-HW-Trojan-Survey]：

```
  硬件木马审计的五大方法（按飞腾适用性）:

  1. 逻辑层审计 (Logic Verification)
     ├─ 形式验证 (JasperGold): 证明 RTL 满足安全属性
     ├─ 等价性检查: 比对设计 vs 出网表 vs GDS, 找未授权改动
     └─ 飞腾适用性: ✅ 内部可做, 外部审不了(RTL闭源)

  2. 侧信道指纹 (Side-Channel Fingerprinting) [论文-FLUSH+RELOAD]
     ├─ 测功耗/延迟/电磁指纹, 与 golden model 比对
     ├─ 木马会增加额外电路 → 功耗/路径延迟有微小偏差
     └─ 飞腾适用性: ✅ 硅后可测, 但需 golden model(飞腾自己有)

  3. 通路激活分析 (Path Sensitization)
     ├─ 生成测试向量, 尽量激活所有内部节点
     ├─ 未覆盖的节点 = 潜在藏木马处
     └─ 飞腾适用性: ⚠️ 取决于 ATPG 覆盖率(见 Expert_17 DFT)

  4. 物理逆向 (Delayering / Optical Inspection)
     ├─ 磨开封装, 逐层拍照, 用机器视觉比对 golden layout
     ├─ 最彻底但破坏性(测完芯片报废)
     └─ 飞腾适用性: ✅ 采购方可抽检(代价高)

  5. 运行时监测 (Runtime Trojan Detection)
     ├─ 部署后持续监测异常行为(隐藏指令/特权后门)
     ├─ 红队尝试触发疑似后门
     └─ 飞腾适用性: ✅ CISO 红队可做(见 §7)
```

**CISO 的诚实结论**：对飞腾 FTC862，方法 1/3 **只有飞腾自己能做**（RTL 闭源），方法 2/4/5 **外部可做但成本高**。**没有一种方法能 100% 证否硬件木马**——这是半导体安全的物理极限。**CISO 的务实态度**：接受「无法 100% 证否」，转而要求**供应链可追溯 + 抽检 + 运行时监测**——把「不可证否」的风险降到「可管理」。

### 5.4 流片 / 封装 / 测试 / 物流阶段

- **流片**：现实工艺节点受出口管制（14nm 级 [推测-出口管制]，与 [Expert_13](../Expert_13_VLSI_Physical/) 一致），**mask 数据不可见 → 代工厂理论可「加料」**。缓解：dual-source（多家代工）+ 硅后逆向抽检。
- **封装 / 测试**：测试程序可能被植入「特殊 pattern」激活后门。缓解：每颗 die 做 unique ID + 区块链/TCM 溯源。
- **物流替换**：真假芯片调包（remark / counterfeit）。缓解：TCM 远程证明 + 供应链溯源。

---

## 6. 量化对标表：D3000M 安全特性全景（核心 artifact）

> 把上述全部汇总成一张安全特性对标表——**这是本视角过「禁止裸断言」门槛的关键 artifact**。

| 安全特性 | 飞腾 D3000M (FTC862, v8.4) | Intel Xeon (Sapp.Rapids) | AMD EPYC (Genoa) | ARM Cortex-X3 (v9) | 华为鲲鹏 920 (v8.2) |
|:--------|:--------------------------|:------------------------|:-----------------|:-------------------|:--------------------|
| **TrustZone / TEE** | ✅ 强制 [官方] | ✅ SGX/TDX | ✅ SEV-SNP | ✅ TrustZone | ✅ TrustZone [官方] |
| **PAuth(指针签名,ROP防护)** | ⚠️ **不确定**(v8.3 OPT) [扩展专题] | ❌(用CET) | ❌(用CET) | ✅ v8.3+ | ⚠️(v8.2 无) |
| **BTI(分支目标识别)** | ❌ **缺失**(v8.5) [推测-v8.4] | ✅ CET-IBT | ✅ CET-IBT | ✅ v8.5+ | ❌(v8.2 无) |
| **MTE(内存标签)** | ❌ **缺失**(v8.5+) [推测] | ❌ | ❌ | ✅ v8.5+ | ❌ |
| **CCA/RME(机密计算)** | ❌(v9才有) [官方-ARM-CCA] | ✅ TDX | ✅ SEV-SNP | ✅ RME | ❌ |
| **Meltdown 免疫** | ✅ 天生 [论文-Meltdown] | ❌(靠KPTI) | ❌(靠KPTI) | ✅ | ✅ |
| **Spectre硬件缓解** | ⚠️ SSBS不确定/无BTI [推测] | ✅ | ✅ | ✅ SSBS+BTI | ⚠️(同v8.x) |
| **Secure Boot** | ✅ ROT→eFuse→逐级签名 [推测] | ✅ Boot Guard | ✅ PSP | ✅ | ✅ [官方] |
| **独立安全子系统** | ❌ 无ME/PSP [推测] | ✅ CSME | ✅ PSP | ❌ | ❌ |
| **SM3/SM4国密** | ✅ **v8.4硬件指令** [实测] | ❌(软件) | ❌(软件) | ✅(v8.4+) | ✅(v8.2?) [官方] |
| **AES/SHA硬件** | ✅ v8.0+ [实测] | ✅ | ✅ | ✅ | ✅ |
| **TPM/TCM度量启动** | ⚠️ 外挂TCM(信创强制) [推测] | ✅ TPM | ✅ TPM | ✅ TPM | ✅ TPM/iBMC |
| **BL31/EL3开源度** | ⚠️ 私有fork [推测] | ❌(在ME里) | ❌(在PSP里) | ✅ TF-A主线 | ✅ 合回主线 [官方] |
| **公开CVE公告渠道** | ❌ 未见 [实测-检索] | ✅ | ✅ | ✅ | ⚠️ |
| **定位结论** | 密码地基强,v8.5防护缺,链不可证 | x86纵深最深 | x86机密计算强 | v9安全标杆 | 中国ARM安全标杆 |

**表 A：D3000M 安全特性量化对标（核心 artifact）。** 来源分级标注于每格。

**这张表的一号读法**：飞腾 D3000M **密码学硬件地基不输任何人**（SM3/SM4/AES/SHA 全有 [实测]），**Meltdown 天生免疫**（ARM 红利）。但在 **v8.5+ 安全扩展（BTI/MTE/PAuth）和机密计算（CCA/RME）两个维度上明确落后**——根因都是**停在 v8.4**（ARM v9 不授中国）。

**二号读法（对飞腾的诚实）**：BTI 缺失 + PAuth 不确定 = **D3000M 的 ROP/JOP 防护比 v8.5+ 竞品弱**——这是 v8.4「卡版本」在安全层的具体税。CISO 部署飞腾时，**必须在应用层补强 CFI（控制流完整性）**，因为硬件层帮不上忙。

---

## 7. 国密 SM2/SM3/SM4 的信任链

```
中国国家标准（GM/T 0002-2012, GB/T 32918/32905/32907）
  ↓ 算法定义
飞腾硬件指令（v8.4 SM3SS1/SM4E 等 9 条 [实测-扩展专题]）
  ↓ 指令实现（RTL）
SM3/SM4 运算单元 → 确定性组合电路 → bit-exact
  ↓ 软件 API
OpenSSL 国密分支 / GmSSL / 国密 TLS
  ↓ 端到端
PKI 证书（CFCA 等 CA 机构）→ 信创合规
```

**飞腾的优势**：
- ✅ 硬件加速（SM4 比 software 快 ~10× [推测]）
- ✅ 国密合规（信创必须，[Expert_06](../Expert_06_Standards_Policy/) 标准视角）
- ✅ 抗侧信道（硬件电路时间确定，非常数时间软件实现更易受 timing attack）

**潜在风险**：
- ❌ 算法设计公开但**实现不公开**（黑盒 RTL）
- ❌ 国密本身在国际加密社区**分析较少**（vs AES/RSA 被 NIST 公开竞赛选中、被全球分析 20 年）
- ❌ **SM2 验签无单条指令**——信任链验签环节或软件或加速器 [实测-无SM2指令]

**CISO 的国密信任判断**：D3000M 的 SM3/SM4 硬件指令是**「中国推动 SM3/SM4 入 ARMv8.4 标准制定博弈」的成果**（[Expert_06](../Expert_06_Standards_Policy/)）——这给了飞腾**别人没有的合规优势**（鲲鹏 v8.2 未必全套）。但「指令在」到「信任链跑通」隔着整条 BL1→内核的工程链（见 [Expert_18](../Expert_18_Firmware_Boot/README.md) §2.5）。

---

## 8. 红队 / 渗透测试建议

> 假设要测试一颗飞腾 D3000M 机器的安全性，红队的六步 SOP：

1. **侧信道测试**：跑 §4.3 的 `spectre_snr_probe.c` + [View_02 cache_timing](../View_02_Security/src/cache_timing.c)，量化 SNR
2. **Spectre POC**：尝试 Spectre v1 POC 读 secret（D3000M 无 BTI，v2 可能更易）
3. **TrustZone 测试**：尝试越界访问 Secure World / 构造恶意 SMC
4. **JTAG / 调试**：尝试通过 JTAG 读 Secure Memory（飞腾应有 JTAG 锁 + eFuse 熔断）
5. **固件分析**：dump TF-A / UEFI，看有没有签名、BL31 banner 是什么版本（接 [Expert_18](../Expert_18_Firmware_Boot/README.md) §2.11 `boot_chain_probe.sh`）
6. **硬件木马探测**：跑 §5.3 方法 5——尝试触发疑似隐藏指令 / 特权后门（功耗侧信道指纹比对）

---

## 9. CISO 治理深化：合规框架与事件响应

### 9.1 企业部署飞腾的安全 checklist

- [ ] 启用 ARM TrustZone + 部署 OP-TEE
- [ ] 安装所有 Spectre 缓解补丁（接受 5–15% 性能税）
- [ ] 启用 Secure Boot + Measured Boot（TCM 2.0 PCR 扩展）
- [ ] 部署磁盘加密（国密 SM4 + LUKS）
- [ ] 启用 TCM（飞腾外挂或片上）
- [ ] 关闭未用接口（JTAG / UART / USB-OTG）+ eFuse 熔断调试口
- [ ] 配置 SELinux + AppArmor（**补强 CFI，因 D3000M 无 BTI/PAuth**）
- [ ] 定期审计固件版本（飞腾安全公告——**若无公告渠道，手动跟踪 EDK2 上游 CVE**）
- [ ] 启用 auditd + log aggregation
- [ ] 网络隔离 + zero-trust 架构
- [ ] **应用层部署 CFI（如 Clang CFI / Shadow Stack）**——因硬件 BTI/MTE 缺失
- [ ] **红队年度演练**（跑 §8 六步 SOP）

### 9.2 合规框架：等保 2.0 / GB 标准

中国 CISO 评估飞腾服务器，绕不开**等保 2.0（GB/T 22239-2019）**——网络安全等级保护。安全保护等级分五级，**三级**是「重要业务系统」的常见门槛：

| 等保 2.0 要求域 | D3000M 能力对照 | CISO 判断 |
|:--------------|:---------------|:---------|
| 安全物理环境 | 国产 CPU + TCM 溯源 | ✅ 信创加分 |
| 安全通信网络 | SM4 加密 / 国密 TLS | ✅ 硬件加速 |
| 安全计算环境 | TrustZone / SM3 度量 | ✅ 地基在 |
| **可信验证(三级新增)** | **TCM 2.0 度量启动 + 远程证明** | ⚠️ **取决于飞腾是否集成 TCM** |
| 安全管理中心 | BMC 带外 + SELinux | ⚠️ 飞腾 BMC 成熟度待证(接 [Expert_23](../Expert_23_Server_RAS/README.md) §2.9) |

**判断**：D3000M **硬件地基支撑等保三级合规**（TrustZone + 国密 + TCM 度量），但「可信验证」和「安全管理中心」两个**新增域**取决于飞腾的 TCM 集成深度与 BMC 成熟度——这两块公开信息不透明 [推测-合规待证]。**「能过等保三级」≠「自动过」——需要采购方 + 飞腾共同做集成验证。**

### 9.3 事件响应（IR）：固件级持久化怎么清？

CISO 最怕的场景：**攻击者拿到 BL31/UEFI 级持久化**——重装 OS 清不掉。NIST SP 800-61 的事件响应四阶段 [标准-NIST-IR] 应用到飞腾：

```
  准备 → 检测分析 → 遏制根除 → 恢复
   │       │           │          │
   TCM度量   异常SMC    物理重刷    重度量
   基线建立   固件行为    固件SPI     PCR比对
              偏离        Flash
              │
   ★ 关键难点: 遏制根除阶段, 若后门在 BL31(EL3),
     重刷固件需飞腾签名包——没有飞腾配合, CISO 清不掉 EL3 后门 ★
```

**CISO 的 IR 红线**：① 部署前先用 TCM 建立固件度量基线（PCR 值），出事时比对能发现篡改；② **要求飞腾提供固件重刷工具 + 签名更新包**（否则 EL3 后门无解）；③ 若飞腾不提供 → 只能物理换 SPI Flash 芯片（拆机级恢复，代价极高）。

---

## 10. 设计决策评估：飞腾哪些决策认可 / 哪些该改

**认可的决策**：
1. **自研 FTC862 核而非买 ARM 核**——降低「外国植入」风险面（地缘安全红利）。代价是「无人审过」（§5.2），但信创语境下自主可控优先。
2. **SM3/SM4 入 ARMv8.4 硬件指令**——国密合规的硬件红利，别人没有的差异化（[Expert_06](../Expert_06_Standards_Policy/)）。
3. **用 mask ROM + eFuse 作 ROT**——ARM 标准方案，简单可审计，没去自研「飞腾版 ME」（ME 本身是攻击面）。

**该改的决策**：
1. **【最高优先】公开 ServerReady 认证 + SBSA ACS 测试报告**——认证不透明 = 进不了开放市场。
2. **【最高优先】BL31 平台代码合回 TF-A 主线**——零 RTL 泄露，立即让 EL3 可审计（[Expert_18](../Expert_18_Firmware_Boot/README.md) §3 最核心建议）。
3. **【高优先】建立 CVE 公告渠道**——「没有 CVE 公告」不是没漏洞，是没人在审。
4. **【高优先】明确 PAuth / SSBS 是否实现**——若实现了 v8.3/v8.5 可选扩展，公开声明；若没实现，下一代（D4000）必补 BTI/SSBS/MTE。
5. **【高优先】提供固件重刷工具 + 签名更新包**——让 CISO 能清 EL3 后门（§9.3 IR 红线）。

---

## 11. 这一视角的盲区与反方（诚实段，强制）

> 宪法 §4.3 第 2 条要求：敢说这一视角看不见什么、会误导什么。杜绝软文。

**盲区 1：CISO 视角会高估「信任链可审计」对采购的权重。** 本视角通篇比「BL31 开不开源、RTL 审不审得了」，但**信创采购的决策逻辑里，『自主可控 + 国产供应链』往往压倒『可审计』**——一个闭源 BL31，对采购方而言「反正都是国产，自主可控」，并不一票否决。**反方**：政府/国企信创采购更关心「能不能国产替代、有没有 TCM」——这些飞腾做到了。本视角若被用来「否定飞腾进信创」，是用开放市场标准套信创市场，过度解读。

**盲区 2：CISO 视角天然有「安全越全越好」的职业偏见。** 把缓解全开（5–15% 性能税）+ Measured Boot + CFI 全堆——**对高吞吐场景（内存数据库），这套安全配置的吞吐代价不可忽视**。**反方**：性能视角（[Expert_09](../Expert_09_Performance_Model/)）会问「全开 vs 默认差多少」，答案常常是「够痛」。本视角主张的缓解策略需与性能视角协商。

**盲区 3：本视角大量结论标 [推测]，本身有不确定性。** D3000M 的 BL31 实现、PAuth/SSBS 有没有、ServerReady 认证、国密信任链签名算法——**我没有一手逆向证据，全是「公开不披露」+「ARM 标准做法」推出来的**。**反方**：飞腾内部可能早已做到——只是信创供应链「闷头做、不宣传」。本视角的「⚠️/❓」**应被读作「需采购方核实」，而非「一定不支持」**。

**盲区 4：「无 ME/PSP」是双刃剑，本视角不应单边批评。** 我说「飞腾无独立安全子系统 = 少一层纵深」，但 **Intel ME 本身是巨大攻击面**（Positive Technologies 系列研究证明 ME 可被攻破）——「多一层纵深」也可能是「多一层攻击面」。**飞腾无 ME，既是弱点（少纵深）也是优点（少攻击面）**。ARM「轻 ROT」哲学反而更干净。

**盲区 5：CISO 视角偏「威胁中心论」，低估了「飞腾没人打」的现实概率。** 把 Spectre / 硬件木马 / 固件后门列得头头是道，但**实际针对飞腾服务器的定向攻击极少**——攻击者更爱打 x86（量大、工具多）。**反方**：这不是「飞腾更安全」，是「飞腾还不够普及到值得被专门打」。随着信创规模扩大，这个「护城河」会消失。

---

## 12. 与其他视角对偶（一致 / 冲突，强制）

> 宪法 §4.3 第 3 条要求：指明与其他视角的一致与冲突。

| 对偶视角 | 一致 / 冲突 | 具体点 |
|:--------|:--------:|:------|
| **Expert_18 固件** | ✅ **强一致** | E18 §2.7「BL31 闭源 = EL3 黑箱」是 E12 §3.2 信任链灰色地带的根因。**E12 说「RTL 闭源无法审计」，E18 把这话具体到 BL31/EL3 这层**——后者安全后果更直接。两者是同一断层的两面。 |
| **Expert_23 服务器 RAS** | ✅ **一致** | RAS 错误上报通路（GHES/APEI）由 BL31 实现，E23 §2.9 的「软件栈待证」根因在 E18 BL31。**安全与可靠共享同一条 EL3 通路**——BL31 一坏，RAS 和安全同时塌。 |
| **Expert_06 标准政策** | ✅ **一致** | SM3/SM4 入 ARMv8.4 是中国推动标准制定博弈的成果（E06），E12 §7 国密信任链是这个成果在安全层的落地。**E06 是「为什么有国密指令」，E12 是「国密指令安不安全」**。 |
| **Expert_19 地缘** | ⚠️ **张力** | 地缘视角看重「自主可控 = 自研核降低外国植入风险」，安全视角补一刀「自研核 = 无人审过 = 自家后门不可证否」。**同一事实（自研 FTC862），两视角一褒一贬——这是「自主可控」与「安全可证明性」的根本张力。** |
| **Expert_03 硬件设计** | ✅ 一致 | 安全机制（TrustZone/PAuth/BTI）要 RTL 实现。E03 设计视角决定「选哪些安全 IP」，E12 安全视角评估「这些 IP 够不够、缺了什么」。**E12 发现「缺 BTI/SSBS」= 给 E03 下一代设计的硬需求。** |
| **Expert_04 OS Kernel** | ✅ 一致 | OS 视角的内核 `mitigations` 决定 D3000M 真实安全等级（E12 §4.2 命令行控制）。**硬件缺 BTI，靠内核软件补——E04 是 E12 安全策略的执行层。** |
| **Expert_21 AI 定位** | ⚠️ 部分冲突 | AI 视角要「能跑大模型」，安全视角要「缓解全开」——缓解有性能税。但**更深一致**：D3000M 无 BF16/I8MM/SVE（E21）与无 BTI/MTE（E12）是**同一个根因（ARM v9 不授中国 → 停在 v8.4）**。 |
| **Expert_09 性能** | ⚠️ **冲突** | 性能视角要「关缓解省 5–15%」，安全视角要「全开」。**这是经典的安全 vs 性能权衡**，CISO 与性能工程师永远在吵。 |

---

## 13. 参考文献（≥15，分级标注）

### 论文（顶会 / arXiv，本视角核心依据）

- [论文-Spectre] **Kocher, P. et al.**, "Spectre Attacks: Exploiting Speculative Execution," *IEEE S&P (Oakland) 2019*. —— **Spectre v1/v2 原始论文**，§4 缓解状态矩阵依据。
- [论文-Meltdown] **Lipp, M. et al.**, "Meltdown: Reading Kernel Memory from User Space," *arXiv:1801.01207, 2018*. —— **Meltdown 原始论文**，§4 ARM 免疫依据。
- [论文-FLUSH+RELOAD] **Yarom, Y. & Falkner, K.**, "FLUSH+RELOAD: a High Resolution, Low Noise, L3 Cache Side-Channel Attack," *USENIX Security 2014*. —— **Cache 侧信道经典方法**，§4.3 SNR 探测 + §5.3 硬件木马侧信道指纹依据。
- [论文-Survey] **Ge, Q. et al.**, "A Survey of Microarchitectural Timing Attacks and Countermeasures on Contemporary Hardware," *ACM Computing Surveys, 2018*. —— **微架构侧信道综述**，§2 威胁模型分类依据。
- [论文-Spectre-BHB] **Canella, M. et al.**, "Spectre-BHB / Cross-Branch History Injection," *IEEE S&P 2022 (CVE-2022-23960)*. —— §4 Spectre-BHB 依据。
- [论文-Retbleed] **Wikner, J. & Gruss, D.**, "Retbleed: Arbitrary Speculative Code Execution," *USENIX Security 2022*. —— §4 Retbleed（主要影响 x86）依据。
- [论文-Downfall] **Moghimi, D.**, "Downfall: Exposing Speculative Data Leaks via AVX Instructions," *USENIX Security 2023 (CVE-2022-40982)*. —— §4 Downfall（x86 专有，ARM 免疫）依据。
- [论文-HW-Trojan-Survey] **Tehranipoor, M. & Koushanfar, F.**, "A Survey of Hardware Trojan Taxonomy and Detection," *IEEE Design & Test of Computers, 2010*. —— **硬件木马审计方法论经典综述**，§5.3 五大审计方法依据。
- [论文-LogoFAIL] **Binarly.io**, "LogoFAIL: Vulnerabilities in UEFI Image Parsers," *Black Hat Europe 2023*. —— §2.3 固件是「重装清不掉」的攻击面依据。

### 标准（国际 / 国密）

- [官方-ARM-TFA] **ARM**, *Trusted Firmware (TF-A) Design Docs* + *Trusted Board Boot Requirements (TBBR)*. —— §3.2 信任链逐级签名依据。
- [官方-ARM-TrustZone] **ARM**, *ARM Security Technology — TrustZone* (ARM DHI 0092). —— §3.1 TrustZone 两世界依据。
- [官方-ARM-CCA] **ARM**, *Confidential Compute Architecture (CCA) / Realm Management Extension (RME)*, 2021+. —— §3.3 CCA/RME 依据。
- [标准-UEFI] **UEFI Forum**, *UEFI Specification* 2.x（Secure Boot PK/KEK/db 章节）. —— §3.2 UEFI Secure Boot 依据。
- [标准-NIST-IR] **NIST**, *SP 800-61: Computer Security Incident Handling Guide*. —— §9.3 事件响应四阶段依据。
- [标准-NIST-PFR] **NIST**, *SP 800-193: Platform Firmware Resiliency (PFR)*. —— §3 固件恢复依据。
- [标准-GB-等保] **GB/T 22239-2019**, *信息安全技术 网络安全等级保护基本要求（等保 2.0）*. —— §9.2 等保合规依据。
- [标准-GB-TCM] **GB/T 29829**（可信计算密码支撑平台）+ **GM/T 0012**（TPCM）+ **GB/T 37092**（密码模块安全）. —— §9.2 TCM/可信计算依据。
- [标准-GB-SM] **GB/T 32918**（SM2）+ **GB/T 32905**（SM3）+ **GB/T 32907**（SM4）. —— §7 国密三件套依据。

### 资源 / 项目内引用

- [资源] <https://spectreattack.com/> —— Spectre/Meltdown 跟踪站。
- [资源] <https://downfall.page/> —— Downfall 详情。
- [资源] <https://www.lockheedmartin.com/cyber/kill-chain> —— Lockheed Cyber Kill Chain® 框架。
- [项目内] [`Expert_18_Firmware_Boot/README.md`](../Expert_18_Firmware_Boot/README.md) §2.4/§2.7 —— **信任链逐级还原 + BL31 闭源风险**（E12 §3 的固件侧根因）。
- [项目内] [`Expert_23_Server_RAS/README.md`](../Expert_23_Server_RAS/README.md) §2.9 —— **RAS 错误上报通路与安全共享 EL3/BL31**。
- [项目内] [`扩展专题.md`](../扩展专题.md) §1 第 22/23 项（SM3/SM4）+ 第 17 项（PAuth ⚠️）—— D3000M 安全特性实测矩阵。
- [项目内] [`View_02_Security/`](../View_02_Security/) —— cache timing POC（§4.3 侧信道探测基础）。
- [项目内] [`Expert_06_Standards_Policy/`](../Expert_06_Standards_Policy/) —— SM3/SM4 入 ARMv8.4 的标准制定博弈。

---

## 14. 延伸阅读（项目内 + 外部）

**项目内**：
- [`Expert_18_Firmware_Boot/README.md`](../Expert_18_Firmware_Boot/README.md) —— **信任链的固件侧全链路**（BL1→BL31→UEFI→内核），E12 §3 的深度前置。
- [`Expert_23_Server_RAS/README.md`](../Expert_23_Server_RAS/README.md) §2.9 —— RAS 与安全共享 EL3 通路。
- [`Expert_19_Geostrategy/`](../Expert_19_Geostrategy/) —— 自主可控 vs 安全可证明性的地缘张力。
- [`Expert_06_Standards_Policy/`](../Expert_06_Standards_Policy/) —— 国密入标的政策博弈。

**外部**：
- ARM CCA / RME Specifications（机密计算下一代）。
- NIST SP 800-193（Platform Firmware Resiliency）+ SP 800-61（Incident Response）。
- Kocher "Spectre" (S&P 2019) + Lipp "Meltdown" (arXiv 2018) + Yarom "FLUSH+RELOAD" (USENIX 2014)。
- Tehranipoor "Hardware Trojan Survey" (IEEE D&T 2010)。
- GB/T 22239（等保 2.0）+ GB/T 32918/32905/32907（国密）+ GB/T 29829（TCM）。

📌 **下一步**：本视角（E12 安全 CISO）与 [Expert_18](../Expert_18_Firmware_Boot/README.md)（固件信任链）、[Expert_23](../Expert_23_Server_RAS/README.md)（服务器 RAS）构成**安全-固件-可靠三角**——三者共享 EL3/BL31 这条命脉。

---

## § 安全分析方法论与资源（不只飞腾，给所有安全工程师/CISO）

> 本章把 E12 的飞腾安全分析上升为**任何安全工程师都可复用的方法与资源**。飞腾是案例锚点（国密合规/侧信道），方法普适。通用资源见 [`领域资源库.md`](../领域资源库.md)。

### 方法论一：威胁建模框架（系统化识别威胁）

| 框架 | 适用场景 | 核心思路 |
|------|---------|---------|
| **STRIDE**（Microsoft）| 系统设计阶段 | 6 类威胁：Spoofing/Tampering/Repudiation/Info Disclosure/DoS/Elevation |
| **攻击树**（Attack Tree）| 特定资产 | 根=攻击目标，叶=具体手段，标注代价/概率 |
| **PASTA**（7 步）| 风险驱动 | 对齐业务目标 → 资产 → 威胁 → 漏洞 → 攻击模拟 |
| **Kill Chain**（Lockheed）| 入侵检测 | 7 阶段：侦察→武器化→投递→利用→安装→C2→行动 |

### 方法论二：硬件侧信道分析框架（CPU 安全核心）

2018 后侧信道成体系结构安全主线，分析框架：
1. **时序侧信道**（Flush+Reload/Prime+Probe）：cache 访问时间泄露秘密
2. **推测执行侧信道**（Spectre v1/v2/v4/RSB/MDS/LVI）：推测执行访问秘密后侧信道泄露
3. **瞬态执行**（Meltdown/Foreshadow/ZombieLoad）：越权读后侧信道
4. **缓解谱系**：retpoline（Spectre v2）、IBRS/STIBP、SSBS（飞腾 v8.5）、speculative fence

### 安全专属资源

- **漏洞库**：**CVE/NVD**（nvd.nist.gov）、CWE（弱点分类）、CAPEC（攻击模式）
- **侧信道论文谱系**：Yarom "FLUSH+RELOAD"(USENIX 2014) → Kocher "Spectre"(S&P 2019) → Lipp "Meltdown"(2018) → 后续 MDS/VRIDL/LVI 系列
- **硬件安全标准**：**Common Criteria**(ISO 15408)、FIPS 140-3（密码模块）、GB/T 22239（等保 2.0）
- **工具**：**scan-build/CodeQL**（静态分析）、**AFL/libFuzzer**（模糊测试）、**Spectre 检测**（speculator/ozel）、侧信道 PoC 库
- **权威书**：Kocher《Cryptography and Secure Design》、Saileshwar《Hardware Security》

### 给安全工程师/CISO 的通用建议

1. **威胁建模先于防护**：不做 STRIDE 就堆防护 = 砸钱无重点。
2. **侧信道是 CPU 时代必修**：2018 后任何 cache/推测执行都可能泄露，需评估缓解开销。
3. **密码学用成熟库，别自造**：AES/SHA 用 OpenSSL/mbedTLS，自造易引入时序侧信道。
4. **国密合规是双刃剑**：中国市场 SM3/SM4 必需，但要兼顾国际互操作（TLS 双栈）。
5. **信任链要完整**：从 ROM → BL31 → OS → App，任何断点都是攻击面（飞腾案例见 E18）。
6. **安全 vs 性能永恒 trade-off**：retpoline 降 5-30% 性能，CISO 要量化告知业务方成本。

---

回到 [Views.md](../Views.md) 看完整视角矩阵，或 [README.md](../../README.md) 看主入口。
