# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.2-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.6.2-rc.1...yaml-sigil-signing-v0.6.2-rc.2) - 2026-10-28

### Changed

- Adopt `yaml-sigil-traits 0.4.2-rc.1` as the shared public contract.

## [0.6.2-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.6.1...yaml-sigil-signing-v0.6.2-rc.1) - 2026-10-27

### Changed

- Prepare a maintenance RC after the compatible dependency refresh
  ([#186](https://github.com/NVIDIA/yaml-sigil-rs/pull/186)).
- Refresh application lockfiles with `cargo update` to pick up compatible
  dependency fixes.

## [0.6.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.6.1-rc.1...yaml-sigil-signing-v0.6.1) - 2026-10-12

### Changed

- Promote `0.6.1-rc.1` to stable without further API or behavior changes.

## [0.6.1-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.6.0...yaml-sigil-signing-v0.6.1-rc.1) - 2026-10-12

### Changed

- Advance implementation dependencies to `0.6.1-rc.1` for the YAML parser
  update.
- Accept compatible `yaml-sigil-traits` patch releases with `~0.4.1`.

## [0.6.0](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.6.0-rc.3...yaml-sigil-signing-v0.6.0) - 2026-09-24

### Changed

- Promote `0.6.0-rc.3` to stable without further API or behavior changes.

## [0.6.0-rc.3](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.6.0-rc.2...yaml-sigil-signing-v0.6.0-rc.3) - 2026-09-24

### Added

- expose the existing Rust API through `v1alpha1` while retaining unqualified
  paths ([#177](https://github.com/NVIDIA/yaml-sigil-rs/pull/177))
- *(crypto)* add P-256 encoding helpers ([#169](https://github.com/NVIDIA/yaml-sigil-rs/pull/169))

### Changed

- *(signing)* change synchronous provider signing to accept a callback per
  operation; `ProviderSigningKeyBuilder` now binds only public-key bytes
  ([#170](https://github.com/NVIDIA/yaml-sigil-rs/pull/170))
- use `yaml-sigil-traits` `=0.4.1` for the shared traits and data types

### Fixed

- *(signing)* sample fresh P-256 nonces ([#168](https://github.com/NVIDIA/yaml-sigil-rs/pull/168))

### Other

- clarify crate contracts and contributor guidance

## [0.6.0-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.6.0-rc.1...yaml-sigil-signing-v0.6.0-rc.2) - 2026-09-22

### Changed

- Advance the `yaml-sigil-core` and `yaml-sigil-transcription` dependencies to
  `0.6.0-rc.2` for the coordinated release. No crate implementation changes.

## [0.6.0-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.5.1...yaml-sigil-signing-v0.6.0-rc.1) - 2026-09-18

### Added

- *(crypto)* [**breaking**] upgrade dependencies and SSH-agent example ([#140](https://github.com/NVIDIA/yaml-sigil-rs/pull/140))
- *(wasm)* add resource-aware JavaScript bindings
- *(crypto)* add async providers and runnable examples
- *(signing)* add qualified provider signing
- add opt-in artifact resource limits ([#107](https://github.com/NVIDIA/yaml-sigil-rs/pull/107))
- *(core)* [**breaking**] hide Buffa behind protobuf facade

### Fixed

- *(crypto)* preserve thread safety and isolate provider key bindings

### Other

- editorial pass ([#159](https://github.com/NVIDIA/yaml-sigil-rs/pull/159))
- document local cryptographic providers
- *(core)* document protobuf security boundaries

## [0.5.0](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.5.0-rc.2...yaml-sigil-signing-v0.5.0) - 2026-09-06

### Other

- *(deps)* refresh Rust dependencies and Buf tooling ([#98](https://github.com/NVIDIA/yaml-sigil-rs/pull/98))
- *(core)* document protobuf resource usage ([#95](https://github.com/NVIDIA/yaml-sigil-rs/pull/95))

## [0.5.0-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.5.0-rc.1...yaml-sigil-signing-v0.5.0-rc.2) - 2026-09-05

### Other

- consolidate repository history

## [0.5.0-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.4.0-rc.2...yaml-sigil-signing-v0.5.0-rc.1) - 2026-08-21

### Fixed

- *(transcoding)* parse markerless carriers
- *(signing)* preserve protobuf payload bytes

## [0.4.0-rc.2](https://github.com/NVIDIA/yaml-sigil-rs/compare/yaml-sigil-signing-v0.4.0-rc.1...yaml-sigil-signing-v0.4.0-rc.2) - 2026-08-20

### Other

- improve crate discovery and reader guidance

## [0.4.0-rc.1](https://github.com/NVIDIA/yaml-sigil-rs/releases/tag/yaml-sigil-signing-v0.4.0-rc.1) - 2026-08-18

### Fixed

- *(core)* prevent YAML field injection during serialization
- *(verification)* reject signature whitespace
- *(security)* prevent signature carrier marker injection

### Other

- *(release)* add Trusted Publishing workflow
- *(release)* prepare YamlSigil 0.4.0-rc.1 crates
- align crate package contents
- add hosted and local validation
- *(metadata)* add crates.io contact
- include compliance docs in crate packages
- normalize packaged license files
- add SPDX metadata to project files
- *(porting)* initial porting
