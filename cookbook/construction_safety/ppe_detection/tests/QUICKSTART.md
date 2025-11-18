# Test Suite Quick Start Guide

Quick reference for running tests in the PPE Detection System.

## Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio pytest-mock scikit-image
```

## Quick Commands

### Run All Tests

```bash
# From project root
cd /home/user/agno/cookbook/construction_safety/ppe_detection

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Run by Category

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# Quick validation (exclude slow tests)
pytest -m "not slow"

# Turkish construction scenarios
pytest -m turkish
```

### Run Specific Tests

```bash
# Single test file
pytest tests/unit/test_ppe_detector.py

# Single test class
pytest tests/unit/test_ppe_detector.py::TestPPEDetector

# Single test function
pytest tests/unit/test_ppe_detector.py::TestPPEDetector::test_detector_initialization
```

## Expected Results

### First Run (All Tests)

```
================================ test session starts =================================
platform linux -- Python 3.10.x, pytest-8.x.x
collected XXX items

tests/unit/test_ppe_detector.py ........................              [ 25%]
tests/unit/test_camera_handler.py ...................                  [ 45%]
tests/unit/test_alert_manager.py .................                     [ 60%]
tests/unit/test_database.py ....................                       [ 75%]
tests/unit/test_api_endpoints.py .................                     [ 85%]
tests/integration/test_end_to_end.py .....                             [ 90%]
tests/integration/test_camera_to_detection.py .......                  [ 95%]
tests/integration/test_detection_to_alert.py ......                    [100%]

========================== XXX passed in XX.XXs =================================
```

### Coverage Report

```
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
src/models/ppe_detector.py            250      15    94%   45-50, 123
src/camera/camera_manager.py          180      20    89%   67-72
src/alerts/alert_manager.py           220      25    89%   89-95
src/database/crud.py                  280      18    94%   234-240
src/api/endpoints.py                  200      30    85%   145-160
-----------------------------------------------------------------
TOTAL                                1500     125    92%
```

## Common Test Patterns

### Test Individual Component

```bash
# Test PPE detector
pytest tests/unit/test_ppe_detector.py -v

# Test camera handling
pytest tests/unit/test_camera_handler.py -v

# Test alerts
pytest tests/unit/test_alert_manager.py -v

# Test database
pytest tests/unit/test_database.py -v
```

### Test End-to-End Pipeline

```bash
# Full pipeline tests
pytest tests/integration/test_end_to_end.py -v

# Camera to detection
pytest tests/integration/test_camera_to_detection.py -v

# Detection to alert
pytest tests/integration/test_detection_to_alert.py -v
```

### Debug Failing Tests

```bash
# Stop at first failure
pytest -x

# Show detailed output
pytest -vv --tb=long

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb
```

## Performance Testing

```bash
# Show slowest 10 tests
pytest --durations=10

# Profile test execution
pytest --durations=0
```

## Continuous Integration

```bash
# Run tests as in CI
pytest --cov=src --cov-report=xml --cov-fail-under=80

# Generate JUnit XML for CI tools
pytest --junit-xml=test-results.xml
```

## Common Issues & Solutions

### Issue: Import errors

```bash
# Solution: Run from project root
cd /home/user/agno/cookbook/construction_safety/ppe_detection
pytest
```

### Issue: No tests collected

```bash
# Check test discovery
pytest --collect-only

# Verify test files match pattern test_*.py
ls tests/unit/test_*.py
ls tests/integration/test_*.py
```

### Issue: Tests timeout

```bash
# Increase timeout
pytest --timeout=600

# Skip slow tests
pytest -m "not slow"
```

### Issue: Coverage too low

```bash
# Show which files need more coverage
pytest --cov=src --cov-report=term-missing

# View detailed HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Development Workflow

### Before Committing

```bash
# 1. Run all tests
pytest

# 2. Check coverage
pytest --cov=src --cov-report=term

# 3. Ensure coverage meets minimum
pytest --cov=src --cov-fail-under=80

# 4. Run linters (if configured)
# black src/ tests/
# flake8 src/ tests/
```

### During Development

```bash
# Run only tests for component you're working on
pytest tests/unit/test_ppe_detector.py -v

# Watch mode (requires pytest-watch)
# pip install pytest-watch
# ptw
```

### Before Pull Request

```bash
# Full test suite with coverage
pytest --cov=src --cov-report=html --cov-fail-under=80

# Run integration tests
pytest -m integration

# Run slow tests
pytest -m slow
```

## Test Markers Reference

| Marker | Description | Example |
|--------|-------------|---------|
| `unit` | Unit tests | `pytest -m unit` |
| `integration` | Integration tests | `pytest -m integration` |
| `slow` | Slow tests (>1s) | `pytest -m slow` |
| `model` | Requires ML model | `pytest -m model` |
| `camera` | Camera/RTSP tests | `pytest -m camera` |
| `database` | Database tests | `pytest -m database` |
| `api` | API endpoint tests | `pytest -m api` |
| `turkish` | Turkish scenarios | `pytest -m turkish` |
| `performance` | Performance tests | `pytest -m performance` |

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [conftest.py](conftest.py) for available fixtures
- Review [test_utils.py](test_utils.py) for helper functions
- See individual test files for usage examples

## Support

For issues:
1. Check this guide
2. Read test README.md
3. Check pytest documentation: https://docs.pytest.org/
4. Review existing tests for patterns
