# 讲透 softiwarp

[zrlio/softiwarp](https://github.com/zrlio/softiwarp) @5d8a418 · 软件 iWARP 栈（Linux 内核模块在 TCP 之上实现 RDMA verbs 语义）

| 产物 | 状态 | 明细 |
|---|---|---|
| deepwiki | ✅ | 17 页 TRUE_100 |
| understand 图谱 | ✅ | 274n/495e/15 层/15 步 tour · validator 0 issues · fingerprints 33 files@5d8a418f |
| onboarding | ✅ | 5999 字 8 节 · 69 锚（36 主锚+33 从属锚）内容级抽验 27 处全命中 |
| explain | ✅ | 12 篇 52587 字符 · 188 锚终验 0 坏 |

## 源码级勘误精选

- **USE_SQ_KTHREAD=活代码**（siw.h:542 默认 #define，kthread 路径默认编译）——批分析误判"死代码"，onboard 阶段源码级反转钉版；**真死代码=SIW_TX_FULLSEGS**（4 处 #ifdef 永假：siw_qp.c:276、siw_qp_tx.c:805/818/954），且 fpdu_len 字段唯一写点（siw_qp_tx.c:806）在死代码内=死域互锁
- **Kbuild siw-objs 重复列 siw_cm.o 笔误**；分发表 SEND_SE 实际绑定 siw_proc_send（siw_qp.c:131-132）非 unsupp——SE 协议语义在结算器 fall-through（siw_qp_rx.c:1113-1115）+TX 模板切换（siw_qp_tx.c:210-216）四层闭环，git ae550b5 即该链修复
- tree-sitter 盲区 52 函数补录：module_param 宏 blob 吞 12、siw_verbs.c 指针返回漏 13（create_qp 215 行等）、siw_mem.c siw_umem_get 72 行、大结构体升 class（siw_dev/siw_qp/rx/tx/cep/sqe/cqe）
- merge 基线洞回补：siw_cm_exit（siw_cm.c:1946 void 返回型漏提取）补节点重 merge 零 drop
- "All DMA addresses" 注释实际在 siw_verbs.c:1655（onboard 修正输入材料错锚 1548）
