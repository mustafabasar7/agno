# CI/CD Pipeline - Quick Reference Card

## 📍 Location
```
/home/user/agno/cookbook/construction_safety/ppe_detection/
```

## ⚡ Quick Start (3 Steps)

```bash
# 1. Install dependencies
make install-dev

# 2. Install hooks
make install-hooks

# 3. Verify
make ci-full
```

## 🛠️ Common Commands

| Command | Purpose |
|---------|---------|
| `make lint` | Run linters (Ruff, Black) |
| `make format` | Auto-format code |
| `make type-check` | Type checking (MyPy) |
| `make ci-test` | Run tests with coverage |
| `make security-check` | Security scan |
| `make ci-full` | **Run all CI checks** |
| `make help` | Show all commands |

## 🔄 Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **ci.yml** | Push, PR | Testing, linting, quality |
| **cd.yml** | Push to main | Deploy to staging/production |
| **release.yml** | Version tags | Create releases |
| **security-scan.yml** | Weekly, manual | Security scanning |

## 📁 Key Files

```
.github/workflows/        # GitHub Actions workflows
├── ci.yml               # Continuous Integration
├── cd.yml               # Continuous Deployment
├── release.yml          # Release automation
└── security-scan.yml    # Security scanning

.pre-commit-config.yaml  # Pre-commit hooks
Makefile                 # Development commands
README.md                # Project docs + badges
SETUP.md                 # Quick setup guide
CONTRIBUTING.md          # How to contribute
docs/CICD_SETUP.md      # Detailed CI/CD guide
```

## 🎯 Typical Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# ... edit files ...

# 3. Run checks
make ci-full

# 4. Commit (pre-commit runs automatically)
git add .
git commit -m "feat: add new feature"

# 5. Push
git push origin feature/my-feature

# 6. Create PR
gh pr create
```

## 🏷️ Release Process

```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Commit and push

# 4. Create tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 5. Release workflow runs automatically
```

## 🔧 Pre-commit Hooks

Runs automatically on commit:
- ✅ Black formatting
- ✅ Ruff linting
- ✅ isort imports
- ✅ MyPy type checking
- ✅ Bandit security
- ✅ Secret detection
- ✅ YAML/JSON validation

Skip if needed: `git commit --no-verify`

## 📊 Status Badges

Add to README (replace USERNAME/REPO):

```markdown
[![CI](https://github.com/USERNAME/REPO/workflows/CI/badge.svg)](...)
[![Coverage](https://codecov.io/gh/USERNAME/REPO/branch/main/graph/badge.svg)](...)
```

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Pre-commit fails | `make format` then retry |
| Tests fail | `make ci-test` to debug |
| Docker build fails | `docker build --progress=plain .` |
| Hooks not running | `make install-hooks` |

## 📖 Documentation

| Doc | Purpose |
|-----|---------|
| **SETUP.md** | Quick setup |
| **docs/CICD_SETUP.md** | Detailed guide |
| **CICD_INSTALL.md** | Installation summary |
| **CONTRIBUTING.md** | Contribute guide |
| **.github/workflows/README.md** | Workflow details |

## ✅ Verification

```bash
./scripts/verify_cicd.sh
```

## 🔐 Required GitHub Secrets

**Optional**:
- `CODECOV_TOKEN` - For coverage
- `PYPI_API_TOKEN` - For PyPI
- Deployment secrets - For CD

## 🌐 Environments

Configure in GitHub Settings → Environments:
- **staging** - Auto-deploy from main
- **production** - Manual approval
- **production-approval** - Approval gate

## 💡 Tips

1. Run `make ci-full` before pushing
2. Use conventional commits: `feat:`, `fix:`, `docs:`
3. Keep commits small and focused
4. Add tests for new features
5. Update docs when needed

## 📞 Get Help

- Run: `make help`
- Read: `SETUP.md`
- Check: `docs/CICD_SETUP.md`
- Verify: `./scripts/verify_cicd.sh`

---

**Quick Links**: [SETUP.md](./SETUP.md) | [CONTRIBUTING.md](./CONTRIBUTING.md) | [docs/CICD_SETUP.md](./docs/CICD_SETUP.md)
