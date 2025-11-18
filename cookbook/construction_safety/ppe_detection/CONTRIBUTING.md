# Contributing to PPE Detection System

Thank you for considering contributing to the PPE Detection System! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [CI/CD Pipeline](#cicd-pipeline)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.10 or 3.11
- Git
- Docker and Docker Compose
- Make

### Setup Development Environment

1. **Fork and clone the repository**

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/ppe-detection.git
cd ppe-detection

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/ppe-detection.git
```

2. **Install dependencies**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make install-dev

# Install pre-commit hooks
make install-hooks
```

3. **Setup environment**

```bash
# Create .env file
make setup

# Edit .env with your configuration
nano .env
```

4. **Verify setup**

```bash
# Run all CI checks
make ci-full

# Start development environment
make start-dev
```

## Development Workflow

### Branch Strategy

We use a simplified Git Flow:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Emergency fixes for production

### Creating a Feature

1. **Update your fork**

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

2. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes**

```bash
# Make changes to code
# ...

# Run tests and checks
make ci-full
```

4. **Commit your changes**

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat: add new feature description"
```

5. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

6. **Create Pull Request**

```bash
# Using GitHub CLI
gh pr create --base main --head feature/your-feature-name

# Or create via GitHub web interface
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (configured in Black)
- **Formatter**: Black
- **Linter**: Ruff
- **Type hints**: Required for public APIs
- **Docstrings**: Google style

### Code Formatting

```bash
# Auto-format code
make format

# Check formatting
black --check src tests

# Check linting
ruff check src tests
```

### Type Checking

```bash
# Run type checking
make type-check

# Or directly
mypy src --ignore-missing-imports
```

### Import Organization

Imports should be organized in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

Use `isort` to auto-organize:

```bash
isort src tests
```

### Example Code Style

```python
"""Module docstring describing the module."""

from typing import List, Optional

import numpy as np
from fastapi import FastAPI

from src.models import Detection
from src.utils import process_image


class PPEDetector:
    """Detect PPE in images.

    Args:
        model_path: Path to the detection model
        confidence_threshold: Minimum confidence for detections

    Attributes:
        model: The loaded detection model
        threshold: Confidence threshold
    """

    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.5
    ) -> None:
        """Initialize the detector."""
        self.model = self._load_model(model_path)
        self.threshold = confidence_threshold

    def detect(self, image: np.ndarray) -> List[Detection]:
        """Detect PPE in an image.

        Args:
            image: Input image as numpy array

        Returns:
            List of Detection objects

        Raises:
            ValueError: If image is invalid
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid image")

        # Process image
        results = self.model(image)
        return self._parse_results(results)

    def _load_model(self, path: str):
        """Load the detection model (private method)."""
        # Implementation
        pass
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── e2e/              # End-to-end tests
└── fixtures/         # Test fixtures
```

### Writing Tests

```python
import pytest
from src.detector import PPEDetector


class TestPPEDetector:
    """Test PPE detector functionality."""

    @pytest.fixture
    def detector(self):
        """Create detector instance for testing."""
        return PPEDetector(model_path="tests/fixtures/model.pt")

    def test_detect_hardhat(self, detector):
        """Test hardhat detection."""
        image = load_test_image("hardhat.jpg")
        results = detector.detect(image)

        assert len(results) > 0
        assert any(r.class_name == "hardhat" for r in results)

    def test_invalid_image_raises_error(self, detector):
        """Test that invalid image raises ValueError."""
        with pytest.raises(ValueError):
            detector.detect(None)
```

### Running Tests

```bash
# Run all tests
make ci-test

# Run specific test file
pytest tests/test_detector.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_detector.py::TestPPEDetector::test_detect_hardhat -v
```

### Test Coverage

- Aim for >80% code coverage
- All new features must include tests
- Critical paths require 100% coverage

## Commit Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Scopes

- `api`: API changes
- `detector`: Detection logic
- `db`: Database changes
- `docker`: Docker configuration
- `ci`: CI/CD pipeline

### Examples

```bash
# Feature
git commit -m "feat(detector): add support for safety boots detection"

# Bug fix
git commit -m "fix(api): correct confidence threshold validation"

# Documentation
git commit -m "docs: update deployment guide"

# Refactor
git commit -m "refactor(detector): optimize image preprocessing"

# Breaking change
git commit -m "feat(api)!: change detection endpoint response format

BREAKING CHANGE: Detection endpoint now returns array of objects instead of object with array"
```

### Pre-commit Hooks

Pre-commit hooks will automatically:
- Format code with Black and isort
- Lint with Ruff
- Check for secrets
- Run type checking
- Validate commit message format

If hooks fail:

```bash
# Fix formatting issues
make format

# Run hooks manually
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

## Pull Request Process

### Before Creating a PR

1. **Update from upstream**

```bash
git fetch upstream
git rebase upstream/main
```

2. **Run all checks**

```bash
make ci-full
```

3. **Update documentation** if needed

4. **Update tests** for new features

### Creating a Pull Request

1. **Use a descriptive title**

```
feat(detector): add support for safety boots detection
```

2. **Fill out the PR template**

Include:
- Description of changes
- Related issues
- Testing performed
- Screenshots (if applicable)

3. **Add labels**

- `feature`, `bugfix`, `documentation`, etc.
- `breaking-change` if applicable

4. **Request reviewers**

### PR Template

```markdown
## Description
Brief description of the changes

## Related Issues
Fixes #123

## Changes
- Added X
- Updated Y
- Fixed Z

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] All CI checks passing

## Screenshots
(if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
- [ ] Changes generate no errors
```

### Review Process

1. **Automated checks** must pass
   - CI workflow
   - Code coverage requirements
   - Security scans

2. **Code review** by maintainer
   - At least 1 approval required for `main` branch

3. **Address feedback**
   - Make requested changes
   - Push updates to the same branch

4. **Merge**
   - Squash and merge (default)
   - Maintainer will merge when approved

## CI/CD Pipeline

### Continuous Integration

On every push and PR, CI will:

1. **Lint and format checks**
   - Black formatting
   - Ruff linting
   - isort import sorting

2. **Type checking**
   - MyPy static type analysis

3. **Tests**
   - Unit tests
   - Integration tests
   - Coverage reporting

4. **Security checks**
   - Dependency scanning
   - Code security analysis

5. **Docker build**
   - Verify image builds successfully

### Running CI Locally

```bash
# Run full CI suite
make ci-full

# Individual checks
make lint           # Linting
make format         # Formatting (auto-fix)
make type-check     # Type checking
make ci-test        # Tests
make security-check # Security scans
```

### Continuous Deployment

Automatic deployment on merge to `main`:

1. Build Docker images
2. Push to container registry
3. Deploy to staging
4. Run smoke tests
5. Manual approval gate
6. Deploy to production

### Release Process

Create a release by pushing a version tag:

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

This triggers:
1. Full test suite
2. Build artifacts
3. Create GitHub release
4. Publish to PyPI (if configured)
5. Build and push Docker images

## Additional Guidelines

### Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update CHANGELOG.md

### Performance

- Profile performance-critical code
- Include benchmarks for optimizations
- Consider memory usage

### Security

- Never commit secrets or credentials
- Use environment variables for configuration
- Follow security best practices
- Report security issues privately

### Accessibility

- Ensure API is well-documented
- Provide helpful error messages
- Include examples and tutorials

## Getting Help

- **Documentation**: Check [docs/](./docs/) directory
- **Issues**: Search existing issues or create new one
- **Discussions**: Use GitHub Discussions for questions
- **Chat**: Join our community chat (if available)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
