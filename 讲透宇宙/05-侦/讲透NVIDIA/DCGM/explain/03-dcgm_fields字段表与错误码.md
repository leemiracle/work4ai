# 03 · dcgm_fields 字段表与 dcgm_errors 错误码：6094 行的元数据巨表

## 角色定位

dcgmlib/dcgm_fields.h（3993 行）+ dcgmlib/src/dcgm_fields.cpp（6872 行）构成 DCGM 的**字段字典**：每个可监控量的 ID、类型、单位、显示位宽、NVML 映射与短标签全在这。dcgm_fields.cpp:213 的 DcgmFieldsPopulateFieldTableWithFormatting 是全仓最大函数——从 213 行到 6306 行 return，**整整 6094 行**逐字段登记。姊妹文件 dcgm_errors.h（733 行）定义诊断/健康错误码全集，靠"尾加"纪律维持二进制兼容。两者都是"数据表代码化"的极端样本：没有 YAML、没有运行时加载，元数据即源码。

## 内部结构

字段 ID 分段是全局秩序：设备/系统字段占低位（如 GPU_TEMP 150=dcgm_fields.h:619、XID_ERROR 230=dcgm_fields.h:806、ECC_MODE 300=dcgm_fields.h:914、ECC SBE/DBE 总量 310-313=dcgm_fields.h:924-941）；NVSwitch 段 700-899（DCGM_FI_FIRST_NVSWITCH_FIELD_ID 700=dcgm_fields.h:1950，LAST 899=dcgm_fields.h:2521，MAX_NVSWITCH_FIELDS=200=dcgm_fields.h:2527）；PROF 段从 1001 起（GR_ENGINE_UTIL_RATIO 1001=dcgm_fields.h:2538、SM 1002=dcgm_fields.h:2544、PCIE_TX_BYTES 1009=dcgm_fields.h:2586）。单个字段登记走 DcgmFieldsPopulateOneFieldWithFormatting（dcgm_fields.cpp:140，十参数：fieldId/类型/尺寸/tag/scope/NVML 映射/短标签/单位/实体组/位宽）；巨函数头部前三条是 DRIVER_VERSION（"DRVER"，dcgm_fields.cpp:216-227）、NVML_VERSION、CUDA_DRIVER_VERSION 等全局字段；末尾一条是 bind_unbind_event（dcgm_fields.cpp:6295-6305）。NVLink profile 字段不手写 200 条，由 DcgmFieldsPopulateNvLinkProfileFieldRange 按链路号 ×Rx/Tx 循环展开（tag 形如 nvlink_l3_rx_bytes）。索引侧：DcgmFieldsPopulateHashTable（dcgm_fields.cpp:6362）建短名→ID 哈希（哈希回调 dcgm_fields.cpp:6313-6341），对外查询 API 为 DcgmFieldsInit（dcgm_fields.cpp:6403）、DcgmFieldGetById（:6450）、DcgmFieldGetByTag（:6461）、Term（:6424）。

错误码三张表强制对齐：dcgm_errors.h:31 起 dcgmError_enum（DCGM_FR_OK=0=dcgm_errors.h:33、UNKNOWN=1、PCI_REPLAY_RATE=3=dcgm_errors.h:36……DCGM_FR_ERROR_SENTINEL=133=dcgm_errors.h:174，注释明言 MUST BE THE LAST）；消息表 195 个 DCGM_FR_*_MSG 宏（dcgm_errors.h:234 起）与建议动作表 DCGM_FR_*_NEXT（dcgm_errors.h:526 起）。dcgm_errors.c 用 X-macro 一行合成三表（DCGM_ERROR_TABLE_ENTRY，dcgm_errors.c:20-21），展开为 dcgmErrorMeta[133] 数组（dcgm_errors.c:23），每项携带 severity（ISOLATE/MONITOR/RESET/CONFIG/TRIAGE）与 category（HARDWARE_PCIE/MEMORY/NVLINK…），如 DCGM_FR_XID_ERROR→TRIAGE/SOFTWARE_XID（dcgm_errors.c:125）。

## 外部连接

DcgmFieldGetById 是全仓最高频查询：watch 表到期校验（common/DcgmWatchTable.cpp:326）、CacheManager 采集循环（DcgmCacheManager.cpp:6077）、dcgmi profile 展示（dcgmi/DcgmiProfile.cpp:67）都调它。字段 ID 段直接喂给模块路由 DcgmWatchTable::IsFieldIgnored（DcgmWatchTable.cpp:184-194）。错误码的生产者是 health/policy/nvvs/diag 模块，消费者是 dcgmi health 与 dcgmDiag 输出层；dcgmErrorGetPriorityByCode（dcgm_errors.c:159）与 dcgmErrorGetCategoryByCode（:171）是 severity/category 的唯一查询口，越界一律返回 DCGM_ERROR_UNKNOWN（:161-167）。

## 数据流

进程初始化时 DcgmFieldsInit（dcgm_fields.cpp:6403）→ PopulateFieldTableWithFormatting（:6410 调用）建静态字段表 → PopulateHashTable 建短名索引，此后只读。监控数据流里它只出元数据：watch 表拿 fieldMeta 判断到期字段、CacheManager 拿 nvmlFieldId 决定 NVML 直采还是定制查询、dcgmi 拿 tag/位宽渲染表格。错误流则是模块产生 dcgmError_t 编码 → 结构化消息给 core → dcgmErrorGetFormatMsgByCode（dcgm_errors.c:183）取消息模板渲染给用户。

## 设计决策

1) **6094 行单函数**看似失控实为纪律：登记顺序即字段 ID 顺序，编译器保证无重复无遗漏，新增字段只能"尾加"，与错误码同款哲学。2) **ID 分段**同时服务三件事：IsFieldIgnored 的模块路由、dcgmi 输出分组、SDK 兼容（deprecated 别名不占新值，如 DCGM_FI_PROF_PCIE_TX_BYTES 旧名 dcgm_fields.h:756 指向新 ID；错误码 DCGM_FR_CLOCK_THROTTLE_THERMAL=dcgm_errors.h:42-43 是 DCGM_FR_CLOCKS_EVENT_THERMAL 的别名）。3) **X-macro 三表合一**（enum+MSG+NEXT+meta）杜绝"改了枚举忘改串"的经典漂移，漏一项直接编译错。4) NVLink profile 用循环生成而非复制粘贴，链路数变化只改一处。5) GPM 指标映射单独成 DcgmFieldIdToNvmlGpmMetricId（约 325 行大映射），与主表解耦，GPM 代际差异不污染字典主体。

## 新人提示

加字段四步：dcgm_fields.h 分段内 #define → Populate 巨函数尾部（bind_unbind_event dcgm_fields.cpp:6295 之后）加登记调用 → 补短标签 → 跑 dcgm_fields_tests.cpp（约 360 行）验证哈希与位宽。加错误码也是四处同步：enum 尾部（SENTINEL 前）+ _MSG + _NEXT + dcgm_errors.c 表项（dcgm_errors.c:24-159 内尾部追加），并递增 SENTINEL——dcgm_errors.h:29 的注释就是这条军规。查"这个字段哪来的"直接 grep 短标签（如 DRVER）比 grep 数字 ID 快；改显示宽度用 getWidthForEnum 的位宽枚举而非裸数字。dcgm_fields_internal.hpp 是引擎内部扩展视图，外部消费者只见 dcgm_fields.h。
