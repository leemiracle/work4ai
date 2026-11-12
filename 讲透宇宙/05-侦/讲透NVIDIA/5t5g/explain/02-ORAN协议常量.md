# O-RAN 协议常量——constants.hpp 的固定值定义

## 角色定位
`common/include/constants.hpp` 是 O-RAN 规范中**固定协议值**的单一来源。被 Generator 和 Receiver 共同引用。

## 内部结构
定义 O-RAN CUS 平面（Control/User/Synchronization）中的常量：
- 包类型/子类型标识
- SDU 长度上限
- eAXC（eAxC ID）配置值
- 其他协议规范固定值

## 外部连接
- 被 `ru.hpp`（RU 基类）、`kernel.cu`（CUDA kernel）、`receiver/main.cpp` 引用
- 是最底层的依赖（无出边）

## 数据流
作为纯常量头文件，不参与运行时数据流。所有引用者编译期内联使用。

## 设计决策
将 O-RAN 规范的魔数集中在一个头文件，避免散落各处。教学示例的最佳实践。

## 新人提示
include guard 为 `COSTANTS_H`（非 `CONSTANTS_H`）——上游笔误。
