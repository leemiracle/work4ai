# Changelog

All notable changes to this crate are documented in this file.

## [Unreleased]

## [0.6.2-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-wasm-v0.6.2-rc.1...yaml-sigil-wasm-v0.6.2-rc.2) - 2026-10-28

### Changed

- Follow the `0.6.2-rc.2` runtime family and its shared
  `yaml-sigil-traits 0.4.2-rc.1` contract.

## [0.6.2-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-wasm-v0.6.1...yaml-sigil-wasm-v0.6.2-rc.1) - 2026-10-27

### Changed

- Prepare a maintenance RC after the compatible dependency refresh
  ([#186](https://github.com/NVIDIA/yaml-sigil-rs/pull/186)).
- Refresh application lockfiles with `cargo update` to pick up compatible
  dependency fixes.

## [0.6.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-wasm-v0.6.1-rc.1...yaml-sigil-wasm-v0.6.1) - 2026-10-12

### Changed

- Promote `0.6.1-rc.1` to stable without further API or behavior changes.

## [0.6.1-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-wasm-v0.6.0...yaml-sigil-wasm-v0.6.1-rc.1) - 2026-10-12

### Changed

- Advance the four implementation dependencies to `0.6.1-rc.1`.
- Allow compatible patch updates for `wasm-bindgen`, `js-sys`, and
  `wasm-bindgen-test`.

## [0.6.0](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-wasm-v0.6.0-rc.3...yaml-sigil-wasm-v0.6.0) - 2026-09-24

### Changed

- Promote `0.6.0-rc.3` to stable without further API or behavior changes.

## [0.6.0-rc.3](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-wasm-v0.6.0-rc.2...yaml-sigil-wasm-v0.6.0-rc.3) - 2026-09-24

### Added

- add a JavaScript `v1alpha1` namespace and matching Rust module while retaining
  top-level operations and shared result and policy classes
  ([#177](https://github.com/NVIDIA/yaml-sigil-rs/pull/177))

### Fixed

- *(signing)* sample fresh P-256 nonces ([#168](https://github.com/NVIDIA/yaml-sigil-rs/pull/168))

### Other

- clarify crate contracts and contributor guidance

## [0.6.0-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-wasm-v0.6.0-rc.1...yaml-sigil-wasm-v0.6.0-rc.2) - 2026-09-22

### Changed

- Raise the `zeroize` dependency requirement from `1.8` to `1.9`.
- Advance the four implementation-crate dependencies to `0.6.0-rc.2` for the
  coordinated release.

## [0.6.0-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/releases/tag/yaml-sigil-wasm-v0.6.0-rc.1) - 2026-09-18

### Added

- *(release)* enable Wasm source crate publication ([#157](https://github.com/NVIDIA/yaml-sigil-rs/pull/157))
- *(crypto)* [**breaking**] upgrade dependencies and SSH-agent example ([#140](https://github.com/NVIDIA/yaml-sigil-rs/pull/140))
- *(wasm)* add resource-aware JavaScript bindings

### Fixed

- *(wasm)* stabilize JavaScript byte input copying

### Other

- editorial pass ([#159](https://github.com/NVIDIA/yaml-sigil-rs/pull/159))
- *(wasm)* mark WebAssembly support experimental
