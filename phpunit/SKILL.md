---
name: phpunit
description: Expert guidance for writing, running, and maintaining PHPUnit tests. Use this skill when creating new tests, refactoring existing ones, or troubleshooting test failures in PHP projects.
---

# PHPUnit Skill

## Overview

This skill provides procedural knowledge for effective PHP testing using PHPUnit. It emphasizes strict type checking, efficient test data management, and modern AI-assisted testing patterns.

## Core Workflow

1. **Analysis**: Identify the System Under Test (SUT) and its dependencies. List all logical paths, boundary conditions, and potential failure states.
2. **Setup**: Use `createStub()` for simple return values and `createMock()` only when interaction verification is needed. Prefer private factory methods over `setUp()` for better isolation and performance.
3. **Implementation**: Use the AAA (Arrange, Act, Assert) pattern. Favor `assertSame()` for all equality checks.
4. **Data Management**: Use `#[DataProvider]` for multi-scenario testing to keep test methods clean and focused.
5. **Validation**: Run the tests and ensure they pass. For AI-driven features, use statistical thresholds or LLM-as-judge patterns.

## Best Practices

- **Strictness**: Always use `assertSame()` to avoid type coercion bugs.
- **Naming**: Use descriptive snake_case names: `test_it_does_something_when_condition_is_met`.
- **Isolation**: Each test MUST be independent. Never rely on the state from a previous test.
- **Speed**: Keep tests fast. Mock slow dependencies like databases or external APIs.

## Resources

- **[best_practices.md](references/best_practices.md)**: Detailed coding standards and structural guidelines.
- **[common_assertions.md](references/common_assertions.md)**: Quick reference for frequently used PHPUnit assertions.
- **[ai_testing.md](references/ai_testing.md)**: Specialized patterns for testing AI agents and probabilistic outputs.

## Example: Creating a Test

```php
use PHPUnit\Framework\TestCase;

class CalculatorTest extends TestCase
{
    public function test_it_adds_two_numbers(): void
    {
        // Arrange
        $calculator = new Calculator();

        // Act
        $result = $calculator->add(2, 3);

        // Assert
        $this->assertSame(5, $result);
    }
}
```
