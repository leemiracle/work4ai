> 来源: [https://deepwiki.com/mozilla-ai/llamafile/15-third-party-dependencies](https://deepwiki.com/mozilla-ai/llamafile/15-third-party-dependencies)
> DeepWiki mozilla-ai/llamafile | Last indexed: 29 August 2026 (435512

# Third-Party Dependencies

  Relevant source files 
 - [third_party/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/BUILD.mk)
 - [third_party/mbedtls/README.llamafile](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/mbedtls/README.llamafile)
 - [third_party/mbedtls/include/mbedtls/version.h](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/mbedtls/include/mbedtls/version.h)
 - [third_party/sqlite/BUILD.mk](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/BUILD.mk)
 - [third_party/sqlite/README.llamafile](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/README.llamafile)
 - [third_party/sqlite/shell.c](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/shell.c)
 - [third_party/sqlite/sqlite3.c](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/sqlite3.c)
 - [third_party/sqlite/sqlite3.h](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/sqlite3.h)
 - [third_party/sqlite/sqlite3ext.h](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/sqlite3ext.h)
 
  The llamafile project bundles several mature third-party libraries to provide specialized functionality such as secure networking, persistent storage, image processing, and high-performance number conversion. These dependencies are integrated directly into the build system to ensure the project remains a self-contained, "actually portable" executable.

 
### Dependency Integration Overview

 Llamafile uses a unified build system where third-party packages are included via `BUILD.mk` files [third_party/BUILD.mk1-4](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/BUILD.mk#L1-L4) This allows the project to apply local patches and specific compiler flags to external code to maintain compatibility with Cosmopolitan Libc. For instance, the SQLite integration uses `-mgcc` and several `SQLITE_ENABLE` flags to tune the engine for the llamafile environment [third_party/sqlite/BUILD.mk22-54](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/BUILD.mk#L22-L54)

 **Dependency to Code Entity Mapping**

 
```

```

 **Sources:** [third_party/BUILD.mk1-12](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/BUILD.mk#L1-L12) [third_party/mbedtls/README.llamafile1-3](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/mbedtls/README.llamafile#L1-L3) [third_party/sqlite/README.llamafile1-3](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/README.llamafile#L1-L3) [third_party/sqlite/BUILD.mk22-54](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/BUILD.mk#L22-L54)

 
---

 
### TLS and Security Libraries

 Llamafile integrates **mbedTLS**, a library developed by ARM Limited, to provide TLS support for its embedded HTTP server [third_party/mbedtls/README.llamafile1-3](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/mbedtls/README.llamafile#L1-L3) This enables secure HTTPS communication when running in server mode. The codebase includes a mapping header to ensure standard include paths like `<mbedtls/version.h>` point to the vendored copy [third_party/mbedtls/include/mbedtls/version.h1-4](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/mbedtls/include/mbedtls/version.h#L1-L4)

 The integration includes specific performance enhancements for x86-64 architectures [third_party/mbedtls/README.llamafile14-16](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/mbedtls/README.llamafile#L14-L16) It also bundles a root certificate store to allow llamafile to verify external connections when acting as a client (e.g., in API mode).

 For details, see [TLS and Security Libraries](https://deepwiki.com/mozilla-ai/llamafile/15.1-tls-and-security-libraries).

 **Sources:** [third_party/mbedtls/README.llamafile1-16](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/mbedtls/README.llamafile#L1-L16) [third_party/mbedtls/include/mbedtls/version.h1-4](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/mbedtls/include/mbedtls/version.h#L1-L4)

 
---

 
### SQLite and Media Libraries

 For persistence and media handling, llamafile bundles the following:

 
 - **SQLite**: The world's most widely deployed database engine. Llamafile uses the SQLite amalgamation (version 3.47.1), which combines the entire core library into a single `sqlite3.c` file for maximum compiler optimization [third_party/sqlite/sqlite3.c1-8](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/sqlite3.c#L1-L8) The library is configured with extensive features enabled, including FTS5, RTREE, and Math functions [third_party/sqlite/BUILD.mk38-42](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/BUILD.mk#L38-L42) The project also includes the `shell.c` to build a standalone `sqlite3` shell utility [third_party/sqlite/BUILD.mk16-18](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/BUILD.mk#L16-L18)
 - **STB**: A collection of single-file public domain libraries used primarily for image decoding in multimodal (LLaVA) modes and audio processing in whisperfile via `stb_vorbis`.
 
 **Library Components**

 
| Library | Primary Files | Purpose |
|---|---|---|
| SQLite | sqlite3.c, sqlite3.h | Persistent storage and SQL query engine third_party/sqlite/BUILD.mk6-11 |
| STB Image | stb_image.h | Decoding JPG, PNG, etc., for vision models |
| STB Vorbis | stb_vorbis.c | Audio decoding for whisperfile |

 For details, see [SQLite and Media Libraries](https://deepwiki.com/mozilla-ai/llamafile/15.2-sqlite-and-media-libraries).

 **Sources:** [third_party/sqlite/sqlite3.c1-22](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/sqlite3.c#L1-L22) [third_party/sqlite/shell.c1-32](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/shell.c#L1-L32) [third_party/sqlite/BUILD.mk6-12](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/BUILD.mk#L6-L12) [third_party/sqlite/README.llamafile1-16](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/README.llamafile#L1-L16) [third_party/sqlite/sqlite3.h149-151](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/sqlite/sqlite3.h#L149-L151)

 
---

 
### Utility Dependencies

 Llamafile also includes specialized utilities to manage its unique distribution format:

 
 - **double-conversion**: Provides binary-to-text and text-to-binary routines for IEEE doubles, ensuring fast and accurate number formatting in JSON responses.
 - **zipalign**: A utility used during the build process to ensure that model weights embedded within the ZIP-based APE executable are aligned to 64KB boundaries [third_party/BUILD.mk15-20](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/BUILD.mk#L15-L20) This alignment is critical for memory-mapping weights directly onto GPUs. It is compiled with `zlib` support from the Cosmopolitan toolchain [third_party/BUILD.mk24-26](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/BUILD.mk#L24-L26)
 
 **Build Integration Diagram**

 
```

```

 **Sources:** [third_party/BUILD.mk15-30](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/BUILD.mk#L15-L30) [third_party/double-conversion/BUILD.mk1](https://github.com/mozilla-ai/llamafile/blob/43551265/third_party/double-conversion/BUILD.mk#L1-L1)
