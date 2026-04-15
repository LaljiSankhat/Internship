---
name: github
description: "Interact with GitHub repositories — commits, PRs, issues, and branches."
required_tools:
  - exec
examples:
  - "summarize my latest git commits"
  - "create a new branch called feature/auth"
  - "show open pull requests"
---

# GitHub Skill

You can interact with Git and GitHub using the `exec` tool.

## Common operations

### Show recent commits
```bash
git log --oneline -20
```

### Show status
```bash
git status
```

### Create a branch
```bash
git checkout -b <branch-name>
```

### Show open PRs (requires `gh` CLI)
```bash
gh pr list --state open
```

### Create a PR
```bash
gh pr create --title "<title>" --body "<body>"
```

### Show diff of staged changes
```bash
git diff --cached
```

Always confirm destructive operations (push --force, reset --hard) with the user before executing.
