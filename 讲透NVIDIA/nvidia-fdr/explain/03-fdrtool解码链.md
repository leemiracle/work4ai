# 03 fdrtool 解码链：Redfish 收 dump → cobsr+protobuf 解码 → 三后端

## 角色定位

fdrtool 是 FDR 的离线半边：BMC 记录器落盘的 dump 是 protobuf 二进制，分析工程师用 `fdrtool/fdrtool.py`（587 行 CLI）完成"收集→解包→解码→入库"。它把黑匣子数据接进三种消费生态：JSON（脚本翻看）、SQLite（SQL 查询/跨 dump 联合）、InfluxDB（时序可视化）。校验臂（tools/data_validation/）负责 dump 与 telemetry-agent 对账。

## 内部结构

**收集**（`fdrtool/fdrtool.py`）：`fdrtool/fdrtool.py:381` CollectFdrDump 用 redfish 库（`fdrtool/fdrtool.py:25` import）连 BMC——`fdrtool/fdrtool.py:391` 调 `/redfish/v1/Systems/HGX_Baseboard_0/LogServices/FDR/Actions/LogService.CollectDiagnosticData` 触发收集，再取 tar；`:373` 查 LogServices/FDR 状态。DEMO 变体 `fdrtool/fdrtool.py:531` CollectFdrDump_DEMO 走本地样例；`-ul/--use_local`（`:176`）直接吃离线 tar。主流程 `fdrtool/fdrtool.py:153` main：收集/解包 → decodingDump → 后端入库。

**解码核心**（`fdrtool/catalog/catalog.py:70` class Catalog）：目录装载 → 逐文件解码：`fdrtool/catalog/catalog.py:422` 用 protobuf 内部 `_DecodeVarint32` 读 varint 长度前缀切帧，`fdrtool/catalog/catalog.py:452` `cobsr.decode` 解 COBS-R 封装得到 protobuf 消息体；版本不符抛 `fdrtool/catalog/catalog.py:104` VersionMisMatch（异常在 `fdrtool/exception.py`）；keeper 特判在 `fdrtool/catalog/catalog.py:592`。CatalogEntry 逐条分流三后端：`fdrtool/catalog/json.py`（记录→JSON）、`fdrtool/catalog/influx.py`（InfluxDBConnection+异步批量回调+LineProtocol）、`fdrtool/catalog/sqlite.py`（建表写批+CreateCombinedViews 跨 dump 视图）。后端选择走函数体内延迟相对导入（NOTES batch-5 甄别）。

**线格式契约**：`fdr_logs_schema.proto`（143 行 proto3/fdrpb/11 个 message）——C++ 与 Python 共用；fdrtool 侧由 `fdrtool/Makefile` 的 protoc 规则生成 pb2（生成物，无仓内边）。

**校验臂**：`tools/data_validation/data_validator.py`（269 行）双向 diff telemetry-agent vs FDR dump；`tools/data_validation/check_fdr_telemetry_coverage.py`（355 行）生成平台覆盖报告；`tools/data_validation/telemetry_catalog.py`（1007 行）是遥测目录 Python 侧核心（Catalog/CatalogEntry/URIExpansion、ExpandTc 展开、FetchMRDValues 取 MRD）。两者都是 fdrtool 主流程延迟导入的校验步骤（NOTES batch-5 手补边）。

## 外部连接

- 配置：`fdrtool/config.yaml`（BMC 地址/凭据/后端，configargparse）；依赖 `fdrtool/requirements.txt`（redfish/influxdb-client/tqdm/cobs 等）。
- 上游：C++ 记录器的 FDRStore 产出（`fdr_store.cpp:74` append 的 delimited protobuf）；boot 计数标注源 `tools/FdrBootCounter.sh`。
- 生态：MRD 取值与记录器同源；PPF 侦察工具 `tools/dbus_dump/dbus_dump.sh`（413 行 14 函数，busctl/gdbus/dbus-send 三后端自适应）服务 PPF 编写而非解码。

## 数据流

BMC 侧：FDRStore 追写 keeper+样本 → Redfish CollectDiagnosticData 打包 tar。主机侧：CollectFdrDump 下载 → 解包出目录树 → Catalog 扫描文件 → 逐条 [varint 定长 → cobsr 解封 → protobuf parse → 版本校验] → CatalogEntry 生成 → 按 decode_format 分流 JSON/Influx/SQLite → 校验臂对账（豁免清单按平台）。

## 设计决策

1. **COBS-R + varint 长度前缀的流式帧**：样本文件是追加式的（记录器侧只 append），COBS 保证帧内无分隔符歧义、varint 前缀定界——解析端一遍流式读，与 FDRStore 的 SerializeDelimitedToOstream（`fdr_store.cpp:101`）严格对偶。
2. **三后端插件式分流**：CatalogEntry 按配置实例化一种后端，延迟导入隔离可选依赖（没有 influxdb-client 也能跑 JSON 模式）。
3. **版本硬校验**（VersionMisMatch）：线格式跨 BMC 版本演进，静默错解比报错更危险——宁可拒解。
4. **收集与解码一体但可离线**：DEMO/--use_local 双入口让无 BMC 环境也能测解码链——工具的可测试性设计。
5. **校验独立成臂**（data_validator/check_coverage）：解码正确性与遥测覆盖度分开度量，豁免清单（`tools/data_validation/platform/` 四平台 yaml）显式管理技术债。

## 新人提示

- 第一次跑用 `--use_local` + 本地 tar，绕开 BMC 依赖；配置抄 `fdrtool/config.yaml`。
- 解码报 VersionMisMatch 先核 fdr_logs_schema.proto 与 BMC 端版本，再核 protoc 生成物是否过期（`fdrtool/Makefile` 重新生成）。
- SQLite 后端的 CreateCombinedViews 是跨 dump 对比分析的入口，比逐个 JSON 翻文件高效。
- 改 proto 记得两头：C++ 记录器（`fdr_logs_schema.proto` 直接编译）与 fdrtool（protoc 生成）都要重建。
