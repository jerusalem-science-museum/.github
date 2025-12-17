# Clone all Jerusalem Science Museum repos organized by category
# Run from the directory where you want to create the category folders

param(
    [string]$TargetDir = ".",
    [string]$OrgName = "jerusalem-science-museum"
)

# Category prefixes and their folder names
# Load from exhibit_names.json (same source as GitHub Actions)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exhibitNamesPath = Join-Path $scriptDir "exhibit_names.json"

if (Test-Path $exhibitNamesPath) {
    $categories = Get-Content $exhibitNamesPath | ConvertFrom-Json -AsHashtable
    Write-Host "Loaded exhibit names from exhibit_names.json" -ForegroundColor Gray
} else {
    Write-Warning "exhibit_names.json not found, using raw prefixes as folder names"
    $categories = @{}
}

# Load the repos inventory
$inventoryPath = Join-Path $scriptDir "repos_inventory.json"

if (-not (Test-Path $inventoryPath)) {
    # Try parent directory
    $inventoryPath = Join-Path (Split-Path -Parent $scriptDir) "repos_inventory.json"
}

if (-not (Test-Path $inventoryPath)) {
    Write-Error "Cannot find repos_inventory.json"
    exit 1
}

$inventory = Get-Content $inventoryPath | ConvertFrom-Json

# Create target directory if needed
if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir | Out-Null
}

Push-Location $TargetDir

foreach ($repo in $inventory.repos) {
    $repoName = $repo.name
    $exhibit = $repo.exhibit
    
    # Skip .github repo
    if ($repoName -eq ".github") {
        continue
    }
    
    # Determine folder name and category folder
    if ($exhibit -eq "uncategorized") {
        $categoryFolder = "Uncategorized"
        $folderName = $repoName
    } else {
        $categoryFolder = if ($categories.ContainsKey($exhibit)) { $categories[$exhibit] } else { $exhibit }
        # Remove prefix from repo name (e.g., "ftc-connect-4-robot" -> "connect-4-robot")
        $prefix = "$exhibit-"
        if ($repoName.StartsWith($prefix)) {
            $folderName = $repoName.Substring($prefix.Length)
        } else {
            $folderName = $repoName
        }
    }
    
    # Create category folder if needed
    if (-not (Test-Path $categoryFolder)) {
        New-Item -ItemType Directory -Path $categoryFolder | Out-Null
        Write-Host "Created folder: $categoryFolder" -ForegroundColor Green
    }
    
    $targetPath = Join-Path $categoryFolder $folderName
    
    if (Test-Path $targetPath) {
        Write-Host "Skipping $repoName (already exists at $targetPath)" -ForegroundColor Yellow
    } else {
        Write-Host "Cloning $repoName -> $targetPath" -ForegroundColor Cyan
        git clone "https://github.com/$OrgName/$repoName.git" $targetPath
    }
}

Pop-Location

Write-Host "`nDone! All repos cloned." -ForegroundColor Green

