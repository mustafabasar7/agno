# Pull Request

## Description

<!-- Provide a brief description of the changes in this PR -->

## Related Issues

<!-- Link related issues here. Use "Fixes #123" to auto-close issues when PR is merged -->

Fixes #
Related to #

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] CI/CD changes
- [ ] Dependency updates

## Changes Made

<!-- List the main changes in this PR -->

-
-
-

## Testing Performed

<!-- Describe the testing you have performed -->

### Test Environment
- Python version:
- OS:
- Docker version (if applicable):

### Tests Run
- [ ] Unit tests (`make ci-test`)
- [ ] Integration tests
- [ ] Manual testing
- [ ] E2E tests
- [ ] Performance tests

### Test Results
<!-- Paste relevant test results or describe manual testing -->

```bash
# Example: paste test output here
```

## Screenshots

<!-- Add screenshots if applicable, especially for UI changes -->

## Checklist

<!-- Mark completed items with an "x" -->

### Code Quality
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have run `make ci-full` and all checks pass

### Documentation
- [ ] I have updated the documentation accordingly
- [ ] I have added/updated docstrings for new/modified functions
- [ ] I have updated the README if needed
- [ ] I have updated CHANGELOG.md

### Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have added integration tests if applicable
- [ ] Code coverage has not decreased

### Dependencies
- [ ] I have checked that no new dependencies were added unnecessarily
- [ ] If dependencies were added, I have documented why they are needed
- [ ] I have updated requirements.txt or pyproject.toml if dependencies changed

### Security
- [ ] My changes do not introduce security vulnerabilities
- [ ] I have not committed any secrets, credentials, or sensitive data
- [ ] I have run `make security-check` and addressed any issues

### CI/CD
- [ ] All CI checks are passing
- [ ] I have verified that the Docker image builds successfully
- [ ] Pre-commit hooks are passing

## Breaking Changes

<!-- If this PR contains breaking changes, describe them here -->

<!--
Example:
BREAKING CHANGE: The `/api/v1/detect` endpoint now returns a different response format.

**Before:**
```json
{
  "detections": [...],
  "count": 5
}
```

**After:**
```json
{
  "results": [...],
  "total": 5,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Migration Guide:**
1. Update API client to use new field names
2. Update any code that relies on the old format
-->

## Deployment Notes

<!-- Add any special instructions for deploying these changes -->

- [ ] Database migrations required
- [ ] Environment variables need to be updated
- [ ] Configuration changes required
- [ ] Requires manual deployment steps

### Migration Commands
<!-- If migrations are needed, list them here -->

```bash
# Example
alembic upgrade head
```

## Performance Impact

<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improvement (describe below)
- [ ] Potential performance degradation (describe below and justify)

<!-- If applicable, add benchmark results -->

## Rollback Plan

<!-- Describe how to rollback these changes if issues occur in production -->

## Additional Context

<!-- Add any other context about the PR here -->

## Reviewer Notes

<!-- Any specific areas you want reviewers to focus on? -->

---

## For Reviewers

### Review Checklist

- [ ] Code follows project style guidelines
- [ ] Changes are well-tested
- [ ] Documentation is updated
- [ ] No security concerns
- [ ] Performance is acceptable
- [ ] Breaking changes are clearly documented
- [ ] Commit messages follow conventional commits format

### Review Comments

<!-- Reviewers: Add your comments here -->
