<!-- source: DeepWiki mcp.deepwiki.com · repo coderabbitai/skills · extra page GitHub Primitives (github.md) · fetched 2026-10-27 -->

# GitHub Primitives (github.md)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/autofix/SKILL.md](skills/autofix/SKILL.md)
- [skills/autofix/github.md](skills/autofix/github.md)

</details>



## Purpose and Scope

This document specifies the technical implementation of the GitHub workflow primitives defined in `skills/autofix/github.md` and mirrored in `skills/autofix/SKILL.md`. The module acts as a reusable helper for skills requiring thread-aware CodeRabbit pull request feedback rather than flat PR summaries [skills/autofix/github.md:1-5](). It details GitHub CLI (`gh`) commands, GraphQL pagination logic for review threads, bot author validation, progress check heuristics, and PR comment posting routines.

Sources: [skills/autofix/github.md:1-6](), [skills/autofix/SKILL.md:28-37]()

---

## 1. Prerequisites and Repository Context Resolution

Before executing any review-thread queries or mutations, the environment requires proper authentication via the GitHub CLI (`gh`) and an active association between the current local branch and a remote GitHub pull request [skills/autofix/github.md:7-11]().

### PR and Repository Resolution
The runtime resolves the active pull request number by inspecting the current branch name against open pull requests. If no pull request exists, the pipeline optionally initializes one using the latest commit metadata [skills/autofix/github.md:12-30]().

```bash
pr_number=$(gh pr list --head "$(git branch --show-current)" --state open --json number --jq '.[0].number')

if [ -z "$pr_number" ] || [ "$pr_number" = "null" ]; then
  # Fallback: create PR if requested
  title=$(git log -1 --pretty=format:'%s')
  body=$(git log -1 --pretty=format:'%b')
  gh pr create --title "$title" --body "${body:-Auto-created by CodeRabbit autofix}"
fi
```

Repository coordinates (`owner` and `repo`) are subsequently fetched via the GitHub CLI API bindings [skills/autofix/github.md:32-37]()：

```bash
owner=$(gh repo view --json owner --jq '.owner.login')
repo=$(gh repo view --json name --jq '.name')
```

Sources: [skills/autofix/github.md:7-37](), [skills/autofix/SKILL.md:38-88]()

---

## 2. Thread-Aware GraphQL Pagination and Filtering

To capture granular feedback rather than top-level summaries, the system queries the GitHub GraphQL API using cursor-based pagination over `reviewThreads` [skills/autofix/github.md:39-90]().

### GraphQL Query Structure
The query requests pull request review threads in pages of 100 nodes, retrieving resolution status, outdated flags, and root comment metadata (`databaseId`, `body`, `path`, `line`, `startLine`, `originalLine`, and `author.login`) [skills/autofix/github.md:53-80]().

```mermaid
graph TD
    UserQuery[""NaturalLanguage:FetchReviewThreads""] --> GhCliCmd[""gh api graphql query($owner:String!, $repo:String!, $pr:Int!, $cursor:String)""]
    GhCliCmd --> RepoNode[""repository(owner:$owner, name:$repo)""]
    RepoNode --> PrNode[""pullRequest(number:$pr)""]
    PrNode --> ThreadNode[""reviewThreads(first:100, after:$cursor)""]
    ThreadNode --> PageInfo[""pageInfo { hasNextPage endCursor }""]
    ThreadNode --> CommentsNode[""nodes { isResolved isOutdated comments(first:1) { nodes { databaseId body path line startLine originalLine author { login } } } }""]

    Sources: [skills/autofix/github.md:39-90](), [skills/autofix/SKILL.md:99-148]()
```

### Filtering and Validation Rules
Retrieved threads are filtered in memory using `jq` to ensure only actionable CodeRabbit feedback is processed [skills/autofix/github.md:91-99]()：
- **Author Verification**: The root comment author must match `coderabbitai`, `coderabbit[bot]`, or `coderabbitai[bot]` [skills/autofix/github.md:94]().
- **Resolution State**: `isResolved` must be `false` [skills/autofix/github.md:95]().
- **Freshness**: `isOutdated` must be `false` [skills/autofix/github.md:96]().

Additionally, the pipeline inspects top-level PR comments and reviews to detect CodeRabbit processing states, such as the "Come back again in a few minutes" message [skills/autofix/github.md:100-115]().

Sources: [skills/autofix/github.md:39-115](), [skills/autofix/SKILL.md:90-178]()

---

## 3. Summary Comment Posting and Reaction Logic

Upon successful application of patches, the autofix workflow posts a consolidation summary back to the active pull request and optionally reacts to the primary review comment [skills/autofix/github.md:117-145]().

### Comment Posting Routine
The summary comment aggregates file counts, modified paths, commit hashes, and target branch names derived entirely from local execution state [skills/autofix/github.md:117-142]()：

```mermaid
graph TD
    LocalState[""NaturalLanguage:LocalExecutionState""] --> BuildComment[""gh pr comment $pr_number --body SummaryTemplate""]
    BuildComment --> FileList[""FilesModifiedList:path/to/file-a.ts""]
    BuildComment --> CommitSha[""CommitHashReference:commit-sha""]
    BuildComment --> PostAction[""GitHubAPI:IssueCommentMutation""]
    PostAction --> ReactionStep[""OptionalReaction:ThumbsUpReactionOnCodeRabbitRoot""]

    Sources: [skills/autofix/github.md:117-145](), [skills/autofix/SKILL.md:179-196]()
```

If no modifications occur during the run, the success template is skipped or replaced with a neutral notification to prevent false artifact publication [skills/autofix/github.md:141-142]().

Sources: [skills/autofix/github.md:117-145]()

---

