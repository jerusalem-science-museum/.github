# Best Practices for Organization Repository Structure

This document outlines recommended standards for organizing code, documentation, and assets across the organization's GitHub repositories.

---

## Naming Conventions

### Repository Names

Use kebab-case (lowercase, hyphens) with optional prefixes for clarity:

```
{category}-{project-name}
{category}-{project-name}-{component}
```

**Prefixes (optional but recommended):**
- `exhibits-` : Exhibition displays and interactive projects
- `tools-` : Utility software and scripts
- `libs-` : Shared libraries and packages
- `infra-` : Infrastructure and deployment
- `research-` : Research and experimental projects

**Examples:**
- `exhibits-robots-control`
- `exhibits-astronomy-display`
- `tools-batch-processor`
- `libs-sensor-interface`
- `infra-github-automation`

### Branch Names

```
main           # Production/stable code
develop        # Integration branch
feature/*      # New features (feature/add-calibration)
fix/*          # Bug fixes (fix/motor-timeout)
docs/*         # Documentation updates
refactor/*     # Code refactoring
```

### Issue Labels

Standardize across organization:
- `bug` - Something not working
- `enhancement` - New feature request
- `documentation` - Needs docs
- `good-first-issue` - Beginner-friendly
- `help-wanted` - Extra attention needed
- `wontfix` - Won't be fixed
- `status: in-progress`
- `priority: high / medium / low`

---

## Repository Metadata

### Required Files

Every repository should include:

```
.gitignore          # Exclude unnecessary files
.gitattributes      # Configure Git LFS
README.md           # Project overview
LICENSE             # License information
```

### Recommended Files

```
CONTRIBUTING.md     # Contributing guidelines
CHANGELOG.md        # Version history
docs/               # Additional documentation
tests/              # Test suite
```

### GitHub Settings

For each repository:

1. **Description:** Concise one-liner explaining purpose
2. **Topics:** Tags for discoverability (e.g., "robotics", "exhibits", "python")
3. **Visibility:** Public (unless sensitive data)
4. **Template:** Use project template if available

Example topics: `robotics`, `exhibits`, `python`, `microcontroller`, `real-time`

---

## Folder Organization

### Standard Structure

```
project/
├── src/                    # Source code
│   ├── main.py            # Entry point
│   ├── module_a.py        # Feature modules
│   └── utils/             # Utilities
├── hardware/              # Hardware-specific files
│   ├── datasheets/        # PDFs (Git LFS)
│   ├── schematics/        # Circuit diagrams
│   └── mechanical/        # CAD models (Git LFS)
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # System design
│   ├── SETUP.md          # Installation/setup
│   ├── API.md            # API reference
│   └── assets/           # Images, diagrams
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── scripts/               # Utility/automation scripts
├── config/               # Configuration templates
├── requirements.txt      # Python dependencies
├── package.json         # Node.js dependencies (if JS)
├── .gitignore           # Git ignore rules
├── .gitattributes       # Git LFS configuration
├── README.md            # Overview and quick start
├── CONTRIBUTING.md      # Contributing guide
├── LICENSE              # License file
└── CHANGELOG.md         # Version history
```

### When to Add Subdirectories

- **Yes:** If folder will contain 5+ items or represents distinct concern
- **No:** If it's just one or two related files
- **Maybe:** If you're uncertain, start flat and refactor later

---

## Git Large File Storage (LFS)

### What to Track with LFS

```gitattributes
# Hardware documentation
*.pdf filter=lfs diff=lfs merge=lfs -text
*.dwg filter=lfs diff=lfs merge=lfs -text

# 3D Models
*.stl filter=lfs diff=lfs merge=lfs -text
*.step filter=lfs diff=lfs merge=lfs -text
*.stp filter=lfs diff=lfs merge=lfs -text

# Archives
*.zip filter=lfs diff=lfs merge=lfs -text
*.tar.gz filter=lfs diff=lfs merge=lfs -text
*.7z filter=lfs diff=lfs merge=lfs -text

# Large images
*.psd filter=lfs diff=lfs merge=lfs -text

# Binaries (optional)
*.bin filter=lfs diff=lfs merge=lfs -text
*.hex filter=lfs diff=lfs merge=lfs -text
```

### Setup Per Repository

```bash
# Install LFS (one-time on machine)
git lfs install

# Configure repository
git lfs track "*.pdf" "*.stl" "*.step" "*.zip"
git add .gitattributes
git commit -m "Configure Git LFS"
git push
```

### Do NOT track with LFS

- Source code files
- Configuration files
- Build artifacts (should be in .gitignore)
- Generated documentation
- Log files

---

## Documentation Standards

### README.md Structure

```markdown
# Project Name

**Status | Owner | Last Updated**

## Overview
What the project does and why

## Quick Start
Minimal setup to get running

## Hardware Setup (if applicable)
BOM, datasheets, assembly

## Software Setup
Installation and configuration

## Architecture
System design and components

## Usage
How to use the project

## Contributing
How to contribute changes

## License
License information

## References
Links to related docs, issues, etc.
```

See `README_PROJECT.md` template for complete example.

### Inline Code Comments

```python
# Good: explains WHY
# We use exponential backoff because API has rate limits
retry_delay = 2 ** attempt

# Poor: explains WHAT (obvious from code)
# Add 2 to the variable
x = x + 2
```

### Docstrings

```python
def motor_control(speed: int, direction: str) -> bool:
    """
    Control motor speed and direction.
    
    Args:
        speed (int): PWM value 0-255
        direction (str): "forward" or "reverse"
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        ValueError: If speed out of range or direction invalid
    """
```

---

## Code Quality

### Python Specifics

```bash
# Style guide: PEP 8
# Linting: pylint, flake8
# Formatting: black
# Type checking: mypy

# Example lint commands
black src/
pylint src/
mypy src/
pytest tests/
```

### Commit Messages

```
feat: add motor calibration routine
fix: resolve timeout in sensor reading
docs: update hardware assembly guide
refactor: simplify control loop
test: add edge case tests for calibration

Format:
{type}: {description}

Types: feat, fix, docs, refactor, test, perf, chore
```

### Pull Requests

- Clear title: "Add PWM control to motor driver"
- Description: What and why
- Link related issues: "Closes #42"
- Add reviewers before merging
- Require 1+ approval before merge

---

## Asset Organization

### Images and Media

```
docs/assets/
├── diagrams/        # Circuit diagrams, flowcharts
├── photos/          # Assembly photos, exhibits
├── screenshots/     # UI screenshots, data viz
└── plots/           # Graphs, analysis results
```

Use Git LFS for large image files (>5MB).

### Hardware Documentation

```
hardware/
├── datasheets/      # Component spec sheets (PDF, LFS)
├── schematics/      # Circuit diagrams (PDF, LFS)
├── mechanical/      # 3D models, CAD (STEP/STL, LFS)
├── assembly/        # Assembly instructions, photos
└── bom.csv          # Bill of materials
```

---

## Maintenance & Archival

### Status Labels

Add to repository description or use labels:
- **Active:** Actively developed, stable
- **Maintenance:** No new features, bug fixes only
- **Dormant:** Not actively developed, but maintained if needed
- **Archived:** No longer developed, read-only

### Archiving Process

1. Create final release tag: `v1.0.0-final`
2. Archive repository in GitHub settings
3. Add "ARCHIVED" to repo description
4. Update index with archived status

### When to Archive

- Project complete and stable
- Project deprecated in favor of newer version
- Project no longer fits organization needs

---

## Security & Privacy

### Never commit to repo:

- API keys, tokens, secrets
- Passwords or credentials
- Private customer data
- Sensitive hardware specifications
- Proprietary algorithms (if applicable)

### Use instead:

- Environment variables (`.env.example` template)
- GitHub Secrets (for CI/CD)
- Encrypted configs (if necessary)
- `.gitignore` for local configs

---

## Tools & Automation

### Recommended Tools

- **Version Control:** Git + GitHub
- **CI/CD:** GitHub Actions
- **Code Quality:** GitHub's built-in checks
- **Package Management:** pip (Python), npm (Node)
- **Documentation:** GitHub markdown + GitHub Pages (optional)

### GitHub Actions Templates

Available in `.github/workflows/`:
- `tests.yml` - Run tests on push
- `lint.yml` - Check code style
- `update-index.yml` - Update central index

---

## Checklist for New Repositories

- [ ] Repository named with appropriate prefix
- [ ] README.md with setup and overview
- [ ] .gitignore for language/environment
- [ ] .gitattributes for LFS (if needed)
- [ ] LICENSE file
- [ ] GitHub description and topics set
- [ ] CONTRIBUTING.md (optional but recommended)
- [ ] Initial folder structure created
- [ ] First commit message clear and descriptive
- [ ] Added to organization index (will auto-update)

---

## References & Links

- [Git Best Practices](https://github.com)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Choose a License](https://choosealicense.com/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
