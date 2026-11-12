# 03 · 异步基建 Queue 与 imgproc 后处理 kernel

## 角色定位

这一对组件一个管"帧在系统里怎么流动"，一个管"帧的像素怎么变"。`src/detail/Queue.h`（67 行）是全库唯一的生产者-消费者原语，串起请求、显示帧、输出序列三条队列；`src/detail/cuda/imgproc.cu`（163 行）是"解码后不落 CPU"承诺的兑现点——NVDEC 吐出的 NV12 显存在这里直接变成任意布局的训练张量。

## 内部结构

Queue 是 mutex + condvar 的教科书实现：push 锁内入队、锁外 notify_one（`src/detail/Queue.h:16-22`）；pop/peek 阻塞在 `cond_.wait(lock, pred)` 直到"有货或中断"（`:27,39`）。精髓在中断路径：`cancel_pops()` 置 atomic 中断位并 notify_all（`:54-57`），等待者醒来后 `if (interrupt_) return std::move(int_return)`，其中 `int_return` 是函数级 `static auto int_return = T{}`（`src/detail/Queue.h:25,37`）——两重含义：T 必须可默认构造；返回的是同一个静态对象的引用/移动，调用方绝不能把它当真数据。imgproc 侧，kernel `process_frame_kernel` 每线程一像素（`src/detail/cuda/imgproc.cu:72-115`），BT.601 矩阵放 `__constant__` 内存（系数 1.164383/1.596027/-0.391762/-0.812968/2.017232，`:20-24`，数学出处注释指向 MSDN `:13`），输出类型特化 half 用 `__float2half`、uint8 用 `roundf`（`:35-43`）。

## 外部连接

Queue 的三个实例全在 NvDecoder：`recv_queue_`（FrameReq 请求）、`frame_queue_`（CUVIDPARSERDISPINFO 显示帧）、`output_queue_`（PictureSequence* 序列句柄）（`src/detail/NvDecoder.h:105-107`）；VideoLoader 自己还有第四条 `send_queue_`（`src/VideoLoader.cpp:125`）。关停协议自上而下：`VideoLoader::finish` 置 done_ 后 cancel 自己的队列再调 decoder 的 finish（`src/VideoLoader.cpp:162-169`），后者对三条队列逐一 cancel（`src/detail/NvDecoder.cpp:474-479`）。imgproc 的 host 入口 `process_frame` 只对 Layer<T> 模板暴露（`src/detail/cuda/imgproc.h:8-12`），唯一调用方是 `NvDecoder::convert_frame`（`src/detail/NvDecoder.cpp:462-464`）；纹理对象由 NvDecoder 的三元组缓存供给（`:366-418`）。

## 数据流

**队列视角**：read_file 线程从 send_queue_ 取请求（`src/VideoLoader.cpp:358`）→ push_req 进 recv_queue_（`:372`）→ nvcuvid 回调在 handle_display 里从 recv_queue_ 补货并把显示帧压进 frame_queue_（`src/detail/NvDecoder.cpp:322,351`）→ convert 线程从 output_queue_ 取序列、从 frame_queue_ 逐帧取 MappedFrame（`:423,429`）→ 处理完 record 事件（`:434`）。pop 之后一律再查 `done_` 二次判死（`:423-424,429-430`）——因为中断返回值与真数据无法区分，这是 Queue 设计强加给调用方的纪律。**kernel 视角**：host 侧把 scale 默认值回填（不缩放就用原尺寸）、算好 fx=input_w/scale_w 与 fy（`src/detail/cuda/imgproc.cu:134-138`）传进 kernel；每线程先算目的坐标，越界即返回（`:78-82`）；源坐标 = (crop + dst) * fx，horiz_flip 时做 (scale_width - crop_x - dst_x) * fx 的镜像（`:84-89`）；luma 采样加半像素中心 +0.5，chroma 坐标除 2 再 +0.5（4:2:0 上采样交给纹理硬件，`:94-95`）；输出地址按 desc.stride.x/y/n 元素步长拼（`:99-101`）；RGB 走 yuv2rgb（Y-16/U/V-128 偏移后乘矩阵，clip 上界按 normalized 选 1.0 或 255.0，`:48-65`），YCbCr 直通只乘 mult（`:108-113`）。

## 设计决策

(1) **static T{} 而非 optional/异常**：2018 年 C++14 语境下最朴素的解除阻塞法；代价是语义模糊，靠 done_ 双检兜底。今天重写会用 `std::optional<T>` 或返回状态枚举。(2) **插值全部交给纹理单元**：缩放比预乘进坐标（`:137-138`），kernel 里没有任何分支型插值代码——GPU 纹理硬件的免费双线性是整个"加载期数据增强"的性能根基；Nearest 对应 Point 过滤、Linear 对应 Linear 过滤，建纹理时决定（`src/detail/NvDecoder.cpp:379-383`）。(3) **normalized 双分支写在 kernel 里**（`src/detail/cuda/imgproc.cu:55-65`）而非两个 kernel，注释说"branch seems faster"——一个 if 换一次 kernel 切换。(4) **host 断言前置**："normalized 必须 float/half"在启动 kernel 前就抛（`:129-132`），不让错误数据流到训练侧。block(32,8) 的 256 线程配置与 divUp 网格（`:117-119,140-144`）是纹理采样 kernel 的常规姿势。

## 新人提示

读 Queue 时先想清楚"谁在等谁"：三条队列上各有不同线程在 pop，cancel_pops 的目标就是叫醒所有等待者让它们去看 done_。改 imgproc 时记得三型显式实例化（uint8_t/half/float，`:147-160`）与 CMake 的 separable compilation（`CMakeLists.txt:59-63`）；加新色彩空间要动 kernel 的 switch（`:103-114`）与头文件枚举（`include/PictureSequence.h:54-64`）两处。chroma 纹理的资源描述是 uchar2、高度减半、指针偏移 height*pitch（`src/detail/NvDecoder.cpp:405-409`）——NV12 布局知识浓缩在这四行，改动前先画一遍内存图。性能调优先看统计：packets_decoded/frames_used > 3 时库自己会警告 GOP 太长（`src/VideoLoader.cpp:542-552`）。
