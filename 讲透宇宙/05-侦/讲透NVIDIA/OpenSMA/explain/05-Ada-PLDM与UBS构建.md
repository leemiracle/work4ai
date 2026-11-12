# 05 · Ada PLDM 固件更新与 UBS 构建：仓库里唯一的 Ada 模块

## 角色定位

`corepdk/modules/pldm-fd/` 是仓库里唯一的 Ada 语言模块（DMTF PLDM for Firmware Update 消息层），承担带外固件更新协议：主机 BMC 用它请求更新 MCU/AP 固件，固件侧走 RequestUpdate→Transfer→Verify 状态机应答。它与 UBS 构建系统（corepdk/ubs）同篇讲解，因为 Ada 工具链（GNAT/GPR 工程）是 UBS 必须特殊照顾的构建对象——src/nv 下甚至有 `src/nv/nv.ads` 包规范，让 C++/Ada 两世界共享常量。

## 内部结构

命令应答核心 `corepdk/modules/pldm-fd/src/fwupdate/pdk-pldm-fwupdate-cmd.adb`（2001 行）：`Pldmfw_Context_Init`（`corepdk/modules/pldm-fd/src/fwupdate/pdk-pldm-fwupdate-cmd.adb:225`）初始化更新上下文（`:235` 起的 Max_Transfer_Size/Last_Transfer_Size/Verify_Comp_Size 字段，`:295-296` 的 Transfer_Fail_CC/Verify_Fail_CC 逐阶段错误码）；`Pldmfw_Generate_Update_Report`（`corepdk/modules/pldm-fd/src/fwupdate/pdk-pldm-fwupdate-cmd.adb:136`）生成更新结果报告；`Pldmfw_Is_Rate_Limit_Reached`（`:157`）做传输限速判定；辅助序列化族 Add_U32/Add_U8/Minus_U32/Le_U32（`:47-104`）——Ada 强类型使显式字节操作成为必需。状态机独立在 `corepdk/modules/pldm-fd/src/fwupdate/pdk-pldm-fwupdate-state.adb`（620 行）：`Pldmfw_Change_State`（`:29`）+ 三态 handler——Idle（`:62`）/Lc（`:119`）/Rdy_Xfer（`:172`）。发现命令 `corepdk/modules/pldm-fd/src/base/pdk-pldm-base-cmd.adb:38`（Process_Base_Commands，GetTID/GetPLDMVersion；`:170` Fill_Resp_Header/`:185` Respond_Error），模块入口 `corepdk/modules/pldm-fd/src/main.adb:20`（procedure Main），平台钩子 `src/platforms/x86/pdk-pldm-hook-plat.adb`。

UBS 侧：`corepdk/ubs/src/ubs/ubs.py`（509 行 34 函数）是 Python 构建主控——`ubs.py:28`（ubs_export 装饰器）/`:35`（ubs_info）/`:45`（ubs_error）/`:61`（ubs_expect_fatal）构成编排与日志骨架，makefile 阶段族（ubs-main.mk 等）与 GNAT/GPR Ada 工程胶合。签名服务在 `libexec/tools/sma-mcxn556-signing-service/src/scripts/`：`sign.py` 主脚本 + `policy.json:29`（KeyPrefix MCXN556_S00_ECDSA_P384）+ `policy.json:30`（PqcKeyPrefix **MCXN556_S00_MLDSA_87**）+ `gen_pqc_isk_cert.py`（PQC ISK 证书生成）——ECDSA P384 与 MLDSA-87 后量子双算法 keystore。签名插件 `etc/plugins/sign-request.mk`/`etc/plugins/local-sign.mk`。

## 外部连接

协议上：PLDM 消息经 MCTP 传输（与 NSM/SPDM 共信封，`src/nv/mctp/driver.cpp:381` forward 链）；C++ 侧客户端在 `src/nv/pldm/`，固件镜像解析在 `src/nv/fw_parser/`（`src/nv/fw_parser/fw_parser_mcu.h:26` 的 nv::fw_parser::mcu 命名空间 + fw_parser_ap.cpp 的 AP 镜像）。构建上：`etc/platforms` 出 mcxn556-core0/core1 变体；CI 双工程矩阵 `.gitlab-ci.yml:20`（PLATFORM mcxn556-both）/`:24`（mcxn556-core0）。镜像打包：libexec 的 pldmfwpkg 打包器（配 pldmfwpkg-gen.py）。

## 数据流

一次固件更新：BMC 发 RequestUpdate（带固件组件描述）→ `corepdk/modules/pldm-fd/src/fwupdate/pdk-pldm-fwupdate-cmd.adb:225` 初始化的上下文校验组件/版本 → 进 Transfer 分块收数据（上下文记 Last_Transfer_Size，状态经 `pdk-pldm-fwupdate-state.adb:29` 的 Change_State 迁移 Idle→Lc→Rdy_Xfer）→ 数据落地 flash（跨核 flash 服务）→ Verify 阶段校验签名 → `corepdk/modules/pldm-fd/src/fwupdate/pdk-pldm-fwupdate-cmd.adb:136` 出结果报告（失败路径有 `:295-296` 的逐阶段 CC 码）。打包侧：pldmfwpkg-gen.py 把 `src/nv/fw_parser/fw_parser_mcu.h:26` 系解析过的镜像打成 PLDM 包 → `libexec/tools/sma-mcxn556-signing-service/src/scripts/sign.py` 按 `policy.json:29-30` 双算法签名 → BMC 分发。

## 设计决策

①**为什么是 Ada**——固件更新是安全关键路径（写 flash+验签），Ada 的强类型/边界检查/SPARK 可验证性是选型理由；代价是团队技能栈分裂与 GNAT 工具链依赖，这也是 UBS 需要 GPR 工程胶合的原因；②**命令/状态分文件**——2001 行 cmd.adb 纯应答、620 行 state.adb 纯状态迁移（`pdk-pldm-fwupdate-state.adb:62/:119/:172` 三 handler），可分别测试；③**限速内置**（`pdk-pldm-fwupdate-cmd.adb:157`）——防 BMC 压垮 MCU 的 flash 写带宽，协议层自带流控；④**双签名算法 keystore**（`policy.json:29-30`）——ECDSA P384 过渡期与 MLDSA-87 抗量子并存，2025+ 固件签名演进的活样本。

## 新人提示

读 PLDM 从 `corepdk/modules/pldm-fd/src/main.adb:20` 进 → `pdk-pldm-base-cmd.adb:38`（发现命令最小）→ `pdk-pldm-fwupdate-cmd.adb:225` 跟上下文字段含义。Ada 语法不熟先看 `pdk-pldm-fwupdate-cmd.adb:47-104` 的序列化原语族（最简单又最能体现 Ada 风格）。构建问题先跑 `mcu_build.sh`（usage 在 `mcu_build.sh:6-11`）确认 PROJECT/PLATFORM/BOARD/MODE/SIGN_KEYSET 组合合法。"固件包打出来装不上"九成在打包器组件描述与 fw_parser 解析不一致。改 UBS 流程记得 `ubs.py:28` 起的导出装饰器约定是唯一入口，别绕过它直接调 makefile。签名算法配置改动只碰 `policy.json:29-30` 与 keystore。
