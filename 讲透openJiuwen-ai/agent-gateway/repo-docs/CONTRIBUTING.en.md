# Contributing Guide

Thank you for your interest in Agent Gateway. Bug reports, features, documentation, and examples are all welcome.

中文: [CONTRIBUTING.md](CONTRIBUTING.md)

## Code of Conduct

- Respect every contributor and communicate kindly
- Keep Issues and PRs objective and focused on the problem
- Welcome developers of all skill levels and help newcomers

## Filing Issues

Submit on [GitCode Issues](https://gitcode.com/openJiuwen/agent-gateway/issues) and choose a template from `.gitcode/ISSUE_TEMPLATE.*`:

| Type | Description |
| --- | --- |
| Bug Report | Reproduction steps, expected behavior, actual behavior, environment |
| Feature Request | Use case, expected outcome, alternatives |
| Documentation | Missing, incorrect, or improvable documentation |

A bug report should include the gateway version, OS and Python version, reproduction commands, and relevant logs (`<root>/agent/.logs/`).

## Submitting Pull Requests

1. Fork [openJiuwen/agent-gateway](https://gitcode.com/openJiuwen/agent-gateway).
2. Branch from `agent_os` (the repository will move to `develop` later):

```bash
git checkout -b feature/your-feature-name origin/agent_os
```

3. Make changes and verify locally:

```bash
uv sync
./run_tests.sh -u          # unit tests
bash scripts/build.sh      # verify packaging when needed
```

4. Use Conventional Commits with sign-off:

```bash
git commit -s -m "feat(gateway): add xxx"
```

5. Push the branch and open a PR following `.gitcode/PULL_REQUEST_TEMPLATE.md`, describing the problem, changes, and test results.

## Branch and Commit Conventions

- Branch names: `feature/<name>`, `fix/<name>`, `docs/<name>`, `chore/<name>`
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/): `<type>(<scope>): <summary>`
- Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- One PR should do one thing; avoid unrelated formatting or refactoring

## Code Standards

- Follow PEP 8 and use type annotations; preserve the existing style of touched code
- Put new tests under `tests/unit_tests/`, name files `test_*.py` and functions `test_*`
- New Python files should include the copyright and license header used by existing files
- Do not commit `.venv/`, `build/`, `dist/`, coverage artifacts, logs, or real secrets

## Documentation Requirements

Feature PRs must update documentation:

- Chinese is authoritative: `docs/zh/`; English follows: `docs/en/`, with a symmetric structure
- Place documents in the Diátaxis categories: `tutorial/`, `how-to/`, `reference/`, `explanation/`
- Tutorials use numeric prefixes (`01-`, `02-`); other categories use kebab-case semantic names without numbers
- Add examples under `examples/<name>/` with a README (run commands and expected output)
- Update navigation links in `docs/README.md` and `docs/README_EN.md`

## Review and Merge

- A PR requires approval from at least one Committer
- All review comments must be resolved before merging
- Do not merge your own PR
- Ensure the associated pipeline and tests pass before merging

## Community Rules

By submitting code you agree to license your contribution under [Apache License 2.0](LICENSE). Please also follow:

- [openJiuwen Contributing Guide](https://gitcode.com/openJiuwen/community/blob/main/CONTRIBUTING_zh.md)
- [License and Copyright Guidelines](https://gitcode.com/openjiuwen/community/tree/main/contribute/License-and-Copyright-Guidelines.md)
- [Community Code of Conduct](https://gitcode.com/openJiuwen/community/blob/main/openJiuwen-Community-Code-of-Conduct.md)
