# OPEN SOURCE SOFTWARE NOTICE

Please note we provide an open source software notice along with this product and/or this product firmware (in the following just "this product"). The open source software licenses are granted by the respective right holders. And the open source licenses prevail all other license information with regard to the respective open source software contained in the product, including but not limited to End User Software Licensing Agreement. This notice is provided on behalf of Huawei Technologies Co. Ltd. and any of its local subsidiaries which may have provided this product to you in your local country.

## Warranty Disclaimer

THE OPEN SOURCE SOFTWARE IN THIS PRODUCT IS DISTRIBUTED IN THE HOPE THAT IT WILL BE USEFUL, BUT WITHOUT ANY WARRANTY, WITHOUT EVEN THE IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. SEE THE APPLICABLE LICENSES FOR MORE DETAILS.

## Scope

This repository does not vendor third-party source code. The table below lists the third-party software that the engine and the optional agent host declare as dependencies and that is installed from its upstream distribution at install time. The native drivers are built on the host against operating-system SDKs only and do not bundle third-party libraries. No AI model weights or model runtimes are included in this product.

## Copyright Notice and License Texts

### Engine runtime dependencies

| Software | Version constraint | License | Provenance |
|---|---|---|---|
| mcp (Model Context Protocol Python SDK) | >=1.29,<2 | MIT | PyPI package `mcp` (`https://github.com/modelcontextprotocol/python-sdk`) |
| jsonschema | >=4.25,<5 | MIT | PyPI package `jsonschema` (`https://github.com/python-jsonschema/jsonschema`) |
| regex | >=2024.11.6 | Apache-2.0 AND CNRI-Python | PyPI package `regex` (`https://github.com/mrabarnett/mrab-regex`) |
| Pillow | >=12.2,<13 | MIT-CMU (HPND) | PyPI package `pillow` (`https://github.com/python-pillow/Pillow`) |

### Optional agent host dependencies

| Software | License | Provenance |
|---|---|---|
| openai (OpenAI Python SDK, used as an OpenAI-compatible client) | Apache-2.0 | PyPI package `openai` (`https://github.com/openai/openai-python`) |
| FastAPI | MIT | PyPI package `fastapi` (`https://github.com/fastapi/fastapi`) |
| Starlette | BSD-3-Clause | PyPI package `starlette` (`https://github.com/encode/starlette`) |
| pydantic | MIT | PyPI package `pydantic` (`https://github.com/pydantic/pydantic`) |
| uvicorn | BSD-3-Clause | PyPI package `uvicorn` (`https://github.com/encode/uvicorn`) |
| httpx | BSD-3-Clause | PyPI package `httpx` (`https://github.com/encode/httpx`) |
| anyio | MIT | PyPI package `anyio` (`https://github.com/agronholm/anyio`) |

### Platform SDKs used by the native drivers (not redistributed)

| Component | Used by | Terms |
|---|---|---|
| Apple macOS SDK frameworks (AppKit, ApplicationServices, CoreGraphics, ScreenCaptureKit, ImageIO) | `engine/backends/macos` (Swift Package, built with the Swift 6 toolchain) | Apple SDK license; linked at build time on the user's machine |
| Microsoft Windows UI Automation (`UIAutomationCore.dll` type library) and .NET Framework | `engine/backends/windows` (C#, built with `csc.exe`); `Interop.NativeUIA.dll` is generated at build time from the host system's type library and is not shipped in source form | Microsoft Windows and .NET Framework terms |

### Software: Python 3.11.x, 3.12.x, 3.13.x

**License:** Python Software Foundation License V2 (`https://docs.python.org/3/license.html`)

## License Texts

### MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### BSD 3-Clause License

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### HPND / MIT-CMU License (Pillow)

Permission to use, copy, modify and distribute this software and its documentation for any purpose and without fee is hereby granted, provided that the above copyright notice appears in all copies, and that both that copyright notice and this permission notice appear in supporting documentation, and that the name of the copyright holder not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

THE COPYRIGHT HOLDER DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

### Apache License 2.0

The full text of the Apache License, Version 2.0 is provided in the [LICENSE](LICENSE) file of this repository.

### CNRI Python License (part of `regex`)

See `https://spdx.org/licenses/CNRI-Python.html`.
