## Pull Request Template

### Description
Brief description of changes made in this PR.

### Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Research contribution
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Other (please describe):

### Related Issues
Fixes # (issue number)
Closes # (issue number)
Related to # (issue number)

### Changes Made
- [ ] Code changes
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Configuration changes
- [ ] Data changes
- [ ] Research results

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance tests conducted
- [ ] Code coverage maintained/improved

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Code is properly commented
- [ ] Type hints added where appropriate
- [ ] No debug statements left in code

### Documentation
- [ ] README.md updated (if applicable)
- [ ] API documentation updated
- [ ] User guide updated
- [ ] Changelog updated
- [ ] Examples added/updated

### Research Validation (if applicable)
- [ ] Methodology is sound
- [ ] Experiments are reproducible
- [ ] Results are validated
- [ ] Statistical significance tested
- [ ] Baselines compared

### Performance Impact
- [ ] Performance benchmarks run
- [ ] No performance regression
- [ ] Memory usage acceptable
- [ ] Scalability considered

### Security Considerations
- [ ] No security vulnerabilities introduced
- [ ] Data privacy maintained
- [ ] Access controls respected
- [ ] Dependencies vetted

### Breaking Changes
- [ ] Breaking changes documented
- [ ] Migration guide provided
- [ ] Backward compatibility considered
- [ ] Deprecation notices added

### Deployment
- [ ] Deployment instructions updated
- [ ] Environment variables documented
- [ ] Database migrations included
- [ ] Rollback plan documented

### Review Checklist
#### For Reviewers
- [ ] Code is logically sound
- [ ] Implementation follows best practices
- [ ] Tests are comprehensive
- [ ] Documentation is accurate
- [ ] Performance is acceptable

#### For Maintainers
- [ ] CI/CD pipeline passes
- [ ] Merge conflicts resolved
- [ ] Branch is up to date
- [ ] Labels applied correctly
- [ ] Milestone assigned

### Screenshots/Videos (if applicable)
Add screenshots or videos to demonstrate the changes.

### Additional Notes
Any additional information that reviewers should know.

### Acknowledgments
Thanks to:
- @reviewer1 for code review
- @reviewer2 for testing suggestions
- @reviewer3 for documentation improvements

---

## How to Test

### Local Testing
```bash
# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run specific test
pytest tests/test_new_feature.py
```

### Integration Testing
```bash
# Setup test data
python scripts/setup_test_data.py

# Run integration tests
pytest tests/integration/
```

### Performance Testing
```bash
# Run benchmarks
python scripts/benchmark.py --compare main
```

---

## Merge Instructions

### Before Merging
1. Ensure all tests pass
2. Update documentation
3. Resolve all review comments
4. Check for merge conflicts
5. Verify CI/CD pipeline

### Merge Strategy
- [ ] Squash and merge
- [ ] Create merge commit
- [ ] Rebase and merge

### Post-Merge Actions
- [ ] Update version number
- [ ] Create release notes
- [ ] Deploy to staging
- [ ] Monitor for issues

---

**By submitting this PR, you agree to:**
- Follow the project's code of conduct
- Maintain code quality standards
- Respond to review feedback in a timely manner
- Update documentation as needed
- Test your changes thoroughly

Thank you for your contribution!
