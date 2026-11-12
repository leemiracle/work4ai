# Game Agent SDK

The Game Agent SDK provides on-device building blocks for AI companions, with a C99 ABI and a thin C++ wrapper for natural integration into game engines and other native applications. A companion uses AI inferencing locally on the end user's GPU with a small language model (SLM). The SDK exposes three groups of APIs:

- **Agent** APIs: stateful APIs that own conversation history and drive the inference loop autonomously, including any tool-call chains, with minimal application code.
- **Chat** APIs: stateless APIs that give developers direct control over inference.
- **RAG** APIs: enable semantic, lexical, and hybrid knowledge retrieval from developer-built databases, grounding model responses in up-to-date knowledge.

## Requirements

- Windows 10 or 11
- NVIDIA Ampere GPU or newer with sufficient VRAM (the bundled SLM uses ~3.8 GB)
- NVIDIA driver 570.65 or later
- Cuda 12.8 SDK or later

## Quick start

### Build the Project

Building from source requires Visual Studio 2019 or later (or the equivalent VS Build Tools).

    setup.bat
    build.bat

`setup.bat` generates Visual Studio project files under `_project/vs2022/`. `build.bat` builds the Release configuration; pass `-debug` for Debug.

### Get the Models

The four models bundled with the SDK (one SLM, two embedders, and a cross-encoder reranker; ~3 GB total) are not stored in this repository. Download the [source zip from the NVIDIA Developer Portal](https://developer.nvidia.com/downloads/ace/game-agent-sdk-v0.5.0-source.zip) and extract `data/models/` into your checkout. The source zip is a complete working tree, so it can also be used directly without a separate `git clone`.

### Run a Sample

Sample executables land in `_out/`. Agent-Sample is a good place to begin, a poker assistant that demonstrates the Agent APIs:

    cd _out
    Agent-Sample.exe

The available samples demonstrate how the SDK can be integrated for various use cases; they are intended as starting points and further tuning would be needed to improve response quality in a real application.

- `Agent-Sample.exe`: poker assistant on the Agent APIs. The SDK drives the inference-and-tool-call loop across two tools: `search` (poker knowledge, backed by RAG) and `check_status` (game state).
- `Chat-Sample.exe`: a simplified version of the same poker assistant on the Chat APIs, with the application driving the loop directly. Same prompt, tools, and RAG pipeline.
- `MultiAgent-Sample.exe`: two Agents sharing one SLM, with distinct identities and conversation histories.

Run any sample with `-h` for command-line options. For a full walkthrough of all samples, see [Samples](docs/sphinx/source/samples.md).

`BuildRag.exe` is also included -- a tool for building a semantic or lexical RAG database from raw text files. See [Building a RAG database](docs/sphinx/source/rag-building-a-database.md).

## Documentation

For API details, architecture, and in-depth sample walkthroughs, the documentation is the best place to start beyond this README:

- [Introduction](docs/sphinx/source/introduction.md)
- [API overview](docs/sphinx/source/api-overview.md)
- [Agent deep dive](docs/sphinx/source/agent-deep-dive.md)
- [Samples](docs/sphinx/source/samples.md)
- [Building a RAG database](docs/sphinx/source/rag-building-a-database.md)
- [Limitations](docs/sphinx/source/limitations.md)
- [Troubleshooting](docs/sphinx/source/troubleshooting.md)

## Packaging a release

`package.bat` creates a redistributable SDK zip with the version number you supply when prompted. `package_nomodels.bat` creates a smaller zip without the bundled models.

## License

The Game Agent SDK is licensed under the Apache License 2.0 (see [LICENSE.txt](LICENSE.txt)). Third-party components and their licenses are listed in [THIRD-PARTY-LICENSES.md](THIRD-PARTY-LICENSES.md).
