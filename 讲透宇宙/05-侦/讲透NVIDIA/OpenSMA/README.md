# 讲透 NVIDIA/OpenSMA

NVIDIA GPU 板卡 MCXN 双核 MCU 的 SMA 诊断固件：NSM 协议（MCTP 之上）+ SPDM 认证 + Ada PLDM 固件更新 + 三平台（mcxn236/mcxn556/x86）。

## 产物状态

| 产物 | 状态 | 位置 | 规模 |
|---|---|---|---|
| deepwiki | ✅（另有专卷） | `deepwiki/` | — |
| 知识图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json` | 7644 节点 / 9439 边 / 16 层 / 16 步 tour，validator 0 issues |
| fingerprints | ✅ | 仓内 `.understand-anything/fingerprints.json` | 3054 文件 @ 0c220c3a |
| ONBOARDING | ✅ | `onboarding/ONBOARDING.md` | 8 节，行号锚 50+ |
| explain | ✅ 6 篇 | `explain/01`~`06` | 每篇 2000-3000 字符（不计空格），锚 12+ |
| 本 README | ✅ | 勘误 11 条 | — |

图谱统计：图谱 source 为全仓 3054 文件（fingerprints 基线），分析时 commit `0c220c3a2d1de8cdc93804f1d86892814ef8a1ca`。

## 核心数字速查

- `src/nv/mctp/nsm.cpp` **3846 行**（全仓最大单文件）；nsm_type_5.cpp 1843 / nsm_type_3.cpp 1572 / nsm_type_4.cpp 1048 / nsm_type_ff.cpp 438 / nsm_type_2.cpp 131
- `src/nv/mctp/driver.cpp` 1096 行；`src/nv/spdm/spdm_cert_chain.cpp` 1577 行；`src/nv/spdm/spdm_get_measurement.cpp` 956 行；`src/nv/spdm/task.cpp` 497 行
- Ada：`pdk-pldm-fwupdate-cmd.adb` **2001 行**；`pdk-pldm-fwupdate-state.adb` 620 行；`pdk-pldm-base-cmd.adb` 565 行
- 证书样例 `unit_test/sample_key/` **887 文件**（long_chains 319）；fuzzing 234 文件
- 平台：mcxn556 135 文件（bootloader.cpp 770 行）/ mcxn236 104 文件 / x86 95 文件
- 构建：`corepdk/ubs/src/ubs/ubs.py` 509 行；签名 keystore ECDSA P384 + MLDSA-87

## 勘误与图谱口径（11 条）

1. **NSM 目录直觉错误**：NSM 协议实现在 `src/nv/mctp/`（与 MCTP driver 同目录），仓库**没有** `src/nv/nsm/`；遥测缓存在 `src/nv/telemetry/`。按直觉路径找代码必然扑空。
2. **scanner importMap 盲区极大**：scan 阶段 importMap 仅 39/1891 文件非空（C/C++/Ada 混合仓 tree-sitter 支持弱），imports 边大量依赖 worker 手扫 `#include` 重补；引用图谱 imports 边时注意这一基数背景。
3. **Ada 无 tree-sitter 支持**：`corepdk/modules/pldm-fd/` 的 .adb/.ads 全部靠自写正则+人工解析建节点，函数级节点粒度弱于 C++ 侧。
4. **弱/强符号对分居两目录**：weak 默认实现在 `src/nv/mctp/nsm_pwr_smoothing_handlers_weak.cpp:43`（`__attribute__((weak))`），strong 真实现在 `src/nv/soc_pwr_smoothing/nsm_pwr_smoothing_handlers.cpp`（452 行）。只 grep 单目录会误判"未实现"。同模式还有 flash/pds_pwr_smoothing_defaults_weak.cpp 对。
5. **capabilites 拼写沿用上游**：`corepdk/modules/spdm/src/app/pdk-spdm-app-res-capabilities.h:203-209` 一组 API 名为 `spdm_library_get_capabilites_*`（少个 i）。这是与上游兼容的历史拼写，**不要"顺手修复"**——改名会破坏链接兼容。
6. **证书批 nodes=25 edges=0 是合法形态**：`unit_test/sample_key/` 887 个证书/私钥二进制无 include 关系，worker 批产出以 file 节点+related 边为主，零 import 边不是缺陷。
7. **CMakeLists 归 document 节点**：file-analyzer 规范下无代码符号的构建文件归 document 类而非 config 类；图谱里查构建逻辑先搜 document: 前缀。
8. **aead_aes_gcm.c 同名三份**：`os_stub/cryptlib_mbedtls/cipher/aead_aes_gcm.c`（187 行）/ `cryptlib_openssl/...`（267 行）/ `cryptlib_null/...`（88 行）。任何引用必须带目录前缀，裸文件名三义。
9. **"2001 行全状态机"应拆两文件**：fwupdate 命令应答在 `pdk-pldm-fwupdate-cmd.adb`（2001 行），持久状态在 `pdk-pldm-fwupdate-state.adb`（620 行）——引用"PLDM 状态机 2001 行"时注意它只是命令侧。
10. **mcxn236 文件计数口径差**：图谱层描述记 111 文件，盘上 `find src/sys/mcxn236 -type f` 实测 104——差异源于分析口径（含/不含部分生成物）。引用时注明口径；mcxn556（135）与 x86（95）两数则已盘上核实。
11. **powersensor 在 i2c 之下**：热插拔功率传感器目录是 `src/nv/i2c/powersensor/`（device_manager + hsc_lm5066i/hsc_mp5926/hscc_mp29540/hscc_raa22800X/hsc_xpd712021 一型号一文件），温度/注错等散在 `src/nv/i2c/` 根（emc1812/nct75/tmp461 族、error_injection.cpp）——**不存在** `src/nv/powersensor/`。

## explain 索引

- `explain/01-NSM协议与遥测.md` —— nsm.cpp 命令分发、Type2/3/4/5/FF、遥测缓存命中模型、弱符号钩子
- `explain/02-MCTP传输栈.md` —— driver.cpp 端点管理、分片重组、mctp-cpp 模块、USB 备份通道
- `explain/03-SPDM安全纵深.md` —— 业务→适配→libspdm→密码学五层、证书槽位、度量缓存
- `explain/04-密码学三后端切换.md` —— aead 三份对照、FIPS 自测、设备密钥库红线
- `explain/05-Ada-PLDM与UBS构建.md` —— RequestUpdate/Transfer/Verify、GNAT 工程、签名 keystore
- `explain/06-平台层与硬件监控.md` —— 三平台 HAL、powersensor 族、跨核 ipc/flash、遥测物理链
