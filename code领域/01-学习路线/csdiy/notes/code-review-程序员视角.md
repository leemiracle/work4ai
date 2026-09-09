# 代码评审 + 性能调优 实战手册 · 上：代码评审

> 不是"什么是好代码"的理论课，而是"评审时眼睛该往哪看、看到什么就拦"。
> 每条都给【坏代码块】→【为什么坑】→【改后代码块】，代码来自本仓库真实作业实现（`PKUFlyingPig/CMU10-714`、`PKUFlyingPig/MIT6.S081`、`PKUFlyingPig/MIT6.824`）。
> 配套下篇 `perf-程序员视角-定位与优化.md`。与 `csapp-程序员视角.md` 互补：那边讲"按层下钻找根因"，这边讲"评审时第一眼抓坏味道"。

---

## 0. 评审的心态：找坑，不是找茬

评审只有一个目标：**在代码合并前，把会在 3 点钟咬你的坑提前挖出来**。所以顺序是：

1. **会不会炸**（崩溃/数据错/安全）——必拦；
2. **会不会难维护**（命名/边界/可读）——必提；
3. **会不会慢**（性能）——指出来，但除非是明显反模式，否则别要求当场优化（见下篇"反模式"）。

下面按"看完先抓什么"组织：命名 → 边界 → 错误处理 → 并发 → 资源 → 安全 → 可读。

---

## 1. 命名（Naming）

### 1.1 单字母 / 缩写到看不懂

【坏】来源 `simple_ml.py` 训练循环里的局部变量：
```python
for i in range(iterations):
    x = X[i * batch : (i+1) * batch, :]
    yy = y[i * batch : (i+1) * batch]
    Z = np.exp(x @ theta)
```
【为什么坑】`x` 和大写 `X` 只差大小写，IDE 报错时极易看错；`yy` 不知道是"标签切片"还是"预测值"。三个月后你自己都认不出来。
【改后】
```python
for start in range(0, len(y), batch):
    X_batch = X[start : start + batch, :]
    y_batch = y[start : start + batch]
    logits = X_batch @ theta
    probs   = softmax(logits)        # 把 exp+归一化抽成命名函数
```
> 规则：循环变量 `i/j/k` 可以，但**承载业务含义的变量必须有意义**。`X_batch`、`logits`、`probs` 一眼懂。

### 1.2 魔法数字

【坏】
```c
if (nproc > 64) retry(3);
buf = malloc(4096);
```
【为什么坑】64 是什么？并发上限？3 次重试为什么是 3？4096 是页大小还是缓冲经验值？改的时候不知道该不该动它。
【改后】
```c
enum { MAX_CONCURRENT_PROC = 64, RESEND_MAX = 3 };
if (nproc > MAX_CONCURRENT_PROC) retry(RESEND_MAX);
buf = malloc(SYSTEM_PAGE_SIZE);   // 或 #define RECV_BUF_BYTES 4096
```
> 规则：**除了 0/1 和明显的循环步进，所有字面量都要有名字**。评审看到裸 `4096`、`0.1`、`100` 直接打回。

---

## 2. 边界（Boundary / Off-by-one）

### 2.1 最后一个 batch 大小不匹配 ★真实坑

【坏】直接抄自 `simple_ml.py` 的 `softmax_regression_epoch` / `nn_epoch`：
```python
iterations = (y.size + batch - 1) // batch      # 向上取整，会有不满 batch 的尾批
for i in range(iterations):
    x  = X[i * batch : (i+1) * batch, :]
    yy = y[i * batch : (i+1) * batch]
    ...
    Y = np.zeros((batch, y.max() + 1))          # ← 永远按 batch 开
    Y[np.arange(batch), yy] = 1                  # ← 尾批 yy 比 batch 短，且 arange(batch) 越界
```
【为什么坑】当 `y.size % batch != 0` 时，最后一批 `yy` 长度小于 `batch`。`np.zeros((batch,...))` 配 `np.arange(batch)` 和短了的 `yy` 做花式索引，要么静默错位，要么抛 `IndexError`。MNIST 60000 % 100 == 0 时不爆，换个数据集就炸——典型的"测试用例遮住的 bug"。
【改后】
```python
for start in range(0, len(y), batch):
    X_batch = X[start : start + batch, :]
    y_batch = y[start : start + batch]
    n       = len(y_batch)                       # 用实际批量大小
    Y       = np.zeros((n, num_classes), dtype=X.dtype)
    Y[np.arange(n), y_batch] = 1
```
> 规则：**凡是切片，长度一律用 `len(切片)` 或 `end-start`，别假设它等于 step**。评审时盯着 `for ... batch` 循环，问一句"最后一批多大？"

### 2.2 `size_t` 反向循环死循环

【坏】
```c
for (size_t i = len - 1; i >= 0; i--) {   // len 是 size_t
    buf[i] = 0;
}
```
【为什么坑】`size_t` 无符号，`i >= 0` 恒真；`i--` 到 0 再减 1 变成 `SIZE_MAX`，死循环 + 越界写。
【改后】
```c
for (size_t i = len; i-- > 0; ) {          // 经典写法：先判 i>0 再减
    buf[i] = 0;
}
// 或直接用有符号
for (ptrdiff_t i = (ptrdiff_t)len - 1; i >= 0; i--) buf[i] = 0;
```
> 规则：**有符号/无符号混用是 C 评审的第一红线**。开 `-Wsign-compare -Wconversion`，看到 `size_t` 做 `>= 0` 比较直接拦。

### 2.3 缓冲区差一个字节

【坏】
```c
char buf[16];
snprintf(buf, sizeof(buf)+1, "%s-%d", name, id);   // 想多写一个？越界
strcpy(buf, user_input);                            // 没长度限制
```
【为什么坑】`sizeof(buf)+1` 是评审常被"善意改动"引入的越界；`strcpy` 完全不看长度。两者都是堆栈破坏的常客。
【改后】
```c
char buf[16];
int n = snprintf(buf, sizeof(buf), "%s-%d", name, id);   // 永远 sizeof(buf)
if (n < 0 || (size_t)n >= sizeof(buf)) { /* 截断或报错 */ }
// 拷贝外部数据一律带长度
strncpy(dst, user_input, dst_size - 1); dst[dst_size - 1] = '\0';
```
> 规则：**评审里见到裸 `strcpy/sprintf/gets` 一律拦截**，必须 `sn/strncpy` 并检查返回值。

---

## 3. 错误处理（Error Handling）

### 3.1 裸 `except` 吞掉一切 ★真实坑

【坏】`simple_ml.py` 文件头：
```python
try:
    from simple_ml_ext import *
except:
    pass
```
【为什么坑】裸 `except:` 连 `KeyboardInterrupt`、`SystemExit`、`MemoryError` 都吞。C 扩展导入失败的原因可能是 ABI 不匹配、缺符号、段错误——全被静默。线上你以为用了快路径（C 扩展），其实一直在跑慢的 Python 回退，性能差 10 倍还不知道。
【改后】
```python
try:
    from simple_ml_ext import *
    _HAS_CPP_BACKEND = True
except ImportError as e:
    import warnings
    warnings.warn(f"C 扩展不可用，回退到纯 Python: {e}")
    _HAS_CPP_BACKEND = False
```
> 规则：**`except:` 永远要带异常类型，且至少记录日志**。评审看到裸 `except: pass`、`except Exception: continue` 直接打回。

### 3.2 忽略 `read/write` 的短读写

【坏】
```c
// "反正我请求了 n 字节"
if (write(fd, buf, n) != n) { perror("write"); return -1; }
```
【为什么坑】`write` 合法地可以只写一部分（管道、网络、信号打断）。把它当失败处理，结果是大文件偶发截断、网络偶发丢字节——很难复现。
【改后】
```c
ssize_t writen(int fd, const void *buf, size_t n) {
    size_t off = 0;
    while (off < n) {
        ssize_t w = write(fd, (const char*)buf + off, n - off);
        if (w < 0) { if (errno == EINTR) continue; return -1; }
        if (w == 0) break;
        off += (size_t)w;
    }
    return (ssize_t)off;
}
```
> 规则：**任何 `read/write/send/recv` 都要在循环里凑齐**，并处理 `EINTR`。这是 CSAPP Ch10 的铁律，评审里见到"假设一次成功"就拦。

### 3.3 错误路径上忘了释放资源（内存/锁/fd）

【坏】仿 `proc.c` 的 `allocproc` 风格，错误分支没回滚：
```c
struct frame *f = malloc(sizeof(*f));
struct page  *pg = malloc(sizeof(*pg));
if (!pg) {
    return NULL;            // ← f 泄漏了
}
```
【为什么坑】早期分配成功、后期失败时，前面的资源没人收。长期跑的服务就这么一点点把内存/fd 漏光。
【改后】两种风格任选其一：
```c
// 风格 A：goto 集中清理（Linux 内核主流写法）
struct frame *f = NULL; struct page *pg = NULL;
f = malloc(sizeof(*f));  if (!f) goto fail;
pg = malloc(sizeof(*pg)); if (!pg) goto fail;
return ok;
fail:
    free(pg); free(f); return NULL;

// 风格 B：用 cleanup 属性自动释放（GCC/Clang）
```
> 规则：**评审每个 `malloc/open`，沿所有 `return/goto/break` 走一遍"它被释放了吗"**。多出口函数优先用 `goto fail` 集中清理。

---

## 4. 并发（Concurrency）

### 4.1 信号处理函数里调了非异步信号安全函数

【坏】
```c
void sigchld_handler(int sig) {
    printf("child %d exited\n", waitpid(-1, NULL, WNOHANG));  // ← printf 持 malloc 锁
}
```
【为什么坑】`printf` 内部调 `malloc`。如果信号打断了正在 `malloc` 的主线程（它正持有堆锁），死锁。表现：服务跑半天假死，`gdb attach` 全卡在 `__lll_lock_wait`。
【改后】
```c
volatile sig_atomic_t child_exited = 0;
void sigchld_handler(int sig) {
    int saved = errno;
    child_exited = 1;                 // 只置标志
    errno = saved;
}
// 主循环里收割
while (child_exited) {
    pid_t pid = waitpid(-1, NULL, WNOHANG);
    if (pid <= 0) { child_exited = 0; break; }
    printf("child %d exited\n", pid); // 这里 printf 才安全
}
```
> 规则：**信号处理函数只允许：写 `volatile sig_atomic_t`、调 `write(2)`、调 `waitpid` 等 man 7 signal-safety 里列出的函数**。评审里见到 `printf/malloc/fopen` 一律拦。

### 4.2 读-改-写没加锁（TOCTOU）

【坏】
```c
if (nextpid == MAX_PID) nextpid = 1;   // 多线程/多核下两个都读到 5
else nextpid++;                         // 都 +1 → 两个进程拿到同一个 pid
```
【为什么坑】"先读后写"中间有窗口，并发下会丢更新、发重复 id。xv6 的 `allocpid` 正确做法是用一把自旋锁包住（见 `proc.c`）。
【改后】
```c
int allocpid(void) {
    acquire(&pid_lock);
    int pid = nextpid;
    nextpid = (nextpid == MAX_PID) ? 1 : nextpid + 1;
    release(&pid_lock);
    return pid;
}
```
> 规则：**任何"读出来、判断、写回"的序列都是临界区**。评审里见到 `x++; if (x>y) ...` 这种跨多语句的状态修改，问"这里有锁吗"。

### 4.3 锁粒度过大 / False Sharing

【坏】所有线程计数器挤一个 cache line：
```c
struct { long a, b, c; } counters[8];   // 8 个 long 一行 64B，全挤一起
// 线程 0 疯狂改 counters[0].a，线程 1 改 counters[1].b —— 同一行，互相 invalidate
```
【为什么坑】逻辑上没共享，物理上共享了一行 cache。多核反而比单核慢。
【改后】
```c
struct alignas(64) Counter { long a, b, c; };   // 每个计数器独占一行
struct Counter counters[8];
// 或更细：按 key 分片多把锁，减少争用
```
> 规则：**评审多线程代码，问两件事：(1) 临界区是否最小；(2) 热点计数器是否对齐 cache line**。详见下篇 case 3。

---

## 5. 资源（Resource：fd / 内存 / 句柄）

### 5.1 fd 泄漏：错误路径没 close

【坏】
```c
int fd = open(path, O_RDONLY);
if (fd < 0) return -1;
if (read_header(fd) < 0) return -1;    // ← fd 泄漏
do_work(fd);
close(fd);
```
【为什么坑】长跑服务漏 fd，迟早 `EMFILE: too many open files`，然后连日志都写不进去。
【改后】
```c
int fd = open(path, O_RDONLY);
if (fd < 0) return -1;
if (read_header(fd) < 0) { close(fd); return -1; }
int rc = do_work(fd);
close(fd);
return rc;
```
> 规则：**每个 `open` 立刻在脑里挂一个"必须 close"的钩子**，沿所有退出路径走一遍。评审用 `ls -l /proc/<pid>/fd | wc -l` 实测（见下篇工具）。

### 5.2 Python 里开了没关（缺 context manager）

【坏】
```python
f = open("data.bin", "rb")
data = f.read()
# 忘了 f.close()；异常路径下更糟
return parse(data)
```
【改后】
```python
with open("data.bin", "rb") as f:        # 退出 with 块自动 close，异常也安全
    data = f.read()
return parse(data)
```
> 规则：**`open/socket/lock/connect` 一律用 `with`**。评审里见到裸 `open` + 手动 `close` 就建议改成 context manager。

---

## 6. 安全（Security）

### 6.1 格式串漏洞

【坏】
```c
syslog(LOG_INFO, user_msg);        // 用户数据当 format
printf(buf);                        // 同上
```
【为什么坑】用户消息里有 `%s%s%s%s%n`，`printf` 会去栈上读"参数"，读到非法地址段错误，或用 `%n` 往内存写值。这是真实可利用漏洞，不是理论。
【改后】
```c
syslog(LOG_INFO, "%s", user_msg);
printf("%s", buf);
```
> 规则：**`printf/fprintf/syslog/snprintf` 的第二个参数（format）必须是字面量或受信常量，永远不要传外部数据**。评审见到 `printf(变量)` 一票否决。

### 6.2 整数溢出导致的小缓冲区

【坏】
```c
size_t n = count * elem_size;        // count 来自网络，可能巨大
char *buf = malloc(n);               // 32-bit 下 4G * 4 溢出成 0，malloc(0) 成功
memcpy(buf, src, count * elem_size); // 然后这里越界写几 GB
```
【为什么坑】这是 Heartbleed / 一堆 CVE 的根因。`-O2` 下 `if (a*b < a)` 还会被编译器优化掉（UB）。
【改后】
```c
size_t n;
if (__builtin_mul_overflow(count, elem_size, &n)) { errno = ENOMEM; return NULL; }
char *buf = malloc(n);
if (!buf) return NULL;
memcpy(buf, src, n);
```
> 规则：**任何"外部输入 × 常量"做大小，必须用溢出检查内建**。评审里见到 `malloc(a*b)` 而 `a/b` 来自外部，必拦。

---

## 7. 可读（Readability）

### 7.1 深层嵌套 → 早返回

【坏】
```python
def process(req):
    if req is not None:
        if req.is_valid():
            user = load(req.uid)
            if user is not None:
                if user.active:
                    return do_work(user)
                else:
                    return Err("inactive")
            return Err("no user")
        return Err("invalid")
    return Err("nil")
```
【为什么坑】业务逻辑缩在最里层，读的人要数 5 层括号。错误处理和正常流程混在一起。
【改后】
```python
def process(req):
    if req is None:           return Err("nil")
    if not req.is_valid():    return Err("invalid")
    user = load(req.uid)
    if user is None:          return Err("no user")
    if not user.active:       return Err("inactive")
    return do_work(user)      # 主流程在最外层，一眼到底
```
> 规则：**守卫语句（guard clause）压平嵌套**。评审看到缩进超过 4 层，建议重构成早返回或抽函数。

### 7.2 布尔参数没名字 → 调用点看不懂

【坏】
```python
train(X, y, 0.1, 100, True, False)   # True 是什么？shuffle？verbose？cuda？
```
【改后】
```python
train(X, y, lr=0.1, batch=100, shuffle=True, verbose=False)
# 或用 enum / dataclass，避免顺序错位
```
> 规则：**两个以上同类型位置参数，或任何布尔参数，强制用关键字传参**。

---

## 8. 5 分钟评审 Checklist

打印贴墙上，按顺序过一遍。前 3 条是"必拦"，后 4 条是"必提"。

### 🟥 必拦（合并阻断，P0）

- [ ] **边界**：所有切片/循环的长度是否假设了"正好等于"？最后一个 batch / 最后一个元素？
- [ ] **错误处理**：有没有裸 `except` / 忽略 `read/write` 返回值 / 错误路径漏 `free/close`？
- [ ] **安全**：有没有 `printf(变量)` / `strcpy` / `malloc(a*b)` 无溢出检查？
- [ ] **并发**：临界区内的读-改-写有没有锁？信号处理函数里有没有调不安全函数？

### 🟧 必提（要求改但不阻断，P1）

- [ ] **命名**：业务变量有没有意义？魔法数字有没有名字？
- [ ] **资源**：`open/malloc` 沿所有退出路径都释放了吗？Python 用了 `with` 吗？

### 🟨 可提（建议，P2）

- [ ] **可读**：嵌套是否过深？布尔参数是否用了关键字？
- [ ] **性能**：有没有明显反模式（循环里 malloc、列遍历、`+` 拼 list）？→ 引到下篇量化。

---

## 9. 严重度标注法：红黄绿（R/Y/G）

评审意见末尾打一个标签，让作者一眼知道轻重缓急。**别把缩进问题和段错误问题标成同一颜色**——那是评审最大的失败。

| 标签 | 颜色 | 含义 | 处理 | 示例 |
|------|------|------|------|------|
| `🟥 P0` | 红 | **会炸**：崩溃、数据错、安全漏洞、死锁、泄漏 | 阻断合并，必须改 | `printf(user_msg)`、短读写、整数溢出、裸 except |
| `🟧 P1` | 橙 | **会埋雷**：边界/错误处理/命名，现在不炸以后炸 | 要求改，可同 PR 改完再合 | 最后 batch 大小、魔法数字、错误路径漏 free |
| `🟨 P2` | 黄 | **会累**：可读性、重复代码、轻微性能 | 建议，作者可拒并说明 | 嵌套过深、布尔位置参数 |
| `🟩 NIT` | 绿 | **吹毛求疵**：空格、注释措辞、变量名偏好 | 可提可不提，绝不纠缠 | `i++` vs `++i`、单引号双引号 |

**评审话术模板**（每条意见都这么写，避免情绪化）：
```
🟥 P0 | src/io.c:42
问题：write 返回值只判了 !=n，没处理短写。
为什么坑：大文件偶发尾部截断（CSAPP Ch10）。
建议：套 writen 循环重试，处理 EINTR。
```
三段式：**问题 → 为什么坑 → 怎么改**。对事不对人，永远给可执行的修改方向。

---

## 10. 把评审变成知识沉淀

每次评审拦下的 `🟥/🟧`，值得记一条到团队的"坑表"里。一年后这份表就是新人 onboarding 的最佳教材——比任何编码规范都真实，因为每一条都来自一个差点上线的 bug。

代码评审的本质不是"挑错"，而是**用一双额外的眼睛，把作者在 3 点钟看不见的坑提前看见**。评审做得好的团队，线上事故频率断崖式下降——不是因为人变聪明了，而是因为坑被拦截在了合并之前。

> 下一篇 `perf-程序员视角-定位与优化.md`：当代码"能跑但慢"，怎么先量后改。

---

## 🎤 费曼挑战（真懂了吗？）

> 费曼法：能讲给小学生听才算真懂。用 `python3 tools/feynman.py` 记录。

### 挑战 1：裸 except 吞一切（对应 §3.1）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 为什么 `except: pass` 是最危险的代码？ | 吞掉所有错误=隐形 bug |
| L2 联系 | 你的代码里有几处裸 except？ | `grep -rn "except:" .` |
| L3 创造 | 写一个"错误处理决策树"：什么时候重试/退出/上报 | 分类处理 |
| L4 教学 | 向新人解释"静默失败比崩溃更可怕" |

### 挑战 2：资源泄漏（对应 §5）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 为什么错误路径容易泄漏资源？ | 忘了 close/free |
| L2 联系 | 你的代码有 fd 泄漏吗？ | `ls /proc/pid/fd | wc -l` |
| L3 创造 | 写一个绝不会泄漏的函数（用 context manager/RAII） | defer close |
| L4 教学 | 解释 RAII/context manager 如何消灭资源泄漏 |

### 挑战 3：TOCTOU 竞态（对应 §4.2）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | TOCTOU 是什么？为什么危险？ | 检查和使用之间状态变了 |
| L2 联系 | 你代码里有 TOCTOU 吗？ | `if exists() then create()` 模式 |
| L3 创造 | 写一个线程安全的"检查-执行"原子操作 | 用锁或 CAS |
| L4 教学 | 用"看天气预报和出门"比喻解释 TOCTOU | 看的时候晴天，出门时下雨 |
