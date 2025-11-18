# PPE Detection System

[![CI](https://github.com/USERNAME/REPO/workflows/CI/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/ci.yml)
[![CD](https://github.com/USERNAME/REPO/workflows/CD%20-%20Continuous%20Deployment/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/cd.yml)
[![Security Scanning](https://github.com/USERNAME/REPO/workflows/Security%20Scanning/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/security-scan.yml)
[![codecov](https://codecov.io/gh/USERNAME/REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/USERNAME/REPO)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)

A comprehensive Personal Protective Equipment (PPE) detection system for construction safety monitoring using computer vision and AI.

## Features

- Real-time PPE detection (hard hats, safety vests, goggles, gloves, safety boots)
- REST API for image and video processing
- Real-time video stream analysis
- Database integration for audit trails
- Redis caching for performance
- Celery task queue for background processing
- Prometheus metrics and Grafana dashboards
- Docker containerization
- Comprehensive CI/CD pipeline

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/USERNAME/REPO.git
cd ppe_detection

# Set up environment
make setup

# Edit .env with your configuration
nano .env

# Build and start services
make install

# Or for development
make install-dev
```

### Local Development

```bash
# Install dependencies
make install-dev

# Install pre-commit hooks
make install-hooks

# Run tests
make ci-test

# Run linters
make lint

# Format code
make format
```

## CI/CD Pipeline

This project includes a comprehensive CI/CD pipeline with the following workflows:

### Continuous Integration (CI)

Triggered on push and pull requests:
- Code formatting checks (Black)
- Linting (Ruff)
- Type checking (MyPy)
- Unit and integration tests with coverage
- Docker build verification
- Security scanning

```bash
# Run CI checks locally
make ci-full
```

### Continuous Deployment (CD)

Triggered on push to main:
- Build and push Docker images
- Deploy to staging environment
- Run smoke tests
- Manual approval for production
- Production deployment
- Automated rollback on failure

### Release Workflow

Triggered on version tags (v*.*.*):
- Full test suite execution
- Build release artifacts
- Multi-platform Docker images
- GitHub release creation
- PyPI publishing
- Changelog generation

### Security Scanning

Weekly automated scans:
- Dependency vulnerability scanning (Safety, pip-audit)
- Code security analysis (Bandit)
- Secret scanning (TruffleHog, GitLeaks)
- Container image scanning (Trivy, Docker Scout)
- SAST with CodeQL
- License compliance

## Development

### Prerequisites

- Python 3.10 or 3.11
- Docker and Docker Compose
- Git

### Setup Development Environment

```bash
# Install development dependencies
make install-dev

# Install pre-commit hooks
make install-hooks

# Run pre-commit on all files
make pre-commit-all
```

### Available Make Commands

#### CI/CD Commands
```bash
make install-dev      # Install development dependencies
make install-hooks    # Install pre-commit hooks
make lint            # Run linters (ruff, black)
make format          # Format code with black and isort
make type-check      # Run type checking with mypy
make ci-test         # Run tests as CI would
make security-check  # Run security checks
make ci-full         # Run all CI checks locally
make deploy          # Deploy application
```

#### Docker Commands
```bash
make build           # Build production images
make build-dev       # Build development images
make start           # Start production services
make start-dev       # Start development services
make stop            # Stop all services
make logs            # View logs
make test            # Run tests in container
make test-coverage   # Run tests with coverage
```

#### Database Commands
```bash
make db-shell        # Access PostgreSQL shell
make db-backup       # Backup database
make db-migrate      # Run migrations
```

See `make help` for all available commands.

### Running Tests

```bash
# Run all tests
make ci-test

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_detector.py -v

# Run integration tests
pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
make format

# Check linting
make lint

# Run type checking
make type-check

# Run all checks
make ci-full
```

## API Documentation

### Endpoints

- `GET /health` - Health check endpoint
- `POST /api/v1/detect` - Detect PPE in single image
- `POST /api/v1/detect/batch` - Batch image processing
- `POST /api/v1/detect/video` - Video processing
- `GET /api/v1/detections/{id}` - Get detection results
- `GET /metrics` - Prometheus metrics

API documentation available at: http://localhost:8000/docs

## Deployment

### Staging Deployment

Automatic deployment to staging on push to main branch:
```bash
git push origin main
```

### Production Deployment

1. Create a version tag:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

2. Approve production deployment in GitHub Actions

3. Monitor deployment:
```bash
# Check logs
make logs-app

# Check health
curl https://ppe-detection.example.com/health
```

### Rollback

If issues occur, use GitHub Actions to trigger rollback or:
```bash
# Manual rollback with kubectl
kubectl rollout undo deployment/ppe-detection -n production
```

## Monitoring

### Metrics

- Application metrics: http://localhost:9090 (Prometheus)
- Dashboards: http://localhost:3000 (Grafana)
- Default credentials: admin/admin

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health

# Check all services
make health

# View resource usage
make stats
```

## Security

### Reporting Vulnerabilities

Please report security vulnerabilities to: security@example.com

### Security Features

- Automated dependency scanning
- Container image vulnerability scanning
- Secret detection in commits
- Code security analysis (SAST)
- Regular security audits

### Pre-commit Hooks

Pre-commit hooks automatically run on every commit:
- Code formatting
- Linting
- Secret detection
- Large file prevention
- Type checking

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make ci-full`)
5. Commit your changes (follows conventional commits)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Your Name - Initial work - [@yourhandle](https://github.com/yourhandle)

## Acknowledgments

- Built with [Agno](https://github.com/agno-agi/agno)
- YOLOv8 for object detection
- FastAPI for API framework

## Support

- Documentation: [docs/](./docs/)
- Issues: [GitHub Issues](https://github.com/USERNAME/REPO/issues)
- Discussions: [GitHub Discussions](https://github.com/USERNAME/REPO/discussions)

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for release history.

## Roadmap

- [ ] Multi-camera support
- [ ] Real-time alerts and notifications
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Integration with building management systems
- [ ] Support for additional PPE types

---

**Note**: Replace `USERNAME/REPO` in badges and links with your actual GitHub repository path.
