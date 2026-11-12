# Custom Allocators

The API supports custom memory allocators for custom buffer management. This enables integration with memory pools, custom allocation strategies, or framework-specific allocators.

## Function Signatures

```c
typedef cudaError_t (*ncclEpAllocFn_t)(void** ptr, size_t size, void* context);
typedef cudaError_t (*ncclEpFreeFn_t)(void* ptr, void* context);

typedef struct {
    ncclEpAllocFn_t alloc_fn;  // NULL → default cudaMalloc
    ncclEpFreeFn_t  free_fn;   // NULL → default cudaFree
    void*           context;   // opaque pointer forwarded to every alloc_fn/free_fn call
} ncclEpAllocConfig_t;
```

The `context` value is set once in `ncclEpAllocConfig_t::context` and forwarded unchanged on every call, giving the allocator a stable handle to its backing pool / arena.

## Example

```c
// Custom allocator using a memory pool
cudaError_t my_alloc(void** ptr, size_t size, void* context) {
    MyPool* pool = static_cast<MyPool*>(context);
    *ptr = pool->allocate(size);
    return (*ptr != nullptr) ? cudaSuccess : cudaErrorMemoryAllocation;
}

cudaError_t my_free(void* ptr, void* context) {
    MyPool* pool = static_cast<MyPool*>(context);
    pool->deallocate(ptr);
    return cudaSuccess;
}

// Wire the allocator into the group config.
ncclEpGroupConfig_t config = NCCL_EP_GROUP_CONFIG_INIT;
config.alloc.alloc_fn = my_alloc;
config.alloc.free_fn  = my_free;
config.alloc.context  = &my_pool;
ncclEpCreateGroup(&ep_group, comm, &config);
```

If `alloc_fn`/`free_fn` are left NULL (the default after `NCCL_EP_GROUP_CONFIG_INIT`), the library uses `cudaMalloc`/`cudaFree`.
