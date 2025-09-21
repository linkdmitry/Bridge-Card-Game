# Contributing to Card Game

We welcome contributions to the Card Game project! This document provides guidelines for contributing.

## 🤝 Ways to Contribute

- **Bug Reports**: Submit issues for bugs you find
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Improve README, comments, or add examples
- **Testing**: Add test cases or improve existing tests

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- Git
- Basic knowledge of Python and Pygame

### Setting Up Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork locally**:
```bash
git clone https://github.com/your-username/card-game.git
cd card-game
```

3. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Run the game to test**:
```bash
python src/main.py
```

## 📝 Coding Standards

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused on a single task

### Code Organization
- Place game logic in `src/game/`
- Place UI components in `src/gui/`
- Place utility functions in `src/utils/`
- Add tests for new features in `tests/` or as `test_*.py` files

### Example Code Structure
```python
class ExampleClass:
    """
    Brief description of the class.
    
    Attributes:
        attribute_name: Description of attribute
    """
    
    def __init__(self):
        """Initialize the class."""
        pass
    
    def example_method(self, parameter):
        """
        Brief description of method.
        
        Args:
            parameter: Description of parameter
            
        Returns:
            Description of return value
        """
        pass
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python test_effects.py
python test_suit_enforcement.py
python test_draw_mechanics.py
python test_six_covering_fix.py
python test_effect_indicators.py

# Run unit tests
pytest tests/
```

### Writing Tests
- Add tests for any new functionality
- Test both success and failure cases
- Use descriptive test names
- Include edge cases in your tests

## 📋 Pull Request Process

### Before Submitting
1. **Test your changes**: Ensure all tests pass
2. **Update documentation**: Update README if needed
3. **Follow coding standards**: Ensure code follows project style
4. **Add tests**: Include tests for new features

### Submitting a Pull Request
1. **Create a feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** and commit them:
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

3. **Push to your fork**:
```bash
git push origin feature/your-feature-name
```

4. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Reference any related issues

### Commit Message Format
Use clear, descriptive commit messages:
- `Add: New feature or functionality`
- `Fix: Bug fixes`
- `Update: Changes to existing features`
- `Docs: Documentation changes`
- `Test: Adding or updating tests`

## 🐛 Bug Reports

When reporting bugs, please include:
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to recreate the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, etc.
- **Screenshots**: If applicable

### Bug Report Template
```markdown
**Description**
Brief description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Python version:
- OS:
- Game version:
```

## ✨ Feature Requests

When requesting features:
- **Description**: Clear description of the feature
- **Use Case**: Why is this feature needed?
- **Implementation Ideas**: Any thoughts on how it could work
- **Alternatives**: Any alternative solutions considered

## 📞 Getting Help

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and general discussion
- **Code Review**: All pull requests will be reviewed by maintainers

## 🏆 Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Git commit history
- Release notes for significant contributions

Thank you for contributing to the Card Game project! 🎉