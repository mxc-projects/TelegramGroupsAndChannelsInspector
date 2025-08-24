# 🤝 Contributing to Telegram Groups Inspector

Thank you for your interest in contributing! We welcome contributions from everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/TelegramGroupsInspector.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Push to your fork: `git push origin feature/your-feature-name`
6. Submit a pull request

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/TelegramGroupsInspector.git
   cd TelegramGroupsInspector
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies (if exists)
   ```

4. **Configure the application**
   ```bash
   cp src/config/config_template.py src/config/config.py
   # Edit config.py with your API credentials
   ```

5. **Run tests**
   ```bash
   python -m pytest
   ```

## 🎯 How to Contribute

### 🐛 Reporting Bugs

Before creating bug reports, please check the issue list as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what behavior you expected**
- **Include screenshots if applicable**
- **Include your environment details** (OS, Python version, etc.)

### 🚀 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain which behavior you expected to see instead**
- **Explain why this enhancement would be useful**

### 🔧 Code Contributions

#### Areas for Contribution

- **New Features**: Add new analysis capabilities
- **Performance Improvements**: Optimize existing algorithms
- **Bug Fixes**: Fix reported issues
- **Documentation**: Improve code documentation and user guides
- **Testing**: Add or improve test coverage
- **UI/UX**: Enhance console interface and user experience

#### Development Guidelines

1. **Feature Branches**: Create feature branches from `main`
2. **Commits**: Make atomic commits with clear messages
3. **Testing**: Add tests for new features
4. **Documentation**: Update documentation for new features
5. **Code Style**: Follow the project's coding standards

## 📝 Pull Request Process

1. **Ensure Prerequisites**
   - [ ] All tests pass
   - [ ] Code follows style guidelines
   - [ ] Documentation is updated
   - [ ] No merge conflicts

2. **PR Description**
   - Clearly describe the changes made
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

3. **Review Process**
   - At least one maintainer review required
   - Address all review comments
   - Ensure CI checks pass

4. **Merging**
   - Squash commits if requested
   - Update CHANGELOG.md if applicable
   - Delete feature branch after merge

## 🎨 Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# ✅ Good
def analyze_messages(group_id: int, limit: int = 100) -> List[Message]:
    """Analyze messages from a specific group.
    
    Args:
        group_id: Telegram group ID
        limit: Maximum number of messages to analyze
        
    Returns:
        List of analyzed messages
    """
    messages = []
    # Implementation here
    return messages

# ❌ Bad
def analyzeMessages(groupId, limit=100):
    messages = []
    return messages
```

### Code Formatting

- **Line Length**: Maximum 79 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Group imports and sort alphabetically
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Use type hints for all function parameters and returns

### Project Structure

```
src/
├── modules/          # Core functionality
├── units/           # Utility components  
├── utils/           # Advanced utilities
├── config/          # Configuration management
├── logs/            # Application logs
├── outputs/         # Generated outputs
└── sessions/        # Telegram sessions
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_group_scanner.py

# Run with coverage
python -m pytest --cov=src

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies

```python
def test_group_scanner_basic_functionality():
    # Arrange
    scanner = GroupScanner()
    mock_group = create_mock_group()
    
    # Act
    result = scanner.scan_group(mock_group)
    
    # Assert
    assert result.member_count > 0
    assert result.group_title == "Test Group"
```

## 📚 Documentation

### Code Documentation

- **Docstrings**: All public functions and classes must have docstrings
- **Comments**: Explain complex logic and business rules
- **Type Hints**: Use comprehensive type annotations

### User Documentation

- **README.md**: Keep the main README up to date
- **API Documentation**: Document all public APIs
- **Examples**: Provide usage examples for new features

## 🏷️ Issue and PR Labels

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `question` - Further information is requested

### PR Labels

- `work in progress` - PR is not ready for review
- `ready for review` - PR is ready for review
- `needs changes` - PR needs modifications
- `approved` - PR has been approved

## 🎯 Development Priorities

### High Priority
- Performance optimizations
- Bug fixes
- Security improvements
- Core feature stability

### Medium Priority
- New analysis features
- UI/UX improvements
- Additional export formats
- Enhanced error handling

### Low Priority
- Code refactoring
- Documentation improvements
- Additional testing
- Nice-to-have features

## 🤔 Questions?

If you have questions about contributing, please:

1. Check the existing issues and discussions
2. Read through this contributing guide
3. Create a new issue with the `question` label
4. Join our discussions (if applicable)

## 🙏 Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes for significant contributions
- GitHub contributors page

---

Thank you for contributing to Telegram Groups Inspector! 🚀
