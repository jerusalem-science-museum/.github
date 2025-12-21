#!/usr/bin/env python3
"""
Museum Sync - Sync all git repositories 1-2 folders deep from current directory.
Pulls, commits, and pushes changes.
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
        # Use list() to avoid repeated iteration overhead
        items = list(base_path.iterdir())
        for item in items:
            # Quick check: is it a directory?
            if not item.is_dir():
                continue
            
            # Skip if in skip list
            if item.name in skip_dirs:
                continue
            
            # Quick check: does .git exist? (just check if it's a file/dir, don't stat)
            git_dir = item / ".git"
            try:
                if git_dir.exists():
                    repos.append(str(item))
                    # Don't search inside git repos - skip recursion
                    continue
            except (OSError, PermissionError):
                # Skip if we can't access
                continue
            
            # Check depth 2 (subdirectories of subdirectories)
            if depth < max_depth:
                repos.extend(find_git_repos(item, depth + 1, max_depth))
    except (PermissionError, OSError):
        # Skip directories we can't access
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


def has_commits(repo_path):
    """Check if repository has at least one commit."""
    returncode, _, _ = run_git_command(repo_path, ["git", "rev-parse", "--verify", "HEAD"])
    return returncode == 0


def needs_pull(repo_path):
    """Check if repository needs to pull from remote."""
    # Check if remote exists
    returncode, _, _ = run_git_command(repo_path, ["git", "remote", "get-url", "origin"])
    if returncode != 0:
        return False
    
    # Check if behind remote (without fetching - use existing remote tracking info)
    # This is faster and works if the remote tracking branch exists
    returncode, stdout, _ = run_git_command(repo_path, ["git", "status", "-sb"])
    if returncode == 0 and "behind" in stdout:
        return True
    
    return False


def needs_commit(repo_path):
    """Check if repository has uncommitted changes (tracked or untracked)."""
    # Check for uncommitted changes to tracked files
    returncode, _, _ = run_git_command(repo_path, ["git", "diff", "--quiet", "HEAD", "--"])
    if returncode != 0:
        return True
    
    # Check for untracked files and staged changes
    returncode, stdout, _ = run_git_command(repo_path, ["git", "status", "--porcelain"])
    if returncode == 0 and stdout.strip():
        return True
    
    return False


def needs_push(repo_path):
    """Check if repository has unpushed commits."""
    returncode, stdout, _ = run_git_command(repo_path, ["git", "status", "-sb"])
    if returncode == 0 and "ahead" in stdout:
        return True
    return False


def main():
    # Get commit message
    commit_message = input("Enter commit message for all repos: ").strip()
    if not commit_message:
        print("Commit message cannot be empty.")
        sys.exit(1)
    
    # Find all git repos 1-2 folders deep from current directory
    base_dir = os.getcwd()
    print("Searching for git repositories...", end="", flush=True)
    start_time = time.time()
    repos = find_git_repos(base_dir)
    elapsed = time.time() - start_time
    print(f" found {len(repos)} in {elapsed:.2f}s")
    
    if not repos:
        print(f"No git repositories found 1-2 folders deep from: {base_dir}")
        print("Make sure you're running this from a directory that contains git repos in subdirectories.")
        input("Press Enter to exit")
        sys.exit(0)
    
    print(f"Found {len(repos)} git repository/repositories to process.\n")
    
    committed = []
    pushed = []
    pulled = []
    
    for repo_path in repos:
        repo_name = os.path.basename(repo_path)
        
        # Check if it's actually a git repo
        if not (Path(repo_path) / ".git").exists():
            print(f"Skipping {repo_name} - .git directory not found")
            continue
        
        # Check what needs to be done
        needs_commit_flag = needs_commit(repo_path)
        needs_push_flag = needs_push(repo_path)
        needs_pull_flag = needs_pull(repo_path)
        
        if not (needs_pull_flag or needs_commit_flag or needs_push_flag):
            continue
        
        print("=" * 50)
        print(f"Repo: {repo_name}")
        print(f"Path: {repo_path}")
        print("=" * 50)
        
        # Show status
        returncode, stdout, _ = run_git_command(repo_path, ["git", "status", "-sb"])
        if returncode == 0:
            print(stdout)
        
        # Pull first if needed
        if needs_pull_flag:
            print("Pulling from remote...")
            # Fetch first to update remote tracking info, then pull
            run_git_command(repo_path, ["git", "fetch", "origin"], capture_output=False)
            returncode, stdout, stderr = run_git_command(repo_path, ["git", "pull", "origin", "HEAD"], capture_output=False)
            if returncode == 0:
                pulled.append(repo_name)
            else:
                print(f"Pull failed for {repo_name} (merge conflict or other error).")
                if stderr:
                    print(stderr)
        
        # Commit if needed
        if needs_commit_flag:
            print("Adding and committing...")
            # Add all changes (tracked and untracked)
            run_git_command(repo_path, ["git", "add", "-A"], capture_output=False)
            
            returncode, _, stderr = run_git_command(repo_path, ["git", "commit", "-m", commit_message])
            if returncode == 0:
                committed.append(repo_name)
            else:
                print(f"Commit failed (nothing to commit or error).")
                if stderr:
                    print(stderr)
        elif needs_push_flag:
            print("No new changes to commit, but branch is ahead of remote. Will push.")
        
        # Push if we committed something or branch was already ahead
        if needs_commit_flag or needs_push_flag:
            print("Pushing...")
            returncode, _, stderr = run_git_command(repo_path, ["git", "push", "--set-upstream", "origin", "HEAD"], capture_output=False)
            if returncode == 0:
                pushed.append(repo_name)
            else:
                print(f"Push failed for {repo_name} (no remote/upstream or other error).")
                if stderr:
                    print(stderr)
        
        print()
    
    # Summary
    print("=" * 50)
    print("Summary")
    print("=" * 50)
    
    if pulled:
        print("Pulled from remote in repos:")
        print("  " + ", ".join(pulled))
    else:
        print("No repos needed to pull from remote.")
    
    if committed:
        print("Committed in repos:")
        print("  " + ", ".join(committed))
    else:
        print("No repos had changes to commit.")
    
    if pushed:
        print("Pushed successfully for:")
        print("  " + ", ".join(pushed))
    else:
        print("No pushes were performed.")
    
    print()
    input("Press Enter to exit")


if __name__ == "__main__":
    main()

