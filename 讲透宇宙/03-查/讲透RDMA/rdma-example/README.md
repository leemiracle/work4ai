# 讲透 rdma-example

[animeshtrivedi/rdma-example](https://github.com/animeshtrivedi/rdma-example) @615b85d · RDMA 编程入门示例（rc/uc verbs + rdma_cm）

| 产物 | 状态 | 明细 |
|---|---|---|
| deepwiki | — | NOT_INDEXED → repo-docs 兜底（1 文件） |
| understand 图谱 | ✅ | 31n/69e/9 层/14 步 tour · validator 0 issues · fingerprints 6 files@615b85d2 |
| onboarding | ✅ | 5998 字 8 节 · 58 锚（+81 L 简写锚）主会话抽验 12/12 |
| explain | ✅ | 12 篇 21957+ 字符 · 174 锚终验 0 坏 |

## 源码级勘误精选（explain/onboard 实证）

- **CMakeLists 只设 CMAKE_CXX_*（-O2/-Ofast/CMAKE_CXX_STANDARD）——纯 C 项目全不生效，CMAKE_C_FLAGS 未设；`project()` 之后才设编译器属双重落空**
- `/home/atr/local` 个人机器路径硬编码（find_library/include）
- tree-sitter 提取 24/25 函数，漏 `check_src_dst`（已在 explain 篇1 勘误⑥注明）
- 星号贴函数名返回类型（`struct ibv_mr* rdma_buffer_alloc`）整体漏提取，图谱手工补录
- 教学简化实证：发 lkey 当 rkey 用、get_addr 清端口顺序、show_rdma_cmid 死代码、WC 收割循环忙等
