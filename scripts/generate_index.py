#!/usr/bin/env python3
"""
GitHub Repository Inventory Generator

Generates a comprehensive index of all repositories in an organization.
Creates both JSON (for processing) and Markdown table (for display).

Usage:
    export GITHUB_TOKEN="your_token"
    export ORG_NAME="your_organization"
    python generate_index.py

Output:
    - repos_inventory.json (structured data)
    - repos_table.md (markdown table for README)
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict

def get_organization_repos(org_name: str, token: str) -> List[Dict]:
    """
    Fetch all repositories from a GitHub organization.
    Handles pagination automatically.
    """
    repos = []
    page = 1
    per_page = 100
    
    print(f"[*] Fetching repositories for organization '{org_name}'...")
    
    while True:
        url = f"https://api.github.com/orgs/{org_name}/repos"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {
            "type": "all",
            "per_page": per_page,
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        page_repos = response.json()
        if not page_repos:
            break
        
        repos.extend(page_repos)
        print(f"    Page {page}: {len(page_repos)} repos")
        page += 1
    
    print(f"[✓] Total: {len(repos)} repositories found\n")
    return repos


def categorize_repo(repo: Dict) -> str:
    """
    Determine repository category based on properties.
    
    Categories:
    - "Active": Last update < 3 months ago
    - "Maintenance": Last update 3-6 months ago
    - "Dormant": Last update > 6 months ago
    - "Archived": GitHub archived flag set
    """
    if repo.get("archived"):
        return "Archived"
    
    updated_at = datetime.fromisoformat(repo["updated_at"].replace("Z", "+00:00"))
    days_since_update = (datetime.now(updated_at.tzinfo) - updated_at).days
    
    if days_since_update < 90:
        return "Active"
    elif days_since_update < 180:
        return "Maintenance"
    else:
        return "Dormant"


def extract_exhibit_name(repo_name: str) -> str:
    """
    Extract exhibit/category name from repo name if using prefix convention.
    
    Examples:
    - exhibits-robots-control → exhibits
    - tools-batch-processor → tools
    - labs-research → labs
    """
    if "-" in repo_name:
        prefix = repo_name.split("-")[0]
        return prefix
    return "uncategorized"


def build_repo_index(repos: List[Dict]) -> Dict:
    """
    Build structured index of repositories.
    """
    index = {
        "generated_at": datetime.now().isoformat(),
        "total_repos": len(repos),
        "by_status": {},
        "by_exhibit": {},
        "repos": []
    }
    
    for repo in repos:
        status = categorize_repo(repo)
        exhibit = extract_exhibit_name(repo["name"])
        
        # Initialize status category
        if status not in index["by_status"]:
            index["by_status"][status] = []
        index["by_status"][status].append(repo["name"])
        
        # Initialize exhibit category
        if exhibit not in index["by_exhibit"]:
            index["by_exhibit"][exhibit] = []
        index["by_exhibit"][exhibit].append(repo["name"])
        
        # Add repo entry
        repo_entry = {
            "name": repo["name"],
            "url": repo["html_url"],
            "description": repo["description"],
            "status": status,
            "exhibit": exhibit,
            "archived": repo["archived"],
            "language": repo["language"],
            "topics": repo.get("topics", []),
            "last_updated": repo["updated_at"],
            "created_at": repo["created_at"],
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "is_fork": repo["fork"],
        }
        index["repos"].append(repo_entry)
    
    # Sort each category
    for status in index["by_status"]:
        index["by_status"][status].sort()
    for exhibit in index["by_exhibit"]:
        index["by_exhibit"][exhibit].sort()
    
    return index


def get_exhibit_display_names() -> Dict[str, str]:
    """
    Load exhibit display name mappings from EXHIBIT_NAMES environment variable.
    Expected format: JSON object like {"ftc": "Freedom To Create", "xyz": "XYZ Project"}
    """
    exhibit_names_json = os.getenv("EXHIBIT_NAMES", "{}")
    try:
        return json.loads(exhibit_names_json)
    except json.JSONDecodeError:
        print("[!] Warning: EXHIBIT_NAMES is not valid JSON, using raw prefixes")
        return {}


def generate_markdown_table(index: Dict) -> str:
    """
    Generate markdown table representation of repositories.
    Groups repos by prefix (first word before hyphen) in collapsible sections.
    """
    exhibit_names = get_exhibit_display_names()
    lines = []
    lines.append("# Organization Repository Index\n")
    lines.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    lines.append(f"**Total Repositories:** {index['total_repos']}\n")
    lines.append("")
    
    # Generate collapsible sections by exhibit/prefix
    for exhibit in sorted(index["by_exhibit"].keys()):
        repos_in_exhibit = [r for r in index["repos"] if r["exhibit"] == exhibit]
        if not repos_in_exhibit:
            continue
        
        display_name = exhibit_names.get(exhibit, exhibit)
        lines.append(f"<details>")
        lines.append(f"  <summary><strong>{display_name}</strong> ({len(repos_in_exhibit)} repos)</summary>\n")
        lines.append("| Repo | Description | Language | Status | Last Updated |")
        lines.append("|------|-------------|----------|--------|--------------|")
        
        for repo in sorted(repos_in_exhibit, key=lambda x: x["name"]):
            repo_link = f"[{repo['name']}]({repo['url']})"
            desc = (repo["description"] or "N/A").replace("|", "\\|")[:60]
            lang = repo["language"] or "N/A"
            status = repo["status"]
            updated = repo["last_updated"][:10]  # YYYY-MM-DD
            
            lines.append(f"| {repo_link} | {desc} | {lang} | {status} | {updated} |")
        
        lines.append("\n</details>\n")
    
    return "\n".join(lines)


def main():
    # Get credentials from environment
    token = os.getenv("GITHUB_TOKEN")
    org_name = os.getenv("ORG_NAME")
    
    if not token:
        print("[!] Error: GITHUB_TOKEN environment variable not set")
        exit(1)
    
    if not org_name:
        print("[!] Error: ORG_NAME environment variable not set")
        exit(1)
    
    # Fetch repos
    repos = get_organization_repos(org_name, token)
    
    # Build index
    print("[*] Building index structure...")
    index = build_repo_index(repos)
    print(f"[✓] Index built\n")
    
    # Save JSON index
    output_json = "repos_inventory.json"
    print(f"[*] Writing JSON index to {output_json}...")
    with open(output_json, "w") as f:
        json.dump(index, f, indent=2)
    print(f"[✓] Saved {output_json}\n")
    
    # Generate markdown table
    print("[*] Generating markdown table...")
    markdown = generate_markdown_table(index)
    output_md = "../profile/README.md"
    with open(output_md, "w") as f:
        f.write(markdown)
    print(f"[✓] Saved {output_md}\n")
    
    # Print summary
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    for status in sorted(index["by_status"].keys()):
        count = len(index["by_status"][status])
        print(f"  {status}: {count} repositories")
    print("=" * 60)


if __name__ == "__main__":
    main()
