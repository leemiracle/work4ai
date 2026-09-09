#pragma once

#include "dequantize.cuh"
#include <cute/tensor.hpp>

#define WARP_SIZE 64
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))

#define TILE_K_SWITCH(TILE_K, CONST_NAME, ...) \
  [&] {                                        \
    if (TILE_K == 32) {                        \
      constexpr static int CONST_NAME = 32;    \
      return __VA_ARGS__();                    \
    } else if (TILE_K == 64) {                 \
      constexpr static int CONST_NAME = 64;    \
      return __VA_ARGS__();                    \
    }                                          \
  }()

#define BOOL_SWITCH(FLAG, CONST_NAME, ...)      \
  [&] {                                         \
    if (FLAG) {                                 \
      constexpr static bool CONST_NAME = true;  \
      return __VA_ARGS__();                     \
    } else {                                    \
      constexpr static bool CONST_NAME = false; \
      return __VA_ARGS__();                     \
    }                                           \
  }()

using namespace cute;
using mma_op = DCU_16x16x16_F32F16F16F32_NT;
using mma_traits = MMA_Traits<mma_op>;
using mma_atom = MMA_Atom<mma_traits>;

namespace vllm {
namespace awq {

__forceinline__ __device__ void block_sync_lds() {
  asm volatile(
      "\
  s_waitcnt lgkmcnt(0) \n \
  s_barrier \
  " ::);
}

__forceinline__ __device__ void block_sync() { asm volatile("s_barrier" ::); }

typedef __fp16 fp16v4 __attribute__((__vector_size__(4 * sizeof(__fp16))));

__forceinline__ __device__ fp16v4 add(fp16v4& a, fp16v4& b) {
  fp16v4 c;

  half2* a_data = reinterpret_cast<half2*>(&a);
  half2* b_data = reinterpret_cast<half2*>(&b);
  half2* c_data = reinterpret_cast<half2*>(&c);
  c_data[0] = a_data[0] + b_data[0];
  c_data[1] = a_data[1] + b_data[1];

  return c;
}

__forceinline__ __device__ void atomicAdd(fp16v4* address, fp16v4& val) {
  unsigned long* base_address = reinterpret_cast<unsigned long*>(address);
  unsigned long old = *base_address, assumed;
  do {
    assumed = old;
    unsigned long compare = assumed;
    fp16v4 new_val = add(*reinterpret_cast<fp16v4*>(&assumed), val);

#if __has_builtin(__hip_atomic_compare_exchange_strong)
    __hip_atomic_compare_exchange_strong(
        base_address, &compare, *reinterpret_cast<unsigned long*>(&new_val),
        __ATOMIC_RELAXED, __ATOMIC_RELAXED, __HIP_MEMORY_SCOPE_AGENT);
#else
    __atomic_compare_exchange_n(base_address, &compare,
                                *reinterpret_cast<unsigned long*>(&new_val),
                                false, __ATOMIC_RELAXED, __ATOMIC_RELAXED);
#endif
    old = compare;
  } while (assumed != old);
}

__forceinline__ __device__ uint4
dequantize_weight(const uint32_t B_loaded,
                  const uint4 B_loaded_zero_neg,  // neg B_loaded_zero;
                  const uint4 B_loaded_scale) {
  static constexpr uint32_t ZERO = 0x0;
  uint4 B_loaded_fp16 = dequantize_s4_to_fp16x2(B_loaded);

  // half2{x} = half2{x} - half2{zero}
  asm volatile("v_pk_add_f16 %0, %1, %2;\n"
               : "=v"(B_loaded_fp16.x)
               : "v"(B_loaded_fp16.x), "v"(B_loaded_zero_neg.x));
  // half2{x} = fma(half2{x}, half2{scale}, zero)
  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(B_loaded_fp16.x)
               : "v"(B_loaded_fp16.x), "v"(B_loaded_scale.x), "v"(ZERO));

  // half2{x} = half2{x} - half2{zero}
  asm volatile("v_pk_add_f16 %0, %1, %2;\n"
               : "=v"(B_loaded_fp16.y)
               : "v"(B_loaded_fp16.y), "v"(B_loaded_zero_neg.y));
  // half2{x} = fma(half2{x}, half2{scale}, zero)
  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(B_loaded_fp16.y)
               : "v"(B_loaded_fp16.y), "v"(B_loaded_scale.y), "v"(ZERO));

  // half2{x} = half2{x} - half2{zero}
  asm volatile("v_pk_add_f16 %0, %1, %2;\n"
               : "=v"(B_loaded_fp16.z)
               : "v"(B_loaded_fp16.z), "v"(B_loaded_zero_neg.z));
  // half2{x} = fma(half2{x}, half2{scale}, zero)
  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(B_loaded_fp16.z)
               : "v"(B_loaded_fp16.z), "v"(B_loaded_scale.z), "v"(ZERO));

  // half2{x} = half2{x} - half2{zero}
  asm volatile("v_pk_add_f16 %0, %1, %2;\n"
               : "=v"(B_loaded_fp16.w)
               : "v"(B_loaded_fp16.w), "v"(B_loaded_zero_neg.w));
  // half2{x} = fma(half2{x}, half2{scale}, zero)
  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(B_loaded_fp16.w)
               : "v"(B_loaded_fp16.w), "v"(B_loaded_scale.w), "v"(ZERO));

  return B_loaded_fp16;
}

__forceinline__ __device__ uint4 dequantize_weight_v2(
    const uint32_t B_loaded,
    const uint4 B_loaded_zero_with_scale_neg,  // neg B_loaded_zero;
    const uint4 B_loaded_scale) {
  uint4 B_loaded_fp16 = dequantize_s4_to_fp16x2(B_loaded);

  // half2{x} = fma(half2{x}, half2{scale}, zero)
  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(B_loaded_fp16.x)
               : "v"(B_loaded_fp16.x), "v"(B_loaded_scale.x),
                 "v"(B_loaded_zero_with_scale_neg.x));

  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(B_loaded_fp16.y)
               : "v"(B_loaded_fp16.y), "v"(B_loaded_scale.y),
                 "v"(B_loaded_zero_with_scale_neg.y));

  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(B_loaded_fp16.z)
               : "v"(B_loaded_fp16.z), "v"(B_loaded_scale.z),
                 "v"(B_loaded_zero_with_scale_neg.z));

  asm volatile("v_pk_fma_f16 %0, %1, %2, %3;\n"
               : "=v"(B_loaded_fp16.w)
               : "v"(B_loaded_fp16.w), "v"(B_loaded_scale.w),
                 "v"(B_loaded_zero_with_scale_neg.w));
  return B_loaded_fp16;
}

__forceinline__ __device__ void zeros_with_scales(
    uint4& B_loaded_zero_neg,  // neg B_loaded_zero;
    const uint4 B_loaded_scale) {
  asm volatile("v_pk_mul_f16 %0, %1, %2;\n"
               : "=v"(B_loaded_zero_neg.x)
               : "v"(B_loaded_zero_neg.x), "v"(B_loaded_scale.x));

  asm volatile("v_pk_mul_f16 %0, %1, %2;\n"
               : "=v"(B_loaded_zero_neg.y)
               : "v"(B_loaded_zero_neg.y), "v"(B_loaded_scale.y));

  asm volatile("v_pk_mul_f16 %0, %1, %2;\n"
               : "=v"(B_loaded_zero_neg.z)
               : "v"(B_loaded_zero_neg.z), "v"(B_loaded_scale.z));

  asm volatile("v_pk_mul_f16 %0, %1, %2;\n"
               : "=v"(B_loaded_zero_neg.w)
               : "v"(B_loaded_zero_neg.w), "v"(B_loaded_scale.w));
}

template <typename EngineQ, typename LayoutQ, typename EngineD,
          typename LayoutD>
__forceinline__ __device__ void dequantize_tensor(
    Tensor<EngineQ, LayoutQ> const& q_tensor,
    Tensor<EngineD, LayoutD>& d_tensor, const uint4* scaling_factors,
    const uint4* dequantized_zeros_neg, const int QB_cpy_col,
    uint4& th_scaling_factors, uint4& th_loaded_zeros_neg,
    bool& need_store_scales_zeros) {
  // static_assert(size<2>(q_tensor) == 1);
  if (need_store_scales_zeros) {
    th_scaling_factors = scaling_factors[QB_cpy_col];
    th_loaded_zeros_neg = dequantized_zeros_neg[QB_cpy_col];
    // zeros_with_scales(th_loaded_zeros_neg, th_scaling_factors);
    need_store_scales_zeros = false;
  }

#pragma unroll
  for (int k = 0; k < size<1>(q_tensor); k++) {
    uint32_t B_loaded = (uint32_t)(q_tensor(0, k, 0));
    uint4 B_loaded_fp16 =
        dequantize_weight_v2(B_loaded, th_loaded_zeros_neg, th_scaling_factors);
    *reinterpret_cast<uint4*>(d_tensor(_, k, 0).data().ptr_) = B_loaded_fp16;
  }
}

template <typename TiledMMA, typename SmemTiledCopyA, typename SmemTiledCopyB,
          typename EngineAs, typename LayoutAs, typename EngineAr,
          typename LayoutAr, typename EngineBs, typename LayoutBs,
          typename EngineBr, typename LayoutBr, typename EngineC,
          typename LayoutC>
__forceinline__ __device__ void gemm(
    TiledMMA const& tiled_mma, SmemTiledCopyA const& smem_tiled_copy_A,
    SmemTiledCopyB const& smem_tiled_copy_B,
    Tensor<EngineAs, LayoutAs> const& tensor_a_s,
    Tensor<EngineAr, LayoutAr>& tensor_a_r,
    Tensor<EngineBs, LayoutBs> const& tensor_b_s,
    Tensor<EngineBr, LayoutBr>& tensor_b_r,
    Tensor<EngineC, LayoutC>& tensor_c) {
  cute::copy(smem_tiled_copy_A, tensor_a_s(_, _, 0), tensor_a_r(_, _, 0));
  cute::copy(smem_tiled_copy_B, tensor_b_s(_, _, 0), tensor_b_r(_, _, 0));

#pragma unroll
  for (int k = 0; k < size<2>(tensor_a_s); ++k) {
    if (k < size<2>(tensor_a_s) - 1) {
      cute::copy(smem_tiled_copy_A, tensor_a_s(_, _, k + 1),
                 tensor_a_r(_, _, (k + 1) & 1));
      cute::copy(smem_tiled_copy_B, tensor_b_s(_, _, k + 1),
                 tensor_b_r(_, _, (k + 1) & 1));
    }
    // __builtin_amdgcn_sched_barrier(0);
    cute::gemm(tiled_mma, tensor_a_r(_, _, k & 1), tensor_b_r(_, _, k & 1),
               tensor_c);
    // __builtin_amdgcn_sched_barrier(0);
  }
}

template <typename TiledMMA, typename SmemTiledCopyB, typename EngineAr,
          typename LayoutAr, typename EngineBs, typename LayoutBs,
          typename EngineBr, typename LayoutBr, typename EngineC,
          typename LayoutC>
__forceinline__ __device__ void gemm(
    TiledMMA const& tiled_mma, SmemTiledCopyB const& smem_tiled_copy_B,
    Tensor<EngineAr, LayoutAr> const& tensor_a_r,
    Tensor<EngineBs, LayoutBs> const& tensor_b_s,
    Tensor<EngineBr, LayoutBr>& tensor_b_r,
    Tensor<EngineC, LayoutC>& tensor_c) {
  cute::copy(smem_tiled_copy_B, tensor_b_s(_, _, 0), tensor_b_r(_, _, 0));

#pragma unroll
  for (int k = 0; k < size<2>(tensor_b_s); ++k) {
    if (k < size<2>(tensor_b_s) - 1) {
      cute::copy(smem_tiled_copy_B, tensor_b_s(_, _, k + 1),
                 tensor_b_r(_, _, (k + 1) & 1));
    }
    // __builtin_amdgcn_sched_barrier(0);
    cute::gemm(tiled_mma, tensor_a_r(_, _, k), tensor_b_r(_, _, k & 1),
               tensor_c);
    // __builtin_amdgcn_sched_barrier(0);
  }
}

template <bool is_even_M = true, typename GmemCopyAType, typename EngineAg,
          typename LayoutAg, typename EngineAr, typename LayoutAr,
          typename TensorP>
__forceinline__ __device__ void copy_A_global_to_register(
    Tensor<EngineAg, LayoutAg> const& tensor_src,
    Tensor<EngineAr, LayoutAr>& tensor_dst, TensorP const& tensor_p) {
#pragma unroll
  for (int m = 0; m < size<1>(tensor_src); ++m) {
    if constexpr (is_even_M) {  // even_M
#pragma unroll
      for (int n = 0; n < size<2>(tensor_src); ++n) {
        *reinterpret_cast<GmemCopyAType*>(tensor_dst(_, m, n).data()) =
            *reinterpret_cast<GmemCopyAType*>(tensor_src(_, m, n).data().ptr_);
      }
    } else {
      if (tensor_p(m)) {
#pragma unroll
        for (int n = 0; n < size<2>(tensor_src); ++n) {
          *reinterpret_cast<GmemCopyAType*>(tensor_dst(_, m, n).data()) =
              *reinterpret_cast<GmemCopyAType*>(
                  tensor_src(_, m, n).data().ptr_);
        }
      } else {
#pragma unroll
        for (int n = 0; n < size<2>(tensor_src); ++n) {
          *reinterpret_cast<GmemCopyAType*>(tensor_dst(_, m, n).data()) = 0;
        }
      }
    }
  }
}

template <bool is_even_M = true, typename EngineCg, typename LayoutCg,
          typename TensorP>
__forceinline__ __device__ void init_C_in_global(
    Tensor<EngineCg, LayoutCg>& tensor_dst, TensorP const& tensor_p) {
#pragma unroll
  for (int m = 0; m < size<1>(tensor_dst); ++m) {
    if constexpr (is_even_M) {  // even_M
#pragma unroll
      for (int n = 0; n < size<2>(tensor_dst); ++n) {
        *reinterpret_cast<uint32_t*>(tensor_dst(_, m, n).data().ptr_) = 0;
      }
    } else {
      if (tensor_p(m)) {
#pragma unroll
        for (int n = 0; n < size<2>(tensor_dst); ++n) {
          *reinterpret_cast<uint32_t*>(tensor_dst(_, m, n).data().ptr_) = 0;
        }
      }
    }
  }
}

template <bool is_even_M = true, typename EngineCg, typename LayoutCg,
          typename TensorP>
__forceinline__ __device__ void init_C_in_global_v2(
    Tensor<EngineCg, LayoutCg>& tensor_dst, TensorP const& tensor_p) {
#pragma unroll
  for (int m = 0; m < size<1>(tensor_dst); ++m) {
    if constexpr (is_even_M) {  // even_M
#pragma unroll
      for (int n = 0; n < size<2>(tensor_dst); ++n) {
        *reinterpret_cast<uint64_t*>(tensor_dst(_, m, n).data().ptr_) = 0;
      }
    } else {
      if (tensor_p(m)) {
#pragma unroll
        for (int n = 0; n < size<2>(tensor_dst); ++n) {
          *reinterpret_cast<uint64_t*>(tensor_dst(_, m, n).data().ptr_) = 0;
        }
      }
    }
  }
}

template <bool is_even_M = true, typename EngineCs, typename LayoutCs,
          typename EngineCg, typename LayoutCg, typename TensorP>
__forceinline__ __device__ void copy_C_shared_to_global(
    Tensor<EngineCs, LayoutCs> const& tensor_src,
    Tensor<EngineCg, LayoutCg>& tensor_dst, TensorP const& tensor_p) {
#pragma unroll
  for (int m = 0; m < size<1>(tensor_src); ++m) {
    if constexpr (is_even_M) {  // even_M
#pragma unroll
      for (int n = 0; n < size<2>(tensor_src); ++n) {
        *reinterpret_cast<uint32_t*>(tensor_dst(_, m, n).data().ptr_) =
            *reinterpret_cast<uint32_t*>(tensor_src(_, m, n).data().ptr_);
      }
    } else {
      if (tensor_p(m)) {
#pragma unroll
        for (int n = 0; n < size<2>(tensor_src); ++n) {
          *reinterpret_cast<uint32_t*>(tensor_dst(_, m, n).data().ptr_) =
              *reinterpret_cast<uint32_t*>(tensor_src(_, m, n).data().ptr_);
        }
      }
    }
  }
}

template <bool is_even_M = true, typename EngineCs, typename LayoutCs,
          typename EngineCg, typename LayoutCg, typename TensorP>
__forceinline__ __device__ void copy_C_shared_to_global_v2(
    Tensor<EngineCs, LayoutCs> const& tensor_src,
    Tensor<EngineCg, LayoutCg>& tensor_dst, TensorP const& tensor_p) {
#pragma unroll
  for (int m = 0; m < size<1>(tensor_src); ++m) {
    if constexpr (is_even_M) {  // even_M
#pragma unroll
      for (int n = 0; n < size<2>(tensor_src); ++n) {
        *reinterpret_cast<uint64_t*>(tensor_dst(_, m, n).data().ptr_) =
            *reinterpret_cast<uint64_t*>(tensor_src(_, m, n).data().ptr_);
      }
    } else {
      if (tensor_p(m)) {
#pragma unroll
        for (int n = 0; n < size<2>(tensor_src); ++n) {
          *reinterpret_cast<uint64_t*>(tensor_dst(_, m, n).data().ptr_) =
              *reinterpret_cast<uint64_t*>(tensor_src(_, m, n).data().ptr_);
        }
      }
    }
  }
}

template <bool is_even_M = true, typename EngineCs, typename LayoutCs,
          typename EngineCg, typename LayoutCg, typename TensorP>
__forceinline__ __device__ void copy_C_shared_to_global_atomic(
    Tensor<EngineCs, LayoutCs> const& tensor_src,
    Tensor<EngineCg, LayoutCg>& tensor_dst, TensorP const& tensor_p) {
#pragma unroll
  for (int m = 0; m < size<1>(tensor_src); ++m) {
    if constexpr (is_even_M) {  // even_M
#pragma unroll
      for (int n = 0; n < size<2>(tensor_src); ++n) {
        half2 src = *reinterpret_cast<half2*>(tensor_src(_, m, n).data().ptr_);
        half2* dst_ptr =
            reinterpret_cast<half2*>(tensor_dst(_, m, n).data().ptr_);
        atomicAdd(dst_ptr, src);
      }
    } else {
      if (tensor_p(m)) {
#pragma unroll
        for (int n = 0; n < size<2>(tensor_src); ++n) {
          half2 src =
              *reinterpret_cast<half2*>(tensor_src(_, m, n).data().ptr_);
          half2* dst_ptr =
              reinterpret_cast<half2*>(tensor_dst(_, m, n).data().ptr_);
          atomicAdd(dst_ptr, src);
        }
      }
    }
  }
}

template <bool is_even_M = true, typename EngineCs, typename LayoutCs,
          typename EngineCg, typename LayoutCg, typename TensorP>
__forceinline__ __device__ void copy_C_shared_to_global_atomic_v2(
    Tensor<EngineCs, LayoutCs> const& tensor_src,
    Tensor<EngineCg, LayoutCg>& tensor_dst, TensorP const& tensor_p) {
#pragma unroll
  for (int m = 0; m < size<1>(tensor_src); ++m) {
    if constexpr (is_even_M) {  // even_M
#pragma unroll
      for (int n = 0; n < size<2>(tensor_src); ++n) {
        fp16v4 src =
            *reinterpret_cast<fp16v4*>(tensor_src(_, m, n).data().ptr_);
        fp16v4* dst_ptr =
            reinterpret_cast<fp16v4*>(tensor_dst(_, m, n).data().ptr_);
        atomicAdd(dst_ptr, src);
      }
    } else {
      if (tensor_p(m)) {
#pragma unroll
        for (int n = 0; n < size<2>(tensor_src); ++n) {
          fp16v4 src =
              *reinterpret_cast<fp16v4*>(tensor_src(_, m, n).data().ptr_);
          fp16v4* dst_ptr =
              reinterpret_cast<fp16v4*>(tensor_dst(_, m, n).data().ptr_);
          atomicAdd(dst_ptr, src);
        }
      }
    }
  }
}

template <typename EngineBr, typename LayoutBr>
__forceinline__ __device__ void copy_B_shared_to_register(
    Tensor<EngineBr, LayoutBr>& tensor_b_r, const half* sB_ptr, const int idx,
    const int k) {
  typedef __fp16 fp16v8 __attribute__((__vector_size__(8 * sizeof(__fp16))));

  // static_assert(size<1>(tensor_b_r) == 1);

  // ds_read_m32x16: load 32x16 data from lds.
  constexpr int block_size = 32 * 16;
  // sB_ptr LayoutAtom: 32x16; N_major.
  // 32: means load 2 k idx one time.
  // 16: means load 1 n idx one time.
  constexpr int n_blocks = 4;  // 4 warps.
  constexpr int k_block_stride = n_blocks * block_size;
  const half* cur_sB_ptr = sB_ptr + k / 2 * k_block_stride;

  __fp16 __attribute__((address_space(3)))* s_ptr =
      (__fp16 __attribute__((address_space(3)))*)(cur_sB_ptr + 8 * idx);

  fp16v8 data = __builtin_amdgcn_ds_read_m32x16f16(s_ptr, 0);
  // fp16v4: (_, 0, 0); fp16v4: (_, 0, 1)
  *reinterpret_cast<fp16v8*>(tensor_b_r(_, 0, 0).data()) = data;
}

template <typename TiledMMA, typename EngineAr, typename LayoutAr,
          typename EngineBs, typename LayoutBs, typename EngineBr,
          typename LayoutBr, typename EngineC, typename LayoutC>
__forceinline__ __device__ void gemm(
    TiledMMA const& tiled_mma, Tensor<EngineAr, LayoutAr> const& tensor_a_r,
    Tensor<EngineBs, LayoutBs> const& tensor_b_s,
    Tensor<EngineBr, LayoutBr>& tensor_b_r, Tensor<EngineC, LayoutC>& tensor_c,
    const half* sB_ptr, const int idx) {
#pragma unroll
  for (int k = 0; k < size<2>(tensor_b_s); k += 2) {
    copy_B_shared_to_register(tensor_b_r, sB_ptr, idx, k);

    // __builtin_amdgcn_sched_barrier(0);
    cute::gemm(tiled_mma, tensor_a_r(_, _, k), tensor_b_r(_, _, 0), tensor_c);
    cute::gemm(tiled_mma, tensor_a_r(_, _, k + 1), tensor_b_r(_, _, 1),
               tensor_c);
    // __builtin_amdgcn_sched_barrier(0);
  }
}

}  // namespace awq
}  // namespace vllm