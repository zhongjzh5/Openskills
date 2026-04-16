# Contributing to AI Research Lab

Thank you for your interest in contributing to our research lab! This guide will help you understand how to contribute effectively.

## Table of Contents

- [Getting Started](#getting-started)
- [Types of Contributions](#types-of-contributions)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Research Guidelines](#research-guidelines)
- [Review Process](#review-process)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites
- Basic understanding of Git and GitHub
- Proficiency in Python and relevant ML frameworks
- Familiarity with research practices

### Setup Your Development Environment

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/research-lab.git
   cd research-lab
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configure Git Hooks**
   ```bash
   # Install pre-commit hooks
   pre-commit install
   ```

4. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Types of Contributions

We welcome various types of contributions:

### Code Contributions
- **Bug Fixes**: Resolve issues in existing code
- **New Features**: Add functionality to projects
- **Performance Improvements**: Optimize existing algorithms
- **Documentation**: Improve code documentation

### Research Contributions
- **New Algorithms**: Novel approaches to existing problems
- **Experimental Results**: Reproduce or extend existing research
- **Datasets**: Curate and share research datasets
- **Literature Reviews**: Comprehensive analysis of research areas

### Community Contributions
- **Issue Triage**: Help manage and categorize issues
- **Code Review**: Provide constructive feedback on PRs
- **Mentorship**: Help new contributors get started
- **Documentation**: Improve guides and tutorials

## Development Workflow

### 1. Find or Create an Issue
- Browse [existing issues](https://github.com/zhongjzh5/research-lab/issues)
- Create a new issue with appropriate template
- Discuss approach with maintainers

### 2. Work on Your Contribution
- Follow the [code standards](#code-standards)
- Write tests for your changes
- Update documentation as needed

### 3. Submit a Pull Request
- Create a PR from your feature branch
- Fill out the PR template completely
- Request reviews from appropriate team members

### 4. Review Process
- Address reviewer feedback promptly
- Keep PR up to date with main branch
- Ensure all checks pass

## Code Standards

### Python Code Style
- Follow [PEP 8](https://pep8.org/) guidelines
- Use [Black](https://black.readthedocs.io/) for formatting
- Maximum line length: 88 characters
- Use type hints where appropriate

### Code Organization
```python
# File structure example
import numpy as np
import torch
from typing import List, Optional, Tuple

class ModelInterface:
    """Base class for all models."""
    
    def __init__(self, config: dict) -> None:
        """Initialize model with configuration."""
        self.config = config
        self._setup_model()
    
    def _setup_model(self) -> None:
        """Set up model architecture."""
        pass
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        raise NotImplementedError
```

### Testing Requirements
- Write unit tests for all new functions
- Aim for >80% code coverage
- Use pytest for testing framework
- Include integration tests for complex workflows

### Documentation Standards
- All public functions must have docstrings
- Use Google-style docstring format
- Include parameter types and return values
- Provide usage examples

```python
def train_model(
    model: torch.nn.Module,
    data_loader: torch.utils.data.DataLoader,
    epochs: int,
    learning_rate: float = 0.001,
) -> Tuple[List[float], torch.nn.Module]:
    """Train a neural network model.
    
    Args:
        model: The neural network to train
        data_loader: Training data loader
        epochs: Number of training epochs
        learning_rate: Learning rate for optimization
    
    Returns:
        A tuple of (loss_history, trained_model)
    
    Example:
        >>> model = SimpleNet()
        >>> losses, trained = train_model(model, loader, 10)
    """
```

## Research Guidelines

### Research Ethics
- Follow institutional review board (IRB) guidelines
- Ensure data privacy and protection
- Consider societal impact of research
- Obtain proper consent for data collection

### Reproducibility
- Provide complete experimental setup
- Share datasets when possible
- Document hyperparameters and random seeds
- Include environment specifications

### Publication Standards
- Follow academic integrity guidelines
- Proper citation of related work
- Clear contribution statements
- Open access to code and data when possible

## Review Process

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive and passing
- [ ] Documentation is updated
- [ ] Performance impact is considered
- [ ] Security implications are addressed
- [ ] Breaking changes are documented

### Research Review Checklist
- [ ] Methodology is sound
- [ ] Experiments are well-designed
- [ ] Results are properly validated
- [ ] Claims are supported by evidence
- [ ] Related work is adequately cited

### Review Roles
- **Primary Reviewer**: Domain expert who evaluates technical content
- **Secondary Reviewer**: Checks code quality and documentation
- **Maintainer**: Ensures overall project consistency

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Avoid personal attacks or harassment

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Slack**: Real-time team communication
- **Email**: Formal communications and announcements

### Meeting Guidelines
- **Weekly Standup**: Progress updates and blockers
- **Bi-weekly Research Review**: Paper discussions and research updates
- **Monthly Planning**: Project planning and resource allocation

## Getting Help

### Resources
- [Lab Handbook](./docs/handbook.md) - Detailed lab policies
- [Development Guide](./docs/development.md) - Technical setup
- [Research Templates](./templates/) - Common research templates

### Contact Points
- **Technical Questions**: Create GitHub issue with `question` label
- **Research Collaboration**: Contact PI directly via email
- **Administrative Issues**: Lab coordinator

## Recognition

### Contributor Recognition
- Contributors are acknowledged in publications
- Top contributors featured in lab newsletter
- Annual contributor awards and recognition

### Authorship Guidelines
- Follow ICMJE criteria for authorship
- Clearly define contribution types
- Use CRediT taxonomy for contribution statements

---

## Quick Reference

### Common Git Commands
```bash
# Sync with upstream
git fetch upstream
git rebase upstream/main

# Create PR
git push origin feature/your-feature-name
# Then create PR on GitHub

# Clean up after merge
git checkout main
git branch -d feature/your-feature-name
```

### Testing Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_model.py
```

### Code Quality Checks
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

---

Thank you for contributing to our research lab! Your contributions help advance AI research and make our tools better for everyone.

If you have any questions, don't hesitate to ask in our [Discussions](https://github.com/zhongjzh5/research-lab/discussions) or contact us directly.
