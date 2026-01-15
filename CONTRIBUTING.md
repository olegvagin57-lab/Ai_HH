# Contributing Guide

## Development Setup

1. Clone the repository
2. Set up backend environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up frontend environment:
   ```bash
   cd frontend
   npm install
   ```

## Running Tests

Before submitting code, ensure all tests pass:

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Code Style

### Backend

- Follow PEP 8
- Use type hints
- Run `ruff` for linting
- Run `mypy` for type checking

```bash
ruff check .
mypy app
```

### Frontend

- Follow ESLint rules
- Use Prettier for formatting

```bash
npm run lint
npm run format
```

## Writing Tests

### Requirements

- All new features must include tests
- Maintain or improve test coverage
- Write tests before fixing bugs (TDD when possible)

### Test Structure

- Unit tests for individual functions
- Integration tests for API endpoints
- E2E tests for user workflows

## Pull Request Process

1. Create a feature branch
2. Write tests for your changes
3. Ensure all tests pass
4. Update documentation if needed
5. Submit pull request with description

## Commit Messages

Use clear, descriptive commit messages:
- `feat: add candidate filtering`
- `fix: resolve authentication issue`
- `test: add tests for vacancy service`
- `docs: update API documentation`
