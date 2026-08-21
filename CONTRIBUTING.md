# 🤝 Contributing to ChatHarvest

First off, thank you for considering contributing to ChatHarvest! 🎉 We welcome contributions from everyone, regardless of experience level.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How Can I Contribute?](#-how-can-i-contribute)
- [Development Setup](#-development-setup)
- [Pull Request Guidelines](#-pull-request-guidelines)
- [Issue Reporting](#-issue-reporting)
- [Coding Standards](#-coding-standards)

## 📜 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Be kind, be constructive, and focus on what's best for the community.

## 💡 How Can I Contribute?

### 🐛 Reporting Bugs

- Use the GitHub Issues tracker
- Include a clear title and description
- Provide steps to reproduce the issue
- Include your OS, Python version, and ChatHarvest version
- Attach sample data if relevant (anonymize personal data!)

### ✨ Suggesting Features

- Open an issue with the `enhancement` label
- Describe the feature and its use case
- Explain why it would be useful for the broader community

### 🔧 Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/chatharvest.git
cd chatharvest

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run the CLI
python -m chatharvest --help
```

## 📝 Pull Request Guidelines

- **Title format**: Use [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `refactor:` for code refactoring
  - `test:` for test additions
  - `chore:` for maintenance tasks

- **Description**: Explain what and why, not just how
- **Tests**: Add tests for new features and bug fixes
- **Documentation**: Update README if needed
- **One PR per feature**: Keep pull requests focused

## 🐛 Issue Reporting

When filing an issue, please include:

1. **ChatHarvest version**: `chatharvest --version`
2. **Python version**: `python --version`
3. **OS**: Windows/macOS/Linux with version
4. **Steps to reproduce**: Clear, numbered steps
5. **Expected behavior**: What should happen
6. **Actual behavior**: What actually happens
7. **Error messages**: Full traceback if applicable

## 💻 Coding Standards

- **Python**: Follow PEP 8, use type hints
- **Zero core dependencies**: New extractors and core features must use only stdlib
- **Docstrings**: All public functions and classes should have docstrings
- **Tests**: Aim for meaningful test coverage
- **Cross-platform**: Code should work on Windows, macOS, and Linux

## 🏷️ Adding a New Extractor

To add support for a new AI coding tool:

1. Create `chatharvest/extractors/<tool_name>.py`
2. Inherit from `BaseExtractor`
3. Implement `extract(path)` method
4. Register in `chatharvest/extractors/__init__.py`
5. Add tests in `tests/test_extractors.py`
6. Update README with the new tool

## 🙏 Thank You!

Your contributions make ChatHarvest better for everyone. We appreciate your time and effort! 💚
