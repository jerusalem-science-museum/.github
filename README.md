# .github Repository

This is the organization's **meta repository** that manages organization-wide configurations, documentation, and automation.

## What This Repo Does

### 🏠 Organization Profile
The `profile/README.md` file is automatically displayed on the organization's GitHub landing page. It contains an auto-generated index of all repositories, organized by category.

### 🔄 Automated Repository Index - Every Monday morning
A GitHub Actions workflow runs weekly (and on push) to:
1. Fetch all repositories in the organization via GitHub API
2. Categorize them by prefix (e.g., `ftc-*`, `space-*`) and compare to [list of categories](https://github.com/jerusalem-science-museum/.github/blob/main/scripts/exhibit_names.json)
3. Generate a collapsible, searchable index in `profile/README.md`

## Manually update index
You can manually run the index update from the Actions tab → "Update Repository Index" → "Run workflow".

### Required Secrets
- `GH_TOKEN`: A GitHub token with `repo` scope to read organization repositories

