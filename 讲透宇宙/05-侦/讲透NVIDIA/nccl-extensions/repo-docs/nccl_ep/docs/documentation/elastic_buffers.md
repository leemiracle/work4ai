# Elastic (GPU + CPU) Receive Buffers

An *elastic buffer* is a single contiguous virtual-address (VA) range whose physical backing is split into a **GPU segment** followed by a **CPU (HOST_NUMA) segment**, mapped end-to-end with the CUDA Virtual Memory Management (`cuMem*`) APIs. Because the EP receive (dispatch-output) token count is data-dependent, the GPU segment can be sized for the common case (e.g. the 95th-percentile receive count) while the much larger CPU segment absorbs rare outliers — instead of permanently sizing the whole receive buffer for the absolute worst case in scarce GPU memory.

Production integrations normally allocate tensors from their framework (PyTorch, etc.), so the elastic allocator is **reference code**, not a shipped EP API: see the self-contained, header-only [`examples/nccl_ep_elastic_buffer.h`](../../examples/nccl_ep_elastic_buffer.h), which integrators can copy or adapt.

Use the elastic buffer as a **plain receive tensor with the Expert-Major layout**
(`NCCL_EP_LAYOUT_EXPERT_MAJOR`), with the Expert-Major duplication modes left
**off** (their defaults):

```
NCCL_EP_HT_EM_LOCAL_DUP=false    # (default)
NCCL_EP_HT_EM_NVLINK_DUP=false   # (default)
```

In this configuration the receiver expands the flat staging buffer into the user's
recv buffer with a **permute kernel** (SASS stores) and combine reads it back with
a reduce kernel — so the recv buffer is filled and read purely by kernel
loads/stores. The Expert-Major layout with both dup modes off is required because:

- The **FLAT** layout stages the recv buffer with `cudaMemcpy`/`cudaMemset`, which
  **crash** on a `cuMem` HOST_NUMA pointer (see below).
- The Expert-Major **local-dup** / **NVLink-dup** variants (and NVLS) deliver into
  the recv buffer through an NCCL **window**, which is a separate, not-yet-supported
  path for CPU-backed segments (see the zero-copy note below).

Only the kernel path — Expert-Major with both dup modes off — safely drives an
elastic buffer's CPU segment:

```c
#include "examples/nccl_ep_elastic_buffer.h"

void* base;
ncclEpElasticBuffer buf;
// GPU segment sized for the common case; CPU segment for the tail. The CPU
// segment lands on the GPU's HOST_NUMA node.
ncclEpElasticAlloc(&base, &buf, gpu_bytes, cpu_bytes, /*gpu_dev_id*/-1);

// Plain recv tensor backed by the elastic buffer (no .win_hdl). Used with an
// EXPERT_MAJOR handle so the permute/reduce kernels fill and read it.
size_t dims[2] = { max_recv_tokens, hidden };
ncclEpTensor_t recv = NCCL_EP_TENSOR_INIT;
recv.ndim = 2; recv.datatype = ncclBfloat16;
recv.data = base; recv.sizes = dims;
// ... ncclEpCreateHandle(..., NCCL_EP_LAYOUT_EXPERT_MAJOR, ...) and pass &recv
//     as ncclEpDispatchOutputs_t::tokens / ncclEpCombineInputs_t::tokens ...

ncclEpElasticFree(&buf);
```

The same buffer can also be **registered as an NCCL window**
(`ncclCommWindowRegister(comm, base, ncclEpElasticTotalBytes(&buf), &win, 0)`)
for paths that need a window handle.

Notes:

- **`NCCL_ELASTIC_BUFFER_REGISTER=1`** (the default) is required to register a window over CPU-backed segments. Each segment is rounded up to the `cuMem` allocation granularity (commonly 2 MiB), so the realised sizes may exceed the requested bytes — use `ncclEpElasticTotalBytes()` for the registration size and `ncclEpElasticGpuBytes()` as the byte offset of the CPU segment.
- **Drive the CPU segment with kernels, not `cudaMemcpy`.** `cudaMemcpyAsync` (any kind, including `cudaMemcpyDefault`) and `cudaMemset` fault inside the CUDA driver when given a `cuMem` HOST_NUMA pointer; only kernel (SASS) loads/stores work on that memory (verified on H100, cross-socket). The Expert-Major path (with `NCCL_EP_HT_EM_LOCAL_DUP` / `NCCL_EP_HT_EM_NVLINK_DUP` off) uses kernels for the recv buffer, which is why it is the supported mode. The FLAT non-zero-copy path stages the recv buffer with `cudaMemcpy` and therefore does **not** work with a CPU-segment recv buffer.
- **Zero-copy (window-backed) receive into a CPU segment is not yet supported.** Passing the elastic buffer as a *window-backed* recv tensor (`.win_hdl` set) makes remote peers write **directly** into the HOST_NUMA segment. The bare peer→HOST_NUMA store path works on the hardware (verified cross-socket on a 2-socket H100 node), but EP's intranode producer→consumer synchronization uses device-scope fences, which do not guarantee a peer's HOST_NUMA stores are visible to the *consuming* GPU — system-scope (`membar.sys`) is required, matching the elastic-buffer design's LSA caveat. This is an EP fencing follow-up, not a hardware limitation.
- **Low Latency (LL) is not yet supported for elastic receive buffers.** LL can have remote ranks GIN-put directly into the receive buffer; correct writes that cross into the CPU segment require the device put to use the multi-segment ("mixed") GIN path, which is not yet wired through the EP kernels. This is a planned follow-up.
