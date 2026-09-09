# 视角 9：安全 / 可靠性专家（Security & Reliability Engineer）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（brisk-jade-fox），扮演曾做 ARM Spectre mitigation、OpenSSL 审计、ASAN/UBSAN 部署的安全专家
> **方法**：read-only 审查内存安全、整数溢出、UB、数值异常、侧信道、DoS 攻击面

---

## 1. 视角定位

我负责内存安全、整数溢出、UB、数值异常（NaN/Inf）、侧信道与 DoS 攻击面。本项目当前是**单机性能实验室**（M/K/N 为 `#define`），但只要演进为 SDK 被上层框架（推理引擎/编译器后端）调用，攻击面会从"零"跳到"全量"。我会按这个演化路径打分。

## 2. 八个盲区

### ① malloc 全仓零 NULL 检查 —— P0 内存安全
`gemm_f32.c:158`、`gemm_s8.c:163-167`、`attention_neon.c:39,73-78,164`、`multicore_tiled.c:85,101-104`、`conv_winograd.c:230-235` 共计 **20+ 处 `malloc` 无任何返回值校验**。OOM 或大矩阵场景下立即产生 NULL 解引用 → SIGSEGV。在麒麟 V10 SP1 + cgroup 内存限制下，攻击者构造一次大 N 调用即可 DoS。违反 MISRA-C Rule 21.3 / CWE-252 / CWE-690。

### ② 整数溢出：`M*K*4` 以 `int` 求值 —— P0
`gemm_f32.c:158`：`malloc(M*K*4)`，三元乘法在 `int` 域。当前 1024³ 安全（4 MiB），但 `gemm_tune.c` 已把 M/K/N 参数化（sweep），一旦 `M>32767`，`M*K` 先于 `*4` 在 `int` 域溢出 → 传给 malloc 一个小值 → **堆溢出（CWE-190/CWE-787）**。`conv_winograd.c:224-228` 同模式。正确写法是 `size_t bytes = (size_t)M * K * sizeof(float)`，并用 `__builtin_mul_overflow` 兜底。

### ③ 未初始化内存读取 / 尾部静默错误 —— P0
两类问题：
- **尾部行未写**：`gemm_f16.c`/`gemm_f32.c` 的 `v4_dual` 用 `M2 = M & ~1`，奇数 M 时最后一行 C 永不写入。在 main() 里因先跑 scalar 覆盖，侥幸不暴露；**一旦作为库被调用，C 的尾部是 malloc 残留 → UB + 信息泄漏（CWE-908/CWE-200）**。
- **`multicore_tiled.c:93` `if (M_sub == 8)`**：tail 分支直接跳过，对应 C 行保持 calloc 的 0 → **静默错误结果**。test.sh 只查 8×8 角，CI 根本抓不到。这是最危险的"看起来对、实际错"。

### ④ NaN/Inf 在 softmax 全链路未防护 —— P0
`attention_neon.c:76,142,213`：`m_vec[i] = -INFINITY` 初值 + `inv = 1.0f/l_vec[i]`。当某行 Q·K 全为 -inf（mask 全屏蔽的 causal 场景）→ `row_sum=0` → `l_vec=0` → `inv=+inf` → `O = 0 × inf = NaN`。NaN 沿着 `vfmaq` 在 BMM2 里**逐层污染整行**，且 NEON 不 trap。Flash Attention 论文里明确要求处理 `m=-inf` 边界，本项目完全裸奔。

### ⑤ 完全没有 ASAN/UBSAN/valgrind 测试矩阵 —— P0
`Makefile:21` 的 `OPT_FLAGS := -O3 -fno-omit-frame-pointer -g -fno-inline-functions` 是**纯性能配置**，`test.sh` 只 grep `✅/❌` 文本。这意味着：
- 越界读写（如盲区②③）跑 100 遍也不报警；
- `gemm_s8.c:95` 的 `vld1_s32(&A[(i+0)*K+k])` 在 K 非 4 倍数时**越界读 4 字节**——ASAN 一秒抓到，现在永远抓不到；
- 严格别名、有符号溢出等 UB 全部沉默。

PhyGCC 12.3.2 基于 GCC 12，**ASAN/UBSAN 在 aarch64 上完全支持**（libasan/libubsan 随 PhyGCC 发布），`-fsanitize=address,undefined` 可直接用。

### ⑥ NEON 数据依赖分支 → 时序侧信道 —— P1
`attention_neon.c:104-105,184` 的 row-max：
```c
for (j...) if (S_blk[i*Kb+j] > rm) rm = S_blk[i*Kb+j];
```
这是**数据依赖分支**，在机密计算/隐私推理场景（联邦学习、TEE 内推理）下，S 的值通过分支预测器时序泄漏。应改用无分支 `rm = vmaxvq_f32(vmaxq_f32(rm_vec, ld))`。`expf` 来自 libm，通常**非定常常数时间**（denormal fast-path、Inf/NaN 专用路径），在侧信道敏感场景必须替换为定常多项式逼近。

### ⑦ Spectre v1/v4 在 D3000 上的缓解缺失 —— P1（SDK 化后才相关）
D3000 FTC862 是 ARMv8.2-A，受 Spectre v1（Bounds Check Bypass）/ v4（Speculative Store Bypass）影响。一旦 SDK 化引入 `if (i < M) A[i*K+k]` 这类边界检查，必须在检查后插屏障：
- **Spectre v1 缓解**：`asm volatile("dsb sy\n isb" ::: "memory")`（重量级，仅在信任边界处用）；
- **Spectre v4 缓解**：`#define CSDB() asm volatile("hint #20" ::: "memory")`，放在 load 之后、依赖使用之前。

### ⑧ DoS / 攻击面（SDK 化评估）—— P1
当前 `#define M 1024` 把攻击面归零，但仓库结构已具备库形态。一旦 H/W/CIN/COUT 来自网络/模型文件：
- `conv_winograd.c:230` `malloc(in_size*sizeof(float))` 攻击者给 H=W=65536 → 单次 64 GiB → OOM；
- `gemm_s8.c:95` K 非 4 倍数 → 越界读；
- 缺少任何 `assert(M>0 && K%4==0 && H%2==0)` 前置校验。

## 3. 改造建议（按优先级）

**P0（本周必做）**
1. Makefile 增加 sanitizer 目标：
   ```make
   SAN_FLAGS = -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all
   sanitize:
       $(MAKE) CFLAGS="$(ARCH_FLAGS) $(SAN_FLAGS)" all
       ASAN_OPTIONS=detect_leaks=1:abort_on_error=1 ./scripts/test.sh
   ```
2. 全仓 `malloc` → `xmalloc` 包装（NULL → `perror+exit`），并把所有 `M*K*N*4` 改 `(size_t)` + `__builtin_mul_overflow`。
3. `gemm_f16/gemm_f32` 的 v4_dual 补 tail 行；`multicore_tiled.c:93` 删掉 `if (M_sub==8)` 让 tail 走 scalar 兜底。

**P1（两周内）**
4. `attention_neon.c` 加 `m_vec[i]==-INFINITY` 早退（输出置 0），并用 `vmaxvq_f32` 消除分支。
5. 新增 `scripts/check-vuln.sh`：读 `/sys/devices/system/cpu/vulnerabilities/*`，对 SDK 入口生成 `csdb`/`dsb sy` 注入清单。
6. INT8 `vld1_s32` 前断言 `K%4==0`。

**P2（SDK 化时）**
7. 所有公共入口加 `if (M<=0||K<=0||N<=0) return -EINVAL;`，并对 `M*K` 做 overflow 检查。
8. 引入定常 `expf` 替代（用于侧信道敏感路径）。

## 4. 关键洞察

- **算子库的攻击面是"阶跃"型的**：当前 `#define` 化让它零攻击面，但仓库已按库结构组织。一旦被推理框架链接，**盲区②③④⑥会同时从"理论"变成"线上 CVE"**。
- **NEON 本身时序基本定常**（`vfmaq`/`vdotq` 无数据依赖延迟），但**人为引入的分支（row-max）和 libm `expf` 才是真泄漏点**。
- **D3000 Spectre 缓解的工程现实**：麒麟 V10 SP1 内核侧通常已开 SSBD，但**用户态算子库需要自行在信任边界加 `csdb`**。
- **最大隐藏雷是 `multicore_tiled.c:93` 的静默错误**：它过 `make test`，却会在真实 LLM workload 下产出错误 token。

## 5. 新增实验清单

| 文件 | 目的 | 关键检查 |
|---|---|---|
| `analysis/lens-asan.c` | ASAN/UBSAN 下跑全算子 | 越界、UAF、UB、tail 漏写 |
| `analysis/lens-fuzz-attack.c` | libFuzzer 风格随机 + 对抗输入 | OOM、整数溢出、NaN 传播 |
| `analysis/lens-sidechannel.c` | `perf stat` 测 row-max 与 `expf` 时序方差 | 方差 > 阈值告警 |
| `analysis/lens-spectre.c` | `dsb sy`/`csdb` 前后做 PoC 探测 | 探测成功率下降 |
| `analysis/lens-tail-coverage.c` | M/K/N ∈ {素数, 非 4/8 倍数} 全组合 | tail 行 ≠ 0 即 FAIL |

---

**一句话结论**：性能 92%、安全 35%。八处盲区里有四处（malloc/溢出/tail 漏写/NaN）能在 SDK 化首日变成线上事故；好在**全部修复成本低于 1 人周**（P0 三项加起来 ~2 天）。建议把 `make sanitize` 作为 CI 必过门槛。
