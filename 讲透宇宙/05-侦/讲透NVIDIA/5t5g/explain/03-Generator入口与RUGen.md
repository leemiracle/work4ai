# Generator 入口与 RUGen——O-RU 模拟发送端

## 角色定位
`generator/src/main.cpp` 是 Generator 应用入口；`generator/include/ru_gen.hpp` 的 RUGen 类继承 RU，实现 O-RU 发送逻辑。

## 内部结构
- `main.cpp`：DPDK EAL 初始化 → 命令行解析 → 创建 RUGen → 主循环发包
- `ru_gen.hpp`：RUGen : public RU，模拟两台 O-RU 用不同 slot 时长发 U-plane 包
- `oran_generator.hpp`：O-RAN U-plane 包格式封装（发送侧拷贝）

## 外部连接
- main.cpp imports: utils.hpp（UDP 工具）, ru_gen.hpp（子类头）
- ru_gen.hpp imports: ru.hpp（基类）, oran_generator.hpp（协议）
- generator/CMakeLists.txt 链接 common 库

## 数据流
```
main() → RUGen 构造 → O-RAN U-plane 包拼装（oran_generator.hpp）
      → DPDK 发包（不同 slot 时长模拟两台 O-RU）
```

## 设计决策
Generator 不用 CUDA——纯 host 侧发包，不需要 GPUDirect。

## 新人提示
oran_generator.hpp 是与 oran_receiver.hpp 同库的发送侧**分叉拷贝**，receiver 版是超集。
