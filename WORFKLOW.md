# Git Workflow: Merge Commit + Fast-Forward

## Merging a feature branch into `main`

1. On GitHub, merge the PR using **Create a merge commit**
2. Locally, switch to the merged branch and fast-forward:

```bash
git checkout <branch-name>
git merge main
git push --force-with-lease
```

Now `<branch-name>` is even with `main` and ready for future work.

## Why this workflow

- Merge commits preserve branch topology in the history
- Fast-forward keeps the feature branch from falling behind
- No need for rebasing or rewriting history
