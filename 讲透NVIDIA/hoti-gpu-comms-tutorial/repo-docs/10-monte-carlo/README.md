# Monte Carlo integration with cuRANDDx and NVSHMEM AMOs

This exercise estimates the integral of a two-dimensional device function over
a rectangular domain. The default `integrand(x, y)` is `x² + y²` on
`[0, 1] × [0, 1]`, whose integral is `2/3`. Replace that function and the four
domain limits to integrate another finite, bounded function; set
`kReferenceIntegral` to `std::numeric_limits<double>::quiet_NaN()` when no
closed-form result is available. Keep the supplied finite reference while
working through the uncompleted starter.

cuRANDDx creates a Philox state in each CUDA thread's registers, then
generates four uniform values at a time. The four values make two `(x, y)`
samples in the configured domain.

Do not make every sampled function value a remote atomic. Each CTA first
combines its threads' partial sums in shared memory, then thread zero adds the
fixed-point magnitude of its sum to one of two symmetric counters on PE 0 with
`nvshmem_uint64_atomic_add`. One counter accumulates positive CTA sums and the
other negative CTA sums, so the integrand may have finite signed values.

`kFixedPointScale` controls the conversion from a CTA's `double` sum to an
integer AMO operand. For a different integrand, choose it so every scaled CTA
sum fits in `long long` and each global positive or negative counter fits in
`uint64_t`. Rounding costs at most half a fixed-point unit per CTA.

~~~text
per-thread Philox samples -> CTA shared sum -> one integer AMO to PE 0 -> barrier -> readback
~~~

`global_fixed_sums` is a two-element symmetric allocation on every PE. Passing
its local pointer with target PE 0 names the corresponding counters on PE 0.
Every PE queues `nvshmemx_barrier_all_on_stream` before PE 0 reads the result,
ensuring that all stream-ordered AMOs have completed.

`monte_carlo.cu` is the starter and `monte_carlo_SOLVED.cu` is the completed
reference. The reference also copies each CTA's fixed-point sum to the host
and uses MPI to verify both symmetric counters exactly; the
reference-integral tolerance is a separate sanity check on the random sample.

## Prerequisites

This lab needs CUDA 13 or newer, MPI, NVSHMEM with device-side unsigned 64-bit
add AMOs, and the MathDx package containing cuRANDDx and commonDx. cuRANDDx is
header-only, so it needs an include path but no `-lcurand` link flag.

The Makefile defaults to Hopper (`CUDA_ARCH=90`, `CURANDDX_SM=900`) and also
derives `900` from CUDA's `90a` or `90f` variants. Set `CURANDDX_SM` separately
when its descriptor architecture differs from NVCC's architecture spelling.

## Build

From the repository root, load the JUPITER environment if applicable, then
point `MATHDX_HOME` at the unpacked MathDx prefix containing `include/`:

~~~bash
source ./env.sh
cd 10-monte-carlo
make MATHDX_HOME=/path/to/nvidia/mathdx/YY.MM
~~~

Alternatively, pass `CURANDDX_INCLUDE_DIR=/path/to/include` directly.

## Run

Run the solved version with one PE per GPU:

~~~bash
make run_SOLVED MATHDX_HOME=/path/to/nvidia/mathdx/YY.MM \
  LAUNCHER='srun --ntasks=2 --gpus-per-task=1'
~~~

A successful default run prints an integral estimate near `0.666667` and
`global AMO aggregation verified`. The estimate is stochastic, while the
comparison between the MPI sum of CTA partial sums and the symmetric global
sum isolates the AMO aggregation path.

## Exercise

1. Add every thread's `local_sum` to the CTA's `block_sum` with CUDA
   `atomicAdd`, then synchronize the CTA.
2. Convert the CTA sum with `__double2ll_rn`, select its positive or negative
   counter, then use `nvshmem_uint64_atomic_add` to add its magnitude at PE 0.
3. Keep the stream-ordered NVSHMEM barrier before host readback. It provides
   completion for the AMO updates; removing it can expose a partial global
   counter.

## Further reading

- [cuRANDDx getting started](https://docs.nvidia.com/cuda/curanddx/get_started/introduction.html)
- [cuRANDDx installation and MathDx include layout](https://docs.nvidia.com/cuda/curanddx/get_started/installation.html)
- [NVSHMEM atomic memory operations](https://docs.nvidia.com/nvshmem/api/latest/gen/api/amo.html)
