# GitHub Actions Workflows

This directory contains the CI/CD pipeline configuration for the PPE Detection project.

## Workflows Overview

### 1. CI (Continuous Integration) - `ci.yml`

**Triggers:**
- Push to `main`, `develop`, `feature/**` branches
- Pull requests to `main`, `develop` branches

**Jobs:**
- **Lint and Test**: Runs on Python 3.10 and 3.11
  - Code formatting check (Black)
  - Linting (Ruff)
  - Type checking (MyPy)
  - Unit tests with coverage
  - Upload coverage to Codecov

- **Docker Build Test**: Verifies Docker image builds

- **Integration Tests**: Tests with PostgreSQL and Redis services

- **Security Check**: Basic security scanning

- **Status Check**: Overall CI status verification

**Required Secrets:**
- `CODECOV_TOKEN` (optional) - For uploading coverage reports

### 2. CD (Continuous Deployment) - `cd.yml`

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Jobs:**
1. **Build and Push**: Build and push Docker images to GitHub Container Registry
2. **Deploy Staging**: Deploy to staging environment
3. **Smoke Tests (Staging)**: Verify staging deployment
4. **Production Approval**: Manual approval gate
5. **Deploy Production**: Deploy to production environment
6. **Smoke Tests (Production)**: Verify production deployment
7. **Rollback**: Automatic rollback on failure

**Required Secrets:**
- `GITHUB_TOKEN` (automatically provided)
- Configure deployment-specific secrets for your environments

**Environments:**
Configure these in GitHub Settings → Environments:
- `staging`: Staging environment
- `production`: Production environment (with protection rules)
- `production-approval`: Manual approval for production
- `production-rollback`: Rollback approval

### 3. Release - `release.yml`

**Triggers:**
- Push of version tags (v*.*.*)
- Manual workflow dispatch

**Jobs:**
1. **Validate Release**: Check version format
2. **Run Tests**: Full test suite
3. **Build Release Artifacts**: Python packages
4. **Build and Push Docker**: Multi-platform images
5. **Generate Changelog**: Auto-generate from commits
6. **Create GitHub Release**: Create release with artifacts
7. **Publish to PyPI**: Publish Python package (optional)
8. **Notify Release**: Send notifications

**Required Secrets:**
- `PYPI_API_TOKEN` (optional) - For publishing to PyPI

**Creating a Release:**
```bash
# Create and push a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 4. Security Scanning - `security-scan.yml`

**Triggers:**
- Push to `main`, `develop` branches
- Pull requests to `main`, `develop` branches
- Weekly schedule (Monday at 00:00 UTC)
- Manual workflow dispatch

**Jobs:**
1. **Dependency Scan**: Safety, pip-audit
2. **Code Security Scan**: Bandit
3. **Secret Scan**: TruffleHog, GitLeaks
4. **Container Scan**: Trivy, Docker Scout
5. **SAST CodeQL**: Static analysis
6. **License Scan**: License compliance
7. **Security Summary**: Aggregate results

**Artifacts:**
All scan results are uploaded as artifacts with 90-day retention.

## Setup Instructions

### 1. GitHub Repository Settings

#### Enable GitHub Actions
1. Go to Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"
3. Set workflow permissions to "Read and write permissions"

#### Configure Secrets

Navigate to Settings → Secrets and variables → Actions:

**Optional Secrets:**
- `CODECOV_TOKEN`: Get from [codecov.io](https://codecov.io)
- `PYPI_API_TOKEN`: Get from [pypi.org](https://pypi.org)

**Deployment Secrets** (configure based on your infrastructure):
- `DEPLOY_SSH_KEY`: SSH key for deployment
- `KUBECONFIG`: Kubernetes config for deployments
- `SLACK_WEBHOOK`: For notifications

#### Configure Environments

Navigate to Settings → Environments:

1. **staging**
   - No protection rules
   - Add environment-specific secrets
   - URL: https://ppe-detection-staging.example.com

2. **production**
   - Required reviewers: Add team members
   - Wait timer: 5 minutes (optional)
   - Add environment-specific secrets
   - URL: https://ppe-detection.example.com

3. **production-approval**
   - Required reviewers: Add approvers
   - Branch protection: main only

4. **production-rollback**
   - Required reviewers: Add approvers

### 2. Configure Branch Protection

Navigate to Settings → Branches → Add rule:

**For `main` branch:**
- Require pull request reviews (1 approval)
- Require status checks to pass:
  - `Lint and Test (3.10)`
  - `Lint and Test (3.11)`
  - `Docker Build Test`
  - `CI Status Check`
- Require branches to be up to date
- Require signed commits (optional)
- Include administrators

**For `develop` branch:**
- Require status checks to pass:
  - `Lint and Test (3.10)`
  - `Lint and Test (3.11)`

### 3. Enable Security Features

Navigate to Settings → Code security and analysis:

- Enable Dependabot alerts
- Enable Dependabot security updates
- Enable Secret scanning
- Enable Code scanning (CodeQL)

### 4. Configure Codecov (Optional)

1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Copy the token
4. Add as `CODECOV_TOKEN` secret in GitHub

### 5. Update Workflow Files

Replace placeholders in the workflow files and README:
- `USERNAME/REPO` → Your GitHub username/repository
- `your.email@example.com` → Your email
- URLs for staging/production environments

### 6. Customize Deployment

Edit the deployment steps in `cd.yml` based on your infrastructure:

**For Kubernetes:**
```yaml
- name: Deploy to staging
  run: |
    kubectl set image deployment/ppe-detection \
      ppe-detection=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest \
      --namespace=staging
```

**For Docker Compose:**
```yaml
- name: Deploy to staging
  run: |
    ssh user@staging-server "
      docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest &&
      docker-compose up -d
    "
```

**For Cloud Providers:**
- AWS ECS: Use AWS ECS deploy action
- Google Cloud Run: Use Google Cloud deploy action
- Azure Container Instances: Use Azure CLI

## Running Workflows

### Manually Trigger Workflows

**CD Workflow:**
```bash
gh workflow run cd.yml -f environment=staging
```

**Security Scan:**
```bash
gh workflow run security-scan.yml
```

**Release:**
```bash
gh workflow run release.yml -f version=v1.0.0
```

### View Workflow Status

```bash
# List workflow runs
gh run list

# View specific run
gh run view <run-id>

# Watch a run
gh run watch
```

### Download Artifacts

```bash
# List artifacts
gh run view <run-id> --artifacts

# Download artifact
gh run download <run-id> -n artifact-name
```

## Best Practices

1. **Branch Strategy**
   - Use feature branches for development
   - Merge to `develop` for integration testing
   - Merge to `main` for production deployment
   - Use version tags for releases

2. **Commit Messages**
   - Follow conventional commits format
   - Use meaningful descriptions
   - Reference issue numbers

3. **Pull Requests**
   - Create small, focused PRs
   - Wait for CI checks to pass
   - Get code review approval
   - Squash commits when merging

4. **Releases**
   - Use semantic versioning (v1.2.3)
   - Test thoroughly before tagging
   - Review changelog before release
   - Monitor deployment after release

5. **Security**
   - Review security scan results weekly
   - Update dependencies regularly
   - Rotate secrets periodically
   - Monitor for exposed secrets

## Troubleshooting

### CI Failures

**Tests failing:**
```bash
# Run tests locally
make ci-test

# Check specific test
pytest tests/test_specific.py -v
```

**Linting errors:**
```bash
# Auto-fix formatting
make format

# Check what would be fixed
black --check --diff src tests
```

**Docker build fails:**
```bash
# Build locally
docker build -t ppe-detection:test .

# Check logs
docker build --progress=plain -t ppe-detection:test .
```

### CD Failures

**Deployment fails:**
1. Check deployment logs in GitHub Actions
2. Verify environment secrets
3. Test deployment manually
4. Check service health endpoints

**Smoke tests fail:**
1. Check application logs
2. Verify environment variables
3. Test endpoints manually
4. Review database migrations

### Security Scan Issues

**High severity vulnerabilities:**
1. Review the security report artifact
2. Update dependencies: `pip install --upgrade package-name`
3. Check for patches or alternatives
4. Document exceptions if needed

**False positives:**
1. Review the scan results
2. Add exceptions to configuration
3. Document the decision

## Monitoring

### GitHub Actions Status

View at: `https://github.com/USERNAME/REPO/actions`

### Coverage Reports

View at: `https://codecov.io/gh/USERNAME/REPO`

### Security Insights

View at: `https://github.com/USERNAME/REPO/security`

## Support

- GitHub Actions Documentation: https://docs.github.com/actions
- Report issues: https://github.com/USERNAME/REPO/issues
- Discussions: https://github.com/USERNAME/REPO/discussions

---

**Last Updated**: 2024
