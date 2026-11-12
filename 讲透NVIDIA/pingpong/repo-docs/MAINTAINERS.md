# Maintainers

NVIDIA maintains this project using an internal-development, public-release
model.

## Roles

- David Sheffield: project owner
- Stephen Hines (`@stephenhines`): repository administrator and release
  coordinator

## Development Model

Development and review occur within NVIDIA. This repository publishes approved
source releases and is currently not accepting external contributions.

## Dependency Management

The project does not vendor third-party code. It builds against the system
interfaces and libraries documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Verification

Release changes must build successfully with `make clean && make`. The command
line interface is smoke-tested with `./pingpong -h`, and benchmark execution is
tested on a Linux system that permits access to `perf_event_open` counters.

## Release Process

Release changes are reviewed through pull requests. Releases require the
applicable NVIDIA PLC, security, legal, and open source approvals before public
distribution. Changes are summarized in [CHANGELOG.md](CHANGELOG.md).

## Issue And Hotfix Handling

This project does not provide a public support commitment. Security reports
must follow [SECURITY.md](SECURITY.md) and must not be filed as public GitHub
issues. Any release hotfix follows the same review and approval requirements as
other release changes.
