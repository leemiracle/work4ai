# DeepWiki 索引 — NVIDIA/Dataset_Synthesizer

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 25 页 · 全文 387940 字符

- [1 Overview](1-overview.md)
- [2 Getting Started](2-getting-started.md)
  - [2.1 Repository Structure](2.1-repository-structure.md)
  - [2.2 Git LFS Configuration](2.2-git-lfs-configuration.md)
- [3 Architecture Overview](3-architecture-overview.md)
  - [3.1 DomainRandomizationDNN Module](3.1-domainrandomizationdnn-module.md)
  - [3.2 NVSceneCapturer Module](3.2-nvscenecapturer-module.md)
  - [3.3 NVDataObject Module](3.3-nvdataobject-module.md)
- [4 Domain Randomization System](4-domain-randomization-system.md)
  - [4.1 Scene Manager (ADRSceneManager)](4.1-scene-manager-adrscenemanager.md)
  - [4.2 Actor Spawning (AGroupActorManager)](4.2-actor-spawning-agroupactormanager.md)
  - [4.3 Randomization Utilities](4.3-randomization-utilities.md)
- [5 Scene Capture & Annotation](5-scene-capture-annotation.md)
  - [5.1 Annotated Actors](5.1-annotated-actors.md)
  - [5.2 Scene Capture Component](5.2-scene-capture-component.md)
  - [5.3 Camera Configuration](5.3-camera-configuration.md)
- [6 Segmentation & Masking](6-segmentation-masking.md)
  - [6.1 Object Mask Manager](6.1-object-mask-manager.md)
  - [6.2 Segmentation Strategies](6.2-segmentation-strategies.md)
- [7 Data Export](7-data-export.md)
  - [7.1 Image Export System](7.1-image-export-system.md)
  - [7.2 Data Object Serialization](7.2-data-object-serialization.md)
- [8 Utility Components](8-utility-components.md)
  - [8.1 Coordinate Visualization](8.1-coordinate-visualization.md)
  - [8.2 Documentation Resources](8.2-documentation-resources.md)

## 附：结构清单外的页
- [Appearance Randomization](x1-appearance-randomization.md)
- [Asset Streaming](x2-asset-streaming.md)
- [Transform Randomization](x3-transform-randomization.md)
