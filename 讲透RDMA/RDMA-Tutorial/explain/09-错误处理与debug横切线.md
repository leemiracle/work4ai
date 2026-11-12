# 09 · 错误处理与 debug 横切线：debug.h 与全仓 error 路径审计

## ① 角色定位

debug.h（43 行）是全仓唯一"每个 .c 都 include 的头文件"（debug.h:5-10 只依赖 stdio/errno/string，自身零依赖，天然可横切）。它出身公开：文件头注释标明来自 *Learn C the Hard Way* 练习 20（debug.h:2，LCTHW ex20），是 Zed Shaw 的错误处理宏框架。这层横切线与 check/goto error 范式共同构成全仓的**错误处理合同**：任何函数失败即跳自身 error 标签做本地清理，返回 -1 逐层上传，最终在 main.c:41-43 的 error 标签统一收尾。本篇做两件事：拆解宏框架本身，然后**横切审计**七个 .c 文件的 error 路径回收完整性——这一审计把散落在组 1 各篇的"泄漏点"统一成一账。

## ② 内部结构

宏家族全景（按输出通道分组）：

| 宏 | 行号 | 行为 | 全仓调用 |
|---|---|---|---|
| log_err | debug.h:19-20 | stderr，前缀含 `__FILE__:__LINE__:__func__: errno` | 仅被 check 间接使用 |
| log_warn | debug.h:22-23 | stderr WARN 前缀 | **0 次（死宏）** |
| log_info | debug.h:25 | stderr 裸文本 | 仅被 log(debug) 组合使用 |
| log_file | debug.h:27 | 写 log_fp 且**每条 fflush** | 仅被 log 组合使用 |
| log | debug.h:37/40 | 双通道：DEBUG 版 log_info+log_file，release 版只写文件 | 全仓主力，约 30 处 |
| check | debug.h:31 | 断言失败→log_err→**errno=0**→goto error | 全仓主力，约 50 处 |
| sentinel | debug.h:29 | 无条件 log_err+goto error | **0 次（死宏）** |
| debug / debug_detail | debug.h:34-36/39 | DEBUG 版 stderr，release 版空展开 | debug 若干处；debug_detail **0 次** |

配套件：`clean_errno()`（debug.h:17）把 errno==0 显示为 "None" 否则 strerror；LOG_HEADER/LOG_SUB_HEADER（debug.h:12-13）两条分隔线格式串；`extern FILE *log_fp`（debug.h:15）声明、main.c:10 定义、init_env 里 fopen（main.c:56，文件名 server[rank].log / client[rank].log，main.c:52-54）。DEBUG 宏的开关在 Makefile 的 `make debug`（-DDEBUG，Makefile:13），改的是 log 宏的第二通道（debug.h:33-41 的条件编译）。

## ③ 外部连接

横切结构的接线方式值得注意：log_fp 是**全局变量跨模块共享**——debug.h 只有 extern 声明，定义在 main.c:10，七个 .c 经 include 拿到同一符号。这意味着 debug.h 与 main.c 存在一条隐式编译耦合：任何想用 log 宏的模块都必须链接到 main.o 的 log_fp（链接期未定义符号会暴露这一点）。check 宏的 `goto error` 则是另一条隐式合同：**使用 check 的函数体内必须存在 error 标签**——宏展开后跳转的目标由各文件自己提供，编译器保证存在性（缺标签直接编译错），这是 goto 在 C 错误处理里罕见的安全用法：跳转半径被限制在单函数内。

## ④ 数据流

**一次 check 失败的完整旅程**（以 setup_ib.c:282 mr 注册失败为例）：`ibv_reg_mr` 返回 NULL → check 展开 `if(!(NULL)) {log_err(...)}` 打印 `ib.c…` 式定位信息（实为 setup_ib.c:282 所在的 FILE/LINE/func）与 strerror(errno) → **errno=0**（防后续清理路径的 clean_errno 误报旧值）→ goto error → 本函数 error 标签 free dev_list（setup_ib.c:336-338）→ return -1 → main.c:32 check 捕获 → main 的 error 标签 close_ib_connection + destroy_env（main.c:41-43）→ 进程退出。注意 setup_ib 自己的 error 路径**不回收**已创建的 ctx/pd/cq/qp——它把兜底完全交给 main 层的 close_ib_connection（setup_ib.c:342-378 判 NULL 幂等），这是"本地清 socket、全局清 verbs 资源"的两层分工。

**逐文件 error 路径审计表**（源码逐一核对）：

| 文件 | error 标签回收 | 完整性判定 |
|---|---|---|
| main.c:41-43 | close_ib_connection + destroy_env，均判 NULL | 完整（含正常路径 fall-through） |
| config.c:197-201 | 关 fp | fp 之外无资源，完整 |
| config.c:88-89 | return -1，不回收 *node_list | 部分泄漏（进程即退，无实害） |
| sock.c:90-97/134-141 | freeaddrinfo + close | 完整 |
| setup_ib.c:335-339 | 只 free dev_list | 靠 main 兜底，设计内 |
| setup_ib.c:113-126 | 关 socket、free peer_sockfd | **泄漏 local/remote_qp_info**（正常路径 L108-109 同样不 free，onboard 坑 3） |
| setup_ib.c:218-236（client 侧） | 全部回收 | 完整（与 server 侧不对称） |
| client.c:160-164 / server.c:159-163 | free(wc) + pthread_exit(-1) | wc 完整；**server.c:43/54 重复 calloc 覆盖指针**是另一类缺陷（第 6 篇⑤②） |
| client.c:210-216 / server.c:206-212 | free 线程数组 + attr_destroy | 完整 |

三个范式外的旁路：① main.c:19-22 argc≠3 时 printf usage 后 **return 0**——参数错误被 shell 判为成功，脚本化调用会静默吞错；② config.c:64-68 parse_node_list 的 calloc 失败走 printf+return 0 而非 check——返回 0 恰好被调用方 `check(ret>0)`（config.c:169）捕获，行为碰巧正确但范式不一；③ **setup_ib.c:299 `ibv_create_srq` 是全仓唯一无 check 的资源创建调用**——失败时 srq=NULL 继续，ibv_create_qp 携带 NULL srq 会静默退化为无 SRQ 的普通 QP（语义改变而非报错），直到数据面 post_srq_recv 对 NULL 操作才崩溃——错误被推迟到离病因最远的地方。

## ⑤ 设计决策

**① errno=0 的防御性重置**：LCTHW 框架的细节。清理路径中若再次调用 log 类宏，clean_errno 会读到上一次失败残留的 errno，把无关错误串进日志造成误导——check 在跳转前清零，保证后续日志的 errno 语义干净。

**② log_file 每条 fflush**：基准程序可能死于任何一处段错误（热路径大量指针运算），不 flush 的 stdio 缓冲会让最后数十条日志消失——崩溃现场与死亡原因一起丢。逐条落盘是以微小性能换**日志的崩溃保全性**，对调试教程是正确取舍（release 版日志频率低，fflush 代价可忽略）。

**③ 集中式兜底而非逐层回收**：setup_ib 的错误路径几乎不回收 verbs 资源，信任 main 的 close_ib_connection 全量兜底。这避免了两层清理的double-free 风险（close 判 NULL+清 ib_res 全零使幂等成立），代价是 close_ib_connection 必须**严格按依赖逆序**销毁（qp→srq→cq→mr→pd→ctx→buf，setup_ib.c:346-377）——顺序错了（如先销毁 pd 再销毁用着它的 qp）verbs 层直接报错。

**④ 线程错误用 pthread_exit 而非 goto 之外的返回**：工作线程不能 return（会绕过 join 的状态回收），pthread_exit((void*)-1) 把失败码塞进 join 的 status（client.c:194-199 捕获），run_* 汇总 thread_ret_normally 再决定返回值——错误码沿"线程→join→run_*→main"三级管道上传，每级都有显式检查。

## ⑥ 新人提示

建议把本篇的审计表当作改代码前的 checklist。死代码清单（grep 实证各仅定义处一次）：sentinel（debug.h:29）、log_warn（debug.h:22）、debug_detail（debug.h:34）、SIG_INTERVAL（ib.h:17）、htonll/ntohll（ib.h:20-24）——五个死宏/死函数说明这个框架是从更完整的模板裁来的，也说明**宏框架的"全家桶"里一半能力从未被本仓用到**，读 LCTHW ex20 原文能看到完整用法。两个上手段实验：① 在 setup_ib.c:299 后补一行 `check(ib_res.srq != NULL, ...)` 观察行为不变（正常路径无感），再故意把 srq_init_attr.max_wr 设成非法值看报错位置从"数据面崩溃"提前到"创建即败"；② 把 main.c:21 的 return 0 改成 return 1，体会"usage 错误返回码"对脚本化的重要性。若要给本仓加第三种日志级别（如带时间戳的 benchmark 数据行），debug.h:27 的 log_file 是唯一需要动的宏——所有调用方自动获益，这正是横切层的修改红利。
