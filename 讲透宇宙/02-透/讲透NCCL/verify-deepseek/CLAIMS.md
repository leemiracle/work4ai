# CLAIMS.md — DeepSeek 对话 NCCL 论断·断言全表

来源对话：https://chat.deepseek.com/share/dix4sd6p2cb1ck9mcp（用户把本仓 v2.32.3 的
nccl.h.in / 参数系统 / init.cc / bootstrap.cc / graph/search.cc 五份精讲文档喂给 DeepSeek
后的深度解析，外加 PyTorch/vLLM/NIXL/UCX/SGLang 关系问答）。

验证分层：**L1** 静态锚点核验（`check_static.py`，173 条机读断言）
**L2** 编译期行为实验（`compile_tests/`） **L3** 参数系统行为实验（`unit_param/`，真实源码组装）
**L4** GPU 运行时实验（`runtime_tests/`，语法已验/待真机） **L5** 框架侧断言（`framework_checks/`）

## 总判定

| 层 | 规模 | 结果 |
|---|---|---|
| L1 静态 | 173 条 | ✅ 171 成立（120 EXACT + 51 PASS）· 1 行号漂移（A16, +22 行）· 1 数字错误（B02） |
| L2 编译期 | 5 组 | ✅ 全部成立（版本公式/枚举钉宽/weak-strong 插桩/ABI append-only/strtoll 三坑） |
| L3 参数系统 | 10 实验 | ✅ 全部成立（缓存/NO_CACHE 穿透/conf 优先级/env>conf/once/八进制坑） |
| L4 运行时 | 8 程序 | ⏳ 语法全过，待 CUDA 节点真跑（断言映射见 runtime_tests/README.md） |
| L5 框架 | 14 条 | ✅ 13 成立 · 1 与快照不符（F10 SGLang "倾向 Abort"） |

**总评：对话对五份源码精讲的转述近乎全对（这是行号锚定文档的转述）；实质错误仅计数
一处（B02，源头还是本仓 explain 文档自身）与 SGLang 快照偏差一处（F10）。首轮曾多判
一条"CLI 幻觉"，复核后翻案——该说法同样源自本仓 explain 文档且实际正确（见"验证者自纠"）。**

## 勘误清单（验证发现的与对话不符处）

| # | 断言 | 对话说法 | 实测事实 | 定性 |
|---|---|---|---|---|
| 1 | B02 | 新轨 DEFINE_NCCL_PARAM **11 处**（8 个在 debug.cc:43-117） | **10 处**：debug.cc 8 个（第 8 个在 **:479** 不在 43-117 段）+ param/param.cc 2 个。⚠️ 错误源头是本仓 explain/02-param-system.md 自身，DeepSeek 转述传播（已回写修正） | 数字勘误 |
| 2 | F10 | SGLang 关闭路径"**倾向 Abort** 而非 Destroy" | 本地 sglang 快照：`GroupCoordinator.destroy()`→`torch.distributed.destroy_process_group`（parallel_state.py:1386-1395）；pynccl_wrapper **只包 ncclCommDestroy 无 ncclCommAbort**。对照：**vLLM** 侧倒是逐字命中（pynccl.py:250-258 注释"ncclCommAbort can block until all CUDA graphs…"） | 张冠李戴候选（或引自旧 commit） |
| 3 | A16 | magic 校验在 init.cc:**2558** | 实际 **init.cc:2572**（+22 行漂移，内容正确：parseCommConfig 检查 NCCL_API_MAGIC；源头同为本仓 explain/01-api-surface.md:51，已回写） | 行号漂移 |

## 验证者自纠（重要：验证套件自身的一条假勘误）

| 事项 | 经过 | 教训 |
|---|---|---|
| F23 `ncclparam -l` | 首轮把"对话说跑 `ncclparam -l`"判为 **DeepSeek 幻觉**（absent 检查全源码内容 0 命中）。次日归档时发现源头是**本仓 explain 文档**（02-param-system.md:58 原文就这么写），进而全仓复核翻案：`src/param/ncclparam.cc` 真实存在（`strcmp(argv[i], "-l")` 逐字实现，调 ncclParamDumpAll），`src/Makefile:71` `PARAMBIN := ncclparam` 单独构建、`:322` 安装到 `$(PREFIX)/bin/`。**对话这条完全正确。** | ① absent 型断言只搜源码**内容**会漏构建目标/文件名维度（ncclparam.cc 内容全是 PascalCase 符号，Makefile 无 .mk 后缀不在遍历集）②"查无"≠"不存在"，先怀疑检查器的覆盖面 ③验证者也会被验证——每条勘误发布前应做反向复核 |

## 对话漏说但实验补全的语义（增量发现）

| # | 发现 | 证据 |
|---|---|---|
| 1 | **PROFAPI 门控**：weak/strong 双符号机制只在 `PROFAPI` 构建分支生效（core.h:17-23），对话未提 | core.h 源码；L2 nm 实验注释 |
| 2 | **conf 不覆盖真实环境变量**：`ncclOsSetEnv = setenv(name, value, 0)`（overwrite=0）→ 优先级=进程 env > NCCL_CONF_FILE > ~/.nccl.conf > /etc/nccl.conf，对话只说"批量 setenv" | os/linux.cc:111-113；L3 实验3c 实证 env=999 赢 conf=111 |
| 3 | **NCCL_CONF_FILE 是分支而非瀑布**：设置了 NCCL_CONF_FILE 就**不再读** HOME conf（仍读 /etc/nccl.conf） | param.cc:52-67 代码路径；L3 实验3/3b |
| 4 | **NCCL_NO_CACHE 名单本身首读快照**：进程内后续 setenv NCCL_NO_CACHE 无效（它自己也是 CACHED 参数） | param.cc:20-21 CACHED flag；L3 实验时序踩坑实录 |
| 5 | **重复 key 注册是 WARN+错误码不是 abort**：`WARN("PARAM: Duplicate registration...")` + return ncclInternalError | param_registry.cc:19-24 |

## 断言全表（按主题，L1 层逐条见 static-results.json）

### A. nccl.h.in 公共 API（38 条 → 37 成立 + A16 漂移）
版本宏千/万进制断层（A01, L2 实证 2803/20900/23203/断层+18001）· 128 字节 uniqueId（A03）·
RedOp dummy enum 钉宽（A04, L2 双编译模式实证）· 12 datatype fp8=10/11（A05）·
pnccl weak/strong（A06, L2 nm+LD_PRELOAD 实证）· map 只导出 nccl*/pnccl*（A07）·
五条 in-place 注释条件（A10）· deprecated Bcast（A11）· Reduce recvbuff root-only（A12）·
AllGather 无 recvcount（A13）· Config 变体 683-725（A14）· v23100 append-only+INITIALIZER
（A15, L2 offset/magic/旧结构体兼容实证）· ext 后门 173-184（A17）· 窗口 flags/4096 对齐
（A20/A21, L4 t04 语法待真机）· RMA 三原语（A23）· sed/cmake 双路径（A28, L4 check_syntax
实证 sed 生成 nccl.h）· TLS OpenSSL（A33）· NvlsHostMode 四档（A34）·
MemStats 四枚举（A37: Suspend/Suspended/Persist/Total——对话说"字段"实为枚举+查询函数，语义等价）

### B. 参数系统（24 条 → 23 成立 + B02 数字勘误）
双轨制（B01/B02）· 两段式宏+静态缓存（B03, L3 实证缓存摊销）· 慢路径互斥锁（B04）·
strtoll base=0 三坑（B05, L2+L3 三重实证 0x10→16/010→8/纯串回退+ATTN）·
conf 三级优先级（B06, L3 实证 111>222）· setEnvFile 批量 setenv（B07）·
once 只读一次（B08, L3 实验改 conf 后仍 111）· INT_MIN 哨兵（B09, L2 实证）·
DEFINE_NCCL_PARAM 模板（B10-B12）· 六 flag（B13）· C 链接单例 registry（B14/B15）·
bind 三查+typeId+thread_local（B16-B18, L4 t07 语法待真机）· NO_CACHE 自举+逗号列表
（B19, L3 实证命中穿透 5→9、未命中仍 8）· MAX_CTAS 数据流（B20）

### C. init.cc（29 条全成立）
4007 行最大文件（C01）· 三层入口（C02）· 异步 init 立即发布句柄（C03, L4 t06 待真机）·
八阶段 Init timings 日志（C08）· split/shrink 复用 bootstrap（C09/C10）· fillInfo+commHash
（C11）· 版本 fail/能力交集（C12/C13: `Mismatched NCCL version`→ncclInvalidUsage；cuMem/ gin/
rma/cft &= 交集）· nranks+1 坑位（C14）· 五张图（C15）· IGNORE_*_MISMATCH（C17）·
CollNet 节点阈值禁用（C18: collNetNodeThreshold）· runtimeConn 默认（C20, init.cc:65
`NCCL_PARAM(RuntimeConnect, "RUNTIME_CONNECT", 1)`）· devCommSetup/workFifo（C21）·
commReclaim/finalizeRankCnt/兄弟补跑（C22）· Finalize 非前置（C23, L4 t03 待真机）

### D. bootstrap.cc（26 条全成立）
1594 行（D01）· uniqueId=婚介所+暗号（D02-D04）· root 从首连接学习 `if (c==0)`（D05b）·
多 root 纯函数组 51-93（D07）· 八步建环全锚点（D08）· stagger 256/7000（D09,
bootstrap.cc:750-751 双参数定义实证）· RAS 参与 ringAllInfo（D10）· Split 不走 root（D11）·
tag 常量 25-29 五枚（D12c: CONNECT/ALLGATHER/COMMSPLIT/INTRANODE_ALLGATHER/GROW_BOUNDARY）·
TLS (peer,tag) 保序（D13）· 双向双环 ⌈N/2⌉（D14）· dissemination barrier（D15）·
close 时 unexpected=错误（D16）· checkAbort 10000（D17, BOOTSTRAP_N_CHECK_ABORT=:24）·
OOB_NET_ENABLE 默认 0（D18, bootstrap.cc:106）· socketSend 先长后体（D19）·
运行期 ~16 文件消费（D21）

### E. graph/search.cc（31 条全成立）
1557 行（E01）· 三级 timeout（E03: `NCCL_SEARCH_GLOBAL_TIMEOUT (1ULL<<19)`/`1<<14`/`1<<8`
:333-336）· LOC_BW 5000.0（E04b）· Intel TLP 6/5+pre-Ampere 1/8+POWER 反向（E06）·
SUB_ROUND（E07）· rewind（E08b）· cmpScore 四级（E09）· NVSwitch 邻居优先（E10: :294-295
注释原话"NVSwitches prefer…neighbors first"）· Ring=Split Tree Loop（E11）·
FORCED_ORDER_PCI/REPLAY（E12）· NIC 轮转+asic/port 扣带宽+head 去重（E13）·
CompareGraphs 五级判优（E18）· 速度档位表含 Rubin 280.8（E19）· GRAPH_FILE/DUMP_FILE
（E20）· ccMin≥90（E21）· minChannels=2（E22）· 兜底 bw=0.1（E23）· PXN 默认 2（E24b）·
CROSS_NIC 默认 2（E26）

### F. 关系问答（14 条 → 12 成立 + 1 与快照不符 + 1 无法本地验证）
P2P 无 tag（F11 ✓）· NCCL_PLUGIN_P2P 非本体变量（F12 ✓ absent 实证；UCX 插件属 HPC-X 侧）·
NCCL_NET_PLUGIN 存在（F12b ✓）· ibverbs 直连路径（F24 ✓）· **ncclparam CLI 存在且支持 -l**
（F23 ✓ 翻案：src/param/ncclparam.cc + Makefile:71/322；首轮误判幻觉已自纠，见上节）·
torch DDP 25MB（F01, L5 源码"default case (bucket cap is 25 MiB)"）· torch 10min 超时
（F02 ✓）· vLLM PyNcclCommunicator 寄生非 NCCL 组（F04 ✓）· CustomAllreduce→NCCL 回退
（F05 ✓）· 权重 Broadcast+packed（F06 ✓）· sglang GroupCoordinator（F07 ✓）·
CustomAllreduce 16B/单节点/dtype 白名单（F08 ✓）· init_custom_process_group（F09 ✓）·
vLLM ncclCommAbort×CUDA Graph 阻塞（F10b ✓ 源码注释逐字命中）·
NIXL "SM tax 30-50%"（F13 — 外部 MI300X benchmark 引用，无法本地验证，不判）
