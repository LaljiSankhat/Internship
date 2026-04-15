---
name: file_management
description: "Read, write, search, and organize files in the workspace."
required_tools:
  - read_file
  - write_file
  - append_file
  - list_dir
  - exec
examples:
  - "show me the project structure"
  - "create a new config file"
  - "find all TODO comments in the codebase"
---

# File Management Skill

Use the built-in file tools to interact with the project filesystem.

## Reading files
Use `read_file` with a relative path. You can optionally pass `start_line` and `end_line`.

## Writing files
Use `write_file` — parent directories are created automatically.

## Listing directories
Use `list_dir` to explore the project. Omit `path` to list the workspace root.

## Searching
Use `exec` with grep:
```bash
grep -rn "TODO" --include="*.py" .
```

## Best practices
- Always read a file before overwriting it so you don't lose content.
- When editing a file, read the full content, modify the relevant section, and write back.
- Use `append_file` when you only need to add content to the end.
