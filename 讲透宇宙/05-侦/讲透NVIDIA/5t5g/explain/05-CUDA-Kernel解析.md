# Receiver CUDA Kernel——GPU 上解析 O-RAN U-plane 包

## 角色定位
`receiver/src/kernel.cu` 在 GPU 上解析 O-RAN U-plane 包格式，提取 IQ 数据并区分两台 O-RU 的数据流。**这是整个项目"实时"特性的核心**。

## 内部结构
- CUDA kernel 函数（tree-sitter 对 .cu 语言的函数提取全空，须手工分析）
- 解析 O-RAN 包头（使用 oran_receiver.hpp 中的 `__host__ __device__` Bitfield 模板）
- 提取 IQ 样本

## 外部连接
- imports: constants.hpp, cuda_headers.hpp, oran_receiver.hpp
- 被 ru_recv.cpp / main.cpp 调用

## 数据流
```
DPDK 收包（GPUDirect 直达显存）
    ↓ mbuf 指针即 GPU 指针
CUDA kernel 直接在显存中解析包
    ↓
提取 IQ 数据 → 按两台 O-RU 的 eAXC 区分
```

## 设计决策
使用 `__host__ __device__` Bitfield 模板使同一份位域操作代码可在 CPU 和 GPU 上编译。

## 新人提示
kernel.cu 的 tree-sitter 提取为空（.cu 语言不支持），图谱节点和函数签名须从源码手工录入。
