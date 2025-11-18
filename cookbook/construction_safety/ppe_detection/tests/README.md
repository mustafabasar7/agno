# PPE Detection System - Test Suite

Comprehensive test suite for the PPE (Personal Protective Equipment) Detection System for Turkish construction sites.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)

## Overview

This test suite provides comprehensive coverage of the PPE detection system including:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and full pipeline
- **Performance Tests**: Benchmark critical operations
- **Turkish Scenario Tests**: Specific tests for Turkish construction site requirements

**Target Coverage**: >80% overall, 100% for critical paths

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_utils.py            # Test helper functions and utilities
├── pytest.ini               # Pytest configuration
├── README.md                # This file
│
├── unit/                    # Unit tests
│   ├── test_ppe_detector.py      # PPE detection logic tests
│   ├── test_camera_handler.py    # Camera connection tests
│   ├── test_alert_manager.py     # Alert logic tests
│   ├── test_database.py          # CRUD operation tests
│   └── test_api_endpoints.py     # API route tests
│
├── integration/             # Integration tests
│   ├── test_end_to_end.py           # Full pipeline tests
│   ├── test_camera_to_detection.py  # Camera + model tests
│   ├── test_detection_to_alert.py   # Detection + alert tests
│   └── test_api_integration.py      # API + database tests
│
└── fixtures/                # Test data and fixtures
    ├── data/                # Test data files
    └── images/              # Test images
```

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only Turkish scenario tests
pytest -m turkish

# Run fast tests (exclude slow tests)
pytest -m "not slow"

# Run model tests (requires model)
pytest -m model

# Run camera tests
pytest -m camera

# Run database tests
pytest -m database
```

### Run Specific Test Files

```bash
# Run specific test file
pytest tests/unit/test_ppe_detector.py

# Run specific test class
pytest tests/unit/test_ppe_detector.py::TestPPEDetector

# Run specific test function
pytest tests/unit/test_ppe_detector.py::TestPPEDetector::test_detector_initialization
```

### Run Tests with Different Output Formats

```bash
# Show test durations
pytest --durations=10

# Show detailed output
pytest -vv

# Show print statements
pytest -s

# Show locals in tracebacks
pytest --showlocals

# Generate JUnit XML report
pytest --junit-xml=test-results.xml
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (auto-detect CPUs)
pytest -n auto

# Run tests on 4 CPUs
pytest -n 4
```

## Test Coverage

### View Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Requirements

- **Overall Coverage**: >80%
- **Critical Modules**:
  - `models/ppe_detector.py`: 100%
  - `database/crud.py`: 95%
  - `alerts/alert_manager.py`: 90%
  - `camera/camera_manager.py`: 85%
  - `api/endpoints.py`: 90%

### Check Coverage

```bash
# Check if coverage meets minimum threshold
pytest --cov=src --cov-fail-under=80
```

## Test Categories

### Unit Tests

Test individual components in isolation using mocks and stubs.

```bash
pytest -m unit
```

**Coverage**:
- PPE Detector: Detection logic, compliance checking, visualization
- Camera Handler: RTSP connection, frame capture, reconnection
- Alert Manager: Alert rules, de-duplication, throttling, escalation
- Database: CRUD operations, queries, transactions
- API: Endpoint validation, request/response handling

### Integration Tests

Test interactions between components and full system pipeline.

```bash
pytest -m integration
```

**Scenarios**:
- Camera → Detection → Database → Alert (full pipeline)
- Multiple cameras processing simultaneously
- Database persistence and retrieval
- API with real database operations

### Slow Tests

Tests that take significant time (>1 second).

```bash
# Run all tests including slow
pytest

# Skip slow tests for quick validation
pytest -m "not slow"
```

### Turkish Construction Site Tests

Specific tests for Turkish construction requirements.

```bash
pytest -m turkish
```

**Scenarios**:
- Multiple workers in same frame (şantiye senaryosu)
- Partial PPE (baret var, yelek yok)
- Turkish zone names (Kazı Alanı, Yüksekte Çalışma)
- Turkish PPE terms (baret, yelek, iş ayakkabısı)
- Occlusion and poor lighting conditions

## Writing Tests

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class TestYourComponent:
    """Test YourComponent class."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        component = YourComponent()

        # Act
        result = component.do_something()

        # Assert
        assert result is not None

    @patch('module.Dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependency."""
        # Setup mock
        mock_dependency.return_value.method.return_value = "mocked"

        # Test with mock
        component = YourComponent(mock_dependency)
        result = component.use_dependency()

        assert result == "mocked"
```

### Using Fixtures

```python
def test_with_fixtures(test_db, sample_camera, sample_image):
    """Test using predefined fixtures."""
    # test_db: In-memory database session
    # sample_camera: Sample camera object
    # sample_image: Test image

    detections = detector.detect_ppe(sample_image)
    assert len(detections) > 0
```

### Custom Assertions

```python
from tests.test_utils import (
    assert_detection_valid,
    assert_compliance_result_valid,
    assert_image_valid
)

def test_detection():
    detection = detector.detect_ppe(image)
    assert_detection_valid(detection)
```

### Test Data Generators

```python
from tests.test_utils import (
    generate_compliant_worker_detections,
    generate_non_compliant_worker_detections,
    create_worker_image
)

def test_compliance():
    detections = generate_compliant_worker_detections()
    image = create_worker_image(has_helmet=True, has_vest=True)
    # Use in test
```

## Performance Testing

### Measure FPS

```python
from tests.test_utils import measure_fps

def test_detection_performance():
    fps = measure_fps(detector.detect_ppe, test_image, duration_seconds=5.0)
    assert fps > 10.0  # At least 10 FPS
```

### Measure Latency

```python
from tests.test_utils import measure_latency

def test_detection_latency():
    stats = measure_latency(detector.detect_ppe, test_image, iterations=100)
    assert stats["mean_ms"] < 200  # Average under 200ms
    assert stats["p95_ms"] < 300   # 95th percentile under 300ms
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Docker Testing

```bash
# Build test container
docker-compose -f docker-compose.dev.yml build test

# Run tests in container
docker-compose -f docker-compose.dev.yml run test pytest

# Run with coverage
docker-compose -f docker-compose.dev.yml run test pytest --cov=src
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "No module named 'src'"
```bash
# Solution: Run from project root
cd /path/to/ppe_detection
pytest
```

**Issue**: Database tests fail
```bash
# Solution: Tests use in-memory SQLite, no setup needed
# If issues persist, check conftest.py fixture
```

**Issue**: Camera tests timeout
```bash
# Solution: Camera tests use mocks by default
# Check mock setup in test file
```

**Issue**: Model tests fail
```bash
# Solution: Model tests mock YOLO by default
# To test with real model, mark with @pytest.mark.model
```

### Debug Tests

```bash
# Run with debugger
pytest --pdb

# Stop at first failure
pytest -x

# Show detailed failure info
pytest -vv --tb=long

# Show print statements
pytest -s
```

## Test Maintenance

### Update Test Data

```bash
# Regenerate test images
python tests/fixtures/generate_test_data.py

# Update fixtures
python tests/fixtures/update_fixtures.py
```

### Clean Test Artifacts

```bash
# Remove coverage files
rm -rf .coverage htmlcov/

# Remove pytest cache
rm -rf .pytest_cache/

# Remove test outputs
rm -rf tests/output/
```

## Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Maintain >80% coverage**
3. **Add appropriate markers** (@pytest.mark.unit, etc.)
4. **Update this README** if adding new test categories
5. **Run full test suite** before committing

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Support

For issues or questions about tests:
- Check this README
- Review existing tests for examples
- Check conftest.py for available fixtures
- Consult test_utils.py for helper functions
