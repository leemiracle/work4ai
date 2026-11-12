# NVTexPy - Python Hooks for NVTeXLive

NVTexPy is a Python package that provides the core functionality for the NVTeXLive pipeline, enabling machine learning OCR annotations for LaTeX documents. It integrates with a custom-modified pdftex compiler to generate structured document annotations in multiple formats.

## Overview

NVTexPy extends the traditional LaTeX compilation process by embedding Python hooks that intercept TeX commands. This allows for:

- **On-the-fly Processing**: Intercepts TeX commands as they execute during compilation
- **Structured Output**: Generates hierarchical document structure with bounding boxes
- **Flat Output Conversion**: Converts the hierarchical structured document into a flat representation
- **Multiple Formats**: Supports flat layout output, and flat HTML output
- **Font Handling**: Comprehensive font mapping and glyph conversion
- **Math Support**: Advanced mathematical expression parsing and latex unification

## Installation

### For compiling latex documents

The easiest way to use this, is to build the [nvtexlive](https://github.com/NVIDIA/nvtexlive) [Dockerfile](https://github.com/NVIDIA/nvtexlive/blob/nvtexlive/Dockerfile):
```bash
git clone https://github.com/NVIDIA/nvtexlive
cd nvtexlive
docker build -t nvtexlive:latest .
# or using podman:
# podman build -t nvtexlive:latest .

cd ..

# Then build the nvtexpy container
git clone https://github.com/NVIDIA/nvtexpy
cd nvtexpy
docker build -t nvtexpy:latest .
# podman build -t nvtexpy:latest .
```

Note that this is not a checked build and we do not provide a ready to use docker container yet. You're responsible for validating the dependencies.

Then, run the docker container on the data:
```bash
docker run --rm -ti -v path/to/document:/doc -v path/to/output:/output nvtexpy:latest nvpdflatex /doc/texfile.tex --output-dir /output --flat-layout --flat-layout-format latex --flat-layout-style markdown
```

### For custom processing of structured output files

This does not require latex to be available, if the pickle files for pages have already been generated. The process can then be split into two stages.

```bash
pip install https://github.com/NVIDIA/nvtexpy
```

in python, run:

```py
from nvtexpy.output.flat_layout import convert_from_pkl


def main():
    converted = convert_from_pkl("/path/to/page.pkl", table_format="latex", style_format="markdown")
    with open("page.txt", "w") as wf:
        wf.write(converted)


if __name__ == "__main__":
    main()

```

## Custom Installation

### Prerequisites

- Python 3.10 or higher
- Custom pdftex binary with nvtexpy hooks (from [nvtexlive](https://github.com/NVIDIA/nvtexlive))
- Ghostscript for PDF to image conversion

### Install NVTexPy

```bash
# Install
pip install https://github.com/NVIDIA/nvtexpy

# Or install from PyPI
pip install nvtexpy
```

## Usage

### Command Line Tools

NVTexPy provides command-line tools for document processing:

```bash
# Convert a single LaTeX document to pkl
nvpdflatex document.tex ./output
```

## Output Formats

### Flat Layout

This is supposed to be compatible with DocLayNet object classes, but extends it.

Document layout analysis format providing:
- Flat document structure
- Bounding box annotations
- Category classification
- Table and figure detection

```json
{
  "metadata": {
    "coord_scale_factor": [6.334075991075136e-05, 6.334075991075136e-05],
    "page_width_px": 2480,
    "page_height_px": 3508
  },
  "ann": [
    {
      "category_id": "Title",
      "bbox": [1064, 467, 1416, 517],
      "content": "# Document 1"
    },
    {
      "category_id": "Text",
      "bbox": [956, 602, 1524, 938],
      "content": "Author A<br>\n`authora@example.com`<br>\nOrganization A<br>\nAuthor B<br>\n`authorb@example.com`<br>\nOrganization A"
    },
    {
      "category_id": "Text",
      "bbox": [1124, 990, 1356, 1024],
      "content": "2024-01-01"
    },
    {
      "category_id": "Text",
      "bbox": [1171, 1147, 1310, 1174],
      "content": "**Abstract**"
    },
    {
      "category_id": "Text",
      "bbox": [404, 1216, 2077, 1288],
      "content": "This is the abstract. This is the abstract. This is the abstract. This is the abstract. This is the abstract. This is the abstract. This is the abstract. This is the abstract. This is the abstract. This is the abstract."
    },
    {
      "category_id": "Section-header",
      "bbox": [300, 1346, 815, 1399],
      "content": "### 1 Basic formatting"
    },
    {
      "category_id": "Text",
      "bbox": [300, 1445, 1074, 1492],
      "content": "**bold**, _italic_, _(slender)italic_, `tt` <sub>subscript</sub><sup>superscript</sup>."
    }
  ]
}
```

#### Field Descriptions

**metadata:**
- `coord_scale_factor`: A list of two floats `[scale_x, scale_y]` representing the scaling factors to convert from internal TeX coordinates to pixel coordinates
- `page_width_px`: Width of the page in pixels (integer)
- `page_height_px`: Height of the page in pixels (integer)

**ann:** Array of annotation objects, where each object contains:
- `category_id`: String indicating the type of document element (see Category IDs below)
- `bbox`: Bounding box in `[x, y, width, height]` format (all integers in pixels)
  - `x`: X-coordinate of the top-left corner
  - `y`: Y-coordinate of the top-left corner  
  - `width`: Width of the bounding box
  - `height`: Height of the bounding box
- `content`: String content of the element, encoded as HTML or Markdown depending on the `--flat-layout-style` option

#### Category IDs

The following category IDs are supported:

- `Inline-Text`: Inline text content (typically not output at the top level)
- `Text`: Regular paragraph text
- `Title`: Document title
- `Section-header`: Section and subsection headers
- `List-item`: List items (bulleted or numbered)
- `Caption`: Figure and table captions
- `Table`: Tables
- `Picture`: Figures and images
- `Formula`: Mathematical formulas and equations
- `Code`: Code blocks
- `Footnote`: Footnotes
- `Page-header`: Page headers
- `Page-footer`: Page footers
- `Bibliography`: Bibliography entries
- `TOC`: Table of contents entries

The content can either be encoded as HTML or Markdown (plus latex tables, mathpix compatible).

### Basic LaTeX Processing

To process a LaTeX document with nvtexpy hooks:

```bash
# Activate nvtexpy hooks (flag 2)
pdflatex -nvtexpy=2 document.tex

# Activate both nvtexpy hooks and debugpy (flag 3)
pdflatex -nvtexpy=3 document.tex
```

### NVTexPy Flags

The `-nvtexpy` option accepts bit flags:

- `1`: Activate debugpy and wait for client
- `2`: Activate nvtexpy hooks (default)
- `3`: Activate both debugpy and nvtexpy hooks
- `16`: Deactivate input_stack optimization of TeX (for development)

## Development

### Interactive Development

Run the [Dockerfile from nvtexlive](https://github.com/NVIDIA/nvtexlive/blob/main/Dockerfile).

### Debug Mode

Enable debug mode to inspect processing:

```bash
# Enable debugpy for remote debugging
pdflatex -nvtexpy=3 document.tex
# Connect your debugger (e.g., VS Code) to the default debugpy port (5678)
```

## Configuration

### Environment Variables

Tex has several config variables:
- `TEXMFHOME`: Custom TeX home directory
- `TEXMFCONFIG`: Custom TeX configuration directory
- `TEXMFVAR`: Custom TeX variable directory
In addition, nvtexpy can be made verbose via `NVTEXPY_DEBUG_*` variables (see [src/nvtexpy/engine/debug.py])
## Troubleshooting

### Debug Information

There are several debug environment variables for debugging 

```bash
nvpdflatex tex_file.tex dst/path
```

Full command line options:
 - `--work-dir DIRECTORY`: Working directory for temporary files (defaults to tex file directory)
 - `--dpi INTEGER`: Resolution for PNG images
 - `--flat-layout / --no-flat-layout`: Generate flat layout annotation
 - `--flat-layout-format [latex|html]`: Flat layout table format
 - `--flat-layout-style [markdown|html]`: Flat layout style format
 - `--keep-work-dir`: Keep working directory after processing (for debugging)
 - `--help`: Show help

## Contributing

### Development Setup

1. Create a docker container from [nvtexlive](https://github.com/NVIDIA/nvtexlive)
2. Clone the repository
3. Within the docker container, run `just nvtexlive-install`
4. Run tests: `just nvtexlive-test`
5. To convert any document, run `nvpdflatex`

## License

SPDIX-Identifier: Apache-2.0

See [Apache License 2.0](LICENSE.txt).

## Authors

- Lukas Vögtle ([@voegtlel](https://www.github.com/voegtlel))
- Philipp Fischer ([@philipp-fischer](https://www.github.com/philipp-fischer))

Contributors:
- Jarno Seppänen ([@jseppanen](https://www.github.com/jseppanen))

## Related Projects

- [**nvtexlive**](https://github.com/NVIDIA/nvtexlive): Custom TeXLive with embedded Python hooks

## Architecture

### Core Components

```
nvtexpy/
├── engine/
│   ├── nvtexpyengine.py     # Main pdflatex hook interface class
│   ├── hooks.py             # Macro call interception system
│   ├── mem.py               # Memory management and node tracking
│   ├── texstate.py          # Document processing state
│   └── rules/               # Processing rules for different elements
├── output/                  # Output format generators
│   ├── flat_layout.py       # Flat layout format conversion
│   └── structured_output.py # Core output structure
```

### NVTexPyEngine

The `NVTexPyEngine` class is the main interface between the modified pdftex compiler and Python code. It provides methods for:

- **Character Processing**: Intercepts character allocation and output
- **Box Management**: Handles hlist/vlist creation and manipulation
- **Font Operations**: Manages font properties and glyph conversion
- **Math Mode**: Processes mathematical expressions and formatting
- **Output Generation**: Creates structured annotations in real-time

### Hook System

The hook system intercepts various TeX operations:

- **Macro Calls**: Records and processes macro definitions and calls
- **Node Operations**: Tracks node allocation, deallocation, and manipulation
- **Output Events**: Captures character, glue, rule, and box output
- **Group Management**: Monitors save level changes and group boundaries
