# Build Data Scripts

This directory contains utility scripts for generating font and glyph mapping data files used by nvtexpy. These are one-time build scripts that generate the data files in `src/nvtexpy/engine/`.

## Scripts

### `make_glyphmap.py`
Builds the main glyph-to-unicode mapping file (`combined_glyphmap.txt`) by parsing:
- TeXLive glyphlist files (`glyphlist.txt`, `texglyphlist.txt`, `pdfglyphlist.txt`)
- Various font definition files from the TeXLive distribution

**Output:** `src/nvtexpy/engine/combined_glyphmap.txt`

### `make_fontmap.py`
Generates font-specific glyph mappings by:
- Reading font encoding files (`.enc`, `.map`, `.tfm`)
- Processing virtual fonts (`.vf`)
- Mapping glyphs to unicode characters

**Output:** `src/nvtexpy/engine/fonts_glyphmap.zip`

**Dependencies:** Requires `vf_reader.py` and output from `make_glyphmap.py`

### `make_fontmap_zhmetrics.py`
Generates glyph mappings for Chinese/Japanese/Korean (CJK) fonts using fontTools.

**Output:** Appends to `src/nvtexpy/engine/fonts_glyphmap.zip`

### `make_mathdef.py`
Parses math definitions from a CSV file (development/experimental).

**Note:** Contains hardcoded paths and is likely outdated.

### `vf_reader.py`
Utility module for reading TeX virtual font (`.vf`) files and extracting font remapping information.

## Usage

These scripts are intended to be run manually when:
- Updating the supported glyph/font mappings
- Adding support for new fonts
- Regenerating data files from updated TeXLive distributions

**Prerequisites:**
- TeXLive installation (typically at `/usr/share/texmf-dist/`)
- Python with nvtexpy development dependencies installed

**Example:**
```bash
cd scripts/build_data
python make_glyphmap.py
python make_fontmap.py
python make_fontmap_zhmetrics.py
```

**Important:** These scripts expect a TeXLive distribution to be installed at standard locations. They are primarily intended for development and data regeneration, not for end-user execution.

