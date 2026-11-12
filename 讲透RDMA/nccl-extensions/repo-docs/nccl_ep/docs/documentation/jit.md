# JIT Kernel Compilation

NCCL EP compiles several of its device kernels **at runtime** rather than
shipping every specialization in the library. The first call that needs a given
kernel variant invokes `nvcc`, caches the resulting cubin on disk, and reuses it
for the rest of that process and for later runs.

This means a deployed NCCL EP needs more than `libnccl_ep.so`: it needs a working
`nvcc`, the kernel headers, the NCCL device headers, the CUDA headers, and a
writable cache directory. Every one of those is discovered through environment
variables with a compiled-in fallback, so a build that stays where it was built
generally needs no configuration at all. The knobs exist for everything else —
relocated installs, wheels, containers, read-only filesystems, and cross-arch
builds.

## Path resolution

Each path is resolved by the first rule that yields a value. The compiled-in
defaults are baked at build time by CMake/Makefile from the build tree's layout.

**Kernel sources** — the NCCL EP headers the JIT compiles against:

1. `NCCL_EP_JIT_SOURCE_DIR`
2. `$NCCL_EP_HOME/include/nccl_ep`
3. compiled-in `NCCL_EP_JIT_SOURCE_DIR`

**NCCL device headers**:

1. `NCCL_EP_JIT_BUILD_INCLUDE_DIR`
2. `$NCCL_HOME/include`
3. compiled-in `NCCL_EP_JIT_BUILD_INCLUDE_DIR`

**CUDA headers**:

1. `NCCL_EP_JIT_CUDA_INCLUDE_DIR`
2. `$CUDA_HOME/include`, else `$CUDA_PATH/include`
3. compiled-in `NCCL_EP_JIT_CUDA_INCLUDE_DIR`

**Compiler binary**:

1. `NCCL_EP_JIT_NVCC`
2. `NVCC`
3. `$CUDA_HOME/bin/nvcc` or `$CUDA_PATH/bin/nvcc`, if that file exists
4. bare `nvcc`, resolved through `PATH`

### `NCCL_EP_HOME`

`NCCL_EP_HOME` is a convenience: it derives the kernel source directory as
`$NCCL_EP_HOME/include/nccl_ep` so a relocated install can be described with one
variable instead of a full path. It has no effect when
`NCCL_EP_JIT_SOURCE_DIR` is set, and no effect when the compiled-in default is
already correct.

The Python package uses exactly this — `nccl.ep` sets `NCCL_EP_HOME` to its own
package directory on import, because the wheel ships headers under
`nccl/ep/include/nccl_ep` and the path baked in on the build machine is
meaningless on the installed system.

## Cache

Compiled cubins are cached under `NCCL_EP_JIT_CACHE_DIR`, defaulting to
**`/tmp/nccl_ep/jit`**.

The cache key is a fingerprint over the kernel variant (family, variant name,
entry point, source, target SM and arch, runtime key) combined with an
environment hash over the compiler identity, a fingerprint of the kernel and NCCL
header trees, and the full compile option list.

Two consequences follow:

- **The cache is self-invalidating.** Editing a kernel header, switching
  compilers, changing arch flags, or pointing at different include directories
  all change the fingerprint and produce a new entry. There is no stale-cache
  hazard and no need to clear it manually after a rebuild.
- **Old entries are not reclaimed.** Superseded cubins remain on disk. On a
  machine that rebuilds often, the cache directory grows until something removes
  it; deleting it is always safe, costing only a recompile.

Cache writes are atomic — each artifact is written to a pid- and
thread-qualified temporary file and renamed into place — so concurrent ranks on
one node populating the same cache do not corrupt each other's entries.

Point `NCCL_EP_JIT_CACHE_DIR` at a writable location when `/tmp` is read-only,
tiny, or not shared the way you expect across containers. A cache on a persistent
volume also removes first-call compile latency from every fresh container start.

## Compilation flags

The JIT always passes `--std=c++17 --extended-lambda --expt-relaxed-constexpr`,
plus the include directories resolved above.

The target architecture is chosen as: the kernel variant's own `target_arch` when
it specifies one; otherwise `NVCC_ARCH_FLAGS` if set; otherwise
`-arch=sm_<detected>` for the running device.

`NVCC_EXTRA_FLAGS` is appended last, after every flag the library chose, so it can
override earlier options. Both flag variables are split on whitespace.

## Diagnostics

`NCCL_EP_JIT_LOG=1` enables JIT logging to stderr, prefixed `[nccl_ep jit]` and
tagged with the pid. It reports compile attempts and failures, and cache write
problems — mkdir, open, write, and rename errors — which is the fastest way to
find a cache directory that is unwritable or full.

A variant that fails to compile is recorded in-process and not retried, so a
failure is reported once rather than on every call. Repeated warnings for the
same kernel are likewise deduplicated.

## Deployment checklist

- `nvcc` reachable, via `PATH`, `CUDA_HOME`, or `NCCL_EP_JIT_NVCC`.
- Kernel headers present — set `NCCL_EP_HOME` (or `NCCL_EP_JIT_SOURCE_DIR`) if
  the library was relocated after being built.
- NCCL and CUDA headers reachable, via `NCCL_HOME` / `CUDA_HOME` or the explicit
  JIT overrides.
- A writable cache directory; override `/tmp` when it is not suitable.
- On first run, expect compile latency the cache will amortize.
