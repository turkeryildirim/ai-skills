---
name: phpunit
description: Expert guidance for writing, running, and maintaining PHPUnit tests. Use this skill when creating new tests, refactoring existing ones, or troubleshooting test failures in PHP projects.
model: inherit
---

# PHPUnit Best Practices

Procedural knowledge and patterns for effective PHP testing using PHPUnit. Emphasizes strict typing, AAA pattern, and modern isolation techniques.

## Specialized Agents

Specialized personas for PHP testing. Load these from `agents/` to provide expert context.

| Agent | Role | Focus |
|-------|------|-------|
| **phpunit-pro** | Testing Expert | AAA pattern, mocking strategies, isolation, AI testing. |

## When to Use

- Creating new unit, integration, or feature tests
- Refactoring existing test suites for better performance or isolation
- Troubleshooting failing tests or flaky test suites
- Implementing complex mocking/stubbing logic
- Setting up CI/CD test pipelines
- Testing AI-driven or probabilistic outputs

## Core Workflow

1. **Analysis**: Identify the System Under Test (SUT) and its dependencies.
2. **Setup**: Use `createStub()` for simple values; `createMock()` for interaction verification.
3. **Implementation**: Follow the **AAA (Arrange, Act, Assert)** pattern.
4. **Data Management**: Use `#[DataProvider]` for multi-scenario testing.
5. **Validation**: Run tests and ensure 0 failures and high coverage.

## Core Directives

### MUST DO

- Follow the **AAA (Arrange, Act, Assert)** pattern in every test method
- Use `assertSame()` for all equality checks to avoid type coercion issues
- Use descriptive, snake_case names (e.g., `test_it_calculates_total_with_tax`)
- Ensure every test is **Isolated**: never rely on the state from a previous test
- Use `#[DataProvider]` for tests that require multiple input scenarios
- Mock slow or external dependencies (Databases, APIs) for unit tests
- Declare return types (`void`) for all test methods

### MUST NOT DO

- Use `assertEquals()` when `assertSame()` is possible (type safety)
- Perform multiple unrelated assertions in a single test method
- Use `setUp()` for complex object creation (prefer private factory methods)
- Rely on real external APIs or network connectivity during testing
- Commit tests that rely on local environment variables or specific paths
- Suppress errors or exceptions during the Act phase

## Category Index — When to Load Which Reference

| # | Category | Impact | Load when… | Reference |
|--:|----------|:------:|------------|-----------|
| 1 | Coding Standards | HIGH | Designing test structure, naming, and organization | [`references/best_practices.md`](references/best_practices.md) |
| 2 | Common Assertions | HIGH | Choosing the right assertion for the task | [`references/common_assertions.md`](references/common_assertions.md) |
| 3 | AI & Probabilistic | MEDIUM | Testing LLM outputs or non-deterministic logic | [`references/ai_testing.md`](references/ai_testing.md) |

## Validation Checklist

- [ ] Every test follows the AAA (Arrange, Act, Assert) structure
- [ ] `assertSame()` is used instead of `assertEquals()` where applicable
- [ ] Test names clearly describe the scenario and expected outcome
- [ ] Tests are fully isolated and do not share state
- [ ] Data providers are used for multi-scenario validation
- [ ] All slow/external dependencies are correctly mocked or stubbed
- [ ] Return types are explicitly declared for all test methods
- [ ] Tests pass consistently in a clean environment

## External References

- [PHPUnit Documentation](https://phpunit.de/documentation.html)
- [Testing in Laravel](https://laravel.com/docs/testing)
- [Pest PHP (Alternative Runner)](https://pestphp.com)
- [Mockery (Alternative Mocking)](http://docs.mockery.io)
