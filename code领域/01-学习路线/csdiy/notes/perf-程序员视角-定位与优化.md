# 代码评审 + 性能调优 实战手册 · 下：性能定位与优化

> 不是"如何写快代码"的理论，而是"代码能跑但慢，怎么先量后改"的工程纪律。
> 每个案例都给【before】→【怎么发现的（命令）】→【after】→【提升量】，命令真实可跑。
> 配套上篇 `code-review-程序员视角.md`，与 `csapp-程序员视角.md` 互补：那边讲"为什么慢"的硬件原理，这边讲"怎么测、怎么改、改完快多少"。

---

## 0. 第一性原则：先量后改

性能优化 90% 的失败，都败在"凭感觉改"。改了一周，一测没快，甚至更慢——因为你改的不是热点。**铁律只有一条：**

> **没有测量，就没有优化。**

正确顺序永远是 **top-down 三层下钻**：

```
第 1 层  火焰图 / perf report   →  时间花在哪个函数？
第 2 层  热点函数内             →  花在函数里哪一段循环？
第 3 层  行级 / 指令级          →  cache miss？分支预测？还是真的在算？
```

每一层都先量化，确认"这就是瓶颈"，再动手改。改完**再测一次**，证明它确实快了，否则回滚。**没有 before/after 数字的优化，等于没做。**

### 0.1 一个真实节奏：30 分钟优化循环

```
1. perf record -g ./prog            # 1 min：采集
2. perf report / flamegraph          # 5 min：定位热点（找最宽的那块）
3. 针对热点读代码，提一个假设        # 5 min："这里应该是 cache miss"
4. 验证假设（perf stat -e cache-misses）# 2 min
5. 改代码                            # 10 min
6. 再测，对比数字                    # 5 min
7. 快了？合并。没快？回滚，回第 2 步  # 2 min
```

每一轮只动**一个变量**。一次改三处，最后不知道是哪处起的作用——这是新人最常见的优化错误。

---

## 1. 工具箱：每个工具抓哪一层

不是工具越多越好，而是"哪一层用哪个工具"要清楚。

### 1.1 先看总时间：`time`

```bash
/usr/bin/time -v ./a.out        # -v 给出 wall/user/sys、page fault、voluntary ctx switch
# 看三点：
#   (1) User time vs Sys time —— sys 高说明在内核里耗（syscall 太多）
#   (2) Major page faults —— 高说明在颠簸/读盘
#   (3) Wall vs User+Sys —— wall 远大说明在等 I/O 或被挂起
```
> 第一眼工具。先判断"慢在用户态、内核态、还是等 I/O"，再选下面的工具。

### 1.2 用户态热点：`perf`

```bash
# (a) 全景统计：IPC、cache、分支
perf stat -e cycles,instructions,cache-misses,cache-references,branches,branch-misses ./a.out
#   IPC = instructions/cycles：>1 说明 CPU 喂得饱；<1 说明在等待（cache/分支/依赖链）
#   cache-miss% > 10%  →  cache 问题（case 2）
#   branch-miss% > 5%  →  分支问题（case 4）

# (b) 函数级热点（采样子集，低开销）
perf record -F 99 -g --call-graph dwarf ./a.out
perf report --sort overthead,symbol            # 交互式，按耗时排序
# 或导出文本：
perf report --stdio | head -40

# (c) 反复跑的服务，挂上去采
perf record -p <pid> -- sleep 30
```

### 1.3 可视化：火焰图（FlameGraph）

`perf report` 是文本，火焰图是"一眼看穿"。
```bash
# 一次性安装
git clone https://github.com/brendangregg/FlameGraph.git

perf record -F 99 -g ./a.out
perf script > out.perf
FlameGraph/stackcollapse-perf.pl out.perf > out.folded
FlameGraph/flamegraph.pl out.folded > flame.svg
# 浏览器打开 flame.svg：横宽 = 时间占比，找最宽的那块就是热点
```
> 火焰图的价值：**5 秒内看到时间花在哪**，不用翻几十屏的 perf report。看不懂火焰图，等于不会做性能调优。

### 1.4 行级：`perf annotate` / `valgrind --tool=callgrind`

```bash
# perf 行级（需要 -g + 调试符号 -g）
perf record -g ./a.out
perf annotate main_loop    # 在 perf report 里按 'a' 也行，看到每行汇编/源码的占比

# callgrind：精确指令级，慢 20-50 倍但无采样噪声
valgrind --tool=callgrind --cache-sim=yes ./a.out
callgrind_annotate callgrind.out.* --auto=yes   # 给出每个函数的指令数 + cache 行为
kcachegrind callgrind.out.*                      # GUI 版，可点进去看每行
```

### 1.5 Python 热点：`cProfile` + `line_profiler`

```bash
# 函数级
python -m cProfile -o prog.prof train.py
python -m pstats prog.prof        # 交互：sort cumulative / stats 20
snakeviz prog.prof                # 可视化（火焰图风格）

# 行级：先 cProfile 找到热点函数，再用 line_profiler 逐行计时
pip install line_profiler
# 在代码里给热点函数加 @profile，然后：
kernprof -l -v train.py           # 输出每行耗时 + 占比
```
> Python 优化的第一步永远是：**把循环里的热点换成 numpy 向量化**。cProfile 找到那个函数，line_profiler 找到那一行，然后看它能不能整段交给 numpy。

### 1.6 系统调用开销：`strace -c`

```bash
strace -c ./a.out                 # 汇总每种 syscall 的次数 + 总耗时
# 看到某 syscall 调了上百万次？那就是 case 6（I/O 合并）的信号
strace -c -e trace=read,write,openat ./a.out   # 只看 I/O 类
```

### 1.7 系统/IO 瓶颈：`iostat` / `vmstat`

```bash
iostat -xz 1                      # 每秒一次磁盘：await 高=磁盘慢，%util 100%=打满
vmstat 1                          # r 列（可运行进程）> CPU 核数=CPU 饱和；si/so>0=在 swap
```

### 工具速查表

| 症状 | 先用 |
|------|------|
| 不知道慢在哪 | `time -v` → `perf stat` → 火焰图 |
| 怀疑某个函数 | `perf record` + `perf report` |
| 想精确到行 | `perf annotate` 或 `callgrind` |
| 怀疑 cache | `perf stat -e cache-misses` / `cachegrind --cache-sim` |
| 怀疑分支 | `perf stat -e branch-misses` |
| 怀疑 Python | `cProfile` → `line_profiler` |
| 怀疑 syscall 太多 | `strace -c` |
| 怀疑磁盘/内存 | `iostat -xz 1` / `vmstat 1` |

---

## 2. 六个真实优化案例

每个案例：before → 怎么发现 → after → 提升量。数字均为典型量级，供校准直觉。

### Case 1：循环里反复分配（list append / np.vstack）★真实

【发现】`cProfile` 显示 `parse_mnist` 占 60% 时间，`np.vstack` 是大头。
【before】来源 `CMU10-714/hw0/simple_ml.py`，逐图读进 list 再堆叠：
```python
X = np.vstack([
    np.array(struct.unpack(f"{tot}B", img_file.read(tot_pixels)), dtype=np.float32)
    for _ in range(img_num)
])
X -= np.min(X); X /= np.max(X)
```
【为什么慢】`np.vstack` 先建一个含 6 万个小数组的 Python list（每图一次 `struct.unpack` + 一次 `np.array` 构造），再整体拷贝成大矩阵。6 万次小分配 + 一次大拷贝，GC 压力爆炸。
【after】一次性 `frombuffer` 读全部，再 reshape：
```python
raw = img_file.read(img_num * tot_pixels)              # 一次 I/O
X = np.frombuffer(raw, dtype=np.uint8).astype(np.float32).reshape(img_num, tot_pixels)
X /= 255.0                                             # 归一化：已知范围 [0,255]，省一次 min/max 全扫
```
【提升】**~30×**（6 万次小分配 → 1 次大分配；归一化从两趟全扫 + min/max 算成单趟除法）。

### Case 2：cache miss —— 列遍历 / 指针追逐

【发现】`perf stat -e cache-misses,cache-references` 显示 `cache-miss%` 高达 40%。
【before】矩阵按列累加（C 行优先存储，列遍历每跳一行 miss 一次）：
```c
for (int j = 0; j < n; j++)
    for (int i = 0; i < n; i++)
        col_sum[j] += A[i][j];          // A[i][j] 与 A[i+1][j] 隔一整行
```
【为什么慢】`A[i][j]` 到 `A[i+1][j]` 跨越 `n*sizeof(double)` 字节，几乎每次访问都 miss。L1 vs 主存差 ~100 倍。
【after】换成行优先遍历，或分块：
```c
// 方案 A：交换循环顺序，让内层连续访问
for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
        col_sum[j] += A[i][j];          // A[i][j]、A[i][j+1] 在同一 cache line

// 方案 B：矩阵乘法用分块（块大小塞进 L1，如 64×64 double）
for (ii=0; ii<n; ii+=B)
  for (jj=0; jj<n; jj+=B)
    for (kk=0; kk<n; kk+=B)
      for (i=ii;i<ii+B;i++) for(j=jj;j<jj+B;j++) for(k=kk;k<kk+B;k++)
        C[i][j] += A[i][k]*B[k][j];
```
【提升】方案 A：**~10×**（列遍历 → 行遍历）；方案 B（矩阵乘分块）：**~3-5×**（朴素 ijk → 分块）。

> 同类陷阱：链表遍历每跳一次 miss 一次（pointer chasing）。热点链表 → 改连续数组。

### Case 3：锁粒度过大 / False Sharing

【发现】8 线程比 1 线程还慢。`perf stat` 看 `cache-misses` 爆表，`perf report` 卡在锁争用。
【before A：全局一把锁】
```c
pthread_mutex_t global_lock;
// 所有线程的计数都抢这一把锁 → 串行化
pthread_mutex_lock(&global_lock);   counter++;   pthread_mutex_unlock(&global_lock);
```
【after A：分片锁（按 hash 分到 N 把）】
```c
#define N_SHARDS 64
pthread_mutex_t locks[N_SHARDS];
long counters[N_SHARDS];
int shard = key % N_SHARDS;
pthread_mutex_lock(&locks[shard]);  counters[shard]++;  pthread_mutex_unlock(&locks[shard]);
```

【before B：False Sharing】
```c
struct { long a, b; } c[8];        // 8 个 long 挤在一两个 cache line
// 线程 i 疯改 c[i].a，互相 invalidate 同一行
```
【after B：对齐到 cache line】
```c
struct alignas(64) Counter { long a, b; };   // 每个独占一行
struct Counter c[8];
```
【提升】分片锁：**接近线性加速**（8 线程 ~7×）；解决 false sharing：**~8×**（从比单核慢 → 接近线性）。

### Case 4：分支预测失败

【发现】`perf stat -e branches,branch-misses` 显示 `branch-miss%` > 20%。
【before】对乱序数组做条件累加，`if` 不可预测：
```c
for (int i = 0; i < n; i++)
    if (a[i] < threshold) sum += b[i];      // 数据随机时预测失败率 ~50%
```
【为什么慢】每次预测失败，流水线冲刷 15-20 周期。1 亿元素 → 几千万次冲刷。
【after】用算术替代分支，编译成 `cmov`：
```c
for (int i = 0; i < n; i++)
    sum += (a[i] < threshold) * b[i];       // 无分支，cmov 或掩码
```
【提升】**~2-4×**（取决于数据随机度）。验证：改完 `branch-miss%` 应掉到 < 2%。

> 经典现象：排序后的数组比乱序数组快 3-5 倍，就是这个原因。看到"排序后变快很多"，立刻想分支预测。

### Case 5：热路径里 malloc/free

【发现】`strace -c` 显示 `brk/mmap` 调用次数巨大；`perf report` 大头是 `malloc`/`free`。
【before】每个请求 new 一个临时对象：
```c
for (int i = 0; i < n; i++) {
    struct Task *t = malloc(sizeof(*t));    // 热循环里 malloc
    process(t);
    free(t);
}
```
【为什么慢】`malloc/free` 走堆分配器，要加锁、维护空闲链表、可能触发系统调用。热路径上每轮一次，开销远超业务计算。
【after】对象池 / arena，复用内存：
```c
struct Task pool[N];                        // 预分配
for (int i = 0; i < n; i++) {
    struct Task *t = &pool[i % N];          // 复用，零分配
    process(t);
}
// 或栈上分配（小对象）：struct Task t; process(&t);
```
【提升】**~5-10×**（取决于分配器竞争程度）。

### Case 6：I/O 没合并（syscall 太多）

【发现】`strace -c` 显示 `write` 被调了几百万次，每次写几字节。
【before】逐行写日志/数据：
```python
for line in records:
    f.write(line + "\n")                    # 每行一次 write（或 stdio 刷得太勤）
```
【为什么慢】每次 `write` 是一次系统调用（用户→内核切换 ~1-2μs），百万次就是秒级开销，纯白费。
【after】批量缓冲后一次写：
```python
import io
buf = io.StringIO()
for line in records:
    buf.write(line); buf.write("\n")
f.write(buf.getvalue())                     # 一次大 write
# 或更省内存：每攒够 64KB flush 一次
```
【提升】**~20-50×**（百万次 syscall → 几千次）。验证：`strace -c` 改后 `write` 计数应骤降。

> 同类：循环里 `read(8)` 逐块读，不如一次 `read` 大块再切片；逐条 SQL insert 不如批量。

---

## 2.7 把六个案例串成一条定位流水线（端到端示例）

一个真实场景：批处理服务，处理 100 万条记录从 10 秒变 90 秒，怎么查。**不要一上来就改代码**，按工具顺序一层层下钻：

```text
① /usr/bin/time -v ./batch
   → User 80s, Sys 5s, Wall 90s          # 慢在用户态，不是 I/O 等待 → 用 perf 不用 iostat

② perf stat -e cycles,instructions,cache-misses,branch-misses ./batch
   → IPC 0.4, cache-miss% 38%            # cache 问题嫌疑最大 → 看 case 2/5

③ perf record -g ./batch && perf report
   → 60% 时间在 process_record()         # 锁定热点函数

④ perf annotate process_record
   → 行 X: 链表 next 解引用 占了 40%      # pointer chasing → case 2 链表陷阱

⑤ 改：链表换成连续数组（struct pool + 索引）
   → 再测 time -v: Wall 14s             # 6.4× 提升，证实假设

⑥ 剩下的 14s 再 perf record → 发现 malloc 残留
   → 改成 arena（case 5）→ Wall 9s       # 又 1.5×
```

要点：**每一步只确认一个假设，每改一处立刻测**。第 ② 步的 `cache-miss% 38%` 已经把范围缩到 case 2/5，不用把六个 case 都试一遍。这就是 top-down 下钻的价值——**用数据淘汰错误假设，而不是穷举**。

如果第 ② 步 `cache-miss%` 很低、`branch-miss%` 也低、但 IPC 还是 0.4？那大概率是**数据依赖链太长**（case 之外的 ILP 问题），用多累加器拆依赖链（见 `csapp-程序员视角.md` Ch5）。工具帮你排除"不是什么"，剩下的就是"是什么"。

---

## 3. 反模式：这些"优化"是陷阱

性能优化里最大的坑，是"看起来在优化、其实在挖坑"。

### 3.1 "不要过早优化"到底指什么

Knuth 那句话被滥用了。它的真正含义是：

| ❌ 过早优化（别做） | ✅ 正确优化（要做） |
|---|---|
| 还没测就在猜"这里可能慢"，花一天手写 SIMD | 先 `perf`，发现热点在别处 |
| 为了省一个比较，把清晰代码改成位运算迷宫 | 热点函数向量化，其余保持可读 |
| 到处加缓存"以防万一" | 缓存加在有测量依据的地方，带淘汰策略 |
| 牺牲正确性换速度（如去掉边界检查） | 正确性永远优先；先对再快 |

> 一句话：**过早优化 = 在没有测量依据的地方花精力**。有数据支撑的优化永远不算早。

### 3.2 这些"优化"其实是负优化

**陷阱 1：手动循环展开。** 现代 CPU + 编译器（`-O3`）自己会展开，你手展开可能让寄存器溢出到栈，反而变慢。除非 `perf` 明确显示这是热点且编译器没展开，否则别动。

**陷阱 2：到处加 `inline`。** `inline` 只是"建议"，编译器比你懂。乱加 `inline` 让二进制变大、icache miss 上升，热路径反而变慢。相信 `-O2/-O3` 的内联决策。

**陷阱 3：无脑上多线程。** 任务小到抵不过线程创建/同步开销时，多线程比单线程慢。先量化任务粒度（任务要 >> 锁/sync 开销）。而且多线程引入的竞态 bug，调试成本远超那点加速。

**陷阱 4：缓存没淘汰策略。** 为了"快"加了个 `dict` 缓存，只进不出。跑几天内存涨爆，被 OOM 杀。**任何缓存必须有上限和淘汰策略（LRU/TTL）**，否则是泄漏。

**陷阱 5：为性能牺牲可读性，但没带来性能。** 把 `for (i=0;i<n;i++) a[i]=b[i]+c[i]` 改成一堆位运算"省一个加法"——编译器早把 `+` 优化成一条 `add` 指令了，你只是让代码不可读。**改完一定测数字，没快就回滚。**

**陷阱 6：优化了不该优化的层。** 业务网络请求 50ms，你花一天把内存拷贝从 0.1ms 优化到 0.05ms。用户毫无感知。**优化要打在最慢的那层**（这里是网络），而不是你最熟的那层。

### 3.3 一条红线

任何优化 PR，必须带三样东西：
1. **before 数字**（用什么命令、跑了多久）；
2. **after 数字**（同样命令、同样机器）；
3. **回滚成本**（改动是否影响可读性/正确性，值不值）。

缺这三样的优化 PR，评审直接打回。**没有数字的优化，不是优化，是玄学。**

---

## 4. 把性能当纪律，而不是天赋

写快代码的人，不是天生会写快代码，而是他们**养成了一套"先量后改"的肌肉记忆**：

1. 写完先跑 `time`，建立基线；
2. 慢了先 `perf`，找最宽的那块火焰；
3. 改一处，测一次，快了才合并；
4. 改不动的（算法已是 `O(n log n)`、cache 已对齐），坦然接受，写进文档。

这套纪律，和上篇的代码评审纪律是一体两面：**评审拦住"会炸的坑"，性能调优挖掉"会慢的根"**。两者合起来，就是一个工程师对代码质量的全部掌控力。

---

## 5. 测量纪律 Checklist

打印贴墙上。每次优化前过一遍，少踩一半坑。

### 动手前（建立基线）

- [ ] **建基线**：`time -v` 跑 3 次取中位数，记下 Wall/User/Sys。没有 before 数字，禁止动手。
- [ ] **关扰动**：关掉其他重进程、关省电（`cpupower frequency-set -g performance`）、固定输入数据，保证可复现。
- [ ] **同一机器**：before 和 after 必须同机、同频、同负载。换机器对比等于没测。

### 定位中（找瓶颈）

- [ ] **先 `perf stat` 全景**：IPC、cache-miss%、branch-miss% 三个数先看，再决定下钻方向。
- [ ] **画火焰图**：`perf record -g` → flame.svg，5 秒看到时间花在哪。
- [ ] **一次一个假设**：别同时猜 cache 和分支。用 `perf stat -e <事件>` 逐个验证，淘汰错的。

### 改完后（证明有效）

- [ ] **再测 3 次取中位数**：和基线对比。提升 < 5% 且代码变复杂 → 回滚，不值。
- [ ] **验证副作用**：跑完整测试套件，确认没改坏正确性（快了但错了，是灾难）。
- [ ] **记 before/after 数字到 PR 描述**：命令 + 数字 + 机器。没数字不合并。

### 永远不做

- [ ] 不在没测量的地方花时间（"过早优化"的全部定义）。
- [ ] 不为微小收益牺牲可读性/正确性。
- [ ] 不优化非热点层（业务网络 50ms 时别去抠 0.05ms 的拷贝）。

> 配套阅读：`csapp-程序员视角.md`（Ch4 流水线/Ch5 优化/Ch6 cache 给你"为什么慢"的硬件底座）、`code-review-程序员视角.md`（合并前拦坑）。

---

## 🎤 费曼挑战（真懂了吗？）

> 费曼法：能讲给小学生听才算真懂。用 `python3 tools/feynman.py` 记录。

### 挑战 1：先量后改（对应 §0）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | "先量后改"为什么是第一原则？ | 不测量=瞎猜 |
| L2 联系 | 你上次优化是凭直觉还是凭数据？ | 有 perf 数据吗？ |
| L3 创造 | 对一段慢代码画火焰图，指出瓶颈 | perf record + flamegraph |
| L4 教学 | 向团队解释"不测量就不优化"的纪律 |

### 挑战 2：cache miss 定位（对应 §2 Case 2）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 为什么顺序遍历比随机访问快？ | cache line 局部性 |
| L2 联系 | 你的代码哪里有 cache miss？ | perf stat -e cache-misses |
| L3 创造 | 写一个 cache 友好的矩阵转置（分块） | CPE 降 50%+ |
| L4 教学 | 解释 false sharing 怎么让多线程变慢 |

### 挑战 3：反模式（对应 §3）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | "不要过早优化"到底指什么？ | 指不要优化非瓶颈 |
| L2 联系 | 你见过哪些"负优化"？ | 提前查表反而慢 |
| L3 创造 | 列出 3 个你代码里的"过早优化" | 逐一评估 ROI |
| L4 教学 | 向新人解释"优化的纪律" | 先量→找瓶颈→改→再量 |
