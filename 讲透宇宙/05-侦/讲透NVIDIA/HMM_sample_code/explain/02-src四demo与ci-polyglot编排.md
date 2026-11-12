# 02 · src/ 四 demo 与 ci/ polyglot 编排 —— HMM 教学层的自编译艺术

## 角色定位

src/ 四个 .cpp 是 HMM（异构内存管理，非隐马尔可夫）的四个教学单元：atomic_flag 讲"CPU-GPU 共享一个原子变量"、ticket_lock 讲"跨设备互斥"、file_before/file_after 用同一任务讲"HMM 前后文件处理的差"。ci/run 与 ci/demos 是编排层：前者拉 nvhpc 容器，后者把 .cpp 当 bash 脚本逐个执行。四 demo **互不依赖**（quoted include=0，只用系统头），每个独立成课。

## 内部结构

- **src/atomic_flag.cpp（56 行）**：main（src/atomic_flag.cpp:35-55）用 jthread 起 GPU 线程（:41），`for_each_n(par,&message,1)` 写 `message=42` 再 `flag.store(1)`（:42-45）；主线程自旋 `flag.load()`（:49）后打印（:52）。
- **src/ticket_lock.cpp（90 行）**：`ticket_lock` 结构体（src/ticket_lock.cpp:36-51）——取号 relaxed（:46）+叫号 acquire（:47）+内嵌 `guard_t` 析构 release 放行（:42）；main（:53-89）64 个 CPU 线程（:57）+4096 个 GPU stdpar 线程（:58,:63）同抢一把锁，校验 `message==4160`（:81-86）。
- **src/file_before.cpp（85 行）**：sortfile（src/file_before.cpp:41-47）`fread` 整读进 vector（:44）→`std::sort(par,...,greater{})` GPU 降序排（:45）；main（:53-84）`for_each_n(par,iota)` 并行生成 N 字节文件（:71-72），`fopen` 后进 sortfile（:77,:82）。
- **src/file_after.cpp（90 行）**：sortfile（src/file_after.cpp:43-52）改 `mmap(...,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0)`（:44）→同一 `std::sort(par)` 直接排在映射页上（:49）→munmap（:51）；main 用 `open(O_RDWR)` 取 fd（:82）。两文件除 sortfile/打开方式外逐行同构，天然 diff 教材。
- **ci/run（12 行）**：`IMG=nvcr.io/nvidia/nvhpc:23.5-devel-cuda12.1-ubuntu22.04`（ci/run:4），docker `--gpus=all` 挂仓库执行 `./ci/demos`（ci/run:5-11）。
- **ci/demos（11 行）**：子 shell `cd src` 后依次 bash 四个 .cpp（ci/demos:5-9）。

## 外部连接

图谱依赖链：ci/run→ci/demos→四 demo（depends_on）；README.md documents 全部下游。四 demo 只用系统头；真正外部依赖仅 nvc++ 工具链（容器提供）与 HMM 使能硬件。与 miniapp 零耦合——那是 nvcc/cub 的另一条产品线。

## 数据流

**polyglot 自编译链**：.cpp 首行 `#if 0`（src/atomic_flag.cpp:1），bash 视为注释、执行紧随三行——内嵌 `nvc++ ... $0` 编译自身、`./demo`（file 系带参数 10）运行、`exit 0`（:2-5）；预处理器整段跳到 `#endif`（:6），C++ 主体无感。**demo 数据流**：atomic_flag——GPU 写/CPU 读同一栈内存；ticket_lock——4160 次跨设备临界区递增；file_before——生成→fread 拷进 vector→GPU 排→打印；file_after——生成→mmap 零拷贝→GPU 在页缓存上直接排→打印（MAP_SHARED 回写文件）。

## 设计决策

1. **`#if 0` polyglot 换掉构建系统**：.cpp 自带"编译+运行"说明书，ci 只剩 23 行 shell——教学仓极简主义。
2. **`-gpu=nomanaged` 的有无是叙事核心**：另三个 demo 自编译命令都带它（src/atomic_flag.cpp:3 等），堆/栈/mmap 全靠 HMM 硬件直访；file_before **故意不带**（src/file_before.cpp:3）——stdpar 默认堆走 managed memory，vector 靠迁移兜底，正是"HMM 之前"的旧姿势。对照阅读即见两种世界观。
3. **标准 C++ 当 GPU 语言**：零 CUDA API，`std::execution::par` 的 sort/for_each_n 即 kernel launch——"plain C++ 直通 GPU"的共同修辞。
4. **MAP_SHARED 而非 MAP_PRIVATE**：file_after.cpp:44 共享映射让排序写回页缓存并落盘——"GPU 改的就是文件本身"，比私有映射更有说服力。

## 新人提示

- `bash src/xxx.cpp` 即可直接跑（须 nvc++ 与 HMM 硬件：`nvidia-smi -q | grep Addressing`）；docker 党用 `./ci/run`。
- ticket_lock 成功输出拼作 `SUCESS`（src/ticket_lock.cpp:86，少一个 C），别当 bug 报。
- 编译产物留在 src/ 内，git status 见未跟踪二进制属预期。
- file 系 demo 的 N 取 10 最直观；`'0'+i` 生成器在 N>256 时回绕，非排序 bug。
- 看"消失的拷贝"：diff 只看 sortfile——fread+vector vs mmap+裸指针。
