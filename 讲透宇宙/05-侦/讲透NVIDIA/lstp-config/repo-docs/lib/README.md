# Vendored libusb + libyaml (built automatically by `make`)

The top-level `Makefile` downloads and builds static copies of:

- libyaml 0.2.5
- libusb 1.0.27 (`--disable-udev`, `--enable-static`)

into per-arch install trees under `build/deps/`,
then links them with **`LDFLAGS=-static`** so the final binaries do not depend
on system `libyaml.so` or `libusb-1.0.so`.

Each architecture gets its own vendored libs (native or cross-built via
`VENDOR_HOST` in `lib/build-deps.sh`).

## First build

On an x86_64 or aarch64 dev machine:

```sh
sudo apt install gcc-arm-linux-gnueabihf gcc-x86-64-linux-gnu
make clean-all
make
```

Requires network (one-time download), `gcc`, `make`, `wget` or `curl`, `tar`.

After `make`, verify:

```sh
file build/lstp_config_tool_x86   # ELF 64-bit … x86-64 … statically linked
file build/lstp_config_tool_ARM   # ELF 32-bit … ARM … statically linked
ldd build/lstp_config_tool_x86    # not a dynamic executable
ldd build/lstp_config_tool_ARM    # not a dynamic executable
```

(`make` runs architecture checks automatically.)

## Not committed

The entire `build/` directory is generated and ignored. It contains downloaded
sources, per-architecture static libraries, object files, and final binaries.

## Reset vendored libs

```sh
make clean-all
make
```
