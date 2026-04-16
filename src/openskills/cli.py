#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenSkills CLI - Toolchain for skill management
"""

import argparse
import json
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional

def validate_skill(skill_path: Path) -> bool:
    """Validate a skill directory structure and SKILL.md"""
    required_files = ["SKILL.md", "requirements.txt"]
    required_dirs = ["scripts", "tests"]
    
    # Check required files
    for file in required_files:
        if not (skill_path / file).exists():
            print(f"  Missing required file: {file}")
            return False
    
    # Check required directories
    for dir_name in required_dirs:
        if not (skill_path / dir_name).is_dir():
            print(f"  Missing required directory: {dir_name}")
            return False
    
    # Validate SKILL.md structure
    skill_md = skill_path / "SKILL.md"
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check YAML frontmatter
        if not content.startswith("---"):
            print(f"  SKILL.md missing YAML frontmatter")
            return False
        
        # Parse frontmatter
        try:
            frontmatter_end = content.find("---", 3)
            if frontmatter_end == -1:
                print(f"  SKILL.md frontmatter not properly closed")
                return False
            
            frontmatter = content[3:frontmatter_end]
            metadata = yaml.safe_load(frontmatter)
            
            # Check required fields
            required_fields = ["name", "version", "author", "description"]
            for field in required_fields:
                if field not in metadata:
                    print(f"  SKILL.md missing required field: {field}")
                    return False
                    
        except yaml.YAMLError as e:
            print(f"  SKILL.md frontmatter YAML error: {e}")
            return False
            
    except Exception as e:
        print(f"  Error reading SKILL.md: {e}")
        return False
    
    # Validate requirements.txt
    req_file = skill_path / "requirements.txt"
    try:
        with open(req_file, "r", encoding="utf-8") as f:
            requirements = f.read().strip()
        if not requirements:
            print(f"  requirements.txt is empty")
            return False
    except Exception as e:
        print(f"  Error reading requirements.txt: {e}")
        return False
    
    return True

def create_skill_template(skill_name: str, target_dir: Path) -> bool:
    """Create a new skill from template"""
    skill_path = target_dir / skill_name
    
    if skill_path.exists():
        print(f"Error: Directory {skill_path} already exists")
        return False
    
    # Create directories
    (skill_path / "scripts").mkdir(parents=True, exist_ok=True)
    (skill_path / "tests").mkdir(parents=True, exist_ok=True)
    (skill_path / "docs").mkdir(parents=True, exist_ok=True)
    (skill_path / "assets").mkdir(parents=True, exist_ok=True)
    
    # Create SKILL.md template
    skill_md_content = f"""---
name: {skill_name}
version: 1.0.0
author: OpenSkills Team
license: MIT
description: Brief description of {skill_name}
---

# Skill Overview

TODO: Add skill description and usage instructions

---

# Trigger Conditions

## Keywords
- TODO: Add trigger keywords

## Context Patterns
- TODO: Add context patterns

---

# Safety Boundaries

## Prohibited Operations
- TODO: List prohibited operations

## Required Permissions
- TODO: List required permissions

---

# Interface Definition

## Input Format (JSON)
```json
{{
  "input": "example input",
  "options": {{
    "parameter": "value"
  }}
}}
```

## Output Format (JSON)
```json
{{
  "status": "success|error",
  "result": "output data",
  "message": "description"
}}
```

---

# Usage Examples

TODO: Add usage examples

---

# Installation

```bash
pip install -r requirements.txt
```

---

# Testing

```bash
python -m pytest tests/
```
"""
    
    with open(skill_path / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(skill_md_content)
    
    # Create requirements.txt
    with open(skill_path / "requirements.txt", "w", encoding="utf-8") as f:
        f.write("# Add your skill dependencies here\n")
    
    # Create main script template
    main_script = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Main script for {skill_name} skill
\"\"\"

import json
import sys
from pathlib import Path

def main():
    \"\"\"Main entry point\"\"\"
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_json>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: Input file {{input_file}} not found")
        sys.exit(1)
    
    with open(input_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)
    
    # TODO: Implement skill logic here
    result = {{
        "status": "success",
        "result": "TODO: implement skill logic",
        "input": input_data
    }}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
"""
    
    with open(skill_path / "scripts" / "main.py", "w", encoding="utf-8") as f:
        f.write(main_script)
    
    # Create test template
    test_content = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Tests for {skill_name} skill
\"\"\"

import pytest
import json
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import main

def test_basic_functionality():
    \"\"\"Test basic skill functionality\"\"\"
    # TODO: Add actual tests
    assert True

def test_input_validation():
    \"\"\"Test input validation\"\"\"
    # TODO: Add input validation tests
    assert True
"""
    
    with open(skill_path / "tests" / "test_{skill_name}.py", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print(f"Created skill template: {skill_path}")
    return True

def list_skills(skills_dir: Path) -> List[Dict]:
    """List all available skills"""
    skills = []
    
    if not skills_dir.exists():
        return skills
    
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            try:
                with open(skill_dir / "SKILL.md", "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Parse frontmatter
                frontmatter_end = content.find("---", 3)
                if frontmatter_end != -1:
                    frontmatter = content[3:frontmatter_end]
                    metadata = yaml.safe_load(frontmatter)
                    
                    skills.append({
                        "name": metadata.get("name", skill_dir.name),
                        "version": metadata.get("version", "unknown"),
                        "description": metadata.get("description", ""),
                        "path": str(skill_dir)
                    })
            except Exception:
                continue
    
    return skills

def main():
    parser = argparse.ArgumentParser(description="OpenSkills CLI - Toolchain for skill management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a skill")
    validate_parser.add_argument("skill_path", help="Path to skill directory")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new skill from template")
    create_parser.add_argument("skill_name", help="Name of the skill to create")
    create_parser.add_argument("--target", default=".", help="Target directory (default: current)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all available skills")
    list_parser.add_argument("--skills-dir", default=".", help="Skills directory (default: current)")
    
    args = parser.parse_args()
    
    if args.command == "validate":
        skill_path = Path(args.skill_path)
        if not skill_path.exists():
            print(f"Error: Skill path {skill_path} does not exist")
            sys.exit(1)
        
        print(f"Validating skill: {skill_path}")
        if validate_skill(skill_path):
            print("  Skill validation: PASSED")
        else:
            print("  Skill validation: FAILED")
            sys.exit(1)
    
    elif args.command == "create":
        target_dir = Path(args.target)
        if create_skill_template(args.skill_name, target_dir):
            print(f"Skill '{args.skill_name}' created successfully")
            print(f"Next steps:")
            print(f"  1. cd {args.skill_name}")
            print(f"  2. Edit SKILL.md with your skill details")
            print(f"  3. Implement skill logic in scripts/main.py")
            print(f"  4. Add tests in tests/")
            print(f"  5. Run 'openskills validate .' to check")
        else:
            print("Failed to create skill")
            sys.exit(1)
    
    elif args.command == "list":
        skills_dir = Path(args.skills_dir)
        skills = list_skills(skills_dir)
        
        if not skills:
            print("No skills found")
        else:
            print("Available skills:")
            for skill in skills:
                print(f"  {skill['name']} v{skill['version']}")
                print(f"    Description: {skill['description']}")
                print(f"    Path: {skill['path']}")
                print()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
