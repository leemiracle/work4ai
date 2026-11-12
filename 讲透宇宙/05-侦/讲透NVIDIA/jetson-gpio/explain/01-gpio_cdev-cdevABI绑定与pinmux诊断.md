# 精讲 01：gpio_cdev.py——ctypes 镜像内核 cdev ABI 与 /dev/mem pinmux 诊断

## 角色定位

`lib/python/Jetson/GPIO/gpio_cdev.py` 是运行时库与内核之间唯一的地基层：上接 `gpio.py` 的全部主 API（setup/output/input/事件注册最终都落到这里的函数），下接 Linux GPIO 字符设备（cdev）ABI 与 Tegra pad 寄存器物理内存。它让整个库不依赖任何 C 扩展、纯 pip 可装——代价是必须手工维护一份与内核 uapi 逐字段一致的 ctypes 镜像。

## 内部结构

三条支柱。其一，**ioctl 魔数**（`gpio_cdev.py:47-52`）：`GPIO_GET_CHIPINFO_IOCTL = 0x8044B401` 等 6 个请求码直接写死，不依赖头文件换算。其二，**结构体镜像**：`gpiochip_info`（`:58`）、`gpiohandle_request`（`:74`，内嵌 64 线 offsets/values 数组与对齐字段）、`gpioevent_request`（`:125`）；任何字段顺序或对齐错误都会让 ioctl 返回 EINVAL 而非崩溃，极难排查。其三，**PadCtlRegister 位域**：`check_pinmux` 用 dataclass 解析 pad 寄存器，`_GPIO_IN_OUT_MASK = (1<<6)|(1<<4)`（`:291`）对应 bit6 输入输出、bit4 tristate，bit10 区分 GPIO/SFIO 复用。

函数族按生命周期排布：`chip_open`（`:151`）按设备名开门 → `chip_check_info` 取 label/行数校验 → `chip_open_by_label`（`:185`）遍历 `/dev/gpiochip*` 用 label 找目标芯片（`gpio.py:122` 的调用点）→ `request_handle`（`:240`）构造方向请求 → `open_line`（`:213`）GET_LINEHANDLE_IOCTL 拿 fd → `get_value/set_value`（`:273/:287`）读写电平；事件线走 `request_event`（`:258`）拿事件 fd 交给 gpio_event 模块。

## 外部连接

被 `gpio.py`（主 API 的每条 setup/cleanup/input/output 路径）与 `gpio_event.py:47`（`from Jetson.GPIO import gpio_cdev as cdev`，事件请求结构体复用）消费；反向依赖 `gpio_pin_data.py` 的 ChannelInfo（`gpio_cdev.py:35`）与 constants 的 OUT/HARD_PWM（`:36`）。引脚表里的 chip label 与 PADCTL 寄存器地址两列数据就是为本文件的两个消费者（chip_open_by_label 与 check_pinmux）准备的。

## 数据流

以 `GPIO.setup(18, OUT)` 为例：`gpio.py` 查通道表得 chip label + line offset → `gpio_pin_data.PinInfo`（`gpio_pin_data.py:536`）→ `chip_open_by_label` 遍历匹配 → `request_handle` 填 `gpiohandle_request`（lineoffset/consumer 标签/初始电平）→ `open_line` ioctl 拿 line_handle fd 存入 ChannelInfo → `check_pinmux`（`gpio.py:131` 调用）读 pad 寄存器核对方向。读输入则是 `GPIO_GET_LINE_VALUES_IOCTL` 把电平写进 `gpiohandle_data.values[0]`。

## 设计决策

- **ctypes 而非 C 扩展**：单文件纯 Python，跨 Jetson 模型免编译，代价是 ioctl 码与结构体布局固化（内核 cdev ABI v1 稳定，风险可控）。
- **/dev/mem 只读映射**：`check_pinmux`（`:322`）`os.open('/dev/mem', O_RDONLY|O_SYNC)`（`:329`）+ `mmap` 映射 **2 页**（`:335`）——注释明示这是处理寄存器跨页边界；方向不符时只告警并给出 busybox devmem 修正命令，双向态直接放行，权限不足降级为 `:373` 友好告警。诊断只读、绝不写物理内存。
- **失败模式偏宽容**：pinmux 检查失败不阻断 setup，因为多数用户烧录的设备树已配好 pinmux，检查只是防呆。

## 新人提示

排查"setup 报 RuntimeError/告警"先看三处：`gpio.py:33-34` 的导入期权限闸（gpiochip 不可写）、`check_pinmux` 的方向告警（设备树没配复用）、chip label 对不上（引脚表与实际内核版本不一致，走 `dev/update_pinmux_registers.py` 再生成）。结构体镜像一旦怀疑漂移，对照内核 `include/uapi/linux/gpio.h` 逐字段比。本文件是理解"用户态怎么裸操作硬件"的最佳教材：ioctl 码、对齐、mmap 三个知识点齐活。
