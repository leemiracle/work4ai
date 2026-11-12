# 07 · NVKMS 显示子系统：nvidia-modeset 双源码树与 EVO 引擎

> 仓库：NVIDIA/open-gpu-kernel-modules @ 615.71.09。本篇覆盖 `src/nvidia-modeset/`（跨平台核心，143 个文件）与 `kernel-open/nvidia-modeset/`（Linux 粘合层，6 个文件）。

## 一、角色定位：显示栈里"独立成国"的内核模块

NVIDIA Linux 显示栈由三个内核模块分担：`nvidia.ko`（RM 资源管理器，管 GPU 计算资源）、`nvidia-modeset.ko`（本篇主角，管显示模式设置）与 `nvidia-drm.ko`（把前两者包装成 DRM 接口给 Wayland/合成器）。NVKMS 就是 `nvidia-modeset.ko` 的内核内实现：模式验证（ValidateMode）、模式设置（SetMode）、翻转（Flip）、光标（MoveCursor）、LUT/颜色、帧锁（FrameLock）、热插拔事件，全部在内核态完成——这与 AMDGPU/i915 把 modeset 决策放用户态的做法截然不同，NVIDIA 选择了"内核内一站式"架构。

代码组织是典型的"双源码树"模式：`src/nvidia-modeset/` 写跨平台 C（OS 抽象经 `os-interface` 分离），`kernel-open/nvidia-modeset/` 只有 Linux 特有的 ~2300 行粘合代码（字符设备注册、file_operations、procfs）。编译时两树合并链接成单个 `nvidia-modeset.ko`（见 `kernel-open/nvidia-modeset/nvidia-modeset.Kbuild` 的源清单）。

EVO 是 NVIDIA 显示引擎的代号（Evolution 系列，自 G80 起服役）。Volta 之后新一代引擎称 NVDisplay，即"EVO3"——`src/nvidia-modeset/src/nvkms-evo3.c:24` 的文件头注释明言"implementations of the EVO HAL methods for display class 3.x (also known as 'nvdisplay')"。所以仓内三代 HAL 并存：evo1（老式通道）、evo3（nvdisplay 3.x，Turing 到 Ada）、evo4（Blackwell C9/CA 新方法集）。

## 二、内部结构：三张"表"定乾坤

整个子系统最值得先读的是三张表，它们分别定义了"用户能做什么"、"硬件是哪代"、"HAL 由谁实现"。

**第一张表：ioctl 分派表**（`src/nvidia-modeset/src/nvkms.c:5070` 起）。`dispatch[]` 数组用 X-macro 风格的 `ENTRY(_cmd, _func)` 宏（nvkms.c:5085）在编译期展开出函数指针、参数尺寸、`offsetof` 计算的 request/reply 偏移，覆盖约 60 个命令：`ALLOC_DEVICE/FREE_DEVICE`（5093-5094）、`QUERY_DISP`、`VALIDATE_MODE/SET_MODE`（带 Pre/DoneUser 钩子的 `ENTRY_CUSTOM_USER`，因为要拷贝用户态可变长数据）、`FLIP`、`SET_CURSOR_IMAGE/MOVE_CURSOR`、`SET_LUT`、FrameLock 四件套、SwapGroup 九件套、表面注册五件套（REGISTER/GRANT/ACQUIRE/RELEASE_SURFACE）。nvkms.c 本体 7196 行，是这个用户态 API 的总实现。

**第二张表：代际探测表**（`src/nvidia-modeset/src/nvkms-hal.c:139` 的 `dispTable[]`，由 `nvAssignEvoCaps()` 遍历）。每行是一个 `(display class, HAL 指针, 能力)` 三元组，按新到旧排列：

| 显示类 | HAL 实例 | 代际 |
|---|---|---|
| CC/CB/CA | `nvEvoCA` | Blackwell GB20x 及后续 |
| C9 | `nvEvoC9` | Blackwell |
| C8 | `nvEvoC8` | T239（车载） |
| C7/C6 | `nvEvoC6` | Ada / Ampere |
| C5 | `nvEvoC5` | Turing |
| NVA083 | `nvDisplayless` | GRID displayless（vGPU 无头） |

探测是"回退式"的：对每行调 `nvRmEvoClassListCheck()` 问 RM"这代硬件有没有该 display class"，第一个命中的行决定 `pDevEvo->hal/dispClass/caps`（nvkms-hal.c:185-190）。HAL 实例的落点：`nvEvoC5/C6/C8` 定义于 nvkms-evo3.c:7873/7958/8043，`nvEvoC9/CA` 于 nvkms-evo4.c:2825/2910。注意 Ada 行（C7）的 window 通道类前缀写的是 C6（nvkms-hal.c:160 的 `ENTRY_NVD(C7, C6, ...)`）——Ada 核心通道升级了类号但窗口通道沿用 Ampere 的，这类"半代升级"细节只在这张表里可见。

**第三张表：EVO 状态表**（`src/nvidia-modeset/src/g_nvkms-evo-states.c`，2826 行生成代码 + `include/g_nvkms-evo-states.h`）。它把硬件状态和方法序列做成声明式表格，是 modeset 事务"验证-暂存-提交"三段式的底座。

围绕三张表的核心源文件按体量排序：nvkms-evo.c 9891 行（EVO 引擎主干）、nvkms-evo3.c 8126 行（nvdisplay HAL）、nvkms.c 7196 行（API 层）、nvkms-rm.c 6024 行（RM 客户端）、nvkms-modeset.c 4688 行（模式设置事务）、nvkms-dpy.c 3944 行（显示设备抽象）、nvkms-hw-flip.c 3433 行（硬件翻转）。另有 headsurface 家族（主文件 2936 行 + config 2684 行 + matrix/3d/swapgroup 共五文件）——当硬件 overlay 不足以完成客户端请求的合成（任意旋转、跨层缩放、swap group 裁剪）时，用 GPU 3D 引擎离屏渲染一个"头表面"再送显。

## 三、外部连接：一个字符设备、两条入口路径

**用户态入口**：`kernel-open/nvidia-modeset/nvidia-modeset-linux.c:2102` 的 `nvkms_register_chrdev()` 注册 `NVKMS_RDEV`（2087 行定义为 `MKDEV(NV_MAJOR_DEVICE_NUMBER, NV_MINOR_DEVICE_NUMBER_MODESET_DEVICE)`，即主设备号 195 的一个次设备号）。`file_operations`（2090 行 `nvkms_fops`）只实现 open/release/ioctl/mmap/poll 五个操作。

ioctl 设计有个值得注意的规避动作：所有命令共用**一个** ioctl 码。`src/nvidia-modeset/interface/nvkms-ioctl.h:45-48` 定义 `NVKMS_IOCTL_CMD 0` 并以 `_IOWR` 包装 `struct NvKmsIoctlParams`——参数结构里真正携带 `cmd/address/size` 三元组。这样 32 位用户态与 64 位内核之间不存在 per-command 的结构尺寸差异（所有命令的结构尺寸都相同），一次性绕开 compat_ioctl 的兼容矩阵，代价是每条命令多一层指针解引用。poll 路径（`nvidia-modeset-linux.c:2060` 的 `nvkms_poll`）在事件队列非空时返回 `POLLPRI|POLLIN`，配合 `nvkms_event.c` 的事件环形队列，把热插拔/翻转完成等内核事件送回用户态。

**内核态入口**：nvidia.ko 与 nvidia-drm.ko 不走字符设备，而是经 kapi 直接调用——`nvidia-modeset-linux.c:1593` 的 `nvkms_open_from_kapi()` 与 :1616/:1638 的 `nvkms_ioctl_from_kapi[_try_pmlock]()`，客户端类型标记为 `NVKMS_CLIENT_KERNEL_SPACE`。这就是 `src/nvidia-modeset/kapi/` 目录存在的意义（include/interface/src 三段）。

**对 RM 的依赖**全部集中在 nvkms-rm.c：`nvRmAllocDeviceEvo`（声明于 nvkms-rm.h:102）、`nvRmAllocEvoDma`（:113）等函数用 RM 控制 API（ctrl0073/ctrl5070/ctrl0080 系列命令，nvkms-evo.c:65-81 的 include 清单可见一斑）分配显示通道与表面。NVKMS 自己不碰寄存器——所有硬件操作都构造成 EVO 通道方法，经 RM 分配的 DMA pushbuffer 送往显示引擎。

## 四、数据流：一条下行链与一条上行链

**下行（命令链）**：用户态 ioctl → `nvkms_ioctl()`（linux.c:2011）解包 NvKmsIoctlParams → `nvkms_ioctl_common()`（1560）查 dispatch 表 → 如 `SetMode` 进入 nvkms-modeset.c 的事务（prealloc 预分配 → validate 验证 → apply 应用）。"应用"的物理形态是向 EVO 通道写方法序列：`NVEvoChannel`（nvkms-types.h:469）内含 `pb`（pushbuffer DMA）、`notifierDma`、`imm.dma`（立即通道）与 `postSyncpt`（同步点）。方法推送复用 GPU 通用 pushbuffer 机制——nvkms-push.c:33 起的 `NvPushImportRmApiControl/Alloc/Free/Map...` 系列包装函数把 nvRmApi* 注入 nvidia-push 通用库（`src/common/nvidia-push/`），通道对象用 `NVA06F` 等 GPU 通道类。core channel 与 window channel 分工：core 管全局/每头状态（时序、光栅），window 管每层表面采样；两者以 interlock 机制保证跨通道原子性（nvkms-types.h:375-400 的 channelMask/noCoreInterlockMask/flipLockQualifyingMask 位掩码组）。

**上行（事件链）**：DP 库检测到热插拔/链路事件 → `nvdp-connector-event-sink.cpp`（DP 库回调适配，第 10 篇详述）→ nvkms 事件入队 → `nvkms_poll` 唤醒等待的 X server/合成器 → 用户态发 `GET_NEXT_EVENT`。翻转完成走 completion notifier（NVEvoChannel 内的 `completionNotifierEventCallback`，nvkms-types.h:480-482）回调，vblank 用 GPU-CPU 时间相关性补偿定时器漂移（nvkms-evo.c:96-99 的 `GPU_CPU_TIME_DIFF_REFRESH_PERIOD_USEC` 十秒刷新）。

多 GPU 帧锁是上行链之外的横向协作：nvkms-evo.c:245 `HasActiveHeads`、:1061 起的 RasterLockGroup 构造、:3944 `nvEnableFrameLockEvo`/:4027 `nvDisableFrameLockEvo`，把多块 GPU 的 DispEvo 按光栅锁组绑定同步。

## 五、设计决策：为什么这样切

1. **内核内 modeset vs 用户态 KMS**：把模式验证/应用全放内核，代价是 nvkms-modeset.c 的事务状态机复杂（prealloc 机制保证"验证通过后应用不再失败"），收益是 X server 崩溃不影响显示状态恢复——console-restore（nvkms-console-restore.c 986 行）与 fbcon 切换（ctrl0080unix VT_SWITCH 命令）依赖这一点。
2. **单一 ioctl 码间接层**：牺牲一次间接寻址，换来彻底免除 compat 处理。对比 nouveau 的 per-cmd compat_ioctl 矩阵，这是简洁性换灵活性的典型取舍。
3. **回退式 HAL 探测**：dispTable 按新到旧线性扫描，新硬件只需在表头加一行；老 HAL（evo3.c 8126 行）永不删除，Turing 卡在 Blackwell 时代的驱动里依然工作。表内还留着注释"列头艺术"（nvkms-hal.c:139-152 每列能力用 ASCII 竖线对齐标注）——生成的 ENTRY 宏参数多达 13 个，没有这张注释图根本无法维护。
4. **displayless 伪 HAL**：GRID vGPU 场景没有物理显示引擎，NVA083 类挂 `nvDisplayless`（nvkms-displayless.c 882 行）提供空实现，让同一套 API 面向无头虚拟机工作。
5. **headsurface 软件逃生门**：硬件 overlay 语义有限（层间缩放/任意旋转/swapgroup），NVKMS 不扩展硬件而是用 GPU 3D 引擎渲染合成帧——客户端永远拿到"硬件能做"的假象，代价是功耗与一条隐性 GPU 依赖。矩阵常量（nvkms-headsurface-matrix.h）与 GLSL 微码（shaders/ 目录，第 10 篇）都为它服务。

## 六、新人提示

- **读码顺序**：nvkms-hal.c（半天可读完，先建立代际地图）→ nvkms.c:5070 dispatch 表顺藤摸瓜选一个命令跟读 → nvkms-evo.c 只读头 500 行（结构体与光栅锁）即可，其余按需查。
- **命名黑话**：EVO=显示引擎；DispEvo=一块 GPU 的显示控制器；Dpy=display device（显示器/接收端）；SOR=串行输出资源（HDMI/DP 物理发送器）；IMP=即时模式策略（带宽预算）。
- `g_nvkms-evo-states.c` 与 shaders/ 下的 `g_*_shader_info.h` 是**生成物**，不要手改；改了也会被下次生成覆盖。
- nvkms-types.h:333 的 `NVEvoChannelMask` 是 NvU64 位掩码，通道数量上限 64；debug 时打印掩码用 `%016llx`。
- 找"这个 ioctl 最终写了哪个寄存器"会失望——NVKMS 全部经 RM/通道方法间接作用于硬件，寄存器语义在 open-gpu-doc 的 dev_display 手册里（nvkms-hal.c:104-115 注释直接给了 Volta 手册链接与 ARMED offset 推导，是仓内少有的"链接硬件文档"注释）。
