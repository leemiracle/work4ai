# O-RAN 协议库分叉——oran_generator.hpp vs oran_receiver.hpp

## 角色定位
`generator/include/oran_generator.hpp` 与 `receiver/include/oran_receiver.hpp` 是**同一 O-RAN 协议库的收/发两份拷贝分叉**。

## 内部结构
- **generator 版**：基础 U-plane 包拼装（section header + data 打包）
- **receiver 版（超集）**：增加了：
  - C-plane section 结构
  - `__host__ __device__` Bitfield 模板（供 CUDA kernel 使用）
  - 接收端特有的包解析逻辑

## 外部连接
- 分别被 ru_gen.hpp（发送）和 ru_recv.hpp/kernel.cu（接收）引用
- 两者之间有 `related` 边标记同源分叉关系

## 设计决策
教学示例避免引入统一协议库的复杂构建。实际工程应抽出为独立共享库（`oran_common`），消除拷贝分叉。

## 新人提示
比较两份文件时注意 receiver 版是超集。Bitfield 模板的 `__host__ __device__` 是 receiver 独有的——generator 版没有（不需要 GPU）。
