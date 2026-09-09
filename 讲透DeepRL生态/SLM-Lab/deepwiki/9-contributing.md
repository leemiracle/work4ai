> 来源: [https://deepwiki.com/kengz/SLM-Lab/9-contributing](https://deepwiki.com/kengz/SLM-Lab/9-contributing)
> DeepWiki kengz/SLM-Lab | Last indexed: 26 February 2026 (d3128a

# Contributing

  Relevant source files 
 - [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/kengz/SLM-Lab/blob/d3128a8a/.github/PULL_REQUEST_TEMPLATE.md?plain=1)
 - [CODE_OF_CONDUCT.md](https://github.com/kengz/SLM-Lab/blob/d3128a8a/CODE_OF_CONDUCT.md?plain=1)
 - [README.md](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1)
 - [slm_lab/lib/viz.py](https://github.com/kengz/SLM-Lab/blob/d3128a8a/slm_lab/lib/viz.py)
 
  This page describes the contribution process for SLM Lab: how to submit pull requests, how to document experiment results for reproducibility, and the community code of conduct. For background on how experiments are structured and run, see the [Experiment System](https://deepwiki.com/kengz/SLM-Lab/4-experiment-system) and [Configuration and Spec Files](https://deepwiki.com/kengz/SLM-Lab/7-configuration-and-spec-files) pages.

 
---

 
## Pull Request Types

 SLM Lab uses a **dual-track PR template** defined in [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/kengz/SLM-Lab/blob/d3128a8a/.github/PULL_REQUEST_TEMPLATE.md?plain=1) Every PR falls into one of two categories:

 
| Track | Purpose | Required Content |
|---|---|---|
| Code Change | Bug fixes, new features, refactors | Description of changes, code snippets, reproduction steps |
| Experiment Result | New benchmark runs, algorithm evaluations | Abstract, methodology, spec file location, git SHA, result data |

 The template contains both sections separated by a divider. Contributors should fill out only the section that applies and remove the other.

 
---

 
## Code Change PRs

 Use the top section of the PR template for any change to source code.

 
 - Describe what changed and why.
 - List any behavioral implications (e.g., changes to training dynamics, API changes).
 - Include code snippets or run commands if the change requires specific steps to reproduce or verify.
 
 **PR Template (code section):**

 
```
## Title of code changes

- describe the code changes and implications
- add instructions to reproduce if relevant

```python
some code snippets
```

 
```
Sources: <FileRef file-url="https://github.com/kengz/SLM-Lab/blob/d3128a8a/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L1-L9" min=1 max=9 file-path=".github/PULL_REQUEST_TEMPLATE.md">.github/PULL_REQUEST_TEMPLATE.md:1-9</FileRef>

---

## Experiment Result PRs

Use the bottom section of the PR template when contributing experiment results: new benchmark numbers, algorithm comparisons, or ablation studies.

### Required Fields

| Field | Description |
|---|---|
| **Abstract** | Brief description of what the experiment tests and what it contributes |
| **Methodology** | Algorithms and methods used |
| **Spec file location** | Path in the repository to the spec JSON used |
| **Git SHA** | The commit hash embedded in the saved spec file |
| **Run command** | Exact command used to reproduce the run |
| **Data** | Link to a zip of the output data files |

### Reproducibility Requirements

Every experiment run in SLM Lab saves its spec file with the git SHA embedded in the output directory. This allows exact reproduction of results. When submitting experiment results, the spec file path and git SHA must both be present so reviewers can reproduce the run.

The canonical run command format is:

```bash
uv run slm-lab <spec file>
```

 or with explicit arguments:

 
```

```

 For cloud runs:

 
```

```

 Sources: [.github/PULL_REQUEST_TEMPLATE.md14-36](https://github.com/kengz/SLM-Lab/blob/d3128a8a/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L14-L36) [README.md64-84](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L64-L84)

 
---

 
## Reproducibility Flow

 The following diagram shows how code, spec files, and git history connect to make experiment results verifiable.

 **Diagram: Experiment Reproducibility Chain**

 
```

```

 Sources: [.github/PULL_REQUEST_TEMPLATE.md14-36](https://github.com/kengz/SLM-Lab/blob/d3128a8a/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L14-L36) [README.md34-36](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L34-L36)

 
---

 
## PR Template Structure

 **Diagram: PR Template Decision Tree**

 
```

```

 Sources: [.github/PULL_REQUEST_TEMPLATE.md1-36](https://github.com/kengz/SLM-Lab/blob/d3128a8a/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L1-L36)

 
---

 
## Code of Conduct

 SLM Lab adopts the [Contributor Covenant](http://contributor-covenant.org) version 1.4, defined in [CODE_OF_CONDUCT.md](https://github.com/kengz/SLM-Lab/blob/d3128a8a/CODE_OF_CONDUCT.md?plain=1)

 
### Expected Behavior

 
 - Use welcoming and inclusive language.
 - Be respectful of differing viewpoints and experience levels.
 - Accept constructive criticism gracefully.
 - Focus on what is best for the community.
 - Show empathy toward other contributors.
 
 
### Unacceptable Behavior

 
 - Sexualized language, imagery, or unwelcome advances.
 - Trolling, insulting or derogatory comments, personal or political attacks.
 - Public or private harassment.
 - Publishing others' private information without permission.
 - Any conduct reasonably considered inappropriate in a professional setting.
 
 
### Enforcement

 Violations may be reported to:

 
 - Wah Loon Keng: `kengzwl@gmail.com`
 - Laura Graesser: `lhgraesser@gmail.com`
 
 Project maintainers will review and investigate all complaints with confidentiality, and may remove, edit, or reject contributions that violate this Code of Conduct, or temporarily or permanently ban contributors.

 Sources: [CODE_OF_CONDUCT.md1-47](https://github.com/kengz/SLM-Lab/blob/d3128a8a/CODE_OF_CONDUCT.md?plain=1#L1-L47)

 
---

 
## Contribution Checklist

 The following table summarizes what is required before submitting each PR type.

 
| Requirement | Code PR | Experiment PR |
|---|---|---|
| Description of changes | ✓ | — |
| Code snippets / reproduction steps | ✓ (if relevant) | — |
| Abstract and methodology | — | ✓ |
| Spec file path in repo | — | ✓ |
| Git SHA from saved spec | — | ✓ |
| Exact run command | — | ✓ |
| Output data zip | — | ✓ |
| Passes CI | ✓ | ✓ |

 Sources: [.github/PULL_REQUEST_TEMPLATE.md1-36](https://github.com/kengz/SLM-Lab/blob/d3128a8a/.github/PULL_REQUEST_TEMPLATE.md?plain=1#L1-L36) [README.md64-119](https://github.com/kengz/SLM-Lab/blob/d3128a8a/README.md?plain=1#L64-L119)
