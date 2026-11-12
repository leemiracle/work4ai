# 12 · libspdm 安全协议栈与 swref 硬件参考头：驱动的"信任根"与"寄存器字典"

> 仓库 @ 615.71.09。本篇覆盖 `src/nvidia/src/libraries/libspdm/`（注意：实际路径非 `src/lib/spdm/`）与 `src/common/inc/swref/`（16 目录 429 头），连带 RM 集成层 `src/nvidia/src/kernel/gpu/spdm/`。

## 一、角色定位：一对"底座"——一个管信任，一个管地址

**SPDM**（Security Protocol and Data Model，DMTF 标准）是驱动与 GPU 之间的设备认证与安全会话协议。在 Hopper 及之后的机密计算（Confidential Computing）GPU 上，它是信任链的起点：驱动（Requester）向 GPU 内的 SPDMResponder 证明自己、GPU 向驱动证明自己是"签过名的真卡"（证书链），随后建立加密会话派生密钥——CC 模式的显存加密密钥派生（keystore）与远程证明（attestation report）都挂在这条会话上。仓内实现是**开源 libspdm 3.5.0 的 vendor 快照 + NVIDIA 内核适配层**，版本号即目录名。

**swref**（software reference）是硬件寄存器参考头的谱系库：从各代芯片手册生成的 `dev_*.h`（设备寄存器偏移/位域定义），按代际（kepler→rubin）与芯片变体分目录。RM 与 NVSwitch 代码里每一个寄存器名到地址的解析都源自这套头。它与 open-gpu-doc 仓的手册文本是同源异构——那边人读，这边编译器读。

两者放一篇的理由：它们都是"驱动不自己发明、只做忠实消费"的层——密码学协议交给上游库，寄存器语义交给生成头。

## 二、内部结构

**libspdm 三层 + 适配层**（`src/nvidia/src/libraries/libspdm/`）：

```
3.5.0/
├── include/            # 第一层：头
│   ├── industry_standard/  # SPDM 规范头（消息格式/能力字/证书槽）
│   ├── hal/                # 平台移植面
│   └── internal/ library/
├── library/            # 第二层：实现
│   ├── spdm_common_lib/        # 上下文/会话/密码服务（libspdm_com_context_data*.c）
│   ├── spdm_requester_lib/     # 请求方状态机（本仓只用这个角色）
│   ├── spdm_crypt_lib/         # 算法协商与验签
│   └── spdm_secured_message_lib/  # 会话加密封装
└── os_stub/            # 第三层：OS 空桩（platform_lib_null/memlib...）
nvidia/                 # NVIDIA 适配层（9 文件 + openspdm.mk）
    nvspdm_malloclib.c / memlib / debuglib / rng / rsa / crypt_null /
    nvspdm_cert.c / nvspdm_cryptlib_extensions.h / nvspdm_rmconfig.h
```

适配的核心是 `nvspdm_rmconfig.h`：以宏覆盖上游 `spdm_lib_config.h` 的默认配置（构建时 `LIBSPDM_CONFIG` 进 CFLAGS 完成替换，文件头注释明言），例如 `LIBSPDM_FIPS_MODE 0`——注释直白记录了原因："chips_a doesn't get the latest mbedtls yet"（内部 mbedtls 未跟上 FIPS 140-3 所需算法，先关）。openspdm.mk（:23-25 说明"allows for the compilation of the libspdm open-source library, in order to implement an SPDM Requester in RM"）逐文件列出要编的上游源并注入 nvspdm_* 的内存/日志/随机数钩子——内核态没有 libc，os_stub 的空桩全部由 nvidia 层填成 portMem/portAtomic 实现。

**RM 集成层**（`src/nvidia/src/kernel/gpu/spdm/`）：`spdm.c`（1233 行，Spdm 对象主体：上下文生命周期 `_spdmClearContext` :73、会话建立 `spdmEstablishSession_IMPL` :1208 内联 `spdmCheckRequesterIdValid`→`spdmContextInit`→`spdmStart`（:589）三步、传输缓冲管理 `_spdmReleaseTransportBuffer` :65）+ `kernel_spdm.c`（151 行）+ 代际证书 HAL：`arch/blackwell/spdm_certs_gb100.c`、`arch/hopper/spdm_certs_gh100.c`、`arch/rubin/spdm_certs_gr100.c`（GB100 头部定义 `NV_GB100_SPDM_REQUESTER_CERT_COUNT (3)`，并留 TODO"CONFCOMP-1965 - Add GB100 Mutual Auth Cert"——双向认证尚在补）。证书数据本身在第 10 篇的 bindata 族（17 个 L1/L2/L3 IndividualCertificate 生成文件）。

**swref 谱系**（`src/common/inc/swref/published/`，按目录头数）：blackwell **103**、nvswitch **99**、ampere 48、turing 38、hopper 34、rubin 28、maxwell 26、pascal 15、volta 12、ada 8、disp 7、br04/br03/pcie_switch/t23x/kepler 各 1-3——共 429。GPU 主线十一代从 kepler 一路到 rubin（下一代），blackwell 目录内再分芯片变体（gb100/gb102/gb10b/gb110/gb112/gb202/gb20b/gb20c）。头命名 `dev_<块>.h`：`dev_pmc.h`（主控）、`dev_fb.h`（帧缓冲）、`dev_mmu.h`、`dev_pbdma.h`（PBDMA 推送单元）、`dev_fault.h`（故障）、新代多出 `dev_fsp_pri.h`（FSP 私有寄存器接口）、`dev_fuse_zb.h`（零化熔丝）等。顶层另有 `common_def_nvlink.h`（NVLink 公共定义）。

## 三、外部连接

SPDM 线的上游消费者是**机密计算**：`conf_compute/conf_compute_api.c:360` 起——`confComputeIsSpdmSupported && PDB_PROP_SPDM_ENABLED` 时调 `spdmGetAttestationReport`（带 nonce、双报告槽：GPU attestation + CEC attestation），**失败即 `confComputeSetErrorState` 拆掉整个 CC 系统**——证明失败比无证明更糟，直接停机。密钥派生线（keystore）与 GSP 引导线（kernel_gsp_gh100.c）同样引 libspdm 头；全仓 include libspdm 的七个文件里三个是 spdm 自家、四个是 conf_compute/keystore/gsp——SPDM 是它们共同的前置。

swref 的消费方式是纯 include：如 `kernel_oob_gb100.c:38` 的 `#include "swref/published/blackwell/gb100/dev_oob_pri.h"`。注意开源仓内直接引用 swref 的内核侧文件不多——**寄存器头的大户是 GSP 固件构建**（RM 主体已在固件里），开源仓内只见少量外设管理代码（OOB 等未迁固件的块）在用；swref 全量随仓发布更多是"参考完整性"而非开源构建依赖。swref 同时被第 8 篇的 NVSwitch 库消费（nvswitch/ 子目录 99 头，lr10/ls10 寄存器定义在此，如 `nvswitch/ls10/dev_nvlsaw_ip.h`，见 tnvl_ls10.c 的 include）。

## 四、数据流

**SPDM 会话建立**（`spdmEstablishSession`，spdm.c:1208）：
1. `spdmCheckRequesterIdValid`——本机 requester 身份合法；
2. `spdmContextInit`——初始化 libspdm 上下文（挂 nvidia 适配钩子）；
3. `spdmStart`（:589）——跑 SPDM 标准握手序列：GET_VERSION → GET_CAPABILITIES → NEGOTIATE_ALGORITHMS → GET_DIGESTS/GET_CERTIFICATE（拉 GPU 证书链 L3→L2→L1）→ CHALLENGE（GPU 证明私钥在场）→ KEY_EXCHANGE（Diffie-Hellman 建会话密钥）→ 结束事件（FINISH）。
此后 attestation 请求走 `spdmGetAttestationReport`（GET_MEASUREMENTS 封装，nonce 防重放），会话密钥供 keystore 做 CC 密钥层级派生。传输层经 RM 的 SPDM 通道（消息缓冲 `_spdmReleaseTransportBuffer` 管理）直达 GPU 上的 responder 微控制器。

**swref 数据流是编译期的**：头里的 `#define NV_..._ADDR`/位域宏经 `DRF_DEF` 宏体系（RM 通用位域工具）展开成移位掩码表达式，内核读寄存器 = `GPU_REG_RD32(pGpu, NV_PMC_...)` 一类宏的常量折叠——零运行时开销，代价是代际正确性全靠 include 路径选择（blackwell 代码绝不 include ampere 头）。

## 五、设计决策

1. **vendor 树零改动**：3.5.0/ 目录保持上游原样（升级=换目录），全部适配集中在 nvidia/ 九文件。这是大型内核项目消费第三方库的健康姿势——diff 上游一目了然。
2. **只编 Requester**：openspdm.mk 只挑 requester 相关源编入（GPU 端 responder 在固件/硬件）。驱动的角色定位单一，减小攻击面与体积。
3. **配置覆盖走编译宏**：LIBSPDM_CONFIG 替换而非 patch 上游配置头，且 `LIBSPDM_CHECK_MACRO 1` 自检宏组合合法性（nvspdm_rmconfig.h:31-35 注释）——宏覆盖错了编译期就炸。
4. **FIPS 未达先显式关闭**：FIPS 140-3 模式因 mbedtls 版本缺口置 0 且注释追踪 TODO——不伪装合规，留审计线索。
5. **swref 生成谱系化**：手册→头的生成链保证与 open-gpu-doc 同步；按代际+变体分目录让驱动代码的 include 路径即文档（见 include 就知道目标芯片）。11 代 GPU 全量保留（连只有 1 个头的 kepler/t23x 也是）——老代硬件的驱动分支还在维护，字典不能抽页。
6. **证书三件套分离**：代码（arch/spdm_certs_*.c HAL）+ 数据（bindata L1/L2/L3）+ 校验（libspdm 上游）三层分离，换证书不碰逻辑，换芯片只加 arch 文件。

## 六、新人提示

- **读码顺序**：spdm.c 的 `spdmEstablishSession`（:1208，30 行看全三步）→ conf_compute_api.c:350-375（唯一重量级消费者）→ nvidia/nvspdm_rmconfig.h（全部编译期决策）；libspdm 上游 library/ 除非做协议改动不必进——DMTF 规范配 industry_standard/ 头读更高效。
- **SPDM 黑话**：Requester=驱动侧；Responder=GPU 侧；L1=Root CA 自签、L2=AK CA、L3=设备证书（链 L3←L2←L1）；CEC=CC Execution Environment（机密执行环境）attestation 是 GPU 环境的补充证明。
- 查寄存器位域：先确定芯片目录（blackwell/gb202 这类），再按块名找 dev_*.h；swref 头与 open-gpu-doc 手册页码可互查（头内注释保留手册路径）。
- swref 头**没有版本号命名空间**：不同代的同名头位域含义可能漂移，跨代 include 混用是经典编译期隐性 bug——HAL 目录纪律（arch/<代>/）是唯一防线。
- 调 SPDM 失败：开 `LIBSPDM_DEBUG_PRINT_ENABLE`（nvspdm_rmconfig.h 默认 0，改 1 需重编 blob——开源构建不可达，实际排查靠 RM 的 SPDM 状态码与 confCompute 错误态）。
- 与第 10 篇的呼应：GSP 固件是 CC 镜像（ConcatenatedFMC）时，SPDM 会话在其加载路径之前——先有信任根，后有固件，这就是 KGSP storage HAL 里 CC 分支（kernel_gsp_gb100.c:126-153）与本篇会话建立的时序关系。

---

**本篇甄别备注**：任务描述路径 `src/lib/spdm/` 实际为 `src/nvidia/src/libraries/libspdm/`；"三层（官方头库/实现/nvidia 适配）"实况为 `3.5.0/{include,library,os_stub}` 三目录 + 平级 `nvidia/` 适配层共四块；"六代际谱系"实测 swref 为 11 个 GPU 代际目录（kepler/maxwell/pascal/volta/turing/ampere/ada/hopper/blackwell/rubin/t23x）另加 nvswitch/br03/br04/disp/pcie_switch，共 429 头，文中按实测口径表述。
