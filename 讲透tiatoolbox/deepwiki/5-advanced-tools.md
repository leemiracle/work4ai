<!-- source: DeepWiki mcp.deepwiki.com · repo TissueImageAnalytics/tiatoolbox · page 5 Advanced Tools · fetched 2026-10-21 -->

# Advanced Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/07-advanced-modeling.ipynb](examples/07-advanced-modeling.ipynb)
- [examples/full-pipelines/slide-graph.ipynb](examples/full-pipelines/slide-graph.ipynb)
- [examples/inference-pipelines/idars.ipynb](examples/inference-pipelines/idars.ipynb)
- [examples/inference-pipelines/slide-graph.ipynb](examples/inference-pipelines/slide-graph.ipynb)
- [tiatoolbox/tools/graph.py](tiatoolbox/tools/graph.py)
- [tiatoolbox/tools/pyramid.py](tiatoolbox/tools/pyramid.py)
- [tiatoolbox/tools/stainaugment.py](tiatoolbox/tools/stainaugment.py)
- [tiatoolbox/tools/tissuemask.py](tiatoolbox/tools/tissuemask.py)

</details>



This document covers specialized tools and advanced workflows in TIAToolbox that extend beyond basic WSI reading and model inference. These tools enable sophisticated analysis pipelines including graph-based slide representation, multi-resolution tile pyramid generation, advanced image preprocessing, and specialized visualization capabilities.

For basic WSI processing and model inference, see [Model and Inference Systems](#4). For fundamental image processing operations, see [Image Processing Pipeline](#3).

## Overview

TIAToolbox's advanced tools provide specialized functionality for complex computational pathology workflows. These tools operate at a higher level than basic image processing, enabling researchers to implement cutting-edge methods and create custom analysis pipelines.

```mermaid
graph TB
    subgraph "Advanced Analysis Tools"
        GraphTools["SlideGraphConstructor<br/>Graph analysis workflows"]
        PyramidTools["TilePyramidGenerator<br/>Multi-resolution tiling"]
        AugmentTools["StainAugmentor<br/>Advanced preprocessing"]
        MaskTools["TissueMasker<br/>Tissue segmentation"]
        VisTools["Visualization<br/>Advanced rendering"]
    end
    
    subgraph "Core Systems"
        WSIReader["WSI Reading System"]
        ModelEngine["Model Inference Engines"]
        AnnotationStore["Annotation Management"]
    end
    
    subgraph "Output Applications"
        Research["Research Pipelines"]
        WebViewing["Web Visualization"]
        DataAugmentation["Training Data"]
        SlideAnalysis["Slide-level Analysis"]
    end
    
    WSIReader --> GraphTools
    WSIReader --> PyramidTools
    WSIReader --> MaskTools
    
    ModelEngine --> GraphTools
    ModelEngine --> AugmentTools
    
    AnnotationStore --> VisTools
    AnnotationStore --> PyramidTools
    
    GraphTools --> SlideAnalysis
    PyramidTools --> WebViewing
    AugmentTools --> DataAugmentation
    MaskTools --> Research
    VisTools --> WebViewing
```

Sources: [tiatoolbox/tools/graph.py:200-521](), [tiatoolbox/tools/pyramid.py:39-521](), [tiatoolbox/tools/stainaugment.py:15-250](), [tiatoolbox/tools/tissuemask.py:14-307]()

## Graph Construction and Analysis

The graph construction system enables slide-level analysis by representing WSIs as graphs where nodes correspond to tissue regions and edges encode spatial relationships. This approach is particularly useful for molecular prediction and understanding tissue architecture.

### SlideGraphConstructor Architecture

```mermaid
graph TB
    subgraph "Input Data"
        PatchFeatures["Patch Features<br/>Deep learning outputs"]
        PatchCoords["Patch Coordinates<br/>WSI spatial locations"]
    end
    
    subgraph "SlideGraphConstructor"
        FeatureFiltering["feature_range_thresh<br/>Remove invariant features"]
        SpatialIndexing["cKDTree<br/>Spatial neighbor search"]
        HybridClustering["Hybrid Clustering<br/>lambda_d, lambda_f weights"]
        ClusterCentroids["Cluster Centroids<br/>Mean features & coordinates"]
        DelaunayTri["delaunay_adjacency<br/>Spatial connectivity"]
        EdgeConstruction["affinity_to_edge_index<br/>Graph edge creation"]
    end
    
    subgraph "Output Graph"
        GraphDict["Graph Dictionary<br/>x, edge_index, coordinates"]
        NodeFeatures["Node Features<br/>Aggregated patch features"]
        EdgeIndex["Edge Index<br/>Node connectivity matrix"]
        NodeCoords["Node Coordinates<br/>WSI spatial positions"]
    end
    
    PatchFeatures --> FeatureFiltering
    PatchCoords --> SpatialIndexing
    
    FeatureFiltering --> HybridClustering
    SpatialIndexing --> HybridClustering
    
    HybridClustering --> ClusterCentroids
    ClusterCentroids --> DelaunayTri
    DelaunayTri --> EdgeConstruction
    
    EdgeConstruction --> GraphDict
    GraphDict --> NodeFeatures
    GraphDict --> EdgeIndex
    GraphDict --> NodeCoords
```

Sources: [tiatoolbox/tools/graph.py:200-417](), [examples/full-pipelines/slide-graph.ipynb:583-1387]()

The `SlideGraphConstructor.build` method implements hybrid hierarchical clustering that combines spatial and feature-space distances:

- **Spatial Distance**: Computed using coordinates in WSI space with `lambda_d` weighting
- **Feature Distance**: Computed using deep learning features with `lambda_f` weighting  
- **Hybrid Similarity**: `1 - exp(-lambda_d * spatial_dist) * exp(-lambda_f * feature_dist)`
- **Clustering**: Hierarchical clustering with threshold `lambda_h`
- **Connectivity**: Delaunay triangulation of cluster centroids with distance threshold `connectivity_distance`

### Graph Construction Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `lambda_d` | 3.0e-3 | Spatial distance weighting |
| `lambda_f` | 1.0e-3 | Feature distance weighting |
| `lambda_h` | 0.8 | Clustering threshold |
| `connectivity_distance` | 4000 | Maximum spatial connection distance |
| `neighbour_search_radius` | 2000 | Spatial neighbor search radius |
| `feature_range_thresh` | 1e-4 | Minimum feature variance threshold |

Sources: [tiatoolbox/tools/graph.py:234-417]()

### Graph Visualization

The `SlideGraphConstructor.visualise` method provides sophisticated graph visualization with customizable node coloring and sizing:

```mermaid
graph LR
    subgraph "Visualization Pipeline"
        GraphInput["Graph Dictionary<br/>x, edge_index, coordinates"]
        ColorFunction["Color Function<br/>_umap_reducer (default)"]
        SizeFunction["Size Function<br/>Static or dynamic sizing"]
        EdgeRendering["Edge Rendering<br/>LineCollection"]
        NodeRendering["Node Rendering<br/>Scatter plot"]
    end
    
    subgraph "Color Options"
        UMAPColors["UMAP Embedding<br/>3D RGB projection"]
        CustomColors["Custom Colors<br/>User-defined values"]
        FunctionColors["Function Colors<br/>Callable color mapping"]
    end
    
    GraphInput --> ColorFunction
    GraphInput --> SizeFunction
    GraphInput --> EdgeRendering
    GraphInput --> NodeRendering
    
    ColorFunction --> UMAPColors
    ColorFunction --> CustomColors
    ColorFunction --> FunctionColors
```

Sources: [tiatoolbox/tools/graph.py:418-521]()

## Tile Pyramid Generation

The tile pyramid system creates multi-resolution tiled representations of WSIs for efficient web viewing and progressive loading. It supports multiple output formats including generic pyramids, DeepZoom, and Zoomify.

### Pyramid Generator Architecture

```mermaid
graph TB
    subgraph "TilePyramidGenerator"
        WSIInput["WSIReader<br/>Source WSI"]
        LevelCalculation["level_count<br/>Calculate pyramid levels"]
        TileCoordination["get_tile<br/>Extract tile at level,x,y"]
        ThumbnailGeneration["get_thumb_tile<br/>Overview thumbnail"]
        OutputGeneration["dump<br/>Write to container"]
    end
    
    subgraph "Configuration"
        TileSize["tile_size: 256<br/>Base tile dimensions"]
        Downsample["downsample: 2<br/>Level scaling factor"]
        Overlap["overlap: 0<br/>Tile edge overlap"]
    end
    
    subgraph "Output Formats"
        Directory["Directory Structure<br/>Individual tile files"]
        ZipContainer["ZIP Archive<br/>Compressed tiles"]
        TarContainer["TAR Archive<br/>Compressed tiles"]
    end
    
    subgraph "Specialized Generators"
        ZoomifyGen["ZoomifyGenerator<br/>Zoomify format support"]
        AnnotationGen["AnnotationTileGenerator<br/>Annotation rendering"]
    end
    
    WSIInput --> LevelCalculation
    TileSize --> TileCoordination
    Downsample --> TileCoordination
    Overlap --> TileCoordination
    
    LevelCalculation --> TileCoordination
    TileCoordination --> ThumbnailGeneration
    ThumbnailGeneration --> OutputGeneration
    
    OutputGeneration --> Directory
    OutputGeneration --> ZipContainer
    OutputGeneration --> TarContainer
    
    TilePyramidGenerator --> ZoomifyGen
    TilePyramidGenerator --> AnnotationGen
```

Sources: [tiatoolbox/tools/pyramid.py:39-402](), [tiatoolbox/tools/pyramid.py:403-483](), [tiatoolbox/tools/pyramid.py:485-521]()

### Tile Generation Process

The `get_tile` method implements the core tile extraction logic:

1. **Level Validation**: Verify requested level exists in pyramid
2. **Coordinate Calculation**: Convert tile indices to WSI baseline coordinates
3. **Scale Computation**: Calculate downsample factor for level
4. **Bounds Calculation**: Determine tile bounds with overlap
5. **Image Reading**: Extract image data via `WSIReader.read_rect`
6. **Format Conversion**: Convert to PIL Image for output

### ZoomifyGenerator Enhancements

The `ZoomifyGenerator` extends the base pyramid generator with Zoomify-specific features:

- **Tile Grouping**: Groups tiles into folders of 256 tiles each via `tile_group`
- **Path Generation**: Creates Zoomify-compatible paths via `tile_path`
- **Naming Convention**: Uses `TileGroup{g}/{z}-{x}-{y}.jpg` format

Sources: [tiatoolbox/tools/pyramid.py:403-483]()

### AnnotationTileGenerator

The `AnnotationTileGenerator` creates tile pyramids that render annotations overlaid on transparent backgrounds:

```mermaid
graph LR
    subgraph "Annotation Rendering"
        WSIMeta["WSIMeta<br/>Slide metadata"]
        AnnotationStore["AnnotationStore<br/>Annotation data"]
        AnnotationRenderer["AnnotationRenderer<br/>Rendering engine"]
        TileGeneration["Tile Generation<br/>Rendered overlay tiles"]
    end
    
    subgraph "Rendering Pipeline"
        SpatialQuery["Spatial Query<br/>Annotations in tile bounds"]
        GeometryRender["Geometry Rendering<br/>Shapes to pixels"]
        ColorMapping["Color Mapping<br/>Category to color"]
        AlphaBlending["Alpha Blending<br/>Transparency handling"]
    end
    
    WSIMeta --> TileGeneration
    AnnotationStore --> SpatialQuery
    AnnotationRenderer --> GeometryRender
    
    SpatialQuery --> GeometryRender
    GeometryRender --> ColorMapping
    ColorMapping --> AlphaBlending
    AlphaBlending --> TileGeneration
```

Sources: [tiatoolbox/tools/pyramid.py:485-521]()

## Stain Augmentation

The `StainAugmentor` provides advanced stain normalization and augmentation capabilities for improving model robustness and training data diversity.

### StainAugmentor Architecture

```mermaid
graph TB
    subgraph "StainAugmentor"
        MethodSelection["method<br/>vahadane or macenko"]
        StainMatrixMgmt["stain_matrix<br/>Predefined or extracted"]
        ParameterControl["sigma1, sigma2<br/>Augmentation parameters"]
        TissueMasking["augment_background<br/>Selective augmentation"]
    end
    
    subgraph "Processing Pipeline"
        StainExtraction["Stain Extraction<br/>Matrix + concentrations"]
        TissueMaskGen["Tissue Mask<br/>get_luminosity_tissue_mask"]
        ConcentrationMod["Concentration Modification<br/>alpha * conc + beta"]
        ImageReconstruction["Image Reconstruction<br/>255 * exp(-matrix @ conc)"]
    end
    
    subgraph "Integration Options"
        Standalone["Standalone Usage<br/>fit + augment"]
        Albumentations["Albumentations<br/>Pipeline integration"]
    end
    
    MethodSelection --> StainExtraction
    StainMatrixMgmt --> StainExtraction
    ParameterControl --> ConcentrationMod
    TissueMasking --> TissueMaskGen
    
    StainExtraction --> ConcentrationMod
    TissueMaskGen --> ConcentrationMod
    ConcentrationMod --> ImageReconstruction
    
    StainAugmentor --> Standalone
    StainAugmentor --> Albumentations
```

Sources: [tiatoolbox/tools/stainaugment.py:15-250]()

### Augmentation Parameters

The stain augmentation process modifies stain concentrations using random parameters:

- **Alpha (Scale)**: Random value in `[1-sigma1, 1+sigma1]` range
- **Beta (Shift)**: Random value in `[-sigma2, sigma2]` range
- **Per-Stain**: Applied independently to each stain channel
- **Tissue-Selective**: Can be limited to tissue regions only

The augmented concentrations are computed as: `augmented_conc = alpha * original_conc + beta`

Sources: [tiatoolbox/tools/stainaugment.py:177-206]()

## Tissue Masking

The tissue masking system provides automated tissue detection and background removal capabilities essential for WSI analysis workflows.

### TissueMasker Hierarchy

```mermaid
graph TB
    subgraph "TissueMasker ABC"
        AbstractMasker["TissueMasker<br/>Abstract base class"]
        FitMethod["fit(images, masks)<br/>Learn parameters"]
        TransformMethod["transform(images)<br/>Generate masks"]
        FitTransformMethod["fit_transform<br/>Combined operation"]
    end
    
    subgraph "Otsu Implementation"
        OtsuMasker["OtsuTissueMasker<br/>Threshold-based masking"]
        ThresholdCalculation["threshold_otsu<br/>Automatic threshold"]
        GrayscaleConversion["RGB2GRAY<br/>Color conversion"]
        BinaryThresholding["Binary Threshold<br/>Tissue vs background"]
    end
    
    subgraph "Morphological Enhancement"
        MorphMasker["MorphologicalMasker<br/>Advanced post-processing"]
        RegionFiltering["Connected Components<br/>Small region removal"]
        MorphDilation["Morphological Dilation<br/>Gap filling"]
        KernelScaling["Kernel Sizing<br/>MPP-based scaling"]
    end
    
    AbstractMasker --> OtsuMasker
    OtsuMasker --> MorphMasker
    
    FitMethod --> ThresholdCalculation
    TransformMethod --> GrayscaleConversion
    GrayscaleConversion --> BinaryThresholding
    
    BinaryThresholding --> RegionFiltering
    RegionFiltering --> MorphDilation
    KernelScaling --> MorphDilation
```

Sources: [tiatoolbox/tools/tissuemask.py:14-307]()

### MorphologicalMasker Features

The `MorphologicalMasker` extends Otsu's method with spatial processing:

- **Scale-Aware Processing**: Kernel size computed from MPP or objective power
- **Small Region Removal**: Connected component analysis with size thresholding  
- **Morphological Dilation**: Gap filling using elliptical structuring elements
- **Automatic Scaling**: Default kernel size of `64/mpp` pixels

Sources: [tiatoolbox/tools/tissuemask.py:167-307]()

## Advanced Modeling Integration

The advanced tools integrate seamlessly with TIAToolbox's modeling framework to enable sophisticated analysis workflows.

### Custom Model Integration

```mermaid
graph TB
    subgraph "Custom Model Framework"
        ModelABC["ModelABC<br/>Abstract model interface"]
        InferBatch["infer_batch<br/>Batch inference method"]
        PreprocFunc["preproc<br/>Preprocessing function"]
        PostprocFunc["postproc<br/>Post-processing function"]
        ForwardMethod["forward<br/>Model forward pass"]
    end
    
    subgraph "Advanced Integration"
        CustomPreproc["Custom Preprocessing<br/>Stain normalization injection"]
        BatchOptimization["Batch Optimization<br/>GPU acceleration"]
        ModelChaining["Model Chaining<br/>Multi-stage pipelines"]
        ResultMerging["Result Merging<br/>WSI-level assembly"]
    end
    
    subgraph "Example Applications"
        BlurModel["BlurModel<br/>Focus scoring example"]
        FeatureExtraction["Feature Extraction<br/>Deep feature workflows"]
        MultiTaskModels["Multi-Task Models<br/>Combined outputs"]
    end
    
    ModelABC --> CustomPreproc
    InferBatch --> BatchOptimization
    PreprocFunc --> CustomPreproc
    PostprocFunc --> ResultMerging
    
    CustomPreproc --> BlurModel
    BatchOptimization --> FeatureExtraction
    ModelChaining --> MultiTaskModels
```

Sources: [examples/07-advanced-modeling.ipynb:343-577](), [tiatoolbox/models/models_abc.py]()

### Pipeline Workflows

Advanced tools enable complex multi-stage analysis pipelines:

1. **Feature Extraction**: Extract deep features or cellular composition from WSI patches
2. **Graph Construction**: Build slide-level graphs from extracted features and coordinates  
3. **Graph Analysis**: Apply graph neural networks for slide-level prediction
4. **Visualization**: Render results as overlays or interactive visualizations
5. **Export**: Generate tile pyramids for web viewing or further analysis

Sources: [examples/full-pipelines/slide-graph.ipynb:583-1387](), [examples/inference-pipelines/slide-graph.ipynb:448-1165]()

---

