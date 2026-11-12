# libcache - Example Network Cache Plugin

## Purpose

`libcache` is a **demonstration plugin** that shows how to implement a network-based cache for OptiX module compilation. It is designed to work with the accompanying `netcache` toy server and is provided as an **educational example** for users who want to understand how to build custom caching solutions.

**⚠️ This is NOT production-ready code.** It is a simplified example intended for experimentation and learning. Users who wish to deploy a network cache in production environments are responsible for:
- Adding comprehensive error handling and validation
- Implementing security measures (authentication, encryption, etc.)
- Adding proper logging and monitoring
- Load testing and hardening the implementation
- Ensuring thread-safety and reliability under production workloads

## What's Included

- **libcache library**: A shared library (.dll on Windows, .so on Linux) that implements a simple cache API
- **netcache server**: A toy Python-based cache server (`../netcache/cache_server.py`) for demonstration
- **ZeroMQ integration**: Uses ZeroMQ 4.3.5 for network communication (vendored in the SDK under `SDK/support/zeromq-4.3.5`, no external download required)

The library will be built to:
- **Windows**: `build/bin/<Config>/libcache.dll`
- **Linux**: `build/lib/libcache.so`

## Using with optixCustomCache Sample

Once built, you can use libcache with the `optixCustomCache` sample:

1. **Start the cache server** (in a separate terminal):
   ```bash
   python SDK/optixCustomCache/netcache/cache_server.py
   ```

2. **Run the sample with libcache**: (endpoint and timeout arguments are optional)
   ```bash
   # Windows
   optixCustomCache.exe --cache-lib path/to/libcache.dll ^
                        --cache-endpoint tcp://localhost:5555 ^
                        --cache-timeout 5000
   
   # Linux
   ./optixCustomCache --cache-lib path/to/libcache.so \
                      --cache-endpoint tcp://localhost:5555 \
                      --cache-timeout 5000
   ```

The sample will connect to the cache server and demonstrate cache miss/hit behavior with network-based caching.
If `--cache-lib` is **not** provided, the sample falls back to a simple in-memory cache and prints messages explaining that disk/network caching is disabled.

## API Overview

The libcache API provides basic cache operations:

```c
// Connect to cache server
CacheResult cache_connect(CacheDeviceContext ctx, const char* endpoint, int timeoutMs);

// Check if connected
bool cache_isOpen(CacheDeviceContext ctx);

// Query cache for a value
CacheResult cache_query(CacheDeviceContext ctx, const char* key, size_t keySize, 
                        char* value, size_t* valueSize);

// Insert value into cache
CacheResult cache_insert(CacheDeviceContext ctx, const char* key, size_t keySize,
                         const char* value, size_t valueSize);

// Disconnect from cache server
CacheResult cache_disconnect(CacheDeviceContext ctx);
```

## Dependencies

- **ZeroMQ 4.3.5** (included)
- **C++17**

## Limitations & Warnings

This is a **demonstration only**:
- ❌ No authentication or security
- ❌ Minimal error handling
- ❌ No production-grade reliability testing
- ❌ Simple text-based protocol (not optimized)
- ❌ No concurrent access patterns tested thoroughly
- ❌ The netcache server is a toy Python script, not a robust server

**Use this code as a starting point for understanding custom cache implementations, not as a deployment-ready solution.**
