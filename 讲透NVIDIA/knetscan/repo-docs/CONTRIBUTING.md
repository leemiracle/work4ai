# Contributing to KNetScan

Thank you for your interest in contributing to KNetScan! This document outlines the process to help you get started.

## Making Changes

1. Make your changes in your feature branch.
2. Add or update tests as necessary.
3. Run tests to ensure your changes don't break existing functionality.
4. Update documentation if necessary.

## Pull Request Process

1. Update the README.md or documentation with details of changes if needed.
2. Update the CHANGELOG.md with details of changes if applicable.
3. The PR should work with existing tests and add new ones if introducing new functionality.
4. Once you have the sign-off of two maintainers, the PR can be merged.

## Go Module Tagging in this Repository

This repository contains multiple Go modules, each in its own subdirectory. To manage dependencies between modules and ensure reproducible builds, we follow a specific tagging convention.

### Tagging Convention

Each Go module in a subdirectory **must be tagged individually** using the following format:

```
directory/vX.Y.Z
```

**Example:**  
If you are releasing version `v1.2.3` of the module in the `knetscan` directory, the tag should be:

```
knetscan/v1.2.3
```

### Why This Matters

- **Go's module system uses these tags to resolve dependencies.**
- **Dependencies in `go.mod` files should reference the full module path and version, e.g.:**
  ```
  require github.com/NVIDIA/knetscan/knetscan v1.2.3
  ```
- **Using root-level tags (e.g., `v1.2.3`) will not work for module dependencies.**

## Coding Standards

- Follow Go best practices and style guidelines.
- Write clean, maintainable, and testable code.
- Include comments where necessary.
- Maintain backward compatibility unless explicitly making a breaking change.

## Developer Certificate of Origin (DCO)

We require all contributions to be signed off with the Developer Certificate of Origin (DCO), indicating that you have the right to contribute the code you are submitting. 

When you submit a pull request, you must include a sign-off statement in the commit message, certifying that you have the right to submit the code under the project's license. This is done using the `-s` or `--signoff` flag in git commit.

```bash
git commit -s -m "Your commit message"
```

The sign-off statement will look like:
```
Signed-off-by: Your Name <your.email@example.com>
```

By signing off, you certify to the statement of the [Developer Certificate of Origin](https://developercertificate.org/), which reads:

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

## License

By contributing to KNetScan, you agree that your contributions will be licensed under the project's [Apache 2.0 License](LICENSE). 