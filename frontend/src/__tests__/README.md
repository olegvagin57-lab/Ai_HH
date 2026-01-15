# Frontend Tests

## Структура тестов

- `components/` - Тесты компонентов
- `integration/` - Integration тесты
- E2E тесты в `e2e/` папке

## Запуск тестов

```bash
# Компонентные тесты
npm test

# С coverage
npm run test:coverage

# В watch режиме
npm run test:watch

# E2E тесты
npm run test:e2e

# E2E с UI
npm run test:e2e:ui
```

## Написание тестов

Используйте React Testing Library для компонентных тестов:

```javascript
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

test('renders component', () => {
  render(<MyComponent />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```
