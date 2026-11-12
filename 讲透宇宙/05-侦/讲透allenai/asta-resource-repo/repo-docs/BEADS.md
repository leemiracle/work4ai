# Beads Task Tracking Guide

This project uses [Beads](https://github.com/steveyegge/beads), a distributed issue tracker designed for AI coding agents, to manage project tasks and roadmap.

## What is Beads?

Beads provides a persistent, structured memory for coding agents by maintaining task relationships and dependencies in a Git-backed JSONL format. Tasks are stored in the `.beads/` directory and version-controlled like source code.

## Quick Start

### Viewing Work

```bash
# View all ready work (unblocked tasks)
bd ready

# List all open issues
bd list

# List by status
bd list --status open
bd list --status closed

# List by priority (0=highest, 4=lowest)
bd list --priority 0

# Show full details of an issue
bd show <issue-id>
```

### Creating Issues

```bash
# Create a new task
bd create "Task title" -d "Description" -p 1 -t feature

# Create an epic for grouping related tasks
bd create "Epic title" -d "Description" -p 0 -t epic
```

### Managing Dependencies

```bash
# Add dependency (child depends on parent)
bd dep add <child-id> <parent-id> -t parent-child

# View dependency tree
bd dep tree <issue-id>

# Check for circular dependencies
bd dep cycles
```

### Updating Issues

```bash
# Update status
bd update <issue-id> --status in_progress
bd update <issue-id> --status open

# Update priority
bd update <issue-id> --priority 0

# Close an issue
bd close <issue-id> --reason "Completed in PR #123"
```

## Project Structure

The project is organized into three main phases:

### Phase 1: Core Infrastructure (P0)
- Epic: `asta-resource-repo-khu`
- Status: Mostly complete (12/13 tasks completed)
- Remaining: Authentication and authorization

### Phase 2: Enhanced Features (P1)
- Epic: `asta-resource-repo-tz8`
- Status: Not started
- Includes: Document parsing (PDF, DOCX, XLSX), OCR, vector embeddings, advanced permissions

### Phase 3: Production Ready (P2)
- Epic: `asta-resource-repo-0ff`
- Status: Not started
- Includes: OAuth 2.1, cloud storage backends, monitoring, scaling

## Common Workflows

### Finding Next Work

```bash
# Show all ready work ordered by priority
bd ready

# Show only P0 ready work
bd list --status open --priority 0
```

### Working on a Task

```bash
# 1. Find and claim a task from ready work
bd ready

# 2. Update status to in_progress
bd update <issue-id> --status in_progress

# 3. Do the work...

# 4. Close when complete
bd close <issue-id> --reason "Implemented in <files>"
```

### Creating Related Tasks

```bash
# Create a new task discovered during work
bd create "New task found during implementation" -p 1

# Link it to the current task
bd dep add <new-task-id> <current-task-id> -t discovered-from
```

## Beads vs Progress.md

Previously, the project used `instructions/Progress.md` and `instructions/Roadmap.md` for tracking progress. These files have been migrated to Beads:

- **Progress.md**: Tracked completion status → Now reflected in Beads task status (open/closed)
- **Roadmap.md**: Defined phases and features → Now structured as epics and tasks with dependencies

**Benefits of Beads:**
- Git-backed versioning of tasks
- Dependency-aware task management
- Better for AI agents to discover and claim work
- Supports cross-branch task tracking
- Structured query capabilities

## Integration with Claude Code

When working with Claude Code, tasks are automatically discoverable:

1. Claude can query `bd ready` to find unblocked work
2. Claude creates new tasks when discovering additional work needed
3. Dependencies prevent duplicate effort across sessions
4. Task history provides context for future work

## Database Location

Beads stores data in:
- **SQLite Database**: `.beads/beads.db` (primary storage)
- **JSONL Export**: `.beads/issues.jsonl` (Git-backed sync)

The system auto-syncs between SQLite and JSONL:
- After CRUD operations → exports to JSONL
- After `git pull` → imports from JSONL if newer

## Issue Naming Convention

Issues in this project use the prefix: `asta-resource-repo-<hash>`

Example: `asta-resource-repo-khu`, `asta-resource-repo-tx1`

## Advanced Features

### Filtering and Search

```bash
# Find issues by type
bd list --type epic
bd list --type feature

# Combine filters
bd list --status open --priority 0 --type feature
```

### Dependency Types

- `blocks`: Task B must complete before task A
- `parent-child`: Epic/subtask hierarchical relationship
- `discovered-from`: Auto-created when AI discovers related work
- `related`: Soft connection, doesn't block progress

### Git Integration

Beads automatically syncs with Git:
```bash
# After making changes, commit the JSONL file
git add .beads/issues.jsonl
git commit -m "Update task status"

# After pulling, Beads auto-imports newer changes
git pull
```

## Troubleshooting

### Check Beads health
```bash
bd doctor
bd doctor --fix
```

### View sync status
```bash
bd status
```

### Force re-sync
```bash
# Export DB to JSONL
bd export

# Import JSONL to DB
bd import
```

## Reference

- **Beads GitHub**: https://github.com/steveyegge/beads
- **Beads Documentation**: https://github.com/steveyegge/beads/tree/main/docs
- **Issue Prefix**: `asta-resource-repo`
- **Database Path**: `.beads/beads.db`
