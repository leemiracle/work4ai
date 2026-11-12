<!-- source: DeepWiki mcp.deepwiki.com · repo different-ai/openwork · extra page Rollback, Validation and Changelog · fetched 2026-10-26 -->

# Rollback, Validation and Changelog

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/pull_request_template.md](.github/pull_request_template.md)
- [.github/workflows/changelog.yml](.github/workflows/changelog.yml)
- [.github/workflows/revert-fastlane.yml](.github/workflows/revert-fastlane.yml)
- [.github/workflows/update-models.yml](.github/workflows/update-models.yml)
- [.opencode/agents/changelog.md](.opencode/agents/changelog.md)
- [.opencode/skills/open-a-pr/SKILL.md](.opencode/skills/open-a-pr/SKILL.md)
- [changelog/release-tracker-2026-08-31.md](changelog/release-tracker-2026-08-31.md)
- [changelog/release-tracker-2026-09-02.md](changelog/release-tracker-2026-09-02.md)
- [changelog/release-tracker-2026-09-09.md](changelog/release-tracker-2026-09-09.md)
- [changelog/release-tracker-2026-10-03.md](changelog/release-tracker-2026-10-03.md)
- [changelog/release-tracker-2026-10-07.md](changelog/release-tracker-2026-10-07.md)
- [changelog/release-tracker-2026-10-13.md](changelog/release-tracker-2026-10-13.md)
- [changelog/release-tracker-2026-10-20.md](changelog/release-tracker-2026-10-20.md)
- [changelog/release-tracker-2026-10-22.md](changelog/release-tracker-2026-10-22.md)
- [ee/apps/landing/components/soc-type-ii-badge.tsx](ee/apps/landing/components/soc-type-ii-badge.tsx)
- [ee/apps/landing/public/soc-2-type-ii.svg](ee/apps/landing/public/soc-2-type-ii.svg)
- [packages/docs/changelog.mdx](packages/docs/changelog.mdx)
- [scripts/check-changelog-output.mjs](scripts/check-changelog-output.mjs)
- [scripts/ci/verify-clean-revert.mjs](scripts/ci/verify-clean-revert.mjs)
- [scripts/release/collect-release-prs.mjs](scripts/release/collect-release-prs.mjs)
- [scripts/release/release-notes-from-changelog.mjs](scripts/release/release-notes-from-changelog.mjs)

</details>



This page details the operational procedures, validation tools, and automation scripts used for managing OpenWork releases. It covers release rollback mechanisms, `docker-compose` image pin verification, release validation skills, the automated changelog generation workflow backed by AI agents, and the public documentation changelog structure.

## Release Rollback and Compose Pin Checks

The release lifecycle incorporates safeguards to revert faulty deployments and ensure that infrastructure definitions remain reproducible through strict image pinning.

### Rollback Procedures

When a published release or deployment encounters critical regressions, the release management pipeline relies on automated rollback scripts located under `scripts/release/`. The `scripts/release/rollback.mjs` script coordinates the reversion of release tags, cloud artifact pointers, and publishing states.

Sources:
- `scripts/release/rollback.mjs`()

### Compose Pin Checks

To guarantee deployment reproducibility across environments, `docker-compose` configuration files are validated prior to distribution. The script `scripts/release/check-compose-pins.mjs` parses configuration definitions to confirm that all container images reference explicit tag hashes or pinned digests rather than floating tags like `latest`. Complementing this check, `scripts/release/pin-compose-images.mjs` automates the update process for these image digests.

**Compose Pin Verification and Rollback Architecture**
```mermaid
graph TD
    A["checkComposePins()" / "scripts/release/check-compose-pins.mjs"] --> B{"Are all images pinned?"}
    B -- "No" --> C["pinComposeImages()" / "scripts/release/pin-compose-images.mjs"]
    B -- "Yes" --> D["Pass Compose Validation"]
    C --> D
    E["Trigger Rollback" / "scripts/release/rollback.mjs"] --> F["Revert Cloud Artifacts"]
    F --> G["Delete/Revert Release Tags"]

    style A fill:none,stroke:#333,stroke-width:2px
    style C fill:none,stroke:#333,stroke-width:2px
    style E fill:none,stroke:#333,stroke-width:2px
```

Sources:
- `scripts/release/check-compose-pins.mjs`()
- `scripts/release/pin-compose-images.mjs`()
- `scripts/release/rollback.mjs`()

---

## Release Validation

Post-release verification utilizes specialized AI agent skills to execute comprehensive checks against newly cut release tags.

### The `validate-a-release` Skill

Defined in `.opencode/skills/validate-a-release/SKILL.md` (referenced via `.opencode/skills/open-a-pr/SKILL.md`() context), the release validation agent runs automated evaluations covering desktop smoke tests, server API route health, and documentation consistency. The skill systematically compares expected artifact signatures and validates schema contracts before marking a distribution channel as stable.

Sources:
- `.opencode/skills/open-a-pr/SKILL.md`()

---

## Changelog Workflow and Release Trackers

The changelog pipeline is fully automated via GitHub Actions, combining git history analysis, pull request summaries, and AI agent generation to produce structured release artifacts.

### Changelog Automation Workflow

The workflow `.github/workflows/changelog.yml` executes whenever a release is published or manually dispatched via `workflow_dispatch` [.github/workflows/changelog.yml:1-17](). 

**Changelog Automation Pipeline**
```mermaid
graph TD
    A["github.event.release.published" / ".github/workflows/changelog.yml"] --> B["validateTag()" / "steps.guard"]
    B -- "Valid Stable Tag" --> C["checkoutDevBranch()" / "actions/checkout"]
    C --> D{"isAlreadyDocumented()" / "steps.dedupe"}
    D -- "No" --> E["gatherReleaseFacts()" / "scripts/release/collect-release-prs.mjs"]
    E --> F["writeReleaseFacts()" / ".opencode/release-facts/$TAG.md"]
    F --> G["installOpenCodeCli()" / "opencode.ai/install"]
    G --> H["draftChangelogEntries()" / ".opencode/agents/changelog.md"]
    H --> I["updateChangelogMdx()" / "packages/docs/changelog.mdx"]
    H --> J["writeReleaseTracker()" / "changelog/release-tracker-$DATE.md"]
    I --> K["commitAndOpenPullRequest()" / "git commit"]
    J --> K
    D -- "Yes" --> L["Skip Docs Generation"]

    style A fill:none,stroke:#333,stroke-width:2px
    style E fill:none,stroke:#333,stroke-width:2px
    style H fill:none,stroke:#333,stroke-width:2px
    style I fill:none,stroke:#333,stroke-width:2px
```

The workflow operates through the following stages:
1. **Tag Validation**: Verifies that the target `$TAG` matches semantic versioning standards (e.g., `v0.18.13`) [.github/workflows/changelog.yml:40-49]().
2. **Fact Gathering**: Executes `scripts/release/collect-release-prs.mjs` to aggregate commit diffs, insertions/deletions, and pull request descriptions between the current release and its predecessor [changelog.yml:77-131](). These facts are saved to `.opencode/release-facts/$TAG.md`.
3. **Agent Drafting**: Invokes the dedicated changelog generation agent defined in `.opencode/agents/changelog.md` using model configuration parameters `.opencode/agents/changelog.md:1-13]().
4. **Artifact Generation**: Appends entry updates to `packages/docs/changelog.mdx` and creates an internal tracker file under `changelog/` [changelog.md:40-53]().

Sources:
- `.github/workflows/changelog.yml`()
- `scripts/release/collect-release-prs.mjs`()
- `.opencode/agents/changelog.md`()

### Release Trackers

Internal tracker files (such as `changelog/release-tracker-2026-10-03.md`() and `changelog/release-tracker-2026-10-20.md`()) record structured metadata for each release. These files include commit SHAs, UTC timestamps, one-line summaries, full pull request decision tables (Audience, Decision, Reason), and exact line-of-code metrics (`LOC_LINE`) [changelog/release-tracker-2026-10-03.md:1-25]().

Sources:
- `changelog/release-tracker-2026-10-03.md`()
- `changelog/release-tracker-2026-10-20.md`()
- `changelog/release-tracker-2026-10-22.md`()

---

## Documentation Changelog

The public-facing documentation changelog is stored at `packages/docs/changelog.mdx` [packages/docs/changelog.mdx:1-5](). It renders update feeds using Mintlify `<Update>` components annotated with date labels and categorization tags such as `"🚀 New Features"`, `"🐛 Bug Fixes"`, and `"🏗️ Refactoring"` [packages/docs/changelog.mdx:6-17](). Each entry maps compare URLs between release versions to user-centric narrative summaries [packages/docs/changelog.mdx:8-16]().

Sources:
- `packages/docs/changelog.mdx`()

---

