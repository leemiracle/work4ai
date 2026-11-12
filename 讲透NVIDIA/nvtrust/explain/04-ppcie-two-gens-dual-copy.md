# 04 · ppcie 两代实现与全仓双拷贝架构

## 角色定位
`ppcie-verifier`（当代版）与 `ppcie-verifier-sdk-cpp`（C++ SDK 版）是 PCIe pDMLUS（机密互连）拓扑证明器：验证 GPU↔NVSwitch 互连拓扑与期望一致（链路未被禁用/替换）。两代并存+全仓三组代码级拷贝，构成本节要讲的"组织事实"——读懂它才能安全地改这个仓。

## 内部结构
**当代版** `ppcie-verifier/ppcie/verifier/verification.py`（511 行）：编排"预检→GPU 证明→交换机证明→拓扑验证→状态汇总"，进度经 `src/utils/status.py` 的 Status 类可观测；异常三层（`src/exceptions/exception.py` 基类 PpcieVerifierException、`src/nvml/exceptions.py`、`src/topology/exceptions.py`）。证据源两件：`src/nvml/nvml_client.py`（GPU 计数/Ready State/CC 设置查询与设置）、`src/topology/validate_topology.py`（210 行）。策略数据 `data/` 8 个 JSON（GPU/NVSwitch × local/remote × claims 2.0/3.0）。

**sdk-cpp 版** `ppcie-verifier-sdk-cpp/ppcie/verifier/verification.py`（635 行）同构编排但证明路径不同：`run_nvattest_command:245` 经外部 nvattest 子命令做证明（捕获退出码/stdout/stderr 记日志），文件证据模式 `--gpu-evidence:57`/`--switch-evidence:62` 允许离线回放。拓扑验证 `src/topology/validate_topology.py`（173 行）**从 EAT claims 读 PDI**：`GPU_SWITCH_PDIS_CLAIM:24`（'x-nvidia-gpu-switch-pdis'）、`SWITCH_PDI_CLAIM:25`、`SWITCH_GPU_PDIS_CLAIM:26`、`DISABLED_PDI:27`（'0000000000000000'），`_pdi_set:32` 规范化 PDI 集合。

**全仓三组双拷贝**（改一处 grep 三处）：
1. local_gpu_verifier ↔ nv_switch_verifier：rim（547↔496 行）、attestation（AttestationReport 同构）、spdm_msrt_resp_msg（758↔740 行，NVSwitch 版 OpaqueData 含 `DEVICE_PDI:286`/`SWITCH_GPU_PDIS:290`/`TOTAL_NUMBER_OF_PDI=8:349`）、exceptions（41↔37 类）、utils、admin（cc_admin 683↔nvswitch_admin 352 行）。
2. **pynscq 双份漂移**：attestation_sdk 版 `nv_switch_verifier/nscq/pynscq.py` 623 行 ↔ sdk-cpp 内嵌版 `src/nscq/pynscq.py` 603 行——20 行差证明拷贝已分叉。
3. 两代 ppcie 的 nvml/topology/utils 互拷（`.pylintrc` 617 行也双份）。

另有三份同构 logging 模块（`attestation_sdk/utils/logging_config.py` 与两代 `ppcie/.../utils/logging.py`，同签名 `get_logger`/`setup_logging`/`SimpleMessageHandler`），互不引用、各被本子树引用。

## 外部连接
当代版是三方枢纽（实证 `guest_tools/ppcie-verifier/ppcie/verifier/verification.py:25-40`）：attestation_sdk 单例@:25、`NSCQHandler:27`、`RIM_SERVICE_URL:28`、本地 `NvmlHandler:29`、NVSwitch 模型@:31、`Status:39`、`TopologyValidation:40`、`set_allow_hold_cert`@:30；拓扑验证复用 `HopperSettings`（`guest_tools/ppcie-verifier/ppcie/verifier/src/topology/validate_topology.py:20`）与 nv_switch_verifier 的 attestation（:23）。NSCQ 的 C 契约仅两个声明头（全仓唯二 C 头）：`nscq_attestation.h`（168 行，`NSCQ_API_VERSION`@46、版本 2.0.0@53-54、`NSCQ_RC_*` 返回码表）与 `nscq_attestation_path.h`（63 行，`{device}/{nvswitch}` 路径占位符）。安装 `install/ppcie-installer.sh`（两代各一）按 local_gpu_verifier→attestation_sdk→ppcie 依赖序建 venv。策略语言样本 `tests/data/relying_party_policy.rego`（OPA Rego）+ `gpu_evidence.json`。

## 数据流
当代版：NVML 预检（Ready State/CC）→ SDK 单例驱动 GPU/交换机证明（本地直调，远程 NRAS）→ 拓扑验证直采 NVML/NSCQ 互连数据与期望比对 → Status 汇总。sdk-cpp 版：nvattest 子命令产出证明 → 从 claims 提取 PDI 集合 → GPU 视角（`GPU_SWITCH_PDIS`）与交换机视角（`SWITCH_PDIS`+`SWITCH_GPU_PDIS`）交叉验证，`DISABLED_PDI` 全零值识别禁用链路（测试覆盖禁用链路/重复 PDI 场景，`tests/test_validate_topology.py`）。

## 设计决策
- **两代并存的实质**：当代版"SDK 直调"（进程内、快、依赖 Python 栈齐装）；sdk-cpp 版"外部命令+文件证据"（解耦、可离线回放、贴近 C++ SDK 交付形态）——不是新旧替代而是部署形态分叉。
- **PDI 从 claims 读而非现场采**（sdk-cpp 版）：拓扑判断只信"已证明的 claims"，把采集与判定解耦——证明一次、判定多次。
- **拷贝式复用**（而非抽公共库）：各子项目保持可独立安装的完整性，代价是漂移（pynscq 20 行差是最轻的症状）。
- **策略数据化**：8 个 claims 2.0/3.0 策略 JSON 让证明口径随版本演进不动代码。

## 新人提示
对照读两代 `verification.py`（511 vs 635 行）先看 import 区与 attest 调用方式差异，一眼分清两代。改 pynscq/rim/exceptions 任何一份先 `grep -rn` 同名文件定位全部拷贝。调拓扑失败先打印 claims 里的 PDI 集合核对 `DISABLED_PDI:27` 全零值。跑 sdk-cpp 测试用 `tests/data/gpu_evidence.json` 文件证据模式免真机；Rego 策略样本是理解依赖方授权语义的最佳入口。
