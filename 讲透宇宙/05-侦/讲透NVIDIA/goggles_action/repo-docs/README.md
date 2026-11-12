# Goggles Action

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A collection of GitHub Actions to streamline automation for NVIDIA GitHub repositories.

## Actions

### LLM Issue Labeler

This action automatically labels GitHub issues using a Language Model (LLM).

For detailed setup and usage instructions, see the [LLM Issue Labeler README](./actions/llm_label/README.md).

### PR Checklist Validator

Ensures that every task list item in a pull request description is either
checked or struck through before the workflow continues. Trigger the workflow on
`pull_request` events including the `edited` type so it reruns whenever the PR
description changes.

For usage instructions, see the [PR Checklist Validator README](./actions/pr_checklist/README.md).
