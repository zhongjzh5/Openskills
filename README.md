# OpenSkills

Skill encapsulation framework for AI assistants.

## Features

- **Skill Management**: Create, validate, and manage AI skills
- **CLI Toolchain**: Command-line tools for skill development
- **Standardized Structure**: Consistent skill organization and documentation
- **Validation**: Built-in skill validation and testing

## Quick Start

### Installation

```bash
pip install -e .
```

### Create a New Skill

```bash
openskills create my-skill
cd my-skill
# Edit SKILL.md and implement your skill
openskills validate .
```

### List Available Skills

```bash
openskills list
```

### Validate a Skill

```bash
openskills validate path/to/skill
```

## Project Structure

```
openskills/
|-- src/openskills/          # Core framework
|   |-- __init__.py
|   |-- cli.py              # CLI toolchain
|-- skills/                 # Skill implementations
|   |-- meme-generator/     # Example skill
|   |-- image-resize/       # Another skill
|-- data/                   # Data and feedback
|-- scripts/               # Utility scripts
|-- tests/                 # Framework tests
```

## Skill Structure

Each skill follows this structure:

```
skill-name/
|-- SKILL.md               # Skill documentation (required)
|-- requirements.txt       # Dependencies (required)
|-- scripts/               # Implementation (required)
|   |-- main.py
|-- tests/                 # Tests (required)
|   |-- test_skill.py
|-- docs/                  # Additional docs
|-- assets/                # Resources
```

## Contributing

1. Fork the project
2. Create a feature branch
3. Implement your skill
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
