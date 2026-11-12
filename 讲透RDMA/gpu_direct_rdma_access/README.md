# 讲透 gpu_direct_rdma_access

[Mellanox/gpu_direct_rdma_access](https://github.com/Mellanox/gpu_direct_rdma_access) @a99d506 · GPU Direct RDMA 示例（GPU 显存直接 RDMA 读写，CUDA+ibverbs，USE_CUDA 条件构建）

| 产物 | 状态 | 明细 |
|---|---|---|
| deepwiki | ✅ | 23 页 TRUE_100 |
| understand 图谱 | ✅ | 64n/121e/12 层/14 步 tour · validator 0 issues · fingerprints 14 files@a99d5069 |
| onboarding | ✅ | 5979 字 8 节 · 34 锚 |
| explain | ✅ | 12 篇 51243 字符 · 261 锚终验 0 坏 |

## 源码级勘误精选

- **khash.h 系 klib 定制版**：KHASH_TYPE/KHASH_IMPL 声明/实现两段式宏（382/385 行），标准 klib 无此 API——宏膨胀零提取属预期
- tree-sitter 盲区 10 函数补录：#ifdef HAVE_CUDA 块 5 个 CUDA 函数（87-226 整体漏，KCCL 钉版复现）+ 星号返回 5 函数（open_ib_device_by_name/by_addr、rdma_open_device_client/server、rdma_buffer_reg）
- **PRINT_LATENCY 分支 1453 行 wc[i] 潜伏编译错误**（explain 组2 发现）；1517 perror 标签错
- 图谱 utils.c 摘要"GB/s+每秒消息数"与实现不符（实为 Mbit/sec+usec/iter）
- README.md:49 write_to_gpu/ 路径不存在；`-l` 模式 64 字节对齐尾差致带宽虚报
- rdma_reset_device L1009 仅 server 侧；rdma_submit_task L1342→rdma_exec_task L890 提交链
