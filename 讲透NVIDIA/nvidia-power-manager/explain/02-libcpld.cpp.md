# 讲透 libcpld.cpp（远端 MB/MID FPGA 烧写，928 行）

## 角色定位
cpld_utility 工具族的传输层：经 I2C 向远端 MotherBoard/Motherboard-Image-Device FPGA 烧写镜像。与 dragonCpld.cpp（本机 Lattice CPLD 状态机）平行分工——一个烧"别人家的"FPGA，一个刷本机 CPLD。被 cpld_utility/main.cpp（133 行 CLI）与 D-Bus 触发的 updateCPLDFw_dbus_log_event 打包调用。

## 内部结构
两个几乎对称的入口：flash_remote_mb_fpga_image（:57）与 flash_remote_mid_fpga_image（:488）——共享同一套骨架（打开 /dev/i2c-N、校验镜像、分页写、忙等），差异只在页大小/地址布局/命令序列。通用原语：wait_until_not_busy（:21）——写 00 20 00 20 四字节命令后读 4 字节状态，bit0 判 STATUS_BUSY，usleep(delay)+TRY_TIMES 轮询上限；实际 I2C 收发走 std_send_i2c_cmd（libi2c.cpp 提供）。

## 外部连接
上承 cpld_utility/main.cpp 的 CLI 参数（bus/image_sel/image/id）；日志双通道——printf（debug_h/debug_l 两档本地开关）+ emitLogMessage 发 Redfish 事件（target_deter/ver_failed 等枚举，配套 65 行的 updateCPLDFw_dbus_log_event.cpp）；flashing_progress 出参供调用方做进度上报。

## 数据流
烧写序列（以 MB 为例）：open /dev/i2c-N（O_RDWR|O_NONBLOCK，:82）→ emitLogMessage(target_deter) → 读镜像文件 stat + open（:92-99）→ **尺寸必须是 MB_PAGE_SIZE_BYTES 整数倍否则 ERROR_WRONG_FIRMWARE**（:100-106）→ malloc 缓冲读入 → 逐页：组命令帧（页地址+数据）→ std_send_i2c_cmd → wait_until_not_busy 把守（:205/:232/:260/:356）→ 关键阶段间再握手 → 完成后版本校验与日志收尾。MID 版本同构（:643/:670/:698/:794 四处忙等点）。

## 设计决策
①忙等而非中断/信号——远端 FPGA 无事件线可用，状态寄存器轮询是唯一手段，TRY_TIMES 上限防挂死；②MB/MID 两函数复制粘贴式对称（928 行里两份 400+ 行近似代码）——接受重复换取各自协议演化的自由度，代价是改公共逻辑要改两处；③页对齐硬校验前置（:100-106）——错配镜像直接拒绝，避免烧到一半才发现地址错位；④O_NONBLOCK 打开（:82）但实际语义靠 std_send_i2c_cmd 的同步 ioctl，文件标志只是防御。

## 新人提示
调烧写失败先看两类输出：printf 的 read_buffer hex（debug_l 开）确认 FPGA 状态字、journal 里 Redfish 事件确认走到了哪个阶段。镜像不页对齐报 "Error size file" 是最常见前置失败（:107-108）。注意 MB_PAGE_SIZE_BYTES/TRY_TIMES/DELAY_1000MS 等常量在 libcpld.h（154 行）——注释 "DELAY_1000MS // 1ms"（:260/:698）单位名与实义不符，是上游注释错误。
