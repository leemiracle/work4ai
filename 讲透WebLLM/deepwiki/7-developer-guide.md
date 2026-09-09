> 来源: [https://deepwiki.com/mlc-ai/web-llm/7-developer-guide](https://deepwiki.com/mlc-ai/web-llm/7-developer-guide)
> DeepWiki mlc-ai/web-llm | Last indexed: 18 April 2025 (632d34

# Developer Guide

  Relevant source files 
 - [.github/workflows/build-site.yaml](https://github.com/mlc-ai/web-llm/blob/632d3472/.github/workflows/build-site.yaml)
 - [docs/Makefile](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/Makefile)
 - [docs/README.md](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/README.md?plain=1)
 - [docs/_static/img/mlc-logo-with-text-landscape.svg](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/_static/img/mlc-logo-with-text-landscape.svg)
 - [docs/conf.py](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/conf.py)
 - [docs/developer/add_models.rst](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/developer/add_models.rst)
 - [docs/developer/building_from_source.rst](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/developer/building_from_source.rst)
 - [docs/index.rst](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/index.rst)
 - [docs/make.bat](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/make.bat)
 - [docs/requirements.txt](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/requirements.txt)
 - [examples/chrome-extension-webgpu-service-worker/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/chrome-extension-webgpu-service-worker/package.json)
 - [examples/chrome-extension/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/chrome-extension/package.json)
 - [examples/get-started/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/get-started/package.json)
 - [examples/logit-processor/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/examples/logit-processor/package.json)
 - [package-lock.json](https://github.com/mlc-ai/web-llm/blob/632d3472/package-lock.json)
 - [package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json)
 - [scripts/gh_deploy_site.sh](https://github.com/mlc-ai/web-llm/blob/632d3472/scripts/gh_deploy_site.sh)
 - [scripts/local_deploy_site.sh](https://github.com/mlc-ai/web-llm/blob/632d3472/scripts/local_deploy_site.sh)
 - [utils/vram_requirements/package.json](https://github.com/mlc-ai/web-llm/blob/632d3472/utils/vram_requirements/package.json)
 
  This guide provides the essential information for developers who want to contribute to WebLLM or build their own applications using WebLLM's codebase. For information about using WebLLM as a library in your own projects, see [Basic Usage](https://deepwiki.com/mlc-ai/web-llm/3-worker-integrations).

 
## Setting Up the Development Environment

 
### Prerequisites

 
 - Node.js and npm
 - Git
 - A browser that supports WebGPU (Chrome is recommended)
 
 
### Building from Source

 
```

```

 Sources: [docs/developer/building_from_source.rst](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/developer/building_from_source.rst) [package.json8-13](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L8-L13)

 
### Project Structure

 
```

```

 Sources: [package.json14-17](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L14-L17)

 
## Development Workflow

 
### Code Standards

 WebLLM uses ESLint for code linting and Prettier for code formatting:

 
```

```

 Sources: [package.json9-13](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L9-L13)

 
### Running Tests

 WebLLM uses Jest for unit testing:

 
```

```

 Sources: [package.json11](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L11-L11)

 
### Testing Your Changes

 When making changes to the WebLLM codebase, you can test your modifications using any of the example applications:

 
 - Build the WebLLM library:

 
```

```
 - Modify the example's `package.json` to use your local build instead of the published package:

 
```

```
 - Install dependencies and start the example:

 
```

```
 
 Sources: [docs/developer/building_from_source.rst23-36](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/developer/building_from_source.rst#L23-L36)

 
## Architecture Overview

 
### Core Components and Relationships

 
```

```

 Sources: [package.json30-31](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L30-L31) [package.json54-55](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L54-L55)

 
### Request Flow for Chat Completion

 
```

```

 Sources: [package.json30-31](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L30-L31)

 
## Key Development Tasks

 
### Adding a New Model

 To add support for a new model in WebLLM, you need to:

 
 - Compile the model using MLC LLM
 - Add model configuration in the model registry
 - Implement tokenizer support if needed
 
 For detailed instructions on compiling and adding custom models, refer to the [Adding Models](https://deepwiki.com/mlc-ai/web-llm/7.1-building-from-source) documentation.

 Sources: [docs/developer/add_models.rst](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/developer/add_models.rst)

 
### Extending Worker Functionality

 WebLLM supports different execution environments through workers:

 
```

```

 Sources: [package.json35-36](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L35-L36)

 
### Implementing Advanced Features

 WebLLM supports advanced features such as:

 
 - Function calling
 - JSON mode
 - Logit processors (for custom token generation logic)
 
 Each of these features has an example implementation in the `examples/` directory.

 
## Working with Dependencies

 WebLLM has the following key dependencies:

 
| Dependency | Purpose | Version |
|---|---|---|
| @mlc-ai/web-runtime | TVM.js runtime for WebGPU execution | 0.18.0-dev2 |
| @mlc-ai/web-tokenizers | Tokenizer implementations | ^0.1.5 |
| @mlc-ai/web-xgrammar | Grammar support for structured generation | 0.1.0 |
| loglevel | Logging utility | ^1.9.1 |

 Sources: [package.json29-59](https://github.com/mlc-ai/web-llm/blob/632d3472/package.json#L29-L59)

 
## Contributing to Documentation

 WebLLM's documentation is built using Sphinx:

 
 - Install documentation dependencies:

 
```

```
 - Build the documentation:

 
```

```
 - View the documentation in your browser:

 
```

```
 
 Sources: [docs/README.md](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/README.md?plain=1) [docs/requirements.txt](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/requirements.txt) [docs/Makefile](https://github.com/mlc-ai/web-llm/blob/632d3472/docs/Makefile)

 
## Deployment Workflow

 
### Building and Deploying the Documentation Site

 The documentation site is automatically built and deployed through GitHub Actions:

 
```

```

 Sources: [.github/workflows/build-site.yaml](https://github.com/mlc-ai/web-llm/blob/632d3472/.github/workflows/build-site.yaml) [scripts/gh_deploy_site.sh](https://github.com/mlc-ai/web-llm/blob/632d3472/scripts/gh_deploy_site.sh)

 
### Releasing a New Version

 To release a new version of WebLLM:

 
 - Update version in `package.json`
 - Run tests and build
 - Publish to npm
 
 
## Troubleshooting Common Issues

 
| Issue | Possible Cause | Solution |
|---|---|---|
| Build fails | TypeScript errors | Check error messages and fix type issues |
| WebGPU not available | Browser doesn't support WebGPU | Use Chrome with WebGPU enabled |
| Model loading fails | Missing or corrupted model files | Check browser console for specific errors |
| Worker communication errors | CORS issues or worker initialization | Ensure proper CORS configuration in your web server |

 
## Contributing Guidelines

 When contributing to WebLLM:

 
 - Fork the repository
 - Create a feature branch
 - Make your changes following code standards
 - Write tests for your changes
 - Submit a pull request
 
 By following this developer guide, you should be equipped to contribute to the WebLLM project effectively or build custom applications using the WebLLM codebase.
