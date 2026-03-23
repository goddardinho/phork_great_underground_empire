# Phork Development Standards

This document outlines the coding standards and conventions used in the Phork project to maintain code quality, consistency, and maintainability.

## 📝 General Principles

- **Clarity over cleverness**: Write code that is easy to read and understand
- **Type safety**: Use type hints throughout the codebase
- **Modularity**: Keep modules focused on single responsibilities
- **Testing**: Write tests for all new functionality
- **Documentation**: Document all public interfaces and complex logic

## 🐍 Python Style Guide

### Code Formatting
- **Line length**: Maximum 100 characters per line
- **Indentation**: 4 spaces (no tabs)
- **String quotes**: Prefer double quotes for strings, single for string literals in code
- **Imports**: Group imports (stdlib, third-party, local) with blank lines between groups

### Naming Conventions
- **Variables**: `snake_case` for variables and functions
- **Classes**: `PascalCase` for class names  
- **Constants**: `UPPER_SNAKE_CASE` for constants
- **Private members**: Single leading underscore `_private_method`
- **Files/modules**: `snake_case.py`

### Type Annotations
```python
# Always use type hints for function parameters and return types
def process_command(self, user_input: str) -> str:
    """Process user command and return response."""
    
# Use typing module for complex types
from typing import Dict, List, Optional, Tuple

def get_room_data(self) -> Dict[str, Any]:
    """Return room data as dictionary."""
```

### Documentation Style
```python
def complex_function(param1: str, param2: Optional[int] = None) -> bool:
    """
    Brief description of what the function does.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of first parameter
        param2: Description of optional second parameter
        
    Returns:
        Description of return value
        
    Raises:
        SpecificException: When and why this exception is raised
    """
```

## 🏗️ Architecture Guidelines

### Module Organization
- **Single responsibility**: Each module should have one clear purpose
- **Dependency direction**: Dependencies should flow inward toward core logic
- **Interface segregation**: Keep public APIs minimal and focused

```
src/
├── game.py              # Main game engine - orchestrates everything
├── world/               # World model (rooms, connections)
├── entities/            # Game objects (player, items)  
├── parser/              # Command parsing and interpretation
└── parsers/             # File format parsers (mud files)
```

### Class Design
- **Composition over inheritance**: Prefer composition when possible
- **Immutable data**: Use immutable data structures where feasible
- **Clear responsibilities**: Each class should have a single, well-defined purpose

### Error Handling
- **Explicit exceptions**: Catch specific exceptions, not bare `except`
- **User-friendly messages**: Present generic error messages to users
- **Detailed logging**: Log detailed error information for debugging
- **Fail gracefully**: Degrade functionality rather than crashing

```python
try:
    result = risky_operation()
except SpecificError as e:
    logging.warning(f"Operation failed: {type(e).__name__}")
    return "Unable to complete that action."
```

## 🧪 Testing Standards

### Test Organization
- **Mirror source structure**: Test files mirror the source directory structure
- **Descriptive names**: Test methods clearly describe what is being tested
- **One concept per test**: Each test should verify one specific behavior

### Test Categories
- **Unit tests**: Test individual functions and classes in isolation
- **Integration tests**: Test interactions between components
- **Security tests**: Validate security measures and input handling
- **Performance tests**: Verify performance characteristics

### Test Naming
```python
class TestCommandParser:
    def test_parse_simple_verb_noun_command(self):
        """Test parsing of basic verb-noun commands like 'take sword'."""
        
    def test_parse_command_with_preposition(self):
        """Test parsing commands with prepositions like 'put sword in chest'."""
        
    def test_parse_invalid_input_returns_none(self):
        """Test that invalid input returns None rather than crashing."""
```

## 🔒 Security Standards

### Input Validation
- **Sanitize all input**: Clean user input before processing
- **Length limits**: Impose reasonable limits on input length
- **Character filtering**: Remove or escape dangerous characters

### File Operations
- **Path validation**: Ensure file paths remain within expected directories
- **Size limits**: Impose limits on file sizes for save/load operations
- **Safe parsing**: Validate data structure when loading files

### Error Disclosure  
- **Generic user messages**: Don't expose internal details in user-facing errors
- **Detailed logging**: Log full error details for debugging
- **No stack traces**: Never show stack traces to end users

## 📊 Performance Guidelines

### Efficiency Principles
- **Profile before optimizing**: Measure performance before making changes
- **Optimize hot paths**: Focus optimization efforts on frequently-called code
- **Memory awareness**: Be mindful of memory usage in loops and data structures

### Resource Management
- **Limit bulk operations**: Cap the number of objects processed in bulk actions
- **Lazy loading**: Load data only when needed
- **Clean up resources**: Properly close files and clean up temporary data

## 📚 Documentation Requirements

### Code Documentation
- **All public methods**: Document all public methods and classes
- **Complex logic**: Add inline comments for non-obvious code
- **Type hints**: Include type hints for all function signatures

### Project Documentation
- **README**: Keep README current with features and setup instructions
- **CHANGELOG**: Document all changes in CHANGELOG.md
- **API changes**: Document breaking changes and migration paths

## 🔧 Development Workflow

### Git Practices
- **Feature branches**: Use descriptive branch names like `feature/security-validation`
- **Commit messages**: Write clear, descriptive commit messages
- **Small commits**: Make small, focused commits rather than large ones
- **Pre-push validation**: Use automated checks to validate documentation and tests

### Code Reviews
- **Review for standards**: Ensure code follows these standards
- **Test coverage**: Verify new code includes appropriate tests  
- **Documentation**: Check that public interfaces are documented
- **Security review**: Consider security implications of changes

## 🛠️ Tools and Automation

### Recommended Tools
- **Type checking**: Use mypy for static type checking
- **Formatting**: Use black for consistent code formatting  
- **Testing**: Use pytest for test execution and reporting
- **Security**: Use bandit for security analysis

### Automation Scripts
- **./scripts/new-feature.sh**: Create new feature branches with planning docs
- **./scripts/create-version.sh**: Interactive version tagging and releases
- **Pre-push hooks**: Automated documentation and validation checks

## ✅ Quality Checklist

Before submitting code, ensure:

- [ ] **Code follows naming conventions**
- [ ] **All functions have type hints** 
- [ ] **Public methods are documented**
- [ ] **Tests cover new functionality**
- [ ] **Security implications considered**
- [ ] **Performance impact assessed**
- [ ] **Documentation updated**
- [ ] **CHANGELOG.md updated**

---

**Remember**: These standards exist to maintain code quality and team productivity. When in doubt, prioritize clarity and maintainability over brevity or cleverness.