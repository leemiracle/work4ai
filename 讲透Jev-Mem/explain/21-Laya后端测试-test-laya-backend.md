> 标题：Laya 后端测试——本地决策后端的质量闸门 · 源文件：tests/test_laya_backend.py（279 行）· 图谱标签：测试层

## 角色定位

HEAD 提交 7ab0c73（"Add optional Laya backends and integration guide"）的验收测试。首行规格宣言（tests/test_laya_backend.py:1）："Exercise local decisions through the same budget/validation/cache as Jev"——Laya 作为本地决策后端不是绕过通道，必须与远程 Jev 走完全相同的 CallBudget 预算、概率校验、缓存与失败策略管线。被测面横跨 memory/laya_backend.py（64 行本地推理封装）、jev_client.py 的 laya 分支、jev_mem_config.py 校验器、jev_mem_retrieval.py 并发槽位四层。

整套测试**纯离线可跑**：不装 laya 权重（假模块注入，tests/test_laya_backend.py:36-37）、不留 TYPESAFE_API_KEY（tests/test_laya_backend.py:38 主动删除）、远程 SDK 被 sabotaged 成 pytest.fail（tests/test_laya_backend.py:49）。CI 双矩阵（ubuntu/macos）跑 `python -m pytest -q`（.github/workflows/ci.yml），本文件随默认套件执行，无密钥无网络。

## 内部结构

- `install_fake_laya`（tests/test_laya_backend.py:14-39）核心夹具：`monkeypatch.setitem(sys.modules, ...)` 把 laya 与 laya_mlx 双双换成带 `load` 的假模块；default_predict 对 noul 型问题回 0.8、对 choice 型回首选项加独热分布（tests/test_laya_backend.py:17-30）；loads/calls 两个列表是断言探针。
- 协议与缓存主测（tests/test_laya_backend.py:46-70）：断言 load 选项形状（51-54——torch 后端只传 device/subfolder，mlx 才带 batch_size）；混合 Noul+Choice 一次 evaluate（55-64）；小批量 usage 翻倍而预算只记一次（64-65）；二次同参命中缓存、usage 置空、predict 不再触发（66-68）；close 后 agent 置 None（69-70）。
- 失败策略复用（73-82）：假 predict 回 NaN，断言 ValueError 走既有 fallback——fallback_to_magma 开则返回 None、关则抛 JevUnavailable 且消息含 ValueError。
- deadline 语义（85-94）：注入单调钟序列 0、0、2（89-90），第三读数越界触发 laya_deadline（91-93），并断言缓存为空（94）——迟到结果永不入缓存。
- 预算闸门（97-104）：CallBudget 上限为零，predict 从未被调（104）。
- 隔离与设备（107-119）：jev_mock 与默认 jev 后端不触碰 laya（111 断言 `_laya is None`）；伪 platform 为 darwin 时 laya.load 收到 cpu。
- 并发排队（122-166）：手搓 ObservedLock 包装真实锁（145-154），证明第二个检索在第一个持槽时排队而非并发起跑 deadline（159-161），两个结果都带 retrieval_queue_seconds 元数据（164-165）。
- 槽位释放（169-181）：_query 抛异常后锁仍可用（180）。
- 可选依赖提示（184-187 与 215-218）：ImportError 消息带 pip 安装指引 `.[laya]` / `.[mlx]`。
- 配置校验（190-231）：六组非法值、两份仓库配置 roundtrip（198-204、221-231）、mlx 设备白名单拒 cuda。
- mlx 专项（207-212）：auto 设备映射为 None，且 laya 模块置 None 证明 mlx 路径不 import torch 侧运行时。
- 全栈冒烟（241-279）：MockEncoder+NumpyVectorDB+TRG+MemoryBuilder 全链——建两节点、save/close、重建 load、查询，断言后端元数据贯通（265、275）、零 fallback 事件（276）、远程 SDK 从未构造（277）。

## 外部连接

顶层 import 三样：typesafe_sdk 的 Choice/Noul 协议类型（tests/test_laya_backend.py:8）、memory.jev_client 的 CallBudget/JevClient/JevUnavailable（10）、memory.jev_mem_config 的 JevMemConfig（11；config 助手 42-43 固定零重试）。函数内惰性导入织入更广被测面：memory.local_device（115）、memory.jev_mem_retrieval.RetrievalController（126 与 172）、memory.memory_builder.MemoryBuilder 及 mock_encoder/query_engine/trg_memory/vector_db 四件套（244-248）。数据依赖 config/laya_mem.json 与 config/laya_mlx_mem.json（200、223）、pyproject.toml:24-25 的 extras 版本钉死、docs/laya.md 集成指南（Laya 只替换 System-One 决策）。测试叶子节点，无文件 import 它（pytest.ini 的 testpaths=tests 收集）。

## 数据流

旗舰测（46-70）沿真实管线走一遍：JevClient.evaluate 先构造 sha256 缓存键（memory/jev_client.py:147-152）→ budget.consume 扣一次（jev_client.py:174）→ laya 分支调 LayaBackend.predict（jev_client.py:182-189）→ 按 batch_size 分批推理并累加 usage（memory/laya_backend.py:43-53）→ `_validate` 的独热分布恰好通过"覆盖全选项、和为一、选中项最大"三道校验（jev_client.py:262-268）→ ProbabilityResult 带 source 与 usage 返回（jev_client.py:197-198）→ 深拷贝入缓存（jev_client.py:199-204）。二次同键命中：source 改写为 cache、usage 清空、cache_hits 加一（jev_client.py:163-167）。两个语义被钉死：**usage 按内部前向次数累计而预算按 evaluate 次数计**——batch_size 为一的两题 predict 两次、input_tokens 相加翻倍，budget.calls 只加一（tests/test_laya_backend.py:64-65）。

deadline 测的时钟注入对应 memory/laya_backend.py 三处 monotonic 读：起算 deadline（34 行）、批前检查（44 行）、批后拒绝迟到（49 行）。迟到抛 TimeoutError 在 jev_client.py:186-187 转 JevUnavailable；缓存写入只在完整成功后发生（jev_client.py:199-204），"迟到不落缓存"由管线顺序保证、94 行断言守护。

## 设计决策

**假模块注入优于 mock 类**：LayaBackend 用 importlib 动态导入（memory/laya_backend.py:14），把 sys.modules 条目换成 SimpleNamespace 即可拦截，于是真实代码路径（含 ImportError 改写成安装指引，laya_backend.py:15-18）全部被执行而非被绕过。None-in-sys.modules 在 Python 3.12 抛 ModuleNotFoundError（本机 3.12.12 实测），这是 184-187 与 215-218 能测到指引文案的前提——若某版本改抛裸 ImportError，这两测会静默失效，升级解释器时留意。

**参数化双后端**（46、73、85、97、122、169、241 七处）：两后端唯一分叉是 load 选项形状（memory/laya_backend.py:24-29），测试用精确 dict 相等（51-54、212）钉死它——torch 版不透传 batch_size、mlx 版 auto 设备映射为 None。**ObservedLock 手搓探针**（145-154）是本文件最漂亮的技巧：包装真实锁只为在第二个等待者到达时点亮事件，把"检索先排队、deadline 后起算"这条时序契约（jev_client.py:108-117 的 retrieval_slot 加 memory/jev_mem_retrieval.py:21-29 的排队计时）变成可断言的可见性。**失败也放锁**（169-181）补异常路径，对应 predict 的 finally 释放（laya_backend.py:59-60）。

**批判两点**。其一，两处配置测试用相对路径 config/laya_mem.json（200）与 config/laya_mlx_mem.json（223），pytest.ini 只设 testpaths 不切目录——隐式依赖从仓库根启动；CI 恰好如此（ci.yml 在 checkout 根跑 pytest），但从 tests/ 目录下直跑就会假失败，属可移植性债。其二，monkeypatch 模块属性 `memory.laya_backend.time`（90）耦合了被测模块"按名导入 time"的实现细节，重构成 `from time import monotonic` 即断掉——Instrumentation 与实现耦合的常见脆性。

## 新人提示

入门顺序：先读 install_fake_laya（14-39）加旗舰测（46-70），这对"夹具+断言"就是本地后端的契约书；再挑失败语义三条（73-94）读。跑法：仓库根 `pytest tests/test_laya_backend.py -q`，无需安装 laya、无需密钥，秒级完成。想加行为（新选项、新失败模式）：扩展 default_predict（tests/test_laya_backend.py:17-30）或在既有参数化上加用例，不要另起夹具文件；改了 laya_backend 的导入或时间调用方式，先回跑 89-94 与 184-187 两组敏感测试。测试名即规格——"does_not_cache_late_results"、"never_predicts" 源自被测代码注释语义，可反查设计意图。macos 注意：114-119 伪造 platform 测的是 local_device 的 darwin 降 CPU 策略（memory/local_device.py:9-14，防 Metal 命令缓冲 abort）。
