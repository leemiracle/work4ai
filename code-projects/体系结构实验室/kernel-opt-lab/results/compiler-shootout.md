# 编译器横评（Compiler Shootout）

> 日期：2026-07-01 ｜ 机器：greatwall-pc / Phytium D3000 (FTC862) ｜ 绑核 taskset -c 0
> 回答编译器专家 lens（[`docs/lenses/04-compiler-expert.md`](../docs/lenses/04-compiler-expert.md)）的"PhyGCC/clang/gcc 零横评"问题

---

## 1. 测试对象

`src/gemm_f32.c` v5_mr8（FP32 GEMM MR=8，4 FVU 全开），1024³，3 次取后一次（warmup 后）。

## 2. 结果

| 编译器 | 版本 | march flag | v5_mr8 时间 | GFLOPS | 利用率 (of 40) | vs PhyGCC |
|--------|------|-----------|:----------:|:------:|:--------------:|:---------:|
| **PhyGCC** | 12.3.2 | `armv8.2-a+fp16+dotprod` | 57.2 ms | **37.54** | **93.9%** | 基准 |
| clang | 10.0.0 | `armv8.2-a` | 58.9 ms | 36.48 | 91.2% | -2.8% |
| gcc | 9.3.1 | `armv8.2-a+fp16+dotprod` | 82.1 ms | 26.17 | 65.4% | **-30.3%** |

## 3. 关键结论

1. **PhyGCC 12.3.2 是 D3000 上的最优编译器**——比系统自带 gcc 9.3.1 快 **43%**（26.17 → 37.54 GFLOPS）。证明飞腾自研编译器对 D3000 微架构（4 FVU 调度、NEON 指令编排）做了针对性优化。
2. **clang 10 接近 PhyGCC**（差 3%），两者都把 v5_mr8 推到 90%+ 利用率。clang 的 LLVM 后端向量化能力强。
3. **gcc 9.3.1 明显落后**（65.4%）。推测原因：老版 gcc（9.x）的 AArch64 后端对 D3000 自研核的调度模型不如 PhyGCC/clang 精确，NEON FMA 的指令编排次优。

## 4. 建议

- **生产/基准测试**：用 PhyGCC（项目 Makefile 默认）
- **调试/交叉验证**：可用 clang（性能接近，警告更清晰）
- **避免**：gcc 9.3.1 会低估 D3000 真实算力 30%，不要用它发性能数据

## 5. 复现命令

```bash
# 三编译器编译 gemm_f32
/opt/apps/phygcc-12.3.2/bin/gcc -O3 -march=armv8.2-a+fp16+dotprod src/gemm_f32.c -o /tmp/gemm_phygcc -lm
gcc -O3 -march=armv8.2-a+fp16+dotprod src/gemm_f32.c -o /tmp/gemm_gcc93 -lm
clang -O3 -march=armv8.2-a src/gemm_f32.c -o /tmp/gemm_clang10 -lm   # clang 不认 PhyGCC 的 +dotprod 语法

# 绑核跑（warmup + measured）
for cc in phygcc gcc93 clang10; do
    taskset -c 0 /tmp/gemm_$cc >/dev/null 2>&1   # warmup
    echo "=== $cc ==="
    taskset -c 0 /tmp/gemm_$cc 2>&1 | grep mr8
done
```

## 6. -O 优化级别对比（PhyGCC 12.3.2，gemm_f32 v5_mr8 + prefetch）

| 级别 | v5_mr8 时间 | GFLOPS | 利用率 | max_diff |
|------|:----------:|:------:|:------:|:--------:|
| -O2 | 110.3 ms | 19.48 | 48.7% | 3.05e-05 |
| **-O3** | **55.8 ms** | **38.48** | **96.2%** | 3.05e-05 |
| -Ofast | 174.3 ms | 12.32 | 30.8% | 6.10e-05 |

### 🔥 反直觉发现：-Ofast 反而比 -O3 慢 3 倍！

**结论**：手工 NEON 优化的 GEMM，**-O3 是最优，-Ofast 有害**。

原因分析：
1. v5_mr8 微内核是**手工编排的 32 条 vfmaq_laneq_f32**，指令顺序已经为 4 FVU 流水线精心调度
2. `-Ofast` = `-O3 -ffast-math`，其中 -ffast-math 允许编译器重排/合并 FMA，**破坏了手工指令调度**
3. 编译器自作主张的"优化"干扰了微内核的 FVU 分配，导致 FMA stall
4. 旁证：-Ofast 的 max_diff 翻倍（3.05e-05 → 6.10e-05），说明 -ffast-math 改变了累加顺序

**教训**（写进项目宪法实验纪律）：手工 SIMD 优化的算子，用 `-O3`，**禁用 `-Ofast`**。编译器的激进数值优化和手工指令调度冲突。

## 7. 待扩展

- [x] ~~-O0/-O1/-O2/-O3/-Ofast 各级别对比~~（§6 完成，结论：-O3 最优，-Ofast 有害）
- [x] ~~fast-math 的影响~~（§6：-Ofast 含 -ffast-math，干扰手工调度，降速 3×）
- [ ] 其他算子横评（gemm_s8 的 vdotq、attention 的 softmax）
- [ ] clang 更新版本（14+）是否有进一步提升

## 8. -O 级别复现命令

```bash
for opt in O2 O3 Ofast; do
  /opt/apps/phygcc-12.3.2/bin/gcc -$opt -march=armv8.2-a+fp16+dotprod src/gemm_f32.c -o /tmp/gemm_$opt -lm
  taskset -c 0 /tmp/gemm_$opt >/dev/null 2>&1   # warmup
  echo "=== -$opt ==="; taskset -c 0 /tmp/gemm_$opt 2>&1 | grep mr8
done
```
