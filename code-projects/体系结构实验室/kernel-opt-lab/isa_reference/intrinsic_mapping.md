# A64 指令 → C/C++ Intrinsic 速查表
> **生成日期**：2026-06-29  
> **PDF 源版本**：ARM DDI 0487G.b (2021-07)  
> **飞腾实测平台**：D3000M (FTC862) @ 2.5 GHz, ARMv8.4-A

> 当你想用 C 写 NEON/LSE/Crypto 代码时，本表帮你快速找到对应的 intrinsic 函数。
> 数据基于 **GCC 12.3 / Clang 16 / ARM ACLE 2.0+** 规范。
> 头文件：`<arm_neon.h>` (NEON/SIMD/Crypto)、`<arm_acle.h>` (CRC32/RDM/PAC/系统)。

---

## 0. 编译开关速查

```makefile
# 飞腾 D3000M (FTC862) 一键开启所有扩展
CFLAGS += -mcpu=ftc86x

# 或显式 march
CFLAGS += -march=armv8.4-a+crypto+crc+simd+lse+rcpc+flagm+jscvt+fcma+dotprod+sm4+sm3+sha3+sha512+rng

# 单独开某扩展
-march=armv8.2-a+fp16      # 仅 FP16
-march=armv8.4-a+dotprod   # 仅 UDOT/SDOT
-march=armv8.1-a+lse       # 仅 LSE
```

C 代码中编译期检测：
```c
#ifdef __ARM_FEATURE_NEON         // NEON 可用
#ifdef __ARM_FEATURE_CRYPTO       // AES/SHA1/SHA256/PMULL 可用
#ifdef __ARM_FEATURE_CRC32        // CRC32 可用
#ifdef __ARM_FEATURE_ATOMICS      // LSE 可用 (v8.1+)
#ifdef __ARM_FEATURE_FP16         // FP16 标量可用 (v8.2+)
#ifdef __ARM_FEATURE_FP16_FMLA    // FHM fp16→fp32 (v8.4 FHM, 飞腾不支持)
#ifdef __ARM_FEATURE_DOTPROD      // UDOT/SDOT (v8.4)
#ifdef __ARM_FEATURE_JCVT         // FJCVTZS (v8.3 JSConv)
#ifdef __ARM_FEATURE_PAUTH        // PAuth (v8.3)
#ifdef __ARM_FEATURE_COMPLEX      // FCMLA/FCADD (v8.3)
#ifdef __ARM_FEATURE_SM4          // SM4 (v8.4)
#ifdef __ARM_FEATURE_SM3          // SM3 (v8.4)
#ifdef __ARM_FEATURE_SHA3         // SHA3 (v8.4)
#ifdef __ARM_FEATURE_SHA512       // SHA512 (v8.4)
#ifdef __ARM_FEATURE_BF16         // BF16 (v8.6, 飞腾不支持)
#ifdef __ARM_FEATURE_MATMUL_INT8  // I8MM (v8.6, 飞腾不支持)
#ifdef __ARM_FEATURE_SVE          // SVE (飞腾不支持)
```

---

## 1. NEON 基础类型（`<arm_neon.h>`）

| 类型 | 寄存器形态 | 元素类型 | 元素数 |
|------|----------|---------|-------|
| `int8x8_t` | 64-bit | int8 | 8 |
| `int8x16_t` | 128-bit | int8 | 16 |
| `int16x4_t` / `int16x8_t` | 64/128 | int16 | 4/8 |
| `int32x2_t` / `int32x4_t` | 64/128 | int32 | 2/4 |
| `int64x1_t` / `int64x2_t` | 64/128 | int64 | 1/2 |
| `uint8x8_t` / `uint8x16_t` | 64/128 | uint8 | 8/16 |
| `uint16x4_t` / `uint16x8_t` | 64/128 | uint16 | 4/8 |
| `uint32x2_t` / `uint32x4_t` | 64/128 | uint32 | 2/4 |
| `uint64x1_t` / `uint64x2_t` | 64/128 | uint64 | 1/2 |
| `float16x4_t` / `float16x4_t` | 64/128 | fp16 | 4/8 (v8.2+) |
| `float32x2_t` / `float32x4_t` | 64/128 | fp32 | 2/4 |
| `float64x1_t` / `float64x2_t` | 64/128 | fp64 | 1/2 |
| `int8x8x2_t` 等 | struct | - | 2 个 64-bit 寄存器（LD2/3/4） |

**命名规则**：`v<op>[q][<type>][<lane>][_<suffix>]`
- `q` = 128-bit (Quad)，无 = 64-bit
- `type` = `s8/s16/s32/s64/u8/u16/u32/u64/f16/f32/f64`
- `n` = lane (element-wise)

例：`vld1q_f32` = load 4×fp32 (128-bit)，`vadd_s32` = add 2×int32 (64-bit)。

---

## 2. 按扩展的 Intrinsic 映射

### 2.1 NEON base（v8.0 ASIMD）—— 常用核心

| 指令族 | intrinsic 示例 | 说明 |
|--------|--------------|------|
| `LD1/ST1` (单寄存器) | `vld1q_f32(p)` / `vst1q_f32(p, v)` | 加载/存储 |
| `LD2/3/4` (struct) | `vld2q_f32(p)` → `float32x4x2_t` | 交织加载 2/3/4 reg |
| `ADD/SUB (vector)` | `vaddq_f32(a,b)` / `vsubq_s16(a,b)` | 加减 |
| `MUL (vector)` | `vmulq_f32(a,b)` | 乘 |
| `MLA/MLS` | `vmlaq_f32(acc,a,b)` / `vmlsq_*` | 乘加/乘减 |
| `FMLA/FMLS` (fp) | `vfmaq_f32(acc,a,b)` | 融合乘加 |
| `FADD/FSUB/FMUL` | `vaddq_f32`, `vmulq_f32` | 浮点四则 |
| `FMINN/MAX` | `vmaxnmq_f32(a,b)` / `vminnmq_*` | IEEE min/max |
| `FMAXV/MINV` (横向) | `vmaxvq_f32(v)` | 横向最大 |
| `FCMEQ/FCMGT` | `vceqq_f32(a,b)` / `vcgtq_*` | 浮点比较 |
| `FCVT (vector)` | `vcvtq_s32_f32(v)` | 类型转换 |
| `FRINTN/P/M/Z` | `vrndnq_f32(v)` / `vrndpq_f32(v)` | 舍入模式 |
| `FDIV` | `vdivq_f32(a,b)` | 浮点除（非流化） |
| `FSQRT` | `vsqrtq_f32(v)` | 开方 |
| `FRECPE/FRSQRTE` | `vrecpeq_f32(v)` | 倒数近似 |
| `FRECPS/FRSQRTS` | `vrecpsq_f32(a,b)` | Newton-Raphson step |
| `AND/ORR/EOR (vector)` | `vandq_s32(a,b)` / `veorq_*` | 位运算 |
| `USHR/SSHR` | `vshrq_n_u32(v, 4)` | 右移 |
| `SHL` | `vshlq_n_s32(v, 2)` | 左移 |
| `UZP1/UZP2` | `vuzp1q_s16(a,b)` | 解交织 |
| `ZIP1/ZIP2` | `vzip1q_s8(a,b)` | 交织 |
| `TRN1/TRN2` | `vtrn1q_*` | 转置 |
| `REV16/32/64` | `vrev16q_s8(v)` / `vrev32q_*` / `vrev64q_*` | 字节反转 |
| `TBL/TBX` | `vqtbl1q_u8(tbl, idx)` | 表查找 |
| `SXTL/UXTL` | `vmovl_s16(v)` | 8→16 / 16→32 / 32→64 扩展 |
| `SQXTN/UQXTN` | `vqmovn_s32(v)` | 饱和收缩 |
| `EXT` | `vextq_u8(a, b, 3)` | 寄存器拼接抽取 |
| `DUP (element)` | `vdupq_n_f32(*p)` / `vdupq_lane_f32(v, 2)` | 广播 |
| `MOV` | `vmovq_n_f32(0.0f)` | 立即数 |
| `ABS/NEG` | `vabsq_s32(v)` / `vnegq_*` | 绝对值/取反 |
| `MAX/MIN` | `vmaxq_s32(a,b)` / `vminq_*` | 整数最大最小 |
| `CNT` | `vcntq_u8(v)` | popcount (每字节) |

### 2.2 AES/SHA1/SHA256/PMULL（v8.0 Crypto）

| 指令 | intrinsic | 说明 |
|------|----------|------|
| `AESE` | `vaeseq_u8(v_data, v_key)` | 一轮 AES：SubBytes+ShiftRows+MixColumns+AddRoundKey |
| `AESD` | `vaesdq_u8(v_data, v_key)` | 解密一轮 |
| `AESMC` | `vaesmcq_u8(v)` | MixColumns 单独 |
| `AESIMC` | `vaesimcq_u8(v)` | InvMixColumns |
| `PMULL/PMULL2 (8b→16b)` | `vpmull_p64(a,b)` / `vpmull_p128` | 多项式乘 |
| `PMULL (64b→128b)` | `vpmaxq_p64(a,b)` (需 GCC 9+) | 64×64 多项式乘 |
| `SHA1C/P/M/H` | `vsha1cq_u32(acc, w, x)`, `vsha1mq_*`, `vsha1pq_*`, `vsha1h_u32(x)` | SHA1 压缩 |
| `SHA1SU0/SU1` | `vsha1su0q_u32(w)`, `vsha1su1q_u32(w)` | SHA1 schedule |
| `SHA256H` | `vsha256hq_u32(acc1, acc2, w)` | SHA256 主压缩 |
| `SHA256H2` | `vsha256h2q_u32(acc1, acc2, w)` | SHA256 高半压缩 |
| `SHA256SU0` | `vsha256su0q_u32(w)` | SHA256 schedule 上 |
| `SHA256SU1` | `vsha256su1q_u32(w, w2)` | SHA256 schedule 下 |

### 2.3 CRC32（v8.0+，头 `<arm_acle.h>`）

| 指令 | intrinsic | 多项式 |
|------|----------|-------|
| `CRC32B` | `__crc32cb(crc, (uint8_t)v))` ⚠️ **反了** | 见下 |
| - | `__crc32b(crc, (uint8_t)v)` | IEEE 802.3 (0xEDB88320) |
| `CRC32H` | `__crc32h(crc, (uint16_t)v)` | IEEE |
| `CRC32W` | `__crc32w(crc, (uint32_t)v)` | IEEE |
| `CRC32X` | `__crc32d(crc, (uint64_t)v)` | IEEE |
| `CRC32CB` | `__crc32cb(crc, (uint8_t)v)` | Castagnoli (0x82F63B78) |
| `CRC32CH` | `__crc32ch(crc, (uint16_t)v)` | Castagnoli |
| `CRC32CW` | `__crc32cw(crc, (uint32_t)v)` | Castagnoli |
| `CRC32CX` | `__crc32cd(crc, (uint64_t)v)` | Castagnoli |

> **注意**：`__crc32{b,h,w,d}` 是 IEEE，`__crc32c{b,h,w,d}` 是 Castagnoli。
> 不要和汇编 `CRC32*` vs `CRC32C*` 混淆，ACLE 命名较随意。

### 2.4 LSE 原子（v8.1，可用 `<stdatomic.h>` 或 GCC `__atomic_*`）

LSE 通常用 GCC `__atomic_*` 内建（GCC 8+ 在 `-march=armv8.1-a+lse` 下自动用 LSE 指令）：

```c
__atomic_add_fetch(p, 1, __ATOMIC_ACQ_REL);       // → LDADDAL
__atomic_fetch_add(p, 1, __ATOMIC_RELAXED);       // → LDADD
__atomic_compare_exchange_n(p, &expected, desired, false, __ATOMIC_ACQ_REL, __ATOMIC_RELAXED); // → CASAL
__atomic_exchange_n(p, desired, __ATOMIC_ACQ_REL); // → SWPAL
```

直接内联汇编：
```c
static inline int ldaddl(int v, int *p) {
    int old;
    asm volatile("ldaddl %w[v], %w[o], [%[p]]"
                 : [o] "=r"(old) : [v] "r"(v), [p] "r"(p) : "memory");
    return old;
}
```

`<arm_acle.h>` 中没有 LSE intrinsic（用 GCC 内建替代）。

### 2.5 FP16（v8.2 FHP+ASIMDHP）

把 NEON base 的 `f32` 后缀换成 `f16` 即可，例：

| 指令 | intrinsic |
|------|----------|
| `FMLA (fp16)` | `vfmaq_f16(acc, a, b)` |
| `FADD (fp16)` | `vaddq_f16(a, b)` |
| `FMUL (fp16, by element)` | `vmulq_lane_f16(a, b, 0)` |
| `FCVT (fp16↔fp32)` | `vcvt_f32_f16(v_4xfp16)`, `vcvt_high_f16_f32(v_4xfp32)`, `vcvtb_f16_f32`, `vcvtt_f16_f32` |
| `FMAXV/MINV (fp16)` | `vmaxvq_f16(v)`, `vminvq_f16(v)` |

**标量 fp16**：
```c
__fp16 a = 1.5f16;          // GCC __fp16 类型
_Float16 b = 2.0f16;        // C 标准 _Float16 (GCC 12+)
```

### 2.6 LSE 详细矩阵（55 条 → 9 个原子操作 × 4 种尺寸 × 内存序后缀）

| 操作 | intrinsic (32-bit) | intrinsic (64-bit) |
|------|-------------------|-------------------|
| ADD | `__atomic_fetch_add` | 同上 (用 long) |
| SWP | `__atomic_exchange_n` | 同上 |
| CAS | `__atomic_compare_exchange_n` | 同上 |
| CLR (and-not) | `__atomic_fetch_and(~v)` | 同上 |
| SET (or) | `__atomic_fetch_or(v)` | 同上 |
| EOR (xor) | `__atomic_fetch_xor(v)` | 同上 |
| SMAX | `__atomic_fetch_max` (C23) | 同上 |
| SMIN | `__atomic_fetch_min` (C23) | 同上 |
| UMAX | (需内联汇编) | - |
| UMIN | (需内联汇编) | - |

子字原子（B/H）：用 `__atomic_*` 的 short/char 重载。

### 2.7 RDM (SQRDMLAH/SH, v8.1)

| 指令 | intrinsic |
|------|----------|
| `SQRDMLAH (vector)` | `vqrdmlahq_s32(acc, a, b)` |
| `SQRDMLAH (by element)` | `vqrdmlahq_lane_s32(acc, a, b, 0)` |
| `SQRDMLSH (vector)` | `vqrdmlshq_s32(acc, a, b)` |
| `SQRDMLSH (by element)` | `vqrdmlshq_lane_s32(acc, a, b, 0)` |

### 2.8 FCMA (FCMLA/FCADD, v8.3)

| 指令 | intrinsic |
|------|----------|
| `FCMLA (vector, #0)` | `vcmlaq_f32(acc, a, b, 0)` |
| `FCMLA (vector, #90)` | `vcmlaq_rot90_f32(acc, a, b)` |
| `FCMLA (vector, #180)` | `vcmlaq_rot180_f32(acc, a, b)` |
| `FCMLA (vector, #270)` | `vcmlaq_rot270_f32(acc, a, b)` |
| `FCMLA (by element)` | `vcmlaq_lane_f32(acc, a, b, 0)` 等 |
| `FCADD (#90)` | `vcaddq_rot90_f32(acc, a, b)` |
| `FCADD (#270)` | `vcaddq_rot270_f32(acc, a, b)` |

### 2.9 UDOT/SDOT (DotProd, v8.4)

| 指令 | intrinsic |
|------|----------|
| `UDOT (vector)` | `vdotq_u32(acc, a_u8x16, b_u8x16)` (GCC 9+) |
| `UDOT (by element)` | `vdotq_lane_u32(acc, a, b, 0)` |
| `SDOT (vector)` | `vdotq_s32(acc, a_s8x16, b_s8x16)` |
| `SDOT (by element)` | `vdotq_lane_s32(acc, a, b, 0)` |

### 2.10 SHA3 (v8.4)

| 指令 | intrinsic |
|------|----------|
| `EOR3` | `veor3q_u8(a, b, c)` |
| `BCAX` | `vbcaxq_u8(a, b, c)` |
| `XAR` | `vxarq_u8(a, b, 41)` |
| `RAX1` | `vrax1q_u64(a, b)` |

### 2.11 SHA512 (v8.4)

| 指令 | intrinsic |
|------|----------|
| `SHA512H` | `vsha512hq_u64(acc, acc2, w)` |
| `SHA512H2` | `vsha512h2q_u64(acc, acc2, w)` |
| `SHA512SU0` | `vsha512su0q_u64(w)` |
| `SHA512SU1` | `vsha512su1q_u64(w, w2)` |

### 2.12 SM3 (v8.4 国密)

| 指令 | intrinsic |
|------|----------|
| `SM3SS1` | `vsm3ss1q_u32(a, b, c, d)` |
| `SM3PARTW1` | `vsm3partw1q_u32(a, b, c)` |
| `SM3PARTW2` | `vsm3partw2q_u32(a, b, c)` |
| `SM3TT1A` | `vsm3tt1aq_u32(a, b, c, 0)` |
| `SM3TT1B` | `vsm3tt1bq_u32(a, b, c, 0)` |
| `SM3TT2A` | `vsm3tt2aq_u32(a, b, c, 0)` |
| `SM3TT2B` | `vsm3tt2bq_u32(a, b, c, 0)` |

### 2.13 SM4 (v8.4 国密)

| 指令 | intrinsic |
|------|----------|
| `SM4E` | `vsm4eq_u32(v, k)` (4 rounds 并行) |
| `SM4EKEY` | `vsm4ekeyq_u32(v, k)` |

### 2.14 LRCPC v1 (LDAPR, v8.1)

GCC/LLVM 自动用 LDAPR 替代 LDAR，无显式 intrinsic。

### 2.15 LRCPC v2 (LDAPUR/STLUR, v8.3)

GCC/LLVM 自动用 LDAPUR/STLUR，无显式 intrinsic。

### 2.16 PAuth (v8.3)

| 指令 | intrinsic (`<arm_acle.h>`) |
|------|----------|
| `PACIA` | `__pacia(x, modifier)` |
| `PACIB` | `__pacib(x, modifier)` |
| `PACDA` | `__pacda(x, modifier)` |
| `PACDB` | `__pacdb(x, modifier)` |
| `AUTIA` | `__autia(x, modifier)` |
| `XPAC` | `__xpaci(x)` / `__xpacd(x)` |

### 2.17 JSConv (FJCVTZS, v8.3)

| 指令 | intrinsic |
|------|----------|
| `FJCVTZS` | `__vjcvtzs_s64_to_s32(double x)` 或直接 `vcvt_s32_f64` 时编译器自动选 |

### 2.18 v8.5+ (BTI/MTE/FlagM/FRINTTS) — 飞腾 D3000 不支持

略，详见 [`v8.5_misc.md`](./v8.5_misc.md)。

---

## 3. 常见代码模式 → Intrinsic 速查

### 3.1 4×4 fp32 矩阵乘（GEMM 核心）

```c
#include <arm_neon.h>
void gemm_4x4(const float *A, const float *B, float *C) {
    float32x4 a0 = vld1q_f32(A), a1 = vld1q_f32(A+4),
              a2 = vld1q_f32(A+8), a3 = vld1q_f32(A+12);
    for (int i = 0; i < 4; i++) {
        float32x4 b = vld1q_f32(B + i*4);
        float32x4 c0 = vld1q_f32(C + i*4);
        c0 = vfmaq_lane_f32(c0, a0, vget_low_f32(b),  0);
        c0 = vfmaq_lane_f32(c0, a1, vget_low_f32(b),  1);
        c0 = vfmaq_lane_f32(c0, a2, vget_high_f32(b), 0);
        c0 = vfmaq_lane_f32(c0, a3, vget_high_f32(b), 1);
        vst1q_f32(C + i*4, c0);
    }
}
```

### 3.2 AES-128 单 block 加密

```c
#include <arm_neon.h>
uint8x16_t aes128_enc_block(uint8x16_t in, const uint8x16_t round_keys[11]) {
    uint8x16_t state = in;
    for (int i = 0; i < 9; i++) {
        state = vaeseq_u8(state, round_keys[i]);  // 一轮完整
        state = vaesmcq_u8(state);                 // MixColumns
    }
    state = vaeseq_u8(state, round_keys[9]);       // 第 10 轮：只 SubBytes/ShiftRows/AddKey
    return veorq_u8(state, round_keys[10]);         // 末轮无 MixColumns，XOR 末密钥
}
```

### 3.3 int8 量化点积（UDOT）

```c
#include <arm_neon.h>
int32x4_t quantized_dot(const int8_t *a, const int8_t *b, int n) {
    int32x4_t acc = vdupq_n_s32(0);
    for (int i = 0; i < n; i += 16) {
        int8x16_t va = vld1q_s8(a + i);
        int8x16_t vb = vld1q_s8(b + i);
        acc = vdotq_s32(acc, va, vb);  // 4×int8 → int32 × 4 lane
    }
    return acc;
}
```

### 3.4 fp16 GEMM（v8.2）

```c
#include <arm_neon.h>
void fp16_dot8(const __fp16 *a, const __fp16 *b, __fp16 *out) {
    float16x8_t va = vld1q_f16(a);
    float16x8_t vb = vld1q_f16(b);
    float16x8_t acc = vmulq_f16(va, vb);     // 8 路 fp16 乘
    *out = vaddvq_f16(acc);                  // 横向加（fp16 → fp16 标量）
}
```

### 3.5 复数乘累加（FCMLA, v8.3）

```c
#include <arm_neon.h>
// 4 个复数并行：lane (re, im) 交错
float32x4_t cmul_4complex(float32x4_t a, float32x4_t b) {
    float32x4_t real = vdupq_n_f32(0.0f);
    float32x4_t imag = vdupq_n_f32(0.0f);
    real = vcmlaq_f32(real, a, b, 0);        // real += a.re*b.re - a.im*b.im
    imag = vcmlaq_rot90_f32(imag, a, b);     // imag += a.re*b.im + a.im*b.re
    // 拼接 real + i*imag：实际上 FCMLA #0/#90 已经把实虚部分别放对位置
    return real;  // 简化，实际需要重新打包
}
```

### 3.6 LSE 原子计数器

```c
#include <stdatomic.h>
atomic_int counter = 0;
int old = atomic_fetch_add_explicit(&counter, 1, memory_order_relaxed);  // LDADD
// 或显式
atomic_int expected = 5, desired = 10;
atomic_compare_exchange_strong_explicit(&counter, &expected, desired,
    memory_order_acq_rel, memory_order_acquire);  // CASAL
```

### 3.7 国密 SM4 单块加密（v8.4）

```c
#include <arm_neon.h>
uint32x4_t sm4_encrypt_block(uint32x4_t x, const uint32x4_t rk[8]) {
    // SM4E 一条指令算 4 round，32 round 共 8 次 SM4E
    for (int i = 0; i < 8; i++) {
        x = vsm4eq_u32(x, rk[i]);
    }
    // 末尾 swap endian (SM4 标准)
    return vrev64q_u32(x);  // 简化
}
```

---

## 4. 编译期调试：看 intrinsic 生成了什么指令

```bash
# 方法 1：直接看汇编
gcc -O3 -S -mcpu=ftc86x test.c -o test.s
grep -E '(fmla|udot|vaese|ldadd|sm3ss1|fcmla)' test.s

# 方法 2：objdump
gcc -O3 -mcpu=ftc86x test.c -o test
objdump -d test | grep -A 1 '<my_func>'

# 方法 3：LLVM-MCA 静态调度分析
llvm-mca -mcpu=cortex-a76 test.s  # 飞腾 D3000 用最接近的 cortex-a76/cortex-x2 模型
```

---

## 5. 参考

- ARM C Language Extensions (ACLE) Specification v3.0: https://developer.arm.com/documentation/101028/0000
- ARM NEON Intrinsic Reference: https://developer.arm.com/architectures/instruction-sets/instruction-sets/neon-intrinsics
- GCC ARM intrinsics: https://gcc.gnu.org/onlinedocs/gcc/ARM-NEON-Intrinsics.html
- LLVM ARM NEON: https://llvm.org/docs/LangRef.html#arm-neon-intrinsics
- 飞腾 PhyGCC 文档（供应商提供）

---

📌 **下一步**：回到 [`isa_reference/README.md`](./README.md)。
