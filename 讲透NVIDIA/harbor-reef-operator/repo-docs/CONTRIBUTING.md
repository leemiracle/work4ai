# Contributing to harbor-reef-operator

Thank you for your interest in contributing to harbor-reef-operator! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Issues

- Check existing issues to avoid duplicates
- Provide a clear description of the problem
- Include steps to reproduce the issue
- Include relevant logs, error messages, and environment details (Kubernetes version, operator version, etc.)

### Submitting Changes

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Ensure your code follows the best practices and coding standards
5. Test your changes thoroughly
6. Commit your changes with a signed-off commit (see [Developer Certificate of Origin](#developer-certificate-of-origin) below)
7. Submit a merge request

## Development Setup

### Prerequisites

- Go 1.24 or later
- Docker
- Access to a Kubernetes cluster (for testing)
- kubectl configured for your cluster

### Building Locally

```bash
# Tidy dependencies
go mod tidy

# Build the binary
go build -o harbor-reef-operator .

# Build Docker image
docker build -t harbor-reef-operator:dev .
```

### Running Tests

```bash
go test ./...
```

## Code Style

- Follow standard Go conventions and idioms
- Use `gofmt` to format your code
- Run `go vet` to catch common issues
- Keep functions focused and well-documented
- Add comments for exported functions and types

## Commit Messages

- Use clear, descriptive commit messages
- Start with a short summary (50 chars or less)
- Provide additional context in the body if needed
- Reference related issues where applicable

Example:
```
Add support for custom annotation prefix

- Allow users to configure the annotation prefix via environment variable
- Update documentation with new configuration option

Fixes #123

Signed-off-by: Your Name <your.email@example.com>
```

## Developer Certificate of Origin

This project uses the [Developer Certificate of Origin (DCO)](https://developercertificate.org/) to ensure that contributors have the right to submit their contributions under the project's license.

By contributing to this project, you agree to the DCO. This means you certify that you wrote the contribution or otherwise have the right to submit it under the open source license used by this project.

### Full DCO Text

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

### How to Sign Your Commits

You must sign off on your commits to indicate your agreement with the DCO. Add a `Signed-off-by` line to your commit messages:

```
Signed-off-by: Your Name <your.email@example.com>
```

You can do this automatically by using the `-s` flag when committing:

```bash
git commit -s -m "Your commit message"
```

To configure Git to always sign off on commits for this repository:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

**Note:** The email address used for the sign-off must match the email address associated with your Git commits.

## Pull Request Process

1. Ensure your changes pass all tests and linting
2. Update documentation if your changes affect user-facing behavior
3. Ensure all commits are signed off (DCO)
4. Request review from maintainers
5. Address any feedback from reviewers
6. Once approved, a maintainer will merge your contribution

## License

By contributing to this project, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).

## Questions?

If you have questions about contributing, feel free to open an issue for discussion.
