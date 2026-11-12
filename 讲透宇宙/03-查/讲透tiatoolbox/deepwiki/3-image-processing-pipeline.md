<!-- source: DeepWiki mcp.deepwiki.com · repo TissueImageAnalytics/tiatoolbox · page 3 Image Processing Pipeline · fetched 2026-10-21 -->

# Image Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/test_patch_extraction.py](tests/test_patch_extraction.py)
- [tests/test_utils.py](tests/test_utils.py)
- [tiatoolbox/tools/patchextraction.py](tiatoolbox/tools/patchextraction.py)
- [tiatoolbox/utils/image.py](tiatoolbox/utils/image.py)
- [tiatoolbox/utils/misc.py](tiatoolbox/utils/misc.py)
- [tiatoolbox/utils/transforms.py](tiatoolbox/utils/transforms.py)

</details>



## Purpose and Scope

The Image Processing Pipeline provides a comprehensive suite of preprocessing and image analysis tools that operate on whole slide images (WSIs) and standard images. This system handles fundamental image operations including I/O, transformations, patch extraction, and coordinate management. It serves as the foundation for preparing image data before feeding it to machine learning models and analysis engines.

For information about reading WSI formats, see [WSI Reading and Formats](#2.1). For model inference operations that consume processed images, see [Prediction Engines](#4.1). For stain-specific processing techniques, see [Stain Processing](#3.2).

## Core Image Processing Utilities

The foundation of image processing is built around basic I/O operations, contrast enhancement, and tissue detection utilities in the `misc` module.

### Basic Image Operations

```mermaid
graph TB
    subgraph "Image I/O Operations"
        imread["imread()"]
        imwrite["imwrite()"]
        load_stain_matrix["load_stain_matrix()"]
    end
    
    subgraph "Image Enhancement"
        contrast_enhancer["contrast_enhancer()"]
        get_luminosity_tissue_mask["get_luminosity_tissue_mask()"]
    end
    
    subgraph "Coordinate Utilities"
        mpp2objective_power["mpp2objective_power()"]
        objective_power2mpp["objective_power2mpp()"]
        ppu2mpp["ppu2mpp()"]
    end
    
    subgraph "Data Loading"
        read_locations["read_locations()"]
        grab_files_from_dir["grab_files_from_dir()"]
    end
    
    imread --> "NumPy arrays"
    imwrite --> "Image files"
    contrast_enhancer --> "Enhanced images"
    get_luminosity_tissue_mask --> "Binary tissue masks"
    
    style imread fill:#e1f5fe
    style imwrite fill:#e8f5e8
    style contrast_enhancer fill:#f3e5f5
```

**Core Image Processing Functions**
The `misc` module provides essential image processing functions that handle basic I/O and preprocessing operations. The `imread` and `imwrite` functions support multiple formats including standard images and NumPy arrays, while `contrast_enhancer` applies percentile-based intensity adjustment for improved visualization.

Sources: [tiatoolbox/utils/misc.py:142-201](), [tiatoolbox/utils/misc.py:391-431](), [tiatoolbox/utils/misc.py:247-276]()

### Tissue Detection and Masking

```mermaid
graph LR
    subgraph "Tissue Detection Pipeline"
        InputImage["Input Image"] --> ContrastEnhancement["contrast_enhancer()"]
        ContrastEnhancement --> ColorConversion["RGB to LAB conversion"]
        ColorConversion --> LuminosityChannel["Extract L channel"]
        LuminosityChannel --> ThresholdMask["Apply luminosity threshold"]
        ThresholdMask --> TissueMask["Binary tissue mask"]
    end
    
    subgraph "Coordinate Conversion"
        MPP["Microns per pixel"] --> ObjectivePower["mpp2objective_power()"]
        ObjectivePower --> CommonPower["mpp2common_objective_power()"]
        PPU["Pixels per unit"] --> MPPConversion["ppu2mpp()"]
    end
```

**Tissue Masking Workflow**
The `get_luminosity_tissue_mask` function implements a luminosity-based approach to identify tissue regions. It first enhances contrast using percentile normalization, converts to LAB color space, and applies thresholding on the L channel to separate tissue from background.

Sources: [tiatoolbox/utils/misc.py:247-276](), [tiatoolbox/utils/misc.py:391-431](), [tiatoolbox/utils/misc.py:279-331]()

## Patch Extraction System

The patch extraction system provides two main strategies for extracting regions from images: sliding window extraction and point-based extraction. Both approaches support mask-based filtering and various padding modes.

### Patch Extraction Architecture

```mermaid
graph TB
    subgraph "PatchExtractor Base Class"
        PatchExtractorABC["PatchExtractorABC"] --> PatchExtractor["PatchExtractor"]
        PatchExtractor --> SlidingWindowPatchExtractor["SlidingWindowPatchExtractor"]
        PatchExtractor --> PointsPatchExtractor["PointsPatchExtractor"]
    end
    
    subgraph "Core Methods"
        PatchExtractor --> get_coordinates["get_coordinates()"]
        PatchExtractor --> filter_coordinates["filter_coordinates()"]
        PatchExtractor --> _generate_location_df["_generate_location_df()"]
    end
    
    subgraph "Input Sources"
        WSIReader["WSIReader"] --> PatchExtractor
        VirtualWSIReader["VirtualWSIReader"] --> PatchExtractor
        AnnotationStore["AnnotationStore"] --> PatchExtractor
        NumpyArray["np.ndarray"] --> PatchExtractor
    end
    
    subgraph "Output"
        PatchExtractor --> PatchIterator["Patch Iterator"]
        PatchIterator --> PatchData["Individual Patches"]
    end
    
    style PatchExtractor fill:#e1f5fe
    style SlidingWindowPatchExtractor fill:#e8f5e8
    style PointsPatchExtractor fill:#f3e5f5
```

**Patch Extraction Hierarchy**
The patch extraction system is built around an abstract base class `PatchExtractorABC` with concrete implementations for different extraction strategies. The base `PatchExtractor` class provides common functionality for coordinate generation, mask filtering, and WSI integration.

Sources: [tiatoolbox/tools/patchextraction.py:97-200](), [tiatoolbox/tools/patchextraction.py:612-712](), [tiatoolbox/tools/patchextraction.py:714-785]()

### Coordinate Generation and Filtering

```mermaid
graph TD
    subgraph "Coordinate Generation"
        ImageShape["image_shape"] --> CoordGeneration["get_coordinates()"]
        PatchInputShape["patch_input_shape"] --> CoordGeneration
        StrideShape["stride_shape"] --> CoordGeneration
        CoordGeneration --> CoordinateList["coordinate_list (N×4 array)"]
    end
    
    subgraph "Mask-Based Filtering"
        CoordinateList --> FilterCoords["filter_coordinates()"]
        VirtualWSIReader["mask_reader"] --> FilterCoords
        MinMaskRatio["min_mask_ratio"] --> FilterCoords
        FilterCoords --> FilteredCoords["filtered coordinates"]
    end
    
    subgraph "Validation Steps"
        FilterCoords --> ScaleCoords["Scale coords to mask resolution"]
        ScaleCoords --> DefaultSelFunc["default_sel_func()"]
        DefaultSelFunc --> AreaCheck["Calculate patch area ratio"]
        AreaCheck --> ValidFlags["boolean flags array"]
    end
```

**Coordinate Processing Pipeline**
The `get_coordinates` method generates patch locations using a sliding window approach with configurable stride and boundary handling. The `filter_coordinates` method then validates these coordinates against a tissue mask, rejecting patches with insufficient tissue content based on the `min_mask_ratio` parameter.

Sources: [tiatoolbox/tools/patchextraction.py:483-609](), [tiatoolbox/tools/patchextraction.py:354-457](), [tiatoolbox/tools/patchextraction.py:436-453]()

### Factory Pattern and Extraction Methods

```mermaid
graph LR
    subgraph "Entry Point"
        get_patch_extractor["get_patch_extractor()"] --> MethodRouter{"method_name"}
    end
    
    subgraph "Extraction Strategies"
        MethodRouter -->|"point"| PointsExtractor["PointsPatchExtractor"]
        MethodRouter -->|"slidingwindow"| SlidingExtractor["SlidingWindowPatchExtractor"]
    end
    
    subgraph "Common Parameters"
        ExtractorParams["ExtractorParams"] --> PatchSize["patch_size"]
        ExtractorParams --> Resolution["resolution"]
        ExtractorParams --> Units["units"]
        ExtractorParams --> PadMode["pad_mode"]
        ExtractorParams --> InputMask["input_mask"]
    end
    
    subgraph "Specialized Parameters"
        PointsExtractor --> LocationsList["locations_list"]
        SlidingExtractor --> Stride["stride"]
        SlidingExtractor --> WithinBound["within_bound"]
    end
```

**Factory Pattern Implementation**
The `get_patch_extractor` function serves as a factory that instantiates the appropriate extractor class based on the specified method. It uses TypedDict classes (`ExtractorParams`, `PointsPatchExtractorParams`, `SlidingWindowPatchExtractorParams`) to define parameter interfaces for type safety.

Sources: [tiatoolbox/tools/patchextraction.py:35-96](), [tiatoolbox/tools/patchextraction.py:58-73](), [tiatoolbox/tools/patchextraction.py:75-95]()

## Image Transformations and Coordinate Management

The transforms module provides essential image manipulation and coordinate conversion utilities that support the broader image processing pipeline.

### Image Transformation Operations

```mermaid
graph TB
    subgraph "Core Transformations"
        imresize["imresize()"] --> OutputImage["Resized image"]
        rgb2od["rgb2od()"] --> ODImage["Optical density image"]
        od2rgb["od2rgb()"] --> RGBImage["RGB image"]
        background_composite["background_composite()"] --> CompositeImage["Background composite"]
    end
    
    subgraph "Coordinate Operations"
        bounds2locsize["bounds2locsize()"] --> LocationSize["(location, size)"]
        locsize2bounds["locsize2bounds()"] --> Bounds["(left, top, right, bottom)"]
        bounds2slices["bounds2slices()"] --> SliceObjects["slice objects"]
        pad_bounds["pad_bounds()"] --> PaddedBounds["padded bounds"]
    end
    
    subgraph "Interpolation Support"
        ScaleFactor["scale_factor"] --> imresize
        OutputSize["output_size"] --> imresize
        InterpolationMode["interpolation"] --> imresize
    end
    
    style imresize fill:#e1f5fe
    style rgb2od fill:#e8f5e8
    style bounds2locsize fill:#f3e5f5
```

**Transformation Pipeline**
The `imresize` function supports multiple interpolation modes and automatic dtype conversion to maintain numerical precision. The optical density conversion functions (`rgb2od`, `od2rgb`) enable stain separation workflows by converting between RGB and OD color spaces.

Sources: [tiatoolbox/utils/transforms.py:94-207](), [tiatoolbox/utils/transforms.py:209-257](), [tiatoolbox/utils/transforms.py:259-421]()

### Coordinate System Management

```mermaid
graph LR
    subgraph "Coordinate Representations"
        Bounds["(left, top, right, bottom)"] <--> LocationSize["(location, size)"]
        Bounds --> SliceObjects["slice(start, stop, stride)"]
        Bounds --> PaddedBounds["padded bounds"]
    end
    
    subgraph "Conversion Functions"
        bounds2locsize_func["bounds2locsize()"] --> LocationSize
        locsize2bounds_func["locsize2bounds()"] --> Bounds
        bounds2slices_func["bounds2slices()"] --> SliceObjects
        pad_bounds_func["pad_bounds()"] --> PaddedBounds
    end
    
    subgraph "Origin Support"
        OriginUpper["origin='upper'"] --> bounds2locsize_func
        OriginLower["origin='lower'"] --> bounds2locsize_func
    end
```

**Coordinate Conversion System**
The coordinate management system provides bidirectional conversion between different representations. The `bounds2locsize` function supports both upper and lower origin conventions, while `bounds2slices` enables direct indexing into NumPy arrays with optional stride support.

Sources: [tiatoolbox/utils/transforms.py:259-305](), [tiatoolbox/utils/transforms.py:307-334](), [tiatoolbox/utils/transforms.py:336-380](), [tiatoolbox/utils/transforms.py:382-421]()

## Advanced Image Reading Operations

The image module provides sophisticated reading capabilities that handle edge cases, sub-pixel coordinates, and various padding modes.

### Safe Padded Reading

```mermaid
graph TD
    subgraph "safe_padded_read Pipeline"
        InputBounds["bounds"] --> ValidateBounds["Validate integer bounds"]
        ValidateBounds --> NormalizePadding["normalize_padding_size()"]
        NormalizePadding --> CheckOverlap["Check image overlap"]
        CheckOverlap --> ReadRegion["Read overlapping region"]
        ReadRegion --> ApplyPadding["Apply edge padding"]
    end
    
    subgraph "Padding Support"
        PadMode["pad_mode"] --> PaddingFunc["np.pad()"]
        PadConstantValues["pad_constant_values"] --> PaddingFunc
        PadKwargs["pad_kwargs"] --> PaddingFunc
        PaddingFunc --> PaddedRegion["Padded image region"]
    end
    
    subgraph "Stride Handling"
        StrideParam["stride"] --> ConvOutSize["conv_out_size()"]
        ConvOutSize --> AdjustedBounds["stride-adjusted bounds"]
    end
```

**Safe Reading Implementation**
The `safe_padded_read` function handles reading from image regions that may extend beyond image boundaries. It normalizes padding specifications, calculates overlapping regions, and applies appropriate padding using NumPy's padding modes.

Sources: [tiatoolbox/utils/image.py:296-441](), [tiatoolbox/utils/image.py:32-72](), [tiatoolbox/utils/image.py:74-114]()

### Sub-Pixel Reading with Interpolation

```mermaid
graph TD
    subgraph "sub_pixel_read Workflow"
        SubPixelBounds["fractional bounds"] --> MakePositive["make_bounds_size_positive()"]
        MakePositive --> InterpolationPadding["Add interpolation padding"]
        InterpolationPadding --> ExpandToIntegers["Expand to integer bounds"]
        ExpandToIntegers --> ReadFunc["read_func() or direct read"]
        ReadFunc --> ResizeRegion["imresize() with interpolation"]
        ResizeRegion --> TrimPadding["Trim interpolation padding"]
        TrimPadding --> ApplyFlips["Apply flip corrections"]
    end
    
    subgraph "Interpolation Support"
        InterpolationMode["interpolation mode"] --> ResizeRegion
        ScalingFactors["scaling factors"] --> ResizeRegion
        OutputSizeParam["output_size"] --> ResizeRegion
    end
    
    subgraph "Custom Read Functions"
        ReadFuncParam["read_func"] --> CustomReader["Custom reading logic"]
        ReadKwargs["read_kwargs"] --> CustomReader
    end
```

**Sub-Pixel Reading Pipeline**
The `sub_pixel_read` function enables reading at fractional coordinates with various interpolation modes. It handles negative bounds by tracking flip operations, applies temporary padding to avoid interpolation artifacts, and supports custom read functions for specialized image sources.

Sources: [tiatoolbox/utils/image.py:443-739](), [tiatoolbox/utils/image.py:153-191](), [tiatoolbox/utils/image.py:193-294]()

## Integration with WSI Pipeline

The image processing pipeline integrates seamlessly with the broader TIAToolbox architecture, particularly with WSI readers and model inference engines.

### Pipeline Integration Flow

```mermaid
graph LR
    subgraph "Data Input"
        WSIReader --> PatchExtractor
        AnnotationStore --> MaskGeneration["AnnotationRenderer"]
        NumpyArrays --> VirtualWSIReader
    end
    
    subgraph "Processing Pipeline"
        PatchExtractor --> ImageTransforms["Transform operations"]
        ImageTransforms --> TissueMasking["Tissue detection"]
        TissueMasking --> CoordinateFiltering["Coordinate filtering"]
    end
    
    subgraph "Output to Models"
        CoordinateFiltering --> ModelInput["Model inference engines"]
        ModelInput --> PatchPredictor
        ModelInput --> SemanticSegmentor
        ModelInput --> NucleusInstanceSegmentor
    end
    
    subgraph "Annotation Integration"
        MaskGeneration --> VirtualWSIReader
        VirtualWSIReader --> PatchExtractor
    end
```

**System Integration**
The image processing pipeline serves as a bridge between raw WSI data and machine learning models. It integrates with the `WSIReader` system to access multi-resolution image data, supports annotation-based masking through `AnnotationStore` integration, and provides processed patches to various inference engines.

Sources: [tiatoolbox/tools/patchextraction.py:202-276](), [tiatoolbox/tools/patchextraction.py:238-258](), [tiatoolbox/tools/patchextraction.py:317-352]()

### Error Handling and Validation

```mermaid
graph TB
    subgraph "Input Validation"
        ValidateShape["validate_shape()"] --> ShapeErrors["Shape validation errors"]
        AssertDtypeInt["assert_dtype_int()"] --> DtypeErrors["Data type errors"]
        BoundsValidation["Bounds validation"] --> BoundsErrors["Invalid bounds errors"]
    end
    
    subgraph "Runtime Checks"
        MaskRatioCheck["min_mask_ratio validation"] --> RatioErrors["Ratio range errors"]
        CoordinateCheck["Coordinate format validation"] --> CoordErrors["Coordinate errors"]
        PaddingCheck["Padding size validation"] --> PadErrors["Padding errors"]
    end
    
    subgraph "Exception Types"
        ShapeErrors --> ValueError
        DtypeErrors --> AssertionError
        BoundsErrors --> ValueError
        RatioErrors --> ValueError
    end
```

**Error Handling Framework**
The pipeline implements comprehensive validation at multiple levels, from basic shape and data type checking to complex coordinate and parameter validation. Custom validation functions like `validate_shape` and `assert_dtype_int` provide consistent error handling across the system.

Sources: [tiatoolbox/tools/patchextraction.py:26-33](), [tiatoolbox/utils/misc.py:643-662](), [tiatoolbox/utils/image.py:153-191]()

---

