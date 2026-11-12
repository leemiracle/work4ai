# 讲透 power_manager.cpp（主服务，1356 行）

## 角色定位
nvidia-power-manager 守护的实现体：把 powermanager.json 声明式配置变成活的 D-Bus 属性监视/动作引擎 + 机箱功耗上限（power capping）状态机。入口在 power_manager_main.cpp（64 行，只做装配）。

## 内部结构
三块：①工具层 util（:43-196）——getService 经 ObjectMapper 三段查（:43/:76/:98）、loadJSONFromFile（:108）、/etc/powerCap.bin 读长度/载入/落盘（:131/:156/:176）；②PowerManager 构造（:197）——载配置、恢复持久化 powerCappingInfo（memcpy :218）、按 powerCappingAlgorithm 建模块对象（:234-257）、按 powerCappingConfigs 建 Property 对象（:259-323，areaObjs/propertyObjs 两个容器）；③capping 状态机——updatePowerCappingLimit（:422）按 PowerMode 选 Q/P/当前三档 limit（:426-437）再按百分比分发（:445-466）；updatePowerCappingStructure（:506）把 JSON 全量灌结构体并 caluclateChecksum（:472）+dump；checkChecksum（:489）验旧档，坏则重建。

## 外部连接
配置 powermanager.json（装在 /usr/share/nvidia-power-manager/，src/meson.build:6）；持久化 /etc/powerCap.bin（JSON powerCappingSavePath）；动作目标全是 D-Bus 服务（State.Chassis/Logging.IPMI/com.Nvidia.PsuEvent…）；Property 层由 power_manager_property.hpp 的模板类（:167）落地，错误类型 NotSupportedInCurrentMode（hpp:55）/ChassisLimitOutOfRange（hpp:73）。

## 数据流
事件流：被监视属性变化（如 chassis0 CurrentPowerState、psu_drop_to_1_event Enabled）→ 触发条件比对（conditionBlock+timeDelay）→ 执行动作（methodName+appendData 组包，OEM data 转 oemKeyHandler）。capping 流：属性写 PowerCap → mode 判定 → chassis limit 分发到各模块 power limit → 写 /etc/powerCap.bin。注意 maxTotalPowerConsumption=100（:41）硬顶：算法节百分比之和超 100 直接报配置错误（:245）。

## 设计决策
①行为全数据驱动——SEL 文案、触发条件、属性集合都在 JSON，换平台改配置不改码；②持久化用结构体直存+校验和（:593-599 先清零再算，含 checksum 自身置 0 的两遍法）而非 JSON——BMC 掉电场景解析零依赖；③Q/P 双模式上限（chassisPowerLimit_Q/_P，:577/:582）为冗余电源策略留档；④main 双总线（power_manager_main.cpp:46-53，文件头 :19 保留 IBM 2019 版权）：classic bus 同步查 mapper、asio bus 供 object_server——sdevent attach 后从未 run，属残留结构。

## 新人提示
先读 src/README.md 再读本文件，配置键与代码字段的对应都在那。两个易错点：caluclateChecksum 是上游拼写错误（:472）不是你眼花，grep 时按错拼搜；PowerCappingInfo 结构体带 checksum 字段参与序列化（:593-595），改字段必须同步改读写两侧，否则旧 bin 全部校验失败走重建。
