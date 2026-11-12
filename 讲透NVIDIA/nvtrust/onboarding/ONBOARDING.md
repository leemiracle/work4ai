# nvtrust Onboarding（NVIDIA GPU/NVSwitch 信任验证）

> 依据：仓内图谱 `.understand-anything/knowledge-graph.json`（584 节点/993 边/12 层/14 步导览，validator 0 issues，fingerprints 245 文件 @ a8090b65）+ 全部锚点源码复核（`onboard-input.json` 145KB）。
> 行号锚均为本仓源码实证，抓取于 2026-11。

---

## 一、nvtrust 是什么：机密计算时代的设备证明工具集

nvtrust 解决的问题是：**虚拟机/容器里的工作负载如何确信自己用的 GPU 和 NVSwitch 处于可信状态**（固件未被篡改、CC 模式已开启、拓扑未被替换）。仓库 `README.md` 给出全景：guest_tools 为主力（attestation_sdk 证明 SDK、gpu_verifiers/local_gpu_verifier GPU 本地验证器、ppcie-verifier 两代 PCIe 拓扑证明器、rims RIM 服务占位），host_tools 与 infrastructure 支撑宿主侧可信执行环境（KVM 透传脚本 `host_tools/sample_kvm_scripts/launch_vm.sh`、`prepare_vm.sh`；内核补丁 `infrastructure/patches/linux/iommu_pagefault.patch` 与 `iommu_pagesize.patch`——pDMLUS 机密互连的 IOMMU 分页依赖）。

guest_tools 六个子目录的真实形态（实证）：`attestation_sdk`（证明 SDK）、`attestation_sdk_cpp`（**空目录占位，0 文件**）、`gpu_verifiers/local_gpu_verifier`（GPU 本地验证器）、`ppcie-verifier`（当代 PCIe 验证器）、`ppcie-verifier-sdk-cpp`（C++ SDK 版验证器）、`rims/rim_service`（仅 README 占位）。治理面在根：`CONTRIBUTE.md`、`SECURITY.md`、`pytest.ini`、issue 模板与 stale workflow。

## 二、验证的信任模型：三方证据 + 黄金度量比对

所有验证器共用一条信任链：**设备证书链（设备身份）→ SPDM 度量证明报告（当前固件状态）→ RIM 参考完整性度量（应然状态）→ 比对产出 EAT claims**。

- **证书链**：GPU 侧 `local_gpu_verifier/src/verifier/nvml/__init__.py` 的 `NvmlHandler`（class@74）经 NVML 取证据：`get_attestation_cert_chain:243`、`get_attestation_report:252`、`get_gpu_architecture:260`、`get_cc_feature:368`、`get_gpu_ready_state:165`、`get_driver_version:219`、`get_uuid:227`、`get_vbios_version:235`。信任锚是本地 PEM：`certs/verifier_RIM_root.pem`（RIM 根）与 `certs/verifier_device_root.pem`（设备根）。
- **SPDM 报文**：`attestation/__init__.py` 的 `AttestationReport`（class@53）承载证明报告——`extract_response_message:63`/`extract_request_message:78` 拆请求响应、`concatenate:94` 拼接待签数据、`verify_signature:117` 验签、`get_measurements:151` 取度量。位级解析在 `spdm_msrt_resp_msg.py`（758 行四类）：`DmtfMeasurement:40`、`MeasurementRecord:148`、`OpaqueData:258`（NVIDIA 专有扩展字段：`parse_switch_pdis:345`、`parse_feature_flag:365`、`parse_chip_info:379`、`parse_measurement_count:321`——超出 DMTF SPDM 标准字段）、`SpdmMeasurementResponseMessage:456`；请求侧对应 `spdm_msrt_req_msg.py`。
- **RIM**：`rim/__init__.py`（547 行）`RIM` 类（class@64）做 `read:105`→`parse_schema:138`（XSD 校验，schema 在 `rim/signSchema.xsd` 等）→`validate_schema:185`→`extract_certificates:230`，黄金度量模型 `golden_measurement.py`（组件/索引/值/替代项）。

## 三、local_gpu_verifier：GPU 本地验证主线

编排入口 `cc_admin.py`（683 行，CLI 主程序）：`main:95`→`attest:314` 驱动"证据采集→证书链验证→OCSP→RIM 比对→EAT claims 生成"全流程；支撑函数库 `cc_admin_utils.py`（616 行，FWID 提取/证书链与 OCSP 验证/RIM 获取）。比对核心 `verifier.py`：`Verifier` 类（class@42）`verify:47` 把运行时 GPU 度量与 RIM 黄金度量逐项比对（`:62` 空黄金度量告警）。

配置与异常是两个"大件"：`config.py`（651 行）的 `class BaseSettings:59` **是手写类而非 pydantic**（勘误见 README），承载 OCSP/RIM 服务端点、nonce、SKU 全部可变状态；架构分派 `HopperSettings:581`/`BlackwellSettings:613`，注册表 `GPU_ARCHITECTURE_MAP[9]=Hopper:650`、`[10]=Blackwell:651`。`exceptions/__init__.py` **41 个异常类**（Error 基类派生的证明/RIM/证书/NVML 全域层次，全仓最大异常产地），`exceptions/utils.py` 的 `is_non_fatal_issue` 区分可忽略问题与硬失败。`utils/claims_utils.py` 生成 GPU 当前 claims 与 detached EAT token。

证据三源之外的**样本库**（`samples/`，28 文件）：26 个 swidtag RIM 样本（1010/g520 两大 GPU 族生产标签，如 `1010_0200_882_96005E0001_PROD.swidtag` 及 `test_no_gpu` 变体）+ Hopper 证明报告与证书链样本——测试与离线验证的地面真值。端到端测试两套：`tests/end_to_end/test_local_gpu_verifier.py`（标准 local 验证）与 `test_trust_outpost_gpu_verifier.py`（trust_outpost 部署形态变体）。

## 四、attestation_sdk：单例门面 + 四证明客户端（单插件）

`guest_tools/attestation_sdk/src/nv_attestation_sdk/attestation.py`（586 行）的 `Attestation`（class@89）是 **`__new__` 单例**（`_instance:100`、`__new__:105-125`）。**注意：四个证明客户端不在 verifiers/ 插件目录**——`attestation.py:19-20` 从 `.gpu` 与 `.nvswitch` 顶层包导入 `attest_gpu_local/attest_gpu_remote/attest_nvswitch_local/attest_nvswitch_remote`，再用 (设备×环境) 二维字典分派：取证 `:280-283`（如 `(Devices.GPU, Environment.LOCAL): attest_gpu_local.get_evidence`）、证明 `:316-319`。`verifiers/` 目录只有 **nv_switch_verifier 一个插件**；GPU 本地客户端直接调 local_gpu_verifier 的 cc_admin。

utils 工具层（SDK 的装配间）：`nras_utils.py`（158 行）对接 NRAS 远程服务——`create_jwks_url:23`（`nras_utils.py:33` 拼出 `/.well-known/jwks.json` 密钥发现 URL）、`validate_gpu_token:37`、`validate_gpu_token_with_policy:73`、`get_matching_key:106`；`unified_eat_parser.py` 识别 token 类型提取整体/detached claims；`claim_utils.py` 按授权策略验证 claims；`local_utils.py` 本地 token 验证；`logging_config.py`（`setup_logging/get_logger`+`SimpleMessageHandler`）；`config.py` 的 `allow_hold_cert` 开关（OCSP hold 证书策略）。

## 五、nv_switch_verifier 插件：GPU 验证器的同构双拷贝

`verifiers/nv_switch_verifier/`（28 文件）与 local_gpu_verifier **代码级同构**（两子项目各自维护一份，已漂移）：`nvswitch_admin.py`（352 行）`collect_evidence:78`/`collect_evidence_remote:63`/`attest:122` ↔ GPU 的 cc_admin；`nvswitch_admin_utils.py`（579 行）↔ cc_admin_utils（616 行）；`rim/__init__.py`（496 行）↔ GPU 版（547 行）；`attestation/spdm_msrt_resp_msg.py`（740 行，四类@39/147/259/440）↔ GPU 版（758 行）——NVSwitch 版 OpaqueData 含 PDI 族字段（`OPAQUE_FIELD_ID_DEVICE_PDI:286`、`OPAQUE_FIELD_ID_SWITCH_GPU_PDIS:290`，`TOTAL_NUMBER_OF_PDI=8:349`）与端口拓扑解析；`exceptions/__init__.py` **37 个异常类**（↔GPU 版 41）；`config.py` LS10 架构专属路径（↔Hopper/Blackwell）。

**NSCQ 封装**是 NVSwitch 侧的"NVML"：`nscq/pynscq.py`（**623 行**，CTypes 手写绑定：`_loadNscq` dlopen+符号查找+CFUNCTYPE 回调）+ `NSCQHandler`（`nscq/__init__.py`，回调式采集交换机 UUID/架构/TNVL/证明数据）。C 契约仅两个声明头：`nscq_attestation.h`（168 行，`NSCQ_API_VERSION` 宏@46、`NSCQ_API_VERSION_CODE = NSCQ_API_VERSION(2,0,0)`@53-54、`NSCQ_RC_*` 返回码）与 `nscq_attestation_path.h`（63 行，extern-C 双态宏+`{device}/{nvswitch}` 路径占位符，与 Python `paths.py` 对应）。**全仓唯二 C 头**。

SDK 测试矩阵（`tests/`，51 文件）三线：`pytests/`（单元+数据，含 `pytests/test_attestation.py`、`pytests/nvswitch/test_attest_nvswitch_local.py`）、`policies/`（local/remote 策略）、`end_to_end/`（hardware/no_gpu 真机矩阵）。

## 六、ppcie-verifier 两代：PCIe 拓扑证明的当代版与 C++ SDK 版

**当代版** `ppcie-verifier/ppcie/verifier/verification.py`（511 行）编排骨架"预检→GPU 证明→交换机证明→拓扑验证→状态汇总"，是三方（attestation_sdk/local_gpu_verifier/自身）的编排层——跨子项目 import 枢纽实证：`:25` `from nv_attestation_sdk import attestation`、`:27` NSCQHandler、`:28/:30` RIM/OCSP 端点与 `set_allow_hold_cert`、`:29` 本地 NvmlHandler、`:31` NVSwitch 模型、`:39` Status、`:40` TopologyValidation。证据源 `src/nvml/nvml_client.py`（GPU 计数/Ready State/CC 设置）与 `src/topology/validate_topology.py`（210 行，`:20` HopperSettings、`:23` 复用 nv_switch_verifier 的 attestation——直调 NVML/NSCQ 采集）。随附策略数据 `data/` 8 个 JSON：GPU/NVSwitch × local/remote × claims 2.0/3.0 双版本。

**sdk-cpp 版** `ppcie-verifier-sdk-cpp/ppcie/verifier/verification.py`（635 行）同构但**证明路径不同**：经 `run_nvattest_command:245` 外部 nvattest 子命令做证明（当代版直调 SDK），并支持文件证据模式（`--gpu-evidence:57`/`--switch-evidence:62`）；拓扑验证 `src/topology/validate_topology.py`（173 行）**从 EAT claims 读 PDI**（`GPU_SWITCH_PDIS_CLAIM:24`='x-nvidia-gpu-switch-pdis'、`SWITCH_PDI_CLAIM:25`、`SWITCH_GPU_PDIS_CLAIM:26`、`DISABLED_PDI:27`='0000000000000000'），不直接调 NVML/NSCQ。内嵌自己的 NSCQ：`src/nscq/pynscq.py`（**603 行**，与 attestation_sdk 版 623 行构成**双份漂移**）。

测试与策略语言：两代各带 `tests/test_verification.py`（当代版 302 行、sdk-cpp 版 385 行含文件证据模式）、`test_nvml_client.py`、`test_validate_topology.py`（sdk-cpp 版含禁用链路/重复 PDI 场景）；sdk-cpp `tests/data/` 有 `gpu_evidence.json`（文件证据样本）与 **`relying_party_policy.rego`（OPA Rego 策略）**——依赖方授权策略的语言示例。安装脚本 `install/ppcie-installer.sh` 按 local_gpu_verifier→attestation_sdk→ppcie 依赖序装 venv。

## 七、双拷贝架构：nvtrust 最重要的组织事实

仓内有**三组代码级拷贝**，阅读时必须两两对照：(1) local_gpu_verifier（GPU）↔ nv_switch_verifier（NVSwitch 插件）——rim/attestation/exceptions/utils/admin 五件套同构；(2) attestation_sdk nscq ↔ ppcie-verifier-sdk-cpp 内嵌 nscq——pynscq 623 vs 603 行已漂移 20 行；(3) ppcie 两代的 nvml/topology/utils 模块互为拷贝。另有三份同构 logging 模块（`attestation_sdk/utils/logging_config.py` 与两代 `ppcie/.../utils/logging.py`，签名完全相同：`get_logger`/`setup_logging`/`SimpleMessageHandler`）——它们互不引用，各被本子树引用（图谱曾生成跨模块假边，已剔除）。这是"fork 式复用再漂移"的典型样貌：改一处 bug 时要 grep 三处同名件。

## 八、上手路径（对应图谱 14 步导览）

T01 `README.md`+`SECURITY.md` 总览 → T04 lgv 验证主线（`cc_admin.py:95` main 入手）→ T05 RIM 与证书（`local_gpu_verifier/src/verifier/rim/__init__.py:64`）→ T06 NVML 接口（`NvmlHandler:74`）→ T07 样本库实测口径 → T08 lgv E2E → T09 SDK 单例（`attestation.py:105` __new__）→ T10 EAT/NRAS 工具 → T11 nv_switch_verifier 与双拷贝 → T13/T14 ppcie 两代对照。

实操建议：离线跑通 local_gpu_verifier 的 no_gpu 路径（用 `samples/` 的 swidtag+证明报告样本）；理解 SPDM 字段先读 `local_gpu_verifier/src/verifier/attestation/spdm_msrt_resp_msg.py:258` 的 OpaqueData 类；调试 NRAS 用 `nras_utils.py:33` 的 JWKS URL 规则。安全报告渠道在根 `SECURITY.md`（勿开 public issue 报漏洞）。
