# Translation Workflow

## Overview

Each chapter is translated in its own git worktree on a feature branch. This allows parallel work without conflicts.

```
charles-blanchard/           ← main branch (manager works here)
../charles-blanchard-ch02/   ← worktree: translate/ch02 branch
../charles-blanchard-ch03/   ← worktree: translate/ch03 branch
```

## Manager Role (Main Branch)

You work here. You:
1. Create worktrees for chapters to translate
2. Spawn workers in those worktrees
3. Review translations
4. Merge completed branches to main
5. Update `translation_status.yaml`

## Worker Role (Worktree)

The translator subagent:
1. Reads the French chapter from `chapters/`
2. Writes English translation to `translations/`
3. Commits its work
4. Returns to manager

## Commands

### Start a chapter translation

```bash
# Create branch and worktree
git worktree add ../charles-blanchard-ch02 -b translate/ch02

# Then spawn worker in that directory
```

### Check worktrees

```bash
git worktree list
```

### After review - merge to main

```bash
git merge translate/ch02
git worktree remove ../charles-blanchard-ch02
git branch -d translate/ch02
```

### If translation needs revision

Just spawn another worker in the same worktree - it still has the branch.

## File Locations

| What | Where |
|------|-------|
| French source | `chapters/*.txt` (never modified) |
| English output | `translations/*.txt` |
| Progress | `translation_status.yaml` (main branch) |
| Style guide | `TRANSLATION_GUIDE.md` |

## Typical Session

```
Manager: "Create worktree for chapter 2"
         git worktree add ../charles-blanchard-ch02 -b translate/ch02

Manager: "Use translator agent in ../charles-blanchard-ch02 to translate
         chapters/02_chapter_1_the_cold.txt"

[Worker runs, writes translation, commits]

Manager: "Read ../charles-blanchard-ch02/translations/02_chapter_1_the_cold.txt"
         [Reviews translation]

Manager: "Merge translate/ch02"
         git merge translate/ch02

Manager: "Update translation_status.yaml - mark ch02 as done"
```
