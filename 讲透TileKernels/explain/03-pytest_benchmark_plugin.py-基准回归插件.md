# tests/pytest_benchmark_plugin.py 精讲

> 原文件：`tests/pytest_benchmark_plugin.py`（477 行）

## ① 角色定位

质量保障体系的**性能侧支柱**：自研 pytest 插件，把内核基准纳入 CI 语义——默认跳过、`--run-benchmark` 显式开启、结果写 JSONL、与基线比对后**回归即 exit 1**——让"慢了 15%"和"算错了"一样是红灯。

## ② 内部结构

文件头注释交代反直觉设计：**故意不叫 `conftest.py`**，由根 `tests/conftest.py` 通过 `pytest_plugins` 加载——直接叫 conftest 会触发 pluggy 重复注册错误。四个板块：

- **CLI 选项**：`--run-benchmark`、`--benchmark-output`、`--benchmark-regression-threshold`（默认 0.15）、`--benchmark-verbose`。
- **`pytest_configure`**：注册 marker；xdist worker 绑卡；会话级结果收集器。
- **回归检测三连**：`_detect_regressions` 按 ratio 分桶 regression/improvement/missing；`pytest_sessionfinish` 有回归或 missing 就把 exitstatus 改 1；`pytest_terminal_summary`（170-317 行）渲染对比表与新基准表，列宽动态计算。
- **两个 fixture**：`benchmark_record` 返回记录函数（打印 + JSONL 追加 + 会话收集三合一）；`benchmark_timer` 包装 `tilelang.profiler.bench.do_bench`，默认 `backend='cupti', warmup=0, rep=30`，返回 ms→µs。

## ③ 外部连接

`tile_kernels.testing.bench.make_param_key` 把参数 dict 排序成稳定 key；CUPTI 后端提供内核级精确时间（区别于含 Python 开销的 torch 事件）。基线文件 `tests/benchmark_baselines.jsonl` 与插件同目录。上游消费方是各测试的 `@pytest.mark.benchmark` 用例。

## ④ 数据流

① `pytest_configure` 时每个 xdist worker 解析 `gw<N>` 编号，`CUDA_VISIBLE_DEVICES = N % num_gpus` 绑卡，再按 `(总显存-10GB)/每卡worker数` 算配额硬限每 worker 显存（67-83 行）——多 worker 共卡不 OOM 的关键；② 未开 `--run-benchmark` 时收集阶段给 benchmark 用例打 skip，开了则与正确性用例混跑，纯跑用 `-m benchmark`；③ 测试体内 `time_us = benchmark_timer(fn)`，再 `benchmark_record(...)`：打印一行人读摘要，有 output 路径则持锁追加 JSON；④ 会话收尾比对基线：`ratio = cur/base`，`>1+thr` 回归（`--`）、`<1-thr` 改进（`++`）、否则 `=`；⑤ 终端汇总表打 Kernel/Latency/Bandwidth/Ratio/Stat，missing 进新基准表；⑥ 回归或 missing 非零退出。

## ⑤ 设计决策

- **基线即版本控制对象**：JSONL 与代码同仓，key 由 kernel/operation/排序参数构成，参数化用例天然多行基线；新 shape 首跑进 missing 表，核对后并入基线提交。
- **阈值双向**：不仅报慢 15%，也报快 15%——异常加速常意味着测错了，显式亮出来防"假绿"。
- **CUPTI + 可覆盖 rep**：CUPTI 报 GPU 侧真实执行；抖动大的内核在用例内多跑取 min，而非动全局阈值。
- **10GB 显存保留 + 钳边界**：给框架/JIT 留 headroom，防御性钳值——被 OOM 教育出来的写法。
- **检测前移到 sessionfinish**：先算好 stash，terminal_summary 只管渲染，顺序无关。

## ⑥ 新人提示

1. 写新基准三步：标记 `@pytest.mark.benchmark`、注入两个 fixture、`params` 传全形状信息——key 稳定才能对上基线。
2. 更新基线正规流程：`--run-benchmark --benchmark-output=new.jsonl`，核对新表后替换基线文件随代码提交。
3. gw 模式下单机 OOM 先想显存配额——每 worker 只分到零头。