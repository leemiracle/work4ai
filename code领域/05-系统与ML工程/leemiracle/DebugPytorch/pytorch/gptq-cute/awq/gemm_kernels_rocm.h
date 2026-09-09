#pragma once

#include <cuda_fp16.h>

void awq_gemm_rocm_for_m16(half* __restrict__ A,                // [M, K]
                           int* __restrict__ B,                 // [K, N // 8]
                           half* __restrict__ scaling_factors,  // [K // G, N]
                           int* __restrict__ zeros,  // [K // G, N // 8]
                           half* __restrict__ C,     // [M, N]
                           const int M, const int N, const int K, const int G);

void awq_gemm_rocm_for_m32(half* __restrict__ A,                // [M, K]
                           int* __restrict__ B,                 // [K, N // 8]
                           half* __restrict__ scaling_factors,  // [K // G, N]
                           int* __restrict__ zeros,  // [K // G, N // 8]
                           half* __restrict__ C,     // [M, N]
                           const int M, const int N, const int K, const int G);

void awq_gemm_rocm_for_m64(half* __restrict__ A,                // [M, K]
                           int* __restrict__ B,                 // [K, N // 8]
                           half* __restrict__ scaling_factors,  // [K // G, N]
                           int* __restrict__ zeros,  // [K // G, N // 8]
                           half* __restrict__ C,     // [M, N]
                           const int M, const int N, const int K, const int G);