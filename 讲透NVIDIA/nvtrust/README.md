# 讲透 nvtrust（NVIDIA GPU/NVSwitch 信任验证）

> 上游 NVIDIA/nvtrust @ commit a8090b65872a15bf0fd1f69f3d9b754b1be431b5（2026-11-09 分析）
> 本地仓 /usr-data/data2/repos/agent-repos/NVIDIA/nvtrust · DeepWiki 抓取 2026-10-26

## 全链状态表

| 阶段 | 产物 | 状态 |
|---|---|---|
| DeepWiki | `deepwiki/`（26 页，454,837 字符，TRUE_100） | ✅ 2026-10-26 |
| understand 图谱 | 仓内 `.understand-anything/knowledge-graph.json`（584 节点/993 边/12 层/14 步导览，validator 0 issues，fingerprints 245 文件 @a8090b65） | ✅ 2026-11-09 |
| onboarding | `onboarding/ONBOARDING.md`（8 节，40+ 行号锚全源码复核） | ✅ |
| explain | `explain/` 4 篇（local_gpu_verifier/SPDM+RIM/attestation_sdk/ppcie 两代与双拷贝，每篇 12+ 锚） | ✅ |

图谱分层：L01 根与治理（14）/L02 host+infrastructure（9）/L03 lgv 验证主线（12）/L04 lgv 证据源（12）/L05 lgv 样本库（28）/L06 lgv 包配置与 E2E（8）/L07 sdk 核心（13）/L08 sdk utils（8）/L09 nv_switch_verifier（28）/L10 sdk 测试矩阵（50）/L11 ppcie 当代版（35）/L12 ppcie-sdk-cpp（28）。

## 勘误清单（图谱/常识表述 vs 源码实证）

1. **"verifiers 四插件"修正为"单插件+四客户端"**：`attestation_sdk/src/nv_attestation_sdk/verifiers/` 只含 nv_switch_verifier 一个插件（28 文件）；四个证明客户端在顶层 `gpu/`（attest_gpu_local/attest_gpu_remote）与 `nvswitch/`（attest_nvswitch_local/attest_nvswitch_remote）包——`attestation.py:19-20` 导入、`:280-283`（get_evidence）与 `:316-319`（attest）两张 (设备×环境) 字典分派。GPU 本地客户端直调 local_gpu_verifier 的 cc_admin，不作为 verifiers 插件存在。
2. **GPU·NVSwitch 双拷贝是组织主事实**：nv_switch_verifier 与 local_gpu_verifier 五件套代码级同构且已漂移——rim 547↔496 行、spdm_msrt_resp_msg 758↔740 行、exceptions **41↔37 个异常类**（脚本实证 `grep -c "^class "`）、cc_admin 683↔nvswitch_admin 352 行、AttestationReport 类结构同构（GPU 版 class@53，方法 extract_response_message@63/concatenate@94/verify_signature@117）。
3. **pynscq 双份漂移 20 行**：attestation_sdk 版 `nv_switch_verifier/nscq/pynscq.py` **623 行** vs ppcie-verifier-sdk-cpp 内嵌版 `src/nscq/pynscq.py` **603 行**（wc 实证）——两份同构 CTypes 绑定（`_loadNscq` dlopen+`__nscqFindFunc`+CFUNCTYPE）独立维护。
4. **logging 假边剔除**：三份同构 logging 模块（`attestation_sdk/utils/logging_config.py`、两代 `ppcie/.../utils/logging.py`）签名完全相同（get_logger/setup_logging/SimpleMessageHandler），曾生成的跨模块 import 边不成立——源码 grep 实证三模块互不引用，各自只被本子树文件 import（如 attestation.py:17、nvswitch_admin.py:48、ppcie-verifier/ppcie/verifier/src/topology/validate_topology.py:30）。图谱终稿已无该假边。
5. **全仓 C 头仅 2 个声明头**：`nv_switch_verifier/nscq/nscq_attestation.h`（168 行，`NSCQ_API_VERSION` 宏@46、`NSCQ_API_VERSION_CODE = NSCQ_API_VERSION(2, 0, 0)`@53-54、`NSCQ_RC_*` 返回码）与 `nscq_attestation_path.h`（63 行，extern-C 双态宏+`{device}/{nvswitch}` sysfs 路径占位符）——不存在其他 C/C++ 源文件；"C 头"语境下的所有 FFI 契约都只有这一对。
6. **BaseSettings 非第三方库**：`local_gpu_verifier/src/verifier/config.py:59` 的 `class BaseSettings` 是 651 行手写单类（OCSP/RIM 端点、nonce、SKU 全部状态），**不是 pydantic BaseSettings**；架构分派 `HopperSettings:581`/`BlackwellSettings:613` 注册于 `GPU_ARCHITECTURE_MAP[9]:650`（Hopper）与 `[10]:651`（Blackwell）。
7. **ppcie 两代证明路径不同源**：当代版直调 attestation_sdk（`ppcie-verifier/ppcie/verifier/verification.py:25-31` 五个 nv_attestation_sdk import）；sdk-cpp 版经 `run_nvattest_command:245` 外部命令+文件证据模式（`--gpu-evidence:57`/`--switch-evidence:62`）；拓扑验证当代版现场采证（`ppcie-verifier/ppcie/verifier/src/topology/validate_topology.py:20-23` 直用 HopperSettings 与 nv_switch_verifier attestation），sdk-cpp 版从 EAT claims 读 PDI（`GPU_SWITCH_PDIS_CLAIM:24` 等三个 claim 常量@24-26、`DISABLED_PDI`@27）。
8. **占位目录**：`guest_tools/attestation_sdk_cpp/` 是空目录（0 文件）；`guest_tools/rims/rim_service/` 仅一个 README 占位——两者在 DeepWiki 叙事中易被误当成实体组件。sdk 测试矩阵图谱 fileCount=50 vs 磁盘 51 文件（含非 py 数据件，近似计数）。

## 阅读路径

- 快速上手：`onboarding/ONBOARDING.md` 一、二节（信任模型）→ `explain/01`（lgv 主线）
- 协议深潜：`explain/02`（SPDM OpaqueData 私有扩展+RIM 双重校验）
- SDK 视角：`explain/03`（单例+四客户端分派表）
- 改仓必读：`explain/04`（ppcie 两代+三组双拷贝，改一处 grep 三处）
- DeepWiki 对照：`deepwiki/INDEX.md`（26 页：attestation-sdk/gpu/nvswitch/ppcie 四大主题）
