# Changelog

All notable changes to these packages will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/). Icon name
removals and export renames are breaking changes (MAJOR). New icons and new
exports are minor releases. Bug fixes to package code are patch releases.

Individual package changelogs are in each package directory:
- [packages/gui-icons/CHANGELOG.md](./packages/gui-icons/CHANGELOG.md)
- [packages/react-gui-icons/CHANGELOG.md](./packages/react-gui-icons/CHANGELOG.md)
- [packages/micro-gui-icons/CHANGELOG.md](./packages/micro-gui-icons/CHANGELOG.md)
- [packages/react-micro-gui-icons/CHANGELOG.md](./packages/react-micro-gui-icons/CHANGELOG.md)

---

## [1.0.0] - 2026-09-16

### Added

- Initial public release of all four packages: `@nvidia/gui-icons`,
  `@nvidia/micro-gui-icons`, `@nvidia/react-gui-icons`,
  `@nvidia/react-micro-gui-icons`.
- 748 GUI Icons and 24 Micro GUI Icons, each in `line` and `fill` variants,
  shipped as raw SVG assets plus TypeScript name and metadata constants.
- React components for every icon, rendered via sprite injection
  (`<use href="#id">`), with tree-shakable per-icon subpath imports and a
  declarative `<NvidiaGuiIconSprite>` / `<NvidiaMicroGuiIconSprite>` escape
  hatch for SSR and static rendering.
- Dual licensing throughout: Apache-2.0 for code, CC-BY-4.0 for
  documentation, assets, and icons. Every published tarball ships `LICENSE`,
  `NOTICE`, and `THIRD_PARTY_NOTICES`.
