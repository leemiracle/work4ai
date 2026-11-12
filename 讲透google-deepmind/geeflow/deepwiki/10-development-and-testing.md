<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/geeflow · page 10 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [geeflow/coords_test.py](geeflow/coords_test.py)
- [geeflow/ee_data_test.py](geeflow/ee_data_test.py)
- [geeflow/stats/stats_util_test.py](geeflow/stats/stats_util_test.py)
- [geeflow/times_test.py](geeflow/times_test.py)
- [geeflow/utils_test.py](geeflow/utils_test.py)

</details>



This page covers the testing infrastructure, development patterns, and testing methodologies used in GeoFlow. It provides guidance for developers contributing to the codebase and explains the testing approach for the core modules.

For information about the overall system architecture, see [Core Architecture](#3). For details about specific modules being tested, see [Data Sources and Processing](#5) and [Utilities and Helpers](#8).

## Testing Framework and Structure

GeoFlow uses the Abseil Testing framework (`absl.testing`) as its primary testing infrastructure. The test suite is organized to mirror the main module structure, with comprehensive unit tests for core functionality.

### Test Organization

```mermaid
graph TB
    subgraph "Test Files"
        COORDS_TEST["coords_test.py<br/>UTM Grid Testing"]
        EE_DATA_TEST["ee_data_test.py<br/>Earth Engine Data Testing"]
        STATS_TEST["stats/stats_util_test.py<br/>Statistics Testing"]
        TIMES_TEST["times_test.py<br/>Date/Time Testing"]
        UTILS_TEST["utils_test.py<br/>Utilities Testing"]
    end
    
    subgraph "Core Modules Under Test"
        COORDS["coords.py<br/>UtmGridMapping"]
        EE_DATA["ee_data.py<br/>Sentinel2, Hansen, etc."]
        STATS_UTIL["stats/stats_util.py<br/>Accumulator Classes"]
        TIMES["times.py<br/>Date Utilities"]
        UTILS["utils.py<br/>Argument Parsing"]
    end
    
    subgraph "Testing Framework"
        ABSL["absl.testing<br/>- absltest<br/>- parameterized"]
        MOCK["unittest.mock<br/>External Dependencies"]
        NUMPY["numpy.testing<br/>Array Assertions"]
    end
    
    COORDS_TEST --> COORDS
    EE_DATA_TEST --> EE_DATA
    STATS_TEST --> STATS_UTIL
    TIMES_TEST --> TIMES
    UTILS_TEST --> UTILS
    
    COORDS_TEST --> ABSL
    EE_DATA_TEST --> MOCK
    STATS_TEST --> NUMPY
    TIMES_TEST --> ABSL
    UTILS_TEST --> ABSL
```

**Sources:** [geeflow/coords_test.py:1-91](), [geeflow/ee_data_test.py:1-58](), [geeflow/stats/stats_util_test.py:1-191](), [geeflow/times_test.py:1-67](), [geeflow/utils_test.py:1-78]()

### Test Execution Patterns

All test files follow a consistent structure using the Abseil testing framework:

| Test File | Primary Test Class | Key Features |
|-----------|-------------------|--------------|
| `coords_test.py` | `CoordsTest` | Parameterized UTM zone testing, coordinate transformation validation |
| `ee_data_test.py` | `EeDataTest` | Earth Engine mocking, data processing validation |
| `stats_util_test.py` | `StatsUtilTest` | Statistical accumulator testing, numerical precision validation |
| `times_test.py` | `TimesTest` | Date format handling, timezone conversion testing |
| `utils_test.py` | `CommonTest` | Argument parsing validation, type checking |

## Core Module Testing Patterns

### Coordinate System Testing

The `coords_test.py` module extensively tests the `UtmGridMapping` class, which is central to GeoFlow's spatial coordinate handling:

```mermaid
graph TB
    subgraph "UtmGridMapping Test Coverage"
        BASIC["test_utm_grid_mapping<br/>Basic CRS Transform"]
        RESCALE["test_utm_grid_mapping_rescale<br/>Grid Rescaling"]
        FROM_BBOX["test_utm_grid_mapping_from_bbox<br/>Bounding Box Creation"]
        FROM_LATLON["test_utm_grid_mapping_from_latlon<br/>Lat/Lon Center Creation"]
        BBOX_LATLON["test_utm_grid_mapping_bbox_latlon<br/>Coordinate Conversion"]
        UTM_EPSG["test_utm_to_epsg<br/>EPSG Code Generation"]
    end
    
    subgraph "Validation Patterns"
        COORD_VALID["Coordinate Validation<br/>UTM bounds checking"]
        PROJ_VALID["Projection Validation<br/>CRS transform accuracy"]
        EPSG_VALID["EPSG Code Validation<br/>Zone to EPSG mapping"]
    end
    
    BASIC --> COORD_VALID
    RESCALE --> COORD_VALID
    FROM_BBOX --> COORD_VALID
    FROM_LATLON --> PROJ_VALID
    BBOX_LATLON --> PROJ_VALID
    UTM_EPSG --> EPSG_VALID
```

Key testing patterns include:
- **Parameterized testing** for multiple UTM zones: `("18N", "EPSG:32618"), ("10C", "EPSG:32710")`
- **Numerical precision validation** using `numpy.testing.assert_allclose`
- **Error condition testing** for invalid coordinate ranges

**Sources:** [geeflow/coords_test.py:23-87]()

### Earth Engine Data Testing

The `ee_data_test.py` module tests Earth Engine integration with careful mocking to avoid external dependencies:

```mermaid
graph TB
    subgraph "EE Data Test Strategy"
        MOCK_EE["@mock.patch.object(ee_data, 'ee')<br/>Mock Earth Engine API"]
        ASSET_TEST["test_s2_asset<br/>Asset Name Validation"]
        STACK_TEST["test_s2_stack<br/>Band Stacking Logic"]
        VIS_TEST["test_s2_vis_and_vis_norm<br/>Visualization Normalization"]
    end
    
    subgraph "Sentinel-2 Testing"
        L2A["L2A Mode<br/>COPERNICUS/S2_SR_HARMONIZED"]
        L1C["L1C Mode<br/>COPERNICUS/S2_HARMONIZED"]
        BAND_STACK["Band Stacking<br/>B1, B2, B3, B4, B5"]
        VIS_STACK["Visualization Stack<br/>RGB Bands Only"]
    end
    
    MOCK_EE --> ASSET_TEST
    ASSET_TEST --> L2A
    ASSET_TEST --> L1C
    STACK_TEST --> BAND_STACK
    STACK_TEST --> VIS_STACK
    VIS_TEST --> VIS_STACK
```

The testing approach uses:
- **Mock patching** to isolate Earth Engine dependencies: `@mock.patch.object(ee_data, "ee")`
- **Parameterized testing** for different Sentinel-2 modes
- **Array shape validation** for band stacking operations
- **Value range validation** for visualization normalization

**Sources:** [geeflow/ee_data_test.py:25-54]()

### Statistics System Testing

The `stats_util_test.py` provides comprehensive testing for the statistics accumulator classes:

```mermaid
graph TB
    subgraph "Statistics Accumulator Testing"
        STATS_ACC["StatsAccumulator<br/>Basic Statistics"]
        COUNTER_ACC["CounterAccumulator<br/>Histogram + Statistics"]
        BANDS_ACC["BandsAccumulator<br/>Multi-band Statistics"]
    end
    
    subgraph "Test Coverage Areas"
        BASIC_STATS["Basic Statistics<br/>mean, std, var, min, max"]
        HIST_STATS["Histogram Statistics<br/>mode, bins, quantiles"]
        MASK_STATS["Masked Statistics<br/>selective computation"]
        RECOMPUTE["Recomputation<br/>after masking"]
    end
    
    subgraph "Validation Methods"
        NUMPY_COMP["NumPy Comparison<br/>arr.mean(), arr.std()"]
        PRECISION_CHECK["Precision Validation<br/>floating point accuracy"]
        EDGE_CASES["Edge Case Testing<br/>empty data, single values"]
    end
    
    STATS_ACC --> BASIC_STATS
    COUNTER_ACC --> HIST_STATS
    COUNTER_ACC --> MASK_STATS
    BANDS_ACC --> BASIC_STATS
    
    BASIC_STATS --> NUMPY_COMP
    HIST_STATS --> PRECISION_CHECK
    MASK_STATS --> RECOMPUTE
    RECOMPUTE --> EDGE_CASES
```

Key testing features:
- **Statistical accuracy validation** against NumPy reference implementations
- **Masking and recomputation testing** for selective statistics
- **Histogram quantile computation** with custom `hist_quantile` function
- **Multi-accumulator management** through `BandsAccumulator`

**Sources:** [geeflow/stats/stats_util_test.py:21-187]()

## Testing Utilities and Patterns

### Parameterized Testing

GeoFlow extensively uses parameterized tests to cover multiple scenarios efficiently:

```python
@parameterized.parameters(
    ("18N", "EPSG:32618"),
    ("10C", "EPSG:32710"), 
    ("49S", "EPSG:32649"),
    ("9m", "EPSG:32709"),
)
def test_utm_to_epsg(self, utm_zone, expected_epsg):
```

This pattern is used across:
- **UTM zone testing** in `coords_test.py`
- **Date format testing** in `times_test.py` 
- **Sentinel-2 mode testing** in `ee_data_test.py`
- **Accumulator type testing** in `stats_util_test.py`

### Mock Strategy for External Dependencies

External dependencies are systematically mocked to ensure test isolation:

```mermaid
graph TB
    subgraph "Mock Targets"
        EE_API["Earth Engine API<br/>ee.ImageCollection()"]
        EE_CALLS["EE Method Calls<br/>call_count validation"]
    end
    
    subgraph "Mock Techniques"
        PATCH_OBJ["@mock.patch.object<br/>Decorator-based mocking"]
        CALL_COUNT["call_count assertion<br/>Verify API usage"]
        RETURN_VAL["return_value control<br/>Simulate responses"]
    end
    
    EE_API --> PATCH_OBJ
    EE_CALLS --> CALL_COUNT
    PATCH_OBJ --> RETURN_VAL
```

**Sources:** [geeflow/ee_data_test.py:29-34]()

### Numerical Testing Patterns

For numerical computations, GeoFlow uses precise validation methods:

| Validation Type | Method | Use Case |
|----------------|--------|----------|
| Exact equality | `self.assertEqual()` | Integer values, discrete categories |
| Floating point | `np.testing.assert_allclose()` | Coordinate transformations |
| Approximate equality | `self.assertAlmostEqual()` | Statistical computations |
| Range validation | `self.assertLessEqual()` | Normalized values (0-1 range) |

## Development Workflow Integration

### Test Execution

Tests are designed to run independently using the standard Python test execution pattern:

```bash
python -m absl.testing.absltest geeflow.coords_test
python -m absl.testing.absltest geeflow.ee_data_test
python -m absl.testing.absltest geeflow.stats.stats_util_test
```

### Continuous Integration Considerations

The test suite is structured to support automated testing environments:

- **No external dependencies** through comprehensive mocking
- **Deterministic results** with fixed random seeds where applicable
- **Fast execution** through isolated unit tests
- **Clear failure reporting** using descriptive assertion messages

**Sources:** [geeflow/coords_test.py:89-91](), [geeflow/ee_data_test.py:56-58](), [geeflow/stats/stats_util_test.py:189-191](), [geeflow/times_test.py:65-67](), [geeflow/utils_test.py:76-78]()

## Testing Best Practices

Based on the existing test patterns, GeoFlow follows these testing principles:

1. **Comprehensive parameterization** for testing multiple scenarios
2. **External dependency isolation** through systematic mocking
3. **Numerical precision validation** using appropriate tolerance levels
4. **Edge case coverage** including empty data and boundary conditions
5. **Reference implementation comparison** against well-established libraries like NumPy

The testing infrastructure provides a solid foundation for maintaining code quality and ensuring reliable functionality across GeoFlow's core modules.