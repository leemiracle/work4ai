# 设计模式 — 程序员视角：真实代码里的模式

> 不是 GoF 23 模式的字母表背诵，而是"你今天写的代码里哪里闻着臭，把它替换成什么"。
> 每节四件事：(a) 你遇到的**信号**（坏味道）；(b) 最小 before/after；(c) **何时别用**（过度设计红线，多数文章不敢写）；(d) 在 xv6 / bustub / 标准库里的**真实出处**（带文件路径，可去仓库核对）。
> 真实代码素材：`github-repos/third-party/xv6-riscv-solution/`、`github-repos/third-party/bustub/`、`github-repos/third-party/Linux0.11/`。
> 反主张：**为模式而模式是负债**。下文每个模式都标了"别用"的红线，因为 90% 的烂架构都源于"我学了策略模式，所以我要把每个 if 都抽成策略类"。

---

## 0. 先把脑子里的误区清掉

GoF 的图是 1994 年画给 C++/Smalltalk 的。今天有三件事变了，照搬会害你：

1. **函数是一等公民**了（Python/Go/JS/Rust 闭包）。GoF 里很多"类"（Strategy、Command、State）现在用一个函数 + 一个 `map` 就够了，别为了"符合 UML"硬造 5 个类。
2. **语言内建了大量模式**（迭代器、装饰器、观察器）。Python `@decorator`、Go channel、JS `for...of`、Rust `Iterator` trait 已经是语法糖，你再手撸一遍就是重复造轮子。
3. **"可测试"比"可扩展"重要**。GoF 假设需求会沿某个轴无限扩展；现实是需求沿你没想到的轴变。抽象早了，扩展轴猜错，比不抽象还惨。

判断标准只有一条：**这段代码是不是已经在重复同样的 if/else 结构第三次了？** 是→上模式；不是→别上。

---

## 1. 策略模式 — "一堆 if/else 切换算法"

### 你遇到的信号
一个函数里 `if type == X ... else if type == Y ...` 在**三个方法**里重复出现，每次加新类型（比如新加 socket）都要改三个地方，漏改一个就 panic。

### 最小例子（before → after）
```c
// ---- BEFORE：xv6 file.c 的真实写法（部分），三个操作各 if/else 一遍 ----
int fileread(struct file *f, ...) {
  if (f->type == FD_PIPE)      r = piperead(...);
  else if (f->type == FD_DEVICE) r = devsw[f->major].read(...);
  else if (f->type == FD_INODE)  r = readi(...);
  else if (f->type == FD_SOCK)   r = sock_read(...);   // 加 socket 要改这里
}
// filewrite、fileclose 里又是几乎一样的一串 if/else

// ---- AFTER：把"行为"塞进 struct，用一张表替代 type 判断 ----
struct file_ops {
  int  (*read)(struct file*, uint64, int);
  int  (*write)(struct file*, uint64, int);
  void (*close)(struct file*);
};
struct file {
  enum ftype type;          // 仍保留，调试/反序列化要
  const struct file_ops *ops;  // 关键：行为跟着对象走
  ...
};
int fileread(struct file *f, uint64 a, int n) { return f->ops->read(f, a, n); }
// 加新类型 = 新增一个 file_ops 实例，零改动调用方
```

### 何时别用（红线）
- **只有一处 if/else，且半年没变过** → 别抽。抽了反而多一层间接。
- **分支逻辑差异巨大、没有共同签名** → 强行统一签名会出现一堆"伪参数"（`read` 用得上 `addr`，`close` 用不上却要传），这是坏味道。
- **类型只有 2 个且互斥**（成功/失败、男/女）→ 用 if 就行，别造 `SuccessStrategy`。
- xv6 自己都没把 `fileread` 的四种 type 全抽成策略——因为 `FD_INODE` 分支要 `ilock/readi/iunlock` 三步，塞进函数表反而更绕。**混合（type tag + 函数表）是常态，不是失败。**

### 在真实代码里在哪
- `third-party/xv6-riscv-solution/net/kernel/file.c:109` — `fileread` 按 `f->type` 分派。
- `third-party/xv6-riscv-solution/cow/kernel/file.h:34` — `struct devsw { int (*read)(...); int (*write)(...); }`，**这就是策略表**，控制台和磁盘各注册一份。
- `third-party/bustub/src/include/buffer/replacer.h:22` — `class Replacer { virtual Victim/Pin/Unpin }`，LRU/LRU-K/Clock/ARC 四个策略实现同一接口，buffer pool 不关心用哪个。

---

## 2. 观察者 / 事件 — "状态变了要通知一堆人"

### 你遇到的信号
你有一个核心数据（订单状态、配置、传感器读数），**好几个模块**都要在它变化时做不同的事（发短信、写日志、刷缓存、推 WebSocket）。你不想让核心模块 `import` 短信/日志/缓存模块。

### 最小例子
```python
# ---- BEFORE：核心模块耦合了一堆下游 ----
class Order:
    def pay(self):
        self.status = "PAID"
        sms.send(...)          # 核心 import 了 sms
        db.log(...)            # 核心 import 了 db
        cache.invalidate(...)  # 核心 import 了 cache
        # 下次再加"发优惠券"又要改这里

# ---- AFTER：核心只管"喊一声"，下游自己订阅 ----
class Order:
    def __init__(self): self._listeners = []
    def on_change(self, fn): self._listeners.append(fn)
    def pay(self):
        self.status = "PAID"
        for fn in self._listeners: fn(self)   # 不知道、也不关心谁在听
# 下游各注册各的：
order.on_change(lambda o: sms.send(...))
order.on_change(lambda o: db.log(...))
```

### 何时别用（红线）
- **订阅者只有 1 个** → 直接调函数，别搞"事件总线"。
- **顺序强相关**（B 必须在 A 之后跑，且依赖 A 的结果）→ 观察者天生无序，你会在 debug "为什么有时 A 没跑完 B 就跑了"上浪费一周。这种情况用**责任链**或显式 pipeline。
- **事件会触发新事件、形成链** → 小心风暴。A 监听 B、B 监听 A，死循环烧 CPU。生产事故高发区。
- **跨进程**别手撸观察者，用现成的消息队列（Kafka/Redis pub-sub）。

### 在真实代码里在哪
- `third-party/xv6-riscv-solution/cow/kernel/console.c` — UART 硬件中断 → `consoleintr` → `console` 把字符喂进 line discipline。**中断就是硬件层面的"事件通知"**，CPU 不去轮询键盘，而是被"通知"。
- `third-party/xv6-riscv-solution/cow/kernel/pipe.c` — 管道写端写完 `wakeup(&pi->nread)`，读端在 `sleep(&pi->nread)` 上被唤醒。这是"生产者通知消费者"，观察者 + 阻塞原语的合体。
- 标准库：Python `logging`、Node `EventEmitter`、Vue 的响应式 `watch`、Linux `inotify`、Rust `std::sync::mpsc`。

---

## 3. 装饰器 — "给函数加横切关注点"

### 你遇到的信号
你发现自己在**很多函数的开头/结尾写一样的代码**：打日志、计时、重试、加锁、检查权限。复制粘贴十遍后，改一处漏九处。

### 最小例子
```python
# ---- BEFORE：每个函数手写一遍日志+重试 ----
def call_api_a():
    log.info("call_api_a start")
    for i in range(3):
        try: return http.get("/a")
        except: sleep(i)
    log.info("done")

def call_api_b():
    log.info("call_api_b start")   # 又来一遍
    for i in range(3):
        try: return http.get("/b")
        except: sleep(i)

# ---- AFTER：横切关注点抽成装饰器，业务函数干净 ----
import functools, time, logging
def with_retry_log(fn):
    @functools.wraps(fn)
    def wrap(*a, **kw):
        logging.info("%s start", fn.__name__)
        for i in range(3):
            try: return fn(*a, **kw)
            except Exception: time.sleep(i)
        raise RuntimeError("retry exhausted")
    return wrap

@with_retry_log
def call_api_a(): return http.get("/a")
@with_retry_log
def call_api_b(): return http.get("/b")
```

### 何时别用（红线）
- **装饰器套超过 3 层**（`@cache @retry @auth @log def f`）→ 执行顺序会把你绕晕，出 bug 时栈帧一层套一层。`functools.wraps` 一定要加，否则调试信息和类型签名全丢。
- **业务逻辑混进装饰器** → 装饰器只该放"和具体业务无关"的横切逻辑（日志/计时/重试/锁）。一旦装饰器里出现 `if order.status == ...`，它就该是个普通函数。
- **要装饰的不是函数而是"对象的行为"** → 用代理/包装类，别硬上函数装饰器。
- C 语言没有装饰器语法，但 Linux 内核的 `ftrace`、`kprobe` 本质是"运行时给函数套一层"，思想一样。

### 在真实代码里在哪
- Python 标准库遍地：`@property`、`@staticmethod`、`@functools.lru_cache`、`@contextlib.contextmanager`、`@dataclass`。
- `third-party/bustub` 里 `DISALLOW_COPY_AND_MOVE` 宏——编译期"装饰"掉拷贝构造，C 语言的装饰器。
- Django/Flask 路由 `@app.route`、FastAPI `@app.get`——把"注册到路由表"这个横切动作挂在函数定义上。

---

## 4. 适配器 — "两个接口对不上"

### 你遇到的信号
你拿到一个第三方库/老模块，接口和你新代码期望的**形状不一样**（字段名不同、单位不同、返回值结构不同）。你又不能改它（库是别人维护的/老代码有人依赖）。

### 最小例子
```python
# ---- BEFORE：调用方被迫记住两套接口 ----
# 老库返回：{"user_name": "lwz", "age": 18}
# 新代码期望：User(name="lwz", age=18)
def greet(raw):
    # 调用方满地写适配逻辑，重复
    print("hi", raw["user_name"], raw["age"])

# ---- AFTER：写一层适配器，只脏这一处 ----
class UserAdapter:
    def __init__(self, raw): self.name = raw["user_name"]; self.age = raw["age"]
    def __getattr__(self, k):  # 还能挡掉字段缺失
        raise AttributeError(f"old api has no {k}")
def greet(raw): u = UserAdapter(raw); print("hi", u.name, u.age)
```

### 何时别用（红线）
- **两边接口都是你能改的** → 别写适配器，直接把其中一边改对。适配器是"两套都不能动"时的妥协，不是偷懒工具。
- **适配器里塞了业务逻辑** → 它只该做"翻译"（字段映射、单位换算、协议转换）。一旦出现 `if` 业务判断，它就变成了伪装的 Service，迟早失控。
- **适配器套适配器**（A 适配 B，B 适配 C）→ 接口推演时每一层都吃一次性能损失和心智负担，重构成直接对接。

### 在真实代码里在哪
- `third-party/bustub/src/include/storage/page/page_guard.h:60` — `ReadPageGuard::As<T>()` 把"一段裸 bytes"适配成"类型化的结构体指针"，挡掉了 `reinterpret_cast` 散落各处。
- `third-party/bustub/src/include/execution/executors/abstract_executor.h` — Volcano 模型把"底层是顺序扫描还是索引扫描"的差异**适配**成统一的 `Init()/Next()` 接口，上层算子不关心。
- 标准库：Python `io.BytesIO` 把 `bytes` 适配成"文件"接口；`csv.DictReader` 把行适配成 dict。

---

## 5. 工厂 — "对象创建逻辑会变"

### 你遇到的信号
你 `new` 一个对象时，**具体 new 哪个类要根据运行时条件决定**，而且这个判断在多处重复。或者创建对象要先做一堆准备工作（读配置、连依赖、注册自己），散落在调用方。

### 最小例子
```cpp
// ---- bustub executor_factory.cpp 的真实骨架（简化）----
auto ExecutorFactory::CreateExecutor(ctx, plan) -> AbstractExecutor {
  switch (plan->GetType()) {              // 根据"计划节点类型"造不同算子
    case PlanType::SeqScan:  return SeqScanExecutor(ctx, plan);
    case PlanType::Insert: {
      auto child = CreateExecutor(ctx, plan->GetChildPlan()); // 递归造子算子
      return InsertExecutor(ctx, plan, child);
    }
    case PlanType::HashJoin: {
      auto left  = CreateExecutor(ctx, plan->GetLeftPlan());
      auto right = CreateExecutor(ctx, plan->GetRightPlan());
      return HashJoinExecutor(ctx, plan, left, right);        // 组装整棵树
    }
    ...
  }
}
// 调用方只要：auto exec = ExecutorFactory::Create(ctx, plan);
// 不关心具体是哪种算子、有几个孩子——工厂全包了
```

### 何时别用（红线）
- **类型只有 1 种、且不会变** → 直接构造，`new Foo()` 比全局唯一的 `FooFactory::create()` 清楚一万倍。
- **为了"可测试"而给每个类配工厂** → 用依赖注入（构造函数传参）就够了，别上工厂。工厂的真正价值是"调用方不知道具体类型"，测试场景调用方明明知道。
- **工厂方法爆炸**（`createA/createB/createC...`）→ 退化成了命名空间，直接用静态函数或自由函数。
- **简单工厂 switch 超过 20 个 case 还在涨** → 该考虑注册表（`map<string, creator>`）了，否则每加一类改一次 switch。

### 在真实代码里在哪
- `third-party/bustub/src/execution/executor_factory.cpp:56` — `CreateExecutor`，递归 switch，**根据查询计划树造出对应的算子树**。教科书级工厂方法 + 递归构造。
- `third-party/xv6-riscv-solution/cow/kernel/syscall.c:110` — `syscalls[]` 跳表，按系统调用号"生产"对应的处理函数调用，是工厂的函数表变体。
- Python `datetime.fromisoformat`、`json.loads`、`pickle.loads` —— 字符串/字节流"造"出对象，都是工厂。

---

## 6. 单例 — "全局只要一个"

### 你遇到的信号
有个对象（连接池、配置、日志器、内核的文件表）整个进程**逻辑上只能有一个**，多了会冲突（两个日志器抢一个文件、两个文件表抢同一组 slot）。

### 最小例子
```c
// ---- xv6 的"全局唯一文件表"，本质就是单例 ----
struct {
  struct spinlock lock;
  struct file file[NFILE];   // 全系统就这一张表，所有进程共享
} ftable;                     // 全局变量，编译期就一个实例
void fileinit(void) { initlock(&ftable.lock, "ftable"); }

// Python 的线程安全单例（别用模块级变量偷懒，多线程下首次访问会重复构造）
class Logger:
    _inst = None
    _lock = threading.Lock()
    def __new__(cls):
        with cls._lock:
            if cls._inst is None: cls._inst = super().__new__(cls)
        return cls._inst
```

### 何时别用（红线，这条最重要）
- **"我觉得它应该只有一个"** → 这是过度设计头号元凶。先用普通对象 + 依赖注入传进去；真出问题了（有人 new 了第二个）再上单例。
- **单例持有可变状态、还要写单测** → 测试地狱。单测要并行、要隔离，单例的全局状态让用例之间互相污染。几乎所有"测试跑单测过、一起跑就挂"的诡异 bug 都是全局可变状态。
- **单例依赖了别的单例** → 初始化顺序灾难（A 的构造要 B 已构造好，B 又要 A）。C++ 跨翻译单元的全局变量初始化顺序未定义，著名的"static initialization order fiasco"。
- **你要支持多实例的将来**（多租户、多数据库）→ 单例把这扇门焊死了。重新打开要大改。
- xv6 用全局单例（`ftable`、`kmem`、`ptable`）是**对的**：内核本来就只有一个地址空间、一组物理资源，单例符合物理事实。你的 Web 应用不是内核，别照搬。

### 在真实代码里在哪
- `third-party/xv6-riscv-solution/net/kernel/file.c:17` — `ftable` 全局唯一文件表。
- `third-party/xv6-riscv-solution/cow/kernel/kalloc.c` — `kmem` 全局空闲内存链表，整个内核就一个内存分配器。
- 标准库：Python `logging.getLogger` 同名返回同一实例、Go `database/sql` 的全局 driver 注册表。

---

## 7. 享元 / 对象池 — "创建太贵要复用"

### 你遇到的信号
你**频繁 new 又立刻丢**某个对象（DB 连接、线程、4KB 的页帧、大数组），GC/分配器成了瓶颈；或者对象本身**很重**（要握手、要预读、要锁），重复建太浪费。

### 最小例子（before → after）
```python
# ---- BEFORE：每个请求新建/关闭 DB 连接，握手开销吃掉一半 RTT ----
def handle(req):
    conn = psycopg.connect(DSN)   # 每次都 TCP 握手 + 认证
    rows = conn.query(req.sql); conn.close()

# ---- AFTER：池化，借了用、用完还 ----
class Pool:
    def __init__(self, n): self._free = [make_conn() for _ in range(n)]
    def acquire(self): return self._free.pop()
    def release(self, c): self._free.append(c)   # 用完还回，下次复用
pool = Pool(16)
def handle(req):
    c = pool.acquire()
    try: return c.query(req.sql)
    finally: pool.release(c)     # 关键：无论成功失败都还
```

### 何时别用（红线）
- **对象很轻、创建几乎免费**（int、小 struct、纯数据对象）→ 池化反而增加管理开销。Python 里池化 `dict` 是负优化。
- **对象有状态、且状态会被上次使用污染** → 复用前必须彻底 reset，reset 比新建还贵就别池化。bustub 的 frame 复用前 `Reset()` 清零就是这个原因。
- **池满了之后的策略要想清楚**（等？报错？建临时实例？），否则高并发下池反而成了瓶颈和死锁源头。
- **连接池大小 > 数据库最大连接数** → 经典生产事故。

### 在真实代码里在哪
- `third-party/bustub/src/include/buffer/buffer_pool_manager.h` —— **整个 buffer pool 就是对象池**：固定数量 frame 反复装不同 page，热的留下、冷的淘汰。这是享元 + 淘汰策略（LRU/LRU-K/ARC）的组合，数据库的核心。
- `third-party/xv6-riscv-solution/net/kernel/file.c:29` — `filealloc` 遍历 `ftable.file[]` 找 `ref==0` 的 slot 复用，配合引用计数 `filedup/fileclose`。**文件描述符表就是对象池 + 引用计数**。
- `third-party/xv6-riscv-solution/cow/kernel/kalloc.c` — `kmem` 空闲页链表，4KB 物理页的池。
- 标准库：Python `queue.Queue`/`multiprocessing.Pool`、Java `ThreadPoolExecutor`、Go `sync.Pool`。

---

## 8. 模板方法 — "算法骨架固定，步骤可变"

### 你遇到的信号
你有**两个以上流程，骨架一模一样**（都是"打开→处理→关闭""接收→校验→执行→返回"），只是其中某几步的具体实现不同。你把骨架复制粘贴后改其中几行，结果骨架修了一处 bug，N 份副本要同步改。

### 最小例子
```c
// ---- xv6 syscall 分发的"骨架固定、步骤可变"（简化）----
void syscall(void) {            // 骨架：读号 → 查表 → 调用 → 存返回
  int num = myproc()->tf->a7;            // 步骤1: 取系统调用号（固定）
  if (num > 0 && num < NELEM(syscalls) && syscalls[num]) {
    myproc()->tf->a0 = syscalls[num]();  // 步骤2: 调对应处理（可变）
  } else {
    myproc()->tf->a0 = -1;               // 步骤3: 错误兜底（固定）
  }
}
// 骨架不动，加新系统调用 = 加一个 sys_xxx 函数 + 注册进表
```

### 何时别用（红线）
- **骨架只有 2 步** → 不值得抽基类，直接写。
- **"可变步骤"其实每个子类都不一样、没有共性** → 模板方法要求子类实现相同的"钩子"签名；签名对不齐就会出现"这个钩子对 A 有意义对 B 没意义"的伪参数。这时该拆成组合（策略），别用继承。
- **继承层级深**（基类→中间类→子类→孙子类）→ 这是 Java 老代码的通病，override 链深到没人能预知最终行为。**优先组合优于继承**是更重要的原则，模板方法恰恰是继承，慎用。
- 用函数式语言时，模板方法天然退化成"高阶函数传回调"，别硬用类继承模拟。

### 在真实代码里在哪
- `third-party/xv6-riscv-solution/cow/kernel/syscall.c:136` — `syscall()` 骨架 + `syscalls[]` 可变步骤。
- `third-party/xv6-riscv-solution/cow/kernel/trap.c:38` — `usertrap()` 是"异常/中断处理骨架"，不同 `scause` 进不同分支（系统调用、缺页、设备中断）。
- 标准库：Python `unittest`（`setUp→test_xxx→tearDown` 骨架）、`asyncio` 事件循环、Django 类视图 `dispatch`。

---

## 9. 状态机 — "对象行为随状态变"

### 你遇到的信号
你对象里 `if (state == A) ... else if (state == B) ...` 满天飞，**同一个方法在不同状态做完全不同的事**；或者出现"非法状态转移"的 bug（一个还没 RUN 的进程被调度、一个已关闭的连接被写）。

### 最小例子（枚举 vs 状态表）
```c
// ---- xv6 进程状态：枚举 + 散落的判断（真实）----
enum procstate { UNUSED, SLEEPING, RUNNABLE, RUNNING, ZOMBIE };
// proc.c 里 scheduler() 只挑 RUNNABLE 的跑；exit() 把自己置 ZOMBIE 等父进程收尸

// ---- 状态多、转移复杂时，用"状态表"比 if/else 清晰 ----
enum state { S0, S1, S2, DONE };
struct edge { enum state from; event_t ev; enum state to; void (*action)(ctx*); };
static const edge FSM[] = {        // 一张表描述全部合法转移
  {S0, EVT_X, S1, act_a},
  {S1, EVT_Y, S2, act_b},
  {S2, EVT_Z, DONE, act_c},
};
void step(ctx *c, event_t e) {
  for (auto &ed : FSM)
    if (ed.from == c->st && ed.ev == e) { ed.action(c); c->st = ed.to; return; }
  // 落到这 = 非法转移，直接报错而不是"静默忽略"
}
```

### 何时别用（红线）
- **状态 ≤ 3 个、转移就是线性的**（init→ready→run）→ 用枚举 + 一两个 if 足够，别造状态表。
- **状态表会让"非法转移"被隐藏** → 反而更危险。状态机的核心价值是**把合法转移显式化、让非法转移在编译期或运行期立刻报错**。如果你的"状态表"什么转移都接，那它不是状态机，是个 `map` 伪装。
- **状态来自外部输入、不可信** → 先用状态表校验合法性，拒绝非法转移，否则就是个"任意跳转的 goto"。
- 用 Rust 的话，**用 enum + match 让非法状态在类型层面就表达不出来**（"让非法状态不可表示"），比运行期状态表更强。

### 在真实代码里在哪
- `third-party/xv6-riscv-solution/cow/kernel/proc.h:83` — `enum procstate { UNUSED, SLEEPING, RUNNABLE, RUNNING, ZOMBIE }`，进程生命周期就是这五个状态的转移。
- `third-party/xv6-riscv-solution/cow/kernel/proc.c` — `scheduler()` 只挑 `RUNNABLE`，`exit()` 置 `ZOMBIE`，`wait()` 回收 `ZOMBIE → UNUSED`。
- TCP 状态机（11 个状态、几十条转移）是工业级状态机的标杆，手撸 if/else 必崩，所以协议栈都用表驱动。
- 正则引擎、词法分析器也是状态机。

---

## 10. 责任链 — "请求一层层处理"

### 你遇到的信号
一个请求要**依次过好几关**：鉴权 → 限流 → 参数校验 → 业务 → 日志。每关可能"放行"也可能"拦截"。你不想把这些 `if` 全堆进业务函数。

### 最小例子
```python
# ---- BEFORE：业务函数里堆满"前置检查" ----
def handler(req):
    if not auth(req): return 401
    if rate_limit(req): return 429
    if not valid(req): return 400
    log(req)
    return business(req)     # 业务被埋在一堆 if 下面

# ---- AFTER：每个 handler 是一环，能处理就处理，不能就交给下一环 ----
class Handler:
    def __init__(self, nxt=None): self.next = nxt
    def handle(self, req):
        r = self._do(req)
        return r if r is not None else self.next.handle(req)
class Auth(Handler):
    def _do(self, req): return None if auth(req) else (401,)
chain = Auth(RateLimit(Validate(Log(Business()))))
chain.handle(req)
# Flask/Django/FastAPI 的 middleware 就是这个：@app.use(...)
```

### 何时别用（红线）
- **链只有一环** → 直接调函数。
- **每一环都要跑（不是"能处理就停"）** → 那不是责任链，是观察者/广播，别用错模型。责任链的语义是"有人接手就停"。
- **链在运行时动态拼、且依赖顺序** → 顺序 bug 极难查（"为什么限流在鉴权前"）。生产里尽量让链在启动期固定下来。
- **链太长（>7 环）** → 每个请求走一遍 O(n)，调试栈深、性能下降。该合并的合并。

### 在真实代码里在哪
- `third-party/xv6-riscv-solution/cow/kernel/trap.c:38` — `usertrap()` 按 `scause` 一层层试：是系统调用？是 COW 缺页？是设备中断？都不是就 kill。**这就是责任链**——每个分支"能认领就认领，认领不了往下走"。
- Linux 内核中断处理：顶半部（hardirq）→ 底半部（softirq/workqueue）也是分层处理。
- 标准库：Python WSGI/ASGI middleware、Java Servlet `FilterChain`、Express/Koa middleware、Go `http.Handler` 链。

---

## 11. 迭代器 — "统一遍历"

### 你遇到的信号
你对**不同容器**（数组、链表、树、文件行、数据库结果集）写了 N 套 `for`，每套写法不一样：数组用下标、链表用 `next` 指针、树用递归。你想统一成"不管底层是什么，我都 `for x in container`"。

### 最小例子
```python
# ---- before：遍历不同结构要不同的代码 ----
for i in range(len(arr)): f(arr[i])          # 数组
node = head
while node: f(node.val); node = node.next    # 链表
def walk(t):                                  # 树要递归
    if t: walk(t.left); f(t.val); walk(t.right)

# ---- after：每个容器实现 __iter__，调用方一种写法 ----
class LinkedList:
    def __init__(self, head): self.head = head
    def __iter__(self):           # 只要实现这个，就能 for x in ll
        node = self.head
        while node: yield node.val; node = node.next
class Tree:
    def __iter__(self):
        if self.left:  yield from self.left
        yield self.val
        if self.right: yield from self.right
# 调用方完全一样：for x in (arr, ll, tree): ...
```

### 何时别用（红线）
- **语言已经内建了**（Python `for...in`、Go `range`、JS `for...of`、Rust `for x in iter`）→ **直接用，别手写 `Iterator` 类**。Python `yield` 已经是最简写法，再封装一层纯增心智负担。
- **容器很小、就遍历一次** → 没必要抽象，直接 `for i in range(len)`。
- **迭代过程有副作用、依赖外部状态** → 生成器虽然优雅，但隐式状态机让 debug 困难。关键路径上有时显式 cursor 更清楚。
- **要随机访问** → 迭代器是"顺序访问"抽象，强行用它做 `get(i)` 会退化成 O(n)。

### 在真实代码里在哪
- `third-party/bustub/src/include/execution/executors/abstract_executor.h:42` — `virtual void Init()=0; virtual auto Next(...)=0;` 这是 **Volcano 模型**：每个算子都是个迭代器，`Next()` 吐一条 tuple。查询执行就是"最外层算子不停 Next，它向左孩子 Next、左孩子向它左孩子 Next……"一棵迭代器树。**迭代器 + 组合的合体**。
- 标准库：Python `iter()/next()`、`itertools`、Go `range`、Rust `Iterator` trait（`map/filter/collect` 链式）、C++ STL 迭代器。

---

## 12. 组合 — "树形结构统一处理"

### 你遇到的信号
你有一个**树形/嵌套结构**（文件系统目录树、AST、组织架构、算子树），叶子节点和非叶子节点接口不同，调用方要写"如果是目录就遍历、如果是文件就处理"的 if/else。

### 最小例子
```python
# ---- before：调用方要区分"是容器还是叶子"----
def total_size(node):
    if isinstance(node, File): return node.size
    if isinstance(node, Dir):
        return sum(total_size(c) for c in node.children)  # 两套逻辑
    raise TypeError

# ---- after：叶子和容器实现同一个接口，统一递归 ----
class Node:                          # 统一接口
    def size(self): raise NotImplementedError
class File(Node):
    def __init__(self, sz): self.sz = sz
    def size(self): return self.sz
class Dir(Node):
    def __init__(self, children): self.children = children
    def size(self): return sum(c.size() for c in self.children)  # 不区分孩子类型
# 调用方：root.size() —— 不管多深、不管叶子还是容器，一句话搞定
```

### 何时别用（红线）
- **结构不是树**（是图、有环、有多父）→ 组合模式假设树（每个孩子一个父亲），图结构强行组合会出现"一个节点被算两次"。
- **叶子和容器的"操作语义"根本不同**（叶子是数据、容器是元数据）→ 强行统一接口会出现"对叶子调用 add_child 没意义"的伪方法。更好的做法是接口里只放真正公共的操作。
- **树很深 + 递归实现** → 栈溢出。要么改迭代，要么限制深度。
- **要严格区分类型安全**（编译期杜绝"把文件当目录"）→ 用 Rust enum / 访问者模式，比组合的"都实现同接口"更安全。

### 在真实代码里在哪
- `third-party/bustub/src/execution/executor_factory.cpp:56` — `CreateExecutor` 递归构造算子树：`HashJoin` 的左右孩子又是算子，`Insert` 的孩子是算子……**整棵查询执行树就是组合模式**，每个算子 `Next()` 时向孩子要数据，对孩子是叶子还是子树一视同仁。
- `third-party/xv6-riscv-solution/cow/kernel/file.h:18` — `struct inode` 的 `addrs[NDIRECT+1]`：前 12 个直接块（叶子），第 13 个是一级间接块（容器，指向更多块），文件系统用这种"块指向块"形成树。**文件系统的多级索引就是组合。**
- AST：编译器里表达式树（`BinOp(Num, Num)`、`Num`）是教科书级组合，访问者模式常和它配套。
- 标准库：Python `pathlib.Path`（目录和文件都是 Path）、DOM/HTML 节点树、React 组件树（`children` 数组，组件套组件）。

---

## 收尾：三个反共识的总结

1. **模式是"症状的药"，不是"维生素"。** 没有那个坏味道（重复的 if/else、失控的耦合、创建逻辑散落），就别预防性吃药。代码库 80% 的过度设计，都来自"我担心将来要扩展"——而那个将来 90% 没来。
2. **先用语言内建的，再自己造。** Python `@decorator`、`for...in`、`async with`；Go `interface`+`range`；Rust `trait Iterator`+`enum`。这些已经是模式了，你再封一层就是在和语言对着干。
3. **真正高频的不是 23 个，是这里讲的 12 个里的 5 个：策略、装饰器、对象池、迭代器、组合。** 把这 5 个吃透（看 bustub 的 buffer pool + 算子树，看 xv6 的 file 表 + syscall 跳表），你已经能解释 90% 的工程代码结构。剩下 7 个是"遇到了再查"，而 GoF 另外那 11 个（桥接、蝇量之外的原型/建造者/命令/备忘录/中介者/外观/代理/访问者/模板方法之外那些）……说实话，五年写业务你可能一次都用不上访问者。

去读 `third-party/bustub/src/buffer/buffer_pool_manager.cpp` 和 `third-party/xv6-riscv-solution/net/kernel/file.c`，你会同时看到对象池、策略、享元、引用计数、单例——**真实系统从不只一个模式，它们是长在一起的。** 这才是程序员该有的模式视角。

---

## 🎤 费曼挑战（真懂了吗？）

> 费曼法：能讲给小学生听才算真懂。用 `python3 tools/feynman.py --source patterns` 记录。

### 挑战 1：单例的陷阱（对应 §6）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 为什么说 90% 的单例是全局变量的伪装？ | 全局可变状态=测试地狱 |
| L2 联系 | 你代码里哪个单例可以删掉？换成什么？ | 依赖注入 |
| L3 创造 | 写一个线程安全的懒加载（不用 synchronized） | 用 once/dcl |
| L4 教学 | 向新人解释"全局变量为什么是坏味道" |

### 挑战 2：状态机 vs if-else（对应 §9）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 什么时候该用状态机，什么时候 if-else 够了？ | 状态>3 且转移复杂 |
| L2 联系 | 你的代码里哪个 if-else 链应该变成状态机？ | 能指出具体位置 |
| L3 创造 | 画一个 TCP 连接状态机（11 个状态） | 标出所有转移 |
| L4 教学 | 解释"状态爆炸"为什么是状态机的红线 |

### 挑战 3：装饰器链（对应 §3）
| 层级 | 挑战 | 过关标准 |
|------|------|---------|
| L1 复述 | 装饰器模式解决什么问题？ | 横切关注点 |
| L2 联系 | 你代码里哪里用了装饰器？ | 日志/缓存/限流 |
| L3 创造 | 用装饰器实现"日志+缓存+限流"三层洋葱 | 能组合 |
| L4 教学 | 向同事解释"装饰器 vs 继承"的区别 | 组合优于继承 |
