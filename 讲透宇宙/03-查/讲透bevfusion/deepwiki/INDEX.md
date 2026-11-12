# DeepWiki 索引 — mit-han-lab/bevfusion

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-30
> 结构 19 页 · 全文 186410 字符

- [1 Overview](1-overview.md)
- [2 System Architecture](2-system-architecture.md)
  - [2.1 Data Flow](2.1-data-flow.md)
- [3 Data Processing Pipeline](3-data-processing-pipeline.md)
  - [3.1 Data Loading](3.1-data-loading.md)
  - [3.2 Data Augmentation & Transformation](3.2-data-augmentation-transformation.md)
  - [3.3 Data Formatting](3.3-data-formatting.md)
- [4 Model Components](4-model-components.md)
  - [4.1 Camera Encoder](4.1-camera-encoder.md)
  - [4.2 LiDAR Encoder](4.2-lidar-encoder.md)
  - [4.3 View Transformation](4.3-view-transformation.md)
  - [4.4 Multi-Modal Fusion](4.4-multi-modal-fusion.md)
  - [4.5 Detection and Segmentation Heads](4.5-detection-and-segmentation-heads.md)
- [5 CUDA Operations](5-cuda-operations.md)
  - [5.1 Point Cloud Processing Operations](5.1-point-cloud-processing-operations.md)
  - [5.2 Sparse Convolution Operations](5.2-sparse-convolution-operations.md)
- [6 Training and Evaluation](6-training-and-evaluation.md)
- [7 Configuration System](7-configuration-system.md)
- [8 Deployment](8-deployment.md)
