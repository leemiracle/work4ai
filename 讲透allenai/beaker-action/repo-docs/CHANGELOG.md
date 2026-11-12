# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Added `jq` to the Docker image so you can things like:
  ```yaml
  uses: allenai/beaker-action
  with:
    token: ${{ secrets.BEAKER_TOKEN }}
    command: account
    args: whoami --format=json | jq '.[0].name'
  ```

## [v0.2.0](https://github.com/allenai/beaker-action/releases/tag/v0.2.0) - 2022-04-12

### Changed

- Official marketplace name of action changed to `beaker-command`.

## [v0.1.0](https://github.com/allenai/beaker-action/releases/tag/v0.1.0) - 2022-04-12

### Added

- Added initial version of action.
