/*
Adapted from https://github.com/mit-han-lab/llm-awq
Modified from NVIDIA FasterTransformer:
https://github.com/NVIDIA/FasterTransformer/blob/main/src/fastertransformer/cutlass_extensions/include/cutlass_extensions/interleaved_numeric_conversion.h
@article{lin2023awq,
  title={AWQ: Activation-aware Weight Quantization for LLM Compression and
Acceleration}, author={Lin, Ji and Tang, Jiaming and Tang, Haotian and Yang,
Shang and Dang, Xingyu and Han, Song}, journal={arXiv}, year={2023}
}
*/

#pragma once

/*
BOTTOM_MASK
0x0X | 0x6400 => 0x640X
0x6400 | 0x03 = 0x6403 = 0110 0100 0000 0011
指数位为10, 尾数位为 1.0000 0000 11 => 10 0000 0011 = 1027
1024 + X = 1027 -> X = 1027 - 1024 = 3
X = (h - 1024)

TOP_MASK
0x6400 | 0xX0 => 0x64X0
0x6400 | 0x30 = 0x6430 = 0110 0100 0011 0000
h * 1/16 => 指数位为6， 尾数位为 1.00 0011 0000 => 0100 0011 = 67
X = (h * 1/16 - 64) = 3
*/

namespace vllm {
namespace awq {

__forceinline__ __device__ uint4 dequantize_s4_to_fp16x2_neg(uint32_t const& source) {
  uint4 result;

  uint32_t* h = reinterpret_cast<uint32_t*>(&result);
  uint32_t const i4s = reinterpret_cast<uint32_t const&>(source);

  static constexpr uint32_t BOTTOM_MASK = 0xff0fff0f;
  static constexpr uint32_t TOP_MASK = 0xfff0fff0;
  static constexpr uint32_t I4s_TO_F16s_MAGIC_NUM = 0xE400E400;
  static constexpr uint32_t mask_for_elt_02 = 0x07020500;
  static constexpr uint32_t mask_for_elt_13 = 0x07030501;

  // i4s: wzyx wzyx
  // elt_02: 0xE4yxE4yx
  auto elt_02 = __builtin_amdgcn_perm(I4s_TO_F16s_MAGIC_NUM, i4s,  mask_for_elt_02);
  // elt_13: 0xE4wzE4wz
  auto elt_13 = __builtin_amdgcn_perm(I4s_TO_F16s_MAGIC_NUM, i4s,  mask_for_elt_13);
  // {0xE40X, 0xE40X}
  h[0] = elt_02 & BOTTOM_MASK;
  // {0xE4Y0, 0xE4Y0}
  h[1] = elt_02 & TOP_MASK;
  // {0xE40Z, 0xE40Z}
  h[2] = elt_13 & BOTTOM_MASK;
  // {0xE4W0, 0xE4W0}
  h[3] = elt_13 & TOP_MASK;

  // half2{-x, -x} + {1024, 1024}
  static constexpr uint32_t FP16_TOP_MAGIC_NUM = 0x64006400;
  // half2{-y, -y} * {1/16, 1/16} + {64, 64}
  static constexpr uint32_t ONE_SIXTEENTH = 0x2c002c00;
  static constexpr uint32_t FP16_64 = 0x54005400;

  // h[0] = h[0] + half2{1024, 1024}
  asm volatile("v_pk_add_f16 %0, %1, %2;\n"
               : "=v"(h[0])
               : "v"(h[0]), "v"(FP16_TOP_MAGIC_NUM));
  // h[1] = fma(h[1], half2{1/16, 1/16}, half2{64, 64})
  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(h[1])
               : "v"(h[1]), "v"(ONE_SIXTEENTH), "v"(FP16_64));

  // h[2] = h[2] + half2{1024, 1024}
  asm volatile("v_pk_add_f16 %0, %1, %2;\n"
               : "=v"(h[2])
               : "v"(h[2]), "v"(FP16_TOP_MAGIC_NUM));
  // h[3] = fma(h[3], half2{1/16, 1/16}, half2{64, 64})
  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(h[3])
               : "v"(h[3]), "v"(ONE_SIXTEENTH), "v"(FP16_64));
  return result;
}

__forceinline__ __device__ uint4 dequantize_s4_to_fp16x2(uint32_t const& source) {
#if (defined(__CUDA_ARCH__) && __CUDA_ARCH__ < 750) && !defined(USE_ROCM)
  assert(false);
#elif defined(USE_ROCM)
  uint4 result;

  uint32_t* h = reinterpret_cast<uint32_t*>(&result);
  uint32_t const i4s = reinterpret_cast<uint32_t const&>(source);

  static constexpr uint32_t BOTTOM_MASK = 0xff0fff0f;
  static constexpr uint32_t TOP_MASK = 0xfff0fff0;
  static constexpr uint32_t I4s_TO_F16s_MAGIC_NUM = 0x64006400;
  static constexpr uint32_t mask_for_elt_02 = 0x07020500;
  static constexpr uint32_t mask_for_elt_13 = 0x07030501;

  // i4s: wzyx wzyx
  // elt_02: 0x64yx64yx
  auto elt_02 = __builtin_amdgcn_perm(I4s_TO_F16s_MAGIC_NUM, i4s,  mask_for_elt_02);
  // elt_13: 0x64wz64wz
  auto elt_13 = __builtin_amdgcn_perm(I4s_TO_F16s_MAGIC_NUM, i4s,  mask_for_elt_13);
  // {0x640X, 0x640X}
  h[0] = elt_02 & BOTTOM_MASK;
  // {0x64Y0, 0x64Y0}
  h[1] = elt_02 & TOP_MASK;
  // {0x640Z, 0x640Z}
  h[2] = elt_13 & BOTTOM_MASK;
  // {0x64W0, 0x64W0}
  h[3] = elt_13 & TOP_MASK;

  // NEG_FP16_TOP_MAGIC_NUM: half2{-1024, -1024}
  // half2{x, x} + {-1024, -1024}
  static constexpr uint32_t NEG_FP16_TOP_MAGIC_NUM = 0xE400E400;
  // half2{y, y} * {1/16, 1/16} + {-64, -64}
  static constexpr uint32_t ONE_SIXTEENTH = 0x2c002c00;
  static constexpr uint32_t NEG_64 = 0xd400d400;

  // h[0] = h[0] + half2{-1024, -1024}
  asm volatile("v_pk_add_f16 %0, %1, %2;\n"
               : "=v"(h[0])
               : "v"(h[0]), "v"(NEG_FP16_TOP_MAGIC_NUM));
  // h[1] = fma(h[1], half2{1/16, 1/16}, half2{-64, -64})
  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(h[1])
               : "v"(h[1]), "v"(ONE_SIXTEENTH), "v"(NEG_64));

  // h[2] = h[2] + half2{-1024, -1024}
  asm volatile("v_pk_add_f16 %0, %1, %2;\n"
               : "=v"(h[2])
               : "v"(h[2]), "v"(NEG_FP16_TOP_MAGIC_NUM));
  // h[3] = fma(h[3], half2{1/16, 1/16}, half2{-64, -64})
  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(h[3])
               : "v"(h[3]), "v"(ONE_SIXTEENTH), "v"(NEG_64));
  return result;
#else
  uint4 result;

  uint32_t* h = reinterpret_cast<uint32_t*>(&result);
  uint32_t const i4s = reinterpret_cast<uint32_t const&>(source);

  // First, we extract the i4s and construct an intermediate fp16 number.
  static constexpr uint32_t immLut = (0xf0 & 0xcc) | 0xaa;
  static constexpr uint32_t BOTTOM_MASK = 0x000f000f;
  static constexpr uint32_t TOP_MASK = 0x00f000f0;
  static constexpr uint32_t I4s_TO_F16s_MAGIC_NUM = 0x64006400;

  // Note that the entire sequence only requires 1 shift instruction. This is
  // thanks to the register packing format and the fact that we force our
  // integers to be unsigned, and account for this in the fp16 subtractions. In
  // addition, I exploit the fact that sub and fma have the same throughput in
  // order to convert elt_23 and elt_67 to fp16 without having to shift them to
  // the bottom bits before hand.

  // Shift right by 8 to now consider elt_45 and elt_67. Issue first to hide RAW
  // dependency if we issue immediately before required.
  const uint32_t top_i4s = i4s >> 8;
  // Extract elt_01 - (i4s & 0x000f000f) | 0x64006400
  asm volatile("lop3.b32 %0, %1, %2, %3, %4;\n"
               : "=r"(h[0])
               : "r"(i4s), "n"(BOTTOM_MASK), "n"(I4s_TO_F16s_MAGIC_NUM),
                 "n"(immLut));
  // Extract elt_23 (i4s & 0x00f000f0) | 0x64006400
  asm volatile("lop3.b32 %0, %1, %2, %3, %4;\n"
               : "=r"(h[1])
               : "r"(i4s), "n"(TOP_MASK), "n"(I4s_TO_F16s_MAGIC_NUM),
                 "n"(immLut));
  // Extract elt_45 (top_i4s & 0x000f000f) | 0x64006400
  asm volatile("lop3.b32 %0, %1, %2, %3, %4;\n"
               : "=r"(h[2])
               : "r"(top_i4s), "n"(BOTTOM_MASK), "n"(I4s_TO_F16s_MAGIC_NUM),
                 "n"(immLut));
  // Extract elt_67 (top_i4s & 0x00f000f0) | 0x64006400
  asm volatile("lop3.b32 %0, %1, %2, %3, %4;\n"
               : "=r"(h[3])
               : "r"(top_i4s), "n"(TOP_MASK), "n"(I4s_TO_F16s_MAGIC_NUM),
                 "n"(immLut));

  // I use inline PTX below because I am not sure if the compiler will emit
  // float2half instructions if I use the half2 ctor. In this case, I chose
  // performance reliability over code readability.

  // This is the half2 {1032, 1032} represented as an integer.
  // static constexpr uint32_t FP16_TOP_MAGIC_NUM = 0x64086408;
  // Haotian: subtract {1024, 1024} instead, we do not need to map to [-8, 7]
  static constexpr uint32_t FP16_TOP_MAGIC_NUM = 0x64006400;
  // This is the half2 {1 / 16, 1 / 16} represented as an integer.
  static constexpr uint32_t ONE_SIXTEENTH = 0x2c002c00;
  // This is the half2 {-72, -72} represented as an integer.
  // static constexpr uint32_t NEG_72 = 0xd480d480;
  // Haotian: Let's use {-64, -64}.
  static constexpr uint32_t NEG_64 = 0xd400d400;

  // Finally, we construct the output numbers.
  // Convert elt_01
  asm volatile("sub.f16x2 %0, %1, %2;\n"
               : "=r"(h[0])
               : "r"(h[0]), "r"(FP16_TOP_MAGIC_NUM));
  // Convert elt_23
  asm volatile("fma.rn.f16x2 %0, %1, %2, %3;\n"
               : "=r"(h[1])
               : "r"(h[1]), "r"(ONE_SIXTEENTH), "r"(NEG_64));
  // Convert elt_45
  asm volatile("sub.f16x2 %0, %1, %2;\n"
               : "=r"(h[2])
               : "r"(h[2]), "r"(FP16_TOP_MAGIC_NUM));
  // Convert elt_67
  asm volatile("fma.rn.f16x2 %0, %1, %2, %3;\n"
               : "=r"(h[3])
               : "r"(h[3]), "r"(ONE_SIXTEENTH), "r"(NEG_64));

  return result;
#endif
  __builtin_unreachable();  // Suppress missing return statement warning
}

}  // namespace awq
}  // namespace vllm
