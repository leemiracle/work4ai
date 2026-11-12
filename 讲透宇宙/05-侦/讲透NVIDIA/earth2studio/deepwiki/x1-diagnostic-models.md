<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/earth2studio · extra page Diagnostic Models · fetched 2026-10-26 -->

# Diagnostic Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [earth2studio/data/cbottle.py](earth2studio/data/cbottle.py)
- [earth2studio/models/dx/cbottle_sr.py](earth2studio/models/dx/cbottle_sr.py)
- [earth2studio/models/dx/cbottle_tc.py](earth2studio/models/dx/cbottle_tc.py)
- [earth2studio/models/dx/corrdiff.py](earth2studio/models/dx/corrdiff.py)
- [earth2studio/models/utils.py](earth2studio/models/utils.py)
- [test/Dockerfile](test/Dockerfile)
- [test/data/test_cbottle.py](test/data/test_cbottle.py)
- [test/models/dx/test_cbottle_infill.py](test/models/dx/test_cbottle_infill.py)
- [test/models/dx/test_cbottle_sr.py](test/models/dx/test_cbottle_sr.py)
- [test/models/dx/test_corrdiff.py](test/models/dx/test_corrdiff.py)

</details>



Diagnostic models in earth2studio perform time-independent transformations on geospatial data, typically taking atmospheric or climate fields at a specific time and predicting derived quantities without time integration. These models enable enhancement, analysis, and post-processing workflows including super-resolution, infilling, and specialized predictions.

For information about time-integrating forecast models, see [Prognostic Models](#3.2.1). For general model architecture and loading systems, see [Models](#3.2).

## Overview

Diagnostic models implement the `DiagnosticModel` interface and provide functionality for transforming input fields into enhanced or derived outputs. Unlike prognostic models that advance fields forward in time, diagnostic models operate on instantaneous data to produce spatially or qualitatively enhanced results.

### Architecture

```mermaid
graph TB
    subgraph "Diagnostic Model Interface"
        DiagnosticModel["DiagnosticModel<br/>Abstract Base"]
        AutoModelMixin["AutoModelMixin<br/>Package Loading"]
        BatchDecorators["@batch_coords()<br/>@batch_func()"]
    end
    
    subgraph "Core Methods"
        InputCoords["input_coords()<br/>CoordSystem"]
        OutputCoords["output_coords()<br/>CoordSystem → CoordSystem"]
        Forward["__call__()<br/>Tensor × CoordSystem → Tensor × CoordSystem"]
    end
    
    subgraph "Model Categories"
        SuperRes["Super-Resolution<br/>CorrDiff, CBottleSR"]
        Infill["Infilling<br/>CBottleInfill"]
        Guidance["Specialized Analysis<br/>CBottleTCGuidance"]
    end
    
    DiagnosticModel --> InputCoords
    DiagnosticModel --> OutputCoords
    DiagnosticModel --> Forward
    AutoModelMixin --> DiagnosticModel
    BatchDecorators --> DiagnosticModel
    
    SuperRes --> DiagnosticModel
    Infill --> DiagnosticModel
    Guidance --> DiagnosticModel
```

Sources: [earth2studio/models/dx/base.py](), [earth2studio/models/dx/corrdiff.py:63-118](), [earth2studio/models/dx/cbottle_sr.py:81-117]()

### Data Flow Pipeline

```mermaid
graph LR
    subgraph "Input Processing"
        InputData["Input Tensor<br/>torch.Tensor"]
        InputCoords["Input Coordinates<br/>CoordSystem"]
        Validation["handshake_coords()<br/>handshake_dim()"]
    end
    
    subgraph "Model Processing"
        Preprocess["preprocess_input()<br/>Normalization"]
        CoreModel["Core Model<br/>torch.nn.Module"]
        Postprocess["postprocess_output()<br/>Denormalization"]
    end
    
    subgraph "Grid Operations"
        Interpolation["Interpolation<br/>latlon_interpolation_regular()"]
        Regridding["Regridding<br/>earth2grid.get_regridder()"]
        Transformation["Grid Transformation<br/>HEALPix ↔ Lat/Lon"]
    end
    
    subgraph "Output"
        OutputTensor["Output Tensor<br/>Enhanced/Derived Fields"]
        OutputCoords["Output Coordinates<br/>Updated CoordSystem"]
    end
    
    InputData --> Validation
    InputCoords --> Validation
    Validation --> Preprocess
    Preprocess --> CoreModel
    CoreModel --> Postprocess
    
    Preprocess --> Interpolation
    Interpolation --> Regridding
    Regridding --> Transformation
    Transformation --> Postprocess
    
    Postprocess --> OutputTensor
    Postprocess --> OutputCoords
```

Sources: [earth2studio/models/dx/corrdiff.py:553-582](), [earth2studio/models/dx/cbottle_sr.py:338-410](), [earth2studio/utils/interp.py]()

## Super-Resolution Models

Super-resolution diagnostic models enhance spatial resolution of input fields using diffusion-based or neural operator approaches.

### CorrDiff

`CorrDiff` implements a Corrector Diffusion model that combines regression and diffusion steps to generate high-resolution weather predictions from low-resolution inputs.

```mermaid
graph TB
    subgraph "CorrDiff Architecture"
        CorrDiffClass["CorrDiff<br/>torch.nn.Module + AutoModelMixin"]
        RegressionModel["regression_model<br/>PhysicsNemoModule"]
        ResidualModel["residual_model<br/>PhysicsNemoModule"]
        Sampler["sampler<br/>deterministic_sampler | stochastic_sampler"]
    end
    
    subgraph "Processing Steps"
        Interpolate["_interpolate()<br/>Input → Output Grid"]
        NormalizeInput["preprocess_input()<br/>(x - center) / scale"]
        RegressionStep["regression_step()<br/>Base Prediction"]
        DiffusionStep["diffusion_step()<br/>Residual Enhancement"]
        DenormalizeOutput["postprocess_output()<br/>x * scale + center"]
    end
    
    subgraph "Grid Management"
        InputGrid["lat_input_grid<br/>lon_input_grid"]
        OutputGrid["lat_output_grid<br/>lon_output_grid"]
        Invariants["invariants<br/>OrderedDict"]
    end
    
    CorrDiffClass --> RegressionModel
    CorrDiffClass --> ResidualModel
    CorrDiffClass --> Sampler
    
    Interpolate --> NormalizeInput
    NormalizeInput --> RegressionStep
    RegressionStep --> DiffusionStep
    DiffusionStep --> DenormalizeOutput
    
    InputGrid --> Interpolate
    OutputGrid --> Interpolate
    Invariants --> NormalizeInput
```

Sources: [earth2studio/models/dx/corrdiff.py:63-118](), [earth2studio/models/dx/corrdiff.py:584-672]()

### CBottleSR

`CBottleSR` provides super-resolution capabilities for climate data using the Climate in a Bottle diffusion model, transforming 0.25° resolution inputs to 5km resolution outputs.

```mermaid
graph TB
    subgraph "CBottleSR Components"
        CBottleSRClass["CBottleSR<br/>torch.nn.Module + AutoModelMixin"]
        CoreModel["core_model<br/>Diffusion Model"]
        Regridders["regrid_latlon_to_hpx<br/>regrid_hpx_to_latlon"]
    end
    
    subgraph "Resolution Processing"
        LowResGrid["Low-Res Input<br/>721 × 1440 lat/lon"]
        HPXHighRes["High-Res HEALPix<br/>Level 10"]
        HighResOutput["High-Res Output<br/>2161 × 4320 or custom"]
    end
    
    subgraph "Sampling Configuration"
        SamplerSteps["sampler_steps: int = 18"]
        SigmaMax["sigma_max: int = 800"]
        OutputResolution["output_resolution<br/>tuple[int, int]"]
        SRWindow["super_resolution_window<br/>Optional[tuple[int,int,int,int]]"]
    end
    
    CBottleSRClass --> CoreModel
    CBottleSRClass --> Regridders
    
    LowResGrid --> HPXHighRes
    HPXHighRes --> HighResOutput
    
    SamplerSteps --> CoreModel
    SigmaMax --> CoreModel
    OutputResolution --> HighResOutput
    SRWindow --> HighResOutput
```

Sources: [earth2studio/models/dx/cbottle_sr.py:81-117](), [earth2studio/models/dx/cbottle_sr.py:338-410]()

## Infilling Models

Infilling diagnostic models generate complete climate realizations by filling in missing or incomplete fields based on provided constraints.

### CBottleInfill

`CBottleInfill` uses diffusion-based sampling to generate global climate fields while preserving specified input variables as constraints.

```mermaid
graph TB
    subgraph "CBottleInfill Structure"
        CBottleInfillClass["CBottleInfill<br/>torch.nn.Module + AutoModelMixin"]
        CoreModel["core_model<br/>cbottle.inference.MixtureOfExpertsDenoiser"]
        SSTDataset["sst_ds<br/>xr.Dataset"]
        InputVariables["input_variables<br/>Constraint Fields"]
    end
    
    subgraph "Input Processing"
        TimeValidation["_validate_time()<br/>1940-2022 Range"]
        SSTRegridding["sst_regridder<br/>lat/lon → HEALPix"]
        VariableMapping["input_variable_idx<br/>Index Mapping"]
    end
    
    subgraph "Sampling Process"
        LatentGeneration["Latent Variables<br/>torch.randn_like()"]
        DiffusionSampling["edm_sampler()<br/>Denoising Process"]
        ConstraintApplication["Constraint Preservation<br/>Input Variable Indices"]
    end
    
    subgraph "Output Variables"
        AllVariables["All cBottle Variables<br/>45 climate fields"]
        ConstrainedOutput["Constrained + Generated<br/>Preserved inputs + synthesized"]
    end
    
    CBottleInfillClass --> CoreModel
    CBottleInfillClass --> SSTDataset
    CBottleInfillClass --> InputVariables
    
    TimeValidation --> SSTRegridding
    SSTRegridding --> VariableMapping
    
    LatentGeneration --> DiffusionSampling
    DiffusionSampling --> ConstraintApplication
    
    AllVariables --> ConstrainedOutput
    ConstraintApplication --> ConstrainedOutput
```

Sources: [earth2studio/models/dx/cbottle_infill.py](), [earth2studio/data/cbottle.py:57-112]()

## Model Loading and Configuration

All diagnostic models implement the `AutoModelMixin` interface for standardized package-based loading from model registries.

### Package Loading Pattern

```mermaid
graph LR
    subgraph "Package System"
        DefaultPackage["load_default_package()<br/>Package from NGC"]
        CustomPackage["Package<br/>Custom Location"]
        PackageResolve["package.resolve()<br/>File Resolution"]
    end
    
    subgraph "Model Loading"
        LoadModel["load_model(package)<br/>Class Method"]
        CheckpointLoading["Checkpoint Loading<br/>Model Weights"]
        ConfigLoading["Configuration<br/>Metadata + Stats"]
        ModelInstantiation["Model Instance<br/>Initialized Object"]
    end
    
    subgraph "Common Assets"
        ModelWeights["Model Checkpoints<br/>.mdlus, .checkpoint"]
        Metadata["metadata.json<br/>Configuration"]
        Statistics["stats.json<br/>Normalization"]
        GridData["Grid Files<br/>latlon_grid.nc"]
    end
    
    DefaultPackage --> LoadModel
    CustomPackage --> LoadModel
    LoadModel --> PackageResolve
    
    PackageResolve --> ModelWeights
    PackageResolve --> Metadata
    PackageResolve --> Statistics
    PackageResolve --> GridData
    
    ModelWeights --> ModelInstantiation
    Metadata --> ModelInstantiation
    Statistics --> ModelInstantiation
    GridData --> ModelInstantiation
```

Sources: [earth2studio/models/dx/corrdiff.py:370-500](), [earth2studio/models/dx/cbottle_sr.py:281-336](), [earth2studio/models/auto/mixin.py]()

### Configuration Parameters

| Model | Key Parameters | Default Values | Purpose |
|-------|---------------|----------------|---------|
| `CorrDiff` | `number_of_samples`, `number_of_steps`, `solver` | `1`, `18`, `"euler"` | Diffusion sampling control |
| `CBottleSR` | `output_resolution`, `sampler_steps`, `sigma_max` | `(2161, 4320)`, `18`, `800` | Resolution and noise control |
| `CBottleInfill` | `input_variables`, `sampler_steps` | User-defined, `18` | Constraint specification |
| `CBottleTCGuidance` | `lat_lon`, `sampler_steps`, `seed` | `True`, `18`, `None` | Output format and reproducibility |

Sources: [earth2studio/models/dx/corrdiff.py:119-143](), [earth2studio/models/dx/cbottle_sr.py:119-126]()

### Coordinate System Handling

Diagnostic models use the `@batch_coords` and `@batch_func` decorators to handle coordinate transformations and ensure compatibility with earth2studio's data pipeline.

```mermaid
graph TB
    subgraph "Coordinate Processing"
        InputCoords["input_coords()<br/>Define Expected Input"]
        OutputCoords["output_coords(input_coords)<br/>Transform to Output"]
        Handshake["handshake_coords()<br/>handshake_dim()<br/>Validation"]
    end
    
    subgraph "Batch Processing"
        BatchCoords["@batch_coords()<br/>Coordinate Decorator"]
        BatchFunc["@batch_func()<br/>Function Decorator"]
        CoordValidation["Coordinate Validation<br/>Dimension Checking"]
    end
    
    subgraph "Grid Transformations"
        LatLonGrid["Lat/Lon Grid<br/>Regular/Irregular"]
        HEALPixGrid["HEALPix Grid<br/>Nested/Ring Order"]
        CustomGrid["Custom Grids<br/>Model-Specific"]
    end
    
    InputCoords --> Handshake
    OutputCoords --> Handshake
    Handshake --> CoordValidation
    
    BatchCoords --> CoordValidation
    BatchFunc --> CoordValidation
    
    LatLonGrid --> InputCoords
    HEALPixGrid --> InputCoords
    CustomGrid --> InputCoords
```

Sources: [earth2studio/models/batch.py](), [earth2studio/utils/coords.py](), [earth2studio/models/dx/corrdiff.py:316-368]()

---

