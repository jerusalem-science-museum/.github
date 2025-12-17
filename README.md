# .github Repository

This is the organization's **meta repository** that manages organization-wide configurations, documentation, and automation.

## What This Repo Does

### 🏠 Organization Profile
The `profile/README.md` file is automatically displayed on the organization's GitHub landing page. It contains an auto-generated index of all repositories, organized by category.

### 🔄 Automated Repository Index
A GitHub Actions workflow runs weekly (and on push) to:
1. Fetch all repositories in the organization via GitHub API
2. Categorize them by prefix (e.g., `ftc-*`, `space-*`)
3. Generate a collapsible, searchable index in `profile/README.md`

### 📁 Repository Structure

```
.github/
├── profile/
│   └── README.md          # Organization landing page (auto-generated)
├── scripts/
│   ├── generate_index.py  # Index generation script
│   └── repos_inventory.json # JSON export of all repos
├── docs/
│   └── REPO_STRUCTURE.md  # Best practices for new projects
├── templates/
│   └── README_PROJECT.md  # Template for new repo READMEs
└── .github/
    └── workflows/
        └── update-index.yml # Automation workflow
```

## Configuration

### Exhibit Display Names
Category prefixes can be mapped to friendly display names via the **project variable** `EXHIBIT_NAMES` in [GitHub Settings → Secrets and variables → Actions → Variables](https://github.com/jerusalem-science-museum/.github/settings/variables/actions/EXHIBIT_NAMES).

Format (single-line JSON):
```json
{"ftc": "Freedom to Create", "space": "Eitan Stiva Space Exhibition"}
```

### Required Secrets
- `GH_TOKEN`: A GitHub token with `repo` scope to read organization repositories

## Manual Trigger
You can manually run the index update from the Actions tab → "Update Repository Index" → "Run workflow".
