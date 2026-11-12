<!--  Thanks for sending a pull request!  Here are some tips for you:

1) If this is your first time, please read our contributor guidelines: CONTRIBUTING.md and docs/plugin-spec.md

2) The PR quality gate (.github/workflows/pr-quality.yml) runs automatically:
   structure check + L0/L1 validation + catalog consistency + secret scan + unit tests.
   Local equivalent: python scripts/pr_check.py
-->

**What type of PR is this?**
<!--
Choose one label from `bug`, `task`, `feature` and `refactor`, and replace `<label>` below the comment block.
-->
/kind <label>

---

**What does this PR do / why do we need it**:

---

**Which issue(s) this PR fixes**:
<!--
*Automatically closes linked issue when PR is merged.
Usage: `Fixes #<issue number>`, or `Fixes (paste link of issue)`.
-->
Fixes #

---

**Test Plan and test result**:
<!--
Describe what was tested and the verification results. At minimum, paste the
local gate output: python scripts/pr_check.py
When tools/ or rails/ are touched, also run in a jiuwenswarm runtime and paste
the RESULT line: python scripts/validate.py --only <name> --require-hot-load
-->

---

**Self-checklist** (**Please self-check by marking [x]; we will review your completion status, otherwise the PR cannot be merged**):

+ - [ ] `python scripts/pr_check.py` passes locally (RESULT: PASS)
+ - [ ] If `tools/` or `rails/` executable code is touched, section 1 of [docs/review-checklist.md](../docs/review-checklist.md) has been completed (mark N/A otherwise)
+ - [ ] `manifest.version` bumped (only when an existing plugin package content changed)
+ - [ ] `python scripts/catalog.py` re-run and the generated catalog committed
+ - [ ] No development-only files inside `plugins/<name>/` (tests/scripts/docs belong in `tests/plugins/<name>/`)
+ - [ ] Plugin id not renamed and not conflicting with existing plugins
