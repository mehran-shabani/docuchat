# Contributing to DocuChat

Thank you for your interest in contributing to DocuChat! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/your-org/docuchat/issues)
2. If not, create a new issue with a clear title and description
3. Include steps to reproduce, expected behavior, and actual behavior
4. Add relevant labels (bug, enhancement, etc.)

### Suggesting Features

1. Check existing [Discussions](https://github.com/your-org/docuchat/discussions) for similar ideas
2. Create a new discussion to gather feedback
3. Once approved, create an issue with detailed specifications

### Pull Requests

1. **Fork the repository** and create a new branch from `develop`
2. **Make your changes** following our coding standards
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Run linting and tests** to ensure everything passes
6. **Submit a pull request** with a clear description

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/docuchat.git
cd docuchat

# Create a feature branch
git checkout -b feature/your-feature-name

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up frontend
cd ../frontend
npm install

# Run tests
cd ../backend
pytest
cd ../frontend
npm run lint
```

### Coding Standards

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all functions
- Run `ruff check` and `ruff format` before committing
- Write docstrings for all public functions
- Maintain test coverage above 80%

#### TypeScript/React (Frontend)
- Follow ESLint configuration
- Use functional components with hooks
- Keep components small and focused
- Write meaningful prop types
- Use meaningful variable names

### Commit Messages

Follow the Conventional Commits specification:

```
type(scope): brief description

Detailed explanation if needed

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(backend): add document upload endpoint`
- `fix(frontend): resolve RTL layout issue in chat component`
- `docs(readme): update installation instructions`

### Review Process

1. All PRs require at least one approval
2. CI/CD checks must pass
3. Code must meet quality standards
4. Documentation must be updated

### Translation Contributions

See [Translation Plan](./docs/translation-plan.md) for details on contributing translations.

## Getting Help

- Join our [Discussions](https://github.com/your-org/docuchat/discussions)
- Check the [Documentation](./docs/en/README.md)
- Contact maintainers via email

Thank you for contributing! 🎉
