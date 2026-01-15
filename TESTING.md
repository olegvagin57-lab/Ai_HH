# Testing Guide

## Overview

This project uses comprehensive testing strategy following industry best practices to ensure code quality and reliability.

## Test Structure

### Backend Tests

```
backend/tests/
├── services/          # Unit tests for services
├── domain/           # Domain entity tests
├── infrastructure/   # Infrastructure tests
├── integration/      # Integration tests
├── tasks/            # Celery tasks tests
├── security/         # Security tests
├── performance/      # Performance tests
└── edge_cases/       # Edge cases and error scenarios
```

### Frontend Tests

```
frontend/src/
├── __tests__/        # Component tests
└── e2e/              # End-to-end tests
```

## Running Tests

### Backend Tests

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/services/test_auth_service.py

# Run specific test
pytest tests/services/test_auth_service.py::test_register_user

# Run by marker
pytest -m unit
pytest -m integration
pytest -m security
```

### Frontend Tests

```bash
# Run all tests
cd frontend
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- SearchPage.test.jsx
```

## Test Categories

### Unit Tests

Test individual components in isolation:
- Services
- Domain entities
- Utility functions

### Integration Tests

Test component interactions:
- API endpoints
- Database operations
- External service integrations

### E2E Tests

Test complete user workflows:
- User authentication flow
- Search creation and processing
- Candidate management

### Security Tests

Test security aspects:
- Authentication and authorization
- Input validation
- SQL/NoSQL injection protection
- XSS protection
- Rate limiting

### Performance Tests

Test performance characteristics:
- API response times
- Concurrent request handling
- Database query performance

## Test Coverage Goals

- **Backend:** Minimum 80% code coverage
- **Frontend:** Minimum 70% component coverage
- **Critical paths:** 100% coverage (auth, data export, payment)

## Writing Tests

### Backend Test Example

```python
@pytest.mark.asyncio
async def test_create_user(auth_service: AuthService):
    """Test user creation"""
    user = await auth_service.register_user(
        email="test@example.com",
        username="testuser",
        password="SecurePass123"
    )
    
    assert user.email == "test@example.com"
    assert user.is_active is True
```

### Frontend Test Example

```javascript
import { render, screen } from '@testing-library/react';
import LoginPage from './LoginPage';

describe('LoginPage', () => {
  it('renders login form', () => {
    render(<LoginPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });
});
```

## Test Fixtures

Common fixtures are available in `backend/tests/conftest.py`:
- `test_user` - Regular test user
- `admin_user` - Admin user
- `hr_manager_user` - HR manager user
- `test_search` - Test search
- `test_resume` - Test resume
- `test_vacancy` - Test vacancy
- `test_candidate` - Test candidate

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Scheduled nightly runs

## Best Practices

1. **Test isolation:** Each test should be independent
2. **Clear naming:** Test names should describe what they test
3. **Arrange-Act-Assert:** Structure tests clearly
4. **Mock external dependencies:** Don't rely on external services
5. **Test edge cases:** Include boundary conditions
6. **Keep tests fast:** Unit tests should run quickly
7. **Maintain test data:** Use fixtures for reusable test data

## Troubleshooting

### Common Issues

1. **Database connection errors:** Ensure test database is configured
2. **Async test errors:** Use `@pytest.mark.asyncio` for async tests
3. **Import errors:** Check PYTHONPATH and module structure
4. **Fixture errors:** Ensure fixtures are properly scoped

### Debugging

```bash
# Run with verbose output
pytest -v

# Run with print statements
pytest -s

# Run with debugger
pytest --pdb
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [Jest Documentation](https://jestjs.io/)
