# Perfetto UI 教程（5 分钟入门）

> 适用：本项目 `scripts/run-perfetto.sh` 采出的 trace
> 浏览器：Chrome / Firefox（推荐 Chrome，性能更好）

---

## 0. 数据流（先理解再操作）

```
perf record -F 999 -g -- ./bench_gemm
        │ 每秒采 999 次 PC + 调用栈
        ▼
perf.data (≈185 MB)
        │ trace_processor_shell 加载到内存
        ▼
内存 SQL 数据库（perf_sample / slice / cpu_counter_track 等表）
        │ RPC over HTTP
        ▼
浏览器 ui.perfetto.dev
```

→ trace_processor 是个**内存 SQLite**，UI 所有视图都是 SQL 查询。

---

## 1. 连接（30 秒）

```bash
./scripts/run-perfetto.sh ./bin/bench_gemm
# 看到提示后：
```

1. 浏览器开 `https://ui.perfetto.dev`
2. 左侧菜单 → **"Open trace from local trace_processor"**
3. 输入 `http://localhost:9001` → Connect

> Chrome 第一次会拦 mixed content → 见 `INSTALL.md` §3

---

## 2. 四大区域（按从上到下）

```
┌────────────────────────────────────────────────────────────────┐
│ ① 顶部时间轴 + Overview（缩略图）                              │
│    [████████████████████░░░░░░░░░░]  全程 6.9 秒              │
│    拖选其中一段 → ② ③ ④ 同步缩放                              │
├────────────────────────────────────────────────────────────────┤
│ ② 左侧栏 Tracks（轨道）                                       │
│    ▾ CPU 0..7   每个核在跑什么                                │
│    ▾ 进程组      bench_gemm_dbg + 系统                        │
│    ▾ Counter     cycles / instructions / cache-miss 曲线      │
├────────────────────────────────────────────────────────────────┤
│ ③ 中间时间轴                                                  │
│    每个 slice = 一次函数调用 / 调度                           │
│    点击 slice → 右下 ④ 显示详情                              │
├────────────────────────────────────────────────────────────────┤
│ ④ 右下 Selection Details + 标签页                            │
│    - Details: 元信息（duration, cpu, pid, tid）              │
│    - Flamegraph: 火焰图（最常用）                             │
│    - Query: 自己写 SQL                                       │
│    - Threads: 线程状态分布                                   │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. 五个必备操作

| # | 操作 | 作用 |
|---|---|---|
| 1 | 顶部拖选时间范围 | 缩放到该区间 |
| 2 | 左栏搜索框输入 `bench_gemm` | 过滤掉无关进程 |
| 3 | `W/S` 键 | 缩放（W 放大、S 缩小）|
| 4 | `A/D` 键 | 左右移动时间窗 |
| 5 | 右上 "Profile / Flamegraph" 标签 | 看选中范围火焰图 |

---

## 4. 第一次看 bench_gemm trace 的标准流程

### 4.1 找 bench_gemm 时间段

- 顶部 Overview 图里 CPU 占用很高的区间（约 6.9 秒）
- 鼠标拖选 → 自动缩放

### 4.2 过滤无关进程

- 左栏搜索框输入 `bench_gemm_dbg`
- 这时 **unknown 全部消失**（opencode、Xorg 等被过滤）

> **unknown 来源**：opencode.exe（无符号）、GPU 驱动 jmgpu（无 kallsyms）、libc（无 libc6-dbg）
> 都跟 bench_gemm 无关，过滤掉即可。

### 4.3 看火焰图

右上角 **"Profile"** 标签：

```
main ────────────────────────────────────────
 ├ run_gemm_suite
 │   ├ gemm_f32           ████████████  (31.7%)  ← 最热
 │   ├ gemm_s8_sdot_dual  ██            ( 3.3%)
 │   ├ gemm_s8_sdot       ██            ( 2.9%)
 │   └ gemm_f16           ██            ( 2.2%)
 └ io / fill_random ...
```

点最长的柱子（`gemm_f32`）→ 看源码行号 + 占比。

### 4.4 看 Counter 趋势

左栏滚到 "CPU Counter Track" 区，看 `cycles` / `instructions` 曲线。
找 IPC（instructions/cycles）低的区段 → 那就是瓶颈所在。

### 4.5 用 SQL 精确提问

右上 "Query" 标签：

```sql
-- Q1: bench_gemm 里 top 10 函数占比
SELECT name, COUNT(*) AS samples,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM perf_sample
                                  WHERE tid IN (SELECT tid FROM thread
                                                 WHERE name LIKE '%bench_gemm%')), 1) AS pct
FROM perf_sample
GROUP BY name
ORDER BY samples DESC
LIMIT 10;
```

```sql
-- Q2: 哪个 CPU 跑得最久
SELECT cpu, COUNT(*) AS samples, MIN(ts) AS start_ts, MAX(ts) AS end_ts
FROM perf_sample
GROUP BY cpu
ORDER BY samples DESC;
```

```sql
-- Q3: 看每个 PMU 计数器在 gemm_f32 期间的平均值
SELECT name, AVG(value) AS avg_value
FROM counter c
JOIN cpu_counter_track t ON c.track_id = t.id
WHERE c.ts BETWEEN <start> AND <end>
GROUP BY name;
```

---

## 5. 常见问题

| 现象 | 原因 | 解决 |
|---|---|---|
| 整张图全是 `[unknown]` | perf record 没用 `-g` 编译的 binary | `./scripts/build.sh` 重编 |
| 顶部看不到 CPU 轨道 | trace_config 没采 system_info | 用 `scripts/run-perfetto.sh` 默认配置 |
| 火焰图太浅 | 采样率太低 | `perf record -F 4999` 提高 |
| 浏览器卡死 | trace > 500 MB | 分段 perf record，或加 `--filter` |
| SQL 查询超时 | 表太大 | 加 `WHERE ts BETWEEN ... AND ...` 限范围 |

---

## 6. 进阶：trace_processor_shell 命令行

不开 UI 也能查询：

```bash
# 一次 SQL 查询
trace_processor_shell query perfetto-traces/bench_gemm.perf.data \
    "SELECT name, COUNT(*) FROM perf_sample GROUP BY name ORDER BY 2 DESC LIMIT 10"

# 看摘要指标
trace_processor_shell summarize --metrics-v2 all \
    perfetto-traces/bench_gemm.perf.data

# 转 JSON 给其他工具
trace_processor_shell convert json \
    perfetto-traces/bench_gemm.perf.data out.json
```

---

## 7. 批判性：Perfetto 在这台机器的局限

| 局限 | 影响 |
|---|---|
| 麒麟关 ftrace | 没有调度时序、syscall trace → 用 PMU + 火焰图凑合 |
| 999Hz 采样 | < 1ms 的函数可能漏 → 提高到 4999Hz 或加 `-c 1000000` 周期模式 |
| Chrome 内存吃 2GB+ | 185MB trace 浏览器吃满 → 分段采 |
| 学习曲线陡 | UI + SQL 都要会 → 模仿本文件示例起步 |
