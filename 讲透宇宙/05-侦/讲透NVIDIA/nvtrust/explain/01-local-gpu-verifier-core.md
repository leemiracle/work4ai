# 01 · local_gpu_verifier：GPU 本地验证主线

## 角色定位
`guest_tools/gpu_verifiers/local_gpu_verifier` 是 nvtrust 的第一个主力组件：在 GPU 所在的 guest 内（不经远程服务）完成"设备身份→固件度量→黄金值比对"全链，产出 EAT claims。它同时是 attestation_sdk GPU 本地客户端的底层引擎（SDK 直调其 cc_admin），也是仓内最大异常产地与样本库所在地。

## 内部结构
四层分工：
1. **编排层** `cc_admin.py`（683 行，CLI 主程序）：`main:95` 解析参数→`attest:314` 驱动全流程（证据采集、证书链验证、OCSP、RIM 比对、EAT claims 生成）；`cc_admin_utils.py`（616 行）提供 FWID 提取、证书链/OCSP 验证、RIM 获取等支撑函数。
2. **比对层** `verifier.py`：`Verifier`（class@42）`verify:47` 把运行时度量与 RIM 黄金度量逐项比对（`:57` 比对日志、`:62-63` 无黄金度量的警告路径）。
3. **证据层** `nvml/__init__.py`：`NvmlHandler`（class@74）封装 NVML 查询——`get_number_of_gpus:80`、`get_gpu_ready_state:165`、`get_driver_version:219`、`get_uuid:227`、`get_vbios_version:235`、`get_attestation_cert_chain:243`、`get_attestation_report:252`、`get_gpu_architecture:260`、`get_cc_feature:368`。测试桩 `nvmlHandlerTest.py`/`test_handle.py` 以预置文件替代真实 GPU。
4. **配置/异常层** `config.py`（651 行）：手写 `class BaseSettings:59`（非 pydantic）承载 OCSP/RIM 端点、nonce、SKU；架构分派 `HopperSettings:581`/`BlackwellSettings:613`，注册 `GPU_ARCHITECTURE_MAP[9]=Hopper:650`、`[10]=Blackwell:651`；`exceptions/__init__.py` 41 个异常类（Error 基类的证明/RIM/证书/NVML 全域层次），`exceptions/utils.py` 的 `is_non_fatal_issue` 划分软硬失败。

## 外部连接
上游：NVML 驱动接口（证据）、本地信任锚 `certs/verifier_RIM_root.pem`+`verifier_device_root.pem`（校验）。下游：attestation_sdk 的 `gpu/attest_gpu_local.py`（get_evidence/attest 直调 cc_admin）；ppcie-verifier 经依赖序安装（`install/ppcie-installer.sh` 先装本包）。横向：EAT 产出走 `utils/claims_utils.py`（GPU 当前 claims+detached EAT token）。样本库 `samples/`（28 文件：26 个 swidtag RIM 生产标签 1010/g520 两族+Hopper 证明报告/证书链样本）支撑离线回放。

## 数据流
`main:95` 启动 → NvmlHandler 枚举 GPU 并按 `get_gpu_architecture:260` 选 Hopper/Blackwell 配置 → `get_attestation_cert_chain:243` 取证书链、`get_attestation_report:252` 取 SPDM 证明报告 → 证书链锚定本地根 PEM + OCSP 在线状态 → `AttestationReport` 验签拆度量 → RIM 读取（`rim/__init__.py` `read:105`→XSD 校验→`extract_certificates:230`）取出黄金度量 → `Verifier.verify:47` 逐项比对 → 差异映射到 41 类异常（经 `is_non_fatal_issue` 分级）→ 通过则 `claims_utils` 生成 EAT claims/token。

## 设计决策
- **本地优先**：全部校验锚在 guest 内的 PEM/样本，不依赖网络可达（OCSP 失败可按策略降级，`BaseSettings` 的 `allow_hold_cert` 系列判断在 `local_gpu_verifier/src/verifier/config.py:540-570` 一带）。
- **异常分类学**（41 类）而非单一错误码：验证失败的诊断信息密度是运维刚需。
- **架构注册表分派**（GPU_ARCHITECTURE_MAP）：新增架构=新增 Settings 子类+一行注册，主流程零改动。
- **测试桩与样本即数据合同**：no_gpu 路径用生产 swidtag 样本回放，E2E（`tests/end_to_end/test_local_gpu_verifier.py`）与 trust_outpost 变体（`test_trust_outpost_gpu_verifier.py`）覆盖两种部署形态。

## 新人提示
入口从 `cc_admin.py:95` 的 main 读起，跟一次 attest 全流程再回头看 41 类异常的分类学。调试"为什么验证失败"先分软硬：`exceptions/utils.py` 的 `is_non_fatal_issue` 决定流程是否继续。无真机时用 `samples/` 的 swidtag+证明报告样本跑 no_gpu 路径（`nvmlHandlerTest.py` 是替换 NvmlHandler 的钥匙）。改配置项记得 Hopper/Blackwell 两个 Settings 子类要同步。
