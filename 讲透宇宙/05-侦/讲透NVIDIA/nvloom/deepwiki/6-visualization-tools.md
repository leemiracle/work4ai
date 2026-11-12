<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvloom · page 6 Visualization Tools · fetched 2026-10-26 -->

# Visualization Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/plot_heatmaps.py](cli/plot_heatmaps.py)
- [docs/bisect_testing.png](docs/bisect_testing.png)

</details>



This page documents nvloom's visualization capabilities, specifically the heatmap plotting utility that transforms benchmark results into visual representations. The primary tool is the `plot_heatmaps.py` script, which generates color-coded heatmaps showing bandwidth performance across GPU pairs and test configurations.

For information about the testing framework that generates the data visualized here, see [Testing Framework](#5). For details about the command line interface that produces the input data, see [Command Line Interface](#3).

## Overview

The nvloom visualization system consists of a Python-based heatmap generator that processes text output from `nvloom_cli` and creates visual representations of benchmark results. The tool is designed to handle complex multi-GPU, multi-rack configurations with support for rack separation indicators and customizable formatting.

```mermaid
flowchart LR
    CLI["nvloom_cli"] 
    PIPE["|"]
    PLOT["plot_heatmaps.py"]
    IMG["Heatmap Images"]
    
    CLI --> PIPE
    PIPE --> PLOT
    PLOT --> IMG
    
    CLI --> |"Benchmark Results<br/>Process Information<br/>Test Case Data"| PLOT
    PLOT --> |"PNG/PDF/SVG<br/>Color-coded Heatmaps<br/>Statistics Summary"| IMG
```

**Data Flow and Processing Pipeline**

Sources: [cli/plot_heatmaps.py:1-372]()

## Core Components

The visualization system is implemented through several key components that work together to parse benchmark data and generate heatmaps:

```mermaid
graph TB
    subgraph "Input Processing"
        STDIN["sys.stdin"]
        PARSER["Line Parser"]
        PROC_INFO["Process Information<br/>parse_process_line()"]
        TEST_DATA["Test Results<br/>parse_result_line()"]
    end
    
    subgraph "Data Transformation"
        FLOAT_CONV["convert_results_to_float()"]
        STATS["get_stats_values()"]
        LABELS["Label Processing<br/>enrich_labels_y()"]
        SEPARATORS["Separator Parsing<br/>parse_column_separators()"]
    end
    
    subgraph "Visualization Generation"
        MAIN_PLOT["create_main_heatmap()"]
        STATS_PLOT["generate_stats_plot()"]
        FORMAT["format_heatmap()"]
        SAVE["plt.savefig()"]
    end
    
    STDIN --> PARSER
    PARSER --> PROC_INFO
    PARSER --> TEST_DATA
    
    PROC_INFO --> LABELS
    TEST_DATA --> FLOAT_CONV
    FLOAT_CONV --> STATS
    FLOAT_CONV --> MAIN_PLOT
    
    LABELS --> FORMAT
    SEPARATORS --> FORMAT
    STATS --> STATS_PLOT
    
    MAIN_PLOT --> SAVE
    STATS_PLOT --> SAVE
    FORMAT --> SAVE
```

**Component Architecture and Data Flow**

Sources: [cli/plot_heatmaps.py:307-371](), [cli/plot_heatmaps.py:205-249](), [cli/plot_heatmaps.py:282-297]()

## Command Line Interface

The `plot_heatmaps.py` script provides extensive customization options through command line arguments:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--path` | Current directory | Output directory for generated plots |
| `--heatmap_lower_limit` | 0 | Minimum value for color scale |
| `--heatmap_upper_limit` | Auto-calculated | Maximum value for color scale |
| `--title_fontsize` | 32 | Font size for plot titles |
| `--legend_fontsize` | 24 | Font size for axis labels and legends |
| `--data_fontsize_scaling_factor` | 1 | Scaling factor for data value labels |
| `--plot_size` | 32 | Size of generated plots in inches |
| `--file_format` | png | Output format (png, pdf, svg, etc.) |

**Usage Pattern:**
```bash
cat benchmark_output.txt | python3 plot_heatmaps.py --path ./heatmaps --plot_size 24
```

Sources: [cli/plot_heatmaps.py:28-40](), [cli/plot_heatmaps.py:43]()

## Input Data Format

The script expects input in the specific format produced by `nvloom_cli`. The parsing system handles three main types of input lines:

```mermaid
graph LR
    subgraph "Input Line Types"
        PROC["Process Lines<br/>'Process X on hostname...'"]
        RUN["Test Case Headers<br/>'Running testname'"]
        DATA["Result Data Lines<br/>'GPU_ID value1 value2...'"]
    end
    
    subgraph "Parsed Information"
        HOSTGPU["Hostname/GPU Mapping<br/>process_to_gpu_list"]
        RACKGUID["Rack GUID Information<br/>rack_guid_list"]
        RESULTS["Numerical Results<br/>results matrix"]
        LABELS["Axis Labels<br/>labels_x, labels_y"]
    end
    
    PROC --> HOSTGPU
    PROC --> RACKGUID
    RUN --> LABELS
    DATA --> RESULTS
    DATA --> LABELS
```

**Input Processing and Data Extraction**

Sources: [cli/plot_heatmaps.py:290-297](), [cli/plot_heatmaps.py:282-287](), [cli/plot_heatmaps.py:324-352]()

## Heatmap Generation

The core visualization functionality creates two-panel plots with a main heatmap and summary statistics:

### Main Heatmap Features

- **Color Mapping**: Uses matplotlib's "YlGn" (Yellow-Green) colormap for bandwidth values
- **Data Labels**: Numerical values overlaid on each cell with automatic color adjustment for readability  
- **Grid Lines**: Minor grid lines separate individual cells
- **Rack Separators**: Horizontal and vertical lines indicate rack boundaries
- **Axis Labels**: Support for both numeric GPU IDs and hostname/GPU combinations

### Statistics Panel

The lower panel displays summary statistics with the same color mapping:
- **Minimum**: Lowest bandwidth value across all measurements
- **Average**: Mean bandwidth across all valid measurements  
- **Maximum**: Highest bandwidth value recorded

```mermaid
graph TB
    subgraph "Heatmap Structure"
        MAIN["Main Heatmap<br/>imshow(results)"]
        STATS["Statistics Bar<br/>min/avg/max"]
        CBAR["Color Bar<br/>GB/s scale"]
    end
    
    subgraph "Visual Elements"
        GRID["Grid Lines<br/>cell separation"]
        LABELS_DATA["Data Labels<br/>bandwidth values"]
        RACK_SEP["Rack Separators<br/>thick black lines"]
        AXIS["Axis Labels<br/>GPU/hostname IDs"]
    end
    
    MAIN --> GRID
    MAIN --> LABELS_DATA
    MAIN --> RACK_SEP
    MAIN --> AXIS
    MAIN --> CBAR
    
    STATS --> LABELS_DATA
```

**Visual Elements and Layout Structure**

Sources: [cli/plot_heatmaps.py:195-203](), [cli/plot_heatmaps.py:58-77](), [cli/plot_heatmaps.py:130-139]()

## Multi-Rack Support

The visualization system includes sophisticated support for multi-rack configurations, automatically detecting rack boundaries and adding visual separators:

### Rack Detection

- **Process Line Parsing**: Extracts rack GUID information from process description lines
- **Boundary Detection**: Identifies transitions between different rack GUIDs
- **Separator Placement**: Adds horizontal lines between GPU groups from different racks

### Column Separators

The system supports explicit column separators using pipe characters (`|`) in the input data:
- **Parsing**: Detects `|` characters in column headers and removes them from labels
- **Visual Separation**: Adds vertical black lines at specified positions
- **Label Grouping**: Groups related columns under common headers

Sources: [cli/plot_heatmaps.py:251-257](), [cli/plot_heatmaps.py:79-106](), [cli/plot_heatmaps.py:260-279]()

## Adaptive Formatting

The plotting system includes intelligent formatting that adapts to data characteristics:

### Font Size Scaling

Dynamic font size calculation based on:
- **Matrix Dimensions**: Larger matrices use smaller fonts to maintain readability
- **Value Magnitudes**: Font size scales with the maximum value length to prevent overlap
- **User Scaling Factor**: Multiplier for manual font size adjustment

### Color Threshold Calculation

Text color selection for data labels:
- **Automatic Threshold**: Set to 50% of maximum value for optimal contrast
- **Binary Color Selection**: Black text on light backgrounds, white text on dark backgrounds
- **Consistent Application**: Same logic applied to both main heatmap and statistics panel

### Layout Optimization

- **Aspect Ratio**: Height ratios calculated based on matrix dimensions
- **Tight Layout**: Automatic padding adjustment to prevent clipping
- **Size Scaling**: Plot dimensions scale with data complexity

Sources: [cli/plot_heatmaps.py:158-164](), [cli/plot_heatmaps.py:225-238](), [cli/plot_heatmaps.py:166-193]()

## Error Handling and Validation

The visualization system includes robust error handling for common issues:

### Data Validation

- **Limit Validation**: Ensures color scale limits are reasonable relative to data range
- **NaN Handling**: Gracefully skips test cases with all NaN values
- **Directory Creation**: Automatically creates output directories with error handling

### Exception Management

- **File I/O Errors**: Catches and reports file system issues during plot saving
- **Plotting Errors**: Individual test case failures don't stop overall processing
- **Input Format Issues**: Robust parsing with graceful degradation for malformed input

Sources: [cli/plot_heatmaps.py:146-156](), [cli/plot_heatmaps.py:218-220](), [cli/plot_heatmaps.py:314-317](), [cli/plot_heatmaps.py:244-248]()

---

