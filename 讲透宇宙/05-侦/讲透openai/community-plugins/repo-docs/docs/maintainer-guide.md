# Maintainer guide

CDE maintainers steward this public plugin collection, review contributions,
and triage issues and security reports. Support is best effort. Admission to
OpenAI's official Plugins Directory requires a separate review.

## Contribution and merge controls

- External contributors submit pull requests from forks and receive no direct
  write access. Grant write access only to verified OpenAI full-time employees
  responsible for maintaining this repository.
- Keep `CODEOWNERS` assigned to the responsible CDE maintainers. Protect the
  default branch with required pull requests and code-owner review, dismiss
  stale approvals after new changes, and require approval of the latest push
  by someone other than its author.
- Require the applicable OpenAI CLA, test, and security checks before merge.
  Verify the CLA integration and branch rules are configured and that each
  required check runs for relevant pull requests. A documented requirement or
  missing check is not active enforcement; hold merges until the controls are
  configured and verified, except for the reviewed one-time CLA bootstrap
  [described below](#ci-and-cla-configuration). Keep external contribution
  merges blocked throughout that bootstrap.
- Apply the [review checklist](review-and-publish.md) to code, skills, setup,
  dependencies, file access, off-machine data flows, and secrets. Protect
  `CODEOWNERS`, workflows, and this policy with the same review requirements.
- Enable GitHub private vulnerability reporting and verify the
  [reporting link](../SECURITY.md) works. Keep vulnerability details private
  during triage and remediation.

## CI and CLA configuration

Run PR tests only on GitHub-hosted runners with read-only tokens, no repository
secrets or internal-network access, and checkout credentials disabled. Require
maintainer approval for every external fork's workflow run. Pin third-party
Actions to full commit SHAs and enforce that setting at the repository level.
PR-generated artifacts are untrusted build candidates and must not feed a
privileged release or deployment job.

The CLA Assistant is a separate privileged metadata-only workflow. It must
never check out or execute contributor code. It uses the built-in GitHub token
to check primary commit authors and record their own signature comments in
`signatures/cla.json` on the `cla-signatures` branch. It does not verify
`Co-authored-by` attribution: maintainers must verify those contributors and
third-party submissions separately. Do not add human signature exemptions.

To bootstrap CLA enforcement:

1. Publish the approved [project CLA](../CLA.md) and reviewed CLA workflow on
   `main`. GitHub reads `pull_request_target` workflows from the base branch,
   so the PR that first introduces this workflow cannot run that new check.
   Hold external contribution merges during this bootstrap.
2. Initialize `cla-signatures` with `signatures/cla.json` containing
   `{"signedContributors":[]}`. This creates no signatures. Never populate
   agreements on someone else's behalf.
3. Confirm the `cla` check runs on a new or reopened PR and fails for an
   unsigned contributor. Require `cla`, from GitHub Actions, in branch
   protection alongside the test and dependency checks before accepting
   external contributions. A maintainer's review cannot replace a signature.

When reviewing workflow changes, verify that the required `cla` result comes
from `.github/workflows/cla.yml`; another job with the same name is not a CLA
verification.

Keep GitHub secret scanning, push protection, private vulnerability reporting,
and Dependabot alerts enabled. Require `Dependency review` on PRs; it covers
GitHub-recognized dependency manifests, so bundled source and binaries still
need the [plugin review checklist](review-and-publish.md). Weekly dependency
updates do not replace review of the resulting PRs.

## Transfer and access review

The current installation source is `tonyloehr/community-plugins`. A transfer
must follow the required approvals and an agreed receiving-owner procedure.
This guide does not assert that transfer or release approval is complete.

Immediately after a transfer to the OpenAI organization:

1. Remove **all outside collaborators**, including accounts with read-only
   access. They can continue contributing through forks of the public repo.
2. Audit effective access through direct grants, every team and parent team,
   organization base permissions, and privileged organization roles. Confirm
   every person with write, maintain, or admin access is a verified OpenAI
   full-time employee. Verify identity and employment through the organization's
   authoritative process; a `-oai` username or profile email alone is insufficient.
3. Remove unnecessary grants and resolve inherited access with organization
   owners. Keep the verification evidence in the appropriate private access
   review record, without publishing employee or identity details here.
4. Recheck branch rules, code-owner resolution, CLA integration, required test
   and security checks, and private vulnerability reporting at the destination.
   Review installed applications and automation permissions as well.
5. Update installation and reporting URLs only after confirming the destination
   repository and redirects work. Verify installation from a fresh checkout.

Repeat the access review when maintainers, team membership, or organization
permissions change. Keep merge and access controls enforced as the catalog
grows.
