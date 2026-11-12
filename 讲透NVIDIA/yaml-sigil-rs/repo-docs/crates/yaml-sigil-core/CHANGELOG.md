# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.2-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.6.2-rc.1...yaml-sigil-core-v0.6.2-rc.2) - 2026-10-28

### Changed

- Adopt `yaml-sigil-traits 0.4.2-rc.1` as the shared public contract.
- Raise the Cargo-resolved Buf tooling minimum to `1.75.0`.

## [0.6.2-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.6.1...yaml-sigil-core-v0.6.2-rc.1) - 2026-10-27

### Changed

- Prepare a maintenance RC after the compatible dependency refresh
  ([#186](https://github.com/NVIDIA/yaml-sigil-rs/pull/186)).
- Refresh application lockfiles with `cargo update` to pick up compatible
  dependency fixes.

## [0.6.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.6.1-rc.1...yaml-sigil-core-v0.6.1) - 2026-10-12

### Changed

- Promote `0.6.1-rc.1` to stable without further API or behavior changes.

## [0.6.1-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.6.0...yaml-sigil-core-v0.6.1-rc.1) - 2026-10-12

### Fixed

- Require the private YAML backend `noyalib` `=0.0.57` and add regression
  tests for typed parser budgets.

### Changed

- Accept compatible `yaml-sigil-traits` patch releases with `~0.4.1`.
- Allow compatible patch updates for Buffa dependencies.

## [0.6.0](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.6.0-rc.3...yaml-sigil-core-v0.6.0) - 2026-09-24

### Changed

- Promote `0.6.0-rc.3` to stable without further API or behavior changes.

## [0.6.0-rc.3](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.6.0-rc.2...yaml-sigil-core-v0.6.0-rc.3) - 2026-09-24

### Added

- expose the existing Rust API through `v1alpha1` while retaining unqualified
  paths ([#177](https://github.com/NVIDIA/yaml-sigil-rs/pull/177))
- *(crypto)* add P-256 encoding helpers ([#169](https://github.com/NVIDIA/yaml-sigil-rs/pull/169))

### Changed

- use `yaml-sigil-traits` `=0.4.1` for the shared traits and data types

### Other

- *(spec)* advance specification review to 30b143f ([#176](https://github.com/NVIDIA/yaml-sigil-rs/pull/176))
- clarify crate contracts and contributor guidance

## [0.6.0-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.6.0-rc.1...yaml-sigil-core-v0.6.0-rc.2) - 2026-09-22

### Changed

- Update the private YAML backend requirement from `noyalib` `0.0.43` to
  `0.0.46` and refresh the backend interoperability documentation.
- Require stable `buf-tools` `1.73.0` or newer for protobuf build tooling.

## [0.6.0-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.5.1...yaml-sigil-core-v0.6.0-rc.1) - 2026-09-18

### Added

- *(crypto)* [**breaking**] upgrade dependencies and SSH-agent example ([#140](https://github.com/NVIDIA/yaml-sigil-rs/pull/140))
- *(wasm)* add resource-aware JavaScript bindings
- add opt-in artifact resource limits ([#107](https://github.com/NVIDIA/yaml-sigil-rs/pull/107))
- *(core)* [**breaking**] hide Buffa behind protobuf facade
- Add opaque owned protobuf messages and zero-copy borrowed views that retain
  unknown fields and unknown algorithm numbers.

### Other

- editorial pass ([#159](https://github.com/NVIDIA/yaml-sigil-rs/pull/159))
- *(spec)* advance non-normative specification review ([#156](https://github.com/NVIDIA/yaml-sigil-rs/pull/156))
- *(core)* define serialization backend boundary ([#108](https://github.com/NVIDIA/yaml-sigil-rs/pull/108))
- *(core)* document protobuf security boundaries
- *(core)* pin protobuf wire compatibility
- *(buf)* adopt minimum toolchain requirements ([#148](https://github.com/NVIDIA/yaml-sigil-rs/pull/148))

### Changed

- *(protobuf)* [**breaking**] Keep generated Buffa types private and require
  callers to use the stable `yaml_sigil_core::pb` construction, access,
  decode, and fallible encode methods.

## [0.5.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.5.0...yaml-sigil-core-v0.5.1) - 2026-09-15

### Fixed

- *(core)* normalize quoted signature keys with bounded decoding ([#131](https://github.com/NVIDIA/yaml-sigil-rs/pull/131))

### Other

- *(core)* make signature scalar parsing policies explicit ([#129](https://github.com/NVIDIA/yaml-sigil-rs/pull/129))

## [0.5.1-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.5.0...yaml-sigil-core-v0.5.1-rc.2) - 2026-09-15

### Fixed

- *(core)* normalize quoted signature keys with bounded decoding ([#131](https://github.com/NVIDIA/yaml-sigil-rs/pull/131))

### Other

- *(core)* make signature scalar parsing policies explicit ([#129](https://github.com/NVIDIA/yaml-sigil-rs/pull/129))

## [0.5.1-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.5.0...yaml-sigil-core-v0.5.1-rc.1) - 2026-09-15

### Fixed

- *(core)* normalize quoted signature keys with bounded decoding ([#131](https://github.com/NVIDIA/yaml-sigil-rs/pull/131))

### Other

- *(core)* make signature scalar parsing policies explicit ([#129](https://github.com/NVIDIA/yaml-sigil-rs/pull/129))

## [0.5.0](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.5.0-rc.2...yaml-sigil-core-v0.5.0) - 2026-09-06

### Other

- *(deps)* refresh Rust dependencies and Buf tooling ([#98](https://github.com/NVIDIA/yaml-sigil-rs/pull/98))
- *(core)* document protobuf resource usage ([#95](https://github.com/NVIDIA/yaml-sigil-rs/pull/95))
- *(spec)* align with current specification ([#97](https://github.com/NVIDIA/yaml-sigil-rs/pull/97))

## [0.5.0-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.5.0-rc.1...yaml-sigil-core-v0.5.0-rc.2) - 2026-09-05

### Other

- consolidate repository history

## [0.5.0-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.4.0-rc.2...yaml-sigil-core-v0.5.0-rc.1) - 2026-08-21

### Fixed

- *(yaml)* bound signature document parsing

## [0.4.0-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-core-v0.4.0-rc.1...yaml-sigil-core-v0.4.0-rc.2) - 2026-08-20

### Other

- improve crate discovery and reader guidance

## [0.4.0-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/releases/tag/yaml-sigil-core-v0.4.0-rc.1) - 2026-08-18

### Fixed

- *(core)* prevent YAML field injection during serialization
- *(conformance)* absorb security clarification
- *(core)* scan YAML markers in constant memory
- *(core)* validate protobuf lengths portably
- *(core)* reject invalid protobuf tags
- *(core)* absorb upstream signature parsing updates
- *(core)* remove unreachable marker outcome
- *(core)* enforce signature document EOF
- *(security)* prevent signature carrier marker injection

### Other

- *(release)* add Trusted Publishing workflow
- *(release)* prepare YamlSigil 0.4.0-rc.1 crates
- align crate package contents
- add hosted and local validation
- *(metadata)* add crates.io contact
- *(schema)* import profile clarification
- include compliance docs in crate packages
- normalize packaged license files
- add SPDX metadata to project files
- *(deps)* update noyalib to 0.0.13
- *(porting)* initial porting
