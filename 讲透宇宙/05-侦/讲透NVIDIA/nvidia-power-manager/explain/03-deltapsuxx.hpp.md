# 讲透 deltapsuxx.hpp（Delta PSU 固件升级，783 行头文件）

## 角色定位
psu_utility 的协议核心：Delta 新一代 PSU 的固件升级命令序列，覆盖解锁、boot 标志、输出禁用/恢复、逐段传输、CRC16 校验、激活全流程。**783 行全部是 .hpp 内联实现**（无对应 .cpp）——工具族里的"厚头文件"。

## 内部结构
`class DeltaPsu : public I2c`（:200）。数据表：MCU_hdlr——每个可升级 MCU 段一条 {APPCRC_STA, FLASH_STA, Delay_1/2/3} 五元组（:194-197），fwupdate 按 section 参数匹配段（:345-349）。错误面：ErrorStatus 枚举 + statusToString（:121-154，含 ERROR_WRONG_CRC16_CHKSM 等文案）。寄存器常量 REG_TRANSMIT_CRC=0xF4（:84）。

## 外部连接
基类 I2c（include/i2c.hpp）提供总线读写原语；被 dragonDeltaPsu.cpp（208 行，实现解锁/擦除/CRC 收发/激活四段回调）与 dragonChassisBasePsu.cpp 的编排（checkManufacturer :42 防刷错厂商 → fwUpdate :78）消费；日志 VERBOSE 流受 CLI -v 控制（psu_utility/main.cpp）。

## 数据流
fwupdate(imageFilename, section)（:323）主序列：读镜像 → 计算 CRC16（:388-409，"FW Image CRC16 Checksum" 日志点 :405-409）→ unlockDevice（:213）→ 进入 :441-484 的解锁/boot 标志/输出禁用重试块（unlock 失败计数与重试）→ 逐段擦除+发送（按 MCU_hdlr 的 Delay 参数节拍）→ "#8 Write CRC16"：组 0xF4 命令帧（REG_TRANSMIT_CRC :664，byte count 0x03，MCU_ID + CRC16_LO/HI + PEC，:659-670）→ activate（:767）。statusToString 把每步错误翻译成可读文案。

## 设计决策
①升级单元是 section（每 PSU 内多 MCU 各自独立镜像段）而非整机一把梭——失败可只重刷坏段；②CRC16 前后双验：传输前算一次（:405），写 CRC 寄存器前再复核（:669-670 "Re-Check"）防长流程中缓冲被改；③输出禁用与恢复围绕升级窗口——升级期间 PSU 输出必须先禁用以防半新半旧固件带载；④头文件即实现——供 psu_utility 多个调用单元直接 include，避免为单一工具建库。

## 新人提示
排障看两处：VERBOSE 输出的 "#N ..." 步骤号（如 "#8 Write CRC16"）直接对应协议步骤；statusToString 文案定位 ErrorStatus 枚举。段号 section 来自 main.cpp 解包后的文件名约定，段表不匹配会在 :345-349 静默失败——升级"没反应"先查 section 值。配套 dragonChassisPsuUpdate.cpp（90 行）是 Dragon 机箱整包编排，含多 PSU 顺序调度；入口 main.cpp（395 行）先 execl("/bin/tar") 解包（:43/:65）再 fcntl F_WRLCK 文件锁互斥（:91-112），两个并发升级实例靠锁而非进程检查互斥。读这份头文件建议自上而下按常量表（:84 起）→ 错误枚举（:121-154）→ MCU_hdlr 段表（:194-197）→ DeltaPsu 类（:200）的顺序，协议参数与代码结构一一对应。
