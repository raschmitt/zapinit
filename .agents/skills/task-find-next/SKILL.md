---
name: find-next-task
description: Identifies the next available task in docs/tasks.md. Triggers when asked to find, pick, or determine the next task to work on. Does NOT trigger for implementing or coding tasks.
---

Find the next available task in `docs/tasks.md` by running the script below and returning its JSON output.

```bash
python3 .agents/skills/task-find-next/scripts/find_next_task.py
```

## How availability is determined

A task header looks like one of these:

```
### T-04 · WhatsApp redirect          ← available
### ~~T-01 · Project scaffold~~        ← done (crossed out)
```

A task is **unavailable** if either:
- Its header is crossed out with `~~` (already done)
- An open PR exists whose title contains `(T-XX):` matching that task ID (e.g. `feat(T-04): add redirect`)

Return the `id` and `name` fields from the script output to the caller.
