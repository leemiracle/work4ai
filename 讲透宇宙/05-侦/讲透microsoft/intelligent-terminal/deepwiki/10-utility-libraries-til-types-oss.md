<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/intelligent-terminal · page 10 Utility Libraries (til, types, oss) · fetched 2026-10-26 -->

# Utility Libraries (til, types, oss)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/buffer/out/ImageSlice.cpp](src/buffer/out/ImageSlice.cpp)
- [src/buffer/out/ImageSlice.hpp](src/buffer/out/ImageSlice.hpp)
- [src/cascadia/WinRTUtils/inc/Utils.h](src/cascadia/WinRTUtils/inc/Utils.h)
- [src/inc/LibraryIncludes.h](src/inc/LibraryIncludes.h)
- [src/inc/til.h](src/inc/til.h)
- [src/inc/til/color.h](src/inc/til/color.h)
- [src/inc/til/point.h](src/inc/til/point.h)
- [src/inc/til/size.h](src/inc/til/size.h)
- [src/inc/til/small_vector.h](src/inc/til/small_vector.h)
- [src/inc/til/static_map.h](src/inc/til/static_map.h)
- [src/renderer/atlas/atlas.vcxproj](src/renderer/atlas/atlas.vcxproj)
- [src/renderer/atlas/pch.h](src/renderer/atlas/pch.h)
- [src/terminal/adapter/SixelParser.cpp](src/terminal/adapter/SixelParser.cpp)
- [src/terminal/adapter/SixelParser.hpp](src/terminal/adapter/SixelParser.hpp)
- [src/terminal/adapter/charsets.hpp](src/terminal/adapter/charsets.hpp)
- [src/til/ut_til/ColorTests.cpp](src/til/ut_til/ColorTests.cpp)
- [src/til/ut_til/PointTests.cpp](src/til/ut_til/PointTests.cpp)
- [src/til/ut_til/RectangleTests.cpp](src/til/ut_til/RectangleTests.cpp)
- [src/til/ut_til/SizeTests.cpp](src/til/ut_til/SizeTests.cpp)
- [src/til/ut_til/SmallVectorTests.cpp](src/til/ut_til/SmallVectorTests.cpp)
- [src/til/ut_til/StaticMapTests.cpp](src/til/ut_til/StaticMapTests.cpp)
- [src/til/ut_til/sources](src/til/ut_til/sources)
- [src/til/ut_til/til.unit.tests.vcxproj](src/til/ut_til/til.unit.tests.vcxproj)
- [src/til/ut_til/til.unit.tests.vcxproj.filters](src/til/ut_til/til.unit.tests.vcxproj.filters)
- [src/types/colorTable.cpp](src/types/colorTable.cpp)
- [src/types/inc/colorTable.hpp](src/types/inc/colorTable.hpp)
- [src/types/inc/utils.hpp](src/types/inc/utils.hpp)
- [src/types/ut_types/UtilsTests.cpp](src/types/ut_types/UtilsTests.cpp)
- [src/types/utils.cpp](src/types/utils.cpp)
- [tools/ConsoleTypes.natvis](tools/ConsoleTypes.natvis)

</details>



The Intelligent Terminal codebase relies on a multi-layered utility infrastructure designed to provide high-performance terminal primitives, Unicode-aware type systems, and specialized third-party algorithms. This infrastructure is partitioned into the **Terminal Implementation Library (til)**, a **Types** library for domain-specific console objects, and a set of vendored **Open Source Software (OSS)** dependencies.

## Shared Infrastructure Overview

The utility stack bridges the gap between low-level Win32/DirectX APIs and the high-level terminal logic used in the renderer and buffer.

Terminal Utility Stack Architecture
```mermaid
graph TD
    subgraph "Terminal Application & Host"
        [TermControl] --> [TypesLib]
        [ConHost] --> [TIL]
    end

    subgraph "[Types Library]"
        [TypesLib] --> [TextAttribute]
        [TypesLib] --> [CodepointWidthDetector]
        [TypesLib] --> [ColorTable]
    end

    subgraph "[til: Terminal Implementation Library]"
        [TIL] --> [til::point/size/rect]
        [TIL] --> [til::color]
        [TIL] --> [til::small_rle]
        [TIL] --> [til::u8u16convert]
    end

    subgraph "[OSS Dependencies]"
        [TIL] --> [ChromiumBaseNumerics]
        [Renderer] --> [stb_rect_pack]
        [TerminalCore] --> [IntervalTree]
    end

    [TypesLib] -.-> [TIL]
```
Sources: [src/inc/LibraryIncludes.h:125-130](), [src/inc/til.h:17-25]()

## til: Terminal Implementation Library (#10.1)

The `til` library is a header-only collection of performance-oriented utilities. It provides the fundamental coordinate system used throughout the terminal, replacing or augmenting standard Win32 `COORD` and `RECT` types with modern C++ equivalents that support safe math via Chromium's numerics.

Key components include:
*   **Coordinate Primitives**: `til::point`, `til::size`, and `til::rect` provide `int32_t` based geometry with built-in conversion to Win32, Direct2D, and WinRT types [src/inc/til/point.h:30-33](), [src/inc/til/size.h:10-11]().
*   **Color Handling**: `til::color` is a universal 8bpp RGBA type that handles alpha blending and conversions between `COLORREF` and `D3DCOLORVALUE` [src/inc/til/color.h:14-39]().
*   **Storage Utilities**: `til::small_vector` for stack-allocated optimizations and `til::small_rle` for run-length encoding of buffer attributes [src/inc/til/small_vector.h](), [src/inc/til/rle.h]().
*   **String & Encoding**: `til::u8u16convert` provides high-speed UTF-8/UTF-16 conversion using Windows APIs but with a safer, more ergonomic interface [src/inc/til/u8u16convert.h]().

For details, see [til: Terminal Implementation Library](#10.1).

Sources: [src/inc/til.h:55-56](), [src/inc/til/point.h:8-10](), [src/inc/til/color.h:142-156]()

## Types Library: Colors, Glyphs, and Utilities (#10.2)

The `types` library contains console-specific logic that is too heavy for the header-only `til` but required by both the host and the terminal application. It defines how the terminal understands text properties and Unicode.

*   **Text Attributes**: Classes like `TextAttribute` and `TextColor` manage the SGR (Select Graphic Rendition) state, including 256-color lookups and RGB "TrueColor" storage [tools/ConsoleTypes.natvis:4-15]().
*   **Unicode Intelligence**: The `CodepointWidthDetector` determines if a character is narrow, wide (CJK), or part of a complex grapheme cluster.
*   **Parsing Utilities**: Includes `SixelParser` for handling DEC Sixel graphics [src/terminal/adapter/SixelParser.cpp:45-51]() and `Utils` for GUID/Color string parsing [src/types/utils.cpp:37-46]().

For details, see [Types Library: Colors, Glyphs, and Utilities](#10.2).

Sources: [src/types/inc/utils.hpp:16-17](), [src/terminal/adapter/SixelParser.cpp:55-57]()

## Vendored OSS Dependencies

The project vendors several lightweight OSS libraries to handle specialized tasks without introducing heavy external package managers.

| Library | Purpose | Code Location |
| :--- | :--- | :--- |
| **Chromium Base** | Safe integer math (prevents overflows in coordinate logic) | `dep/chromium/base/numerics/` |
| **Interval Tree** | Efficiently tracking URL/pattern ranges in the scrollback buffer | `src/inc/IntervalTree.h` |
| **stb** | `stb_rect_pack` is used by the AtlasEngine to pack glyphs into GPU textures | `oss/stb/` |
| **{fmt}** | High-performance string formatting and compile-time format checking | `src/inc/LibraryIncludes.h:84-99]` |
| **wyhash** | Fast, non-cryptographic hashing for internal maps and caches | `src/inc/til/hash.h` |

Sources: [src/inc/LibraryIncludes.h:74-78](), [src/inc/LibraryIncludes.h:101-102](), [src/renderer/atlas/BackendD3D.cpp]() (referenced)

## Utility Integration Mapping

The following diagram maps high-level utility concepts to their specific implementations within the `til` and `Microsoft::Console` namespaces.

Utility Entity Mapping
```mermaid
classDiagram
    class "Coordinate System" {
        til::point
        til::size
        til::rect
    }
    class "Color Management" {
        til::color
        Microsoft::Console::Utils::ColorFromHexString()
        Microsoft::Console::Utils::InitializeVT340ColorTable()
    }
    class "Memory & Performance" {
        til::small_vector
        til::small_rle
        til::generational
    }
    class "Data Conversion" {
        til::u8u16convert
        Microsoft::Console::Utils::GuidToString()
    }

    "Coordinate System" --|> "Chromium Safe Math" : uses base::CheckedNumeric
    "Color Management" --|> "til::color" : returns/consumes
```
Sources: [src/inc/til/point.h:19-27](), [src/types/utils.cpp:94-97](), [src/types/inc/utils.hpp:52-56]()

---

