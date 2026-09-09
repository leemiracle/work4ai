#include <torch/all.h>
#include <c10/cuda/CUDAGuard.h>

#include "dequantize.cuh"
#include "core/math.hpp"
#include "gemm_kernels_rocm.h"

#include <cuda_fp16.h>

torch::Tensor awq_gemm(torch::Tensor _in_feats,        /* [M, K] */
                       torch::Tensor _kernel,          /* [K, N // 8] */
                       torch::Tensor _scaling_factors, /* [K // G, N] */
                       torch::Tensor _zeros,           /* [K // G, N // 8] */
                       int64_t split_k_iters) {
  int num_in_feats = _in_feats.size(0);
  int num_in_channels = _in_feats.size(1);
  const at::cuda::OptionalCUDAGuard device_guard(device_of(_in_feats));

  auto options = torch::TensorOptions()
                     .dtype(_in_feats.dtype())
                     .device(_in_feats.device());
  int num_out_feats = num_in_feats;
  int num_out_channels = _kernel.size(1) * 8;

  auto in_feats = reinterpret_cast<half*>(_in_feats.data_ptr<at::Half>());
  auto kernel = reinterpret_cast<int*>(_kernel.data_ptr<int>());

  auto scaling_factors =
      reinterpret_cast<half*>(_scaling_factors.data_ptr<at::Half>());
  auto zeros = reinterpret_cast<int*>(_zeros.data_ptr<int>());
  int group_size = num_in_channels / _scaling_factors.size(0);

  if (num_out_channels % 64 != 0)
    throw std::invalid_argument("OC is not multiple of cta_N = 64");
  if (num_out_channels % 8 != 0)
    throw std::invalid_argument("OC is not multiple of pack_num = 8");
  if (group_size % 32 != 0)
    throw std::invalid_argument("Group size should be a multiple of 32");
  if (num_out_channels % group_size != 0)
    throw std::invalid_argument("OC is not multiple of Group size");

  const cudaStream_t stream = at::cuda::getCurrentCUDAStream();

  int M = num_in_feats;
  int N = num_out_channels;
  int K = num_in_channels;
  int Q_N = N / 8;
  int G = group_size;

  int tileM = 32;
  if (M > 32) {
    tileM = 64;
  } else if (M <= 16) {
    tileM = 16;
  }

  at::Tensor _out_feats =
      torch::empty({num_in_feats, _kernel.size(1) * 8}, options);
  auto out_feats = reinterpret_cast<half*>(_out_feats.data_ptr<at::Half>());

  if (tileM == 16) {
    awq_gemm_rocm_for_m16(in_feats, kernel, scaling_factors, zeros, out_feats,
                          M, N, K, G);
  } else if (tileM == 32) {
    awq_gemm_rocm_for_m32(in_feats, kernel, scaling_factors, zeros, out_feats,
                          M, N, K, G);
  } else {
    awq_gemm_rocm_for_m64(in_feats, kernel, scaling_factors, zeros, out_feats,
                          M, N, K, G);
  }

  return _out_feats;
}