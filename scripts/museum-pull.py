#!/usr/bin/env python3
"""
Museum Pull - Pull latest changes from all git repositories 1-2 folders deep.
Simple and fast - just updates all repos.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def find_git_repos(base_dir, depth=1, max_depth=2):
    """Find all git repositories 1-2 folders deep from base_dir."""
    repos = []
    base_path = Path(base_dir)
    
    if not base_path.exists():
        return repos
    
    # Skip common directories that are unlikely to be repos
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", ".env"}
    
    # Check depth 1 (direct subdirectories)
    try:
        items = list(base_path.iterdir())
        for item in items:
            if not item.is_dir():
                continue
            
            if item.name in skip_dirs:
                continue
            
            git_dir = item / ".git"
            try:
                if git_dir.exists():
                    repos.append(str(item))
                    continue
            except (OSError, PermissionError):
                continue
            
            # Check depth 2 (subdirectories of subdirectories)
            if depth < max_depth:
                repos.extend(find_git_repos(item, depth + 1, max_depth))
    except (PermissionError, OSError):
        pass
    
    return repos


def run_git_command(repo_path, command, capture_output=True):
    """Run a git command in the specified repository."""
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def has_remote(repo_path):
    """Check if repository has a remote origin."""
    returncode, _, _ = run_git_command(repo_path, ["git", "remote", "get-url", "origin"])
    return returncode == 0


def main():
    # Find all git repos 1-2 folders deep from current directory
    base_dir = os.getcwd()
    print("Searching for git repositories...", end="", flush=True)
    start_time = time.time()
    repos = find_git_repos(base_dir)
    elapsed = time.time() - start_time
    print(f" found {len(repos)} in {elapsed:.2f}s\n")
    
    if not repos:
        print(f"No git repositories found 1-2 folders deep from: {base_dir}")
        print("Make sure you're running this from a directory that contains git repos in subdirectories.")
        input("Press Enter to exit")
        sys.exit(0)
    
    pulled = []
    skipped = []
    failed = []
    
    for repo_path in repos:
        repo_name = os.path.basename(repo_path)
        
        # Check if it's actually a git repo
        if not (Path(repo_path) / ".git").exists():
            skipped.append(repo_name)
            continue
        
        # Check if it has a remote
        if not has_remote(repo_path):
            skipped.append(f"{repo_name} (no remote)")
            continue
        
        print(f"Pulling {repo_name}...", end="", flush=True)
        
        # Fetch first, then pull
        returncode, _, stderr = run_git_command(repo_path, ["git", "fetch", "origin"], capture_output=False)
        if returncode != 0:
            print(f" (fetch failed)")
            failed.append(f"{repo_name} (fetch failed)")
            continue
        
        returncode, stdout, stderr = run_git_command(repo_path, ["git", "pull", "origin", "HEAD"], capture_output=False)
        if returncode == 0:
            print(" ✓")
            pulled.append(repo_name)
        else:
            print(f" (failed)")
            failed.append(f"{repo_name} (pull failed)")
            if stderr:
                print(f"  Error: {stderr.strip()}")
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    
    if pulled:
        print(f"Successfully pulled {len(pulled)} repos:")
        for repo in pulled:
            print(f"  ✓ {repo}")
    
    if skipped:
        print(f"\nSkipped {len(skipped)} repos:")
        for repo in skipped:
            print(f"  - {repo}")
    
    if failed:
        print(f"\nFailed {len(failed)} repos:")
        for repo in failed:
            print(f"  ✗ {repo}")
    
    if not pulled and not failed and not skipped:
        print("No repos to process.")
    
    print()
    input("Press Enter to exit")


if __name__ == "__main__":
    main()

