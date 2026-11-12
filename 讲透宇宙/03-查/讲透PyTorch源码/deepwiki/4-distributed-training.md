# Distributed Training Systems

- docs/source/distributed.md
- test/distributed/_composable/test_composability/test_2d_composability.py
- test/distributed/algorithms/ddp_comm_hooks/test_ddp_hooks.py
- test/distributed/checkpoint/test_state_dict_utils.py
- test/distributed/tensor/experimental/test_local_map.py
- test/distributed/tensor/parallel/test_tp_random_state.py
- test/distributed/tensor/test_common_rules.py
- test/distributed/tensor/test_decompositions.py
- test/distributed/tensor/test_dtensor.py
- test/distributed/tensor/test_dtensor_ops.py
- test/distributed/tensor/test_math_ops.py
- test/distributed/tensor/test_op_strategy.py
- test/distributed/tensor/test_placement_types.py
- test/distributed/tensor/test_pointwise_ops.py
- test/distributed/tensor/test_redistribute.py
- test/distributed/tensor/test_single_dim_strategy.py
- test/distributed/tensor/test_strategy_validation.py
- test/distributed/tensor/test_tensor_ops.py
- test/distributed/tensor/test_utils.py
- test/distributed/tensor/test_view_ops.py
- test/distributed/test_c10d_common.py
- test/distributed/test_c10d_nccl.py
- test/quantization/fx/test_model_report_fx.py
- torch/_C/_distributed_c10d.pyi
- torch/csrc/distributed/c10d/Backend.hpp
- torch/csrc/distributed/c10d/Ops.cpp
- torch/csrc/distributed/c10d/ProcessGroup.hpp
- torch/csrc/distributed/c10d/ProcessGroupNCCL.cpp
- torch/csrc/distributed/c10d/ProcessGroupNCCL.hpp
- torch/csrc/distributed/c10d/init.cpp
- torch/distributed/algorithms/ddp_comm_hooks/quantization_hooks.py
- torch/distributed/distributed_c10d.py
- torch/distributed/tensor/_api.py
- torch/distributed/tensor/_collective_utils.py
- torch/distributed/tensor/_decompositions.py
- torch/distributed/tensor/_dtensor_spec.py
- torch/distributed/tensor/_ops/_math_ops.py
- torch/distributed/tensor/_ops/_matrix_ops.py
- torch/distributed/tensor/_ops/_pointwise_ops.py
- torch/distributed/tensor/_ops/_tensor_ops.py
- torch/distributed/tensor/_ops/_view_ops.py
- torch/distributed/tensor/_ops/single_dim_strategy.py
- torch/distributed/tensor/_ops/strategy_validation.py
- torch/distributed/tensor/_ops/utils.py
- torch/distributed/tensor/_redistribute.py
- torch/distributed/tensor/_sharding_prop.py
- torch/distributed/tensor/_utils.py
- torch/distributed/tensor/experimental/_func_map.py
- torch/distributed/tensor/placement_types.py
- torch/testing/_internal/common_distributed.py
- torch/testing/_internal/common_ops_unbacked.py
- torch/testing/_internal/distributed/_tensor/common_dtensor.py

## Purpose and Scope

- c10d Collective Communication : The foundational communication library providing process group management and efficient collective operations across hardware backends like NCCL and Gloo.
- DTensor (Distributed Tensor) : A distributed tensor abstraction supporting Single Program Multiple Data (SPMD) programming with automatic sharding propagation and communication insertion.
- DeviceMesh : An abstraction for managing multidimensional device topologies and associated process groups, enabling flexible parallelism strategies.
- Symmetric Memory : A specialized subsystem enabling high-bandwidth peer-to-peer direct GPU-to-GPU communication with minimal overhead.

## c10d Collective Communication

`c10d`

- ProcessGroup : Central to c10d , this abstraction manages a group of processes participating in collective operations. Several backend implementations exist. The commonly used backends include: ProcessGroupNCCL : Optimized for NVIDIA GPUs, leveraging NCCL for high-performance GPU collectives torch/csrc/distributed/c10d/ProcessGroupNCCL.cpp 30-52 ProcessGroupGloo : A cross-platform, CPU-based backend suitable for heterogeneous devices torch/csrc/distributed/c10d/init.cpp 27-30
- Store : Used during rendezvous to exchange key-value pairs (metadata) needed for process group setup. Implementations include PrefixStore , TCPStore , FileStore , and HashStore torch/csrc/distributed/c10d/init.cpp 4-19 torch/distributed/distributed_c10d.py 56-63
- Work : Represents the handle to asynchronous collective operations, allowing synchronization and status checks torch/distributed/distributed_c10d.py 65-66
- Functional Collectives : Modern workflows often use functional collective APIs (e.g., torch.ops.c10d_functional ) for better integration with PyTorch's compilation stack test/distributed/tensor/test_math_ops.py 40

`c10d`
`all_reduce`
`all_gather`
`reduce_scatter`
`broadcast`
torch/distributed/distributed_c10d.py 108-120

`c10d`
c10d Collective Communication

Sources:
torch/distributed/distributed_c10d.py 1-187
torch/csrc/distributed/c10d/init.cpp 1-75
torch/csrc/distributed/c10d/ProcessGroupNCCL.cpp 1-52

## DTensor: Distributed Tensor Abstraction

### Architecture and Placement Types

- DTensor : A wrapper around local tensors with a global distribution specification ( DTensorSpec ). Users interact with DTensor as if it were a single logical tensor across all devices torch/distributed/tensor/_ops/_math_ops.py 10-15 test/distributed/tensor/test_tensor_ops.py 9-17
- DTensorSpec : Encapsulates the tensor distribution pattern and the DeviceMesh over which it is distributed torch/distributed/tensor/_ops/_math_ops.py 11
- Placement Types define how a tensor is distributed: Shard(dim) : Tensor is partitioned along a given dimension torch/distributed/tensor/placement_types.py 39 Replicate : Tensor is fully replicated on all ranks torch/distributed/tensor/placement_types.py 38 Partial(reduce_op) : Each rank holds partial results that need reduction (e.g., sum, mean) to get the global tensor torch/distributed/tensor/placement_types.py 36 _StridedShard : A specialized sharding type for more complex memory layouts torch/distributed/tensor/placement_types.py 35

### Relationship of DTensor Entities

```

```

`DeviceMesh`
`ShardingPropagator`
torch/distributed/tensor/_sharding_prop.py 19
`OpStrategy`
torch/distributed/tensor/_op_schema.py 15

DTensor: Distributed Tensor Abstraction

Sources:
test/distributed/tensor/test_tensor_ops.py 9-20
torch/distributed/tensor/_ops/_math_ops.py 10-40
torch/distributed/tensor/placement_types.py 33-40

## DeviceMesh Topology Management

`DeviceMesh`

- It manages the creation and lifecycle of process groups along each mesh dimension, coordinating communication primitives like all-reduce or broadcast per dimension.
- DeviceMesh interfaces cleanly with DTensor to describe tensor shard placements in the context of the mesh topology torch/distributed/tensor/_ops/_math_ops.py 10 test/distributed/tensor/test_math_ops.py 11-13

`c10d`

DeviceMesh and Device Topology

Sources:
torch/distributed/tensor/_ops/_math_ops.py 10
test/distributed/tensor/test_math_ops.py 11-20

## Symmetric Memory for High-Performance Communication

- SymmetricMemory is a subsystem implemented in C++ and exposed via Python that enables direct memory access between GPUs, reducing communication latency and CPU involvement torch/csrc/distributed/c10d/init.cpp 59-64
- It uses a rendezvous protocol to create symmetric, shared GPU memory regions accessible across ranks.
- Backend implementations include: NCCLSymmetricMemory : NCCL-based symmetric communication integration torch/csrc/distributed/c10d/init.cpp 42 NVSHMEM : Backend providing scalable shared memory for GPU collectives torch/csrc/distributed/c10d/init.cpp 62-64 DMAConnectivity : Abstraction for underlying hardware transport torch/csrc/distributed/c10d/init.cpp 59

`ProcessGroupNCCL`
torch/csrc/distributed/c10d/ProcessGroupNCCL.cpp 34

Symmetric Memory for High-Performance Communication

Sources:
torch/csrc/distributed/c10d/init.cpp 42-64
torch/csrc/distributed/c10d/ProcessGroupNCCL.cpp 34

## Integration and Higher-Level Distributed APIs

- Fully Sharded Data Parallel (FSDP) : Manages parameter sharding, gradient synchronization, and overlap of communication/computation using c10d collectives and DTensor abstractions. See FSDP: Fully Sharded Data Parallel for details.
- Pipeline Parallelism : Defines model partitioning into pipeline stages, microbatch management, and interoperability with DTensor and FSDP. See Pipeline Parallelism .
- Distributed Checkpointing : Supports efficient distributed state dict save/load with resharding and integration with DTensor and FSDP to facilitate large-scale model checkpointing. See Distributed Checkpointing .

### System Integration Map

```

```

- c10d Collective Communication
- DTensor: Distributed Tensor Abstraction
- Symmetric Memory for High-Performance Communication
- FSDP: Fully Sharded Data Parallel
- Pipeline Parallelism
- Distributed Checkpointing

Sources:
torch/distributed/distributed_c10d.py 1-138
torch/csrc/distributed/c10d/init.cpp 1-75
test/distributed/tensor/test_tensor_ops.py 9-35

###
