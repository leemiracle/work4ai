# 讲透 qperf

[linux-rdma/qperf](https://github.com/linux-rdma/qperf) @118a571 · RDMA/网络带宽与延迟基准测试工具（socket/RDS/RDMA 三代传输 + XRC）

| 产物 | 状态 | 明细 |
|---|---|---|
| deepwiki | — | NOT_INDEXED → repo-docs 兜底（1 文件） |
| understand 图谱 | ✅ | 253n/396e/16 层/15 步 tour · validator 0 issues · fingerprints 19 files@118a571e |
| onboarding | ✅ | 5975 字 8 节 · 61 锚机械校验零坏 |
| explain | ✅ | 12 篇 54455 字符 · 383 锚终验真坏 0（1 处正则假阳性已消歧） |

## 源码级勘误精选

- **qperf.h 三个死原型**：`check_remote_error`(qperf.h:257)/`run_client_bug`/`run_server_bug`(qperf.h:308-309) 全仓无定义无调用
- **头文件注释漂移**：RDS 测试原型错挂 "Socket tests in socket.c" 节下（qperf.h:281，实现在 rds.c:123）；send_mesg/recv_mesg 注释列在 qperf.c 段而实现在 support.c
- **版本考古**：src/qperf.c VER_ 0.4.11 vs configure.ac 0.4.10 vs spec 0.4.10——ver_inc 四处同步协议允许漂移，RPM 元数据落后一个增量版
- **许可证口径差**：COPYING 仅 GPLv2 全文，源文件头实为 GPLv2/OpenIB 两条款 BSD 双许可，qperf.spec.in:4 "BSD 3-Clause" 系打包惰性标注与两条款矛盾
- **rdma.c:1586 格式串 bug**：5 占位传 6 参数（explain 组1 新发现）
- ServerAddr/ServerAddrLen 死存储（qperf.c:1527-1528 只写不读）
- **rd_open 非"回退"语义**：与 rd_open_ib 是 use_cm 二选一（onboard 纠图谱摘要）
- 帮助系统：help.c/qperf.1 为构建期产物不在仓内（Perl mkhelp/mkman 生成）；mkhelp/mkman 本身是 Perl 脚本被 scanner 标 unknown 零提取，图谱手工补 7 个 sub 节点
- tree-sitter 盲区补漏 21 函数：rdma.c #ifdef HAS_XRC 块 6 个 XRC 入口（L770-840 整体漏）、qperf.c 9 个星号/指针返回类型函数等
