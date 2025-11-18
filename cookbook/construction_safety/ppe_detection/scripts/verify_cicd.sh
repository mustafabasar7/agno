#!/bin/bash
# CI/CD Pipeline Verification Script
# This script verifies that all CI/CD components are properly installed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counter for checks
PASSED=0
FAILED=0

# Function to print section header
print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2 - Missing: $1"
        ((FAILED++))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2 - Missing: $1"
        ((FAILED++))
        return 1
    fi
}

# Function to check command exists
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2 ($(which $1))"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $2 - Command not found: $1"
        ((FAILED++))
        return 1
    fi
}

# Function to check Python package
check_python_package() {
    if python -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python package: $1"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Python package not found: $1"
        ((FAILED++))
        return 1
    fi
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         CI/CD Pipeline Verification Script            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "Project directory: ${BLUE}$PROJECT_DIR${NC}"

# Check GitHub Actions Workflows
print_section "1. GitHub Actions Workflows"
check_dir ".github" "GitHub directory"
check_dir ".github/workflows" "Workflows directory"
check_file ".github/workflows/ci.yml" "CI workflow"
check_file ".github/workflows/cd.yml" "CD workflow"
check_file ".github/workflows/release.yml" "Release workflow"
check_file ".github/workflows/security-scan.yml" "Security scan workflow"

# Check GitHub Templates
print_section "2. GitHub Templates"
check_dir ".github/ISSUE_TEMPLATE" "Issue templates directory"
check_file ".github/ISSUE_TEMPLATE/bug_report.md" "Bug report template"
check_file ".github/ISSUE_TEMPLATE/feature_request.md" "Feature request template"
check_file ".github/PULL_REQUEST_TEMPLATE.md" "Pull request template"

# Check Configuration Files
print_section "3. Configuration Files"
check_file ".pre-commit-config.yaml" "Pre-commit configuration"
check_file ".secrets.baseline" "Secrets baseline"
check_file "pyproject.toml" "Python project configuration"
check_file "Makefile" "Makefile"

# Check Documentation
print_section "4. Documentation Files"
check_file "README.md" "README"
check_file "SETUP.md" "Setup guide"
check_file "CONTRIBUTING.md" "Contributing guide"
check_file "CHANGELOG.md" "Changelog"
check_file "CICD_INSTALL.md" "CI/CD installation guide"
check_file "docs/CICD_SETUP.md" "Detailed CI/CD setup guide"
check_file ".github/workflows/README.md" "Workflows documentation"

# Check Required Tools
print_section "5. Required Tools"
check_command "python" "Python"
check_command "pip" "pip"
check_command "git" "Git"
check_command "docker" "Docker"
check_command "docker-compose" "Docker Compose"
check_command "make" "Make"

# Check Optional Tools
print_section "6. Optional Tools (Recommended)"
check_command "gh" "GitHub CLI" || echo -e "   ${YELLOW}Install: https://cli.github.com/${NC}"
check_command "pre-commit" "Pre-commit" || echo -e "   ${YELLOW}Run: pip install pre-commit${NC}"

# Check Python Version
print_section "7. Python Environment"
PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
echo -e "Python version: ${BLUE}$PYTHON_VERSION${NC}"
if [[ "$PYTHON_VERSION" == 3.10* ]] || [[ "$PYTHON_VERSION" == 3.11* ]]; then
    echo -e "${GREEN}✓${NC} Python version is compatible (3.10 or 3.11)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Python version should be 3.10 or 3.11 (current: $PYTHON_VERSION)"
    ((FAILED++))
fi

# Check Python Packages
print_section "8. Python Development Packages"
check_python_package "black" || echo -e "   ${YELLOW}Run: pip install black${NC}"
check_python_package "ruff" || echo -e "   ${YELLOW}Run: pip install ruff${NC}"
check_python_package "mypy" || echo -e "   ${YELLOW}Run: pip install mypy${NC}"
check_python_package "pytest" || echo -e "   ${YELLOW}Run: pip install pytest${NC}"
check_python_package "pytest_cov" || echo -e "   ${YELLOW}Run: pip install pytest-cov${NC}"

# Check Makefile targets
print_section "9. Makefile Targets"
if grep -q "^install-dev:" Makefile 2>/dev/null; then
    echo -e "${GREEN}✓${NC} install-dev target exists"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} install-dev target missing"
    ((FAILED++))
fi

if grep -q "^install-hooks:" Makefile 2>/dev/null; then
    echo -e "${GREEN}✓${NC} install-hooks target exists"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} install-hooks target missing"
    ((FAILED++))
fi

if grep -q "^ci-full:" Makefile 2>/dev/null; then
    echo -e "${GREEN}✓${NC} ci-full target exists"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} ci-full target missing"
    ((FAILED++))
fi

# Check Git repository
print_section "10. Git Repository"
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Git repository initialized"
    ((PASSED++))

    # Check for remote
    if git remote -v | grep -q "origin"; then
        echo -e "${GREEN}✓${NC} Git remote 'origin' configured"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Git remote 'origin' not configured"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Not a Git repository"
    ((FAILED++))
fi

# Summary
print_section "Verification Summary"
TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

echo ""
echo -e "Total checks:  ${BLUE}$TOTAL${NC}"
echo -e "Passed:        ${GREEN}$PASSED${NC}"
echo -e "Failed:        ${RED}$FAILED${NC}"
echo -e "Success rate:  ${BLUE}$PERCENTAGE%${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ All checks passed! CI/CD pipeline is ready!        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. Run: ${YELLOW}make install-dev${NC}"
    echo -e "  2. Run: ${YELLOW}make install-hooks${NC}"
    echo -e "  3. Run: ${YELLOW}make ci-full${NC}"
    echo -e "  4. Review: ${YELLOW}SETUP.md${NC}"
    echo ""
    exit 0
else
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠ Some checks failed. Review the output above.       ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}To fix missing components:${NC}"
    echo -e "  • Missing files: Check CICD_INSTALL.md"
    echo -e "  • Missing tools: Install recommended tools"
    echo -e "  • Python packages: Run ${YELLOW}make install-dev${NC}"
    echo ""
    exit 1
fi
