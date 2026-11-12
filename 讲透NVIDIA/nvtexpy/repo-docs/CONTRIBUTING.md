## NVTexPy Contribution Rules

Thank you for your interest in contributing to NVTexPy! This document provides guidelines for contributing to the NVTexPy project, which provides Python hooks for the NVTexLive pipeline to enable machine learning OCR annotations for LaTeX documents.

#### Issue Tracking

* All enhancement, bugfix, or change requests must begin with the creation of a [NVTexPy Issue Request](https://github.com/NVIDIA/nvtexpy/issues).
  * The issue request must be reviewed by NVTexPy maintainers and approved prior to code review.


#### NVTexPy-Specific Considerations

When contributing to NVTexPy, please keep in mind:

- **Integration with pdftex**: NVTexPy works closely with a modified pdftex binary. Changes to the engine interface must be carefully tested.
- **Performance**: NVTexPy runs during LaTeX compilation, so performance is critical. Profile your changes for large documents.
- **Memory Management**: Be mindful of memory usage, especially when processing large documents with many pages.
- **Output Formats**: Ensure changes maintain compatibility with all supported output formats (flat layout, pickle).
- **Font Handling**: Test changes with various fonts and ensure glyph mapping works correctly.


#### Coding Guidelines

- All source code contributions must adhere to Python best practices and PEP 8 standards.

- In addition, please follow the existing conventions in the relevant file, module, and project when you add new code or when you extend/fix existing functionality.


#### Development Setup

Before contributing, set up your development environment:

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/nvtexpy.git
cd nvtexpy

# Set up development environment with uv
just dev-sync

# Verify the installation
python -c "import nvtexpy; print(nvtexpy.__file__)"
```


#### Code Formatting and Style

- To maintain consistency in code formatting and style, you should run `ruff` on the modified sources. This applies NVTexPy code formatting rules to:
  - Function, method, class, and variable naming (following Python conventions)
  - Docstring style (Google format)
  - Type hints and annotations
  - Import organization
  - Line length (100 characters)

- Use the provided `just` commands for development:
  ```bash
  # Sync development environment
  just dev-sync
  
  # Check code style and linting
  just check
  
  # Auto-fix formatting issues, linting, and license headers
  just fix
  
  # Run tests within nvtexlive container
  just nvtexlive-test
  ```

- Avoid introducing unnecessary complexity into existing code so that maintainability and readability are preserved.


#### Python Best Practices

- **Type Hints**: Always use type hints for function signatures and class attributes:
  ```python
  from pathlib import Path
  from typing import Optional, Dict, Any, List
  
  def process_tex_file(
      input_path: Path, 
      output_dir: Optional[Path] = None,
      options: Dict[str, Any] = None
  ) -> List[Dict[str, Any]]:
      """Process a TeX file and return structured output."""
      ...
  ```

- **Pathlib**: Use `pathlib.Path` instead of string paths:
  ```python
  # Good
  from pathlib import Path
  output_file = Path("output") / "result.pkl"
  
  # Avoid
  output_file = "output/result.pkl"
  ```

- **Error Handling**: Use specific exception types and provide helpful error messages:
  ```python
  if not input_path.exists():
      raise FileNotFoundError(f"Input file not found: {input_path}")
  ```

- **Constants**: Define module-level constants in UPPER_CASE:
  ```python
  DEFAULT_DPI = 300
  MAX_PAGE_SIZE = 10000
  ```

- **Docstrings**: Use Google-style docstrings for all public functions and classes:
  ```python
  def convert_document(path: Path, dpi: int = 300) -> Dict[str, Any]:
      """Convert a LaTeX document to structured output.
      
      Args:
          path: Path to the input document
          dpi: Resolution for rendering (default: 300)
          
      Returns:
          Dictionary containing converted document data
          
      Raises:
          FileNotFoundError: If the input file doesn't exist
          ValueError: If DPI is not positive
      """
  ```

- Try to keep merge requests (MRs) as concise as possible:
  - Avoid committing commented-out code.
  - Wherever possible, each PR should address a single concern. If there are several otherwise-unrelated things that should be fixed to reach a desired endpoint, our recommendation is to open several PRs and indicate the dependencies in the description. The more complex the changes are in a single PR, the more time it will take to review those changes.

- Write commit titles using imperative mood and [these rules](https://chris.beams.io/posts/git-commit/), and reference the Issue number corresponding to the MR. Following is the recommended format for commit texts:
```
#<Issue Number> - <Commit Title>

<Commit Body>
```

- Ensure that all linting checks pass and there are no errors or warnings:
  ```bash
  just check
  ```

- Ensure that all tests pass prior to submitting your code:
  ```bash
  just nvtexlive-test
  ```

- All OSS components must contain accompanying documentation (docstrings and READMEs) describing the functionality, dependencies, and known issues.

  - Use Google-style docstrings for all functions, classes, and modules
  - See existing modules in `src/nvtexpy/` for reference





- All new Python files must include the appropriate license header:
  ```python
  # SPDX-License-Identifier: Apache-2.0
  # Copyright (c) 2025, NVIDIA CORPORATION.
  ```
  
  The `just fix` command will automatically add or fix license headers.

- Make sure that you can contribute your work to open source (no license and/or patent conflict is introduced by your code). You will need to [`sign`](#signing-your-work) your commit.

- Thanks in advance for your patience as we review your contributions; we do appreciate them!


#### Pull Requests
Developer workflow for code contributions is as follows:

1. Developers must first [fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the [upstream](https://github.com/NVIDIA/nvtexpy) NVTexPy repository.

2. Git clone the forked repository and push changes to the personal fork.

  ```bash
git clone https://github.com/YOUR_USERNAME/YOUR_FORK.git nvtexpy
# Checkout the targeted branch and commit changes
# Push the commits to a branch on the fork (remote).
git push -u origin <local-branch>:<remote-branch>
  ```

3. Once the code changes are staged on the fork and ready for review, a [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) (PR) can be [created](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) to merge the changes from a branch of the fork into a selected branch of upstream.
  * Exercise caution when selecting the source and target branches for the PR.
    Note that versioned releases of NVTexPy are posted to `release/` branches of the upstream repo.
  * Creation of a PR kicks off the code review process.
  * At least one NVTexPy maintainer will be assigned for the review.
  * While under review, mark your PRs as work-in-progress by using GitHub's draft pull request feature.

4. The PR will be accepted and the corresponding issue closed after:
   - All tests pass (`just nvtexlive-test`)
   - Linting checks pass (`just check`)
   - Code style is properly formatted (`just fix` has been run)
   - Code review is approved by maintainers
   - Documentation is updated if needed


#### Signing Your Work

* We require that all contributors "sign-off" on their commits. This certifies that the contribution is your original work, or you have rights to submit it under the same license, or a compatible license.

  * Any contribution which contains commits that are not Signed-Off will not be accepted.

* To sign off on a commit you simply use the `--signoff` (or `-s`) option when committing your changes:
  ```bash
  $ git commit -s -m "Add cool feature."
  ```
  This will append the following to your commit message:
  ```
  Signed-off-by: Your Name <your@email.com>
  ```

* Full text of the DCO:

  ```
    Developer Certificate of Origin
    Version 1.1
    
    Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
    1 Letterman Drive
    Suite D4700
    San Francisco, CA, 94129
    
    Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.
  ```

  ```
    Developer's Certificate of Origin 1.1
    
    By making a contribution to this project, I certify that:
    
    (a) The contribution was created in whole or in part by me and I have the right to submit it under the open source license indicated in the file; or
    
    (b) The contribution is based upon previous work that, to the best of my knowledge, is covered under an appropriate open source license and I have the right under that license to submit that work with modifications, whether created in whole or in part by me, under the same open source license (unless I am permitted to submit under a different license), as indicated in the file; or
    
    (c) The contribution was provided directly to me by some other person who certified (a), (b) or (c) and I have not modified it.
    
    (d) I understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information I submit with it, including my sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.
  ```