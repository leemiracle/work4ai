# 讲透 RDMA-Tutorial

[jcxue/RDMA-Tutorial](https://github.com/jcxue/RDMA-Tutorial) @be4d713 · RDMA 教程与示例（main 入口+client/server 线程模型+config 体系+setup_ib 资源编排）

| 产物 | 状态 | 明细 |
|---|---|---|
| deepwiki | — | NOT_INDEXED → repo-docs 兜底（1 文件） |
| understand 图谱 | ✅ | 46n/121e/13 层/15 步 tour · validator 0 issues · fingerprints 17 files@be4d713b |
| onboarding | ✅ | 5999 字 8 节 · 102 锚界内零坏 |
| explain | ✅ | 12 篇 48470 字符 · 353 锚终验真坏 0（1 处正则吞斜杠假阳性已消歧） |

## 源码级勘误精选

- **destroy_config_info 死代码**：config.c:204-227，main.c:41-43 不调用（图谱 tour 15 描述与控制流不符已纠）
- **server.c:43/54 对 wc 重复 calloc 覆盖 L43 指针**（内存泄漏，与 client.c:52 单次对照实证）
- setup_ib.c:269-272 注释漂移：宣称两倍缓冲实际未实现（L273 无乘 2 负向断言验证）
- **-lrdmacm 链接零调用冗余**（Makefile 链接 rdmacm 但源码全用裸 ibv_*）
- 1 client×N server 时 server 端 `qp[imm_data]` 越界（源码推演，explain 06 标注未实测）
- 吞吐统计分子含预热请求 → ~5% 系统性偏高；saguaro%d 不补零在节点数≥10 时 rank 子串碰撞
- imm_data 三义复用（长度/索引/结束标记）建立在单 client 拓扑假设上
- main.c 冗余 include grep 计数 0 实锤（组 12 篇微勘误）
- void* 星号返回线程函数 2 个 tree-sitter 漏提取已手工补
