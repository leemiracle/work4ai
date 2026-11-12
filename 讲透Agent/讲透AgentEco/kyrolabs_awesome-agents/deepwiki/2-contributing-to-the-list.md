<!-- source: DeepWiki mcp.deepwiki.com · repo kyrolabs/awesome-agents · page 2 Contributing to the List · fetched 2026-10-27 -->

# Contributing to the List

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)

</details>



This page documents the rules and mechanics for submitting a new entry to the `awesome-agents` curated list. It covers what projects are eligible, how to open a Pull Request via the GitHub browser editor, and what occurs during maintainer review. For an overview of the list's contents and categories, see [Overview](#1).

---

## Eligibility Criteria

All submissions are governed by `CONTRIBUTING.md` and are curated by the repository maintainers. A project must pass every criterion before it will be merged.

### Required Criteria

| Criterion | Description |
|---|---|
| **Open source** | The project repository must be publicly accessible and use an open-source license. |
| **English** | Documentation and README must be in English. |
| **Agentic relevance** | The project must be related to the AI agent / agentic framework ecosystem. |
| **Maintained** | The project must still be actively maintained. |
| **Online** | The project's links and hosted resources must be live. |
| **Added value** | The project must offer something not already covered by existing list entries. |
| **Demonstrated traction** | New projects with no evident community usage (history) are excluded. |

Sources: [CONTRIBUTING.md:3-13](), [CONTRIBUTING.md:19-19]()

### Placement Rule

New entries must be added at the **bottom of the relevant category section** in `README.md`, not inserted anywhere else in the list.

Sources: [CONTRIBUTING.md:15-15]()

---

## Submission Workflow

The only accepted submission mechanism is a GitHub Pull Request. Issues are not processed for new entries and will not result in additions to the list [CONTRIBUTING.md:17-17]().

**Workflow overview:**

```mermaid
flowchart TD
    C["Contributor"]
    step1["1. Navigate to\nhttps://github.com/kyrolabs/awesome-agents"]
    step2["2. Open README.md\nin the repository"]
    step3["3. Click the Edit icon\n(pencil icon, top-right of file view)"]
    step4["4. Edit README.md\nin the GitHub in-browser editor\n(GitHub Flavored Markdown)"]
    step5["5. Write a summary\nof why the entry is being proposed"]
    step6["6. Click Propose file change\n(creates a fork + branch automatically)"]
    step7["7. Submit Pull Request\nvia GitHub PR interface"]
    R["Maintainer Review\n(kyrolabs)"]

    C --> step1 --> step2 --> step3 --> step4 --> step5 --> step6 --> step7 --> R
```

Sources: [CONTRIBUTING.md:27-32]()

### Step-by-Step Details

1. **Navigate** to the repository at `https://github.com/kyrolabs/awesome-agents` [CONTRIBUTING.md:27-27]().
2. **Open `README.md`** — this is the file that constitutes the curated list [CONTRIBUTING.md:28-28]().
3. **Click the edit icon** (pencil) in the top-right corner of the file view [CONTRIBUTING.md:29-29]().
4. **Make your edit** in the in-browser editor using GitHub Flavored Markdown [CONTRIBUTING.md:30-30](). All entries follow a standard format. Place your entry at the **bottom** of the appropriate category section [CONTRIBUTING.md:15-15]().
5. **Scroll to the bottom** of the editor and write a description of your proposed change in the "Propose file change" box [CONTRIBUTING.md:31-31]().
6. **Click "Propose file change"** — GitHub will fork the repository under your account and create a branch with your edit [CONTRIBUTING.md:31-31]().
7. **Submit the Pull Request** on the resulting "Open a pull request" page [CONTRIBUTING.md:32-32]().

Sources: [CONTRIBUTING.md:15-32]()

---

## Entry Format Reference

The following diagram maps the physical structure of a list entry in `README.md` to the components that maintainers check during review.

```mermaid
graph LR
    ENTRY["README.md list entry"]
    NAME["Tool name\n(linked to GitHub repo)"]
    DESC["One-line description\n(English, concise)"]
    STARS["GitHub stars badge\n(img.shields.io social)"]
    CATEGORY["Category section\n(e.g. Frameworks, Research,\nSoftware Development)"]
    PLACEMENT["Bottom of category\n(per CONTRIBUTING.md rule)"]

    ENTRY --> NAME
    ENTRY --> DESC
    ENTRY --> STARS
    ENTRY --> CATEGORY
    ENTRY --> PLACEMENT
```

Sources: [CONTRIBUTING.md:15-15](), [CONTRIBUTING.md:3-13]()

---

## Maintainer Review

Once a Pull Request is submitted, a maintainer from `kyrolabs` evaluates it against the criteria in `CONTRIBUTING.md`. There are three possible outcomes:

```mermaid
flowchart TD
    PR["Pull Request Submitted"]
    CHECK{"Does it meet\nall criteria?"}
    CLOSE["PR Auto-Closed\nNo action required\nfrom contributor"]
    REVISE["Changes Requested\n(spelling, guideline mismatch,\nplacement error)"]
    UPDATE["Contributor updates\nthe PR branch"]
    MERGE["PR Merged\nEntry appears in README.md"]

    PR --> CHECK
    CHECK -- "Fails any criterion\n(not open source, no traction,\nnot English, etc.)" --> CLOSE
    CHECK -- "Minor issues only" --> REVISE
    REVISE --> UPDATE --> CHECK
    CHECK -- "Passes all criteria" --> MERGE
```

Sources: [CONTRIBUTING.md:17-19](), [CONTRIBUTING.md:34-36]()

### Automatic Closure and Revision Requests

Any PR that does not follow the guidelines will be **automatically closed** [CONTRIBUTING.md:17-17](). Non-negotiable criteria that trigger immediate closure include brand new repositories with no history, brand new GitHub users, or incorrect placement in the list [CONTRIBUTING.md:19-19]().

If a maintainer requests changes — typically for spelling errors or guideline mismatches — the contributor must amend the existing PR branch rather than opening a new PR [CONTRIBUTING.md:34-36]().

| Issue | Cause |
|---|---|
| **Wrong placement** | Entry was not added at the bottom of the category [CONTRIBUTING.md:19-19](). |
| **Spelling / formatting** | Markdown formatting incorrect or description contains errors [CONTRIBUTING.md:36-36](). |
| **Guideline mismatch** | Entry violates one of the exclusion rules (e.g., unmaintained repo) [CONTRIBUTING.md:17-17](). |
| **No Traction** | Brand new repo with no history [CONTRIBUTING.md:19-19](). |

Sources: [CONTRIBUTING.md:17-19](), [CONTRIBUTING.md:34-36]()

---

## Relationship Between Governance and Artifacts

The following diagram maps the governance flow between the policy document and the resulting list.

```mermaid
graph TD
    CONTRIB_FILE["CONTRIBUTING.md\n(policy document)"]
    README_FILE["README.md\n(the curated list artifact)"]

    CURATION_POLICY["Curation policy\n(open source, English, traction,\nadded value, maintained)"]
    WORKFLOW_STEPS["Step-by-step PR workflow\n(edit README.md via browser editor)"]
    EXCLUSION_LIST["Exclusion rules\n(new repo, non-English, unmaintained,\nnot open source, not agentic)"]
    PLACEMENT_RULE["Placement rule\n(bottom of category)"]

    SECTIONS["Category sections\n(Frameworks, Testing, Software Development,\nResearch, Conversational, Game, Knowledge, Automation)"]
    ENTRIES["Individual tool entries\n(name + description + stars badge)"]

    CONTRIB_FILE --> CURATION_POLICY
    CONTRIB_FILE --> WORKFLOW_STEPS
    CONTRIB_FILE --> EXCLUSION_LIST
    CONTRIB_FILE --> PLACEMENT_RULE

    PLACEMENT_RULE -- "governs edits to" --> README_FILE
    WORKFLOW_STEPS -- "describes how to edit" --> README_FILE

    README_FILE --> SECTIONS
    SECTIONS --> ENTRIES
```

Sources: [CONTRIBUTING.md:1-36]()

---

