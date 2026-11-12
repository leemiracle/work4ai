# 01 · 公共 C API 与 pImpl 边界

## 角色定位

`include/` 的两个头是 NVVL 对世界的全部承诺：`VideoLoader.h` 管"怎么喂请求、怎么收结果、怎么问统计"，`PictureSequence.h` 管"结果长什么样"。每个头都各有恰好 12 个 `nvvl_*` 纯 C 函数（`include/VideoLoader.h:64-122`、`include/PictureSequence.h:250-331`），C++ 类部分只是同一契约的语法糖。安装方只需要这两个头 + `libnvvl.so`，不拖 Boost——这是 pImpl 的唯一动机（`include/VideoLoader.h:241-243` 注释原话 "to prevent copying a slew of headers for installation"）。

## 内部结构

`VideoLoader.h` 的 C 区块先给数据结构：`VideoLoaderStats` 五字段（`include/VideoLoader.h:15-41`）——bytes_read 与 bytes_decoded 是两本账，seek 不精确会让送进 NVDEC 的字节多于从盘上读的；五级 LogLevel（`:46-52`）；不透明句柄就是 `void*`（`:57`）。`PictureSequence.h` 的核心是 `NVVL_LayerDesc` 16 字段（`include/PictureSequence.h:87-188`）：几何四件套、crop 与 scale 的"先缩放再裁剪"次序（`:121-142`）、horiz_flip（`:147`）、normalized（`:155`）、三个方法枚举（`:162-177`），以及**元素 stride**（非字节，`:179-186`）。C++ 侧 `Layer<T>` 模板（`:381-422`）加了两样 C 给不了的：`std::vector<int> index_map`（帧挑选/倒放语义，`:412`）与类型化指针 `T* data`（`:421`）。

pImpl 的实现体在 `src/PictureSequenceImpl.h`：层数据不是继承多态而是 `variant<Layer<uint8_t>, Layer<half>, Layer<float>>`——类型表用 boost.mp11 从枚举映射生成（`src/PictureSequenceImpl.h:89-94` 的 PDTMap，`:99-103` 的 PMTMap），再 `mp_rename<mp_transform<add_layer, PDTypes>, boost::variant>` 拼出容器类型（`:190-194`），存进 `unordered_map<string, LayerVariant>`（`:196`）。`include/PictureSequence.h:555-558` 注释直说 pImpl 挡的就是"a chunk of boost for boost::variant"。

## 外部连接

上游消费者三条线：C 接口示例 `doc/examples/extract_frames_c.c`；C++ 示例 `doc/examples/extract_frames.cpp`（模板版 get_pixels 消费，`:45`）；Python 绑定（cffi 直接吃 `PictureSequence.h`，见 04 篇）。头文件顶部 `#ifndef CFFI` 分支（`include/PictureSequence.h:3-10`）为 cffi 预处理留了纯 C 通道：用前置声明 `struct CUstream_st; typedef struct CUstream_st* cudaStream_t;` 顶替 `<cuda_runtime.h>`。实现层向 `src/VideoLoader.cpp` 与 `src/detail/NvDecoder.cpp` 供给容器；`Decoder` 是唯一 friend，负责 record 事件（`src/PictureSequenceImpl.h:210`）。

## 数据流

一次典型的序列消费：`nvvl_create_sequence(count)` 造容器 → `nvvl_set_layer` 动态分派——C 侧 `mp_for_each<PDTMap>` 逐型试探（`src/PictureSequence.cpp:246-252`），选中后 `set_layer<T>` 把 PicLayer 拷进 variant（`src/PictureSequenceImpl.h:111-117`）→ `nvvl_receive_frames` → 解码线程填数据 → `nvvl_sequence_wait`（`src/PictureSequence.cpp:321-329`）。等待分两级：先条件变量等"传输已开始"（`src/PictureSequence.cpp:127-130`），再 `cudaEventSynchronize`（`:138`）或 `cudaStreamWaitEvent`（`:147`）——事件 record 之前等待无效，故 started 标志不可省（`src/PictureSequenceImpl.h:199-204`）。取回时 `get_layer<T>` 用 `boost::get` 取值并按 `stride.n * index` 平移指针（`src/PictureSequenceImpl.h:120-129`）；类型取错抛 `boost::bad_get`，C 层捕获打日志返回空（`src/PictureSequence.cpp:278-280`）。

## 设计决策

三处决策值得抄走：(1) **variant 而非虚基类**——层类型是封闭三选一，无堆分配、访问局部性好；加类型只需动 PDTMap 一处，实例化与 C 分派自动跟随。(2) **模板成员 + .cpp 显式实例化**：`src/PictureSequence.cpp:37-46` 注释解释了为什么——g++ -O2 会把模板内联进 C 包装函数导致符号不导出，于是用 mp11 递归实例化器取成员函数指针强制实体化（`:47-61`）。(3) **stride 用元素数**：nchw/nhwc/fchw 任何维度序都能描述，`pytorch/nvvl/dataset.py:324-325` 按 dimension_order 现场映射即闭环。诚实代价：字符串 meta 数组直接 `throw not_implemented()`（`src/PictureSequence.cpp:188-193,200-205`）；`nvvl_get_layer_indexed` 不敢返回临时 vector 的指针，index_map 置 NULL（`:297-301`）。

## 新人提示

先读 `doc/examples/extract_frames.cpp` 再读头，顺序反了会陷进注释海洋。两个易踩坑：stride 填字节数（正确：元素数，`include/PictureSequence.h:179-186`）；normalized=true 却选 uint8 输出——kernel 启动前就抛"must be floating point"（`src/detail/cuda/imgproc.cu:129-132`）。改输出类型集合时 PDTMap 与 `nvvl_set_layer` 分派同表驱动不会漏；但 `pytorch1.0/src/nvvl_th.cpp:56-78` 的 pybind11 层是手写三份的，要同步改。
