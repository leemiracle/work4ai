# Media File Generator

Convert MP4 video files to raw media formats compatible with **SMPTE ST 2110-20** Professional Media Over Managed IP Networks: Uncompressed Active Video.

## Overview

This tool converts standard MP4 video files into raw packed formats suitable for use with NVIDIA Rivermax SDK and SMPTE ST 2110 video streaming workflows.

> ⚠️ **Note:** This tool is in early development and has not been thoroughly tested across all format combinations.

### Supported Output Formats

| Format | Description | Bit Depths | Resolutions |
|--------|-------------|------------|-------------|
| `ycbcr422` | YCbCr 4:2:2 chroma subsampling | 10-bit, 12-bit | FHD, UHD |
| `ycbcr420` | YCbCr 4:2:0 chroma subsampling | 10-bit only | FHD, UHD |
| `rgb` | RGB color space | 8-bit, 10-bit, 12-bit | FHD, UHD |

### Valid Combinations

| Format | FHD/8 | FHD/10 | FHD/12 | UHD/8 | UHD/10 | UHD/12 |
|--------|:-----:|:------:|:------:|:-----:|:------:|:------:|
| ycbcr422 | ✗ | ${\color{green}✓}$ | ${\color{green}✓}$ | ✗ | ${\color{green}✓}$ | ${\color{green}✓}$ |
| ycbcr420 | ✗ | ${\color{green}✓}$ | ✗ | ✗ | ${\color{green}✓}$ | ✗ |
| rgb | ${\color{green}✓}$ | ${\color{green}✓}$ | ${\color{green}✓}$ | ${\color{green}✓}$ | ${\color{green}✓}$ | ${\color{green}✓}$ |

## Quick Start

**Prerequisites:** Make sure ffmpeg and build tools (make, g++) are installed (see Installation section below).

```bash
# Build the converter first (one-time setup)
./generate_media_file.sh --build

# Basic YCbCr 4:2:2 conversion
./generate_media_file.sh -i input.mp4 -o output.ycbcr -f ycbcr422

# RGB 8-bit (fast - no converter needed)
./generate_media_file.sh -i input.mp4 -o output.rgb -f rgb -b 8

# UHD 12-bit with custom duration
./generate_media_file.sh -i input.mp4 -o output.ycbcr -f ycbcr422 -r UHD -b 12 -d 10
```

## Installation

### Prerequisites

You need to install these dependencies manually:

- **ffmpeg** - Video processing tool for decoding MP4 files and converting them to raw formats
- **make, g++** - Build tools required to compile the media_converter

### Installing Dependencies

**Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg build-essential
```

**RHEL/CentOS/Fedora:**
```bash
# RHEL/CentOS
sudo yum install epel-release
sudo yum install ffmpeg
sudo yum groupinstall "Development Tools"

# Fedora
sudo dnf install ffmpeg
sudo dnf groupinstall "Development Tools"
```

### Building media_converter

After installing the dependencies, build the media_converter binary:

```bash
# Option 1: Use the built-in build command
./generate_media_file.sh --build

# Option 2: Build manually
cd src && make media_converter
```

The `--build` flag checks build dependencies (make, g++) and builds media_converter if it's missing.

## Usage

```
./generate_media_file.sh -i <MP4_FILE> -o <OUTPUT_FILE> -f <FORMAT> [OPTIONS]
```

### Required Parameters

| Flag | Parameter | Description |
|------|-----------|-------------|
| `-i` | `<MP4_FILE>` | Input MP4 file to convert |
| `-o` | `<OUTPUT_FILE>` | Output file name (e.g., output.ycbcr) |
| `-f` | `<FORMAT>` | Pixel format: `ycbcr422`, `ycbcr420`, or `rgb` |

### Optional Parameters

| Flag | Parameter | Default | Description |
|------|-----------|---------|-------------|
| `-r` | `<RESOLUTION>` | FHD | Resolution: `FHD` (1920×1080) or `UHD` (3840×2160) |
| `-b` | `<BIT_DEPTH>` | 10 | Bit depth: `8`, `10`, or `12` (8 only for rgb) |
| `-p` | `<FPS>` | 50 | Frame rate in frames per second |
| `-d` | `<DURATION>` | 3 | Duration in seconds to extract |
| `-s` | `<START_TIME>` | 0 | Start time offset in seconds |

### Help

```bash
# Quick help
./generate_media_file.sh -h

# Full documentation
./generate_media_file.sh --help
```

## Examples

#### YCbCr 4:2:2 10-bit FHD

```bash
./generate_media_file.sh -i video.mp4 -o video.ycbcr -f ycbcr422 -r FHD -b 10
```

#### YCbCr 4:2:0 10-bit UHD (starting at 30 seconds)

```bash
./generate_media_file.sh -i video.mp4 -o video.ycbcr -f ycbcr420 -r UHD -s 30
```

#### RGB 12-bit at 60fps

```bash
./generate_media_file.sh -i video.mp4 -o video.rgb -f rgb -b 12 -p 60
```

#### RGB 8-bit (fast conversion)

```bash
./generate_media_file.sh -i video.mp4 -o video.rgb -f rgb -b 8
```

> **Note:** RGB 8-bit uses direct ffmpeg output and skips the converter step.

#### Extract 5 seconds starting at 1 minute

```bash
./generate_media_file.sh -i video.mp4 -o clip.ycbcr -f ycbcr422 -d 5 -s 60
```

## Conversion Process

### Format Transformation

**ffmpeg** outputs video in planar format, where each color component (Y, Cb, Cr or R, G, B) is stored in a separate continuous plane:

```
Planar:  YYYY... CbCbCb... CrCrCr...  (separate planes)
```

**SMPTE ST 2110-20** requires packed format, where color components are interleaved per pixel group:

```
Packed:  Cb Y Cr Y Cb Y Cr Y...       (interleaved samples)
```

The **media_converter** performs this planar-to-packed conversion and handles bit-packing.

### For YCbCr and RGB 10/12-bit

1. **ffmpeg** extracts raw video from MP4 in planar format
2. **media_converter** transforms planar to packed format
3. Output file is ready for SMPTE ST 2110-20 streaming

### For RGB 8-bit

1. **ffmpeg** converts MP4 directly to RGB24 packed format
2. No additional conversion needed (faster)

## File Structure

```
├── generate_media_file.sh   # Main conversion script
├── README.md                # This file
└── src/                     # Backend implementation
    ├── media_converter.cpp  # C++ converter source
    └── Makefile             # Build configuration
```

## Supported Platforms

- **Linux only** (This tool was developed on Ubuntu)
- Requires bash installed on the system
