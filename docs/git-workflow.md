# Git Workflow

Recommended branches:

- `main` — stable production code
- `develop` — integrated development work
- `feature/*` — new features (e.g., `feature/authentication`)
- `fix/*` — bug fixes
- `docs/*` — documentation updates

Rules and conventions:

- Create feature branches from `develop`.
- Keep `main` protected and deployable.
- Use pull requests to merge into `develop` and `main`.
- Use descriptive branch names and short PR titles.

Example branch commands:

```bash
# create develop branch locally (if safe)
git checkout -b develop
git push -u origin develop

# create a feature branch
git checkout develop
git checkout -b feature/golfer-profile
```

Notes:

- Do not create or delete branches that would overwrite uncommitted work.
- If the repository already has a `develop` branch, preserve its history.
