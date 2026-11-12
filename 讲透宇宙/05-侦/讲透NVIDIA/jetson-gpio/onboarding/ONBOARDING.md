# jetson-gpio 讲透导航（Onboarding）

> 基于图谱 141 节点/220 边/6 层/6 步 tour @ commit d46fefb5，全部行号锚经源码核实（2026-11）。
> 配套：`../deepwiki/`（官方 wiki 全量）、`../explain/`（核心文件精讲 2 篇）、`../README.md`（勘误与全链状态表）。

## 1. 这个仓库是什么

NVIDIA 官方的 Jetson 系列 GPIO 控制 Python 库，API 语义完整复刻 RPi.GPIO（树莓派事实标准），让既有树莓派脚本零改动跑在 Jetson 硬件上。但它不是 RPi.GPIO 的 fork：底层完全重写为 Linux **GPIO 字符设备（cdev/gpiod）ABI**，而非 RPi.GPIO 时代的 sysfs `/sys/class/gpio` 旧接口。一个库同时干了三件事：

1. **运行时库**：`setmode/setup/output/input/PWM/事件检测` 全套 RPi 风格 API（`lib/python/Jetson/GPIO/gpio.py`，542 行起是 PWM 类）；
2. **RPi 兼容垫片**：`lib/python/RPi/GPIO/__init__.py:1` 一行 `from Jetson.GPIO import *` 即让 `import RPi.GPIO as GPIO` 的老代码直接可用（`samples/simple_out.py:22` 正是这么用的）；
3. **板级数据工程**：11 个 Jetson 模型的引脚数据库 + 从内核 pinctrl 源码再生成寄存器地址的工具链（`dev/update_pinmux_registers.py`）。

最关键的认知锚点：**导入即校验权限**。`gpio.py:31` 定义 `_GPIOCHIP_ROOT = "/dev/gpiochip0"`，`gpio.py:33-34` 在模块导入期就 `os.access` 检查写权限，不通过直接 `raise RuntimeError`——所以"import 就报错"不是 bug，是设计；解法是把用户加进 gpio 组并装 udev 规则（第 7 节）。

## 2. 分层地图（图谱 6 层怎么读）

图谱把仓库切成自下而上的六层，恰好也是依赖方向：

| 层 | 内容 | 代表锚 |
|---|---|---|
| L1 文档、打包与 CI | README/setup.py/MANIFEST/两套 CI | `setup.py:43` |
| L2 Debian 打包与 udev 权限 | debian/* 与 99-gpio.rules | `debian/rules:25` |
| L3 引脚数据库与生成工具 | gpio_pin_data.py + dev/ 工具 | `gpio_pin_data.py:600` |
| L4 核心运行时库 | gpio.py/gpio_cdev.py/gpio_event.py/constants.py | `gpio.py:33` |
| L5 RPi.GPIO 兼容垫片 | RPi/GPIO/__init__.py | `RPi/GPIO/__init__.py:1` |
| L6 示例与板级测试 | samples/ 16 个文件 | `samples/test_all_apis.py:196` |

依赖主干一图流：`__init__.py:1`（星号导出）→ `gpio.py:22-25`（导入 constants/gpio_event/gpio_pin_data/gpio_cdev 四件套）→ `gpio_cdev.py:35-36`（反向依赖 pin_data 的 ChannelInfo 与 constants 的方向常量）→ 内核 `/dev/gpiochip*`。注意图谱在此处有 4 条 `__init__` 伪边（见 README 勘误 #4），真实依赖以 `gpio.py:22-25` 的四条 import 语句为准。

## 3. 核心运行时 gpio.py：主 API 与硬件 PWM

`gpio.py` 是对外命名空间的本体（`Jetson/GPIO/__init__.py:1` 只是星号转发）：

- **编号模式**：`setmode`（`gpio.py:258`）接受四种模式，常量定义在 `constants.py:2-5`——BOARD=10（物理 40 脚）、BCM=11（SoC 名）、TEGRA_SOC=1000、CVM=1001（载板名）。数值故意拉开距离，与上下拉（`constants.py:12` 起 `_PUD_OFFSET=20`）、边沿（`constants.py:22` 起 `_EDGE_OFFSET=30`）的偏移量编码互不重叠，防止 HIGH 被误当 RISING 传入。
- **setup 的哨兵默认值**：`gpio.py:287` 的 `_Default` 可变默认参数类，用于区分 `pull_up_down` 是否被显式传入（`gpio.py:297-302`）。Jetson 硬件没有软件可控上下拉，显式传入只会得到 `gpio.py:315-316` 的一条 RuntimeWarning"Jetson.GPIO ignores setup()'s pull_up_down parameter"——这是从 RPi.GPIO 迁移代码时最常见的告警。
- **PWM 是真的硬件 sysfs PWM**：`gpio.py:542` 的 `PWM` 类经 `_export_pwm`（`gpio.py:160`）向 `/sys/class/pwm/pwmchip*/export` 写通道号，周期换算 `gpio.py:610` `int(1000000000.0/frequency_hz)` 取 ns 写 `period`，占空比走 `_set_pwm_duty_cycle`（`gpio.py:183`），并处理"周期变更后占空比必须小于周期"的边界。与 RPi.GPIO 的软件 PWM 完全不同档位。
- **pinmux 自检挂在 setup 路径上**：`gpio.py:122` 按 label 打开 gpiochip（`chip_open_by_label`），`gpio.py:131` 对每个通道调用 `check_pinmux`，方向不符时告警并给出 devmem 修正命令（见第 4 节）。

## 4. gpio_cdev.py：ctypes 镜像内核 ABI + /dev/mem 诊断

这是全仓最有"内核味"的文件，两个绝活：

1. **手写 ioctl 绑定**：`gpio_cdev.py:47-52` 把 6 个 ioctl 请求码直接写成魔数（如 `GPIO_GET_CHIPINFO_IOCTL = 0x8044B401`），`gpio_cdev.py:58/74/125` 用 `ctypes.Structure` 逐字段镜像内核 uapi 的 `gpiochip_info/gpiohandle_request/gpioevent_request`（64 线数组+对齐字段一个不能错）。调用链：`chip_open`（`:151`）→ `chip_open_by_label`（`:185`，遍历 /dev 下 gpiochip 用 label 匹配）→ `request_handle`（`:240`，构造方向/初值/consumer 的请求）→ `open_line`（`:213`，GET_LINEHANDLE_IOCTL 拿 fd）→ `get_value/set_value`（`:273/:287`）。
2. **绕过内核读物理内存**：`check_pinmux`（`gpio_cdev.py:322`）用 `os.open('/dev/mem', O_RDONLY|O_SYNC)`（`:329`）+ `mmap` 映射 **2 页**（`:335`，注释明确是为处理寄存器跨页边界）读 Tegra pad 控制寄存器，`_GPIO_IN_OUT_MASK`（`:291`）按 bit6（输入输出）与 bit4（tristate）判断 pinmux 方向与用户请求是否一致，不符则告警；权限不足时降级为 `:373` 的友好告警而非崩溃。这属于用户态硬件诊断手段，读操作零风险。

## 5. gpio_event.py：边沿事件引擎

RPi.GPIO 血统的 NVIDIA 重写版，实现 `add_event_detect/wait_for_edge` 两种姿势：

- **三张模块级状态表 + 一把全局锁**：`_epoll_fd_thread`（`gpio_event.py:64`，每 channel 一个 epoll）、`_thread_running_dict`（`:76`）、`_gpio_event_list`，全部由 `:79` 的 `_mutex`（`thread.allocate_lock()`）保护。
- **Py2/3 双兼容残留**：`gpio_event.py:34-38` `try: import thread / except: import _thread as thread`，线程也用底层 `thread.start_new_thread`（`:158`）而非 threading.Thread——与 `gpio_pin_data.py:610` 的 f-string（Py3.6+）并存，是"逐步弃 Py2"的活化石（README 勘误 #5）。
- **注册流程**（`add_edge_detect`，`:115`）：先 `request_event` 拿事件 fd，`:139` 建 epoll，`:148` 以 `EPOLLIN|EPOLLET` 边沿触发注册，`:158` 启动 `_edge_handler` 监视线程（`:349`）。`_Gpios` 类（`:81`）持有 `event_occurred` 标志（`:99`）、`bouncetime` 防抖（`:96`）与 lastcall 时间戳。
- **消费姿势**：轮询式 `edge_event_detected`（`:242-243` 消费后清标志）；阻塞式 `blocking_wait_for_edge` 用 `select.select` 限时监听，结束必调 `remove_edge_detect`（`:179`，默认 0.3s 超时等线程退出）清场。
- 三个 button 示例是同一硬件的三种姿势对照：`button_led.py:42`（裸轮询 `GPIO.input`）、`button_event.py:49`（`wait_for_edge` 阻塞）、`button_interrupt.py:50`（回调+`bouncetime=10, polltime=0.2`）。

## 6. 引脚数据库、板型探测与 pinmux 工具链

- **11 张引脚表**：`gpio_pin_data.py` 为 TX1/TX2/TX2-NX/Xavier/NX/Clara AGX/Orin/Orin NX/Orin Nano(+Super)/Nano/Thor Reference 各维护一张表（`:55-:366` 共 11 个 `*_PIN_DEFS` 数组），每行 10 元组由 `PinInfo`（`:536`）承载：line 偏移、GPIO 名、chip label、四种编号、PWM 芯片目录与 id、PADCTL 寄存器地址。
- **探测三通道**（`get_model`，`gpio_pin_data.py:600`）：① `JETSON_TESTING_MODEL_NAME` 环境变量（`:604`，测试专用）→ ② `/proc/device-tree/compatible`（`:601/:614-618`，按 `get_compatibles`（`:594-597`，以 `\x00` 切分）逐族匹配 TX1→Thor 全系并做载板校验，载板信息取自 `:554-555` 的 plugin-manager ids 或 k510 ids 两路径）→ ③ `JETSON_MODEL_NAME` 环境变量（`:662`，容器内无 device-tree 时兜底）。`get_data()`（`:677`）把模型名+按模式索引的通道表一次性交出去，`gpio.py:36` 导入期即调用——所以板型探测失败同样是导入期爆炸。
- **数据再生成**：`dev/update_pinmux_registers.py` 是新板适配主路径——`:48` 正则解析内核 `pinctrl-tegra234.c` 的 PINGROUP 表（先 `:43-44` 剥注释），`:32-33` 配 Orin 基址 `0x02430000` 与 AON 基址 `0x0C300000`，`:104` AON 域加基址，`update_pin_definitions`（`:108`）括号计数定位数组边界后 `:150` 只替换每元组最后一列（寄存器地址）写回。查询侧：`gpio_pinmux_lookup.py:35` `lookup_mux_register` + `:46-58` main（校验 0-40 BOARD 引脚号，`0x%X` 打印），它经 `setup.py:46-50` 的 entry_points 注册成 `jetson-gpio-pinmux-lookup` 系统命令；黑盒测试 `samples/test_gpio_pinmux_lookup.py:30` 内嵌 Orin/Orin NX 各 40 pin 的期望地址表，`:134` 用 `JETSON_TESTING_MODEL_NAME` 驱动多模型分支。

## 7. 打包分发链、示例矩阵与上手路线

- **PyPI 侧**：`setup.py:42-44` 以 `package_dir={'':'lib/python/'}` 一次发四个包（Jetson/Jetson.GPIO/RPi/RPi.GPIO），`99-gpio.rules` 作 package_data 随包分发；`MANIFEST.in:3` 也包含它（但 `:1` 是死行，见勘误 #1）。
- **udev 权限链**（装不上权限一切白搭）：`lib/python/Jetson/GPIO/99-gpio.rules:22-23` gpiochip 出现即 `chown root:gpio + 660`；`:25-26` pwmchip 的 export/unexport 给 220；`:27-28` period/duty_cycle/enable 给 660；`:30-31` spidev 归 gpio 组。Debian 侧 `jetson-gpio-common.udev` 与它逐字节相同，由 `debian/rules:25` 的 PYBUILD_AFTER_INSTALL（find+xargs rm）把规则从 python 包挪到 common 包，避免双份安装。
- **Debian 双包**：`debian/control:15/21` 拆 jetson-gpio-common（规则文件）与 python3-jetson-gpio；`.gitlab-ci.yml:3` tags 锁 ARM64 runner，`:20` 用 `dpkg-parsechangelog` 从 `debian/changelog:1`（2.1.13-0ubuntu1 noble）提版本剥 Debian 修订号。
- **示例矩阵**：simple_out/simple_input/simple_pwm（点灯三件套）→ button_led/button_event/button_interrupt（事件三姿势）→ `test_all_apis.py`（1146 行自制微型框架：`:196` tests 列表+`:199/204` 装饰器注册，pwmtest 仅在有 PWM 引脚的板型注册，注释给各板手动 devmem 预配命令）→ `test_all_pins.py`（全引脚闪烁，可参数缩短时长）。`run_sample.sh` 是官方入口，但帮助文本与实际文件名有脱节（勘误 #2）。
- **新人路线**：装 udev 规则+加 gpio 组 → 跑通 `simple_out.py` → `jetson_model.py` 验证探测链 → 读 `gpio.py` 主 API → 按需深入 `gpio_cdev.py`（explain/01）或 `gpio_event.py`（explain/02）→ 换板时走第 6 节再生成工具链。
