# Receiver 入口与 DPDK 集成

## 角色定位
`receiver/src/main.cpp` 是 Receiver 应用入口，集成 DPDK EAL 和 GPU mempool。

## 内部结构
- DPDK EAL 初始化（Environment Abstract Layer）
- 配置 GPU mempool：`RTE_PKTMBUF_HEADROOM=0`（GPUDirect 直达显存的关键）
- 创建 RURecv 实例
- 主循环：DPDK 收包 → 调度到 CUDA kernel

## 外部连接
- imports: constants.hpp（常量）, ru_recv.hpp（子类）
- 与 `ru_recv.cpp`（DPDK 包处理逻辑）配对

## 数据流
```
main() → DPDK EAL init → GPU mempool 创建（headroom=0）
      → RURecv 构造 → rte_eth_rx_burst 收包
      → GPU kernel 解析 O-RAN U-plane
```

## 设计决策
`RTE_PKTMBUF_HEADROOM=0` 允许 DPDK 包直接落在 GPU 显存（GPUDirect），免去 CPU→GPU 拷贝——这是 5T for 5G 实时性的核心。

## 新人提示
此文件依赖正确的 CUDA/DPDK 联合编译环境。kernel.cu 须与 main.cpp 链接到同一 target。
