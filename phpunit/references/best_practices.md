# PHPUnit Best Practices

## 1. Core Principles
- **Use `assertSame()` over `assertEquals()`**: Always prefer strict type checking (`===`) to avoid false positives caused by type coercion.
- **Leverage Data Providers**: Use `#[DataProvider]` (or `@dataProvider` for PHPUnit < 10) to test multiple scenarios with a single test method.
- **Prefer Stubs over Mocks**: Use `createStub()` for objects that only need to return values. Reserve `createMock()` for verifying method calls.
- **Maintain Test Isolation**: Ensure each test is independent. Avoid using `setUp()` for heavy operations; use private factory methods to create the "System Under Test" (SUT).
- **Follow Naming Conventions**: Use descriptive, snake_case method names (e.g., `test_it_calculates_total_correctly`).

## 2. Structure
- **Directory**: Tests should mirror the `src/` directory structure.
- **Namespace**: Use `Tests\` prefix for test classes.
- **Class Name**: Suffix with `Test` (e.g., `UserServiceTest`).

## 3. Writing Tests
- **AAA Pattern**: Arrange, Act, Assert.
- **Single Responsibility**: Each test should focus on one behavior.
- **Avoid Logic in Tests**: Tests should be simple and declarative.
