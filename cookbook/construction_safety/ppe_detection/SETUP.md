# CI/CD Pipeline Setup - Quick Guide

This is a quick reference guide for setting up the CI/CD pipeline. For detailed instructions, see [docs/CICD_SETUP.md](./docs/CICD_SETUP.md).

## Quick Setup Checklist

### Local Development

- [ ] Clone repository
- [ ] Install Python 3.10 or 3.11
- [ ] Run `make install-dev`
- [ ] Run `make install-hooks`
- [ ] Create `.env` from `.env.example`
- [ ] Run `make ci-full` to verify setup

### GitHub Repository

#### Required

- [ ] Enable GitHub Actions (Settings → Actions → General)
- [ ] Set workflow permissions to "Read and write"
- [ ] Configure branch protection for `main` branch
- [ ] Add required status checks

#### Optional

- [ ] Add `CODECOV_TOKEN` secret (for coverage reports)
- [ ] Add `PYPI_API_TOKEN` secret (for PyPI publishing)
- [ ] Configure environments (staging, production)
- [ ] Add deployment secrets
- [ ] Enable Dependabot
- [ ] Enable secret scanning
- [ ] Enable CodeQL

### First Commit

```bash
# Make a change
echo "# Test" >> test.md

# Pre-commit will run automatically
git add .
git commit -m "chore: test CI/CD setup"

# Push and verify CI runs
git push origin your-branch
```

## Available Commands

### Development

```bash
make install-dev      # Install dependencies
make install-hooks    # Install pre-commit hooks
make lint            # Run linters
make format          # Format code
make type-check      # Type checking
make ci-test         # Run tests
make security-check  # Security scan
make ci-full         # Run all CI checks
```

### Docker

```bash
make setup           # Setup .env file
make build           # Build images
make start           # Start services
make stop            # Stop services
make logs            # View logs
make test            # Run tests in container
```

### Pre-commit

```bash
pre-commit run --all-files    # Run on all files
pre-commit autoupdate         # Update hooks
pre-commit clean             # Clear cache
```

## Workflows

### CI Workflow

**Triggers**: Push, Pull Request
**Runs**: Lint, test, type check, Docker build
**Required for**: Merging to main

### CD Workflow

**Triggers**: Push to main, Manual
**Steps**: Build → Deploy Staging → Smoke Tests → Manual Approval → Deploy Production
**Environments**: staging, production

### Release Workflow

**Triggers**: Version tags (v*.*.*)
**Steps**: Test → Build → Release → Publish
**Creates**: GitHub release, Docker images, PyPI package

### Security Scan

**Triggers**: Push, PR, Weekly schedule
**Scans**: Dependencies, code, secrets, containers
**Reports**: Uploaded as artifacts

## Creating a Release

```bash
# Ensure main is clean and tested
git checkout main
git pull origin main
make ci-full

# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Monitor release
gh run watch
```

## Common Issues

### Pre-commit fails

```bash
make format          # Auto-fix formatting
pre-commit clean     # Clear cache
```

### Tests fail

```bash
make ci-test        # Run tests locally
pytest tests/ -v    # Run specific tests
```

### Docker build fails

```bash
docker build --progress=plain .  # Verbose output
docker system prune -a           # Clean Docker cache
```

## Status Badges

Add to README.md (replace USERNAME/REPO):

```markdown
[![CI](https://github.com/USERNAME/REPO/workflows/CI/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/USERNAME/REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/USERNAME/REPO)
```

## File Structure

```
.
├── .github/
│   └── workflows/
│       ├── ci.yml              # Continuous Integration
│       ├── cd.yml              # Continuous Deployment
│       ├── release.yml         # Release automation
│       ├── security-scan.yml   # Security scanning
│       └── README.md           # Workflow documentation
├── .pre-commit-config.yaml     # Pre-commit hooks
├── .secrets.baseline           # Secret scanning baseline
├── Makefile                    # Development commands
├── pyproject.toml             # Python configuration
├── README.md                  # Project README
├── SETUP.md                   # This file
└── docs/
    └── CICD_SETUP.md          # Detailed setup guide
```

## Resources

- [Detailed Setup Guide](./docs/CICD_SETUP.md)
- [Workflow Documentation](./.github/workflows/README.md)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Pre-commit Docs](https://pre-commit.com/)

## Getting Help

- Review [docs/CICD_SETUP.md](./docs/CICD_SETUP.md) for detailed instructions
- Check [.github/workflows/README.md](./.github/workflows/README.md) for workflow details
- Create an issue for questions or problems
- Check GitHub Actions logs for error details

## Next Steps

1. **Local Development**: Run `make ci-full` to ensure everything works
2. **GitHub Setup**: Configure repository settings and secrets
3. **First PR**: Create a feature branch and test the CI workflow
4. **Deployment**: Configure environments and test CD workflow
5. **Release**: Create a test release to verify the release workflow

---

For detailed instructions, see [docs/CICD_SETUP.md](./docs/CICD_SETUP.md)
