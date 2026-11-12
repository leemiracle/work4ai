# Usage Examples

> **Note:** For a complete working example, see `ep_test.cu` which demonstrates both LL and HT modes with all API calls.

## Example 1: High Throughput Mode - Forward and Backward Pass

```c
#include "nccl.h"
#include "nccl_ep.h"
#include "cuda_runtime.h"

// The library does not own tensor memory. The caller can mix two descriptor
// shapes — value-type "static" descriptors (stack / struct member /
// global, populated in place via NCCL_EP_TENSOR_INIT_INLINE) and heap
// "dynamic" descriptors obtained from ncclEpTensorAlloc (library-owned
// `sizes` copy, released by ncclEpTensorDestroy). Public structs hold
// `ncclEpTensor_t*` either way, so the two are interchangeable at use sites.

// Initialize NCCL communicator
ncclComm_t comm;
ncclCommInitRank(&comm, nRanks, id, myRank);

cudaStream_t stream;
cudaStreamCreate(&stream);

unsigned int top_k = 8;
unsigned int hidden = 4096;

// Configure for High Throughput mode
ncclEpGroupConfig_t config = NCCL_EP_GROUP_CONFIG_INIT;
config.algorithm = NCCL_EP_ALGO_HIGH_THROUGHPUT;
config.num_experts = 256;
config.max_dispatch_tokens_per_rank = 4;
config.max_recv_tokens_per_rank = nRanks * config.max_dispatch_tokens_per_rank;
config.max_token_bytes = hidden * 2;  // bfloat16
config.rdma_buffer_size = NCCL_EP_AUTO;     // Auto-size
config.num_qp_per_rank = NCCL_EP_AUTO;      // Auto-size
config.num_channels = NCCL_EP_AUTO;         // Auto-size
// Optional: wire a custom device-memory allocator via config.alloc.
// config.alloc.alloc_fn = my_alloc; config.alloc.free_fn = my_free; config.alloc.context = &my_pool;

ncclEpGroup_t ep_group;
ncclEpCreateGroup(&ep_group, comm, &config);

unsigned int num_local_experts = config.num_experts / nRanks;
unsigned int num_recv_tokens   = config.max_recv_tokens_per_rank;

// --- topk_idx: dynamic descriptor (heap, library-owned sizes copy) ---
// ncclEpTensorAlloc copies `dims` into its own storage, so the local
// array can go out of scope safely after the call.
ncclEpTensor_t* topk_idx = nullptr;
{
    size_t dims[2] = { num_tokens, top_k };
    ncclEpTensorAlloc(&topk_idx, 2, ncclInt64, dims, /*config=*/NULL);
    cudaMalloc(&topk_idx->data, num_tokens * top_k * sizeof(int64_t));
}

// --- expert_counters: static descriptor with in-place initialization ---
// The caller owns both the device buffer and the `sizes` array; both must
// outlive any library call that observes the descriptor.
size_t expert_counters_dims[1] = { num_local_experts };
void*  expert_counters_data    = nullptr;
cudaMalloc(&expert_counters_data, num_local_experts * sizeof(int32_t));
ncclEpTensor_t expert_counters = { NCCL_EP_TENSOR_INIT_INLINE,
                                   .ndim = 1, .datatype = ncclInt32,
                                   .data = expert_counters_data,
                                   .sizes = expert_counters_dims };

// Mix dynamic (topk_idx) and static (expert_counters) in the same call.
ncclEpLayoutInfo_t handle_layout = NCCL_EP_LAYOUT_INFO_INIT;
handle_layout.expert_counters = &expert_counters;   // address-of stack descriptor

ncclEpHandle_t handle;
ncclEpCreateHandle(&handle, ep_group, NCCL_EP_LAYOUT_FLAT, topk_idx, &handle_layout,
                   /*config=*/NULL, stream);

// === FORWARD PASS ===
//
// Static (stack, in-place init): in/out tokens, out topk_weights, out topk_idx.
// Dynamic (heap, ncclEpTensorAlloc):  in topk_weights.

// Static input/output token descriptors.
size_t in_tokens_dims[2]        = { num_tokens,      hidden };
size_t out_tokens_dims[2]       = { num_recv_tokens, hidden };
size_t out_topk_weights_dims[2] = { num_recv_tokens, top_k };
size_t out_topk_idx_dims[2]     = { num_recv_tokens, top_k };
void*  in_tokens_data           = nullptr;
void*  out_tokens_data          = nullptr;
void*  out_topk_weights_data    = nullptr;
void*  out_topk_idx_data        = nullptr;
cudaMalloc(&in_tokens_data,        num_tokens      * hidden * sizeof(uint16_t));
cudaMalloc(&out_tokens_data,       num_recv_tokens * hidden * sizeof(uint16_t));
cudaMalloc(&out_topk_weights_data, num_recv_tokens * top_k  * sizeof(float));
cudaMalloc(&out_topk_idx_data,     num_recv_tokens * top_k  * sizeof(int64_t));

// Fast in-place initialization of static tensors
// go away after Dispatch invocation
ncclEpTensor_t in_tokens        = {                          
    NCCL_EP_TENSOR_INIT_INLINE,
    .ndim = 2,
    .datatype = ncclBfloat16,
    .data = in_tokens_data,
    .sizes = in_tokens_dims };
ncclEpTensor_t out_tokens       = { 
    NCCL_EP_TENSOR_INIT_INLINE,
    .ndim = 2,
    .datatype = ncclBfloat16,
    .data = out_tokens_data,
    .sizes = out_tokens_dims };
ncclEpTensor_t out_topk_weights = {
    NCCL_EP_TENSOR_INIT_INLINE,
    .ndim = 2,
    .datatype = ncclFloat32,
     .data = out_topk_weights_data,
    .sizes = out_topk_weights_dims };
ncclEpTensor_t out_topk_idx     = {
    NCCL_EP_TENSOR_INIT_INLINE,
    .ndim = 2,
    .datatype = ncclInt64,
    .data = out_topk_idx_data,
    .sizes = out_topk_idx_dims };

// Dynamic input topk_weights.
ncclEpTensor_t* in_topk_weights = nullptr;
{
    size_t dims[2] = { num_tokens, top_k };
    ncclEpTensorAlloc(&in_topk_weights, 2, ncclFloat32, dims, /*config=*/NULL);
    cudaMalloc(&in_topk_weights->data, num_tokens * top_k * sizeof(float));
}

// Pointer assignments mix `&` (address of stack descriptor) and the bare
// pointer returned by ncclEpTensorAlloc.
ncclEpDispatchInputs_t  dispatch_in  = NCCL_EP_DISPATCH_INPUTS_INIT;
ncclEpDispatchOutputs_t dispatch_out = NCCL_EP_DISPATCH_OUTPUTS_INIT;
dispatch_in.tokens        = &in_tokens;          // static
dispatch_in.topk_weights  = in_topk_weights;     // dynamic
dispatch_out.tokens       = &out_tokens;         // static
dispatch_out.topk_weights = &out_topk_weights;   // static
dispatch_out.topk_idx     = &out_topk_idx;       // static

ncclEpDispatchConfig_t dispatch_cfg = NCCL_EP_DISPATCH_CONFIG_INIT;
ncclEpDispatch(handle, &dispatch_in, &dispatch_out,
               &handle_layout, &dispatch_cfg, stream);

// Expert forward computation
// ... process out_tokens using expert_counters to size each expert's slab ...

// Combine expert outputs back to original token order (static descriptors).
size_t combine_in_dims[2]  = { num_recv_tokens, hidden };
size_t combine_out_dims[2] = { num_tokens,      hidden };
void*  combine_in_data     = nullptr;
void*  combine_out_data    = nullptr;
cudaMalloc(&combine_in_data,  num_recv_tokens * hidden * sizeof(uint16_t));
cudaMalloc(&combine_out_data, num_tokens      * hidden * sizeof(uint16_t));
ncclEpTensor_t combine_in_tokens  = { 
    NCCL_EP_TENSOR_INIT_INLINE,
    .ndim = 2, 
    .datatype = ncclBfloat16,
    .data = combine_in_data,
    .sizes = combine_in_dims };
ncclEpTensor_t combine_out_tokens = { 
    NCCL_EP_TENSOR_INIT_INLINE,
    .ndim = 2,
    .datatype = ncclBfloat16,
    .data = combine_out_data,
    .sizes = combine_out_dims };

ncclEpCombineInputs_t  combine_in  = NCCL_EP_COMBINE_INPUTS_INIT;
ncclEpCombineOutputs_t combine_out = NCCL_EP_COMBINE_OUTPUTS_INIT;
combine_in.tokens  = &combine_in_tokens;
combine_out.tokens = &combine_out_tokens;

ncclEpCombineConfig_t combine_cfg = NCCL_EP_COMBINE_CONFIG_INIT;
ncclEpCombine(handle, &combine_in, &combine_out, &combine_cfg, stream);

// === BACKWARD PASS ===
// Reuse the same handle — routing information stays the same. Backward
// descriptors not shown here in detail; assume `grad_*` are caller-prepared
// ncclEpTensor_t values (either pattern works).
//
// IMPORTANT (HT only): the forward/backward direction is selected by the
// `pass_direction` field in the dispatch/combine config. The default is
// NCCL_EP_FWD_PASS, so the backward pass MUST set it to NCCL_EP_BWD_PASS.
// This field impacts the set of required fields:
//   - dispatch: FWD requires inputs->topk_weights and forbids it on BWD
//     (BWD also forbids outputs->topk_weights / outputs->topk_idx);
//   - combine:  FWD forbids inputs->topk_weights, BWD requires both
//     inputs->topk_weights and outputs->topk_weights.

ncclEpDispatchInputs_t  bwd_dispatch_in  = NCCL_EP_DISPATCH_INPUTS_INIT;
ncclEpDispatchOutputs_t bwd_dispatch_out = NCCL_EP_DISPATCH_OUTPUTS_INIT;
bwd_dispatch_in.tokens   = &grad_combined;     // user-supplied grad descriptor
bwd_dispatch_out.tokens  = &grad_at_experts;   // preallocated buffer descriptor

ncclEpDispatchConfig_t bwd_dispatch_cfg = NCCL_EP_DISPATCH_CONFIG_INIT;
bwd_dispatch_cfg.pass_direction = NCCL_EP_BWD_PASS;   // toggle the selector
ncclEpDispatch(handle, &bwd_dispatch_in, &bwd_dispatch_out,
               &handle_layout, &bwd_dispatch_cfg, stream);

// Expert backward computation
// ... compute gradients for each expert ...

// Combine gradients (backward combine: also carry per-token routing weights).
ncclEpCombineInputs_t  bwd_combine_in  = NCCL_EP_COMBINE_INPUTS_INIT;
ncclEpCombineOutputs_t bwd_combine_out = NCCL_EP_COMBINE_OUTPUTS_INIT;
bwd_combine_in.tokens        = &grad_expert_outputs;
bwd_combine_in.topk_weights  = &combine_topk_weights_input;
bwd_combine_out.tokens       = &grad_tokens;
bwd_combine_out.topk_weights = &combine_topk_weights_output;

ncclEpCombineConfig_t bwd_combine_cfg = NCCL_EP_COMBINE_CONFIG_INIT;
bwd_combine_cfg.pass_direction = NCCL_EP_BWD_PASS;    // toggle the selector
ncclEpCombine(handle, &bwd_combine_in, &bwd_combine_out, &bwd_combine_cfg, stream);

// Cleanup
ncclEpHandleDestroy(handle);
ncclEpGroupDestroy(ep_group);
// Dynamic descriptors: free the caller-owned device buffer first, then the
// descriptor (which also releases the library-owned `sizes` copy).
cudaFree(topk_idx->data);
ncclEpTensorDestroy(topk_idx);
cudaFree(in_topk_weights->data);
ncclEpTensorDestroy(in_topk_weights);
// Static descriptors: free the device buffer; the descriptor itself lives on
// the stack and needs no release. The `sizes` arrays are stack locals too.
cudaFree(in_tokens_data);
cudaFree(out_tokens_data);
cudaFree(out_topk_weights_data);
cudaFree(out_topk_idx_data);
cudaFree(expert_counters_data);
cudaFree(combine_in_data);
cudaFree(combine_out_data);
ncclCommDestroy(comm);
cudaStreamDestroy(stream);
```

## Example 2: Low Latency Mode - Forward Pass (Expert-Major and Rank-Major)

```c
#include "nccl.h"
#include "nccl_ep.h"
#include "cuda_runtime.h"

// Mirrors Example 1's pattern: mix value-type "static" descriptors
// (NCCL_EP_TENSOR_INIT_INLINE) with heap "dynamic" descriptors
// (ncclEpTensorAlloc). In LL forward, only topk_idx is dynamic.

// Initialize NCCL communicator
ncclComm_t comm;
ncclCommInitRank(&comm, nRanks, id, myRank);

cudaStream_t stream;
cudaStreamCreate(&stream);

unsigned int top_k = 8;
unsigned int hidden = 4096;

// Configure for Low Latency mode
ncclEpGroupConfig_t config = NCCL_EP_GROUP_CONFIG_INIT;
config.algorithm = NCCL_EP_ALGO_LOW_LATENCY;
config.num_experts = 256;
config.max_dispatch_tokens_per_rank = 128;  // Required for LL mode
config.max_token_bytes = hidden * 2;    // bfloat16
config.rdma_buffer_size = NCCL_EP_AUTO; // Auto-size
config.num_qp_per_rank = NCCL_EP_AUTO;  // Auto-size (or specify for LL)
config.num_channels = NCCL_EP_AUTO;     // Auto-size

ncclEpGroup_t ep_group;
ncclEpCreateGroup(&ep_group, comm, &config);

unsigned int num_local_experts = config.num_experts / nRanks;

// --- topk_idx: dynamic descriptor (required at handle creation in LL mode) ---
ncclEpTensor_t* topk_idx = nullptr;
{
    size_t dims[2] = { num_tokens, top_k };
    ncclEpTensorAlloc(&topk_idx, 2, ncclInt64, dims, /*config=*/NULL);
    cudaMalloc(&topk_idx->data, num_tokens * top_k * sizeof(int64_t));
}

// Choose the LL receive-buffer layout. Both EXPERT_MAJOR and RANK_MAJOR are
// supported in LL mode; this example branches on `layout` because the dispatch
// output / combine input tensors and the required metadata differ between them.
ncclEpLayout_t layout = NCCL_EP_LAYOUT_EXPERT_MAJOR;  // or NCCL_EP_LAYOUT_RANK_MAJOR
const bool expert_major = (layout == NCCL_EP_LAYOUT_EXPERT_MAJOR);

// Create EP handle. LL mode does not consume layout_info at handle-create time.
ncclEpHandle_t handle;
ncclEpCreateHandle(&handle, ep_group, layout, topk_idx,
                   /*layout_info=*/NULL, /*config=*/NULL, stream);

// === FORWARD PASS ===
//
// Static (stack, in-place init): input tokens, output tokens, and the count
// metadata (expert_counters for expert-major / src_rank_counters for rank-major,
// plus the rank-major-only per-slot topk outputs and per-token input weights).

// Input: tokens [B x H].
size_t in_tokens_dims[2] = { num_tokens, hidden };
void*  in_tokens_data    = nullptr;
cudaMalloc(&in_tokens_data, num_tokens * hidden * sizeof(uint16_t));
ncclEpTensor_t in_tokens = { NCCL_EP_TENSOR_INIT_INLINE,
                             .ndim = 2, .datatype = ncclBfloat16,
                             .data = in_tokens_data,
                             .sizes = in_tokens_dims };

// Dispatch-output tokens are 3D in both layouts, but the leading dimension differs:
//   expert-major: [num_local_experts, nRanks * max_dispatch_tokens_per_rank, hidden]
//   rank-major:   [nRanks,            max_dispatch_tokens_per_rank,          hidden]
size_t out_tokens_dims[3];
if (expert_major) {
    out_tokens_dims[0] = num_local_experts;
    out_tokens_dims[1] = (size_t)nRanks * config.max_dispatch_tokens_per_rank;
    out_tokens_dims[2] = hidden;
} else {  // rank-major
    out_tokens_dims[0] = (size_t)nRanks;
    out_tokens_dims[1] = config.max_dispatch_tokens_per_rank;
    out_tokens_dims[2] = hidden;
}
void*  out_tokens_data    = nullptr;
cudaMalloc(&out_tokens_data,
           out_tokens_dims[0] * out_tokens_dims[1] * out_tokens_dims[2] * sizeof(uint16_t));
ncclEpTensor_t out_tokens = { NCCL_EP_TENSOR_INIT_INLINE,
                              .ndim = 3, .datatype = ncclBfloat16,
                              .data = out_tokens_data,
                              .sizes = out_tokens_dims };

ncclEpDispatchInputs_t  dispatch_in  = NCCL_EP_DISPATCH_INPUTS_INIT;
ncclEpDispatchOutputs_t dispatch_out = NCCL_EP_DISPATCH_OUTPUTS_INIT;
ncclEpLayoutInfo_t      layout_info  = NCCL_EP_LAYOUT_INFO_INIT;
dispatch_in.tokens  = &in_tokens;    // static; always 2D [B x H]
dispatch_out.tokens = &out_tokens;   // static; 3D (shape chosen above)

// Per-rank-or-expert count metadata: per-local-expert for expert-major,
// per-source-rank for rank-major. Declared here so it outlives the dispatch call.
size_t counters_dims[1] = { expert_major ? (size_t)num_local_experts : (size_t)nRanks };
void*  counters_data    = nullptr;
cudaMalloc(&counters_data, counters_dims[0] * sizeof(int32_t));
ncclEpTensor_t counters = { NCCL_EP_TENSOR_INIT_INLINE,
                            .ndim = 1, .datatype = ncclInt32,
                            .data = counters_data, .sizes = counters_dims };

// Rank-major-only dispatch extras (unused, left NULL, for expert-major).
size_t out_w_dims[3]   = { (size_t)nRanks, config.max_dispatch_tokens_per_rank, top_k };
size_t out_idx_dims[3] = { (size_t)nRanks, config.max_dispatch_tokens_per_rank, top_k };
size_t in_w_dims[2]    = { num_tokens, top_k };
void*  out_w_data = nullptr, *out_idx_data = nullptr, *in_w_data = nullptr;
ncclEpTensor_t out_topk_weights, out_topk_idx, in_topk_weights;

if (expert_major) {
    // Expert-major: per-expert recv counts. Routing weights are applied on the
    // receive side during combine (see combine_out.topk_weights below), so the
    // dispatch carries no per-slot topk metadata and no input weights.
    layout_info.expert_counters = &counters;
} else {  // rank-major
    // Rank-major: per-source-rank counts (note: src_rank_counters, NOT expert_counters).
    layout_info.src_rank_counters = &counters;

    // Rank-major REQUIRES dispatch to also return per-slot routing metadata, both
    // 3D [nRanks, max_dispatch_tokens_per_rank, top_k]:
    cudaMalloc(&out_w_data,   out_w_dims[0]   * out_w_dims[1]   * out_w_dims[2]   * sizeof(float));
    cudaMalloc(&out_idx_data, out_idx_dims[0] * out_idx_dims[1] * out_idx_dims[2] * sizeof(int32_t));
    out_topk_weights = (ncclEpTensor_t){ NCCL_EP_TENSOR_INIT_INLINE,
                                         .ndim = 3, .datatype = ncclFloat32,
                                         .data = out_w_data, .sizes = out_w_dims };
    out_topk_idx     = (ncclEpTensor_t){ NCCL_EP_TENSOR_INIT_INLINE,
                                         .ndim = 3, .datatype = ncclInt32,
                                         .data = out_idx_data, .sizes = out_idx_dims };
    dispatch_out.topk_weights = &out_topk_weights;
    dispatch_out.topk_idx     = &out_topk_idx;

    // ... and per-token routing weights on the dispatch INPUT.
    cudaMalloc(&in_w_data, num_tokens * top_k * sizeof(float));
    in_topk_weights = (ncclEpTensor_t){ NCCL_EP_TENSOR_INIT_INLINE,
                                        .ndim = 2, .datatype = ncclFloat32,
                                        .data = in_w_data, .sizes = in_w_dims };
    dispatch_in.topk_weights = &in_topk_weights;
}

// Dispatch tokens to experts (staged execution for overlap)
ncclEpDispatchConfig_t dispatch_cfg = NCCL_EP_DISPATCH_CONFIG_INIT;
dispatch_cfg.send_only = 1;
ncclEpDispatch(handle, &dispatch_in, &dispatch_out,
               &layout_info, &dispatch_cfg, stream);

// Overlap with other computation...
// doOtherWork(stream);

// Wait for dispatch to complete
ncclEpComplete(handle, /*config=*/NULL, stream);
cudaStreamSynchronize(stream);

// Expert forward computation:
//   expert-major: out_tokens is [experts x slots x hidden]; use the per-expert
//                 counts to size each expert's valid range.
//   rank-major:   out_tokens is [ranks x slots x hidden]; use out_topk_idx to route
//                 each slot to its local expert(s) and the per-rank counts for valid
//                 ranges. The rank-major combine kernel applies weight = 1, so the
//                 caller MUST pre-reduce (apply out_topk_weights) before combine.

// Combine input: post-processed activation, SAME 3D shape as dispatch_out.tokens.
void*  combine_in_data = nullptr;
cudaMalloc(&combine_in_data,
           out_tokens_dims[0] * out_tokens_dims[1] * out_tokens_dims[2] * sizeof(uint16_t));
ncclEpTensor_t combine_in_tokens = {
    NCCL_EP_TENSOR_INIT_INLINE,
    .ndim = 3, .datatype = ncclBfloat16,
    .data = combine_in_data,
    .sizes = out_tokens_dims };

// Combine output: [B x H] back to original token order.
size_t combine_out_dims[2] = { num_tokens, hidden };
void*  combine_out_data    = nullptr;
cudaMalloc(&combine_out_data, num_tokens * hidden * sizeof(uint16_t));
ncclEpTensor_t combine_out_tokens = {
    NCCL_EP_TENSOR_INIT_INLINE,
    .ndim = 2,
    .datatype = ncclBfloat16,
    .data = combine_out_data,
    .sizes = combine_out_dims };

ncclEpCombineInputs_t  combine_in  = NCCL_EP_COMBINE_INPUTS_INIT;
ncclEpCombineOutputs_t combine_out = NCCL_EP_COMBINE_OUTPUTS_INIT;
combine_in.tokens  = &combine_in_tokens;
combine_out.tokens = &combine_out_tokens;

// Expert-major applies the per-token routing weights on the receive side, so it
// REQUIRES combine_out.topk_weights [B x top_k]. Rank-major already applied the
// weights in the caller's pre-reduction, so it leaves this field NULL.
size_t combine_out_w_dims[2] = { num_tokens, top_k };
void*  combine_out_w_data    = nullptr;
ncclEpTensor_t combine_out_weights;
if (expert_major) {
    cudaMalloc(&combine_out_w_data, num_tokens * top_k * sizeof(float));
    combine_out_weights = (ncclEpTensor_t){ NCCL_EP_TENSOR_INIT_INLINE,
                                            .ndim = 2, .datatype = ncclFloat32,
                                            .data = combine_out_w_data,
                                            .sizes = combine_out_w_dims };
    combine_out.topk_weights = &combine_out_weights;
}

ncclEpCombineConfig_t combine_cfg = NCCL_EP_COMBINE_CONFIG_INIT;
combine_cfg.send_only = 1;
ncclEpCombine(handle, &combine_in, &combine_out, &combine_cfg, stream);

ncclEpComplete(handle, /*config=*/NULL, stream);
cudaStreamSynchronize(stream);

// Cleanup
ncclEpHandleDestroy(handle);
ncclEpGroupDestroy(ep_group);
// Dynamic descriptor: free device buffer, then descriptor.
cudaFree(topk_idx->data);
ncclEpTensorDestroy(topk_idx);
// Static descriptors: free device buffers only (descriptors and sizes are stack locals).
cudaFree(in_tokens_data);
cudaFree(out_tokens_data);
cudaFree(counters_data);
cudaFree(combine_in_data);
cudaFree(combine_out_data);
if (expert_major) {
    cudaFree(combine_out_w_data);   // expert-major receive-side weights
} else {                            // rank-major dispatch extras
    cudaFree(out_w_data);
    cudaFree(out_idx_data);
    cudaFree(in_w_data);
}
ncclCommDestroy(comm);
cudaStreamDestroy(stream);
```
