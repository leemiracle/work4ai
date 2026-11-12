<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/earth2studio · page 6 Reference · fetched 2026-10-26 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/modules/datasources.rst](docs/modules/datasources.rst)
- [docs/templates/class.rst](docs/templates/class.rst)
- [docs/userguide/advanced/lexicon.md](docs/userguide/advanced/lexicon.md)
- [docs/userguide/components/diagnostic.md](docs/userguide/components/diagnostic.md)
- [docs/userguide/components/prognostic.md](docs/userguide/components/prognostic.md)
- [docs/userguide/components/statistics.md](docs/userguide/components/statistics.md)
- [docs/userguide/developer/documentation.md](docs/userguide/developer/documentation.md)
- [docs/userguide/index.md](docs/userguide/index.md)
- [earth2studio/data/__init__.py](earth2studio/data/__init__.py)
- [earth2studio/lexicon/__init__.py](earth2studio/lexicon/__init__.py)
- [earth2studio/lexicon/base.py](earth2studio/lexicon/base.py)
- [earth2studio/lexicon/gfs.py](earth2studio/lexicon/gfs.py)

</details>



This page provides comprehensive reference documentation for earth2studio's standardized systems, including the lexicon vocabulary, variable mappings across data sources, and links to auto-generated API documentation.

For conceptual explanations of these systems, see [Core Architecture](#3). For implementation guides and examples, see [Examples and Workflows](#5).

## Lexicon System Overview

The earth2studio lexicon system provides standardized variable naming and mapping between the framework's unified vocabulary (`E2STUDIO_VOCAB`) and data source-specific variable names. This enables consistent variable handling across different weather and climate data sources.

### Lexicon Architecture

```mermaid
graph TD
    subgraph "Standardized Variables"
        E2STUDIO["E2STUDIO_VOCAB<br/>Unified variable names"]
        StandardVars["u10m, v10m, t2m<br/>z500, msl, tp, etc."]
    end
    
    subgraph "Data Source Lexicons"
        GFSLex["GFSLexicon<br/>UGRD::10 m above ground"]
        ARCOLex["ARCOLexicon<br/>10m_u_component_of_wind"]
        CDSLex["CDSLexicon<br/>10-metre U wind component"]
        HRRRLex["HRRRLexicon<br/>UGRD:10 m above ground"]
        OtherLex["WB2Lexicon, IFSLexicon<br/>GOESLexicon, etc."]
    end
    
    subgraph "Data Sources"
        GFS["GFS Data Source"]
        ARCO["ARCO Data Source"]
        CDS["CDS Data Source"] 
        HRRR["HRRR Data Source"]
        Others["WB2ERA5, IFS, GOES<br/>CMIP6, IMERG, etc."]
    end
    
    E2STUDIO --> StandardVars
    StandardVars --> GFSLex
    StandardVars --> ARCOLex
    StandardVars --> CDSLex
    StandardVars --> HRRRLex
    StandardVars --> OtherLex
    
    GFSLex --> GFS
    ARCOLex --> ARCO
    CDSLex --> CDS
    HRRRLex --> HRRR
    OtherLex --> Others
```

Sources: [earth2studio/lexicon/base.py:28-200](), [earth2studio/lexicon/__init__.py:17-29](), [earth2studio/data/__init__.py:17-40]()

### Lexicon Type System

```mermaid
graph LR
    subgraph "Base Lexicon Framework"
        LexiconType["LexiconType<br/>metaclass"]
        GetItem["__getitem__(val: str)<br/>→ tuple[str, Callable]"]
        GetItemImpl["get_item(val: str)<br/>→ tuple[str, Callable]"]
    end
    
    subgraph "Lexicon Implementation"
        VOCAB["VOCAB: dict<br/>E2Studio → DataSource"]
        Modifier["Modifier Function<br/>Data transformation"]
        DataSourceKey["Data Source Key<br/>Parsing identifier"]
    end
    
    subgraph "Usage Pattern"
        Lookup["lexicon[variable]"]
        Result["(data_key, modifier_func)"]
        Parse["Parse data_key<br/>to access data"]
        Transform["Apply modifier_func<br/>to normalize data"]
    end
    
    LexiconType --> GetItem
    GetItem --> GetItemImpl
    GetItemImpl --> VOCAB
    GetItemImpl --> Modifier
    VOCAB --> DataSourceKey
    
    Lookup --> Result
    Result --> Parse
    Result --> Transform
```

Sources: [earth2studio/lexicon/base.py:20-26](), [earth2studio/lexicon/gfs.py:288-306]()

## E2STUDIO_VOCAB Reference

The standardized vocabulary contains meteorological variables organized by category. Each variable has a standardized name and physical description.

### Surface Variables

| Variable | Description | Units |
|----------|-------------|-------|
| `u10m` | u-component (eastward, zonal) of wind at 10 m | m s⁻¹ |
| `v10m` | v-component (northward, meridional) of wind at 10 m | m s⁻¹ |
| `u100m` | u-component of wind at 100 m | m s⁻¹ |
| `v100m` | v-component of wind at 100 m | m s⁻¹ |
| `t2m` | temperature at 2m | K |
| `d2m` | dewpoint temperature at 2m | K |
| `r2m` | relative humidity at 2 m | % |
| `q2m` | specific humidity at 2 m | kg kg⁻¹ |
| `sp` | surface pressure | Pa |
| `msl` | mean sea level pressure | Pa |
| `skt` | skin temperature at surface | K |

### Atmospheric Column Variables

| Variable | Description | Units |
|----------|-------------|-------|
| `tcwv` | total column water vapor / precipitable water | kg m⁻² |
| `tclw` | total column liquid water / vertically integrated liquid water path | kg m⁻² |
| `tciw` | total column ice water / vertically integrated ice water path | kg m⁻² |

### Precipitation Variables

| Variable | Description | Units |
|----------|-------------|-------|
| `tp` | total precipitation | m |
| `tpp` | total precipitation probability | - |
| `tpi` | total precipitation index | - |
| `tp06` | total precipitation accumulated over past 6 hours | - |
| `tpf` | total precipitation flux | kg m⁻² s⁻¹ |

### Pressure Level Variables

The lexicon includes atmospheric variables at standard pressure levels (50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000 hPa):

- **Wind Components**: `u{level}`, `v{level}`, `w{level}` (m s⁻¹)
- **Geopotential**: `z{level}` (m² s⁻²) 
- **Temperature**: `t{level}` (K)
- **Humidity**: `r{level}` (%), `q{level}` (kg kg⁻¹)
- **Additional**: `vpd{level}` (vapor pressure deficit), `ws{level}` (wind speed)

### Specialized Variables

| Variable | Description | Units |
|----------|-------------|-------|
| `sic` | sea ice concentration / sea ice area fraction | 0-1 |
| `sst` | Temperature of sea water near the surface | K |
| `lsm` | land-sea mask | - |
| `z` | geopotential at surface (orography) | m² s⁻² |
| `fg10m` | maximum 10 m wind gust since previous post-processing | m s⁻¹ |
| `refc` | Maximum/Composite radar reflectivity | dB |

Sources: [earth2studio/lexicon/base.py:28-200]()

## Data Source Lexicons

Each data source implements its own lexicon class that maps `E2STUDIO_VOCAB` variables to data source-specific identifiers.

### Available Lexicons

```mermaid
graph TB
    subgraph "Weather Data Lexicons"
        GFSLex["GFSLexicon<br/>Global Forecast System"]
        HRRRLex["HRRRLexicon, HRRRFXLexicon<br/>High Resolution Rapid Refresh"]
        GEFSLex["GEFSLexicon, GEFSLexiconSel<br/>Global Ensemble Forecast"]
        IFSLex["IFSLexicon<br/>Integrated Forecast System"]
    end
    
    subgraph "Reanalysis Lexicons"
        ARCOLex["ARCOLexicon<br/>Analysis-Ready Cloud Optimized"]
        WB2Lex["WB2Lexicon, WB2ClimatetologyLexicon<br/>WeatherBench2"]
        NCARLex["NCAR_ERA5Lexicon<br/>NCAR ERA5"]
        CDSLex["CDSLexicon<br/>Copernicus Data Store"]
    end
    
    subgraph "Specialized Lexicons"
        GOESLex["GOESLexicon<br/>Geostationary Satellite"]
        IMERGLex["IMERGLexicon<br/>Precipitation"]
        CMIP6Lex["CMIP6Lexicon<br/>Climate Model"]
        CBottleLex["CBottleLexicon<br/>AI-generated Data"]
    end
```

Sources: [earth2studio/lexicon/__init__.py:17-29]()

### Lexicon Implementation Pattern

Data source lexicons follow a consistent pattern with vocabulary mapping and optional data modifiers:

```mermaid
graph LR
    subgraph "Lexicon Structure"
        Class["DataSourceLexicon<br/>metaclass=LexiconType"]
        VOCAB["VOCAB: dict<br/>{'e2studio_var': 'source_key'}"]
        GetItem["get_item(val: str)<br/>→ (source_key, modifier)"]
    end
    
    subgraph "Modifier Functions"
        Identity["Identity: return x"]
        Transform["Transform: x * factor"]
        Convert["Convert: f(x)"]
    end
    
    subgraph "Example: GFS"
        GFSVocab["'u10m': 'UGRD::10 m above ground'<br/>'z500': 'HGT::500 mb'"]
        GFSMod["HGT variables:<br/>x * 9.81 (height → geopotential)"]
    end
    
    Class --> VOCAB
    Class --> GetItem
    GetItem --> Identity
    GetItem --> Transform  
    GetItem --> Convert
    
    GFSVocab --> GFSMod
```

Sources: [earth2studio/lexicon/gfs.py:24-306](), [earth2studio/lexicon/base.py:20-26]()

### Example: GFS Lexicon Mapping

| E2Studio Variable | GFS Key | Modifier |
|-------------------|---------|----------|
| `u10m` | `UGRD::10 m above ground` | Identity |
| `v10m` | `VGRD::10 m above ground` | Identity |
| `t2m` | `TMP::2 m above ground` | Identity |
| `z500` | `HGT::500 mb` | `x * 9.81` |
| `msl` | `PRMSL::mean sea level` | Identity |
| `tp` | `596::APCP::surface` | Identity |

Sources: [earth2studio/lexicon/gfs.py:39-85](), [earth2studio/lexicon/gfs.py:288-306]()

## API Documentation System

earth2studio uses Sphinx with auto-generation to create comprehensive API documentation from docstrings.

### Documentation Structure

```mermaid
graph TB
    subgraph "Auto-Generated API Docs"
        ModuleDocs["Module Documentation<br/>docs/modules/*.rst"]
        DataSources["Data Sources<br/>earth2studio.data"]
        Models["Models<br/>earth2studio.models.px/dx"]
        IO["I/O Systems<br/>earth2studio.io"]
        Stats["Statistics<br/>earth2studio.statistics"]
    end
    
    subgraph "Templates"
        ClassTemplate["class.rst<br/>Class documentation"]
        FunctionTemplate["function.rst<br/>Function documentation"]
        DataSourceTemplate["datasource.rst<br/>Data source specific"]
        DiagnosticTemplate["diagnostic.rst<br/>Model specific"]
    end
    
    subgraph "Sphinx Directives"
        AutoModule["automodule<br/>Module overview"]
        AutoClass["autoclass<br/>Class details"]
        AutoSummary["autosummary<br/>Member lists"]
        CurrentModule["currentmodule<br/>Context setting"]
    end
    
    ModuleDocs --> ClassTemplate
    ModuleDocs --> FunctionTemplate
    ModuleDocs --> DataSourceTemplate
    ModuleDocs --> DiagnosticTemplate
    
    ClassTemplate --> AutoClass
    FunctionTemplate --> AutoModule
    DataSourceTemplate --> AutoSummary
    DiagnosticTemplate --> CurrentModule
```

Sources: [docs/modules/datasources.rst:1-89](), [docs/templates/class.rst:1-17](), [docs/userguide/developer/documentation.md:15-42]()

### API Documentation Links

| Component | Documentation Path | Description |
|-----------|-------------------|-------------|
| **Data Sources** | `earth2studio.data` | Weather/climate data APIs, caching, lexicon integration |
| **Prognostic Models** | `earth2studio.models.px` | Time-integration models for forecasting |
| **Diagnostic Models** | `earth2studio.models.dx` | Instantaneous prediction and analysis models |
| **I/O Backends** | `earth2studio.io` | Asynchronous Zarr, NetCDF4, coordinate systems |
| **Statistics** | `earth2studio.statistics` | Metrics, moments, ensemble analysis |
| **Lexicon** | `earth2studio.lexicon` | Variable mapping and data source vocabularies |
| **Utilities** | `earth2studio.utils` | Coordinate systems, data utilities, type definitions |

### Documentation Generation

The documentation system uses several key components:

- **Sphinx**: Core documentation engine with MyST markdown support
- **sphinx-gallery**: Executable examples with auto-generated notebooks  
- **AutoDocstring**: NumPy-style docstring enforcement via interrogate
- **API Templates**: Consistent formatting across all auto-generated content

Sources: [docs/userguide/developer/documentation.md:1-242](), [docs/userguide/index.md:1-132]()

---

