# Security Policy

Thank you for helping keep ImageGenCam secure.

## Reporting Security Issues

Please do not report security vulnerabilities through public GitHub issues,
pull requests, or discussions.

If you believe you have found a security vulnerability, follow OpenAI's
[Coordinated Vulnerability Disclosure Policy](https://openai.com/policies/coordinated-vulnerability-disclosure-policy/).
OpenAI's security program is managed through the
[OpenAI Bug Bounty Program](https://bugcrowd.com/openai).

## Scope

This repository contains software and hardware files for a local DIY camera
project. The companion web app is intended for local network use only. Do not
expose the app directly to the public internet without adding appropriate
authentication and transport security.

## Maintainer Checks

Before committing, run:

```bash
./scripts/install_git_hooks.sh
```

This enables the local pre-commit hook in `.githooks/pre-commit`, which runs
`scripts/check_secrets.sh --staged`.

To scan the current worktree manually, run:

```bash
./scripts/check_secrets.sh
```
