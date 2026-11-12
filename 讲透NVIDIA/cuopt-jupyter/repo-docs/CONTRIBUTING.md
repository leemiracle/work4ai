# Contributing to NVIDIA cuopt-jupyter repository

The scope of this repository is quite focused. It provides a bootstrap notebook that installs missing libraries on the Jupyter host necessary to run cuOpt, and then it downloads additional notebooks from github.com/NVIDIA/cuopt-examples.
It is designed primarily for use with a NVIDIA Brev Launchable, but may be of use on other platforms.  The scope of this repository will remain focused on this one deliverable.

Having said that, bugs and feature requests are still possible even for a small repository.

Contributions to NVIDIA cuopt-jupyter fall into the following categories:

1. To report a bug, request a new feature, or report a problem with documentation, please file an issue describing the problem or new feature in detail. The team evaluates and triages issues, and schedules them for a release. If you believe the issue needs priority attention, please comment on the issue to notify the team.

2. To implement a feature or bug fix for an existing issue, please follow the code contributions guide below. If you need more context on a particular issue, please ask in a comment.

As contributors and maintainers to this project, you are expected to abide by the project's code of conduct.

## Code contributions

### Your first issue

1. Find an issue to work on. The best way is to look for the `good first issue` or `help wanted` labels.
2. Comment on the issue stating that you are going to work on it.
3. Create a fork of the repository and check out a branch with a name that describes your planned work.
4. Write code to address the issue.
5. Create your pull request.
6. Wait for other developers to review your code and update code as needed.
7. Once reviewed and approved, a team member will merge your pull request.

If you are unsure about anything, don't hesitate to comment on issues and ask for clarification!

## Developer Guidelines

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints for function arguments and return values
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable and function names
- Add comments for complex logic

### Notebook Guidelines

- Use Jupyter notebooks for interactive examples
- Include markdown cells with clear explanations
- Add code comments for complex operations
- Include visualization cells for results
- Provide example outputs and expected results
- Add troubleshooting sections for common issues
- Include links to relevant documentation

