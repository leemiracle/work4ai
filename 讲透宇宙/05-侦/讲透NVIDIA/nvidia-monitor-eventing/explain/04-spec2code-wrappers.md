# 04 · spec2code 生成器家族与 wrapper 体系

## 角色定位

这条线回答"配置和工具从哪来"：spec2code 家族把硬件规范（RAS 类别表、FPGA 寄存器表、故障汇总）编译成事件配置与文档——配置是生成物不是手写物；wrapper 体系把 BMC 上的裸命令（fpga/i2c/NVLink/PCIe 状态查询）包成统一接口的 bash 脚本，供事件配置的 CMDLINE accessor 与 selftest 消费。两者合起来是"规范→可执行监控"的自动化生产管线。

## 内部结构

**spec2code 家族**（仓根 `spec2code/`，注意不在 tools/ 下）：

- `rascat_spec2code`（1156 行，家族最大）：解析 RAS 类别规范生成事件配置与配套文档——核心类 `ErrorCatalog`（rascat_spec2code:118），设备模式/上卷/OOC 三个生成器 `get_device_pattern`（rascat_spec2code:777）/`get_rollup_device`（rascat_spec2code:786）/`get_ooc_device`（rascat_spec2code:796）；手册 `spec2code/rascat_spec2code.md`（300 行）。
- `fpga_alert_spec2code`（571 行）：寄存器规范表→事件定义（`FpgaRegtbl` fpga_alert_spec2code:135，`bitrange_to_bitmask` fpga_alert_spec2code:117）；`gpiomon_event_generator`（192 行）；`glacier_spec2code`（46 行）；`redfish_eventing_recipe_validator`（284 行，入口 main redfish_eventing_recipe_validator:489）：Redfish 事件配方合规校验器，守住生成物的出口质量；骨架模板 event-info-skeleton.xsh。
- 姊妹目录 `tools/vulcan-faults/`：`data/in/vulcan-faults-summary.csv`（3436 行故障汇总）→ 生成 event_info 骨架，产出 `data/out/vulcan-faults-smbpbi-op-code.tsv`。

**注入验证线**（生成的配置要被证明能用）：

- `tools/event_injector`（394 行）调度 `tools/modules/` 两注入器：event_accessor_script.py（428 行，改写设备属性到触发条件值）与 event_logging_script.py（155 行，直接向 D-Bus Logging 注条目），基类 injector_script_base.py（232 行）。
- 共享判定 `tools/modules/com.py`（399 行）：`replace_last_range_if_repeated`（com.py:205）与 `expand_range`（com.py:228）做设备区间展开、`compare_mandatory_event_fields`（com.py:386）做字段比对、Redfish 数据比对——注入结果与预期的一致性检查。
- 端到端验证 `tools/event_validation.py`（865 行，测试编排类 `InjectTest` event_validation.py:318，CLI 入口 main event_validation.py:817）：注入后断言 Redfish 日志/健康状态；`tools/nvidia-xid-event-handler`（442 行）消费 Xid 错误码。
- 解析器/探测器家族：fpga_pwrfail_parser、gb200_pwrfail_parser、glacier_boot_status_parser、ocp_recovery_status_parser、mcu_event_parser、mctp-error-detection、mctp-vdm-util-wrapper。

**wrapper 体系**（`tools/wrapper-tools/` + 五个成品目录）：

- 生成器 `tools/wrapper-tools/src/python/generate-wrappers.py`（mockup 定义类 `WrapperMockupDefs` generate-wrappers.py:28）从 mockup 定义模板生成 bash 包装脚本；模板 `wrappers-mockup-definition_dat-obmc=adf4a8847.tsv`（文件名钉住基线 commit adf4a8847）；共享库 common.py（argparse CSV/IO 扩展）。
- jq 查询四件：testpoints.jq、commands-list.jq、tabular-testpoints.jq、tabular-testpoints-CMDLINE.jq——把 DAT/报告转表格。
- 性能线：performance-test-deploy-pkg/wrappers-exec-time.sh 部署测耗时；performance-test-results/ 留存三机型 CSV（2022-10-08 LunaDP-B1-12、2022-10-10 Sravanthi、2022-10-12 VikingDP2-B2-45/46，及 B2-28 的 original/optimized device-id-norm 对照）。
- 成品五件：`tools/wrapper_nvlink_wp_status/nvlink-wp-status-wrapper`（686 行最大）+ 测试脚本与 nvlink_wp_profile.csv、wrapper_pcie_status/pcie_wrapper、wrapper_i2c_status/i2c_wrapper、wrapper_fpga_register_table/fpga_regtbl（配 tools/fpga_regtbl 寄存器表）。
- 调试底座：tools/dbus_tester.cpp（裸 D-Bus 探测）、tools/jtag（jtag.h 598 行寄存器访问）。

## 外部连接

上游输入是硬件团队规范（RAS 手册/寄存器表/Sheets）；生成物落入 examples/event_info.json（1515 行蓝本）与运行时配置，装载侧由 config_schemas.cpp（180 行六 schema）+ diagnostics（03 篇 JsonSchemaTest 等）把守。wrapper 输出被 DataAccessor 的 CMDLINE 来源消费（02 篇），也是 selftest 测试点的执行体（03 篇）；注入验证线直接驱动 EventDetection 与健康上卷的端到端回归；vulcan-faults 与 rascat 的产物经 redfish_eventing_recipe_validator 才能合入。

## 数据流

生产流：硬件规范（CSV/TSV/手册）→ rascat_spec2code/fpga_alert_spec2code/vulcan-faults 生成 event_info 片段 → event-info-skeleton.xsh 模板定型 → redfish_eventing_recipe_validator 校验 → 合入 event_info.json → diagnostics 开机体检 → EventInstantiator 实例化。验证流：event_injector 调度 modules 注入器 → com.py 展开设备区间生成目标实例 → 改属性/注日志 → EventDetection 匹配 → event_validation.py 断言 Redfish 日志与健康 → 回归结论。访问流：测试点 CMDLINE accessor → 调 wrapper 脚本（统一参数/输出约定）→ 脚本内跑 fpga/i2c/nvlink/pcie 裸命令 → 结构化 stdout 回给 accessor 解析。

## 设计决策

- **规范即真理源**：3436 行故障 CSV、寄存器表、RAS 类别手册直接编译成配置——手写配置的漂移问题被生成管线消解，重生成永远可重复。
- **校验器守出口**：redfish_eventing_recipe_validator（284 行）独立于生成器存在——生成器可以换代，Redfish 合规这条线不放松。
- **注入器成对**：accessor 注入（改数据面）与 logging 注入（直接注日志）覆盖两条触发路径——匹配逻辑与上报逻辑各自可独立回归。
- **wrapper 统一接口**：五个成品 wrapper 都走 generate-wrappers 的同一模板约定——新硬件接入的边际成本是一份 mockup TSV 行而不是一个新工具。
- **性能数据入库**：exec-time CSV 与 original/optimized 对照留存——模式语言规范化（01 篇）的每一步优化都有机型级证据。

## 新人提示

读序 spec2code/rascat_spec2code.md → 手跑一次生成对照 examples/event_info.json 的片段；写新事件先问"规范表里有没有这一行"再决定手写还是生成；wrapper 调试从 wrapper_nvlink_wp_status/nvlink-wp-status-wrapper-test.sh 入手；改 com.py 的比对逻辑后必跑 event_validation.py 全套；mockup TSV 文件名里的 commit 后缀（adf4a8847）是基线锁，更新要连生成器一起动。
