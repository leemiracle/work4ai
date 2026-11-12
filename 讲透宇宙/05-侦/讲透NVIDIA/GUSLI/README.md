# 讲透 GUSLI

NVIDIA [GUSLI](https://github.com/NVIDIA/GUSLI)——Gusli（G3+ User Space Access Library）：C++ 用户态块设备 IO 库。client .so 供 IO 提交方、server .so 执行 IO，两进程同机用户态经共享内存零拷贝通信（控制面 UDS/TCP/UDP socket + 数据面共享内存 SQ/CQ 环），无内核组件；1 client 连多 server，每 server 代表一个块设备（SPDK bdev/文件/内核块设备/dummy）。client/server 分离的动机是解耦编译链接依赖——后端是 SPDK 不代表 client 应用也得是。

## 全链状态表

| 阶段 | 状态 | 明细 |
|---|---|---|
| DeepWiki | ✗ 未收录 | 后台未索引（收录决定权钉版），**本图谱为唯一知识源** |
| understand 图谱 | ✅ | 199 节点 / 345 边 / 9 层 / 14 步 tour，validator 0 issues |
| fingerprints | ✅ | 41 文件基线 @d3fb64e0 |
| onboarding | ✅ | [ONBOARDING.md](onboarding/ONBOARDING.md) 5933 字（不计空格；行号锚密度致略超 5000 上限，与本流水线既往 explain 2500-4800 norm 一致）8 节 73 锚 |
| explain | ✅ | 3 篇（2770/3128/3656 字不计空格，44/56/60 锚，40 点自动核对 0 坏锚）：[01 数据面环](explain/01-数据面dp_io_ring零拷贝环.md) / [02 API 门面与 client 引擎](explain/02-双API门面与client引擎.md) / [03 server 引擎与示例家族](explain/03-server引擎与示例家族.md) |

图谱位置：仓内 `.understand-anything/knowledge-graph.json`。

## 结构速览（九层纵队）

- `00utils/` 内核风格原语（三态锁/位图/侵入式链表/三模 socket/invoke_crash 崩溃注入）
- `01common/` 控制面 MGMT 消息协议 + 共享内存注册表 + 数据面 io_csring 环（模仿 NVMe SQ/CQ 的 datapath_t<T> 模板六方法）+ 在途 IO 跟踪
- `gusli_{client,server}_api.hpp` 双单头门面：client 侧 bdev_config_params 五型设备（'F'/'K'/'N'/'x'失败/'s'卡死）+io_request_base 位域 params_t+global_clnt_context 单例；server 侧 srvr_backend_bdev_api 三纯虚（open1/close1/exec_io）
- `05clnt/` 客户端引擎（16 方法+五种执行器 blocking/sync/aio/uring/never_reply）
- `03backend/` 服务端引擎（握手/注册/IO 派发/事件循环）
- `07examples/server/` 参考实现光谱：fail/zero 故障注入→只读 RAM→SPDK 生产级；`unitest/` 876 行十七组测试；`80scripts/` NIXL/SPDK 依赖搭建+service.sh 调试命令库

## 甄别精选（详见 onboarding §7，行号实证）

1. **tested_by 6 条被 merge 词法误杀后人工回补**：merge 的 test 判定只认 test_/_test 词干，unitest.cpp 不匹配——端点全真实，按真实测试关系回补
2. Makefile:128 无 git 时 dummy `VER_TAGID:=v3.1.0` 与 CHANGELOG v0.0.4 矛盾——版本烟雾弹
3. `io_submittion_example.hpp` 文件名拼写错误（submittion→submission）
4. cp_messaging.hpp:197/223 `while(true)` 后不可达 return（死代码）
5. `wrap_remote_io_exec_blocking::is_still_running`（io_executors.hpp:298）名为查询实为阻塞等待，语义陷阱
6. 代码自认竞态两处：client_imp.cpp:620 "fix me" 注释、:673 nvTODO use-after-free
7. 容量口径三层差：bdev_info 注释 [1..500] vs small_ints_set<512> 硬上限 vs 示例 256+环 512 的 throttle 保证
8. SECURITY.md 威胁登记（UDS chmod 0777、恶意 n_entries DEFERRED HIGH）与单机信任模型边界
9. io_multi_map_t._reserved 魔数 0x6f696d6d（"oimm"）做 client/server 映射错检；三处 bdev_descriptor 魔数不一致（100000001/202020202/555，仅日志用）

## 工艺备注

- imports 51 条=45 scanner 全量对账+6 条手工补齐（Makefile L53 -I00utils -I01common 解析坐实）
- tree-sitter 盲区四型全命中：template 类全盲（datapath_t+六成员函数）、#ifdef 整块盲（uring_request_executor L337-446、spdk_app_1server 全文件）、文件尾 include 后的类（utils.hpp base_library）、纯宏头零提取（dp_logging.hpp）——全部人工源码补齐
