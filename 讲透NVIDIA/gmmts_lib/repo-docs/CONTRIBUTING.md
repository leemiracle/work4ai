# Contributing to GMMTS

If you are interested in contributing to GMMTS, your contributions will fall
into three categories:
1. You want to report a bug, feature request, or documentation issue
    - File an [issue](https://github.com/NVIDIA/gmmts_lib/issues/new/choose)
    describing what you encountered or what you want to see changed.
    - Please run and paste the output of the `print_env.sh` script while
    reporting a bug to gather and report relevant environment details.
    - Maintainers will evaluate the issues and triage them. If you believe the issue needs priority attention,
    comment on the issue to notify the team.
2. You want to propose a new Feature and implement it
    - Post about your intended feature, and we shall discuss the design and
    implementation.
    - Once we agree that the plan looks good, go ahead and implement it, using
    the [code contributions](#code-contributions) guide below.
3. You want to implement a feature or bug-fix for an outstanding issue
    - Follow the [code contributions](#code-contributions) guide below.
    - If you need more context on a particular issue, please ask and we shall
    provide.

## Code contributions

### Your first issue

1. Read the project's [README.md](https://github.com/NVIDIA/gmmts_lib/blob/main/README.md)
    to learn how to setup the development environment.
2. Find an issue to work on. Look for issues labeled [good first issue](https://github.com/NVIDIA/gmmts_lib/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
    or [help wanted](https://github.com/NVIDIA/gmmts_lib/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22).
3. Comment on the issue saying you are going to work on it.
4. Code! Make sure to update or add tests where applicable.
5. When done, [create your pull request](https://github.com/NVIDIA/gmmts_lib/compare).
6. Verify that CI passes all [status checks](https://help.github.com/articles/about-status-checks/), or fix if needed.
7. Wait for other developers to review your code and update code as needed.
8. Once reviewed and approved, a maintainer will merge your pull request.

Remember, if you are unsure about anything, don't hesitate to comment on issues and ask for clarifications!

### Branch naming

Branches used to create PRs should have a name of the form `<type>-<name>`
which conforms to the following conventions:
- Type:
    - fea - For if the branch is for a new feature(s)
    - enh - For if the branch is an enhancement of an existing feature(s)
    - bug - For if the branch is for fixing a bug(s) or regression(s)
- Name:
    - A name to convey what is being worked on
    - Please use dashes or underscores between words as opposed to spaces.

For all development, your changes should be pushed into a branch in your own fork of GMMTS and then create a pull request when the code is ready.

## Attribution
Portions adopted from https://github.com/pytorch/pytorch/blob/master/CONTRIBUTING.md
