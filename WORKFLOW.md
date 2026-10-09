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

## What happens after the merge

A merge to `main` deploys the website automatically. The **Deploy** workflow asks the updater on the server to build and publish the new version, and waits for the result. A failed deployment shows up as a failed run in GitHub Actions, and the previous version keeps running.

`main` is protected: the pull request needs the required checks to pass before the merge button works. See [`.github/workflows/README.md`](.github/workflows/README.md).

## Why this workflow

- Merge commits preserve branch topology in the history
- Fast-forward keeps the feature branch from falling behind
- No need for rebasing or rewriting history
