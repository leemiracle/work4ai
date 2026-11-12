# DeepWiki 索引 — google-deepmind/xarray_jax

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 23 页 · 全文 153703 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started](1.1-getting-started.md)
  - [1.2 Key Concepts and Design Philosophy](1.2-key-concepts-and-design-philosophy.md)
- [2 Core Architecture](2-core-architecture.md)
  - [2.1 PyTree Registration (pytree.py)](2.1-pytree-registration-pytree.py.md)
  - [2.2 Core Constructors and Coordinate Management (core.py)](2.2-core-constructors-and-coordinate-management-core.py.md)
- [3 JAX Transformations](3-jax-transformations.md)
  - [3.1 vmap and pmap](3.1-vmap-and-pmap.md)
  - [3.2 scan](3.2-scan.md)
  - [3.3 tree_map_variables and tree_map_with_dims](3.3-tree-map-variables-and-tree-map-with-dims.md)
- [4 Coordinate System](4-coordinate-system.md)
  - [4.1 Static Coordinates](4.1-static-coordinates.md)
  - [4.2 JAX Coordinates (jax_coords)](4.2-jax-coordinates-jax-coords.md)
- [5 Public API Reference](5-public-api-reference.md)
  - [5.1 Data Structures and Constructors](5.1-data-structures-and-constructors.md)
  - [5.2 Data Extraction Utilities](5.2-data-extraction-utilities.md)
- [6 Testing](6-testing.md)
  - [6.1 Integration Tests (xarray_jax_test.py)](6.1-integration-tests-xarray-jax-test.py.md)
  - [6.2 PyTree and Transform Tests (pytree_test.py, jax_transforms_test.py)](6.2-pytree-and-transform-tests-pytree-test.py-jax-transforms-test.py.md)
- [7 Contributing and Project Metadata](7-contributing-and-project-metadata.md)
  - [7.1 Contributing Guide](7.1-contributing-guide.md)
  - [7.2 Package Configuration and Versioning](7.2-package-configuration-and-versioning.md)
- [8 Glossary](8-glossary.md)

## 附：结构清单外的页
- [Flatten and Unflatten Internals](x1-flatten-and-unflatten-internals.md)
- [NonArrayLeafWrapper and Dimension Change Handling](x2-nonarrayleafwrapper-and-dimension-change-handling.md)
