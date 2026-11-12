# 精讲 02：gpio_event.py——边沿事件引擎（epoll×监视线程×防抖）

## 角色定位

`lib/python/Jetson/GPIO/gpio_event.py` 承载库的事件三 API：`add_event_detect`（回调式）、`event_detected`（轮询式）、`wait_for_edge`（阻塞式）。它是 RPi.GPIO 事件机制的 NVIDIA 重写版——语义照搬，实现从 sysfs 轮询升级为 cdev 事件 fd + epoll 边沿触发 + 每引脚监视线程。`gpio.py:23` 以 `from Jetson.GPIO import gpio_event as event` 引入，全部公开函数都由 gpio.py 的同名 API 薄包装后透出。

## 内部结构

模块级状态三张表一把锁：`_epoll_fd_thread`（`gpio_event.py:64`，channel → epoll 对象）、`_thread_running_dict`（`:76`，线程退出标志）、`_gpio_event_list`（channel → `_Gpios` 状态对象），由 `:79` 的 `_mutex` 保护。`_Gpios`（`:81`）是每条被监视线路的运行时容器：`value_fd` 事件 fd、`bouncetime` 防抖毫秒数（`:96`）、`event_occurred` 标志（`:99`）、回调列表与 lastcall 时间戳。文件头 `:34-38` 的 `try: import thread / except: import _thread as thread` 与 `:158` 用 `thread.start_new_thread` 起线程，是 Python2/3 双兼容时代的活化石——全文件刻意避开 threading.Thread。

注册主线 `add_edge_detect`（`:115`）：复用 `gpio_cdev.request_event`（`gpio_cdev.py:258`）拿事件 fd → `:134` 建 `_Gpios` → `:137-154` 加锁建 epoll 并 `register(fd, EPOLLIN|EPOLLET)`（`:148`，边沿触发保证高电平停留不重复报）→ `:158` 启动 `_edge_handler`（`:349`）监视线程，线程在 epoll 上限时等待，读 `gpioevent_data` 判边沿、做 bouncetime 时间窗过滤，然后置 `event_occurred`、逐个跑回调。

## 外部连接

上游是 `gpio.py` 的三个 API 包装（`gpio.py:400` add_event_detect / `:478` wait_for_edge / cleanup 链路的 `event_cleanup`）；下游依赖 `gpio_cdev`（`:47`）的事件请求结构体与 ioctl。`remove_edge_detect`（`:179`）置线程运行标志 False 并默认等 0.3s 超时收尸，再从 epoll 注销 fd——事件不存在时静默返回，这与 RPi.GPIO 行为一致。

## 数据流

硬件边沿 → 内核 cdev 在事件 fd 上放一个 `gpioevent_data`（时间戳+边沿类型）→ epoll ET 唤醒监视线程 → 防抖窗内丢弃/窗外接受 → 置 `event_occurred` + 执行回调。轮询姿势由 `edge_event_detected`（`:242-243`）读后清零；阻塞姿势 `blocking_wait_for_edge` 不走线程，直接 `select.select` 限时监听同一 fd，超时返回 0、成功返回 1，收尾必调 remove_edge_detect。

## 设计决策

- **每 channel 独立 epoll + 独立线程**：文件头注释（`:32`）写明"Each thread should not share epoll instance"——共享 epoll 需要多路分发，独立实例最简单可靠，代价是引脚多时线程数线性涨。
- **ET 边沿触发**（`:148`）：电平触发会在保持期间反复上报；ET 配合读尽 fd 数据正好一次边沿一次事件。
- **Py2 兼容残留未清**：与 `gpio_pin_data.py:610` 的 f-string（Py3.6+）并存，实际早已 Python3-only（README 勘误 #5 的证据链）。

## 新人提示

三个 button 示例是本文件的活教材：`button_led.py:42` 裸轮询 `GPIO.input`、`button_event.py:49` `wait_for_edge` 阻塞、`button_interrupt.py:50` 回调+`bouncetime=10, polltime=0.2`。调回调丢事件时先查三件事：bouncetime 是否过小（抖动当多次边沿）、是否忘了 `event_cleanup`/`GPIO.cleanup()`（线程泄漏会让第二次注册静默失败）、回调里是否又同步调了 GPIO API 造成锁重入。进程退出前务必 `cleanup`——监视线程是非 daemon 的 `start_new_thread` 产物，不收干净会挂住解释器退出。
