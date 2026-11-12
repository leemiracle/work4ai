# 03 · attestation_sdk：单例门面、四证明客户端与单插件目录

## 角色定位
`guest_tools/attestation_sdk`（Python 包名 `nv_attestation_sdk`）是 nvtrust 的证明 SDK：给依赖方（relying party）一个统一入口，把 GPU/NVSwitch × 本地/远程四种证明组合收进一套 API。它是 ppcie-verifier 当代版的直接依赖，也是 NRAS（NVIDIA Remote Attestation Service）远程证明的消费端。

## 内部结构
**门面** `src/nv_attestation_sdk/attestation.py`（586 行）：`Attestation`（class@89）以 `__new__` 实现单例（`_instance:100`、`__new__:105-125`，重入返回同一实例 `:125`）。四个证明客户端**不在 verifiers/ 目录**而在顶层包：`:19` `from .gpu import attest_gpu_local, attest_gpu_remote`、`:20` `from .nvswitch import attest_nvswitch_local, attest_nvswitch_remote`；每个客户端实现 `get_evidence`/`attest` 两接口。分派是两张 (设备×环境) 字典：取证 `:280-283`、证明 `:316-319`（如 `(Devices.GPU, Environment.LOCAL): attest_gpu_local.attest`）。`verifiers/` 插件目录**只有 nv_switch_verifier 一个成员**（28 文件）。

**客户端四件**：`gpu/attest_gpu_local.py`（直调 local_gpu_verifier 的 cc_admin）、`gpu/attest_gpu_remote.py`（经 NRAS 取证并解析返回的 EAT token）、`nvswitch/attest_nvswitch_local.py`（本地 NSCQ 通道）、`nvswitch/attest_nvswitch_remote.py`（NRAS 交换机证明）。

**utils 工具层**（8 文件）：`nras_utils.py`（158 行）——`create_jwks_url:23` 从 verifier URL 推导 `/.well-known/jwks.json` 密钥发现端点（URL 拼接在 `nras_utils.py:33`）、`validate_gpu_token:37`/`validate_gpu_token_with_policy:73`/`validate_claims_and_decode:59`、`get_matching_key:106` 按 kid 匹配 JWKS 密钥；`unified_eat_parser.py`（识别 token 类型提取整体/detached claims）；`claim_utils.py`（按授权策略验证 claims、提取策略规则）；`local_utils.py`（本地 token 验证 `validate_token`）；`logging_config.py`（`setup_logging/get_logger`+`SimpleMessageHandler` 居中标题 Handler）；`config.py`（`allow_hold_cert` OCSP hold 策略开关+RIM/OCSP 端点常量）；`headers.py`（NRAS 请求头）。

**nv_switch_verifier 插件**：`nvswitch_admin.py`（352 行）`collect_evidence:78`/`collect_evidence_remote:63`/`attest:122`，`nvswitch_admin_utils.py`（579 行）FWID/证书链/OCSP/RIM 支撑，`config.py` LS10 架构设置，`exceptions/__init__.py` 37 个异常类（↔GPU 版 41），rim（496 行）/attestation（`AttestationReport` 同构）/models 数据模型。NSCQ 封装见 04 篇。

## 外部连接
上游：local_gpu_verifier（本地 GPU 证据）、NSCQ/libnscq（交换机证据）、NRAS（远程两路）。下游：ppcie-verifier 当代版 `guest_tools/ppcie-verifier/ppcie/verifier/verification.py:25-31` 直接 import 本 SDK（attestation 单例、NSCQHandler、RIM/OCSP 端点常量、`set_allow_hold_cert`、NVSwitch 模型）；`pyproject.toml`（poetry）声明 ppcie/local_gpu_verifier 本地依赖。测试矩阵 `tests/`（51 文件）三线：`pytests/`（`test_attestation.py`、`nvswitch/test_attest_nvswitch_local.py` 等）、`policies/`（local/remote 策略）、`end_to_end/`（hardware/no_gpu 真机矩阵）。

## 数据流
依赖方拿单例 → `get_verifiers:259` 查注册 → 按 (Devices, Environment) 从 `:280-283` 取 evidence 函数采集证据（本地走 NVML/NSCQ，远程走 NRAS）→ 从 `:316-319` 取 attest 函数验证（本地全链校验；远程则 NRAS 返回 EAT token，`nras_utils` 经 JWKS 验签+`claim_utils` 按策略校验 claims）→ `unified_eat_parser` 归一化输出整体/detached token。

## 设计决策
- **单例门面+字典分派**：新增设备/环境组合=实现两接口+两张表各加一行，客户端零继承。
- **GPU 侧不设 verifiers 插件**：GPU 本地验证已有成熟独立包（local_gpu_verifier），SDK 客户端做薄壳直调；只有 NVSwitch 因无独立包才以插件形态自含 28 文件——"verifiers=插件目录"与"四个客户端"是两回事。
- **远程证明信任 JWKS 而非本地 PEM**：NRAS 的密钥经标准 well-known 端点发现，密钥轮换零发版。
- 策略与代码分离：policies 测试 + ppcie data/ 的 claims 2.0/3.0 JSON 让授权规则可数据化演进。

## 新人提示
从 `attestation.py:105` 的 `__new__` 与 `:280-283/:316-319` 两张分派表读起，5 分钟可画出 SDK 全图。排查"客户端没被调用"先查设备/环境枚举组合是否命中字典键。做远程证明联调时先用 `nras_utils.py:33` 的 URL 规则手工 curl JWKS 端点确认连通。改 nv_switch_verifier 记得与 local_gpu_verifier 的同名件对照（双拷贝漂移坑见 04 篇）。
