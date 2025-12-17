# Create GitHub repos from local folders
# Requires: gh CLI (GitHub CLI) authenticated with your org

param(
    [string]$SourceDir = "C:\Users\arieg\Documents\Projects\Science Museum Code\nathan\Museum_of_Science\sorted",
    [string]$OrgName = "jerusalem-science-museum",
    [switch]$DryRun = $false
)

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is not installed. Install from https://cli.github.com/"
    exit 1
}

# Get all folders (each folder = one repo)
$folders = Get-ChildItem -Path $SourceDir -Directory

Write-Host "Found $($folders.Count) folders to create as repos" -ForegroundColor Cyan
Write-Host ""

foreach ($folder in $folders) {
    $repoName = $folder.Name
    $folderPath = $folder.FullName
    
    Write-Host "Processing: $repoName" -ForegroundColor Yellow
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would create repo: $OrgName/$repoName" -ForegroundColor Gray
        continue
    }
    
    # Check if repo already exists on GitHub
    $exists = gh repo view "$OrgName/$repoName" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Repo already exists on GitHub, skipping" -ForegroundColor DarkYellow
        continue
    }
    
    # Check if this folder has its own .git (not inherited from parent)
    $hasOwnGit = Test-Path (Join-Path $folderPath ".git")
    
    # Check if already has origin remote (only if it has its own .git)
    $originUrl = $null
    if ($hasOwnGit) {
        $originUrl = git -C "$folderPath" remote get-url origin 2>$null
    }
    if ($hasOwnGit -and $originUrl) {
        # Has origin - check if remote repo actually exists
        $fetchResult = git -C "$folderPath" fetch origin 2>&1
        if ($LASTEXITCODE -ne 0) {
            # Remote doesn't exist or not accessible - remove stale origin and create fresh
            Write-Host "  Origin remote set but repo doesn't exist, recreating..." -ForegroundColor Cyan
            git -C "$folderPath" remote remove origin
            # Fall through to create repo
        } else {
            # Remote exists - check if in sync
            $localHead = git -C "$folderPath" rev-parse HEAD 2>$null
            $remoteHead = git -C "$folderPath" rev-parse origin/master 2>$null
            if ($LASTEXITCODE -ne 0) {
                $remoteHead = git -C "$folderPath" rev-parse origin/main 2>$null
            }
            
            if ($localHead -and $remoteHead -and $localHead -eq $remoteHead) {
                Write-Host "  Already pushed and in sync, skipping" -ForegroundColor DarkYellow
                continue
            } else {
                Write-Host "  Origin exists but not in sync, pushing..." -ForegroundColor Cyan
                git -C "$folderPath" push -u origin HEAD
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  Pushed!" -ForegroundColor Green
                }
                continue
            }
        }
    }
    
    # Initialize git if needed
    if (-not (Test-Path (Join-Path $folderPath ".git"))) {
        Write-Host "  Initializing git..." -ForegroundColor Gray
        git -C "$folderPath" init
    }
    
    # Stage and commit if there are changes
    git -C "$folderPath" add .
    $status = git -C "$folderPath" status --porcelain
    if ($status) {
        git -C "$folderPath" commit -m "Initial commit"
    }
    
    # Check if there are any commits
    $hasCommits = git -C "$folderPath" rev-parse HEAD 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  No files to commit, skipping" -ForegroundColor DarkYellow
        continue
    }
    
    # Create the repo and push
    Write-Host "  Creating repo..." -ForegroundColor Cyan
    gh repo create "$OrgName/$repoName" --public --source="$folderPath" --push
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Done!" -ForegroundColor Green
    } else {
        Write-Host "  Failed to create repo" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "Finished!" -ForegroundColor Green

