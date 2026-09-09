#include <torch/all.h>
#include <c10/cuda/CUDAGuard.h>

#include "dequantize.cuh"
#include "core/math.hpp"
#include "gemm_kernels_rocm_utils.cuh"
#include <cute/tensor.hpp>

#include <cuda_fp16.h>

namespace vllm {
namespace awq {

template <int m_warps, int n_warps, int tileM, int tileN, int tileK,
          typename SmemLayoutAtomA, typename GmemTiledCopyA,
          typename SmemLayoutAtomC, typename GmemTiledCopyC,
          typename GmemCopyAType = cute::uint64_t, int GmemCopyAThrLayoutX = 8,
          bool is_even_M = true>
__launch_bounds__(m_warps* n_warps* WARP_SIZE) __global__
    void gemm_forward_4bit_for_m64(
        half* __restrict__ A,                // [M, K]
        int* __restrict__ B,                 // [K, N // 8]
        half* __restrict__ scaling_factors,  // [K // G, N]
        int* __restrict__ zeros,             // [K // G, N // 8]
        half* __restrict__ C,                // [M, N]
        const int M, const int N, const int K, const int G, const int kSplits) {
  static_assert(tileM == 64);
  // use shared space to store A_tile and B_tile,
  // need shared mem: (tileM + tileN) * tileK * sizeof(half)
  // use shared space to store C_tile,
  // need shared mem: tileM * tileN * sizeof(half)
  __shared__ half smem_[MAX((tileM + tileN) * tileK, tileM * tileN)];

  using MMA = decltype(make_tiled_mma(
      mma_atom{}, make_layout(Shape<Int<m_warps>, Int<n_warps>, _1>{})));

  constexpr int num_threads = m_warps * n_warps * WARP_SIZE;
  const int idx = threadIdx.x;
  // const int warp_idx = idx >> 6;  // / 64
  // const int lane_idx = idx & 63;  // % 64
  const int n_tile = blockIdx.x;
  const int m_tile = blockIdx.y;
  const int k_split_idx = blockIdx.z;

  const int n_tiles = N / tileN;
  const int m_idx = m_tile * tileM;
  const int n_idx = n_tile * tileN;

  Tensor gC = make_tensor(make_gmem_ptr<half>(C + m_idx * N + n_idx),
                          Shape<Int<tileM>, Int<tileN>>{}, make_stride(N, 1));
  GmemTiledCopyC gmem_tiled_copy_c;
  auto gmem_thr_copy_c = gmem_tiled_copy_c.get_thread_slice(idx);
  auto tCgC_copy = gmem_thr_copy_c.partition_S(gC);
  Tensor tCpC_copy = make_tensor<bool>(make_shape(size<1>(tCgC_copy)));
  if constexpr (!is_even_M) {
    // (16, 16): make sure same as ThrLayout of GmemTiledCopyC;
    const int th_m_idx = idx / 16;
    constexpr int block_m_idxs = 16 * m_warps;
    for (int m = 0; m < size(tCpC_copy); ++m) {
      tCpC_copy(m) = m * block_m_idxs + th_m_idx + m_idx < M ? true : false;
    }
  }

  if (kSplits > 1 && k_split_idx == 0) {
    init_C_in_global_v2<is_even_M>(tCgC_copy, tCpC_copy);
  }

  const int q_n_idx = n_idx / 8;
  // const int k_idx = k_tile * tileK;

  constexpr int tileB = tileN / 8;
  const int QN = N / 8;

  // shared mem; used to store the scaling_factors and zeros in current k_tile;
  // G % tileK = 0; make sure that one k_tile in K dimension will belong to one
  // Quantized Group.
  __shared__ uint4 shared_scaling_factors[tileB];
  __shared__ uint4 shared_dequantized_zeros_neg[tileB];

  const int k_titles = K / tileK;
  const int even_k_split_tiles = (k_titles + kSplits - 1) / kSplits;
  const int start_k_split_titles = k_split_idx * even_k_split_tiles;
  const int block_split_tiles = k_split_idx != kSplits - 1
                                    ? even_k_split_tiles
                                    : k_titles - start_k_split_titles;

  int k_idx = start_k_split_titles * tileK;

  int g_idx = k_idx / G;
  uint4* scaling_factors_ptr =
      reinterpret_cast<uint4*>(scaling_factors + g_idx * N + n_idx);
  uint32_t* zeros_ptr =
      reinterpret_cast<uint32_t*>(zeros + g_idx * QN + q_n_idx);
  uint4 th_scaling_factors;
  uint4 th_loaded_zeros_neg;
  {
    // preload current tile scaling-factors and zeros to register
    if (idx < tileB) {
      th_scaling_factors = scaling_factors_ptr[idx];
      // }
      // if (warp_idx == 1 && lane_idx < tileB) {
      uint32_t zeros_loaded = zeros_ptr[idx];
      th_loaded_zeros_neg = dequantize_s4_to_fp16x2_neg(zeros_loaded);
      zeros_with_scales(th_loaded_zeros_neg, th_scaling_factors);
    }
  }

  // sA = (tileM, tileK)
  using SmemLayoutA = decltype(
      tile_to_shape(SmemLayoutAtomA{}, Shape<Int<tileM>, Int<tileK>>{}));
  Tensor sA = make_tensor(make_smem_ptr<half>(smem_), SmemLayoutA{});

  GmemTiledCopyA gmem_tiled_copy_a;
  auto gmem_thr_copy_a = gmem_tiled_copy_a.get_thread_slice(idx);

  // (GMEM_A_CPY_Y, GMEM_A_CPY_X): make sure same as ThrLayout of
  // GmemTiledCopyA.
  auto tAsA_copy = gmem_thr_copy_a.partition_D(sA);
  Tensor tApA_copy = make_tensor<bool>(make_shape(size<1>(tAsA_copy)));
  if constexpr (!is_even_M) {
    const int A_th_m_idx = idx / GmemCopyAThrLayoutX;
    constexpr int A_block_m_idxs = num_threads / GmemCopyAThrLayoutX;
    for (int m = 0; m < size(tApA_copy); ++m) {
      tApA_copy(m) = m * A_block_m_idxs + A_th_m_idx + m_idx < M ? true : false;
    }
  }

  // A: [M, K]; gA: [tileM, tileK]
  Tensor gA = make_tensor(make_gmem_ptr<half>(A + m_idx * K + k_idx),
                          Shape<Int<tileM>, Int<tileK>>{}, make_stride(K, 1));
  auto tAgA_copy = gmem_thr_copy_a.partition_S(gA);
  auto tArA_copy = make_fragment_like(tAgA_copy);
  {
    // preload current A_tile to register
    copy_A_global_to_register<is_even_M, GmemCopyAType>(tAgA_copy, tArA_copy,
                                                        tApA_copy);

    // store scaling-factors and zeros to lds
    if (idx < tileB) {
      shared_scaling_factors[idx] = th_scaling_factors;
      // }
      // if (warp_idx == 1 && lane_idx < tileB) {
      shared_dequantized_zeros_neg[idx] = th_loaded_zeros_neg;
    }
  }

  // 16x64; [tileK, tileN] % [16, 64] == 0
  using LayoutAtomB = decltype(composition(
      Swizzle<2, 4, 4>{}, Layout<Shape<_16, _64>, Stride<_64, _1>>{}));
  using B_s_layout =
      decltype(tile_to_shape(LayoutAtomB{}, Shape<Int<tileK>, Int<tileN>>{}));
  Tensor sB = make_tensor(make_smem_ptr(sA.data() + size(sA)), B_s_layout{});

  using GmemCopyAtomQB = Copy_Atom<UniversalCopy<cute::uint32_t>, int>;
  // tileN = 64; 32x8 o 1x1 => 32x8; [tileK, tileB] % [32, 8] == 0
  const int QB_cpy_col = idx & 7;  // % 8
  using GmemTiledCopyQB = decltype(
      make_tiled_copy(GmemCopyAtomQB{},
                      // nums_threads / 8 == tileK
                      Layout<Shape<Int<num_threads / 8>, _8>, Stride<_8, _1>>{},
                      Layout<Shape<_1, _1>>{}));

  using GmemCopyAtomDB = Copy_Atom<UniversalCopy<cute::uint128_t>, half>;
  using GmemTiledCopyDB = decltype(
      make_tiled_copy(GmemCopyAtomDB{},
                      Layout<Shape<Int<num_threads / 8>, _8>, Stride<_8, _1>>{},
                      Layout<Shape<_1, _8>>{}));

  GmemTiledCopyQB gmem_tiled_copy_qb;
  auto gmem_thr_copy_qb = gmem_tiled_copy_qb.get_thread_slice(idx);

  GmemTiledCopyDB gmem_tiled_copy_db;
  auto gmem_thr_copy_db = gmem_tiled_copy_db.get_thread_slice(idx);
  auto tBsB_copy = gmem_thr_copy_db.partition_D(sB);
  static_assert(size<2>(tBsB_copy) == 1);

  // QB: [K, QN]; gQB: [tileK, tileB]
  Tensor gQB = make_tensor(make_gmem_ptr<int>(B + k_idx * QN + q_n_idx),
                           Shape<Int<tileK>, Int<tileB>>{}, make_stride(QN, 1));
  const int QB_k_tile_stride = tileK * QN;
  auto tQBgQB_copy = gmem_thr_copy_qb.partition_S(gQB);
  auto tQBrQB_copy = make_fragment_like<int>(tQBgQB_copy);
  static_assert(size<2>(tQBrQB_copy) == 1);
  {
    // preload QB_tile to register.
    cute::copy(gmem_tiled_copy_qb, tQBgQB_copy, tQBrQB_copy);

    // wait scaling_factors, loaded_zeros are stored into lds
    block_sync_lds();

    // store A_tile to lds
    cute::copy(gmem_tiled_copy_a, tArA_copy, tAsA_copy);
  }

  /***********************
   * objects used for MMA
   ***********************/
  MMA tiled_mma;
  auto thr_mma = tiled_mma.get_slice(idx);
  // 64bits => 4 half
  using SmemCopyAtomA = Copy_Atom<UniversalCopy<cute::uint64_t>, half>;
  auto smem_copy_A = make_tiled_copy_A(SmemCopyAtomA{}, tiled_mma);
  auto tAsA_mma = thr_mma.partition_A(sA);
  auto tArA_mma = thr_mma.partition_fragment_A(sA);
  // auto tArA_mma = make_fragment_like<half>(
  //     Shape<Int<size<0>(tAsA_mma)>, Int<size<1>(tAsA_mma)>, _2>{});

  // B_s_layout_transposed: used for MMA;
  using LayoutBAtom_transposed = decltype(composition(
      Swizzle<2, 4, 4>{}, Layout<Shape<_64, _16>, Stride<_1, _64>>{}));
  using B_s_layout_transposed =
      decltype(tile_to_shape(LayoutBAtom_transposed{},
                             Shape<Int<tileN>, Int<tileK>>{}, GenRowMajor{}));
  // sB_transposed = (tileN, tileK)
  Tensor sB_transposed =
      make_tensor(make_smem_ptr(sB.data()), B_s_layout_transposed{});

  using SmemCopyAtomB = Copy_Atom<DefaultCopy, half>;
  auto smem_copy_B = make_tiled_copy_B(SmemCopyAtomB{}, tiled_mma);
  // load B_tile from shared to register;
  auto tBsB_mma = thr_mma.partition_B(sB_transposed);
  auto tBrB_mma = make_fragment_like<half>(
      Shape<Int<size<0>(tBsB_mma)>, Int<size<1>(tBsB_mma)>, _2>{});

  auto tCrC_mma =
      partition_fragment_C(tiled_mma, Shape<Int<tileM>, Int<tileN>>{});
  clear(tCrC_mma);

  bool need_store_scales_zeros = true;
  {
    // store B_tile to lds
    dequantize_tensor(tQBrQB_copy, tBsB_copy, shared_scaling_factors,
                      shared_dequantized_zeros_neg, QB_cpy_col,
                      th_scaling_factors, th_loaded_zeros_neg,
                      need_store_scales_zeros);
  }

  // loop on k_tiles; process all k_tiles;
  int k_tile = 0;
  for (; k_tile + 1 < block_split_tiles; ++k_tile) {
    // NB(smile): wait pre k_tile is completed
    // __syncthreads();

    k_idx = k_idx + tileK;
    const int next_g_idx = k_idx / G;
    {
      // load next tile A_tile, B_tile, scaling_factors, zeros to register.
      if (next_g_idx != g_idx) {
        scaling_factors_ptr += QN;
        zeros_ptr += QN;
        if (idx < tileB) {
          th_scaling_factors = scaling_factors_ptr[idx];
          // }
          // if (warp_idx == 1 && lane_idx < tileB) {
          uint32_t zeros_loaded = zeros_ptr[idx];
          th_loaded_zeros_neg = dequantize_s4_to_fp16x2_neg(zeros_loaded);
          zeros_with_scales(th_loaded_zeros_neg, th_scaling_factors);
        }
      }
      tAgA_copy.data() = tAgA_copy.data() + tileK;
      tQBgQB_copy.data() = tQBgQB_copy.data() + QB_k_tile_stride;

      copy_A_global_to_register<is_even_M, GmemCopyAType>(tAgA_copy, tArA_copy,
                                                          tApA_copy);
      cute::copy(gmem_tiled_copy_qb, tQBgQB_copy, tQBrQB_copy);

      if (next_g_idx != g_idx) {
        block_sync_lds();

        if (idx < tileB) {
          shared_scaling_factors[idx] = th_scaling_factors;
          // }
          // if (warp_idx == 1 && lane_idx < tileB) {
          shared_dequantized_zeros_neg[idx] = th_loaded_zeros_neg;
        }
        g_idx = next_g_idx;
        need_store_scales_zeros = true;
      }
    }

    // wait curent tile: A_tile, B_tile are loaded into lds.
    block_sync_lds();

    // gemm on current tile
    // gemm(tiled_mma, smem_copy_A, smem_copy_B, tAsA_mma, tArA_mma, tBsB_mma,
    //      tBrB_mma, tCrC_mma);
    cute::copy(smem_copy_A, tAsA_mma, tArA_mma);
    gemm(tiled_mma, smem_copy_B, tArA_mma, tBsB_mma, tBrB_mma, tCrC_mma);

    {
      // wait current MMA operation done.
      block_sync();
      // register -> lds
      // sA, sB pointer: point to next sA_tile, sB_tile;
      cute::copy(gmem_tiled_copy_a, tArA_copy, tAsA_copy);
      dequantize_tensor(tQBrQB_copy, tBsB_copy, shared_scaling_factors,
                        shared_dequantized_zeros_neg, QB_cpy_col,
                        th_scaling_factors, th_loaded_zeros_neg,
                        need_store_scales_zeros);
    }
  }
  if (k_tile < block_split_tiles) {
    // wait curent tile: A_tile, B_tile are loaded into lds.
    block_sync_lds();
    // gemm on current tile
    // gemm(tiled_mma, smem_copy_A, smem_copy_B, tAsA_mma, tArA_mma, tBsB_mma,
    //      tBrB_mma, tCrC_mma);
    cute::copy(smem_copy_A, tAsA_mma, tArA_mma);
    gemm(tiled_mma, smem_copy_B, tArA_mma, tBsB_mma, tBrB_mma, tCrC_mma);
  }

  // do C_tile type convert and stored it to shared.
  // sC = (tileM, tileN)
  using SmemLayoutC = decltype(
      tile_to_shape(SmemLayoutAtomC{}, Shape<Int<tileM>, Int<tileN>>{}));
  Tensor sC = make_tensor(make_smem_ptr(sA.data()), SmemLayoutC{});
  {
    // convert C_tile from float to half
    auto tCrC_mma_half = make_fragment_like<half>(tCrC_mma);
#pragma unroll
    for (int i = 0; i < size(tCrC_mma); ++i) {
      tCrC_mma_half[i] = __float2half_rn(tCrC_mma[i]);
    }
    // store C_tile from register to shared.
    using SmemCopyAtomC = Copy_Atom<DefaultCopy, half>;
    auto smem_copy_C = make_tiled_copy_C(SmemCopyAtomC{}, tiled_mma);
    auto tCsC_mma = thr_mma.partition_C(sC);
    // NB(smile): make sure all MMA operations are completed.
    // block_sync_lds();
    block_sync();
    cute::copy(smem_copy_C, tCrC_mma_half, tCsC_mma);
  }

  // cute::copy(smem_copy_C, tCrC_mma, tCsC_mma);
  // copy C_tile from shared to global;
  {
    auto tCsC_copy = gmem_thr_copy_c.partition_D(sC);

    // NB(smile): make sure that C_tile are loaded to shared.
    block_sync_lds();
    if (kSplits > 1) {
      // if (k_split_idx == 0) {
      //   __builtin_amdgcn_sched_barrier(0);
      //   __builtin_amdgcn_s_setprio(1);
      //   __builtin_amdgcn_sched_barrier(0);
      // } else {
      //   __builtin_amdgcn_sched_barrier(0);
      //   __builtin_amdgcn_s_setprio(0);
      //   __builtin_amdgcn_sched_barrier(0);
      // }
      copy_C_shared_to_global_atomic_v2<is_even_M>(tCsC_copy, tCgC_copy,
                                                   tCpC_copy);
    } else {
      copy_C_shared_to_global_v2<is_even_M>(tCsC_copy, tCgC_copy, tCpC_copy);
    }
  }
}

}  // namespace awq
}  // namespace vllm

void awq_gemm_rocm_for_m64(half* __restrict__ A,                // [M, K]
                           int* __restrict__ B,                 // [K, N // 8]
                           half* __restrict__ scaling_factors,  // [K // G, N]
                           int* __restrict__ zeros,  // [K // G, N // 8]
                           half* __restrict__ C,     // [M, N]
                           const int M, const int N, const int K, const int G) {
  constexpr int tileM = 64;
  constexpr int tileN = 64;
  // set G % tileK == 0,
  // make sure that one tile in K dimension will in one Group.
  int tileK = 32;
  if (G % 64 == 0 && tileM != 32) {
    tileK = 64;
  }
  assert(G % tileK == 0);

  constexpr int num_threads = 256;
  constexpr int num_warps = 4;
  dim3 block(num_threads);

  int n_blocks = N / tileN;
  int m_blocks = (M + tileM - 1) / tileM;
  int max_blocks = tileM == 16 ? 128 * 3 : 128 * 4;
  // one block process 8 k_Tiles at max;
  int k_blocks = MIN(((K / tileK) + 7) / 8, 4);
  k_blocks = MIN(k_blocks, MAX(max_blocks / (m_blocks * n_blocks), 1));
  int kSplits = k_blocks;
  dim3 grid(n_blocks, m_blocks, k_blocks);

  // 16x32; [tileM, tileK] % [16, 32] == 0
  using SmemLayoutAtomA = decltype(composition(
      Swizzle<3, 2, 4>{}, Layout<Shape<_16, _32>, Stride<_32, _1>>{}));

  // 16x64; [tileM, tileN] % [16, 64] == 0
  using SmemLayoutAtomC = decltype(composition(
      Swizzle<4, 2, 4>{}, Layout<Shape<_16, _64>, Stride<_64, _1>>{}));

  using GmemCopyAtomC = Copy_Atom<UniversalCopy<cute::uint32_t>, half>;
  // 16x16 o 1x4 => 16x64; [tileM, tileN] % [16, 64] == 0
  using GmemTiledCopyC = decltype(make_tiled_copy(
      GmemCopyAtomC{}, Layout<Shape<_16, _16>, Stride<_16, _1>>{},
      Layout<Shape<_1, _4>>{}));

  const cudaStream_t stream = at::cuda::getCurrentCUDAStream();
  bool is_even_m = M % tileM == 0 ? true : false;

  BOOL_SWITCH(is_even_m, is_even_M, [&] {
    // tileK = 64 or 32;
    // 16x32; [tileM, tileK] % [16, 32] == 0
    constexpr int n_warps = 4;

    TILE_K_SWITCH(tileK, TILE_K, [&] {
      // 32 = 256 / 8; 8 = tileB; 256 = n_warps * warp_size;
      constexpr int m_warps = TILE_K / 32;  // 1, 2;
      constexpr int num_threads = m_warps * n_warps * WARP_SIZE;
      dim3 block(num_threads);

      constexpr int BBits = TILE_K == 32 ? 3 : 4;
      using SmemLayoutAtomA = decltype(composition(
          Swizzle<BBits, 2, 4>{},
          Layout<Shape<_16, Int<TILE_K>>, Stride<Int<TILE_K>, _1>>{}));

      constexpr int GmemTiledCopyAThrLayoutX = TILE_K == 32 ? 8 : 16;
      constexpr int GmemTiledCopyAThrLayoutY = 32;
      using GmemTiledCopyAThrLayout = Layout<
          Shape<Int<GmemTiledCopyAThrLayoutY>, Int<GmemTiledCopyAThrLayoutX>>,
          Stride<Int<GmemTiledCopyAThrLayoutX>, _1>>;
      using GmemCopyAType = cute::uint64_t;
      using GmemCopyAtomA = Copy_Atom<UniversalCopy<cute::uint64_t>, half>;
      // 16x16 o 1x4 => 16x64; [tileM, tileK] % [16, 64] == 0
      using GmemTiledCopyA = decltype(make_tiled_copy(
          GmemCopyAtomA{}, GmemTiledCopyAThrLayout{}, Layout<Shape<_1, _4>>{}));

      using GmemTiledCopyC = decltype(make_tiled_copy(
          GmemCopyAtomC{},
          Layout<Shape<Int<num_threads / 16>, _16>, Stride<_16, _1>>{},
          Layout<Shape<_1, _4>>{}));

      vllm::awq::gemm_forward_4bit_for_m64<
          m_warps, n_warps, 64, tileN, TILE_K, SmemLayoutAtomA, GmemTiledCopyA,
          SmemLayoutAtomC, GmemTiledCopyC, GmemCopyAType,
          GmemTiledCopyAThrLayoutX, is_even_M><<<grid, block, 0, stream>>>(
          A, B, scaling_factors, zeros, C, M, N, K, G, kSplits);
    });
  });
}