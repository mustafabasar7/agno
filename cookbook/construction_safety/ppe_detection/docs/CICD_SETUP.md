# CI/CD Pipeline Setup Guide

Complete guide to setting up and configuring the CI/CD pipeline for the PPE Detection project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Local Development Setup](#local-development-setup)
4. [GitHub Actions Setup](#github-actions-setup)
5. [Environment Configuration](#environment-configuration)
6. [Deployment Setup](#deployment-setup)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- Git (v2.30+)
- Python (3.10 or 3.11)
- Docker (v20.10+)
- Docker Compose (v2.0+)
- Make

### Optional Tools

- GitHub CLI (`gh`) - For easier workflow management
- kubectl - For Kubernetes deployments
- AWS/GCP/Azure CLI - For cloud deployments

### Required Accounts

- GitHub account with repository access
- Container registry (GitHub Container Registry is included)
- (Optional) Codecov account for coverage reports
- (Optional) PyPI account for package publishing

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/USERNAME/REPO.git
cd ppe_detection

# Install development dependencies
make install-dev

# Install pre-commit hooks
make install-hooks
```

### 2. Verify Local CI/CD

```bash
# Run all CI checks locally
make ci-full

# Run individual checks
make lint          # Run linters
make format        # Format code
make type-check    # Type checking
make ci-test       # Run tests
make security-check # Security scan
```

### 3. Test Pre-commit Hooks

```bash
# Run on all files
make pre-commit-all

# Or manually
pre-commit run --all-files

# Test a commit
git add .
git commit -m "test: verify pre-commit hooks"
```

## Local Development Setup

### Install Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

### Configuration Files

The project includes these configuration files:

1. **`.pre-commit-config.yaml`** - Pre-commit hooks configuration
2. **`pyproject.toml`** - Python project configuration
3. **`.github/workflows/*.yml`** - GitHub Actions workflows
4. **`Makefile`** - Development commands

### Running Checks Locally

```bash
# Format code
make format

# Check formatting
black --check src tests

# Lint code
make lint

# Type check
make type-check

# Run tests
make ci-test

# Full CI suite
make ci-full
```

## GitHub Actions Setup

### 1. Enable GitHub Actions

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Actions** → **General**
3. Under "Actions permissions":
   - Select "Allow all actions and reusable workflows"
4. Under "Workflow permissions":
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"

### 2. Configure Branch Protection

Navigate to **Settings** → **Branches** → **Add branch protection rule**

**For `main` branch:**

```
Branch name pattern: main

[✓] Require a pull request before merging
    [✓] Require approvals: 1
    [✓] Dismiss stale pull request approvals when new commits are pushed
    [✓] Require review from Code Owners

[✓] Require status checks to pass before merging
    [✓] Require branches to be up to date before merging
    Status checks that are required:
      - Lint and Test (3.10)
      - Lint and Test (3.11)
      - Docker Build Test
      - CI Status Check

[✓] Require conversation resolution before merging
[✓] Require signed commits (optional)
[✓] Require linear history (optional)
[✓] Include administrators
```

**For `develop` branch:**

```
Branch name pattern: develop

[✓] Require status checks to pass before merging
    Status checks that are required:
      - Lint and Test (3.10)
      - Lint and Test (3.11)
```

### 3. Configure Secrets

Navigate to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

#### Required Secrets

These are automatically provided by GitHub:
- `GITHUB_TOKEN` - Automatically available

#### Optional Secrets

**For Coverage Reports:**
```
Name: CODECOV_TOKEN
Value: <token from codecov.io>
```

**For PyPI Publishing:**
```
Name: PYPI_API_TOKEN
Value: <token from pypi.org>
```

**For Deployments:**
```
Name: DEPLOY_SSH_KEY
Value: <your deployment SSH private key>

Name: DOCKER_REGISTRY_USERNAME
Value: <registry username>

Name: DOCKER_REGISTRY_PASSWORD
Value: <registry password>
```

**For Notifications:**
```
Name: SLACK_WEBHOOK_URL
Value: <your Slack webhook URL>
```

### 4. Configure Environments

Navigate to **Settings** → **Environments** → **New environment**

#### Staging Environment

```
Name: staging

Environment protection rules:
  [  ] Required reviewers
  [  ] Wait timer: 0 minutes
  [✓] Deployment branches: Selected branches
      - main
      - develop

Environment secrets:
  DATABASE_URL: <staging database URL>
  REDIS_URL: <staging Redis URL>
  API_KEY: <staging API key>

Environment URL: https://ppe-detection-staging.example.com
```

#### Production Environment

```
Name: production

Environment protection rules:
  [✓] Required reviewers: (Add team members)
  [✓] Wait timer: 5 minutes
  [✓] Deployment branches: Selected branches
      - main

Environment secrets:
  DATABASE_URL: <production database URL>
  REDIS_URL: <production Redis URL>
  API_KEY: <production API key>

Environment URL: https://ppe-detection.example.com
```

#### Production Approval Environment

```
Name: production-approval

Environment protection rules:
  [✓] Required reviewers: (Add approvers)
  [✓] Deployment branches: Selected branches
      - main
```

### 5. Enable Security Features

Navigate to **Settings** → **Code security and analysis**

Enable the following:
- [✓] Dependency graph
- [✓] Dependabot alerts
- [✓] Dependabot security updates
- [✓] Dependabot version updates (optional)
- [✓] Secret scanning
- [✓] Push protection for secret scanning
- [✓] Code scanning (CodeQL)

## Environment Configuration

### Docker Registry Setup

#### GitHub Container Registry (Default)

Already configured in workflows. Images will be pushed to:
```
ghcr.io/USERNAME/REPO/ppe-detection
```

To use:
```bash
# Login locally
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull image
docker pull ghcr.io/USERNAME/REPO/ppe-detection:latest
```

#### Alternative Registries

**Docker Hub:**

Update in `.github/workflows/cd.yml` and `.github/workflows/release.yml`:

```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: username/ppe-detection
```

Add secrets:
```
DOCKERHUB_USERNAME: <your username>
DOCKERHUB_TOKEN: <your access token>
```

Update login action:
```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

**AWS ECR:**

```yaml
env:
  REGISTRY: <account-id>.dkr.ecr.<region>.amazonaws.com
  IMAGE_NAME: ppe-detection
```

Add secrets and configure AWS authentication.

### Codecov Setup (Optional)

1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Copy the upload token
4. Add as `CODECOV_TOKEN` secret in GitHub

Codecov will automatically:
- Track coverage over time
- Comment on pull requests
- Generate coverage reports

## Deployment Setup

### Option 1: Kubernetes Deployment

1. **Setup kubectl and kubeconfig**

```bash
# Test connection
kubectl cluster-info

# Create namespace
kubectl create namespace ppe-detection
```

2. **Add GitHub Secret**

```bash
# Get kubeconfig
cat ~/.kube/config | base64

# Add as KUBECONFIG secret in GitHub
```

3. **Update CD Workflow**

In `.github/workflows/cd.yml`:

```yaml
- name: Deploy to staging
  run: |
    echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
    export KUBECONFIG=./kubeconfig

    kubectl set image deployment/ppe-detection \
      ppe-detection=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
      --namespace=staging

    kubectl rollout status deployment/ppe-detection -n staging
```

4. **Create Kubernetes manifests**

```bash
# Create deployment files
mkdir -p k8s/staging k8s/production

# Add deployment.yaml, service.yaml, ingress.yaml
```

### Option 2: Docker Compose Deployment

1. **Setup SSH Access**

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "github-actions"

# Add public key to server
ssh-copy-id user@server

# Add private key as DEPLOY_SSH_KEY secret in GitHub
```

2. **Update CD Workflow**

```yaml
- name: Deploy to staging
  run: |
    echo "${{ secrets.DEPLOY_SSH_KEY }}" > deploy_key
    chmod 600 deploy_key

    ssh -i deploy_key -o StrictHostKeyChecking=no user@staging-server "
      cd /app/ppe-detection &&
      docker-compose pull &&
      docker-compose up -d &&
      docker-compose exec -T app alembic upgrade head
    "
```

### Option 3: Cloud Platform Deployment

#### AWS ECS

Use the [AWS ECS deploy action](https://github.com/aws-actions/amazon-ecs-deploy-task-definition)

#### Google Cloud Run

Use the [Google Cloud deploy action](https://github.com/google-github-actions/deploy-cloudrun)

#### Azure Container Instances

Use Azure CLI in the workflow

### Database Migrations

Add migration step to CD workflow:

```yaml
- name: Run database migrations
  run: |
    # For Kubernetes
    kubectl exec -n staging deployment/ppe-detection -- \
      alembic upgrade head

    # For SSH deployment
    ssh user@server "cd /app && docker-compose exec -T app alembic upgrade head"
```

## Monitoring and Observability

### Application Monitoring

1. **Setup Prometheus and Grafana**

```bash
# Start monitoring stack
make start-monitoring

# Access Grafana
open http://localhost:3000
```

2. **Configure Alerts**

Add to Prometheus `alertmanager.yml`:

```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: '<slack-webhook-url>'
        channel: '#alerts'
```

### CI/CD Monitoring

1. **GitHub Actions Dashboard**
   - View at: `https://github.com/USERNAME/REPO/actions`
   - Monitor workflow runs
   - Check job execution times

2. **Workflow Notifications**

Add to `.github/workflows/ci.yml`:

```yaml
- name: Notify on failure
  if: failure()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"CI Failed: ${{ github.workflow }}"}'
```

### Security Monitoring

1. **Review Security Alerts**
   - Navigate to Security tab
   - Review Dependabot alerts
   - Check CodeQL findings
   - Monitor secret scanning alerts

2. **Weekly Security Reports**
   - Automated security scans run weekly
   - Review artifacts in Actions

## Troubleshooting

### Common Issues

#### 1. Pre-commit Hooks Failing

```bash
# Update pre-commit
pre-commit autoupdate

# Clear cache
pre-commit clean

# Run manually
pre-commit run --all-files
```

#### 2. CI Tests Failing

```bash
# Run tests locally with same environment
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Check test logs
docker-compose -f docker-compose.test.yml logs app
```

#### 3. Docker Build Fails

```bash
# Build locally with verbose output
docker build --progress=plain -t ppe-detection:debug .

# Check for layer caching issues
docker build --no-cache -t ppe-detection:debug .
```

#### 4. Deployment Fails

```bash
# Check deployment logs
kubectl logs -f deployment/ppe-detection -n staging

# Check pod status
kubectl get pods -n staging

# Describe pod for events
kubectl describe pod <pod-name> -n staging
```

#### 5. Secret Not Available

```bash
# Verify secret exists
gh secret list

# Set secret
gh secret set SECRET_NAME

# Check environment secret
# Go to Settings → Environments → environment-name → Secrets
```

### Debug Workflows

Enable debug logging:

```bash
# Set repository secret
gh secret set ACTIONS_STEP_DEBUG --body true
gh secret set ACTIONS_RUNNER_DEBUG --body true
```

View detailed logs in workflow runs.

### Rollback Procedures

#### Rollback Deployment

```bash
# Kubernetes
kubectl rollout undo deployment/ppe-detection -n production

# Docker Compose
ssh user@server "
  cd /app/ppe-detection &&
  docker-compose pull <previous-tag> &&
  docker-compose up -d
"
```

#### Rollback Release

```bash
# Delete tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Delete release
gh release delete v1.0.0
```

## Best Practices

### 1. Development Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# ...

# Run checks locally before committing
make ci-full

# Commit with conventional commits
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
gh pr create
```

### 2. Release Workflow

```bash
# Ensure main is up to date
git checkout main
git pull origin main

# Run full test suite
make ci-full

# Create and push tag
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0

# Monitor release workflow
gh run watch
```

### 3. Security Practices

- Review security scan results weekly
- Update dependencies regularly: `pip install --upgrade package`
- Rotate secrets every 90 days
- Enable branch protection on main
- Require signed commits
- Use environment protection rules

### 4. Performance Optimization

- Use Docker layer caching
- Cache pip dependencies
- Minimize workflow steps
- Use matrix builds efficiently
- Archive only necessary artifacts

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## Support

For issues or questions:
- Create an issue: `gh issue create`
- Discussion: `https://github.com/USERNAME/REPO/discussions`
- Documentation: `./docs/`

---

**Last Updated**: 2024
**Maintained by**: Development Team
