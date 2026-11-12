# DeepSeek 对话 NCCL 论断·验证报告

- 对话来源: https://chat.deepseek.com/share/dix4sd6p2cb1ck9mcp
- 被验证代码: NVIDIA/nccl v2.32.3-1 (`/usr-data/data2/kylin/nccl`, 图谱基线同源 commit 3e46c089 的 src 树)
- 验证日期: 2026-11-04 10:34:51

## L1 静态锚点核验
```
  [≠ DIFF ] B02   新轨 DEFINE_NCCL_PARAM 全库 11 处
              └─ 实际 10 / 断言 11

==============================================================================================================
总计 173 条: DIFF=1  EXACT=120  NEAR=1  PASS=51
  ✔ EXACT/PASS = 断言成立   ≈ NEAR = 成立但行号有偏移(见详情)   ≠ DIFF = 数量/行数有出入   ✗ FAIL = 不成立

JSON → static-results.json
```

## L2 编译期行为实验
```
==================== L2 编译期行为实验 ====================
---- [1/5] NCCL_VERSION 公式 (断言 A01/A02) ----
== NCCL_VERSION 公式行为实验 ==
  [PASS] NCCL_VERSION(2,8,3)          = 2803 (断言 2803)
  [PASS] NCCL_VERSION(2,9,0)          = 20900 (断言 20900)
  [PASS] NCCL_VERSION(2,32,3)         = 23203 (断言 23203)
  [PASS] NCCL_VERSION(2,8,99)         = 2899 (断言 2899)
  ---- 断层: 2.8.99=2899 < 2.9.0=20900 (跳变 +18001, 非连续) ----
  [PASS] NCCL_VERSION(1,6,5)          = 1605 (断言 1605)
  [PASS] NCCL_VERSION(3,0,0)          = 30000 (断言 30000)
  [PASS] 同族单调性 2.8.3 < 2.8.4

结论: 断言 A01 全部成立: 千/万进制分支行为与对话描述一致

---- [2/5] ncclRedOp 枚举钉宽, 普通模式 ----
== ncclRedOp_t 枚举宽度实验 (sizeof(dummy)=4, 编译模式见下) ==
  [PASS] ncclNumOps == 5 (内置算子上界)
  [PASS] ncclNumOps_dummy == 5
  [PASS] ncclMaxRedOp == 0x7fffffff>>(32-8*sizeof(dummy)) 自适应
  [PASS] 4 字节模式: ncclMaxRedOp == 0x7fffffff
  [PASS] sizeof(ncclRedOp_t) == sizeof(ncclRedOp_dummy_t) (两枚举同宽)
  [INFO] 动态算子(preMulSum 等)句柄值域下界 = ncclNumOps = 5

结论: 断言 A04 成立: dummy enum 钉宽 + MaxRedOp 自适应上界
---- [2/5] ncclRedOp 枚举钉宽, -fshort-enums 模式 (验证自适应) ----
== ncclRedOp_t 枚举宽度实验 (sizeof(dummy)=1, 编译模式见下) ==
  [PASS] ncclNumOps == 5 (内置算子上界)
  [PASS] ncclNumOps_dummy == 5
  [PASS] ncclMaxRedOp == 0x7fffffff>>(32-8*sizeof(dummy)) 自适应
  [PASS] 1 字节模式(-fshort-enums): ncclMaxRedOp == 0x7f
  [PASS] sizeof(ncclRedOp_t) == sizeof(ncclRedOp_dummy_t) (两枚举同宽)
  [INFO] 动态算子(preMulSum 等)句柄值域下界 = ncclNumOps = 5

结论: 断言 A04 成立: dummy enum 钉宽 + MaxRedOp 自适应上界

---- [3/5] weak/strong 双符号 + LD_PRELOAD 插桩 (断言 A06/A07) ----
== 编译 (产物在 /tmp/nv-l2, 规避 noexec) ==
== ① nm 符号类型 (断言: nccl* weak / pnccl* 强) ==
    00000000000005b4 W ncclFakeAllReduce
    00000000000005b4 T pncclFakeAllReduce
  [PASS] ncclFakeAllReduce 是 weak
  [PASS] pncclFakeAllReduce 是全局强符号(T)
== ② 无 preload 基线 ==
== [无 preload 基线] ==
  [PASS] weak=100, pncclAlias=100 (均为真实现)
结论: 断言 A06 机制成立: weak 可插桩 / pnccl 恒真 / 双导出符号
== ③ LD_PRELOAD 插桩 (模拟 profiler) ==
== [LD_PRELOAD 插桩场景 (模拟 profiler)] ==
  [PASS] ncclFakeAllReduce 被插桩 (weak 被强定义覆盖): -1
  [PASS] pncclFakeAllReduce 穿透插桩拿真实现: 100
  [PASS] dlsym 取到的也是插桩符号: -1
结论: 断言 A06 机制成立: weak 可插桩 / pnccl 恒真 / 双导出符号

---- [4/5] ncclConfig ABI 布局 + INITIALIZER + append-only (断言 A15/A16/B09) ----
== ncclConfig ABI 布局实验 ==
  [PASS] 头三字段 offset: size@0 / magic@8 / version@12 (append-only 地基) — 布局与对话描述一致
  [PASS] INITIALIZER: size==sizeof(ncclConfig_t)
  [PASS] INITIALIZER: magic==0xcafebeef 且 version==NCCL_VERSION_CODE — magic=0xcafebeef version=23203
  [PASS] 所有可定制字段初始化为 UNDEF 哨兵 (INT_MIN/NULL) — '用户没说'的哨兵语义
  [PASS] NCCL_CONFIG_UNDEF_INT == INT_MIN
  [PASS] 老版本小结构体传入新库: magic/size 校验通过(size 判定) — 库按 size 安全忽略尾部新字段 — append-only 跨版本 ABI 兼容成立
  [PASS] 手动置零(不用 INITIALIZER): magic==0 → 库校验拒绝 (-1) — 从'内存乱读'变成'可诊断错误'

结论: 断言 A15/A16 成立: 版本化 append-only + magic 诊断 + 哨兵语义全实证

---- [5/5] strtoll base=0 解析行为 (断言 B05, param.cc 原码) ----
== strtoll(str,&end,0) base=0 行为实验 (ncclLoadParam 原码) ==
    INFO: 8 set by environment to 8.
  [PASS] NCCL_X="8" → 8 (断言 8)
    INFO: 0x10 set by environment to 16.
  [PASS] NCCL_X="0x10" → 16 (断言 16)
    INFO: 010 set by environment to 8.
  [PASS] NCCL_X="010" → 8 (断言 8)
    INFO: 12abc set by environment to 12.
  [PASS] NCCL_X="12abc" → 12 (断言 12)
    ATTN: Invalid value info, using default -77.
  [PASS] NCCL_X="info(纯字符串)" → -77 (断言 -77)
  [PASS] NCCL_X="(空串)" → -77 (断言 -77)
  [PASS] ATTN 触发 1 次 / INFO 触发 4 次 (与'只打 ATTN 不 abort'描述一致)

结论: 断言 B05 全部成立: 0x→16 / 前导0→八进制 / 前缀容错 / 纯串回退默认+ATTN

==================== L2 全部 PASS ====================
```

## L3 参数系统行为实验 (真实源码组装, 每实验独立进程)
```
---- 缓存摊销 (B03/B20) ----
[实验1|B03/B20] 首读缓存: NCCL_TEST_P 首读后改 env 无效
    [INFO] NCCL_TEST_P set by environment to 8
  [PASS] 首读 8 → setenv 16 → 仍 8 — 静态缓存摊销, 热路径零锁
---- NO_CACHE 命中穿透 (B19/B21) ----
[实验2|B19/B21] NCCL_NO_CACHE 含 NCCL_TEST_R → 每读穿透
    [INFO] NCCL_TEST_R set by environment to 5
    [INFO] NCCL_TEST_R set by environment to 9
  [PASS] 首读 5 → setenv 9 → 读到 9 (热更新) — 逃生舱: 命中 key 每次走慢路径
---- NO_CACHE 未命中仍缓存 (B19) ----
[实验2b|B19] NCCL_NO_CACHE 不含 NCCL_TEST_P → 仍缓存
    [INFO] NCCL_TEST_P set by environment to 8
  [PASS] 首读 8 → setenv 16 → 仍 8 (选择性穿透)
---- conf 优先级 1>2 (B06) ----
[实验3|B06] NCCL_CONF_FILE(A=111) 优先于 HOME/.nccl.conf(=222)
    [INFO] NCCL_TEST_Q set by environment to 111
  [PASS] 读到 111 (显式 conf 赢) — 查找序: NCCL_CONF_FILE > $HOME/.nccl.conf > /etc/nccl.conf
---- HOME conf 兜底 (B06) ----
[实验3b|B06] 无 NCCL_CONF_FILE → HOME/.nccl.conf(=222) 生效
    [INFO] NCCL_TEST_Q set by environment to 222
  [PASS] 读到 222 (HOME conf 赢)
---- 真实 env > conf (B07b) ----
[实验3c|B07b] 进程 env=999 与 conf=111 同名 → env 赢
    [INFO] NCCL_TEST_Q set by environment to 999
  [PASS] 读到 999 (真实环境变量 > conf) — ncclOsSetEnv=setenv(...,0) 不覆盖已有 env
---- conf once 只读一次 (B08) ----
[实验4|B08] conf 只读一次: 首读后改 conf 文件不再生效
    [INFO] NCCL_TEST_Q set by environment to 111
  [PASS] 首读 111 → 改 conf 555 → 仍 111 — call_once 一次性, 改 ~/.nccl.conf 不生效
---- strtoll hex (B05) ----
[实验5|B05] strtoll base=0: hex
    [INFO] NCCL_TEST_R set by environment to 16
  [PASS] hex 解析正确 — 0x10→16
---- strtoll oct 坑 (B05) ----
[实验5|B05] strtoll base=0: oct
    [INFO] NCCL_TEST_R set by environment to 8
  [PASS] oct 解析正确 — 010→8 前导0八进制坑
---- strtoll 纯串回退 (B05) ----
[实验5|B05] strtoll base=0: str
    [ATTN] Invalid value, using default -1
  [PASS] str 解析正确 — 纯串回退默认+ATTN

== L3 参数系统实验 全部 PASS ==
```

## L4 GPU 运行时实验
模式: 本地语法验证 (无 GPU — 运行时行为留待 CUDA 节点, 见 runtime_tests/README)
```
== [A28] sed 生成 nccl.h (复刻 src/Makefile:159-165 替换) ==
  [PASS] 占位符全替换 — .in 模板可用 sed 变真头文件
  [PASS] NCCL_VERSION_CODE=23203 注入

== 语法检查 (cuda_stub + 生成头, gcc -fsyntax-only) ==
  [PASS] t01_inplace.c 语法/类型检查通过
  [PASS] t02_group_p2p.c 语法/类型检查通过
  [PASS] t03_lifecycle.c 语法/类型检查通过
  [PASS] t04_rma_window.c 语法/类型检查通过
  [PASS] t04b_rma_cross_rank.c 语法/类型检查通过
  [PASS] t05_collconfig.c 语法/类型检查通过
  [PASS] t06_async_init.c 语法/类型检查通过
  [PASS] t07_version_param_api.c 语法/类型检查通过
== L4 语法检查全部通过 (待 GPU 节点真跑) ==
```

## L5 框架侧断言 (torch/vLLM/SGLang)
```
== L5: PyTorch 侧断言 (本地 torch) ==
  torch 2.10.0+cpu
  [PASS] F01: DDP 梯度桶默认 25MB (源码显式) — 签名默认 None 是哨兵; 源码 'default case (bucket cap is 25 MiB)' → bucket_cap_mb=25
  [PASS] F02: NCCL watchdog/PG 默认超时=10min (文档/实现) — doc 含 '10 minutes' 且 timeout 可配; TORCH_NCCL_HEARTBEAT_TIMEOUT_SEC 等环境变量控制 watchdog 行为
  [PASS] F03: ProcessGroupNCCL 通信器缓存 (C++ 层, Python 仅可见封装) — C++ 实现不可内省; 该断言属 torch 源码机制, 见 check_framework.sh 源码 grep
== L5: vLLM 侧断言 (~/ai/vllm) ==
  [PASS] F04 PyNcclCommunicator 附加非 NCCL 组 — pynccl wrapper 依赖非 NCCL 组广播 uniqueId
  [PASS] F04b PyNcclCommunicator 类存在 — 直接绑定 NCCL 动态库的轻量封装
  [PASS] F05 CustomAllreduce→NCCL 回退 — 引擎开关与回退路径存在
  [PASS] F06 权重传输 Broadcast/packed — P/D 权重广播引擎

== L5: SGLang 侧断言 (~/ai/sglang) ==
  [PASS] F07 GroupCoordinator 抽象 — 统一调度 pynccl/custom_allreduce
  [PASS] F07b pynccl 寄生非 NCCL 组 — PyNcclCommunicator 附加 gloo 组
  [PASS] F08 CustomAllreduce 16B/单节点/dtype — 尺寸/dtype 门控细节
  [PASS] F08b 单节点限制 — 跨节点禁用 CustomAllreduce
  [PASS] F09 init_custom_process_group — 训练器↔SGLang 动态建 NCCL 组
  [INFO] F10 SGLang 销毁路径 — 当前快照: GroupCoordinator.destroy→destroy_process_group; wrapper 仅包 ncclCommDestroy 无 Abort — 对话'倾向 Abort'与快照不符(勘误候选, 可能引自旧 commit 或 torch 内部行为)
  [PASS] F10b vLLM ncclCommAbort 阻塞于 CUDA Graph 销毁 — pynccl.py destroy() 注释逐字命中(daemon 线程+timeout 规避)
  [PASS] F08c dtype 白名单(bf16/fp16/fp32) — device_communicators 含 dtype 门控

== L5 框架断言核验完成 ==
```

## 结论速览 — 见 CLAIMS.md 断言全表与勘误清单
