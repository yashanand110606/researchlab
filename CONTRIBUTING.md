# Contributing to ResearchLab

Thank you for your interest in contributing! This document outlines the process for contributing.

## Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/` and `npm test`)
5. Commit with descriptive messages
6. Push to the branch
7. Open a Pull Request

## Code Standards

### Python
```bash
# Format code
ruff format .

# Lint
ruff check .

# Type check
mypy app/
```

### TypeScript
```bash
# Lint
npm run lint

# Type check
npx tsc --noEmit
```

## Adding New Features

### Backend
1. Follow the existing module structure
2. Add tests for new functionality
3. Update API documentation if endpoints change
4. Use Alembic migrations for database schema changes

### Frontend
1. Add components in appropriate directories
2. Update TypeScript types
3. Add tests for new components
4. Ensure responsive design on all breakpoints

## Commit Message Format

Use conventional commits:
```
feat: add parameter sweep experiment type
fix: handle null values in metric recording
docs: update API reference for runs endpoint
test: add reproducibility tests for monte carlo
chore: update dependencies
```

## Pull Request Process

1. Update README.md with any new features
2. Ensure all tests pass
3. Get review from at least one maintainer
4. Squash commits if requested
5. Merge after approval

## Reporting Issues

Include:
- System information (OS, Python version, Node version)
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or screenshots

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
