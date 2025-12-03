#!/bin/bash
#
# Monorepo Splitter Script
# Extracts exhibit folders into separate repositories with full Git history
#
# Usage:
#   bash split_monorepo.sh --help
#   bash split_monorepo.sh --dry-run
#   bash split_monorepo.sh --execute
#
# Requirements:
#   - git-filter-repo: pip install git-filter-repo
#   - jq: brew/apt install jq
#   - GitHub CLI: gh auth login
#   - split_plan.csv in same directory
#

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAN_FILE="${SCRIPT_DIR}/split_plan.csv"
TEMP_DIR="/tmp/monorepo_split_$$"
LOG_FILE="${SCRIPT_DIR}/split_log.txt"
DRY_RUN=false
EXECUTE=false

print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

print_info() {
    echo -e "${YELLOW}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
}

print_usage() {
    cat << EOF
Usage: bash split_monorepo.sh [OPTIONS]

OPTIONS:
    --help          Show this help message
    --dry-run       Parse and validate plan without making changes
    --execute       Actually create repos and push to GitHub

REQUIREMENTS:
    - split_plan.csv in same directory with columns:
      old_path,new_repo_name,description,owner
    - git-filter-repo installed (pip install git-filter-repo)
    - GitHub CLI installed and authenticated (gh auth login)
    - GITHUB_ORGANIZATION environment variable set

EXAMPLE:
    export GITHUB_ORGANIZATION="my-org"
    bash split_monorepo.sh --dry-run
    bash split_monorepo.sh --execute

EOF
    exit 0
}

validate_setup() {
    print_header "Validating Setup"
    
    # Check plan file
    if [[ ! -f "$PLAN_FILE" ]]; then
        print_error "Plan file not found: $PLAN_FILE"
        print_info "Create split_plan.csv with columns: old_path,new_repo_name,description,owner"
        exit 1
    fi
    print_success "Plan file found: $PLAN_FILE"
    
    # Check required tools
    if ! command -v git-filter-repo &> /dev/null; then
        print_error "git-filter-repo not found"
        print_info "Install with: pip install git-filter-repo"
        exit 1
    fi
    print_success "git-filter-repo installed"
    
    if ! command -v jq &> /dev/null; then
        print_error "jq not found"
        print_info "Install with: brew install jq (macOS) or apt install jq (Linux)"
        exit 1
    fi
    print_success "jq installed"
    
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) not found"
        print_info "Install from https://github.com/cli/cli"
        exit 1
    fi
    print_success "GitHub CLI installed"
    
    # Check authentication
    if ! gh auth status &> /dev/null; then
        print_error "Not authenticated with GitHub"
        print_info "Run: gh auth login"
        exit 1
    fi
    print_success "GitHub authentication OK"
    
    # Check organization
    if [[ -z "$GITHUB_ORGANIZATION" ]]; then
        print_error "GITHUB_ORGANIZATION not set"
        print_info "Export it: export GITHUB_ORGANIZATION='your-org'"
        exit 1
    fi
    print_success "GitHub organization: $GITHUB_ORGANIZATION"
    
    echo ""
}

parse_plan() {
    print_header "Parsing Split Plan"
    
    # Skip header line and parse
    local count=0
    while IFS=',' read -r old_path new_repo description owner; do
        # Skip header and empty lines
        [[ "$old_path" == "old_path" ]] && continue
        [[ -z "$old_path" ]] && continue
        
        # Trim whitespace
        old_path=$(echo "$old_path" | xargs)
        new_repo=$(echo "$new_repo" | xargs)
        description=$(echo "$description" | xargs)
        owner=$(echo "$owner" | xargs)
        
        print_info "[$((++count))] $old_path → $new_repo"
        echo "    Description: $description"
        echo "    Owner: $owner"
    done < "$PLAN_FILE"
    
    echo ""
}

split_repo() {
    local old_path="$1"
    local new_repo="$2"
    local description="$3"
    local monorepo_path="$4"
    
    print_info "Splitting: $old_path"
    
    # Create temp workspace
    local work_dir="${TEMP_DIR}/${new_repo}"
    mkdir -p "$work_dir"
    
    # Clone monorepo to temp location
    print_info "  Cloning monorepo to temp..."
    git clone --quiet "$monorepo_path" "$work_dir"
    
    cd "$work_dir"
    
    # Use git-filter-repo to extract subdirectory
    print_info "  Extracting $old_path with git-filter-repo..."
    git-filter-repo \
        --subdirectory-filter "$old_path" \
        --force \
        2>&1 | grep -v "Rewriting" | head -5 || true
    
    # Create new repo on GitHub
    print_info "  Creating repository on GitHub: $new_repo"
    if gh repo create "$new_repo" \
        --public \
        --description "$description" \
        --source=. \
        --remote=origin \
        --push \
        2>&1 | grep -q "created remotely"; then
        print_success "  Repository created and pushed"
    else
        print_info "  Repository may already exist, attempting push"
        git remote set-url origin "https://github.com/${GITHUB_ORGANIZATION}/${new_repo}.git"
        git push -u origin main 2>&1 | tail -3 || true
    fi
    
    cd - > /dev/null
}

execute_split() {
    print_header "Executing Repository Splits"
    
    # Prompt for monorepo path
    read -p "Enter path to monorepo (absolute or relative): " monorepo_input
    
    if [[ ! -d "$monorepo_input" ]]; then
        print_error "Path not found: $monorepo_input"
        exit 1
    fi
    
    local monorepo_path=$(cd "$monorepo_input" && pwd)
    print_success "Using monorepo: $monorepo_path"
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    print_info "Working directory: $TEMP_DIR"
    
    # Process each line in plan
    local line_num=0
    while IFS=',' read -r old_path new_repo description owner; do
        # Skip header and empty lines
        [[ "$old_path" == "old_path" ]] && continue
        [[ -z "$old_path" ]] && continue
        
        # Trim whitespace
        old_path=$(echo "$old_path" | xargs)
        new_repo=$(echo "$new_repo" | xargs)
        description=$(echo "$description" | xargs)
        owner=$(echo "$owner" | xargs)
        
        print_info ""
        print_info "Processing [$((++line_num))]:"
        split_repo "$old_path" "$new_repo" "$description" "$monorepo_path"
        
    done < "$PLAN_FILE"
    
    # Cleanup
    print_info "Cleaning up temporary directory..."
    rm -rf "$TEMP_DIR"
    
    echo ""
    print_success "All repositories split and pushed!"
    print_info "Update your org-directory index by running:"
    echo "  export GITHUB_TOKEN='...'"
    echo "  export ORG_NAME='$GITHUB_ORGANIZATION'"
    echo "  python generate_index.py"
    echo ""
}

# Parse arguments
case "${1:-}" in
    --help)
        print_usage
        ;;
    --dry-run)
        DRY_RUN=true
        ;;
    --execute)
        EXECUTE=true
        ;;
    *)
        if [[ -n "$1" ]]; then
            print_error "Unknown option: $1"
            print_usage
        fi
        ;;
esac

# Main execution
validate_setup
parse_plan

if [[ "$EXECUTE" == true ]]; then
    read -p "Are you sure? This will create new repositories on GitHub. (y/N) " confirm
    if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
        execute_split
    else
        print_info "Aborted"
    fi
elif [[ "$DRY_RUN" == true ]]; then
    print_header "Dry Run Complete"
    print_info "Plan validated. Run with --execute to proceed."
else
    print_info "Showing plan only. Use --dry-run or --execute"
fi
