# 02 · SPDM 度量证明与 RIM：nvtrust 的两类信任根

## 角色定位
SPDM（Security Protocols and Data Model，DMTF 标准）与 RIM（Reference Integrity Manifest）是 nvtrust 全部验证器的证据语法：前者是"设备此刻的度量证明"的线缆协议格式，后者是"设备应该是什么样"的黄金参考（SWID tag XML）。两者都存在 GPU 与 NVSwitch 双拷贝（见 04 篇），本文以 GPU 版（`local_gpu_verifier/src/verifier/`）为主线。

## 内部结构
**SPDM 报文解析**（`attestation/` 目录）：
- `__init__.py` 的 `AttestationReport`（class@53）：`extract_response_message:63`/`extract_request_message:78` 从证明报告二进制拆出请求/响应、`concatenate:94` 拼接待签数据、`verify_signature:117` 用设备证书验签、`get_measurements:151` 取度量块、`get_request_message:170`/`get_response_message:178` 取解析后的消息对象。
- `spdm_msrt_resp_msg.py`（758 行，四类）：`DmtfMeasurement:40`（标准度量块）、`MeasurementRecord:148`（度量记录，`parse` 逻辑在 `:179` 一带）、`OpaqueData:258`（**NVIDIA 专有扩展**——`parse_measurement_count:321`、`parse_switch_pdis:345`（交换机端口 PDI）、`parse_feature_flag:365`、`parse_chip_info:379`，字段超出 DMTF SPDM 标准定义）、`SpdmMeasurementResponseMessage:456`（响应总装）。位级 get/set 遍布各类。
- `spdm_msrt_req_msg.py`：请求消息的版本/参数/nonce/slot id 位级解析。

**RIM 解析**（`rim/` 目录）：`__init__.py`（547 行）`RIM` 类（class@64）——`read:105`（路径或内容二选一）→`parse_schema:138`（XSD 校验，schema 三件套 `signSchema.xsd`/`swidSchema2015.xsd`/`xml.xsd`）→`validate_schema:185`→`extract_certificates:230`；`golden_measurement.py` 的 `GoldenMeasurement` 模型（组件/索引/期望值/替代项）。NVSwitch 拷贝 `nv_switch_verifier/rim/__init__.py`（496 行）同构，`signSchema.xsd` 为 GPU 版同构拷贝。

## 外部连接
上游：SPDM 报文来自 GPU 驱动（NVML `get_attestation_report:252`）或 NVSwitch 驱动（NSCQ 证明查询，C 契约 `nscq_attestation.h`，`NSCQ_API_VERSION(2,0,0)`@53-54）；RIM 来自 `samples/` 本地样本（26 个 swidtag 生产标签）或 RIM 服务（占位 `rims/rim_service/README.md`，端点配在 config）。下游：`Verifier.verify:47`（`verifier.py:42`）消费黄金度量做比对；`utils/claims_utils.py` 把结果编为 EAT claims；sdk-cpp 版 ppcie 的拓扑验证直接消费 claims 里的 PDI 字段（`x-nvidia-gpu-switch-pdis` 等）。

## 数据流
证明请求（nonce+slot）→ 设备返回 SPDM GET_MEASUREMENT 响应（版本/参数/度量块+OpaqueData+签名）→ `AttestationReport.concatenate:94` 拼接待签串 → `verify_signature:117` 用证书链里的证书验签 → `get_measurements:151`/`SpdmMeasurementResponseMessage:456` 拆出 DMTF 度量与 NVIDIA 扩展字段（PDI/feature flag/chip info）→ 与 RIM 的 `GoldenMeasurement` 逐项比对 → 差异异常化，一致则进 claims。RIM 侧先经 XSD schema 校验再验 RIM 自身签名（锚 `certs/verifier_RIM_root.pem`），黄金值才可信。

## 设计决策
- **位级手写解析而非 ASN.1/protobuf**：SPDM 是紧凑二进制协议，手写 get/set 保字节级控制（代价是 758 行类文件的可读性）。
- **OpaqueData 扩展槽**：NVIDIA 把私有字段（PDI/芯片信息/特性开关）塞进 SPDM 标准的 opaque 区，既过标准解析器又留私有语义——`parse_switch_pdis:345` 一族就是这层私有协议的解码器。
- **RIM 双重校验**（schema+签名）：XML 可被构造，黄金值必须先证明自己可信。
- **样本库即回归资产**：26 个生产 swidtag 让解析器对真实世界变体保持覆盖。

## 新人提示
先读 `local_gpu_verifier/src/verifier/attestation/spdm_msrt_resp_msg.py:258` 的 OpaqueData 类再读标准类——私有扩展才是本仓特色。抓包对不上时检查 `AttestationReport.concatenate:94` 的拼接顺序（验签失败 90% 是待签串拼错）。加新 OpaqueData 字段要在 GPU 与 NVSwitch 两份拷贝同步（`nv_switch_verifier/attestation/spdm_msrt_resp_msg.py` 四类在 `:39/147/259/440`）。RIM 样本命名规律：`1010_0200_882_*` 为 1010 族 vBIOS 标签，`_PROD` 生产版/`_test_no_gpu` 无 GPU 测试版。
